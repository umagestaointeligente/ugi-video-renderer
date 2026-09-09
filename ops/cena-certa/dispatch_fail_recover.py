#!/usr/bin/env python3
"""CAS-protected recovery for a failed, unpublished Cena Certa dispatch."""
from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
OPS = ROOT / 'ops/cena-certa'
DISPATCH = OPS / 'dispatch.json'
OUTBOX = OPS / 'publisher-outbox.json'
STATE = OPS / 'publisher-state.json'
APPROVAL = OPS / 'human-approval.json'


def load(path: pathlib.Path) -> dict:
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise SystemExit(f'JSON_OBJECT_REQUIRED {path.name}')
    return value


def atomic_json(path: pathlib.Path, value: dict) -> None:
    tmp = path.with_name(path.name + f'.tmp-{os.getpid()}')
    try:
        tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--request-id', required=True)
    parser.add_argument('--batch-sha256', required=True)
    parser.add_argument('--failed-run-id', required=True, type=int)
    args = parser.parse_args()

    dispatch = load(DISPATCH)
    if dispatch.get('enabled') is not True or str(dispatch.get('mode') or '').upper() != 'PREPARE':
        raise SystemExit('FAILED_DISPATCH_NOT_ACTIVE')
    if dispatch.get('request_id') != args.request_id or dispatch.get('batch_sha256') != args.batch_sha256:
        raise SystemExit('FAILED_DISPATCH_CAS_FAIL')

    outbox, state, approval = load(OUTBOX), load(STATE), load(APPROVAL)
    if outbox.get('items'):
        raise SystemExit('FAILED_DISPATCH_RECOVERY_OUTBOX_NOT_EMPTY')
    if state.get('state') == 'AWAITING_HUMAN_APPROVAL' or approval.get('approved') is True:
        raise SystemExit('FAILED_DISPATCH_RECOVERY_PUBLICATION_STATE_UNSAFE')

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    incident = {
        'schema': 'CENA_CERTA_FAILED_DISPATCH_V1',
        'request_id': args.request_id,
        'batch_sha256': args.batch_sha256,
        'failed_run_id': args.failed_run_id,
        'recovered_at': now,
        'publication_attempted': False,
        'blind_retry_forbidden': True,
    }
    incident_path = OPS / 'incidents' / f'failed-dispatch-{args.request_id}.json'
    incident_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_json(incident_path, incident)
    atomic_json(DISPATCH, {
        'schema': 'CENA_CERTA_PRODUCTION_DISPATCH_V1',
        'enabled': False,
        'mode': 'IDLE',
        'batch_path': '',
        'batch_sha256': '',
        'prepared_run_id': '',
        'requested_at': '',
        'request_id': '',
        'note': f'CAS-closed after failed production run {args.failed_run_id}; no publisher outbox existed.',
    })
    print('FAILED_DISPATCH_RECOVERY_PASS', args.request_id, args.failed_run_id, incident_path.relative_to(ROOT))


if __name__ == '__main__':
    main()

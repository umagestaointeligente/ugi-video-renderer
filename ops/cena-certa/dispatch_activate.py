#!/usr/bin/env python3
"""Single sanctioned activation path for Cena Certa production.

It is intentionally local and zero-network. It refuses a second active request,
refuses to overwrite a pending publisher outbox, revalidates the exact immutable
batch before any dispatch write, binds its SHA and writes a unique request_id for
CAS protection in the production workflow. It does not commit, schedule or publish.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import pathlib
import sys
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[2]
OPS = ROOT / 'ops/cena-certa'
FACTORY_SRC = ROOT / 'vendor/cena-certa-factory-v2/src'
DISPATCH = OPS / 'dispatch.json'
OUTBOX = OPS / 'publisher-outbox.json'
STATE = OPS / 'publisher-state.json'
APPROVAL = OPS / 'human-approval.json'
sys.path.insert(0, str(FACTORY_SRC))
from factory.cena_certa.v2.preflight import validate_batch  # noqa: E402


def load(path: pathlib.Path) -> dict:
    obj = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(obj, dict):
        raise SystemExit(f'JSON_OBJECT_REQUIRED {path.name}')
    return obj


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--batch', required=True)
    ap.add_argument('--note', default='Canonical single-run production request.')
    args = ap.parse_args()

    current = load(DISPATCH)
    if current.get('schema') != 'CENA_CERTA_PRODUCTION_DISPATCH_V1':
        raise SystemExit('DISPATCH_SCHEMA_FAIL')
    if current.get('enabled') is True or str(current.get('mode') or '').upper() != 'IDLE':
        raise SystemExit('DISPATCH_ALREADY_ACTIVE')
    if any(str(current.get(k) or '') for k in ('batch_path','batch_sha256','prepared_run_id','requested_at','request_id')):
        raise SystemExit('DISPATCH_IDLE_STATE_DIRTY')

    outbox = load(OUTBOX); state = load(STATE); approval = load(APPROVAL)
    if outbox.get('items'):
        raise SystemExit('PENDING_OUTBOX_MUST_BE_RECONCILED_BEFORE_NEW_DISPATCH')
    if state.get('state') not in ('IDLE','PUBLISH_RECONCILED'):
        raise SystemExit(f'PUBLISHER_STATE_NOT_READY {state.get("state")}')
    if approval.get('approved') is True:
        raise SystemExit('ORPHAN_APPROVAL_MUST_BE_CLOSED_BEFORE_NEW_DISPATCH')

    batch = pathlib.Path(args.batch)
    if not batch.is_absolute():
        batch = (ROOT / batch).resolve()
    batch_dir = (OPS / 'batches').resolve()
    try:
        rel = batch.relative_to(ROOT.resolve())
        batch.relative_to(batch_dir)
    except ValueError as e:
        raise SystemExit('DISPATCH_BATCH_PATH_FAIL') from e
    if not batch.is_file() or batch.suffix != '.json':
        raise SystemExit('DISPATCH_BATCH_MISSING')

    # Re-run the full zero-network batch gate immediately before activation.
    # This catches expired ready/readback timestamps, stale schedules, title/CC
    # overflow and policy drift before a commit can wake any production runner.
    validate_batch(batch, expect=10)

    digest = hashlib.sha256(batch.read_bytes()).hexdigest()
    request_id = uuid.uuid4().hex
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    payload = {
        'schema':'CENA_CERTA_PRODUCTION_DISPATCH_V1',
        'enabled':True,
        'mode':'PREPARE',
        'batch_path':rel.as_posix(),
        'batch_sha256':digest,
        'prepared_run_id':'',
        'requested_at':now,
        'request_id':request_id,
        'note':str(args.note).strip() or 'Canonical single-run production request.'
    }
    tmp = DISPATCH.with_name(DISPATCH.name + f'.tmp-{os.getpid()}')
    try:
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        os.replace(tmp, DISPATCH)
    finally:
        tmp.unlink(missing_ok=True)
    print('DISPATCH_ACTIVATE_PASS')
    print('pre_dispatch_batch_revalidation=true')
    print('request_id=' + request_id)
    print('batch_path=' + rel.as_posix())
    print('batch_sha256=' + digest)
    print('next_action=review_and_commit_dispatch_json')
    print('scheduling=false publication=false')


if __name__ == '__main__':
    main()

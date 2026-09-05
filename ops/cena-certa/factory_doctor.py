#!/usr/bin/env python3
"""Zero-network proactive audit for the Cena Certa factory.

The doctor is deliberately cheap: no render, no external API, no scheduler write.
It validates state, geometry, critical code invariants and the absence of known
dead routes before expensive work starts.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
OPS = ROOT / 'ops/cena-certa'
FACTORY_ROOT = ROOT / 'vendor/cena-certa-factory-v2/src'
ENGINE = FACTORY_ROOT / 'factory/cena_certa/v2'
WORKFLOWS = ROOT / '.github/workflows'


def fail(msg: str) -> None:
    raise SystemExit(msg)


def load_json(path: pathlib.Path) -> dict:
    try:
        obj = json.loads(path.read_text(encoding='utf-8'))
    except Exception as e:
        fail(f'DOCTOR_JSON_FAIL {path.relative_to(ROOT)} {type(e).__name__}')
    if not isinstance(obj, dict):
        fail(f'DOCTOR_JSON_OBJECT_REQUIRED {path.relative_to(ROOT)}')
    return obj


def _rect(v, name: str, width: int, height: int) -> tuple[int, int, int, int]:
    if not isinstance(v, list) or len(v) != 4:
        fail(f'DOCTOR_RECT_FAIL {name}')
    x, y, w, h = (int(x) for x in v)
    if x < 0 or y < 0 or w <= 0 or h <= 0 or x + w > width or y + h > height:
        fail(f'DOCTOR_RECT_OUT_OF_CANVAS {name} {v}')
    return x, y, w, h


def _overlap(a, b) -> bool:
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def _contains(outer, inner) -> bool:
    ox, oy, ow, oh = outer; ix, iy, iw, ih = inner
    return ix >= ox and iy >= oy and ix + iw <= ox + ow and iy + ih <= oy + oh


def check_geometry_and_mask() -> None:
    c = load_json(ENGINE / 'contract_v9_factory.json')
    if c.get('schema') != 'ORBIT_CENA_CERTA_FACTORY_V2' or c.get('fail_closed') is not True:
        fail('DOCTOR_CONTRACT_SCHEMA_FAIL')
    if c.get('visual_precedence') != 'APPROVED_FRAME_OVER_TABLE':
        fail('DOCTOR_VISUAL_PRECEDENCE_FAIL')
    width = int(c['canvas']['width']); height = int(c['canvas']['height'])
    if (width, height, int(c['canvas']['fps'])) != (1080, 1920, 30):
        fail('DOCTOR_CANVAS_FAIL')
    geo = c['geometry_approved_frame_1080x1920']
    rects = {k: _rect(geo[k], k, width, height) for k in ('title_panel','title_static_anchor','story_logo','film_window','cc_reference_bbox','cc_safe_zone','footer')}
    cc = rects['cc_safe_zone']
    if not _contains(cc, rects['cc_reference_bbox']):
        fail('DOCTOR_CC_REFERENCE_OUTSIDE_SAFE_ZONE')
    for name in ('title_panel','title_static_anchor','story_logo','film_window','footer'):
        if _overlap(cc, rects[name]):
            fail(f'DOCTOR_CC_STATIC_COLLISION {name}')
    if rects['film_window'][1] + rects['film_window'][3] >= cc[1]:
        fail('DOCTOR_FILM_CC_VERTICAL_ORDER_FAIL')
    if cc[1] + cc[3] >= rects['footer'][1]:
        fail('DOCTOR_CC_FOOTER_VERTICAL_ORDER_FAIL')
    if list(geo.get('cta_full') or []) != [0, 0, width, height]:
        fail('DOCTOR_CTA_FULL_FRAME_FAIL')
    if int(c['selection']['film_default_min_year']) != 1995 or int(c['selection']['film_exception_min_year']) != 1985:
        fail('DOCTOR_FILM_YEAR_POLICY_DRIFT')
    for key in ('story','cta'):
        spec = c['approved_visual_sources'][key]
        p = FACTORY_ROOT / spec['path']
        if not p.is_file() or not spec.get('git_blob_sha1') or not spec.get('library_byte_sha256') or not spec.get('pixel_sha256'):
            fail(f'DOCTOR_PHYSICAL_MASTER_LOCK_FAIL {key}')
    render = (ENGINE / 'render.py').read_text(encoding='utf-8')
    order = [render.find("[film]subtitles='"), render.find('[captioned][ttl]overlay='), render.find('[titled][mask]overlay=0:0')]
    if min(order) < 0 or order != sorted(order):
        fail('DOCTOR_MASK_COMPOSITE_ORDER_FAIL')
    if "'mask_composite_order':'FILM_CC_TITLE_THEN_FINAL_STATIC_MASK'" not in render:
        fail('DOCTOR_MASK_RECEIPT_MARKER_MISSING')
    print('DOCTOR_MASK_GEOMETRY_PASS')


def check_code_and_routes() -> None:
    common = (ENGINE / 'common.py').read_text(encoding='utf-8')
    r2 = (OPS / 'r2_stage.py').read_text(encoding='utf-8')
    prod = (WORKFLOWS / 'cena-certa-production-v2.yml').read_text(encoding='utf-8')
    if '--retry-all-errors' in common:
        fail('DOCTOR_BLIND_SOURCE_RETRY_PRESENT')
    if 'R2_TRANSIENT_HTTP' not in r2 or 'blind_retry_used' not in r2:
        fail('DOCTOR_R2_RETRY_CLASSIFIER_MISSING')
    for token in ('factory_doctor.py', 'ready_matrix', 'request_id', '[skip ci]'):
        if token not in prod:
            fail(f'DOCTOR_PRODUCTION_INVARIANT_MISSING {token}')
    forbidden = (
        'vendor/cena-certa-factory-v2/assets-b64',
        'vendor/cena-certa-factory-v2/payload-exact-v1',
        'vendor/cena-certa-factory-v2/payload-test',
        'vendor/cena-certa-factory-v2/payload-v2',
        '.github/workflows/cena-certa-gitlab-r2-bridge-20260903.yml',
        '.github/workflows/cena-certa-snapshot-sync-once.yml',
        'ops/cena-certa/ready-assets-dispatch.json',
    )
    present = [p for p in forbidden if (ROOT / p).exists()]
    if present:
        fail('DOCTOR_DEAD_ROUTE_OR_LITTER_PRESENT ' + ','.join(present))
    if not (OPS / 'dispatch_activate.py').is_file() or not (OPS / 'batch_admit.py').is_file():
        fail('DOCTOR_CANONICAL_ENTRYPOINT_MISSING')
    print('DOCTOR_CODE_ROUTE_PASS')


def check_state() -> None:
    dispatch = load_json(OPS / 'dispatch.json')
    outbox = load_json(OPS / 'publisher-outbox.json')
    approval = load_json(OPS / 'human-approval.json')
    state = load_json(OPS / 'publisher-state.json')
    if dispatch.get('schema') != 'CENA_CERTA_PRODUCTION_DISPATCH_V1':
        fail('DOCTOR_DISPATCH_SCHEMA_FAIL')
    enabled = dispatch.get('enabled') is True
    mode = str(dispatch.get('mode') or '').upper()
    if not enabled:
        if mode != 'IDLE' or any(str(dispatch.get(k) or '') for k in ('batch_path','batch_sha256','prepared_run_id','requested_at','request_id')):
            fail('DOCTOR_IDLE_DISPATCH_DIRTY')
    else:
        if mode != 'PREPARE' or str(dispatch.get('prepared_run_id') or ''):
            fail('DOCTOR_ACTIVE_DISPATCH_MODE_FAIL')
        if not re.fullmatch(r'[A-Za-z0-9._-]{12,96}', str(dispatch.get('request_id') or '')):
            fail('DOCTOR_ACTIVE_DISPATCH_REQUEST_ID_FAIL')
        if not str(dispatch.get('batch_path') or '').startswith('ops/cena-certa/batches/'):
            fail('DOCTOR_ACTIVE_DISPATCH_BATCH_PATH_FAIL')
        if not re.fullmatch(r'[0-9a-f]{64}', str(dispatch.get('batch_sha256') or '').lower()):
            fail('DOCTOR_ACTIVE_DISPATCH_BATCH_SHA_FAIL')
    items = outbox.get('items')
    if not isinstance(items, list):
        fail('DOCTOR_OUTBOX_ITEMS_FAIL')
    if items:
        if len(items) != 8 or int(outbox.get('expected_network_placements') or 0) != 32:
            fail('DOCTOR_OUTBOX_COUNT_FAIL')
        h = outbox.get('handoff_sha256'); run = outbox.get('production_run_id')
        if not h or not run:
            fail('DOCTOR_OUTBOX_IDENTITY_FAIL')
        if approval.get('handoff_sha256') != h or approval.get('production_run_id') != run:
            fail('DOCTOR_APPROVAL_OUTBOX_MISMATCH')
        if state.get('handoff_sha256') != h or state.get('production_run_id') != run:
            fail('DOCTOR_PUBLISHER_STATE_OUTBOX_MISMATCH')
    else:
        if outbox.get('state') != 'EMPTY':
            fail('DOCTOR_EMPTY_OUTBOX_STATE_FAIL')
        if approval.get('approved') is True:
            fail('DOCTOR_ORPHAN_APPROVAL_FAIL')
        if state.get('state') == 'AWAITING_HUMAN_APPROVAL':
            fail('DOCTOR_ORPHAN_PUBLISHER_WAIT_FAIL')
    if state.get('blind_retry_forbidden') is not True:
        fail('DOCTOR_PUBLISHER_BLIND_RETRY_GUARD_FAIL')
    print('DOCTOR_STATE_PASS')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--state-only', action='store_true')
    args = ap.parse_args()
    check_state()
    if not args.state_only:
        check_geometry_and_mask()
        check_code_and_routes()
        print('CENA_CERTA_FACTORY_DOCTOR_PASS zero_network=true render=false external_writes=false')
    else:
        print('CENA_CERTA_FACTORY_DOCTOR_STATE_PASS')


if __name__ == '__main__':
    main()

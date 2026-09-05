#!/usr/bin/env python3
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
REGISTRY = ROOT / 'ops/cena-certa/route-registry.json'
PRODUCTION = ROOT / '.github/workflows/cena-certa-production-v2.yml'
R2_STAGE = ROOT / 'ops/cena-certa/r2_stage.py'
CONTRACT = ROOT / 'vendor/cena-certa-factory-v2/src/factory/cena_certa/v2/contract_v9_factory.json'


def fail(msg: str) -> None:
    raise SystemExit(msg)


def main() -> None:
    reg = json.loads(REGISTRY.read_text(encoding='utf-8'))
    if reg.get('schema') != 'CENA_CERTA_ROUTE_REGISTRY_V1' or reg.get('fail_closed') is not True:
        fail('ROUTE_REGISTRY_SCHEMA_FAIL')

    prod = reg['production_route']
    for key in ('render_executor', 'media_delivery'):
        route = prod[key]
        if route.get('required_for_render') is not True or route.get('state') != 'ACTIVE':
            fail(f'REQUIRED_RENDER_ROUTE_NOT_ACTIVE {key}')

    render = prod['render_executor']
    if render.get('runtime_gitlab_clone') is not False:
        fail('RUNTIME_GITLAB_CLONE_FORBIDDEN')
    if [render.get('candidate_pool'), render.get('final_videos'), render.get('hot_reserves')] != [10, 8, 2]:
        fail('N_PLUS_2_ROUTE_CONTRACT_FAIL')

    media = prod['media_delivery']
    if media.get('auth_header') != 'x-ugi-video-upload-key':
        fail('R2_AUTH_HEADER_ROUTE_FAIL')
    if media.get('blind_post_retry') is not False:
        fail('R2_BLIND_RETRY_ROUTE_FAIL')
    if media.get('ambiguous_response_reconciliation') != 'PUBLIC_HEAD_EXACT_SIZE':
        fail('R2_AMBIGUOUS_RECONCILIATION_ROUTE_FAIL')

    secondary = prod['scheduler_secondary']
    if sorted(secondary.get('networks') or []) != ['facebook', 'youtube']:
        fail('SECONDARY_ROUTE_NETWORK_SCOPE_FAIL')
    if sorted(secondary.get('unsupported_networks') or []) != ['instagram', 'tiktok']:
        fail('SECONDARY_ROUTE_UNSUPPORTED_SCOPE_FAIL')
    if secondary.get('never_treat_partial_as_full_redundancy') is not True:
        fail('SECONDARY_ROUTE_REDUNDANCY_GUARD_FAIL')

    workflow = PRODUCTION.read_text(encoding='utf-8')
    forbidden_runtime_tokens = (
        'git clone',
        'gitlab.com/umagestaointeligente-group/umagestaointeligente-project',
        'ready-assets-dispatch.json',
        'cena-certa-gitlab-r2-bridge-20260903',
    )
    for token in forbidden_runtime_tokens:
        if token in workflow:
            fail(f'DEAD_ROUTE_REFERENCE_IN_PRODUCTION {token}')

    r2 = R2_STAGE.read_text(encoding='utf-8')
    if "'x-ugi-video-upload-key': key" not in r2:
        fail('R2_DEDICATED_AUTH_HEADER_MISSING')
    if "'Authorization': f'Bearer {key}'" in r2:
        fail('R2_BEARER_AUTH_FORBIDDEN')
    if 'blind_retry_used' not in r2 or '_head_exact' not in r2:
        fail('R2_RECONCILIATION_GUARD_MISSING')

    contract = json.loads(CONTRACT.read_text(encoding='utf-8'))
    if int(contract['sla']['candidate_pool_size']) != 10:
        fail('CONTRACT_CANDIDATE_POOL_FAIL')
    if int(contract['sla']['daily_batch_size']) != 8 or int(contract['sla']['hot_reserve_count']) != 2:
        fail('CONTRACT_8_PLUS_2_FAIL')
    if contract['continuity']['secondary_route']['networks'] != ['facebook', 'youtube']:
        fail('CONTRACT_SECONDARY_ROUTE_SCOPE_FAIL')
    if contract['state_rules']['schedule_retry_requires_live_reconciliation'] is not True:
        fail('CONTRACT_SCHEDULE_RECONCILE_GUARD_FAIL')

    workflow_dir = ROOT / '.github/workflows'
    forbidden_files = (
        'cena-certa-gitlab-r2-bridge-20260903.yml',
        'cena-certa-snapshot-sync-once.yml',
        'cena-certa-ready-assets-v2.yml',
        'cena-certa-factory-v2.yml',
        'cena-certa-route-b-replay.yml',
    )
    leftovers = [name for name in forbidden_files if (workflow_dir / name).exists()]
    if leftovers:
        fail('DEAD_CENA_CERTA_WORKFLOW_PRESENT ' + ','.join(leftovers))

    disabled = reg.get('disabled_routes') or []
    if any(x.get('allowed_in_production') is not False for x in disabled):
        fail('DISABLED_ROUTE_ALLOWED_IN_PRODUCTION')

    print('CENA_CERTA_ROUTE_GUARD_PASS')
    print('ACTIVE_RENDER_ROUTE', render['id'])
    print('ACTIVE_MEDIA_ROUTE', media['id'])
    print('SECONDARY_SCHEDULER_SCOPE', ','.join(secondary['networks']))
    print('UNSUPPORTED_SECONDARY_NETWORKS', ','.join(secondary['unsupported_networks']))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from .common import contract
from .publish_reconcile import reconcile_publication

NETWORKS = ['facebook', 'instagram', 'tiktok', 'youtube']


def handoff(due):
    rows = []
    flat = []
    for i in range(8):
        rid = f'CC-PUBLISH-SELFTEST-{i:02d}'
        idem = f'idem-{i}'
        placements = []
        for n in NETWORKS:
            pk = f'{idem}:{n}'
            placements.append({'network': n, 'placementKey': pk})
            flat.append({'id': rid, 'idempotencyKey': idem, 'network': n, 'placementKey': pk})
        rows.append({'id': rid, 'date': due.isoformat(), 'idempotencyKey': idem, 'expectedPlacements': placements})
    return {'items': rows, 'expectedPlacements': flat, 'expectedNetworkPlacements': 32}


def scheduled(h, observed_at):
    out = []
    for r in h['items']:
        for p in r['expectedPlacements']:
            out.append({
                'id': r['id'], 'network': p['network'], 'placementKey': p['placementKey'],
                'status': 'SCHEDULED', 'observedAt': observed_at.isoformat(),
                'providerPostId': f"provider-{r['id']}",
            })
    return out


def published(h, observed_at, evidence='PLATFORM_NATIVE_READBACK'):
    out = []
    for r in h['items']:
        for p in r['expectedPlacements']:
            row = {
                'id': r['id'], 'network': p['network'], 'placementKey': p['placementKey'],
                'status': 'PUBLISHED', 'observedAt': observed_at.isoformat(),
                'providerPostId': f"native-{r['id']}-{p['network']}",
                'evidenceType': evidence,
            }
            if evidence == 'PLATFORM_NATIVE_READBACK':
                row['nativeReadbackOk'] = True
            else:
                row['permalink'] = f"https://example.invalid/{r['id']}/{p['network']}"
                row['publicProbeOk'] = True
            out.append(row)
    return out


def replace(obs, rid, network, **changes):
    return [{**x, **changes} if x['id'] == rid and x['network'] == network else x for x in obs]


def remove(obs, rid, network):
    return [x for x in obs if not (x['id'] == rid and x['network'] == network)]


def run():
    c = contract()
    grace = int(c['publication_reconciliation']['post_due_grace_seconds'])
    base = datetime(2026, 9, 6, 15, 0, tzinfo=timezone.utc)

    # 1. Scheduled is blue, never publication-green.
    due = base + timedelta(minutes=20)
    h = handoff(due)
    r = reconcile_publication(h, scheduled(h, base), now=base)
    assert r['state'] == 'SCHEDULE_READBACK_CONFIRMED' and r['uiStatus'] == 'BLUE'
    assert r['counts']['published_confirmed'] == 0

    # 2. A scheduled placement disappearing before due is a recovery condition.
    obs = remove(scheduled(h, base), h['items'][0]['id'], 'instagram')
    r = reconcile_publication(h, obs, now=base)
    assert r['state'] == 'RECOVERY_REQUIRED'
    assert any(x['decision'] == 'RECOVERY_REQUIRED_PRE_DUE' for x in r['rows'])

    # 3. Disappearing just after due is ambiguous, not success.
    due = base - timedelta(seconds=30)
    h = handoff(due)
    obs = remove(scheduled(h, base), h['items'][0]['id'], 'tiktok')
    r = reconcile_publication(h, obs, now=base)
    assert r['state'] == 'PUBLISH_CONFIRMATION_PENDING' and r['uiStatus'] == 'AMBER'

    # 4. All 32 need independent positive evidence for the only green final state.
    due = base - timedelta(seconds=grace + 30)
    h = handoff(due)
    r = reconcile_publication(h, published(h, base), now=base)
    assert r['state'] == 'PUBLISH_RECONCILED' and r['uiStatus'] == 'GREEN'
    assert r['counts']['published_confirmed'] == 32

    # 5. Provider says PUBLISHED but independent evidence is missing: never green.
    bad = published(h, base)
    bad = replace(bad, h['items'][0]['id'], 'facebook', evidenceType='PROVIDER_RESULT', nativeReadbackOk=False)
    r = reconcile_publication(h, bad, now=base)
    assert r['state'] == 'RECOVERY_REQUIRED'
    assert r['counts']['published_confirmed'] == 31

    # 6. PROCESSING past grace is stuck and requires recovery.
    bad = published(h, base)
    bad = replace(bad, h['items'][0]['id'], 'youtube', status='PROCESSING', evidenceType=None, nativeReadbackOk=False)
    r = reconcile_publication(h, bad, now=base)
    assert r['state'] == 'RECOVERY_REQUIRED'
    assert any(x['reason'] == 'STUCK_PROCESSING_AFTER_DUE' for x in r['rows'])

    # 7. Explicit failure permits an idempotent recovery/failover decision, not blind success.
    bad = published(h, base)
    bad = replace(bad, h['items'][0]['id'], 'facebook', status='FAILED', evidenceType=None, nativeReadbackOk=False)
    r = reconcile_publication(h, bad, now=base, secondary_health={'facebook': True})
    assert r['state'] == 'RECOVERY_REQUIRED'
    assert r['counts']['retry_allowed'] == 1

    # 8. A stale observation cannot satisfy publication confirmation.
    stale = published(h, base - timedelta(seconds=int(c['publication_reconciliation']['max_observation_age_seconds']) + 60))
    r = reconcile_publication(h, stale, now=base)
    assert r['state'] == 'RECOVERY_REQUIRED'
    assert r['counts']['published_confirmed'] == 0

    # 9. Wrong placement key is evidence corruption and must fail closed.
    corrupt = published(h, base)
    corrupt[0] = {**corrupt[0], 'placementKey': 'wrong-placement-key'}
    try:
        reconcile_publication(h, corrupt, now=base)
    except RuntimeError as e:
        assert 'OBSERVATION_PLACEMENT_KEY_MISMATCH' in str(e)
    else:
        raise AssertionError('placement-key corruption must fail')

    # 10. Primary+secondary both published is a duplicate, not extra confidence.
    primary = published(h, base)
    secondary = [dict(primary[0])]
    try:
        reconcile_publication(h, primary, secondary, now=base)
    except RuntimeError as e:
        assert 'DUPLICATE_CROSS_ROUTE_PUBLISHED' in str(e)
    else:
        raise AssertionError('cross-route duplicate must fail')

    # 11. Published before the due window is an anomaly, not green.
    due = base + timedelta(minutes=20)
    h = handoff(due)
    r = reconcile_publication(h, published(h, base), now=base)
    assert r['state'] == 'RECOVERY_REQUIRED'
    assert all(x['decision'] == 'RECOVERY_REQUIRED_EARLY_PUBLISH' for x in r['rows'])

    # 12. Public permalink evidence must include a successful public probe.
    due = base - timedelta(seconds=grace + 30)
    h = handoff(due)
    rows = published(h, base, evidence='PUBLIC_PERMALINK_PROBE')
    rows[0]['publicProbeOk'] = False
    r = reconcile_publication(h, rows, now=base)
    assert r['state'] == 'RECOVERY_REQUIRED'
    assert r['counts']['published_confirmed'] == 31

    print('FACTORY_V2_PUBLICATION_FALSE_POSITIVE_SELFTEST_PASS cases=12 placements=32 final_green_requires_independent_positive_evidence')


if __name__ == '__main__':
    run()

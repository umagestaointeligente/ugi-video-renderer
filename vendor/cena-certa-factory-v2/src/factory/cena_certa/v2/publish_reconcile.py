#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from .common import contract, safe_id

SCHEDULED = {'SCHEDULED'}
PUBLISHED = {'POSTED', 'PUBLISHED'}
AMBIGUOUS = {'ACCEPTED', 'QUEUED', 'PENDING', 'PROCESSING', 'UNKNOWN', 'TIMEOUT_AFTER_SEND', 'RESPONSE_LOST'}
FAILED = {'FAILED', 'ERROR', 'REJECTED', 'CANCELLED', 'EXPIRED'}
INDEPENDENT_EVIDENCE = {'PLATFORM_NATIVE_READBACK', 'PUBLIC_PERMALINK_PROBE'}


def _dt(value):
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    s = str(value or '').strip()
    if not s:
        raise RuntimeError('TIMESTAMP_MISSING')
    if s.endswith('Z'):
        s = s[:-1] + '+00:00'
    d = datetime.fromisoformat(s)
    if d.tzinfo is None:
        raise RuntimeError(f'TIMESTAMP_TZ_MISSING {value!r}')
    return d.astimezone(timezone.utc)


def _expected(handoff):
    rows = []
    seen = set()
    for item in handoff.get('items') or []:
        rid = safe_id(item['id'])
        due = _dt(item['date'])
        idem = str(item['idempotencyKey'])
        for p in item.get('expectedPlacements') or []:
            network = str(p['network']).lower().strip()
            placement_key = str(p['placementKey'])
            key = (rid, network)
            if key in seen:
                raise RuntimeError(f'EXPECTED_PLACEMENT_DUPLICATE {rid} {network}')
            seen.add(key)
            rows.append({
                'id': rid,
                'network': network,
                'placementKey': placement_key,
                'idempotencyKey': idem,
                'dueAt': due,
            })
    return rows


def _index(observations, label, max_age_seconds, now):
    idx = {}
    for raw in observations or []:
        rid = safe_id(raw.get('id'))
        network = str(raw.get('network') or '').lower().strip()
        if not network:
            raise RuntimeError(f'OBSERVATION_NETWORK_MISSING {label} {rid}')
        key = (rid, network)
        if key in idx:
            raise RuntimeError(f'DUPLICATE_PUBLICATION_OBSERVATION {label} {rid} {network}')
        row = dict(raw)
        observed_at = _dt(row.get('observedAt'))
        age = (now - observed_at).total_seconds()
        row['_observedAt'] = observed_at
        row['_ageSeconds'] = age
        row['_fresh'] = -30 <= age <= max_age_seconds
        idx[key] = row
    return idx


def _positive_evidence(row):
    evidence_type = str(row.get('evidenceType') or '').upper()
    post_id = str(row.get('providerPostId') or '').strip()
    if evidence_type not in INDEPENDENT_EVIDENCE:
        return False, 'INDEPENDENT_EVIDENCE_MISSING'
    if not post_id:
        return False, 'PROVIDER_POST_ID_MISSING'
    if evidence_type == 'PUBLIC_PERMALINK_PROBE':
        permalink = str(row.get('permalink') or '').strip()
        if not permalink.startswith('https://') or row.get('publicProbeOk') is not True:
            return False, 'PUBLIC_PERMALINK_PROBE_INVALID'
    if evidence_type == 'PLATFORM_NATIVE_READBACK' and row.get('nativeReadbackOk') is not True:
        return False, 'PLATFORM_NATIVE_READBACK_INVALID'
    return True, 'PASS'


def reconcile_publication(handoff, primary_obs, secondary_obs=None, *, now=None, secondary_health=None):
    c = contract()
    pcfg = c['publication_reconciliation']
    now = _dt(now or datetime.now(timezone.utc))
    expected = _expected(handoff)
    required = int(c['scheduler']['expected_placements_per_batch'])
    if len(expected) != required:
        raise RuntimeError(f'EXPECTED_PUBLICATION_PLACEMENT_COUNT_FAIL {len(expected)} != {required}')

    max_age = int(pcfg['max_observation_age_seconds'])
    grace = int(pcfg['post_due_grace_seconds'])
    early_tol = int(pcfg['early_publish_tolerance_seconds'])
    primary = _index(primary_obs, 'primary', max_age, now)
    secondary = _index(secondary_obs or [], 'secondary', max_age, now)
    health = {str(k).lower(): bool(v) for k, v in (secondary_health or {}).items()}
    fallback_networks = set(c['continuity']['secondary_route']['networks'])

    counts = {
        'schedule_readback_confirmed': 0,
        'published_confirmed': 0,
        'confirmation_pending': 0,
        'recovery_required': 0,
        'retry_allowed': 0,
    }
    rows = []

    for exp in expected:
        key = (exp['id'], exp['network'])
        p = primary.get(key)
        s = secondary.get(key)

        for label, obs in (('primary', p), ('secondary', s)):
            if obs is None:
                continue
            observed_pk = str(obs.get('placementKey') or '')
            if observed_pk != exp['placementKey']:
                raise RuntimeError(f'OBSERVATION_PLACEMENT_KEY_MISMATCH {label} {exp["id"]} {exp["network"]}')

        if p and s:
            ps = str(p.get('status') or '').upper()
            ss = str(s.get('status') or '').upper()
            if ps in PUBLISHED and ss in PUBLISHED:
                raise RuntimeError(f'DUPLICATE_CROSS_ROUTE_PUBLISHED {exp["id"]} {exp["network"]}')
            if ps in SCHEDULED | AMBIGUOUS and ss in PUBLISHED:
                raise RuntimeError(f'SECONDARY_PUBLISHED_BEFORE_PRIMARY_ABSENCE_CONFIRMED {exp["id"]} {exp["network"]}')

        obs = p or s
        route = 'primary' if p else ('secondary' if s else 'none')
        status = str((obs or {}).get('status') or 'MISSING').upper()
        fresh = bool((obs or {}).get('_fresh'))
        due = exp['dueAt']
        seconds_after_due = (now - due).total_seconds()
        is_pre_due = seconds_after_due < -early_tol
        within_grace = -early_tol <= seconds_after_due <= grace
        after_grace = seconds_after_due > grace
        reason = None
        decision = None
        retry_allowed = False

        if obs and not fresh:
            status = 'STALE_OBSERVATION'
            obs = None

        if is_pre_due:
            if status in SCHEDULED:
                post_id = str((obs or {}).get('providerPostId') or '').strip()
                if post_id:
                    decision = 'SCHEDULE_READBACK_CONFIRMED'
                    counts['schedule_readback_confirmed'] += 1
                else:
                    decision = 'RECOVERY_REQUIRED_PRE_DUE'
                    reason = 'SCHEDULED_WITHOUT_PROVIDER_POST_ID'
            elif status in PUBLISHED:
                decision = 'RECOVERY_REQUIRED_EARLY_PUBLISH'
                reason = 'PUBLISHED_BEFORE_DUE_WINDOW'
            elif status in AMBIGUOUS:
                decision = 'SCHEDULE_CONFIRMATION_PENDING'
                reason = status
                counts['confirmation_pending'] += 1
            else:
                decision = 'RECOVERY_REQUIRED_PRE_DUE'
                reason = status
                retry_allowed = status in FAILED
        else:
            if status in PUBLISHED:
                ok, evidence_reason = _positive_evidence(obs or {})
                if ok:
                    decision = 'PUBLISHED_CONFIRMED'
                    counts['published_confirmed'] += 1
                elif after_grace:
                    decision = 'RECOVERY_REQUIRED'
                    reason = evidence_reason
                else:
                    decision = 'PUBLISH_CONFIRMATION_PENDING'
                    reason = evidence_reason
                    counts['confirmation_pending'] += 1
            elif status in FAILED:
                decision = 'RECOVERY_REQUIRED'
                reason = status
                retry_allowed = True
            elif status in SCHEDULED:
                if after_grace:
                    decision = 'RECOVERY_REQUIRED'
                    reason = 'STUCK_SCHEDULED_AFTER_DUE'
                else:
                    decision = 'PUBLISH_CONFIRMATION_PENDING'
                    reason = 'STILL_SCHEDULED'
                    counts['confirmation_pending'] += 1
            elif status in AMBIGUOUS:
                if after_grace:
                    decision = 'RECOVERY_REQUIRED'
                    reason = f'STUCK_{status}_AFTER_DUE'
                else:
                    decision = 'PUBLISH_CONFIRMATION_PENDING'
                    reason = status
                    counts['confirmation_pending'] += 1
            else:
                if after_grace:
                    decision = 'RECOVERY_REQUIRED'
                    reason = 'MISSING_AFTER_DUE_GRACE'
                else:
                    decision = 'PUBLISH_CONFIRMATION_PENDING'
                    reason = 'MISSING_WITHIN_DUE_GRACE'
                    counts['confirmation_pending'] += 1

        if decision and decision.startswith('RECOVERY_REQUIRED'):
            counts['recovery_required'] += 1
        if retry_allowed:
            counts['retry_allowed'] += 1

        fallback_healthy = exp['network'] in fallback_networks and health.get(exp['network']) is True
        rows.append({
            **{k: v for k, v in exp.items() if k != 'dueAt'},
            'dueAt': due.isoformat(),
            'routeObserved': route,
            'observedStatus': status,
            'observedAt': (obs or {}).get('observedAt'),
            'providerPostId': (obs or {}).get('providerPostId'),
            'decision': decision,
            'reason': reason,
            'retryAllowed': retry_allowed,
            'secondaryFallbackHealthy': fallback_healthy,
            'secondsAfterDue': round(seconds_after_due, 3),
        })

    if counts['published_confirmed'] == required:
        state = 'PUBLISH_RECONCILED'
        ui = 'GREEN'
    elif counts['recovery_required'] > 0:
        state = 'RECOVERY_REQUIRED'
        ui = 'RED'
    elif counts['schedule_readback_confirmed'] == required:
        state = 'SCHEDULE_READBACK_CONFIRMED'
        ui = 'BLUE'
    else:
        state = 'PUBLISH_CONFIRMATION_PENDING'
        ui = 'AMBER'

    return {
        'schema': 'CENA_CERTA_PUBLICATION_RECONCILIATION_V1',
        'state': state,
        'uiStatus': ui,
        'expectedPlacements': required,
        'counts': counts,
        'rows': rows,
        'failClosed': True,
        'scheduledNeverMeansPublished': True,
        'greenRequiresAllPlacementsPositiveIndependentEvidence': True,
        'blindRetryForbidden': True,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--handoff', required=True)
    ap.add_argument('--primary', required=True)
    ap.add_argument('--secondary')
    ap.add_argument('--secondary-health')
    ap.add_argument('--now')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    h = json.loads(Path(a.handoff).read_text(encoding='utf-8'))
    p = json.loads(Path(a.primary).read_text(encoding='utf-8'))
    s = json.loads(Path(a.secondary).read_text(encoding='utf-8')) if a.secondary else []
    health = json.loads(Path(a.secondary_health).read_text(encoding='utf-8')) if a.secondary_health else {}
    r = reconcile_publication(h, p, s, now=a.now, secondary_health=health)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + '.tmp')
    tmp.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(tmp, out)
    print('FACTORY_V2_PUBLISH_RECONCILE', r['state'], r['counts'])


if __name__ == '__main__':
    main()

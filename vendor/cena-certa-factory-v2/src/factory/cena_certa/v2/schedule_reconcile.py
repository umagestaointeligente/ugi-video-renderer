#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os
from pathlib import Path
from .common import contract, safe_id

GOOD={'SCHEDULED','POSTED','PUBLISHED'}
AMBIGUOUS={'ACCEPTED','QUEUED','PENDING','PROCESSING','UNKNOWN','TIMEOUT_AFTER_SEND','RESPONSE_LOST'}


def expected_placements(handoff):
    out=[]
    seen=set()
    for row in handoff.get('items') or []:
        rid=safe_id(row['id'])
        idem=str(row['idempotencyKey'])
        for p in row.get('expectedPlacements') or []:
            network=str(p['network']).lower().strip()
            placement_key=str(p['placementKey'])
            key=(rid,network)
            if key in seen:
                raise RuntimeError(f'EXPECTED_PLACEMENT_DUPLICATE {rid} {network}')
            seen.add(key)
            out.append({'id':rid,'network':network,'placementKey':placement_key,'idempotencyKey':idem})
    declared=handoff.get('expectedPlacements')
    if declared is not None:
        declared_keys={(str(x.get('id')),str(x.get('network')).lower(),str(x.get('placementKey'))) for x in declared}
        actual_keys={(x['id'],x['network'],x['placementKey']) for x in out}
        if declared_keys!=actual_keys:
            raise RuntimeError('EXPECTED_PLACEMENT_DECLARATION_MISMATCH')
    return out


def _index(observations,label):
    idx={}
    for row in observations or []:
        key=(str(row.get('id')),str(row.get('network')).lower())
        status=str(row.get('status','')).upper()
        if key in idx:
            prior=str(idx[key].get('status','')).upper()
            if prior in GOOD or prior in AMBIGUOUS or status in GOOD or status in AMBIGUOUS:
                raise RuntimeError(f'DUPLICATE_PLACEMENT_OBSERVED {label} {key[0]} {key[1]}')
        idx[key]=row
    return idx


def reconcile(handoff,primary_obs,secondary_obs=None,secondary_health=None,buffer_ok=False):
    c=contract()
    expected=expected_placements(handoff)
    if len(expected)!=int(c['scheduler']['expected_placements_per_batch']):
        raise RuntimeError(f'EXPECTED_PLACEMENT_COUNT_FAIL {len(expected)}')
    primary=_index(primary_obs,'primary')
    secondary=_index(secondary_obs or [],'secondary')
    health={str(k).lower():bool(v) for k,v in (secondary_health or {}).items()}
    fallback_networks=set(c['continuity']['secondary_route']['networks'])
    rows=[]
    counts={'confirmed':0,'fallback_allowed':0,'wait_reconcile':0,'stop_ship':0}
    for exp in expected:
        key=(exp['id'],exp['network'])
        ps=str((primary.get(key) or {}).get('status','MISSING')).upper()
        ss=str((secondary.get(key) or {}).get('status','MISSING')).upper()
        if ps in GOOD and ss in GOOD:
            raise RuntimeError(f'DUPLICATE_CROSS_ROUTE {exp["id"]} {exp["network"]}')
        if ps in AMBIGUOUS and ss in GOOD:
            raise RuntimeError(f'SECONDARY_USED_BEFORE_PRIMARY_RECONCILED {exp["id"]} {exp["network"]}')
        if ps in GOOD:
            decision='CONFIRMED_PRIMARY'; counts['confirmed']+=1
        elif ps in AMBIGUOUS:
            decision='WAIT_RECONCILE'; counts['wait_reconcile']+=1
        elif ss in GOOD:
            decision='CONFIRMED_SECONDARY'; counts['confirmed']+=1
        elif ss in AMBIGUOUS:
            decision='WAIT_RECONCILE'; counts['wait_reconcile']+=1
        elif exp['network'] in fallback_networks and health.get(exp['network']) is True:
            decision='FALLBACK_ALLOWED'; counts['fallback_allowed']+=1
        else:
            decision='STOP_SHIP_CONTINUITY'; counts['stop_ship']+=1
        rows.append({**exp,'primaryStatus':ps,'secondaryStatus':ss,'secondaryHealth':health.get(exp['network'],False),'decision':decision})
    if counts['confirmed']==len(expected):
        state='SCHEDULE_RECONCILED'
    elif counts['wait_reconcile']>0:
        state='WAIT_RECONCILE'
    elif counts['stop_ship']>0:
        state='STOP_SHIP_CONTINUITY'
    elif counts['fallback_allowed']>0:
        state='FALLBACK_REQUIRED'
    else:
        state='STOP_SHIP_CONTINUITY'
    return {
        'schema':'CENA_CERTA_PLACEMENT_RECONCILIATION_V3','state':state,'expected':len(expected),
        'counts':counts,'rows':rows,'fail_closed':True,'no_retry_on_ambiguous':True,
        'future_buffer_ok':bool(buffer_ok),'future_buffer_does_not_replace_current_placement':True
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--handoff',required=True)
    ap.add_argument('--primary',required=True)
    ap.add_argument('--secondary')
    ap.add_argument('--secondary-health')
    ap.add_argument('--buffer-ok',action='store_true')
    ap.add_argument('--out',required=True)
    a=ap.parse_args()
    h=json.loads(Path(a.handoff).read_text(encoding='utf-8'))
    p=json.loads(Path(a.primary).read_text(encoding='utf-8'))
    s=json.loads(Path(a.secondary).read_text(encoding='utf-8')) if a.secondary else []
    health=json.loads(Path(a.secondary_health).read_text(encoding='utf-8')) if a.secondary_health else {}
    r=reconcile(h,p,s,health,a.buffer_ok)
    out=Path(a.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    tmp=out.with_suffix(out.suffix+'.tmp')
    tmp.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    os.replace(tmp,out)
    print('FACTORY_V2_PLACEMENT_RECONCILE',r['state'],r['counts'])


if __name__=='__main__':
    main()

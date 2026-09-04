#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os
from pathlib import Path
from .common import contract, safe_id

GOOD={'SCHEDULED','POSTED','PUBLISHED','PROCESSING'}
AMBIGUOUS={'ACCEPTED','QUEUED','PENDING','UNKNOWN','TIMEOUT_AFTER_SEND','RESPONSE_LOST'}


def expected_placements(handoff):
    out=[]
    for row in handoff.get('items') or []:
        rid=safe_id(row['id'])
        for p in row.get('expectedPlacements') or []:
            out.append({'id':rid,'network':p['network'],'placementKey':p['placementKey'],'idempotencyKey':row['idempotencyKey']})
    return out


def _index(observations):
    idx={}
    for row in observations or []:
        key=(str(row.get('id')),str(row.get('network')).lower())
        if key in idx and str(idx[key].get('status','')).upper() in GOOD and str(row.get('status','')).upper() in GOOD:
            raise RuntimeError(f'DUPLICATE_PLACEMENT_OBSERVED {key[0]} {key[1]}')
        idx[key]=row
    return idx


def reconcile(handoff,primary_obs,secondary_obs=None,buffer_ok=False):
    c=contract(); expected=expected_placements(handoff)
    if len(expected)!=int(c['scheduler']['expected_placements_per_batch']): raise RuntimeError(f'EXPECTED_PLACEMENT_COUNT_FAIL {len(expected)}')
    primary=_index(primary_obs); secondary=_index(secondary_obs or []); fallback_networks=set(c['continuity']['secondary_route']['networks'])
    rows=[]; counts={'confirmed':0,'fallback_allowed':0,'wait_reconcile':0,'buffer_protected':0,'stop_ship':0}
    for exp in expected:
        key=(exp['id'],exp['network']); ps=str((primary.get(key) or {}).get('status','MISSING')).upper()
        if ps in GOOD: decision='CONFIRMED_PRIMARY'; counts['confirmed']+=1
        elif ps in AMBIGUOUS: decision='WAIT_RECONCILE'; counts['wait_reconcile']+=1
        else:
            ss=str((secondary.get(key) or {}).get('status','MISSING')).upper()
            if ss in GOOD: decision='CONFIRMED_SECONDARY'; counts['confirmed']+=1
            elif exp['network'] in fallback_networks: decision='FALLBACK_ALLOWED'; counts['fallback_allowed']+=1
            elif buffer_ok: decision='BUFFER_PROTECTED'; counts['buffer_protected']+=1
            else: decision='STOP_SHIP_CONTINUITY'; counts['stop_ship']+=1
        rows.append({**exp,'primaryStatus':ps,'secondaryStatus':str((secondary.get(key) or {}).get('status','MISSING')).upper(),'decision':decision})
    if counts['confirmed']==len(expected): state='SCHEDULE_RECONCILED'
    elif counts['wait_reconcile']>0: state='WAIT_RECONCILE'
    elif counts['stop_ship']>0: state='STOP_SHIP_CONTINUITY'
    elif counts['fallback_allowed']>0: state='FALLBACK_REQUIRED'
    else: state='BUFFER_PROTECTED'
    return {'schema':'CENA_CERTA_PLACEMENT_RECONCILIATION_V2','state':state,'expected':len(expected),'counts':counts,'rows':rows,'fail_closed':True,'no_retry_on_ambiguous':True}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--handoff',required=True); ap.add_argument('--primary',required=True); ap.add_argument('--secondary'); ap.add_argument('--buffer-ok',action='store_true'); ap.add_argument('--out',required=True); a=ap.parse_args()
    h=json.loads(Path(a.handoff).read_text(encoding='utf-8')); p=json.loads(Path(a.primary).read_text(encoding='utf-8')); s=json.loads(Path(a.secondary).read_text(encoding='utf-8')) if a.secondary else []
    r=reconcile(h,p,s,a.buffer_ok); out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True); tmp=out.with_suffix(out.suffix+'.tmp'); tmp.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8'); os.replace(tmp,out); print('FACTORY_V2_PLACEMENT_RECONCILE',r['state'],r['counts'])
if __name__=='__main__': main()

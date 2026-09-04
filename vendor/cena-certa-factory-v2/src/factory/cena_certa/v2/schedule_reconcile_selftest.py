#!/usr/bin/env python3
from __future__ import annotations
from .schedule_reconcile import reconcile
from .common import contract

def handoff():
    c=contract(); rows=[]
    for i in range(8):
        rid=f'CC-RECON-{i:02d}'; idem=f'idem-{i}'
        rows.append({'id':rid,'idempotencyKey':idem,'expectedPlacements':[{'network':n,'placementKey':f'{idem}:{n}'} for n in c['scheduler']['networks']]})
    return {'items':rows}

def obs(h,status='SCHEDULED'):
    return [{'id':r['id'],'network':p['network'],'status':status} for r in h['items'] for p in r['expectedPlacements']]

def run():
    h=handoff(); full=obs(h)
    r=reconcile(h,full); assert r['state']=='SCHEDULE_RECONCILED' and r['counts']['confirmed']==32
    ambiguous=list(full); ambiguous[0]={**ambiguous[0],'status':'TIMEOUT_AFTER_SEND'}
    r=reconcile(h,ambiguous); assert r['state']=='WAIT_RECONCILE' and r['counts']['wait_reconcile']==1
    miss_fb=[x for x in full if not (x['id']=='CC-RECON-00' and x['network']=='facebook')]
    r=reconcile(h,miss_fb); assert r['state']=='FALLBACK_REQUIRED' and r['counts']['fallback_allowed']==1
    secondary=[{'id':'CC-RECON-00','network':'facebook','status':'SCHEDULED'}]
    r=reconcile(h,miss_fb,secondary); assert r['state']=='SCHEDULE_RECONCILED' and r['counts']['confirmed']==32
    miss_ig=[x for x in full if not (x['id']=='CC-RECON-00' and x['network']=='instagram')]
    r=reconcile(h,miss_ig,buffer_ok=True); assert r['state']=='BUFFER_PROTECTED' and r['counts']['buffer_protected']==1
    r=reconcile(h,miss_ig,buffer_ok=False); assert r['state']=='STOP_SHIP_CONTINUITY' and r['counts']['stop_ship']==1
    duplicate=list(full)+[dict(full[0])]
    try: reconcile(h,duplicate)
    except RuntimeError as e: assert 'DUPLICATE_PLACEMENT_OBSERVED' in str(e)
    else: raise AssertionError('duplicate must fail')
    print('FACTORY_V2_RECONCILIATION_SELFTEST_PASS cases=7 placements=32')

if __name__=='__main__': run()

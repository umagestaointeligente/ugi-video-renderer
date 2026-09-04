#!/usr/bin/env python3
from __future__ import annotations
from .schedule_reconcile import reconcile, expected_placements
from .schedule_manifest import build_expected_placements
from .common import contract


def handoff():
    c=contract(); rows=[]; flat=[]
    for i in range(8):
        rid=f'CC-RECON-{i:02d}'; idem=f'idem-{i}'
        placements=build_expected_placements(rid,idem,c['scheduler']['networks'])
        rows.append({'id':rid,'idempotencyKey':idem,'expectedPlacements':placements})
        flat.extend({'id':rid,'idempotencyKey':idem,**p} for p in placements)
    return {'items':rows,'expectedPlacements':flat}


def obs(h,status='SCHEDULED'):
    return [{'id':r['id'],'network':p['network'],'status':status} for r in h['items'] for p in r['expectedPlacements']]


def run():
    h=handoff()
    assert len(expected_placements(h))==32
    full=obs(h)
    r=reconcile(h,full)
    assert r['state']=='SCHEDULE_RECONCILED' and r['counts']['confirmed']==32

    ambiguous=list(full); ambiguous[0]={**ambiguous[0],'status':'PROCESSING'}
    r=reconcile(h,ambiguous)
    assert r['state']=='WAIT_RECONCILE' and r['counts']['wait_reconcile']==1

    miss_fb=[x for x in full if not (x['id']=='CC-RECON-00' and x['network']=='facebook')]
    r=reconcile(h,miss_fb,secondary_health={'facebook':True})
    assert r['state']=='FALLBACK_REQUIRED' and r['counts']['fallback_allowed']==1
    r=reconcile(h,miss_fb,secondary_health={'facebook':False})
    assert r['state']=='STOP_SHIP_CONTINUITY' and r['counts']['stop_ship']==1

    secondary=[{'id':'CC-RECON-00','network':'facebook','status':'SCHEDULED'}]
    r=reconcile(h,miss_fb,secondary,secondary_health={'facebook':True})
    assert r['state']=='SCHEDULE_RECONCILED' and r['counts']['confirmed']==32

    miss_ig=[x for x in full if not (x['id']=='CC-RECON-00' and x['network']=='instagram')]
    r=reconcile(h,miss_ig,buffer_ok=True)
    assert r['state']=='STOP_SHIP_CONTINUITY' and r['counts']['stop_ship']==1
    assert r['future_buffer_ok'] is True

    duplicate=list(full)+[dict(full[0])]
    try:
        reconcile(h,duplicate)
    except RuntimeError as e:
        assert 'DUPLICATE_PLACEMENT_OBSERVED' in str(e)
    else:
        raise AssertionError('duplicate must fail')

    try:
        reconcile(h,full,[dict(full[0])],secondary_health={'facebook':True})
    except RuntimeError as e:
        assert 'DUPLICATE_CROSS_ROUTE' in str(e)
    else:
        raise AssertionError('cross-route duplicate must fail')

    primary_amb=list(full); primary_amb[0]={**primary_amb[0],'status':'TIMEOUT_AFTER_SEND'}
    try:
        reconcile(h,primary_amb,[dict(full[0])],secondary_health={'facebook':True})
    except RuntimeError as e:
        assert 'SECONDARY_USED_BEFORE_PRIMARY_RECONCILED' in str(e)
    else:
        raise AssertionError('secondary race must fail')

    print('FACTORY_V2_RECONCILIATION_SELFTEST_PASS cases=9 placements=32 manifest_contract=live')


if __name__=='__main__':
    run()

#!/usr/bin/env python3
from __future__ import annotations
import json, shutil
from pathlib import Path
from .aggregate import aggregate
from .common import OUT, contract


def _write_batch(path: Path):
    c=contract(); n=int(c['sla']['candidate_pool_size'])
    items=[{'id':f'CC-SMOKE-SLOT-{i:02d}'} for i in range(n)]
    path.write_text(json.dumps(items),encoding='utf-8')
    return items

def _seed(items):
    base=OUT/'CC-FACTORY-V2-SELFTEST.receipt.json'
    if not base.exists(): raise RuntimeError('SELFTEST_RECEIPT_MISSING')
    r=json.loads(base.read_text())
    for x in items:
        rid=x['id']; rr=dict(r); rr['id']=rid; rr['state']='PREVIEW_READY'; rr['render_pass']=True; rr['qa_pass']=True
        (OUT/f'{rid}.receipt.json').write_text(json.dumps(rr),encoding='utf-8')
        (OUT/f'{rid}.r2.json').write_text(json.dumps({'status':'ready','videoUrl':f'https://example.invalid/{rid}.mp4','videoKey':f'smoke/{rid}.mp4'}),encoding='utf-8')

def _remove(items, count):
    for x in items[:count]:
        p=OUT/f"{x['id']}.r2.json"
        if p.exists(): p.unlink()

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    batch=OUT/'smoke-pool.json'; items=_write_batch(batch); _seed(items)
    a=aggregate(batch,True)
    if a['selected_count']!=8 or a['reserve_count']!=2: raise RuntimeError('POOL_BASELINE_FAIL')
    _seed(items); _remove(items,1); a=aggregate(batch,True)
    if a['selected_count']!=8 or a['reserve_count']!=1: raise RuntimeError('POOL_ONE_FAIL_RECOVERY_FAIL')
    _seed(items); _remove(items,2); a=aggregate(batch,True)
    if a['selected_count']!=8 or a['reserve_count']!=0: raise RuntimeError('POOL_TWO_FAIL_RECOVERY_FAIL')
    _seed(items); _remove(items,3)
    try: aggregate(batch,True)
    except SystemExit: pass
    else: raise RuntimeError('POOL_THREE_FAIL_MUST_STOP')
    print('FACTORY_V2_BATCH_SMOKE_PASS 10_TO_8_PLUS_2 AND 1_2_FAIL_RECOVERY AND 3_FAIL_STOP')
if __name__=='__main__': run()

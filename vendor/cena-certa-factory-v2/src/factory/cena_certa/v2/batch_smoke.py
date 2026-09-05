#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from .aggregate import aggregate
from .common import OUT, contract, sha256


def _write_batch(path: Path):
    c=contract(); n=int(c['sla']['candidate_pool_size'])
    items=[{'id':f'CC-SMOKE-SLOT-{i:02d}'} for i in range(n)]
    path.write_text(json.dumps(items),encoding='utf-8')
    return items

def _seed(items,batch):
    base=OUT/'CC-FACTORY-V2-SELFTEST.receipt.json'
    if not base.exists(): raise RuntimeError('SELFTEST_RECEIPT_MISSING')
    r=json.loads(base.read_text()); batch_sha=sha256(batch)
    if not r.get('video_sha256'): raise RuntimeError('SELFTEST_VIDEO_HASH_MISSING')
    for x in items:
        rid=x['id']; rr=dict(r); rr['id']=rid; rr['state']='PREVIEW_READY'; rr['render_pass']=True; rr['qa_pass']=True
        (OUT/f'{rid}.receipt.json').write_text(json.dumps(rr),encoding='utf-8')
        r2={'schema':'CENA_CERTA_R2_RECEIPT_V2','id':rid,'batchSha256':batch_sha,'status':'ready','public_probe_pass':True,'public_head_size_match':True,'videoUrl':f'https://example.invalid/{rid}.mp4','videoKey':f'smoke/{rid}.mp4','contentSha256':rr['video_sha256']}
        (OUT/f'{rid}.r2.json').write_text(json.dumps(r2),encoding='utf-8')

def _remove(items, count):
    for x in items[:count]:
        p=OUT/f"{x['id']}.r2.json"
        if p.exists(): p.unlink()

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    batch=OUT/'smoke-pool.json'; items=_write_batch(batch)
    _seed(items,batch); a=aggregate(batch,True)
    if a['selected_count']!=8 or a['reserve_count']!=2: raise RuntimeError('POOL_BASELINE_FAIL')
    _seed(items,batch); _remove(items,1); a=aggregate(batch,True)
    if a['selected_count']!=8 or a['reserve_count']!=1: raise RuntimeError('POOL_ONE_FAIL_RECOVERY_FAIL')
    _seed(items,batch); _remove(items,2); a=aggregate(batch,True)
    if a['selected_count']!=8 or a['reserve_count']!=0: raise RuntimeError('POOL_TWO_FAIL_RECOVERY_FAIL')
    _seed(items,batch); _remove(items,3)
    try: aggregate(batch,True)
    except SystemExit: pass
    else: raise RuntimeError('POOL_THREE_FAIL_MUST_STOP')
    print('FACTORY_V2_BATCH_SMOKE_PASS 10_TO_8_PLUS_2 AND 1_2_FAIL_RECOVERY AND 3_FAIL_STOP')
if __name__=='__main__': run()

#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, json, os
from pathlib import Path
from .common import contract, safe_id
from .preflight import validate_item


def _stage_ok(staged,item):
    rid=safe_id(item['id'])
    receipt_path=staged/f'{rid}.receipt.json'; r2_path=staged/f'{rid}.r2.json'
    if not receipt_path.exists() or not r2_path.exists(): return False,'MISSING_STAGE_PROOF'
    try:
        rec=json.loads(receipt_path.read_text(encoding='utf-8')); r2=json.loads(r2_path.read_text(encoding='utf-8'))
    except Exception: return False,'STAGE_PROOF_PARSE_FAIL'
    if not (rec.get('render_pass') is True and rec.get('qa_pass') is True and rec.get('state')=='PREVIEW_READY'): return False,'RENDER_QA_NOT_READY'
    if r2.get('status')!='ready': return False,'R2_NOT_READY'
    return True,'PASS'


def select(candidate_batch,staged_root,out):
    c=contract(); staged=Path(staged_root); items=json.loads(Path(candidate_batch).read_text(encoding='utf-8'))
    expected=int(c['continuity']['ready_pool_size']); primary_n=int(c['scheduler']['daily_posts']); reserve_n=int(c['continuity']['hot_reserve_count'])
    if len(items)!=expected or expected!=primary_n+reserve_n: raise RuntimeError(f'CONTINUITY_POOL_SIZE_FAIL got={len(items)} expected={expected}')
    primary=items[:primary_n]; reserves=items[primary_n:]; selected=[]; failed=[]; reserve_pass=[]
    for idx,item in enumerate(primary):
        ok,reason=_stage_ok(staged,item)
        if ok: selected.append(copy.deepcopy(item))
        else: failed.append({'slot':idx,'item':item,'reason':reason})
    for item in reserves:
        ok,reason=_stage_ok(staged,item)
        if ok: reserve_pass.append(copy.deepcopy(item))
    if len(failed)>reserve_n: raise RuntimeError(f'CONTINUITY_PRIMARY_FAILURE_OVER_CAP failures={len(failed)} reserve={reserve_n}')
    if len(reserve_pass)<len(failed): raise RuntimeError(f'CONTINUITY_RESERVE_SHORTAGE need={len(failed)} pass={len(reserve_pass)}')
    substitutions=[]
    for failure,reserve in zip(failed,reserve_pass):
        reserve['schedule']['date']=failure['item']['schedule']['date']; reserve['continuity_substitution_for']=failure['item']['id']; reserve['continuity_substitution_reason']=failure['reason']; validate_item(c,reserve)
        selected.append(reserve); substitutions.append({'failed_id':failure['item']['id'],'reserve_id':reserve['id'],'slot':failure['slot'],'reason':failure['reason']})
    selected.sort(key=lambda x:x['schedule']['date'])
    if len(selected)!=primary_n: raise RuntimeError(f'CONTINUITY_SELECTED_COUNT_FAIL {len(selected)}')
    ids=[x['id'] for x in selected]
    if len(ids)!=len(set(ids)): raise RuntimeError('CONTINUITY_DUPLICATE_SELECTED_ID')
    payload={'schema':'CENA_CERTA_CONTINUITY_SELECTION_V2','selected_count':len(selected),'expected_placements':len(selected)*len(c['scheduler']['networks']),'substitution_count':len(substitutions),'substitutions':substitutions,'continuity_pass':True,'items':selected}
    p=Path(out); p.parent.mkdir(parents=True,exist_ok=True); tmp=p.with_suffix(p.suffix+'.tmp'); tmp.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8'); os.replace(tmp,p)
    selected_path=p.with_name(p.stem+'.selected-batch.json'); tmp2=selected_path.with_suffix(selected_path.suffix+'.tmp'); tmp2.write_text(json.dumps(selected,ensure_ascii=False,indent=2),encoding='utf-8'); os.replace(tmp2,selected_path)
    print('FACTORY_V2_CONTINUITY_PASS selected=8 substitutions=',len(substitutions),'placements=',payload['expected_placements']); return payload,selected_path


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--candidate-batch',required=True); ap.add_argument('--staged-root',required=True); ap.add_argument('--out',required=True); a=ap.parse_args(); select(a.candidate_batch,a.staged_root,a.out)
if __name__=='__main__': main()

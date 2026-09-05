#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, re, time
from pathlib import Path
from .common import OUT, contract, safe_id, sha256

SHA256_RE=re.compile(r'^[0-9a-f]{64}$')


def _find_media(obj):
    if isinstance(obj,dict):
        if obj.get('videoUrl') and obj.get('videoKey'):
            return {'videoUrl':obj['videoUrl'],'videoKey':obj['videoKey']}
        for v in obj.values():
            r=_find_media(v)
            if r: return r
    elif isinstance(obj,list):
        for v in obj:
            r=_find_media(v)
            if r: return r
    return None


def aggregate(batch,require_staging=True):
    c=contract(); batch_path=Path(batch); items=json.loads(batch_path.read_text(encoding='utf-8')); batch_sha=sha256(batch_path)
    pool_expected=int(c['sla']['candidate_pool_size']); final_expected=int(c['sla']['daily_batch_size']); reserve_expected=int(c['sla']['hot_reserve_count'])
    if len(items)!=pool_expected:
        raise RuntimeError(f'CANDIDATE_POOL_COUNT_FAIL {len(items)} != {pool_expected}')
    rows=[]; qualified=[]
    for index,it in enumerate(items):
        rid=safe_id(it['id']); receipt_path=OUT/f'{rid}.receipt.json'; r2_path=OUT/f'{rid}.r2.json'
        receipt=json.loads(receipt_path.read_text(encoding='utf-8')) if receipt_path.exists() else {'id':rid,'state':'MISSING','qa_pass':False}
        video_sha=str(receipt.get('video_sha256') or '').lower(); receipt_batch=str(receipt.get('batch_sha256') or '').lower()
        qa_ok=bool(
            receipt.get('id')==rid and receipt.get('state')=='PREVIEW_READY' and
            receipt.get('render_pass') is True and receipt.get('qa_pass') is True and
            SHA256_RE.fullmatch(video_sha) and receipt_batch==batch_sha
        )
        media=None; staged=False; binding_ok=False
        if r2_path.exists():
            try:
                r2=json.loads(r2_path.read_text(encoding='utf-8')); media=_find_media(r2)
                binding_ok=bool(
                    r2.get('schema')=='CENA_CERTA_R2_RECEIPT_V2' and
                    r2.get('id')==rid and
                    r2.get('batchSha256')==batch_sha and
                    r2.get('contentSha256')==video_sha and
                    r2.get('blind_retry_used') is False
                )
                staged=bool(r2.get('status')=='ready' and r2.get('public_probe_pass') is True and r2.get('public_head_size_match') is True and media and binding_ok)
            except Exception:
                staged=False; binding_ok=False
        eligible=bool(qa_ok and (staged or not require_staging))
        row={'index':index,'id':rid,'qa_ok':qa_ok,'staged':staged,'binding_ok':binding_ok,'eligible':eligible,'state':receipt.get('state'),'elapsed_seconds':float(receipt.get('elapsed_seconds') or 0),'media':media}
        rows.append(row)
        if eligible: qualified.append((index,it,row))
    if len(qualified)<final_expected:
        report={'schema':'CENA_CERTA_FACTORY_V2_POOL_REPORT','state':'INSUFFICIENT_READY_POOL','batch_sha256':batch_sha,'candidate_count':len(items),'qualified_count':len(qualified),'required_final':final_expected,'rows':rows,'fail_closed':True}
        tmp=OUT/'pool-report.json.tmp'; tmp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8'); os.replace(tmp,OUT/'pool-report.json')
        print('FACTORY_V2_POOL_FAIL',len(qualified),'/',final_expected)
        raise SystemExit(1)
    selected=qualified[:final_expected]
    reserves=qualified[final_expected:final_expected+reserve_expected]
    selected_items=[x[1] for x in selected]; reserve_items=[x[1] for x in reserves]
    (OUT/'selected-batch.json').write_text(json.dumps(selected_items,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'hot-reserve.json').write_text(json.dumps(reserve_items,ensure_ascii=False,indent=2),encoding='utf-8')
    slowest=max((x[2]['elapsed_seconds'] for x in selected),default=0.0)
    report={'schema':'CENA_CERTA_FACTORY_V2_POOL_REPORT','state':'POOL_SELECTED','generated_epoch':time.time(),'batch_sha256':batch_sha,'candidate_count':len(items),'qualified_count':len(qualified),'selected_count':len(selected_items),'reserve_count':len(reserve_items),'selected_ids':[x['id'] for x in selected_items],'reserve_ids':[x['id'] for x in reserves and reserve_items],'failed_or_ineligible_ids':[r['id'] for r in rows if not r['eligible']],'require_staging':bool(require_staging),'expected_network_placements':final_expected*int(c['sla']['network_count']),'slowest_selected_render_qa_seconds':round(slowest,2),'schedule_gate':'BLOCKED_UNTIL_PRIVATE_PREVIEW_AND_HUMAN_APPROVAL','rows':rows,'fail_closed':True}
    tmp=OUT/'pool-report.json.tmp'; tmp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8'); os.replace(tmp,OUT/'pool-report.json')
    print('FACTORY_V2_POOL_10_TO_8_PASS selected=',len(selected_items),'reserve=',len(reserve_items),'qualified=',len(qualified))
    if len(reserve_items)<reserve_expected:
        print('FACTORY_V2_RESERVE_DEGRADED',len(reserve_items),'/',reserve_expected)
    return report


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--batch',required=True); ap.add_argument('--allow-unstaged',action='store_true'); a=ap.parse_args(); aggregate(a.batch,require_staging=not a.allow_unstaged)
if __name__=='__main__': main()

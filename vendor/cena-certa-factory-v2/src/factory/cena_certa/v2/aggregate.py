#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, time
from pathlib import Path
from .common import OUT, contract, safe_id

def aggregate(batch):
 c=contract(); items=json.loads(Path(batch).read_text(encoding='utf-8')); rows=[]
 for it in items:
  rid=safe_id(it['id']); p=OUT/f'{rid}.receipt.json'; rows.append(json.loads(p.read_text(encoding='utf-8')) if p.exists() else {'id':rid,'state':'MISSING','qa_pass':False})
 ready=[r for r in rows if r.get('state')=='PREVIEW_READY' and r.get('render_pass') is True and r.get('qa_pass') is True]; elapsed=[float(r.get('elapsed_seconds') or 0) for r in ready]; slowest=max(elapsed,default=0.0); expected=int(c['sla']['daily_batch_size']); networks=int(c['sla']['network_count'])
 report={'schema':'CENA_CERTA_FACTORY_V2_BATCH_REPORT','generated_epoch':time.time(),'count':len(rows),'expected_videos':expected,'network_count':networks,'expected_network_placements':expected*networks,'preview_ready':len(ready),'all_render_qa_pass':len(rows)==expected and len(ready)==expected,'slowest_video_render_qa_seconds':round(slowest,2),'render_stage_target_seconds':c['sla']['render_stage_target_seconds'],'scheduler_target_seconds':c['sla']['scheduler_target_seconds'],'end_to_end_target_seconds':c['sla']['target_seconds'],'schedule_gate':'BLOCKED_UNTIL_PRIVATE_PREVIEW_AND_HUMAN_APPROVAL','items':rows}
 tmp=OUT/'batch-report.json.tmp'; tmp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8'); os.replace(tmp,OUT/'batch-report.json'); print('FACTORY_V2_BATCH_REPORT',len(ready),'/',expected,'slowest_seconds',round(slowest,2))
 if not report['all_render_qa_pass']: raise SystemExit(1)
 return report

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--batch',required=True); a=ap.parse_args(); aggregate(a.batch)
if __name__=='__main__': main()

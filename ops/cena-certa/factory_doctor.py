#!/usr/bin/env python3
"""Zero-network proactive audit for the Cena Certa factory.

Cheap by design: no render, no external API, no scheduler write. It must detect
policy drift, incomplete mask protection, late deterministic failures and dead
routes before expensive production starts.
"""
from __future__ import annotations
import argparse, json, pathlib, re

ROOT=pathlib.Path(__file__).resolve().parents[2]
OPS=ROOT/'ops/cena-certa'; FACTORY_ROOT=ROOT/'vendor/cena-certa-factory-v2/src'; ENGINE=FACTORY_ROOT/'factory/cena_certa/v2'; WORKFLOWS=ROOT/'.github/workflows'

def fail(msg): raise SystemExit(msg)
def load_json(path):
 try: obj=json.loads(path.read_text(encoding='utf-8'))
 except Exception as e: fail(f'DOCTOR_JSON_FAIL {path.relative_to(ROOT)} {type(e).__name__}')
 if not isinstance(obj,dict): fail(f'DOCTOR_JSON_OBJECT_REQUIRED {path.relative_to(ROOT)}')
 return obj

def _rect(v,name,width,height):
 if not isinstance(v,list) or len(v)!=4: fail(f'DOCTOR_RECT_FAIL {name}')
 x,y,w,h=(int(x) for x in v)
 if x<0 or y<0 or w<=0 or h<=0 or x+w>width or y+h>height: fail(f'DOCTOR_RECT_OUT_OF_CANVAS {name} {v}')
 return x,y,w,h

def _overlap(a,b):
 ax,ay,aw,ah=a; bx,by,bw,bh=b
 return ax<bx+bw and bx<ax+aw and ay<by+bh and by<ay+ah

def _contains(outer,inner):
 ox,oy,ow,oh=outer; ix,iy,iw,ih=inner
 return ix>=ox and iy>=oy and ix+iw<=ox+ow and iy+ih<=oy+oh

def check_geometry_and_mask():
 c=load_json(ENGINE/'contract_v9_factory.json')
 if c.get('schema')!='ORBIT_CENA_CERTA_FACTORY_V2' or c.get('fail_closed') is not True: fail('DOCTOR_CONTRACT_SCHEMA_FAIL')
 if c.get('visual_precedence')!='APPROVED_FRAME_OVER_TABLE': fail('DOCTOR_VISUAL_PRECEDENCE_FAIL')
 width=int(c['canvas']['width']); height=int(c['canvas']['height'])
 if (width,height,int(c['canvas']['fps']))!=(1080,1920,30): fail('DOCTOR_CANVAS_FAIL')
 geo=c['geometry_approved_frame_1080x1920']
 # Later Canonical Mask V1 hard-lock geometry. This must never silently drift.
 hard={'title_panel':[61,94,979,220],'title_static_anchor':[61,94,289,220],'story_logo':[910,371,99,168],'film_window':[16,664,1046,602],'footer':[42,1666,995,201]}
 for k,v in hard.items():
  if list(geo.get(k) or [])!=v: fail(f'DOCTOR_CANONICAL_MASK_GEOMETRY_DRIFT {k} {geo.get(k)} != {v}')
 bezel=geo.get('film_mask_bezel') or {}
 if int(bezel.get('inset_pixels',0))<2 or int(bezel.get('corner_radius_pixels',0))<8: fail('DOCTOR_FULL_BEZEL_POLICY_FAIL')
 rects={k:_rect(geo[k],k,width,height) for k in ('title_panel','title_static_anchor','story_logo','film_window','cc_reference_bbox','cc_safe_zone','footer')}
 cc=rects['cc_safe_zone']
 if not _contains(cc,rects['cc_reference_bbox']): fail('DOCTOR_CC_REFERENCE_OUTSIDE_SAFE_ZONE')
 for name in ('title_panel','title_static_anchor','story_logo','film_window','footer'):
  if _overlap(cc,rects[name]): fail(f'DOCTOR_CC_STATIC_COLLISION {name}')
 if rects['film_window'][1]+rects['film_window'][3]>=cc[1]: fail('DOCTOR_FILM_CC_VERTICAL_ORDER_FAIL')
 if cc[1]+cc[3]>=rects['footer'][1]: fail('DOCTOR_CC_FOOTER_VERTICAL_ORDER_FAIL')
 if list(geo.get('cta_full') or [])!=[0,0,width,height]: fail('DOCTOR_CTA_FULL_FRAME_FAIL')
 if int(c['selection']['film_default_min_year'])!=1995 or int(c['selection']['film_exception_min_year'])!=1985: fail('DOCTOR_FILM_YEAR_POLICY_DRIFT')
 for key in ('story','cta'):
  spec=c['approved_visual_sources'][key]; p=FACTORY_ROOT/spec['path']
  if not p.is_file() or not spec.get('git_blob_sha1') or not spec.get('library_byte_sha256') or not spec.get('pixel_sha256'): fail(f'DOCTOR_PHYSICAL_MASTER_LOCK_FAIL {key}')
 common=(ENGINE/'common.py').read_text(encoding='utf-8'); render=(ENGINE/'render.py').read_text(encoding='utf-8'); qa=(ENGINE/'qa.py').read_text(encoding='utf-8')
 order=[render.find("[film]subtitles='"),render.find('[captioned][ttl]overlay='),render.find('[titled][mask]overlay=0:0')]
 if min(order)<0 or order!=sorted(order): fail('DOCTOR_MASK_COMPOSITE_ORDER_FAIL')
 for token in ('_physical_film_bezel','physical-full-bezel-v3-cache-sealed','mask_protected_mae'):
  if token not in common: fail(f'DOCTOR_FULL_BEZEL_IMPLEMENTATION_MISSING {token}')
 if 'CANONICAL_MASK_PROTECTED_PIXEL_FAIL' not in qa: fail('DOCTOR_FULL_MASK_QA_MISSING')
 if "'mask_composite_order':'FILM_CC_TITLE_THEN_FINAL_STATIC_MASK'" not in render: fail('DOCTOR_MASK_RECEIPT_MARKER_MISSING')
 print('DOCTOR_MASK_GEOMETRY_PASS')

def check_editorial_and_blank_guards():
 c=load_json(ENGINE/'contract_v9_factory.json'); sel=c['selection']; qa=c['qa']; runtime=c['runtime']
 for k in ('professional_production_required','audience_demand_required','recognized_or_acclaimed_required','student_amateur_backyard_production_forbidden','obscure_low_demand_fallback_forbidden'):
  if sel.get(k) is not True: fail(f'DOCTOR_PREMIUM_EDITORIAL_POLICY_FAIL {k}')
 if int(sel.get('premium_evidence_min_independent_signals',0))<3: fail('DOCTOR_PREMIUM_EVIDENCE_TOO_WEAK')
 if float(qa.get('story_black_interval_max_seconds',9))>0.20: fail('DOCTOR_BLANK_VISUAL_TOLERANCE_LOOSENED')
 if runtime.get('scene_black_guard_before_render') is not True or runtime.get('deterministic_failures_must_precede_render') is not True: fail('DOCTOR_PRE_RENDER_GUARD_FAIL')
 pre=(ENGINE/'preflight.py').read_text(encoding='utf-8'); prep=(ENGINE/'prepare.py').read_text(encoding='utf-8'); q=(ENGINE/'qa.py').read_text(encoding='utf-8')
 for token in ('PROFESSIONAL_PRODUCTION_REQUIRED','AUDIENCE_DEMAND_REQUIRED','PREMIUM_EDITORIAL_BLOCK','PREMIUM_DEMAND_SIGNAL_REQUIRED'):
  if token not in pre: fail(f'DOCTOR_PREMIUM_PREFLIGHT_MISSING {token}')
 if 'SCENE_' not in prep or 'black_intervals(out,c' not in prep: fail('DOCTOR_SCENE_BLANK_GUARD_MISSING')
 if "label='FINAL_STORY'" not in q: fail('DOCTOR_FINAL_STORY_BLANK_GUARD_MISSING')
 if '_prepared_cache_valid' not in prep or 'READY_ASSETS_REUSE_PASS' not in prep: fail('DOCTOR_PREPARED_REUSE_MISSING')
 if int(c['sla'].get('pilot_pair_target_seconds',999))>180: fail('DOCTOR_PILOT_PAIR_SLA_DRIFT')
 print('DOCTOR_EDITORIAL_BLANK_PERFORMANCE_PASS')

def check_code_and_routes():
 common=(ENGINE/'common.py').read_text(encoding='utf-8'); r2=(OPS/'r2_stage.py').read_text(encoding='utf-8'); prod=(WORKFLOWS/'cena-certa-production-v2.yml').read_text(encoding='utf-8')
 if '--retry-all-errors' in common: fail('DOCTOR_BLIND_SOURCE_RETRY_PRESENT')
 if 'R2_TRANSIENT_HTTP' not in r2 or 'blind_retry_used' not in r2: fail('DOCTOR_R2_RETRY_CLASSIFIER_MISSING')
 for token in ('factory_doctor.py','ready_matrix','request_id','[skip ci]'):
  if token not in prod: fail(f'DOCTOR_PRODUCTION_INVARIANT_MISSING {token}')
 forbidden=('vendor/cena-certa-factory-v2/assets-b64','vendor/cena-certa-factory-v2/payload-exact-v1','vendor/cena-certa-factory-v2/payload-test','vendor/cena-certa-factory-v2/payload-v2','.github/workflows/cena-certa-gitlab-r2-bridge-20260903.yml','.github/workflows/cena-certa-snapshot-sync-once.yml','ops/cena-certa/ready-assets-dispatch.json')
 present=[p for p in forbidden if (ROOT/p).exists()]
 if present: fail('DOCTOR_DEAD_ROUTE_OR_LITTER_PRESENT '+','.join(present))
 if not (OPS/'dispatch_activate.py').is_file() or not (OPS/'batch_admit.py').is_file(): fail('DOCTOR_CANONICAL_ENTRYPOINT_MISSING')
 print('DOCTOR_CODE_ROUTE_PASS')

def check_state():
 dispatch=load_json(OPS/'dispatch.json'); outbox=load_json(OPS/'publisher-outbox.json'); approval=load_json(OPS/'human-approval.json'); state=load_json(OPS/'publisher-state.json')
 if dispatch.get('schema')!='CENA_CERTA_PRODUCTION_DISPATCH_V1': fail('DOCTOR_DISPATCH_SCHEMA_FAIL')
 enabled=dispatch.get('enabled') is True; mode=str(dispatch.get('mode') or '').upper()
 if not enabled:
  if mode!='IDLE' or any(str(dispatch.get(k) or '') for k in ('batch_path','batch_sha256','prepared_run_id','requested_at','request_id')): fail('DOCTOR_IDLE_DISPATCH_DIRTY')
 else:
  if mode!='PREPARE' or str(dispatch.get('prepared_run_id') or ''): fail('DOCTOR_ACTIVE_DISPATCH_MODE_FAIL')
  candidate_count=int(dispatch.get('candidate_count') or 0); selected_count=int(dispatch.get('selected_count') or 0); reserve_count=int(dispatch.get('reserve_count') or 0)
  if candidate_count<1 or candidate_count>10 or selected_count<1 or reserve_count<0 or candidate_count!=selected_count+reserve_count: fail('DOCTOR_ACTIVE_DISPATCH_COUNT_FAIL')
  if not re.fullmatch(r'[A-Za-z0-9._-]{12,96}',str(dispatch.get('request_id') or '')): fail('DOCTOR_ACTIVE_DISPATCH_REQUEST_ID_FAIL')
  if not str(dispatch.get('batch_path') or '').startswith('ops/cena-certa/batches/'): fail('DOCTOR_ACTIVE_DISPATCH_BATCH_PATH_FAIL')
  if not re.fullmatch(r'[0-9a-f]{64}',str(dispatch.get('batch_sha256') or '').lower()): fail('DOCTOR_ACTIVE_DISPATCH_BATCH_SHA_FAIL')
 items=outbox.get('items')
 if not isinstance(items,list): fail('DOCTOR_OUTBOX_ITEMS_FAIL')
 if items:
  expected_objects=int(outbox.get('expected_schedule_objects') or 0); expected_placements=int(outbox.get('expected_network_placements') or 0)
  if expected_objects<1 or len(items)!=expected_objects or expected_placements!=expected_objects*4: fail('DOCTOR_OUTBOX_COUNT_FAIL')
  h=outbox.get('handoff_sha256'); run=outbox.get('production_run_id')
  if not h or not run: fail('DOCTOR_OUTBOX_IDENTITY_FAIL')
  if approval.get('handoff_sha256')!=h or approval.get('production_run_id')!=run: fail('DOCTOR_APPROVAL_OUTBOX_MISMATCH')
  if state.get('handoff_sha256')!=h or state.get('production_run_id')!=run: fail('DOCTOR_PUBLISHER_STATE_OUTBOX_MISMATCH')
 else:
  if outbox.get('state')!='EMPTY': fail('DOCTOR_EMPTY_OUTBOX_STATE_FAIL')
  if approval.get('approved') is True: fail('DOCTOR_ORPHAN_APPROVAL_FAIL')
  if state.get('state')=='AWAITING_HUMAN_APPROVAL': fail('DOCTOR_ORPHAN_PUBLISHER_WAIT_FAIL')
 if state.get('blind_retry_forbidden') is not True: fail('DOCTOR_PUBLISHER_BLIND_RETRY_GUARD_FAIL')
 print('DOCTOR_STATE_PASS')

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--state-only',action='store_true'); args=ap.parse_args(); check_state()
 if not args.state_only:
  check_geometry_and_mask(); check_editorial_and_blank_guards(); check_code_and_routes(); print('CENA_CERTA_FACTORY_DOCTOR_PASS zero_network=true render=false external_writes=false')
 else: print('CENA_CERTA_FACTORY_DOCTOR_STATE_PASS')
if __name__=='__main__': main()

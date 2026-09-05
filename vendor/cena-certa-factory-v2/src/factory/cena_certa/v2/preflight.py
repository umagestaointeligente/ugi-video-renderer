#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo
from PIL import Image
from .common import *

FORBIDDEN=('trailer','teaser','preview','recap','sizzle','promo')

def _https(url,label):
 p=urlparse(str(url))
 if p.scheme!='https' or not p.netloc: raise RuntimeError(f'{label}_HTTPS_REQUIRED')

def _fresh_iso(value,max_age_hours,label):
 try: dt=datetime.fromisoformat(str(value).replace('Z','+00:00'))
 except Exception as e: raise RuntimeError(f'{label}_TIMESTAMP_INVALID') from e
 if dt.tzinfo is None: raise RuntimeError(f'{label}_TIMEZONE_REQUIRED')
 age=(datetime.now(timezone.utc)-dt.astimezone(timezone.utc)).total_seconds()/3600
 if age<-.25 or age>max_age_hours: raise RuntimeError(f'{label}_STALE age_hours={age:.2f} max={max_age_hours}')
 return dt

def schedule_instant(c,value,phase=None):
 try: dt=datetime.fromisoformat(str(value).replace('Z','+00:00'))
 except Exception as e: raise RuntimeError('SCHEDULE_DATE_INVALID') from e
 if dt.tzinfo is None: raise RuntimeError('SCHEDULE_TIMEZONE_REQUIRED')
 local=dt.astimezone(ZoneInfo(c['scheduler']['timezone']))
 lead=(local.astimezone(timezone.utc)-datetime.now(timezone.utc)).total_seconds()
 publisher_min=float(c['scheduler'].get('publisher_minimum_lead_seconds',900))
 factory_budget=float(c.get('sla',{}).get('target_seconds',660))
 configured=float(c['scheduler'].get('minimum_schedule_lead_seconds',0))
 phase=str(phase or os.getenv('ORBIT_SCHEDULE_PHASE','admission')).strip().lower()
 if phase=='admission':
  required=max(configured,publisher_min+factory_budget)
 elif phase=='publisher':
  required=publisher_min
 else:
  raise RuntimeError(f'SCHEDULE_PHASE_FAIL {phase}')
 if lead<required: raise RuntimeError(f'SCHEDULE_LEAD_TIME_FAIL phase={phase} seconds={lead:.0f} required={required:.0f}')
 return local

def validate_schedule(c,item):
 s=item.get('schedule')
 if not isinstance(s,dict): raise RuntimeError('SCHEDULE_MANIFEST_REQUIRED')
 for k in ('date','text','youtube_title','made_for_kids','providers','ai_flags'):
  if k not in s: raise RuntimeError(f'SCHEDULE_FIELD_FAIL {k}')
 schedule_instant(c,s['date'])
 if not str(s['text']).strip() or not str(s['youtube_title']).strip(): raise RuntimeError('SCHEDULE_COPY_EMPTY')
 providers=list(s['providers']); expected=list(c['scheduler']['networks'])
 if sorted(providers)!=sorted(expected): raise RuntimeError(f'SCHEDULE_PROVIDER_ROUTE_FAIL {providers}')
 if len(providers)!=len(set(providers)): raise RuntimeError('SCHEDULE_PROVIDER_DUPLICATE')
 if not isinstance(s['made_for_kids'],bool): raise RuntimeError('SCHEDULE_KIDS_FLAG_REQUIRED')
 flags=s['ai_flags']
 if not isinstance(flags,dict) or any(k not in flags or not isinstance(flags[k],bool) for k in ('instagram','tiktok','youtube')): raise RuntimeError('SCHEDULE_AI_FLAGS_REQUIRED')
 if len(str(s['youtube_title']))>100: raise RuntimeError('YOUTUBE_TITLE_TOO_LONG')
 if len(str(s.get('tiktok_title',s['youtube_title'])))>150: raise RuntimeError('TIKTOK_TITLE_TOO_LONG')
 tags=s.get('youtube_tags',[])
 if not isinstance(tags,list) or any(not isinstance(x,str) for x in tags): raise RuntimeError('YOUTUBE_TAGS_FAIL')
 return True

def validate_item(c,item):
 req=['id','work_type','film_title','film_year','source_url','rights_evidence','license','relevance_evidence','anti_repeat_evidence','caption_chunks','scene_plan','music_track','live_readback_pass','rights_pass','relevance_pass','ready_checked_at','schedule','source_clean_verified','scene_semantic_verified']
 miss=[k for k in req if k not in item]
 if miss: raise RuntimeError(f"ITEM_REQUIRED_FIELDS_FAIL {item.get('id')} {miss}")
 rid=safe_id(item['id']); _https(item['source_url'],'SOURCE_URL')
 _fresh_iso(item['ready_checked_at'],c['ready_queue']['expire_hours'],'READY_QUEUE')
 if item['live_readback_pass'] is not True: raise RuntimeError('LIVE_READBACK_FAIL')
 if item['rights_pass'] is not True: raise RuntimeError('RIGHTS_FAIL')
 if item['relevance_pass'] is not True: raise RuntimeError('RELEVANCE_FAIL')
 if item['source_clean_verified'] is not True: raise RuntimeError('SOURCE_CLEANLINESS_FAIL')
 if item['scene_semantic_verified'] is not True: raise RuntimeError('SCENE_SEMANTIC_GLOBAL_FAIL')
 y=int(item['film_year']); current=datetime.now().year
 if y>current+1: raise RuntimeError('FUTURE_YEAR_FAIL')
 if item['work_type']=='film':
  if y<c['selection']['film_exception_min_year']: raise RuntimeError('YEAR_GATE_FAIL')
  if y<c['selection']['film_default_min_year'] and not item.get('year_exception_approved'): raise RuntimeError('YEAR_EXCEPTION_APPROVAL_REQUIRED')
  if y<c['selection']['film_default_min_year'] and not item.get('classic_high_demand_verified'): raise RuntimeError('CLASSIC_HIGH_DEMAND_REQUIRED')
  if item.get('dedup_60d_pass') is not True or not item['anti_repeat_evidence']: raise RuntimeError('ANTI_REPEAT_60D_FAIL')
 elif item['work_type']=='series':
  if y<c['selection']['series_min_year']: raise RuntimeError('SERIES_YEAR_GATE_FAIL')
  for k in ('series_title','season','episode','episode_title'):
   if not item.get(k): raise RuntimeError(f'SERIES_IDENTITY_FAIL {k}')
  if not item.get('episode_self_contained'): raise RuntimeError('SERIES_SELF_CONTAINED_FAIL')
  if item.get('series_cooldown_pass') is not True: raise RuntimeError('SERIES_COOLDOWN_FAIL')
  if item.get('episode_never_used_pass') is not True: raise RuntimeError('SERIES_EPISODE_REPEAT_FAIL')
  if not item['anti_repeat_evidence']: raise RuntimeError('SERIES_ANTI_REPEAT_EVIDENCE_FAIL')
 else: raise RuntimeError('WORK_TYPE_FAIL')
 if item.get('animation') is True and not item.get('animation_exception_approved'): raise RuntimeError('ANIMATION_DEFAULT_BLOCK')
 if not isinstance(item['relevance_evidence'],list) or len(item['relevance_evidence'])<c['selection']['relevance_min_independent_signals'] or any(not str(x).strip() for x in item['relevance_evidence']): raise RuntimeError('RELEVANCE_EVIDENCE_FAIL')
 if not item['rights_evidence'] or not item['license']: raise RuntimeError('RIGHTS_EVIDENCE_FAIL')
 public=(item.get('film_title','')+' '+item.get('source_url','')).lower()
 if any(x in public for x in FORBIDDEN): raise RuntimeError('PROMO_SOURCE_FAIL')
 chunks=item['caption_chunks']
 if not isinstance(chunks,list) or len(chunks)<5 or any(not isinstance(x,str) or not x.strip() for x in chunks): raise RuntimeError('VOICE_PLAN_FAIL')
 validate_caption_layout(chunks,c)
 title_probe=TMP/f'preflight-title-{rid}.png'; make_title(c,item['film_title'],item['film_year'],title_probe); title_probe.unlink(missing_ok=True)
 script=' '.join(chunks)
 if item.get('script') and normalize_text(item['script'])!=normalize_text(script): raise RuntimeError('SCRIPT_CAPTION_LITERAL_FAIL')
 if len(item['scene_plan'])<c['story']['scene_min_count']: raise RuntimeError('SCENE_COUNT_FAIL')
 coverage=[]; expected_start=0; starts=[]
 for i,s in enumerate(item['scene_plan']):
  for k in ('start_seconds','caption_start','caption_end','semantic_reason','semantic_verified'):
   if k not in s: raise RuntimeError(f'SCENE_PLAN_FIELD_FAIL {k}')
  a=int(s['caption_start']); b=int(s['caption_end']); start=float(s['start_seconds'])
  if a!=expected_start or b<a or b>=len(chunks): raise RuntimeError(f'SCENE_PLAN_PARTITION_FAIL expected_start={expected_start} got={a}:{b}')
  if start<0 or not str(s['semantic_reason']).strip(): raise RuntimeError('SCENE_PLAN_CONTENT_FAIL')
  if s['semantic_verified'] is not True: raise RuntimeError(f'SCENE_SEMANTIC_FAIL scene={i}')
  if any(abs(start-x)<0.25 for x in starts): raise RuntimeError(f'SCENE_REPEAT_START_FAIL {start}')
  starts.append(start); coverage.extend(range(a,b+1)); expected_start=b+1
 if coverage!=list(range(len(chunks))) or expected_start!=len(chunks): raise RuntimeError('SCENE_PLAN_COVERAGE_FAIL')
 mt=item['music_track']
 for k in ('id','url','rights_evidence','license','genre','instrumental_verified','editorial_match_verified'):
  if k not in mt or mt.get(k) in (None,''): raise RuntimeError(f'MUSIC_MANIFEST_FAIL {k}')
 _https(mt['url'],'MUSIC_URL')
 if mt['instrumental_verified'] is not True: raise RuntimeError('MUSIC_INSTRUMENTAL_FAIL')
 if mt['editorial_match_verified'] is not True: raise RuntimeError('MUSIC_EDITORIAL_MATCH_FAIL')
 if mt['genre']!=item.get('music_profile',mt['genre']): raise RuntimeError('MUSIC_GENRE_MISMATCH')
 validate_schedule(c,item); return True

def validate_batch(path,expect=8):
 c=verify_contract_and_assets(); items=json.loads(Path(path).read_text(encoding='utf-8'))
 if not isinstance(items,list): raise RuntimeError('BATCH_NOT_LIST')
 if expect and len(items)!=expect: raise RuntimeError(f'BATCH_SIZE_FAIL {len(items)} expected {expect}')
 ids=set(); tracks=set(); instants=set()
 for item in items:
  validate_item(c,item)
  if item['id'] in ids: raise RuntimeError('DUPLICATE_CONTENT_ID')
  ids.add(item['id']); tid=item['music_track']['id']
  if tid in tracks and c['music']['unique_track_per_batch']: raise RuntimeError('MUSIC_TRACK_REPEAT_FAIL')
  tracks.add(tid)
  instant=schedule_instant(c,item['schedule']['date']).astimezone(timezone.utc).replace(microsecond=0).isoformat()
  if instant in instants: raise RuntimeError('SCHEDULE_TIME_COLLISION_FAIL')
  instants.add(instant)
 print('FACTORY_V2_BATCH_PASS',len(items)); return items

def canary():
 t0=time.time(); c=verify_contract_and_assets(); mask=prepare_static_assets(c)
 title=TMP/'canary-title.png'; make_title(c,'CANARY',2026,title); cta=CACHE/'cta-master.png'; out=OUT/'FACTORY-V2-CANARY.mp4'
 tx,ty,tw,th=c['geometry_approved_frame_1080x1920']['title_panel']; fps=int(c['canvas']['fps'])
 filt=';'.join([
  f'[0:v]scale=1080:1920,setsar=1,fps={fps},eq=brightness=-0.1[base]',
  f'[2:v]scale={tw}:{th},setsar=1,fps={fps},format=rgba[t]',
  f'[base][t]overlay={tx}:{ty}[titled]',
  f'[1:v]fps={fps},format=rgba[mask]',
  '[titled][mask]overlay=0:0,setsar=1[story]',
  f'[3:v]scale=1080:1920,setsar=1,fps={fps},trim=duration=1.5,setpts=PTS-STARTPTS[cta]',
  f'[story]trim=duration=1.5,setpts=PTS-STARTPTS,fps={fps}[s];[s][cta]concat=n=2:v=1:a=0,fps={fps},setsar=1[v]'])
 sh(['ffmpeg','-loglevel','error','-y','-f','lavfi','-i','testsrc2=size=1080x1920:rate=30:duration=1.5','-loop','1','-i',str(mask),'-loop','1','-i',str(title),'-loop','1','-i',str(cta),'-f','lavfi','-i','anullsrc=r=48000:cl=stereo','-filter_complex',filt,'-map','[v]','-map','4:a','-shortest','-t','3','-r',str(fps),'-fps_mode','cfr','-c:v','libx264','-threads','2','-preset','ultrafast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-ar','48000',str(out)],timeout=90)
 p=ffprobe(out); v=next(x for x in p['streams'] if x['codec_type']=='video')
 actual={'width':int(v['width']),'height':int(v['height']),'avg_frame_rate':v['avg_frame_rate'],'fps':fps_value(v['avg_frame_rate']),'sample_aspect_ratio':v.get('sample_aspect_ratio')}
 print('CANARY_TECH_PROBE',json.dumps(actual,sort_keys=True))
 if actual['width']!=1080 or actual['height']!=1920 or abs(actual['fps']-fps)>.02 or actual['sample_aspect_ratio'] not in (None,'1:1'):
  raise RuntimeError(f'CANARY_TECH_FAIL {actual}')
 frame=TMP/'canary-cta.png'; extract_frame(out,2.2,frame); e=mae(Image.open(frame),Image.open(cta))
 if e>c['qa']['cta_pixel_mae_max']: raise RuntimeError(f'CANARY_CTA_FAIL {e}')
 print('FACTORY_V2_CANARY_PASS',round(time.time()-t0,2),'seconds','cta_mae',round(e,5))

def main():
 ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest='cmd',required=True); sub.add_parser('preflight'); sub.add_parser('canary')
 v=sub.add_parser('validate-batch'); v.add_argument('--batch',required=True); v.add_argument('--expect',type=int,default=8)
 a=ap.parse_args()
 if a.cmd=='preflight': verify_contract_and_assets(); prepare_static_assets(contract())
 elif a.cmd=='canary': canary()
 else: validate_batch(a.batch,a.expect)
if __name__=='__main__': main()

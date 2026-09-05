#!/usr/bin/env python3
from __future__ import annotations
import argparse, asyncio, concurrent.futures, hashlib, json, os, shutil, time
from pathlib import Path
from .common import *
from .preflight import validate_item
from .voice import tts_with_real_boundaries
from .fingerprint import prepared_asset_fingerprint, prepared_contract_fingerprint, engine_fingerprint

def precut_scene(src,start,dur,out,threads=1):
 dur=max(0.8,float(dur)); out=Path(out); tmp=out.with_name(out.stem+f'.part-{os.getpid()}'+out.suffix)
 try:
  sh(['ffmpeg','-loglevel','error','-y','-ss',f'{float(start):.3f}','-i',str(src),'-t',f'{dur:.3f}','-an','-vf','fps=30,scale=1280:-2:flags=fast_bilinear','-c:v','libx264','-threads',str(int(threads)),'-preset','ultrafast','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',str(tmp)],timeout=180)
  media_probe(tmp,'video'); actual=duration(tmp)
  if actual+0.12<dur: raise RuntimeError(f'SCENE_PRECUT_SHORT actual={actual:.3f} target={dur:.3f}')
  os.replace(tmp,out)
 finally: tmp.unlink(missing_ok=True)
 return out

def normalize_music(c,src,out):
 target=float(c['music'].get('prepared_master_lufs',-14.0)); tp=float(c['music'].get('prepared_master_true_peak_dbtp',-2.0)); out=Path(out); tmp=out.with_name(out.stem+f'.part-{os.getpid()}'+out.suffix); fix=out.with_name(out.stem+f'.peakfix-{os.getpid()}'+out.suffix)
 try:
  sh(['ffmpeg','-loglevel','error','-y','-i',str(src),'-vn','-af',f'loudnorm=I={target}:TP={tp}:LRA=7','-c:a','aac','-b:a','192k','-ar','48000',str(tmp)],timeout=150)
  media_probe(tmp,'audio'); os.replace(tmp,out)
  measured_lufs,measured_tp=loudness(out)
  if measured_tp>tp+0.3:
   correction_db=(tp-0.4)-measured_tp
   sh(['ffmpeg','-loglevel','error','-y','-i',str(out),'-vn','-af',f'volume={correction_db:.3f}dB','-c:a','aac','-b:a','192k','-ar','48000',str(fix)],timeout=150)
   media_probe(fix,'audio'); os.replace(fix,out)
   measured_lufs,measured_tp=loudness(out)
  if abs(measured_lufs-target)>1.5: raise RuntimeError(f'MUSIC_MASTER_LUFS_FAIL actual={measured_lufs:.2f} target={target:.2f}')
  if measured_tp>tp+0.3: raise RuntimeError(f'MUSIC_MASTER_PEAK_FAIL actual={measured_tp:.2f} max={tp:.2f}')
  return measured_lufs,measured_tp
 finally:
  tmp.unlink(missing_ok=True); fix.unlink(missing_ok=True)

def _visual_timeline(item,cues,story):
 plan=item['scene_plan']; rows=[]
 for i,s in enumerate(plan):
  cue_idx=int(s['caption_start']); timeline_start=0.0 if i==0 else float(cues[cue_idx]['start'])
  if i+1<len(plan): timeline_end=float(cues[int(plan[i+1]['caption_start'])]['start'])
  else: timeline_end=float(story)
  target=timeline_end-timeline_start
  if target<0.80: raise RuntimeError(f'SCENE_TIMELINE_TOO_SHORT scene={i} duration={target:.3f}')
  rows.append((timeline_start,timeline_end,target))
 total=sum(x[2] for x in rows)
 if abs(total-story)>0.12: raise RuntimeError(f'SCENE_TIMELINE_COVERAGE_FAIL total={total:.3f} story={story:.3f}')
 return rows

def _validate_source_ranges(item,timeline,source_dur):
 ranges=[]
 for i,s in enumerate(item['scene_plan']):
  source_start=float(s['start_seconds']); target=float(timeline[i][2]); source_end=source_start+target
  if source_end>source_dur+0.08: raise RuntimeError(f'SCENE_SOURCE_RANGE_FAIL scene={i} start={source_start:.3f} target={target:.3f} source={source_dur:.3f}')
  for j,(prev_start,prev_end) in enumerate(ranges):
   overlap=min(source_end,prev_end)-max(source_start,prev_start)
   if overlap>0.20: raise RuntimeError(f'SCENE_SOURCE_OVERLAP_FAIL scenes={j},{i} overlap={overlap:.3f}')
  ranges.append((source_start,source_end))
 return True

def _prepared_cache_valid(root,c,item):
 p=root/'prepared.json'
 if not p.is_file(): return None
 try:
  m=json.loads(p.read_text(encoding='utf-8'))
  if m.get('schema')!='CENA_CERTA_PREPARED_ASSETS_V2' or m.get('prepared_pass') is not True: return None
  if m.get('prepared_asset_fingerprint')!=prepared_asset_fingerprint(item): return None
  if m.get('prepared_contract_fingerprint')!=prepared_contract_fingerprint(c): return None
  if m.get('prepared_engine_fingerprint')!=engine_fingerprint(): return None
  age=(time.time()-float(m.get('created_epoch',0)))/3600
  if age<-.25 or age>float(c['prepared_assets']['expire_hours']): return None
  specs=[(m['voice'],'audio'),(m['cta_voice'],'audio'),(m['music'],'audio')]+[(s,'video') for s in m.get('scenes',[])]
  if len(m.get('scenes',[]))!=len(item['scene_plan']) or m.get('no_blank_visual_pass') is not True: return None
  for spec,kind in specs:
   path=root/Path(spec['file']).name
   if not path.is_file() or sha256(path)!=spec['sha256']: return None
   media_probe(path,kind)
  return m
 except Exception:
  return None

def prepare_one(batch,index,prepared_root):
 t0=time.time(); c=verify_contract_and_assets(); items=json.loads(Path(batch).read_text(encoding='utf-8'))
 if index<0 or index>=len(items): raise RuntimeError(f'PREPARE_INDEX_FAIL {index}/{len(items)}')
 item=items[index]; validate_item(c,item); rid=safe_id(item['id']); free_disk_guard(c['runtime']['minimum_free_disk_gb'])
 root=Path(prepared_root)/rid
 cached=_prepared_cache_valid(root,c,item)
 if cached:
  print('FACTORY_V2_READY_ASSETS_REUSE_PASS',rid,'elapsed_seconds',round(time.time()-t0,2)); return cached
 if root.exists(): shutil.rmtree(root)
 root.mkdir(parents=True,exist_ok=True)

 voice=root/'voice.mp3'; text=' '.join(item['caption_chunks']); cues=asyncio.run(tts_with_real_boundaries(c,text,item['caption_chunks'],voice)); vd=duration(voice)
 if not cues or float(cues[0]['start'])>0.35 or float(cues[-1]['end'])>vd+0.08: raise RuntimeError('VOICE_BOUNDARY_RANGE_FAIL')
 wpm=len(tokens(text))/(vd/60.0)
 if not (c['voice']['pace_wpm'][0]-8<=wpm<=c['voice']['pace_wpm'][1]+8): raise RuntimeError(f'VOICE_PACE_FAIL {wpm:.1f}')
 story=float(cues[-1]['end'])+0.12
 target_min,target_max=(float(x) for x in c['story']['default_total_seconds'])
 if not (target_min<=story<=target_max) and item.get('duration_exception_approved') is not True: raise RuntimeError(f'STORY_DURATION_TARGET_FAIL actual={story:.3f} target={target_min:.1f}..{target_max:.1f}')
 if story+c['cta']['duration_seconds']>c['story']['absolute_max_seconds']: raise RuntimeError('DURATION_MAX_FAIL')
 cta_entry_gap=story+0.05-float(cues[-1]['end'])
 if cta_entry_gap>float(c['voice']['story_to_cta_gap_max_seconds'])+0.001: raise RuntimeError(f'STORY_CTA_GAP_FAIL {cta_entry_gap:.3f}')
 timeline=_visual_timeline(item,cues,story)

 cta_voice=root/'cta-voice.mp3'; cta_cues=asyncio.run(tts_with_real_boundaries(c,c['cta']['spoken_line'],[c['cta']['spoken_line']],cta_voice)); cvd=duration(cta_voice); cta_budget=float(c['cta']['duration_seconds'])-0.15
 if cvd>cta_budget or not cta_cues or float(cta_cues[-1]['end'])>cta_budget+0.05: raise RuntimeError(f'CTA_VOICE_DURATION_FAIL voice={cvd:.3f} budget={cta_budget:.3f}')

 source=CACHE/(hashlib.sha256(item['source_url'].encode()).hexdigest()+'.source.mp4')
 atomic_download(item['source_url'],source,'video',c['runtime']['source_max_bytes'],item.get('source_sha256'),c['runtime']['source_download_timeout_seconds'])
 source_dur=duration(source); _validate_source_ranges(item,timeline,source_dur)
 mt=item['music_track']; music_raw=CACHE/('music-'+hashlib.sha256(mt['url'].encode()).hexdigest()+'.source')
 atomic_download(mt['url'],music_raw,'audio',c['runtime']['music_max_bytes'],mt.get('sha256'),90)
 music=root/'music-master.m4a'; music_lufs,music_tp=normalize_music(c,music_raw,music)

 scene_jobs=[]
 for i,s in enumerate(item['scene_plan']):
  timeline_start,timeline_end,target=timeline[i]; source_start=float(s['start_seconds'])
  scene_jobs.append((source,source_start,target,root/f'scene-{i:02d}.mp4',c['runtime']['scene_encoder_threads']))
 workers=max(1,min(int(c['runtime']['scene_workers_per_video']),len(scene_jobs)))
 with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex: list(ex.map(lambda a:precut_scene(*a),scene_jobs))
 scenes=[]
 for i,(src,start,target,out,threads) in enumerate(scene_jobs):
  actual=duration(out); timeline_start,timeline_end,_=timeline[i]
  if actual+0.12<target: raise RuntimeError(f'SCENE_PRECUT_SHORT scene={i} actual={actual:.3f} target={target:.3f}')
  if c['runtime'].get('scene_black_guard_before_render',True): black_intervals(out,c,max_duration=target,label=f'SCENE_{i:02d}')
  scenes.append({'index':i,'file':out.name,'sha256':sha256(out),'duration':actual,'target_duration':target,'timeline_start':timeline_start,'timeline_end':timeline_end,'source_start':start,'caption_start':item['scene_plan'][i]['caption_start'],'caption_end':item['scene_plan'][i]['caption_end'],'semantic_reason':item['scene_plan'][i]['semantic_reason'],'blank_visual_pass':True})
 manifest={'schema':'CENA_CERTA_PREPARED_ASSETS_V2','id':rid,'prepared_pass':True,'no_blank_visual_pass':True,'prepared_asset_fingerprint':prepared_asset_fingerprint(item),'prepared_contract_fingerprint':prepared_contract_fingerprint(c),'prepared_engine_fingerprint':engine_fingerprint(),'created_epoch':time.time(),'source_duration':source_dur,'story_duration':story,'voice_wpm':round(wpm,1),'story_to_cta_gap_seconds':round(cta_entry_gap,3),'cues':cues,'voice':{'file':voice.name,'sha256':sha256(voice),'duration':vd},'cta_voice':{'file':cta_voice.name,'sha256':sha256(cta_voice),'duration':cvd,'cues':cta_cues},'music':{'file':music.name,'sha256':sha256(music),'duration':duration(music),'track_id':mt['id'],'master_lufs':music_lufs,'master_true_peak':music_tp},'scenes':scenes,'timeline_coverage_seconds':sum(x['target_duration'] for x in scenes),'prepare_elapsed_seconds':round(time.time()-t0,2)}
 tmp=root/'prepared.json.tmp'; tmp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8'); os.replace(tmp,root/'prepared.json')
 print('FACTORY_V2_READY_ASSETS_PASS',rid,manifest['prepare_elapsed_seconds']); return manifest

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--batch',required=True); ap.add_argument('--index',required=True,type=int); ap.add_argument('--prepared-root',required=True); a=ap.parse_args(); prepare_one(a.batch,a.index,a.prepared_root)
if __name__=='__main__': main()

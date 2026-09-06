#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, re, time
from pathlib import Path
from .common import *
from .preflight import validate_item
from .fingerprint import prepared_asset_fingerprint, prepared_contract_fingerprint, dispatch_fingerprint, engine_fingerprint
from .qa import qa_video

def _asset(root,spec,kind):
 name=Path(str(spec['file'])).name
 if name!=str(spec['file']): raise RuntimeError('PREPARED_ASSET_PATH_FAIL')
 p=root/name
 if not p.exists(): raise RuntimeError(f'PREPARED_ASSET_MISSING {name}')
 if sha256(p)!=spec['sha256']: raise RuntimeError(f'PREPARED_ASSET_HASH_FAIL {name}')
 media_probe(p,kind); return p

def _validate_prepared_cues(c,item,m,cues,voice_duration,story):
 if len(cues)!=len(item['caption_chunks']): raise RuntimeError('PREPARED_CUES_COUNT_FAIL')
 if normalize_text(' '.join(x['text'] for x in cues))!=normalize_text(' '.join(item['caption_chunks'])): raise RuntimeError('PREPARED_CUES_TEXT_FAIL')
 if not cues: raise RuntimeError('PREPARED_CUES_EMPTY')
 prev_end=None
 for i,cue in enumerate(cues):
  start=float(cue.get('start',-1)); end=float(cue.get('end',-1))
  if start<0 or end<=start: raise RuntimeError(f'PREPARED_CUE_RANGE_FAIL {i}')
  if prev_end is not None:
   gap=start-prev_end
   if gap>float(c['voice']['max_internal_speech_gap_seconds'])+0.01: raise RuntimeError(f'PREPARED_VOICE_GAP_FAIL cue={i} gap={gap:.3f}')
   if start+0.02<prev_end: raise RuntimeError(f'PREPARED_CUE_OVERLAP_FAIL cue={i}')
  prev_end=end
 if float(cues[0]['start'])>0.35: raise RuntimeError('PREPARED_FIRST_VOICE_LATE_FAIL')
 last_end=float(cues[-1]['end'])
 if last_end>voice_duration+0.08: raise RuntimeError('PREPARED_LAST_CUE_AFTER_VOICE_FAIL')
 target_min,target_max=(float(x) for x in c['story']['default_total_seconds'])
 if not (target_min<=story<=target_max) and item.get('duration_exception_approved') is not True: raise RuntimeError(f'PREPARED_STORY_DURATION_TARGET_FAIL {story:.3f}')
 expected_story=last_end+0.12
 if abs(story-expected_story)>0.08: raise RuntimeError(f'PREPARED_STORY_BOUNDARY_DRIFT actual={story:.3f} expected={expected_story:.3f}')
 gap=story+0.05-last_end
 if gap>float(c['voice']['story_to_cta_gap_max_seconds'])+0.001: raise RuntimeError(f'PREPARED_STORY_CTA_GAP_FAIL {gap:.3f}')
 return gap

def load_prepared(c,item,prepared_root):
 rid=safe_id(item['id']); root=Path(prepared_root)/rid; manifest_path=root/'prepared.json'
 if not manifest_path.exists(): raise RuntimeError(f'PREPARED_MANIFEST_MISSING {rid}')
 m=json.loads(manifest_path.read_text(encoding='utf-8'))
 if m.get('schema')!='CENA_CERTA_PREPARED_ASSETS_V2' or m.get('prepared_pass') is not True or m.get('id')!=rid: raise RuntimeError('PREPARED_MANIFEST_INVALID')
 asset_fp=m.get('prepared_asset_fingerprint',m.get('item_fingerprint'))
 if asset_fp!=prepared_asset_fingerprint(item): raise RuntimeError('PREPARED_ASSET_FINGERPRINT_FAIL')
 if m.get('prepared_contract_fingerprint')!=prepared_contract_fingerprint(c): raise RuntimeError('PREPARED_CONTRACT_FINGERPRINT_FAIL')
 current_engine=engine_fingerprint()
 if m.get('prepared_engine_fingerprint')!=current_engine: raise RuntimeError('PREPARED_ENGINE_FINGERPRINT_FAIL')
 age=(time.time()-float(m.get('created_epoch',0)))/3600; max_age=float(c['prepared_assets'].get('expire_hours',c['ready_queue']['expire_hours']))
 if age<-.25 or age>max_age: raise RuntimeError(f'PREPARED_ASSETS_STALE age_hours={age:.2f} max={max_age:.2f}')
 voice=_asset(root,m['voice'],'audio'); cta_voice=_asset(root,m['cta_voice'],'audio'); music=_asset(root,m['music'],'audio')
 voice_actual=duration(voice); cta_actual=duration(cta_voice); music_actual=duration(music)
 if abs(voice_actual-float(m['voice'].get('duration',0)))>0.12: raise RuntimeError('PREPARED_VOICE_DURATION_METADATA_FAIL')
 if abs(cta_actual-float(m['cta_voice'].get('duration',0)))>0.12: raise RuntimeError('PREPARED_CTA_DURATION_METADATA_FAIL')
 if abs(music_actual-float(m['music'].get('duration',0)))>0.15: raise RuntimeError('PREPARED_MUSIC_DURATION_METADATA_FAIL')
 if m['music'].get('track_id')!=item['music_track']['id']: raise RuntimeError('PREPARED_MUSIC_ID_FAIL')
 if len(m.get('scenes') or [])!=len(item['scene_plan']): raise RuntimeError('PREPARED_SCENE_COUNT_FAIL')
 scenes=[]; coverage=0.0; previous_end=0.0
 for i,s in enumerate(m['scenes']):
  if int(s.get('index',-1))!=i: raise RuntimeError('PREPARED_SCENE_INDEX_FAIL')
  p=_asset(root,s,'video'); target=float(s.get('target_duration',0)); actual=float(s.get('duration',0))
  if actual+0.12<target: raise RuntimeError(f'PREPARED_SCENE_SHORT {i}')
  ts=float(s.get('timeline_start',previous_end)); te=float(s.get('timeline_end',ts+target))
  if abs(ts-previous_end)>0.12 or te<=ts: raise RuntimeError(f'PREPARED_TIMELINE_GAP scene={i} start={ts:.3f} expected={previous_end:.3f}')
  previous_end=te; coverage+=target; scenes.append(p)
 story=float(m['story_duration'])
 if abs(previous_end-story)>0.15 or abs(coverage-story)>0.15: raise RuntimeError(f'PREPARED_TIMELINE_COVERAGE_FAIL end={previous_end:.3f} coverage={coverage:.3f} story={story:.3f}')
 cues=m.get('cues') or []
 _validate_prepared_cues(c,item,m,cues,voice_actual,story)
 return root,m,voice,cta_voice,music,scenes,cues,current_engine

def concat_scenes(root,scenes,expected_story):
 concat=root/'concat-render.txt'; concat.write_text('\n'.join("file '"+str(p.resolve()).replace("'","'\\''")+"'" for p in scenes),encoding='utf-8')
 raw=root/'story-scenes-render.mp4'; tmp=root/'story-scenes-render.part.mp4'
 try:
  sh(['ffmpeg','-loglevel','error','-y','-f','concat','-safe','0','-i',str(concat),'-an','-c','copy','-movflags','+faststart',str(tmp)],timeout=90)
  media_probe(tmp,'video'); d=duration(tmp)
  if abs(d-float(expected_story))>0.20: raise RuntimeError(f'CONCAT_DURATION_FAIL actual={d:.3f} expected={float(expected_story):.3f}')
  os.replace(tmp,raw)
 finally: tmp.unlink(missing_ok=True)
 return raw

def _loudnorm_analysis(path,target,tp):
 p=sh(['ffmpeg','-hide_banner','-nostats','-i',str(path),'-vn','-af',f'loudnorm=I={target}:TP={tp}:LRA=7:print_format=json','-f','null','-'],check=False,timeout=120)
 blocks=re.findall(r'\{[^{}]*"input_i"[^{}]*\}',p.stderr,re.S)
 if not blocks: raise RuntimeError('AUDIO_REPAIR_ANALYSIS_FAIL')
 return json.loads(blocks[-1])

def audio_only_repair(c,path):
 target=float(c['mix']['target_lufs']); contract_tp=float(c['mix']['true_peak_max_dbtp']); repair_tp=contract_tp-0.30; a=_loudnorm_analysis(path,target,repair_tp)
 filt=(f"loudnorm=I={target}:TP={repair_tp}:LRA=7:measured_I={a['input_i']}:measured_LRA={a['input_lra']}:" f"measured_TP={a['input_tp']}:measured_thresh={a['input_thresh']}:offset={a['target_offset']}:linear=true:print_format=summary")
 repaired=path.with_name(path.stem+'.audio-repair.mp4')
 try:
  sh(['ffmpeg','-loglevel','error','-y','-i',str(path),'-map','0:v:0','-map','0:a:0','-c:v','copy','-af',filt,'-c:a','aac','-b:a',c['canvas']['audio_bitrate'],'-ar',str(c['canvas']['sample_rate']),'-movflags','+faststart',str(repaired)],timeout=120)
  media_probe(repaired,'video'); os.replace(repaired,path)
 finally: repaired.unlink(missing_ok=True)

def render_one(batch,index,prepared_root):
 t0=time.time(); c=verify_contract_and_assets(); mask=prepare_static_assets(c); batch_path=Path(batch); batch_sha=sha256(batch_path); items=json.loads(batch_path.read_text(encoding='utf-8'))
 if index<0 or index>=len(items): raise RuntimeError(f'RENDER_INDEX_FAIL {index}/{len(items)}')
 item=items[index]; validate_item(c,item); rid=safe_id(item['id']); root,m,voice,cta_voice,music,scenes,cues,engine_fp=load_prepared(c,item,prepared_root)
 vd=float(m['voice']['duration']); story=float(m['story_duration']); voice_story_dur=min(vd,story); wpm=float(m['voice_wpm']); cvd=float(m['cta_voice']['duration']); cta_seconds=float(c['cta']['duration_seconds']); total=story+cta_seconds
 if cvd>cta_seconds-0.15: raise RuntimeError(f'CTA_VOICE_DURATION_FAIL voice={cvd:.3f} budget={cta_seconds-0.15:.3f}')
 cta_cues=m['cta_voice'].get('cues') or []
 if cta_cues and float(cta_cues[-1]['end'])>cta_seconds-0.10: raise RuntimeError('CTA_BOUNDARY_OVERFLOW_FAIL')
 raw=concat_scenes(root,scenes,story); ass=root/'cc.ass'; make_ass(c,cues,ass); title=root/'title.png'; make_title(c,item['film_title'],item['film_year'],title); cta=CACHE/'cta-master.png'
 esc=str(ass.resolve()).replace('\\','\\\\').replace(':','\\:').replace("'","\\'"); fx,fy,fw,fh=c['geometry_approved_frame_1080x1920']['film_window']; tx,ty,tw,th=c['geometry_approved_frame_1080x1920']['title_panel']; fps=int(c['canvas']['fps'])
 music_gain=float(c['music'].get('final_gain_db',-10.0)); fade=float(c['music'].get('final_fade_seconds',[0.7,0.7])[0] if isinstance(c['music'].get('final_fade_seconds'),list) else 0.7)
 fc=';'.join([
  f'[0:v]trim=duration={story:.3f},setpts=PTS-STARTPTS,setsar=1,fps={fps},split=2[bg0][fg0]',
  '[bg0]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,gblur=sigma=5,scale=1080:1920,setsar=1,eq=brightness=-0.25:contrast=0.98:saturation=0.86[bg]',
  f'[fg0]scale={fw}:{fh}:force_original_aspect_ratio=decrease,setsar=1[fg]',f'[bg][fg]overlay={fx}+({fw}-w)/2:{fy}+({fh}-h)/2,setsar=1[film]',
  f"[film]subtitles='{esc}',setsar=1[captioned]",f'[1:v]scale={tw}:{th},setsar=1,fps={fps},format=rgba[ttl]',f'[captioned][ttl]overlay={tx}:{ty},setsar=1[titled]',f'[2:v]setsar=1,fps={fps},format=rgba[mask]',f'[titled][mask]overlay=0:0,setsar=1,fps={fps}[storyv]',
  f'[3:v]scale=1080:1920,setsar=1,fps={fps},trim=duration={cta_seconds:.3f},setpts=PTS-STARTPTS[ctav]',f'[storyv]trim=duration={story:.3f},setpts=PTS-STARTPTS,setsar=1,fps={fps}[sv];[sv][ctav]concat=n=2:v=1:a=0,setsar=1,fps={fps},fade=t=out:st={total-fade:.3f}:d={fade:.3f}[vout]',
  f'[4:a]atrim=0:{voice_story_dur:.3f},asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-2:LRA=7,apad=whole_dur={total:.3f}[voice]',
  f'[5:a]atrim=0:{cvd:.3f},asetpts=PTS-STARTPTS,adelay={int((story+0.05)*1000)}|{int((story+0.05)*1000)},apad=whole_dur={total:.3f}[cta]',
  '[voice][cta]amix=inputs=2:duration=longest:normalize=0[voc0];[voc0]asplit=2[key][voc]',f'[6:a]atrim=0:{total:.3f},volume={music_gain}dB[music0];[music0][key]sidechaincompress=threshold=0.025:ratio=6:attack=15:release=240[music]',
  f'[voc][music]amix=inputs=2:duration=longest:normalize=0,loudnorm=I={c["mix"]["target_lufs"]}:TP=-1.7:LRA=7,afade=t=out:st={total-fade:.3f}:d={fade:.3f}[aout]'])
 out=OUT/f'{rid}.mp4'; tmp=OUT/f'{rid}.part.mp4'; tmp.unlink(missing_ok=True)
 try:
  sh(['ffmpeg','-loglevel','error','-y','-i',str(raw),'-loop','1','-i',str(title),'-loop','1','-i',str(mask),'-loop','1','-i',str(cta),'-i',str(voice),'-i',str(cta_voice),'-stream_loop','-1','-i',str(music),'-filter_complex',fc,'-map','[vout]','-map','[aout]','-r',str(fps),'-fps_mode','cfr','-c:v','libx264','-threads',str(c['runtime']['final_encoder_threads']),'-preset',os.getenv('ORBIT_X264_PRESET','veryfast'),'-crf',os.getenv('ORBIT_CRF','18'),'-pix_fmt','yuv420p','-c:a','aac','-b:a',c['canvas']['audio_bitrate'],'-ar',str(c['canvas']['sample_rate']),'-movflags','+faststart','-t',f'{total:.3f}',str(tmp)],timeout=360)
  media_probe(tmp,'video'); os.replace(tmp,out)
 finally: tmp.unlink(missing_ok=True)
 audio_repair=False
 try:
  qa=qa_video(c,item,out,story,cues)
 except RuntimeError as e:
  private_preview_repair=os.getenv('ORBIT_PRIVATE_PREVIEW_AUDIO_REPAIR','0')=='1'
  timed_repair=c.get('runtime',{}).get('audio_repair_in_timed_run',False) is True
  repair_allowed=private_preview_repair or timed_repair
  if repair_allowed and str(e).startswith(('LUFS_FAIL','TRUE_PEAK_FAIL')):
   audio_only_repair(c,out); audio_repair=True; qa=qa_video(c,item,out,story,cues)
  else:
   raise
 receipt={'schema':'CENA_CERTA_FACTORY_V2_RECEIPT','id':rid,'state':'PREVIEW_READY','ready_assets_pass':True,'render_pass':True,'qa_pass':True,'editorial_pass':False,'private_preview_pass':False,'human_approval':False,'delivered':False,'scheduled':False,'published':False,'duration':duration(out),'video_sha256':sha256(out),'batch_sha256':batch_sha,'story_duration':story,'story_to_cta_gap_seconds':round(story+0.05-float(cues[-1]['end']),3),'cta_duration':cta_seconds,'voice_wpm':round(wpm,1),'music_track_id':item['music_track']['id'],'rights_evidence':item['rights_evidence'],'anti_repeat_evidence':item['anti_repeat_evidence'],'relevance_evidence':item['relevance_evidence'],'scene_plan_count':len(item['scene_plan']),'prepared_manifest_sha256':sha256(root/'prepared.json'),'prepared_asset_fingerprint':prepared_asset_fingerprint(item),'prepared_engine_fingerprint':engine_fp,'dispatch_fingerprint':dispatch_fingerprint(item),'audio_repair_used':audio_repair,'mask_composite_order':'FILM_CC_TITLE_THEN_FINAL_STATIC_MASK','qa':qa,'elapsed_seconds':round(time.time()-t0,2)}
 tmpj=OUT/f'{rid}.receipt.json.tmp'; tmpj.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8'); os.replace(tmpj,OUT/f'{rid}.receipt.json')
 print('FACTORY_V2_RENDER_PASS',rid,receipt['elapsed_seconds'])

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--batch',required=True); ap.add_argument('--index',required=True,type=int); ap.add_argument('--prepared-root',required=True); a=ap.parse_args(); render_one(a.batch,a.index,a.prepared_root)
if __name__=='__main__': main()
#!/usr/bin/env python3
from __future__ import annotations
import json, time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from .common import *
from .fingerprint import prepared_asset_fingerprint, prepared_contract_fingerprint
from .render import render_one

def _tone(path,freq,dur):
 sh(['ffmpeg','-loglevel','error','-y','-f','lavfi','-i',f'sine=frequency={freq}:sample_rate=48000:duration={dur}','-c:a','libmp3lame','-b:a','128k',str(path)],timeout=60); media_probe(path,'audio')

def run():
 c=verify_contract_and_assets(); root=TMP/'selftest'; prepared=root/'prepared'; root.mkdir(parents=True,exist_ok=True)
 now=datetime.now(ZoneInfo(c['scheduler']['timezone'])); chunks=[f'Teste técnico {x}' for x in ('um','dois','três','quatro','cinco','seis','sete','oito','nove','dez')]
 item={'id':'CC-FACTORY-V2-SELFTEST','work_type':'film','film_title':'SELFTEST','film_year':2026,'source_url':'https://example.invalid/selftest.mp4','rights_evidence':'SELFTEST_ONLY','license':'SELFTEST_ONLY','rights_pass':True,'relevance_evidence':['SELFTEST_SIGNAL_1','SELFTEST_SIGNAL_2'],'relevance_pass':True,'anti_repeat_evidence':'SELFTEST_LEDGER','dedup_60d_pass':True,'live_readback_pass':True,'ready_checked_at':now.isoformat(),'source_clean_verified':True,'scene_semantic_verified':True,'caption_chunks':chunks,'script':' '.join(chunks),'scene_plan':[{'start_seconds':float(i),'caption_start':i,'caption_end':i,'semantic_reason':f'SELFTEST_SCENE_{i}','semantic_verified':True} for i in range(10)],'music_profile':'selftest','music_track':{'id':'SELFTEST-MUSIC','url':'https://example.invalid/music.mp3','rights_evidence':'SELFTEST_ONLY','license':'SELFTEST_ONLY','genre':'selftest','instrumental_verified':True,'editorial_match_verified':True},'schedule':{'date':(now+timedelta(days=2)).isoformat(),'text':'Selftest técnico.','youtube_title':'Selftest técnico','made_for_kids':False,'providers':c['scheduler']['networks'],'ai_flags':{'instagram':False,'tiktok':False,'youtube':False},'youtube_tags':[]}}
 batch=root/'batch.json'; batch.write_text(json.dumps([item],ensure_ascii=False),encoding='utf-8'); rid=item['id']; pr=prepared/rid; pr.mkdir(parents=True,exist_ok=True)
 voice=pr/'voice.mp3'; cta_voice=pr/'cta-voice.mp3'; music=pr/'music.mp3'; _tone(voice,330,10.0); _tone(cta_voice,440,2.0); _tone(music,140,20.0)
 cues=[{'text':txt,'start':i,'end':i+0.88} for i,txt in enumerate(chunks)]; story=10.12; scenes=[]
 for i in range(10):
  timeline_start=0.0 if i==0 else float(i); timeline_end=float(i+1) if i<9 else story; target=timeline_end-timeline_start
  p=pr/f'scene-{i:02d}.mp4'; sh(['ffmpeg','-loglevel','error','-y','-f','lavfi','-i',f'testsrc2=size=1280x720:rate=30:duration={target:.3f}','-vf',f'hue=h={i*18}:s=1','-an','-c:v','libx264','-threads','1','-preset','ultrafast','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',str(p)],timeout=60); media_probe(p,'video'); scenes.append({'index':i,'file':p.name,'sha256':sha256(p),'duration':duration(p),'target_duration':target,'timeline_start':timeline_start,'timeline_end':timeline_end,'source_start':float(i),'caption_start':i,'caption_end':i,'semantic_reason':f'SELFTEST_SCENE_{i}'})
 manifest={'schema':'CENA_CERTA_PREPARED_ASSETS_V2','id':rid,'prepared_pass':True,'prepared_asset_fingerprint':prepared_asset_fingerprint(item),'prepared_contract_fingerprint':prepared_contract_fingerprint(c),'created_epoch':time.time(),'source_duration':60,'story_duration':story,'voice_wpm':150.0,'cues':cues,'voice':{'file':voice.name,'sha256':sha256(voice),'duration':duration(voice)},'cta_voice':{'file':cta_voice.name,'sha256':sha256(cta_voice),'duration':duration(cta_voice)},'music':{'file':music.name,'sha256':sha256(music),'duration':duration(music),'track_id':'SELFTEST-MUSIC'},'scenes':scenes,'timeline_coverage_seconds':sum(x['target_duration'] for x in scenes)}
 (pr/'prepared.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 t0=time.time(); render_one(batch,0,prepared); elapsed=time.time()-t0; out=OUT/f'{rid}.mp4'; rec=json.loads((OUT/f'{rid}.receipt.json').read_text(encoding='utf-8'))
 if not out.exists() or not rec.get('qa_pass') or rec.get('mask_composite_order')!='FILM_CC_TITLE_THEN_FINAL_STATIC_MASK': raise RuntimeError('FACTORY_V2_SELFTEST_FAIL')
 print('FACTORY_V2_SELFTEST_PASS',round(elapsed,2),'seconds')
if __name__=='__main__': run()

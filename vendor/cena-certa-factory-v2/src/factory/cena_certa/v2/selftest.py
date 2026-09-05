#!/usr/bin/env python3
from __future__ import annotations
import json, time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from .common import *
from .fingerprint import prepared_asset_fingerprint, prepared_contract_fingerprint, engine_fingerprint
from .render import render_one

def _tone(path,freq,dur):
 sh(['ffmpeg','-loglevel','error','-y','-f','lavfi','-i',f'sine=frequency={freq}:sample_rate=48000:duration={dur}','-c:a','libmp3lame','-b:a','128k',str(path)],timeout=60); media_probe(path,'audio')

def run():
 c=verify_contract_and_assets(); root=TMP/'selftest'; prepared=root/'prepared'; root.mkdir(parents=True,exist_ok=True)
 now=datetime.now(ZoneInfo(c['scheduler']['timezone']))
 chunks=['A cena começa calma antes do perigo surgir','O personagem nota um detalhe que muda tudo','A câmera acompanha a reação sem perder contexto','O conflito cresce e a saída fica distante','Cada corte mantém a história conectada','A legenda fica baixa limpa e legível','O quadro preserva a proporção sem cortes','A música segue presente abaixo da voz','A virada acontece sem quebrar o ritmo','O rodapé permanece inteiro em todas as camadas','A consequência fecha a história sem enrolação','O CTA entra direto com voz música e identidade']
 validate_caption_layout(chunks,c)
 item={'id':'CC-FACTORY-V2-SELFTEST','work_type':'film','film_title':'MASCARA CENA CERTA STRESS','film_year':2026,'source_url':'https://example.invalid/selftest.mp4','rights_evidence':'SELFTEST_ONLY','license':'SELFTEST_ONLY','rights_pass':True,'relevance_evidence':['SELFTEST_SIGNAL_1','SELFTEST_SIGNAL_2'],'relevance_pass':True,'professional_production_pass':True,'audience_demand_pass':True,'recognized_or_acclaimed_pass':True,'production_class':'MAJOR_STUDIO','premium_evidence':[{'type':'DEMAND','source':'SELFTEST_DEMAND','signal':'synthetic demand gate proof'},{'type':'ACCLAIM','source':'SELFTEST_ACCLAIM','signal':'synthetic acclaim gate proof'},{'type':'PRODUCTION','source':'SELFTEST_PRODUCTION','signal':'synthetic professional production proof'}],'anti_repeat_evidence':'SELFTEST_LEDGER','dedup_60d_pass':True,'live_readback_pass':True,'ready_checked_at':now.isoformat(),'source_clean_verified':True,'scene_semantic_verified':True,'caption_chunks':chunks,'script':' '.join(chunks),'scene_plan':[{'start_seconds':float(i*3),'caption_start':i,'caption_end':i,'semantic_reason':f'SELFTEST_SCENE_{i}','semantic_verified':True} for i in range(len(chunks))],'music_profile':'selftest','music_track':{'id':'SELFTEST-MUSIC','url':'https://example.invalid/music.mp3','rights_evidence':'SELFTEST_ONLY','license':'SELFTEST_ONLY','genre':'selftest','instrumental_verified':True,'editorial_match_verified':True},'schedule':{'date':(now+timedelta(days=2)).isoformat(),'text':'Selftest técnico.','youtube_title':'Selftest técnico','made_for_kids':False,'providers':c['scheduler']['networks'],'ai_flags':{'instagram':False,'tiktok':False,'youtube':False},'youtube_tags':[]}}
 batch=root/'batch.json'; batch.write_text(json.dumps([item],ensure_ascii=False),encoding='utf-8'); rid=item['id']; pr=prepared/rid; pr.mkdir(parents=True,exist_ok=True)
 voice=pr/'voice.mp3'; cta_voice=pr/'cta-voice.mp3'; music=pr/'music.mp3'; _tone(voice,330,32.0); _tone(cta_voice,440,2.0); _tone(music,140,40.0)
 step=2.66; cues=[]
 for i,txt in enumerate(chunks):
  start=i*step; cues.append({'text':txt,'start':start,'end':start+2.50})
 cues[-1]['end']=32.0; story=float(cues[-1]['end'])+0.12; scenes=[]
 for i in range(len(chunks)):
  timeline_start=0.0 if i==0 else float(cues[i]['start']); timeline_end=float(cues[i+1]['start']) if i+1<len(chunks) else story; target=timeline_end-timeline_start
  p=pr/f'scene-{i:02d}.mp4'; sh(['ffmpeg','-loglevel','error','-y','-f','lavfi','-i',f'testsrc2=size=1280x720:rate=30:duration={target:.3f}','-vf',f'hue=h={i*15}:s=1','-an','-c:v','libx264','-threads','1','-preset','ultrafast','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',str(p)],timeout=60); media_probe(p,'video'); black_intervals(p,c,max_duration=target,label=f'SELFTEST_SCENE_{i}'); scenes.append({'index':i,'file':p.name,'sha256':sha256(p),'duration':duration(p),'target_duration':target,'timeline_start':timeline_start,'timeline_end':timeline_end,'source_start':float(i*3),'caption_start':i,'caption_end':i,'semantic_reason':f'SELFTEST_SCENE_{i}','blank_visual_pass':True})
 manifest={'schema':'CENA_CERTA_PREPARED_ASSETS_V2','id':rid,'prepared_pass':True,'no_blank_visual_pass':True,'prepared_asset_fingerprint':prepared_asset_fingerprint(item),'prepared_contract_fingerprint':prepared_contract_fingerprint(c),'prepared_engine_fingerprint':engine_fingerprint(),'created_epoch':time.time(),'source_duration':90,'story_duration':story,'voice_wpm':155.0,'story_to_cta_gap_seconds':round(story+0.05-float(cues[-1]['end']),3),'cues':cues,'voice':{'file':voice.name,'sha256':sha256(voice),'duration':duration(voice)},'cta_voice':{'file':cta_voice.name,'sha256':sha256(cta_voice),'duration':duration(cta_voice)},'music':{'file':music.name,'sha256':sha256(music),'duration':duration(music),'track_id':'SELFTEST-MUSIC'},'scenes':scenes,'timeline_coverage_seconds':sum(x['target_duration'] for x in scenes)}
 (pr/'prepared.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 t0=time.time(); render_one(batch,0,prepared); elapsed=time.time()-t0; out=OUT/f'{rid}.mp4'; rec=json.loads((OUT/f'{rid}.receipt.json').read_text(encoding='utf-8'))
 if not out.exists() or not rec.get('qa_pass') or rec.get('mask_composite_order')!='FILM_CC_TITLE_THEN_FINAL_STATIC_MASK': raise RuntimeError('FACTORY_V2_SELFTEST_FAIL')
 if rec.get('prepared_engine_fingerprint')!=engine_fingerprint(): raise RuntimeError('FACTORY_V2_SELFTEST_ENGINE_FINGERPRINT_FAIL')
 if rec.get('audio_repair_used') is not False: raise RuntimeError('FACTORY_V2_SELFTEST_UNEXPECTED_AUDIO_REPAIR')
 if rec.get('video_sha256')!=sha256(out): raise RuntimeError('FACTORY_V2_SELFTEST_VIDEO_HASH_FAIL')
 if rec.get('batch_sha256')!=sha256(batch): raise RuntimeError('FACTORY_V2_SELFTEST_BATCH_HASH_FAIL')
 if rec.get('qa',{}).get('canonical_mask_pass') is not True or rec.get('qa',{}).get('no_blank_visual_pass') is not True: raise RuntimeError('FACTORY_V2_SELFTEST_ACCEPTANCE_GATES_FAIL')
 if float(rec.get('story_to_cta_gap_seconds') or 99)>float(c['voice']['story_to_cta_gap_max_seconds']): raise RuntimeError('FACTORY_V2_SELFTEST_STORY_CTA_GAP_FAIL')
 if not (36.0<=float(rec.get('duration') or 0)<=38.0): raise RuntimeError('FACTORY_V2_SELFTEST_DURATION_PROFILE_FAIL')
 # Negative proof: a one-second black segment must be rejected by the same guard.
 black=root/'intentional-black.mp4'; sh(['ffmpeg','-loglevel','error','-y','-f','lavfi','-i','color=c=black:size=640x360:rate=30:duration=1','-c:v','libx264','-preset','ultrafast',str(black)],timeout=30)
 try: black_intervals(black,c,max_duration=1.0,label='SELFTEST_INTENTIONAL_BLACK')
 except RuntimeError as e:
  if 'BLANK_VISUAL_FAIL' not in str(e): raise
 else: raise RuntimeError('FACTORY_V2_SELFTEST_BLANK_GUARD_DID_NOT_BLOCK')
 print('FACTORY_V2_SELFTEST_STRESS_PASS',round(elapsed,2),'seconds','story_seconds',story,'caption_chunks',len(chunks),'full_mask=true','no_blank=true')
if __name__=='__main__': run()

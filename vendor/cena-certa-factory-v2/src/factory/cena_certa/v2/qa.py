from __future__ import annotations
import os, re
from PIL import Image
from .common import *

def _black_band_score(im,box,band=18):
 x,y,w,h=box; crop=im.crop((x,y,x+w,y+h)).convert('L'); a=np.asarray(crop)
 if a.size==0: return 0.0
 top=a[:band,:]; bottom=a[-band:,:]
 return max(float((top<6).mean()),float((bottom<6).mean()))

def _silence_guard(path,total):
 p=sh(['ffmpeg','-hide_banner','-nostats','-i',str(path),'-vn','-af','silencedetect=n=-45dB:d=0.70','-f','null','-'],check=False,timeout=120)
 durations=[float(x) for x in re.findall(r'silence_duration:\s*([0-9.]+)',p.stderr)]
 if any(x>0.72 for x in durations): raise RuntimeError(f'AUDIO_SILENCE_FAIL max={max(durations):.3f}')
 return max(durations) if durations else 0.0

def _masked_luma_mae(actual,reference_rgba,box):
 x,y,w,h=box; a=np.asarray(actual.crop((x,y,x+w,y+h)).convert('RGB'),dtype=np.float32)/255.0
 r=reference_rgba.crop((x,y,x+w,y+h)).convert('RGBA'); rr=np.asarray(r,dtype=np.float32); alpha=rr[:,:,3]>220
 if not alpha.any(): raise RuntimeError('MASKED_REFERENCE_EMPTY')
 rgb=rr[:,:,:3]/255.0; weights=np.asarray([0.2126,0.7152,0.0722],dtype=np.float32)
 ay=(a*weights).sum(axis=2); ry=(rgb*weights).sum(axis=2)
 return float(np.abs(ay[alpha]-ry[alpha]).mean())

def qa_video(c,item,out,story_duration,cues):
 probe=ffprobe(out); streams=probe.get('streams') or []; v=next((x for x in streams if x['codec_type']=='video'),None); a=next((x for x in streams if x['codec_type']=='audio'),None)
 if v is None or a is None: raise RuntimeError('TECH_STREAM_MISSING')
 if not (v['codec_name']=='h264' and int(v['width'])==1080 and int(v['height'])==1920 and v['pix_fmt']=='yuv420p'): raise RuntimeError('TECH_VIDEO_FAIL')
 if a['codec_name']!='aac' or int(a['sample_rate'])!=48000: raise RuntimeError('TECH_AUDIO_FAIL')
 if abs(fps_value(v.get('avg_frame_rate','0/1'))-30)>0.02: raise RuntimeError('FPS_FAIL')
 total=float(probe['format']['duration']); expected=story_duration+float(c['cta']['duration_seconds'])
 if abs(total-expected)>0.22: raise RuntimeError(f'DURATION_QA_FAIL actual={total:.3f} expected={expected:.3f}')
 lufs,tp=loudness(out)
 if not (c['mix']['target_lufs']-c['mix']['tolerance_lu']<=lufs<=c['mix']['target_lufs']+c['mix']['tolerance_lu']): raise RuntimeError(f'LUFS_FAIL {lufs}')
 if tp>c['mix']['true_peak_max_dbtp']: raise RuntimeError(f'TRUE_PEAK_FAIL {tp}')
 max_silence=_silence_guard(out,total)
 work=TMP/safe_id(item['id']); work.mkdir(parents=True,exist_ok=True); ref=scaled_reference(c,'story'); cta=Image.open(CACHE/'cta-master.png').convert('RGB'); mask=Image.open(CACHE/'story-mask-last.png').convert('RGBA'); geo=c['geometry_approved_frame_1080x1920']; vals={'checkpoints':[]}
 expected_title=work/'qa-expected-title.png'; make_title(c,item['film_title'],item['film_year'],expected_title); expected_title_im=Image.open(expected_title).convert('RGB')
 for n,fraction in enumerate(c['qa']['story_frame_checkpoints']):
  t=max(0.05,min(story_duration-0.05,story_duration*float(fraction))); frame=work/f'qa-story-{n}.png'; extract_frame(out,t,frame); sf=Image.open(frame).convert('RGB'); row={'t':round(t,3)}
  for key in ('footer','story_logo'):
   x,y,w,h=geo[key]; score=mae(sf.crop((x,y,x+w,y+h)),ref.crop((x,y,x+w,y+h))); row[key]=score
   if score>c['qa']['static_region_pixel_mae_max']: raise RuntimeError(f'STATIC_REGION_FAIL checkpoint={n} {key} {score:.4f}')
  tx,ty,tw,th=geo['title_panel']; title_score=mae(sf.crop((tx,ty,tx+tw,ty+th)),expected_title_im); row['title_panel']=title_score
  if title_score>c['qa']['title_panel_pixel_mae_max']: raise RuntimeError(f'TITLE_PANEL_PIXEL_FAIL checkpoint={n} score={title_score:.4f}')
  border_score=_masked_luma_mae(sf,mask,geo['film_window']); row['film_border_luma']=border_score
  if border_score>c['qa']['film_border_pixel_mae_max']: raise RuntimeError(f'FILM_BORDER_PIXEL_FAIL checkpoint={n} score={border_score:.4f}')
  black=_black_band_score(sf,geo['film_window']); row['black_edge_score']=black
  if c['qa']['black_padding_forbidden'] and black>0.985: raise RuntimeError(f'BLACK_PADDING_FAIL checkpoint={n} score={black:.4f}')
  vals['checkpoints'].append(row)
 cta_frame=work/'qa-cta.png'; extract_frame(out,story_duration+min(2.0,c['cta']['duration_seconds']*0.5),cta_frame); vals['cta_full']=mae(Image.open(cta_frame).convert('RGB'),cta)
 if vals['cta_full']>c['qa']['cta_pixel_mae_max']: raise RuntimeError(f'CTA_PIXEL_FAIL {vals["cta_full"]:.4f}')
 if normalize_text(' '.join(x['text'] for x in cues))!=normalize_text(' '.join(item['caption_chunks'])): raise RuntimeError('CAPTION_QA_FAIL')
 contact=None
 if os.getenv('ORBIT_CONTACT_SHEET','0')=='1':
  contact=OUT/f"{safe_id(item['id'])}-contact.jpg"; sh(['ffmpeg','-loglevel','error','-y','-i',str(out),'-vf','fps=1/5,scale=180:320,tile=4x3:padding=2:margin=2','-frames:v','1',str(contact)],timeout=120)
 return {'tech_pass':True,'geometry_pass':True,'title_pass':True,'film_border_pass':True,'caption_pass':True,'audio_pass':True,'duration_pass':True,'black_padding_pass':True,'lufs':lufs,'true_peak':tp,'max_silence_seconds':max_silence,'pixel_mae':vals,'contact_sheet':str(contact) if contact else None}

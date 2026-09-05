from __future__ import annotations
import hashlib, json, os, re, shutil, subprocess, textwrap, time
from fractions import Fraction
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
CONTRACT_PATH=HERE/'contract_v9_factory.json'
CACHE=ROOT/'.cache'/'cena-certa-v2'
OUT=ROOT/'output'/'cena-certa-v2'
TMP=ROOT/'tmp'/'cena-certa-v2'
for d in (CACHE,OUT,TMP): d.mkdir(parents=True,exist_ok=True)
GOLD=(244,181,44); WHITE=(245,245,245); BLACK=(4,5,7)
FONT_B='/usr/share/fonts/truetype/lato/Lato-Heavy.ttf'
FONT_R='/usr/share/fonts/truetype/lato/Lato-Regular.ttf'
SAFE_ID_RE=re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]{2,95}$')
RUNTIME_VISUAL_KEYS=('story','cta')

def sh(cmd,check=True,timeout=None):
 timeout=float(timeout or os.getenv('ORBIT_PROCESS_TIMEOUT_SECONDS','240'))
 try:
  p=subprocess.run(cmd,text=True,capture_output=True,timeout=timeout)
 except subprocess.TimeoutExpired as e:
  raise RuntimeError(f"PROCESS_TIMEOUT {cmd[0]} after {timeout:.0f}s") from e
 if check and p.returncode:
  raise RuntimeError(f"{cmd[0]} failed rc={p.returncode}: {(p.stderr or p.stdout or '')[-6000:]}")
 return p

def sha256(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()

def git_blob_sha1(path):
 b=Path(path).read_bytes(); return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()

def safe_id(value):
 s=str(value or '')
 if not SAFE_ID_RE.fullmatch(s) or '..' in s: raise RuntimeError(f'UNSAFE_ID {s!r}')
 return s

def open_visual(path):
 p=Path(path)
 if not p.is_file(): raise RuntimeError(f'VISUAL_ASSET_MISSING {p}')
 try:
  im=Image.open(p); im.load(); return im
 except Exception as e:
  raise RuntimeError(f'VISUAL_ASSET_PHYSICAL_IMAGE_FAIL {p}: {e}') from e

def pixel_sha256(path):
 im=open_visual(path).convert('RGB')
 return hashlib.sha256(im.tobytes()).hexdigest(), list(im.size)

def contract(): return json.loads(CONTRACT_PATH.read_text(encoding='utf-8'))
def font(size,bold=True):
 p=Path(FONT_B if bold else FONT_R)
 if not p.is_file(): raise RuntimeError(f'CANONICAL_FONT_MISSING {p}')
 return ImageFont.truetype(str(p),size)
def ffprobe(path,timeout=60): return json.loads(sh(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)],timeout=timeout).stdout)
def duration(path): return float(ffprobe(path)['format']['duration'])
def fps_value(rate): return float(Fraction(rate))
def normalize_text(s): return re.sub(r'\s+',' ',re.sub(r'[^0-9a-zà-ÿ]+',' ',str(s).lower(),flags=re.I)).strip()
def tokens(s): return normalize_text(s).split()

def free_disk_guard(min_free_gb=3.0):
 free=shutil.disk_usage(ROOT).free/(1024**3)
 if free<float(min_free_gb): raise RuntimeError(f'DISK_SPACE_FAIL free_gb={free:.2f} min_gb={min_free_gb}')
 return free

def media_probe(path,kind):
 p=ffprobe(path)
 streams=p.get('streams') or []
 if kind=='video' and not any(x.get('codec_type')=='video' for x in streams): raise RuntimeError(f'MEDIA_VIDEO_STREAM_MISSING {path}')
 if kind=='audio' and not any(x.get('codec_type')=='audio' for x in streams): raise RuntimeError(f'MEDIA_AUDIO_STREAM_MISSING {path}')
 d=float((p.get('format') or {}).get('duration') or 0)
 if d<=0.2: raise RuntimeError(f'MEDIA_DURATION_INVALID {path} {d}')
 return p

def atomic_download(url,path,kind,max_bytes,expected_sha256=None,timeout=150):
 path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
 def valid():
  if not path.exists() or path.stat().st_size<1024: return False
  if expected_sha256 and sha256(path)!=expected_sha256: return False
  try: media_probe(path,kind)
  except Exception: return False
  return True
 if valid(): return path
 if path.exists(): path.unlink()
 part=path.with_name(path.name+f'.part-{os.getpid()}-{int(time.time()*1000)}')
 try:
  cmd=['curl','--fail-with-body','--location','--silent','--show-error','--retry','2','--retry-delay','1','--retry-max-time','20','--retry-connrefused','--connect-timeout','10','--max-time',str(int(timeout)),'--max-filesize',str(int(max_bytes)),'-A','OrbitMediaLabs-CenaCertaFactory/2.1','-o',str(part),str(url)]
  sh(cmd,timeout=timeout+20)
  if not part.exists() or part.stat().st_size<1024: raise RuntimeError(f'DOWNLOAD_EMPTY {url}')
  if part.stat().st_size>max_bytes: raise RuntimeError(f'DOWNLOAD_TOO_LARGE bytes={part.stat().st_size} max={max_bytes}')
  if expected_sha256 and sha256(part)!=expected_sha256: raise RuntimeError('DOWNLOAD_SHA256_FAIL')
  media_probe(part,kind)
  os.replace(part,path)
 finally:
  if part.exists(): part.unlink(missing_ok=True)
 return path

def save_png_atomic(im,path):
 path=Path(path); tmp=path.with_name(path.name+f'.tmp-{os.getpid()}')
 im.save(tmp,format='PNG'); os.replace(tmp,path)

def verify_contract_and_assets():
 c=contract()
 assert c['schema']=='ORBIT_CENA_CERTA_FACTORY_V2' and c['fail_closed'] is True
 assert c['visual_precedence']=='APPROVED_FRAME_OVER_TABLE'
 assert c['canvas']['width']==1080 and c['canvas']['height']==1920 and c['canvas']['fps']==30
 assert c['voice']['caption_max_lines']==2 and c['voice']['max_internal_speech_gap_seconds']<=0.5
 assert c['selection']['movie_repeat_days']==60 and c['selection']['series_cooldown_days']==10
 assert c['selection']['professional_production_required'] is True and c['selection']['audience_demand_required'] is True
 assert c['selection']['student_amateur_backyard_production_forbidden'] is True and c['selection']['obscure_low_demand_fallback_forbidden'] is True
 assert c['story']['scene_min_count']>=10 and c['story']['no_blank_visual_during_story'] is True and 4<=c['cta']['duration_seconds']<=6
 assert c['qa']['story_black_interval_max_seconds']<=0.20
 assert c['sla']['daily_batch_size']==8 and c['sla']['network_count']==4 and c['sla']['target_seconds']<=660 and c['sla']['pilot_pair_target_seconds']<=180
 assert c['scheduler']['expected_placements_per_batch']==32
 for p in (Path(FONT_B),Path(FONT_R)):
  if not p.is_file(): raise RuntimeError(f'CANONICAL_FONT_MISSING {p}')
 free_disk_guard(c.get('runtime',{}).get('minimum_free_disk_gb',3.0))
 for name in RUNTIME_VISUAL_KEYS:
  spec=c['approved_visual_sources'][name]; p=ROOT/spec['path']
  if not p.exists(): raise RuntimeError(f'ASSET_MISSING {name}: {p}')
  open_visual(p)
  if spec.get('git_blob_sha1') and git_blob_sha1(p)!=spec['git_blob_sha1']: raise RuntimeError(f'ASSET_BLOB_LOCK_FAIL {name}')
  if spec.get('library_byte_sha256') and sha256(p)!=spec['library_byte_sha256']: raise RuntimeError(f'ASSET_BYTE_LOCK_FAIL {name}')
  if spec.get('pixel_sha256'):
   actual,size=pixel_sha256(p)
   if size!=spec.get('source_size') or actual!=spec['pixel_sha256']: raise RuntimeError(f'ASSET_VISUAL_ID_FAIL {name}')
 print('FACTORY_V2_CONTRACT_PASS'); print('FACTORY_V2_PHYSICAL_MASTER_LOCK_PASS'); print('FACTORY_V2_CANONICAL_FONTS_PASS')
 return c

def scaled_reference(c,key):
 p=ROOT/c['approved_visual_sources'][key]['path']
 return open_visual(p).convert('RGB').resize((1080,1920),Image.Resampling.LANCZOS)

def _physical_film_bezel(ref,box,bezel):
 x,y,w,h=box; crop=ref.crop((x,y,x+w,y+h)).convert('RGBA')
 inset=int(bezel.get('inset_pixels',6)); radius=int(bezel.get('corner_radius_pixels',24))
 if inset<2 or inset*2>=min(w,h): raise RuntimeError('FILM_BEZEL_INSET_FAIL')
 alpha=Image.new('L',(w,h),255); d=ImageDraw.Draw(alpha)
 d.rounded_rectangle((inset,inset,w-1-inset,h-1-inset),radius=max(2,radius),fill=0)
 rgba=np.asarray(crop,dtype=np.uint8).copy(); rgba[:,:,3]=np.asarray(alpha,dtype=np.uint8)
 protected=int((rgba[:,:,3]>0).sum())
 if protected<5000: raise RuntimeError(f'PHYSICAL_FILM_BEZEL_EXTRACTION_FAIL pixels={protected}')
 return Image.fromarray(rgba,'RGBA'),protected

def prepare_static_assets(c):
 ref=scaled_reference(c,'story'); geo=c['geometry_approved_frame_1080x1920']; footer=geo['footer']; logo=geo['story_logo']; film=geo['film_window']; bezel=geo['film_mask_bezel']
 fp=hashlib.sha256((json.dumps(geo,sort_keys=True)+c['approved_visual_sources']['story'].get('pixel_sha256','')+c['approved_visual_sources']['cta'].get('pixel_sha256','')+'physical-full-bezel-v3-cache-sealed').encode()).hexdigest()
 stamp=CACHE/'static-bundle.json'; outputs=[CACHE/'footer-master.png',CACHE/'story-logo-master.png',CACHE/'cta-master.png',CACHE/'story-mask-last.png']
 if stamp.exists() and all(p.exists() for p in outputs):
  try:
   state=json.loads(stamp.read_text(encoding='utf-8')); locked=state.get('output_sha256') or {}
   if state.get('fingerprint')==fp and all(locked.get(p.name)==sha256(p) for p in outputs):
    for p in outputs: open_visual(p)
    print('FACTORY_V2_STATIC_CACHE_VERIFIED_PASS')
    return CACHE/'story-mask-last.png'
  except Exception: pass
 save_png_atomic(ref.crop((footer[0],footer[1],footer[0]+footer[2],footer[1]+footer[3])),CACHE/'footer-master.png')
 save_png_atomic(ref.crop((logo[0],logo[1],logo[0]+logo[2],logo[1]+logo[3])),CACHE/'story-logo-master.png')
 save_png_atomic(scaled_reference(c,'cta'),CACHE/'cta-master.png')
 mask=Image.new('RGBA',(1080,1920),(0,0,0,0)); ring,protected=_physical_film_bezel(ref,film,bezel); mask.alpha_composite(ring,(film[0],film[1]))
 mask.alpha_composite(Image.open(CACHE/'story-logo-master.png').convert('RGBA'),(logo[0],logo[1]))
 mask.alpha_composite(Image.open(CACHE/'footer-master.png').convert('RGBA'),(footer[0],footer[1]))
 save_png_atomic(mask,CACHE/'story-mask-last.png')
 locked={p.name:sha256(p) for p in outputs}
 state={'fingerprint':fp,'physical_bezel_pixels':protected,'output_sha256':locked}
 tmp=stamp.with_name(stamp.name+f'.tmp-{os.getpid()}')
 try:
  tmp.write_text(json.dumps(state,sort_keys=True),encoding='utf-8'); os.replace(tmp,stamp)
 finally: tmp.unlink(missing_ok=True)
 print('FACTORY_V2_PHYSICAL_FULL_BEZEL_PASS',protected); print('FACTORY_V2_STATIC_CACHE_SEALED_PASS')
 return CACHE/'story-mask-last.png'

def make_title(c,title,year,out):
 x,y,w,h=c['geometry_approved_frame_1080x1920']['title_panel']; ax,ay,anchor_w,anchor_h=c['geometry_approved_frame_1080x1920']['title_static_anchor']
 if anchor_h!=h: raise RuntimeError(f'TITLE_ANCHOR_GEOMETRY_FAIL {anchor_h}!={h}')
 im=Image.new('RGB',(w,h),BLACK); d=ImageDraw.Draw(im)
 d.rounded_rectangle((0,0,w-1,h-1),radius=30,fill=BLACK,outline=GOLD,width=4); d.rounded_rectangle((7,7,w-8,h-8),radius=23,outline=(88,62,16),width=1)
 story=scaled_reference(c,'story'); anchor=story.crop((ax,ay,ax+anchor_w,ay+anchor_h)); im.paste(anchor,(0,0)); d=ImageDraw.Draw(im)
 d.line((anchor_w,25,anchor_w,h-25),fill=GOLD,width=3); name=str(title).upper().strip(); maxw=w-anchor_w-50; selected=None
 for sz in range(88,41,-2):
  cand=font(sz); bb=d.textbbox((0,0),name,font=cand,stroke_width=1)
  if bb[2]-bb[0]<=maxw: selected=cand; break
 if selected is None: raise RuntimeError(f'TITLE_OVERFLOW {title!r}')
 d.text((anchor_w+31,32),name,font=selected,fill=WHITE,stroke_width=2,stroke_fill=(74,58,28))
 d.rounded_rectangle((anchor_w+29,145,anchor_w+246,204),radius=24,fill=(7,8,10),outline=GOLD,width=3); d.text((anchor_w+61,152),str(year),font=font(38),fill=GOLD)
 save_png_atomic(im,out)

def wrap_caption_pixels(text,max_width=700,max_lines=2):
 f=font(52); d=ImageDraw.Draw(Image.new('RGB',(1,1))); words=str(text).split(); lines=[]; cur=''
 for word in words:
  if d.textbbox((0,0),word,font=f,stroke_width=4)[2]>max_width: raise RuntimeError(f'CAPTION_WORD_OVERFLOW {word!r}')
  cand=(cur+' '+word).strip()
  if d.textbbox((0,0),cand,font=f,stroke_width=4)[2]<=max_width: cur=cand
  else:
   if cur: lines.append(cur)
   cur=word
 if cur: lines.append(cur)
 if not lines or len(lines)>max_lines: raise RuntimeError(f'CAPTION_LAYOUT_FAIL lines={len(lines)} text={text!r}')
 return lines

def validate_caption_layout(chunks,c):
 safe_w=int(c['geometry_approved_frame_1080x1920']['cc_safe_zone'][2])-80
 for chunk in chunks: wrap_caption_pixels(chunk,max_width=safe_w,max_lines=c['voice']['caption_max_lines'])
 return True

def make_ass(c,cues,path):
 geo=c['geometry_approved_frame_1080x1920']; safe=geo['cc_safe_zone']; ref=geo['cc_reference_bbox']; width=int(c['canvas']['width']); height=int(c['canvas']['height'])
 margin_l=int(safe[0])+30; margin_r=width-(int(safe[0])+int(safe[2]))+30; margin_v=height-(int(ref[1])+int(ref[3]))
 header=f'''[Script Info]\nScriptType: v4.00+\nPlayResX: {width}\nPlayResY: {height}\nWrapStyle: 2\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: CC,Lato Heavy,52,&H00F7F7F7,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,4,0,2,{margin_l},{margin_r},{margin_v},1\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'''
 def at(sec):
  h=int(sec//3600); sec-=h*3600; m=int(sec//60); sec-=m*60; return f'{h}:{m:02d}:{sec:05.2f}'
 lines=[header]; maxw=int(safe[2])-80
 for cue in cues:
  wrapped=wrap_caption_pixels(cue['text'],max_width=maxw,max_lines=c['voice']['caption_max_lines'])
  lines.append(f"Dialogue: 0,{at(cue['start'])},{at(cue['end'])},CC,,0,0,0,,{'\\N'.join(wrapped)}\n")
 path.write_text(''.join(lines),encoding='utf-8')

def black_intervals(path,c,max_duration=None,crop=None,label='VIDEO'):
 q=c['qa']; max_blank=float(q['story_black_interval_max_seconds']); pix=float(q['story_black_pixel_threshold']); pic=float(q['story_black_picture_ratio'])
 vf=[]
 if crop:
  x,y,w,h=(int(v) for v in crop); vf.append(f'crop={w}:{h}:{x}:{y}')
 vf.append(f'blackdetect=d={max_blank:.3f}:pix_th={pix:.3f}:pic_th={pic:.3f}')
 cmd=['ffmpeg','-hide_banner','-nostats','-loglevel','info']
 if max_duration is not None: cmd+=['-t',f'{float(max_duration):.3f}']
 cmd+=['-i',str(path),'-an','-vf',','.join(vf),'-f','null','-']
 p=sh(cmd,check=False,timeout=120)
 found=[]
 for m in re.finditer(r'black_start:([0-9.]+)\s+black_end:([0-9.]+)\s+black_duration:([0-9.]+)',p.stderr or ''):
  found.append((float(m.group(1)),float(m.group(2)),float(m.group(3))))
 bad=[x for x in found if x[2]>max_blank+0.001]
 if bad: raise RuntimeError(f'{label}_BLANK_VISUAL_FAIL intervals={bad[:5]} max={max_blank}')
 return found

def mask_protected_mae(frame,reference,mask):
 a=np.asarray(frame.convert('RGB'),dtype=np.float32)/255.0; b=np.asarray(reference.convert('RGB'),dtype=np.float32)/255.0; alpha=np.asarray(mask.convert('RGBA'))[:,:,3]>200
 if not alpha.any(): raise RuntimeError('MASK_PROTECTED_PIXELS_EMPTY')
 return float(np.abs(a[alpha]-b[alpha]).mean())

def loudness(path):
 p=sh(['ffmpeg','-hide_banner','-nostats','-i',str(path),'-vn','-sn','-dn','-af','loudnorm=I=-15.5:TP=-1.5:LRA=7:print_format=json','-f','null','-'],check=False,timeout=120)
 blocks=re.findall(r'\{[^{}]*"input_i"[^{}]*\}',p.stderr,re.S)
 if not blocks: raise RuntimeError('LOUDNESS_PARSE_FAIL')
 d=json.loads(blocks[-1]); return float(d['input_i']),float(d['input_tp'])
def extract_frame(video,t,path): sh(['ffmpeg','-loglevel','error','-y','-ss',f'{t:.3f}','-i',str(video),'-frames:v','1',str(path)],timeout=60)
def mae(a,b):
 aa=np.asarray(a.convert('RGB'),dtype=np.float32)/255.0; bb=np.asarray(b.convert('RGB'),dtype=np.float32)/255.0
 return float(np.abs(aa-bb).mean())

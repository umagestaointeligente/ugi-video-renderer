#!/usr/bin/env python3
from __future__ import annotations
import argparse, asyncio, json, math, os, subprocess, sys, textwrap
from pathlib import Path
from urllib.request import Request, urlopen
from PIL import Image, ImageDraw, ImageFont, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import render_batch as rb
ROOT=Path(__file__).resolve().parents[3]; CANON=Path(__file__).resolve().parent
ASSETS=CANON/'assets'; OUT=ROOT/'output'; SRC=ROOT/'sources'; TMP=ROOT/'tmp'/'canonical-v1'
for d in (OUT,SRC,TMP): d.mkdir(parents=True,exist_ok=True)
W,H,FPS=1080,1920,30; FX,FY,FW,FH=16,664,1046,602; TX,TY,TW,TH=61,94,979,220
CTA_SECONDS=4.70; STORY_GAP=.12; GOLD=(244,181,44); WHITE=(245,245,245); BLACK=(4,5,7)
CONTRACT=CANON/'contract_cena_certa_canonical_mask_v1.json'; GUARD=CANON/'canonical_mask_guard.py'
LOGO=ASSETS/'cena_certa_logo_v1.jpg'; CLAPPER=ASSETS/'cena_certa_clapper_v1.jpg'
FONT_B='/usr/share/fonts/truetype/lato/Lato-Heavy.ttf'; FONT_R='/usr/share/fonts/truetype/lato/Lato-Regular.ttf'; FALLBACK='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def run(cmd):
 p=subprocess.run(cmd,text=True,capture_output=True)
 if p.returncode: raise RuntimeError(f'{cmd[0]} failed: {p.stderr[-5000:]}')
 return p.stdout
def ffprobe_duration(p): return float(run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)]).strip())
def font(sz,bold=True):
 p=FONT_B if bold else FONT_R
 return ImageFont.truetype(p if Path(p).exists() else FALLBACK,sz)
def fit_crop(img,size):
 tw,th=size; iw,ih=img.size; scale=max(tw/iw,th/ih); nw,nh=round(iw*scale),round(ih*scale); x=img.resize((nw,nh),Image.Resampling.LANCZOS); l=(nw-tw)//2; t=(nh-th)//2
 return x.crop((l,t,l+tw,t+th))
def black_to_alpha(patch,threshold=28):
 p=patch.convert('RGBA'); a=p.load()
 for y in range(p.height):
  for x in range(p.width):
   r,g,b,aa=a[x,y]; m=max(r,g,b)
   if m<threshold: a[x,y]=(r,g,b,0)
   elif m<58: a[x,y]=(r,g,b,int((m-threshold)/(58-threshold)*255))
 return p
def component(path,size): return black_to_alpha(fit_crop(Image.open(path).convert('RGB'),size))
def fit_text(draw,text,maxw,start,minsz):
 for s in range(start,minsz-1,-2):
  f=font(s); bb=draw.textbbox((0,0),text,font=f,stroke_width=1)
  if bb[2]-bb[0]<=maxw: return f
 return font(minsz)
def make_title(title,year,out):
 im=Image.new('RGB',(TW,TH),BLACK); d=ImageDraw.Draw(im); d.rounded_rectangle((0,0,TW-1,TH-1),radius=30,fill=BLACK,outline=GOLD,width=3); d.rounded_rectangle((7,7,TW-8,TH-8),radius=23,outline=(88,62,16),width=1)
 for off in (0,38,76): d.polygon([(780+off,8),(840+off,8),(760+off,212),(700+off,212)],fill=(11,12,14))
 rgba=im.convert('RGBA'); rgba.alpha_composite(component(CLAPPER,(230,210)),(12,5)); im=rgba.convert('RGB'); d=ImageDraw.Draw(im); d.line((260,28,260,192),fill=GOLD,width=3)
 name=str(title).upper().strip(); f=fit_text(d,name,610,100,46); d.text((292,34),name,font=f,fill=WHITE,stroke_width=2,stroke_fill=(74,58,28)); d.rounded_rectangle((290,145,510,203),radius=24,fill=(7,8,10),outline=GOLD,width=3)
 x,y=310,158; d.rounded_rectangle((x,y,x+28,y+25),radius=3,outline=GOLD,width=2); d.line((x,y+7,x+28,y+7),fill=GOLD,width=2); d.line((x+7,y-4,x+7,y+4),fill=GOLD,width=2); d.line((x+21,y-4,x+21,y+4),fill=GOLD,width=2); d.text((354,151),str(year),font=font(38),fill=GOLD); im.save(out,quality=95)
def make_static(out):
 ov=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov); d.rounded_rectangle((FX,FY,FX+FW,FY+FH),radius=20,outline=GOLD,width=3); ov.alpha_composite(component(LOGO,(99,168)),(910,371))
 footer=Image.new('RGBA',(995,201),(0,0,0,0)); fd=ImageDraw.Draw(footer); fd.rounded_rectangle((0,0,994,200),radius=48,fill=(3,4,5,247),outline=GOLD,width=3); fd.rounded_rectangle((7,7,987,193),radius=42,outline=(87,62,18),width=1)
 for yy in range(35,175,16):
  for xx in range(930,978,15): fd.ellipse((xx,yy,xx+3,yy+3),fill=(139,91,18,150))
 footer.alpha_composite(component(LOGO,(140,170)),(38,15)); fd=ImageDraw.Draw(footer); fd.line((218,26,218,175),fill=GOLD,width=2); top='Siga, curta e compartilhe'; bot='Cena Certa'; ft=fit_text(fd,top,690,48,34); bb=fd.textbbox((0,0),top,font=ft); x=250+(720-(bb[2]-bb[0]))//2; fd.text((x,36),top,font=ft,fill=WHITE); fd.line((300,112,850,112),fill=(190,129,20),width=2); fd.ellipse((570,108,578,116),fill=(255,201,75)); ft=fit_text(fd,bot,620,54,38); bb=fd.textbbox((0,0),bot,font=ft); x=250+(720-(bb[2]-bb[0]))//2; fd.text((x,122),bot,font=ft,fill=GOLD); ov.alpha_composite(footer,(42,1666)); ov.save(out)
def make_cta(out):
 im=Image.new('RGB',(W,H),(2,3,5)); d=ImageDraw.Draw(im)
 for x in (-100,760,900): d.polygon([(x,0),(x+170,0),(x-80,350),(x-250,350)],fill=(10,10,11))
 for yy in range(50,1850,22):
  for xx in range(20,95,18): d.ellipse((xx,yy,xx+3,yy+3),fill=(104,68,12))
  for xx in range(985,1060,18): d.ellipse((xx,yy,xx+3,yy+3),fill=(104,68,12))
 d.rounded_rectangle((55,285,1025,1840),radius=62,fill=(3,4,5),outline=GOLD,width=4); d.rounded_rectangle((68,298,1012,1827),radius=52,outline=(92,64,15),width=1)
 rgba=im.convert('RGBA'); rgba.alpha_composite(component(CLAPPER,(310,210)),(385,80)); rgba.alpha_composite(component(LOGO,(300,420)),(390,330)); im=rgba.convert('RGB'); d=ImageDraw.Draw(im); d.line((230,745,850,745),fill=(160,110,17),width=2); d.ellipse((536,740,546,750),fill=(255,201,70))
 for text,y,color,sz in [('Siga, curta e',800,WHITE,78),('compartilhe',890,WHITE,78),('o Cena Certa',990,GOLD,74)]:
  f=font(sz); bb=d.textbbox((0,0),text,font=f); d.text(((W-(bb[2]-bb[0]))//2,y),text,font=f,fill=color)
 centers=[285,540,795]; labels=['SIGA','CURTA','COMPARTILHE']
 for cx,label in zip(centers,labels):
  d.rounded_rectangle((cx-92,1180,cx+92,1315),radius=22,outline=(190,129,20),width=2)
  if label=='CURTA': d.polygon([(cx,1280),(cx-57,1231),(cx-51,1207),(cx-25,1192),(cx,1211),(cx+25,1192),(cx+51,1207),(cx+57,1231)],fill=GOLD)
  elif label=='SIGA': d.ellipse((cx-33,1202,cx+7,1242),outline=GOLD,width=4); d.arc((cx-52,1233,cx+26,1290),190,350,fill=GOLD,width=4); d.line((cx+34,1210,cx+34,1248),fill=GOLD,width=4); d.line((cx+15,1229,cx+53,1229),fill=GOLD,width=4)
  else: d.polygon([(cx-50,1258),(cx+20,1205),(cx+20,1233),(cx+58,1233),(cx+58,1268),(cx+20,1268),(cx+20,1296)],fill=GOLD)
  f=font(28); bb=d.textbbox((0,0),label,font=f); d.text((cx-(bb[2]-bb[0])//2,1330),label,font=f,fill=GOLD)
 for line,y in zip(['Qual filme merece','a próxima cena?'],[1450,1510]): f=font(52,False); bb=d.textbbox((0,0),line,font=f); d.text(((W-(bb[2]-bb[0]))//2,y),line,font=f,fill=WHITE)
 d.line((160,1510,250,1510),fill=GOLD,width=2); d.line((830,1510,920,1510),fill=GOLD,width=2); d.rounded_rectangle((220,1630,860,1775),radius=55,outline=GOLD,width=4); text='COMENTE AQUI'; f=font(60); bb=d.textbbox((0,0),text,font=f); d.text(((W-(bb[2]-bb[0]))//2,1664),text,font=f,fill=GOLD); im.save(out,quality=95)
def prep_static():
 for p in (LOGO,CLAPPER):
  if not p.exists(): raise RuntimeError(f'canonical component missing: {p}')
  Image.open(p).verify()
 make_static(TMP/'static.png'); make_cta(TMP/'cta.jpg')
def ass_time(sec):
 h=int(sec//3600); sec-=h*3600; m=int(sec//60); sec-=m*60; return f'{h}:{m:02d}:{sec:05.2f}'
def captions(words,path):
 groups=[]; g=[]
 for w in words:
  candidate=' '.join(x['text'] for x in g+[w])
  if g and (len(g)>=6 or len(candidate)>34): groups.append(g); g=[]
  g.append(w)
 if g: groups.append(g)
 header='''[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: CC,Lato Heavy,52,&H00F7F7F7,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,4,0,2,219,219,443,1\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'''; lines=[header]
 for grp in groups:
  txt=' '.join(w['text'] for w in grp); wr=textwrap.wrap(txt,width=29,break_long_words=False); wr=wr if len(wr)<=2 else [wr[0],' '.join(wr[1:])]; st=grp[0]['start']; en=grp[-1]['start']+grp[-1]['dur']+.04; lines.append(f"Dialogue: 0,{ass_time(st)},{ass_time(en)},CC,,0,0,0,,{'\\N'.join(wr)}\n")
 path.write_text(''.join(lines),encoding='utf-8')
def download(item):
 ext='mp4' if item.get('source_type')=='youtube' else 'webm'; p=SRC/f"{item['id']}.{ext}"
 if p.exists() and p.stat().st_size>200000: return p
 if item.get('source_type')=='youtube': run(['yt-dlp','--no-playlist','-f','bv*[height<=720]+ba/b[height<=720]','--merge-output-format','mp4','-o',str(p),item['source_url']]); return p
 req=Request(item['source_url'],headers={'User-Agent':'OrbitMediaLabs/1.0'})
 with urlopen(req,timeout=240) as r, open(p,'wb') as f:
  while True:
   b=r.read(1024*1024)
   if not b: break
   f.write(b)
 return p
def make_midi_music(item,duration,outwav):
 import mido
 profile=item.get('music_profile','scifi'); bpm,roots,lead_program={'scifi':(114,[45,41,48,43],0),'horror':(100,[38,41,36,43],42),'tactical':(118,[38,36,41,43],56)}[profile]
 mid=mido.MidiFile(ticks_per_beat=480); meta=mido.MidiTrack(); mid.tracks.append(meta); meta.append(mido.MetaMessage('set_tempo',tempo=mido.bpm2tempo(bpm),time=0)); pad=mido.MidiTrack(); bass=mido.MidiTrack(); lead=mido.MidiTrack(); drums=mido.MidiTrack(); mid.tracks.extend([pad,bass,lead,drums]); pad.append(mido.Message('program_change',program=48,channel=0,time=0)); bass.append(mido.Message('program_change',program=32,channel=1,time=0)); lead.append(mido.Message('program_change',program=lead_program,channel=2,time=0)); bars=math.ceil(duration/(4*60/bpm))+1
 for i in range(bars):
  root=roots[i%4]; chord=[root,root+3,root+7] if profile!='tactical' else [root,root+5,root+7]
  for n in chord: pad.append(mido.Message('note_on',note=n,velocity=38+(i%3)*3,channel=0,time=0))
  pad.append(mido.Message('note_off',note=chord[0],velocity=0,channel=0,time=1920))
  for n in chord[1:]: pad.append(mido.Message('note_off',note=n,velocity=0,channel=0,time=0))
  for b in range(4): bass.append(mido.Message('note_on',note=root-12,velocity=48+(b==0)*8,channel=1,time=0)); bass.append(mido.Message('note_off',note=root-12,velocity=0,channel=1,time=480))
  arp=[root+12,root+15,root+19,root+22,root+19,root+15,root+12,root+19]
  for j,n in enumerate(arp): lead.append(mido.Message('note_on',note=n,velocity=40+((i+j)%4)*4,channel=2,time=0)); lead.append(mido.Message('note_off',note=n,velocity=0,channel=2,time=240))
  for beat in range(8):
   note,vel=(36,52) if beat in (0,4) else ((38,43) if beat in (2,6) else (42,30)); drums.append(mido.Message('note_on',note=note,velocity=vel,channel=9,time=0)); drums.append(mido.Message('note_off',note=note,velocity=0,channel=9,time=240))
 midi=TMP/f"{item['id']}.mid"; mid.save(midi); found=list(Path('/usr/share/sounds').rglob('*.sf2')); sf=Path('/usr/share/sounds/sf2/TimGM6mb.sf2') if Path('/usr/share/sounds/sf2/TimGM6mb.sf2').exists() else (found[0] if found else None)
 if not sf: raise RuntimeError('SoundFont not found')
 run(['fluidsynth','-ni','-g','0.65','-F',str(outwav),'-r','48000',str(sf),str(midi)])
def build_story_filter(scene_starts,story):
 n=max(1,len(scene_starts)); seg=story/n; parts=[f'[0:v]split={n}'+''.join(f'[s{i}]' for i in range(n))]; labels=[]
 for i,st in enumerate(scene_starts): lab=f'c{i}'; parts.append(f'[s{i}]trim=start={float(st):.3f}:duration={seg:.3f},setpts=PTS-STARTPTS[{lab}]'); labels.append(f'[{lab}]')
 parts.append(''.join(labels)+f'concat=n={n}:v=1:a=0[raw]'); return parts
def render(item):
 year=int(item['film_year'])
 if year<1985: raise RuntimeError('YEAR_GATE_FAIL')
 if not item.get('dedup_60d_pass'): raise RuntimeError('DEDUP_60D_GATE_FAIL')
 prep_static(); src=download(item); sd=ffprobe_duration(src); title=TMP/f"{item['id']}-title.jpg"; make_title(item['film_title'],year,title); voice=TMP/f"{item['id']}-voice.mp3"; words=asyncio.run(rb.voice_and_words(item['script'],voice)); vd=ffprobe_duration(voice); story=vd+STORY_GAP; total=story+CTA_SECONDS; ass=TMP/f"{item['id']}.ass"; captions(words,ass); ctv=TMP/f"{item['id']}-cta.mp3"; asyncio.run(rb.voice_and_words('Siga, curta e compartilhe o Cena Certa.',ctv)); cvd=ffprobe_duration(ctv); music=TMP/f"{item['id']}-music.wav"; make_midi_music(item,total,music); starts=[float(x) for x in item.get('scene_starts',[])] or [float(item.get('start_seconds',0))]
 if any(x<0 or x>=sd for x in starts): raise RuntimeError('SCENE_START_OUT_OF_RANGE')
 esc=str(ass).replace('\\','\\\\').replace(':','\\:').replace("'","\\'"); fs=build_story_filter(starts,story); fs += ['[raw]split=3[bg0][wb0][fg0]','[bg0]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,gblur=sigma=5,scale=1080:1920,eq=brightness=-0.28:contrast=0.98:saturation=0.84[bg]',f'[wb0]scale={FW}:{FH}:force_original_aspect_ratio=increase,crop={FW}:{FH},gblur=sigma=12,eq=brightness=-0.08:saturation=0.88[wb]',f'[fg0]scale={FW}:{FH}:force_original_aspect_ratio=decrease[fg]','[wb][fg]overlay=(W-w)/2:(H-h)/2[film]',f'[bg][film]overlay={FX}:{FY}[base]',f'[1:v]scale={TW}:{TH},format=rgba[title]',f'[base][title]overlay={TX}:{TY}[titled]','[2:v]format=rgba[static]','[titled][static]overlay=0:0[storybase]',f"[storybase]subtitles='{esc}'[storyv]",f'[3:v]scale=1080:1920,trim=duration={CTA_SECONDS:.3f},setpts=PTS-STARTPTS[ctav]',f'[storyv]trim=duration={story:.3f},setpts=PTS-STARTPTS[sv];[sv][ctav]concat=n=2:v=1:a=0,fade=t=out:st={total-.25:.3f}:d=.25[vout]']; delay=int((story+.05)*1000); fs += [f'[4:a]atrim=0:{vd:.3f},asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-2:LRA=7,apad=pad_dur={total:.3f}[svoc]',f'[5:a]atrim=0:{cvd:.3f},asetpts=PTS-STARTPTS,adelay={delay}|{delay},apad=pad_dur={total:.3f}[cvoc]','[svoc][cvoc]amix=inputs=2:duration=longest:normalize=0[voc]',f'[6:a]atrim=0:{total:.3f},volume=-11.5dB[m0]','[m0][voc]sidechaincompress=threshold=.018:ratio=6:attack=15:release=230[md]',f'[voc][md]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-15.5:TP=-2.0:LRA=7,afade=t=out:st={total-.25:.3f}:d=.25[aout]']; out=OUT/f"{item['id']}.mp4"; cmd=['ffmpeg','-y','-i',str(src),'-loop','1','-i',str(title),'-loop','1','-i',str(TMP/'static.png'),'-loop','1','-i',str(TMP/'cta.jpg'),'-i',str(voice),'-i',str(ctv),'-i',str(music),'-filter_complex',';'.join(fs),'-map','[vout]','-map','[aout]','-r','30','-c:v','libx264','-preset',os.getenv('ORBIT_X264_PRESET','veryfast'),'-crf',os.getenv('ORBIT_CRF','18'),'-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart','-t',f'{total:.3f}',str(out)]; run(cmd); report=run([sys.executable,str(GUARD),'--candidate',str(out),'--contract',str(CONTRACT)])
 if 'CANONICAL_MASK_CANDIDATE_PASS' not in report: raise RuntimeError('canonical guard did not pass')
 (OUT/f"{item['id']}-canonical-mask-report.txt").write_text(report,encoding='utf-8'); rec={'id':item['id'],'canonical':'ORBIT_CENA_CERTA_CANONICAL_MASK_V1','canonical_mask_pass':True,'film_title':item['film_title'],'film_year':year,'duration':ffprobe_duration(out),'voice_duration':vd,'story_duration':story,'cta_seconds':CTA_SECONDS,'speechless_story_tail':round(story-vd,3),'music_profile':item.get('music_profile'),'scene_starts':starts,'rights_evidence':item.get('rights_evidence'),'dedup_60d_pass':True,'publication_gate':'HUMAN_APPROVAL_REQUIRED'}; (OUT/f"{item['id']}.receipt.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8'); print('CANONICAL_MASK_PASS',item['id'],f"{rec['duration']:.2f}s")
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--batch',default='golden_master/batch_canonical_pilots_v1.json'); ap.add_argument('--limit',type=int,default=0); a=ap.parse_args(); items=json.loads((ROOT/a.batch).read_text(encoding='utf-8')); items=items[:a.limit] if a.limit else items
 for item in items: render(item)
if __name__=='__main__': main()

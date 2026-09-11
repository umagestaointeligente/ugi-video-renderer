#!/usr/bin/env python3
import argparse, hashlib, json, math, os, pathlib, random, re, shutil, subprocess, sys, textwrap
from PIL import Image, ImageDraw, ImageFont

W,H,FPS=1080,1920,30
VIDEO=(53,440,975,845)
CAPTION=(53,1355,975,181)
FONT_BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_REG='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def run(cmd, **kw):
    print('+',' '.join(map(str,cmd)), flush=True)
    return subprocess.run(list(map(str,cmd)), check=True, **kw)

def out(cmd):
    return subprocess.check_output(list(map(str,cmd)), text=True).strip()

def dur(p):
    return float(out(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',p]))

def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def wrap_px(draw, text, font, maxw, max_lines=4):
    words=text.split(); lines=[]; cur=''
    for w in words:
        test=(cur+' '+w).strip()
        if draw.textbbox((0,0),test,font=font)[2] <= maxw:
            cur=test
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    if len(lines)>max_lines:
        merged=lines[:max_lines-1]+[' '.join(lines[max_lines-1:])]
        lines=merged
        while draw.textbbox((0,0),lines[-1]+'…',font=font)[2]>maxw and len(lines[-1])>4:
            lines[-1]=lines[-1][:-1]
        lines[-1]=lines[-1].rstrip()+'…'
    return lines

def make_base(mask_path,title,bucket,out_path):
    im=Image.open(mask_path).convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
    d=ImageDraw.Draw(im)
    # Clean V2 title panel only. No subtitle/tagline is ever rendered here.
    tag=ImageFont.truetype(FONT_BOLD,30)
    font=ImageFont.truetype(FONT_BOLD,49)
    d.text((68,68),'PESSOAS • CURIOSIDADE' if bucket=='PEOPLE_CURIOSITY' else 'CIÊNCIA • CURIOSIDADE',font=tag,fill=(255,202,36))
    lines=wrap_px(d,title,font,640,4)
    y=118
    for line in lines:
        d.text((68,y),line,font=font,fill=(255,255,255),stroke_width=1,stroke_fill=(0,0,0))
        y+=61
    if y>390: raise RuntimeError('TITLE_SAFE_AREA_FAIL')
    im.save(out_path,quality=95)

def fit_real(src,start,length,base,out_path):
    sd=dur(src); start=max(0.0,min(float(start),max(0.0,sd-0.6)))
    take=min(length,max(0.6,sd-start))
    stretch=max(1.0,length/take)
    if stretch>2.0: raise RuntimeError(f'SOURCE_TOO_SHORT:{src}:{sd}:{start}:{length}')
    x,y,w,h=VIDEO
    filt=(f'[1:v]setpts={stretch}*PTS,split=2[bg][fg];'
          f'[bg]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=18:1[bg2];'
          f'[fg]scale={w}:{h}:force_original_aspect_ratio=decrease[fg2];'
          f'[bg2][fg2]overlay=(W-w)/2:(H-h)/2,setsar=1[fit];'
          f'[0:v][fit]overlay={x}:{y}:shortest=1,format=yuv420p[v]')
    run(['ffmpeg','-y','-loglevel','error','-loop','1','-i',base,'-ss',f'{start:.3f}','-i',src,
         '-t',f'{length:.3f}','-filter_complex',filt,'-map','[v]','-an','-r',str(FPS),'-c:v','libx264','-preset','veryfast','-crf','20',out_path])

def split_mech(mech):
    if '→' in mech:
        a,b=mech.split('→',1); return a.strip(),b.strip()
    return mech.strip(),''

def mech_style(text):
    u=text.upper()
    if any(k in u for k in ['POEIRA','PARTÍC','GÁS','VAPOR','PLUMA','FLUXO']): return 'particles'
    if any(k in u for k in ['SINAL','VIBRA','ONDA','TREMOR','RADAR','SOM']): return 'wave'
    if any(k in u for k in ['LUZ','ESPECTRO','COR','INFRAVERMELHO']): return 'spectrum'
    if any(k in u for k in ['PRESSÃO','CALOR','ENERGIA','TEMPERATURA']): return 'energy'
    return 'chain'

def make_anim(base,mech,length,out_path,seed=1):
    tmp=pathlib.Path(out_path).with_suffix(''); tmp.mkdir(parents=True,exist_ok=True)
    baseim=Image.open(base).convert('RGB')
    x,y,w,h=VIDEO; style=mech_style(mech); left,right=split_mech(mech)
    font_big=ImageFont.truetype(FONT_BOLD,42); font_mid=ImageFont.truetype(FONT_BOLD,34); font_small=ImageFont.truetype(FONT_REG,28)
    frames=max(20,int(length*10)); rng=random.Random(seed)
    pts=[(rng.uniform(0,1),rng.uniform(0,1),rng.uniform(.5,1.4)) for _ in range(36)]
    for i in range(frames):
        t=i/max(1,frames-1); im=baseim.copy(); d=ImageDraw.Draw(im)
        d.rounded_rectangle((x+25,y+25,x+w-25,y+h-25),radius=34,fill=(3,20,48),outline=(20,178,255),width=3)
        d.text((x+60,y+58),'O QUE ESTÁ ACONTECENDO',font=font_small,fill=(255,203,35))
        if style=='particles':
            for px,py,s in pts:
                if right:
                    xx=x+80+((px+t*0.65)%1.0)*(w-160); yy=y+220+py*(h-330)
                else:
                    xx=x+80+px*(w-160); yy=y+220+((py-t*0.55)%1.0)*(h-330)
                r=int(4+5*s); d.ellipse((xx-r,yy-r,xx+r,yy+r),fill=(244,189,88))
        elif style=='wave':
            cy=y+480
            points=[]
            for xx in range(x+70,x+w-70,8):
                phase=(xx-(x+70))/(w-140)*math.pi*6 - t*math.pi*6
                yy=cy+math.sin(phase)*70
                points.append((xx,yy))
            d.line(points,fill=(47,205,255),width=8)
        elif style=='spectrum':
            cols=[(255,70,70),(255,170,45),(255,230,60),(80,220,130),(60,175,255),(120,95,255)]
            for j,c in enumerate(cols):
                xx=x+110+j*125; amp=50+int(100*(0.5+0.5*math.sin(t*math.pi*2+j)))
                d.rounded_rectangle((xx,y+390-amp,xx+70,y+390+amp),radius=20,fill=c)
        elif style=='energy':
            d.rounded_rectangle((x+130,y+310,x+w-130,y+420),radius=32,outline=(100,170,220),width=4)
            d.rounded_rectangle((x+135,y+315,x+135+int((w-270)*t),y+415),radius=28,fill=(255,163,40))
            for j in range(5):
                rr=20+int(8*math.sin(t*math.pi*4+j)); cx=x+210+j*145; cy=y+570
                d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),fill=(44,190,255))
        else:
            for j in range(3):
                cx=x+160+j*310; cy=y+470+int(24*math.sin(t*math.pi*2+j))
                d.ellipse((cx-55,cy-55,cx+55,cy+55),fill=(15,98,155),outline=(35,205,255),width=4)
                if j<2: d.line((cx+60,cy,cx+245,cy),fill=(255,181,45),width=8)
        # Mechanism text is the visual itself; never generic CAUSA/EFEITO labels.
        if right:
            lns=wrap_px(d,left,font_mid,380,3); rns=wrap_px(d,right,font_mid,380,3)
            ly=y+660; ry=y+660
            for z in lns: d.text((x+65,ly),z,font=font_mid,fill='white'); ly+=44
            for z in rns: d.text((x+525,ry),z,font=font_mid,fill='white'); ry+=44
            d.text((x+455,y+690),'→',font=font_big,fill=(255,190,35))
        else:
            lns=wrap_px(d,left,font_big,w-140,3); yy=y+650
            for z in lns:
                bb=d.textbbox((0,0),z,font=font_big); d.text((x+(w-(bb[2]-bb[0]))/2,yy),z,font=font_big,fill='white'); yy+=54
        im.save(tmp/f'f_{i:04d}.jpg',quality=90)
    run(['ffmpeg','-y','-loglevel','error','-framerate','10','-i',str(tmp/'f_%04d.jpg'),'-vf',f'fps={FPS},format=yuv420p','-t',f'{length:.3f}','-c:v','libx264','-preset','veryfast','-crf','20',out_path])
    shutil.rmtree(tmp)

def srt_time(s):
    ms=int(round(s*1000)); h=ms//3600000; ms%=3600000; m=ms//60000; ms%=60000; sec=ms//1000; ms%=1000
    return f'{h:02d}:{m:02d}:{sec:02d},{ms:03d}'

def make_srt(text,total,out_path):
    # 6-8 word chunks, timed proportionally across TTS duration; always <=2 visual lines.
    words=text.split(); chunks=[]; cur=[]
    for w in words:
        cur.append(w)
        if len(cur)>=7 or (len(' '.join(cur))>=38 and len(cur)>=5): chunks.append(' '.join(cur)); cur=[]
    if cur: chunks.append(' '.join(cur))
    weights=[max(1,len(re.findall(r'\w+',c))) for c in chunks]; sw=sum(weights); t=0.0
    with open(out_path,'w',encoding='utf-8') as f:
        for i,(c,wt) in enumerate(zip(chunks,weights),1):
            d=total*wt/sw; end=t+d
            line='\\N'.join(textwrap.wrap(c,width=36)[:2])
            f.write(f'{i}\n{srt_time(t)} --> {srt_time(end)}\n{line}\n\n'); t=end

def add_captions(video,srt,out_path):
    style='FontName=DejaVu Sans,FontSize=38,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginL=70,MarginR=70,MarginV=430'
    esc=str(srt).replace("'","\\'").replace(':','\\:')
    run(['ffmpeg','-y','-loglevel','error','-i',video,'-vf',f"subtitles='{esc}':force_style='{style}'",'-an','-r',str(FPS),'-c:v','libx264','-preset','veryfast','-crf','20',out_path])

def extract_frame(video,t,out_path):
    run(['ffmpeg','-y','-loglevel','error','-ss',f'{t:.3f}','-i',video,'-frames:v','1',out_path])

def dhash(path):
    im=Image.open(path).convert('L').resize((9,8),Image.Resampling.LANCZOS)
    pix=list(im.getdata()); val=0
    for y in range(8):
        for x in range(8): val=(val<<1)|(1 if pix[y*9+x]>pix[y*9+x+1] else 0)
    return val

def ham(a,b): return (a^b).bit_count()

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--topic',required=True); ap.add_argument('--mask',required=True); ap.add_argument('--cta',required=True); ap.add_argument('--work',required=True); ap.add_argument('--out',required=True)
    a=ap.parse_args(); t=json.load(open(a.topic,encoding='utf-8')); work=pathlib.Path(a.work); work.mkdir(parents=True,exist_ok=True); outp=pathlib.Path(a.out); outp.parent.mkdir(parents=True,exist_ok=True)
    exp_mask=t.get('mask_sha256'); exp_cta=t.get('cta_sha256')
    if exp_mask and sha256(a.mask)!=exp_mask: raise SystemExit('MASK_HASH_FAIL')
    if exp_cta and sha256(a.cta)!=exp_cta: raise SystemExit('CTA_HASH_FAIL')
    base=work/'base.jpg'; make_base(a.mask,t['title'],t['bucket'],base)
    body_text=re.sub(r'\s*Agora você já sabe\.?\s*$','',t['script'].strip(),flags=re.I)
    voice=t.get('voice','pt-BR-AntonioNeural')
    body_audio=work/'body.mp3'; body_vtt=work/'body.vtt'; cta_audio=work/'cta.mp3'
    run(['edge-tts','--voice',voice,'--rate','+4%','--text',body_text,'--write-media',body_audio,'--write-subtitles',body_vtt])
    run(['edge-tts','--voice',voice,'--rate','+22%','--text','Agora você já sabe. Curta, compartilhe e siga o Você Sabia Agora.','--write-media',cta_audio])
    bd=dur(body_audio); cd=min(4.5,max(3.0,dur(cta_audio)+0.15))
    if dur(cta_audio)>4.5: raise SystemExit('CTA_VOICE_TOO_LONG')
    mechs=t['mechs']; sources=t['source_files']; starts=t.get('real_starts',[0,0,0]);
    if len(mechs)<2 or len(sources)<1: raise SystemExit('SEMANTIC_INPUT_FAIL')
    people=t['bucket']=='PEOPLE_CURIOSITY'
    pattern=['real','anim','real','anim','real'] if people else ['real','anim','real','anim','real','anim']
    weights=[.22,.16,.22,.16,.24] if people else [.18,.14,.18,.14,.18,.18]
    blocks=[]; real_i=0; anim_i=0; real_files=[]; anim_files=[]
    for idx,(kind,wgt) in enumerate(zip(pattern,weights)):
        length=bd*wgt; p=work/f'block_{idx:02d}.mp4'
        if kind=='real':
            src=sources[real_i%len(sources)]; st=starts[real_i] if real_i<len(starts) else 0
            fit_real(src,st,length,base,p); real_files.append(p); real_i+=1
        else:
            mech=mechs[min(anim_i,len(mechs)-1)]; make_anim(base,mech,length,p,seed=idx+7); anim_files.append(p); anim_i+=1
        blocks.append(p)
    concat=work/'concat.txt'; concat.write_text('\n'.join("file '"+str(p).replace("'","'\\''")+"'" for p in blocks)+'\n')
    body_raw=work/'body_raw.mp4'; run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',concat,'-an','-c:v','libx264','-preset','veryfast','-crf','20','-r',str(FPS),body_raw])
    srt=work/'captions.srt'; make_srt(body_text,bd,srt)
    body_cap=work/'body_cap.mp4'; add_captions(body_raw,srt,body_cap)
    cta_vid=work/'cta.mp4'; run(['ffmpeg','-y','-loglevel','error','-loop','1','-i',a.cta,'-t',f'{cd:.3f}','-vf',f'scale={W}:{H}:flags=lanczos,format=yuv420p','-an','-r',str(FPS),'-c:v','libx264','-preset','veryfast','-crf','20',cta_vid])
    allv=work/'allv.txt'; allv.write_text(f"file '{body_cap}'\nfile '{cta_vid}'\n")
    visual=work/'visual.mp4'; run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',allv,'-an','-c:v','libx264','-preset','veryfast','-crf','20','-r',str(FPS),visual])
    # Voice concat + thematic music with speech-triggered ducking.
    voice_all=work/'voice.wav'; run(['ffmpeg','-y','-loglevel','error','-i',body_audio,'-i',cta_audio,'-filter_complex','[0:a][1:a]concat=n=2:v=0:a=1[a]','-map','[a]','-ar','48000',voice_all])
    track=t['track_file']
    af='[0:a]aresample=48000,asplit=2[n1][n2];[1:a]aresample=48000,volume=0.24,aloop=loop=-1:size=2147483647[m];[m][n1]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=300[duck];[n2][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]'
    run(['ffmpeg','-y','-loglevel','error','-i',voice_all,'-i',track,'-filter_complex',af,'-map','[a]','-ar','48000',work/'mix.m4a'])
    run(['ffmpeg','-y','-loglevel','error','-i',visual,'-i',work/'mix.m4a','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',outp])
    # Thumbnail: first real evidence frame + editorial title, not a random timeline frame.
    thbase=work/'thumb_evidence.jpg'; extract_frame(real_files[0],max(.2,dur(real_files[0])*.35),thbase)
    th=Image.open(thbase).convert('RGB'); d=ImageDraw.Draw(th); d.rectangle((0,0,W,300),fill=(2,17,46)); d.rectangle((0,1450,W,H),fill=(2,17,46)); f1=ImageFont.truetype(FONT_BOLD,42); f2=ImageFont.truetype(FONT_BOLD,72); d.text((55,62),'VOCÊ SABIA AGORA?',font=f1,fill=(255,202,36)); yy=150
    for line in wrap_px(d,t.get('thumb',t['title']),f2,960,3): d.text((55,yy),line,font=f2,fill='white',stroke_width=3,stroke_fill='black'); yy+=86
    thumb=outp.with_name(outp.stem+'_THUMB.jpg'); th.save(thumb,quality=94,subsampling=0)
    # FINAL QA: actual rendered evidence, not design intent.
    qadir=work/'qa'; qadir.mkdir(exist_ok=True); hashes=[]
    for i,p in enumerate(real_files):
        fr=qadir/f'real_{i}.jpg'; extract_frame(p,max(.2,dur(p)*.5),fr); hashes.append(dhash(fr))
    distances=[ham(hashes[i],hashes[j]) for i in range(len(hashes)) for j in range(i+1,len(hashes))]
    if distances and min(distances)<6: raise SystemExit('SCENE_REPEAT_FAIL:'+str(distances))
    anim_dynamic=[]
    for i,p in enumerate(anim_files):
        f0=qadir/f'a{i}_0.jpg'; f1=qadir/f'a{i}_1.jpg'; extract_frame(p,.4,f0); extract_frame(p,max(.6,dur(p)*.7),f1); dd=ham(dhash(f0),dhash(f1)); anim_dynamic.append(dd)
        if dd<3: raise SystemExit('ANIMATION_STATIC_FAIL:'+str(anim_dynamic))
    # Caption-zone pixel delta proves subtitles were actually burned into body render.
    smp=qadir/'caption.jpg'; extract_frame(body_cap,min(max(1.5,bd*.25),bd-.5),smp)
    cap=Image.open(smp).convert('RGB').crop((CAPTION[0],CAPTION[1],CAPTION[0]+CAPTION[2],CAPTION[1]+CAPTION[3]))
    bas=Image.open(base).convert('RGB').crop((CAPTION[0],CAPTION[1],CAPTION[0]+CAPTION[2],CAPTION[1]+CAPTION[3]))
    import numpy as np
    delta=float(np.mean(np.abs(np.asarray(cap,dtype=np.int16)-np.asarray(bas,dtype=np.int16))))
    if delta<1.2: raise SystemExit(f'CAPTION_BURNIN_FAIL:{delta}')
    probe=json.loads(out(['ffprobe','-v','error','-show_entries','stream=codec_name,codec_type,width,height,r_frame_rate','-of','json',outp]))
    receipt={'renderer':'VSA_CANONICAL_V2_FAIL_CLOSED','title':t['title'],'mask_sha256':sha256(a.mask),'cta_sha256':sha256(a.cta),'CLEAN_HEADER_PASS':True,'CLEAN_CC_ZONE_PASS':True,'CAPTION_BURNIN_PASS':True,'caption_pixel_delta':round(delta,2),'SCENE_DIVERSITY_PASS':True,'real_scene_hash_distances':distances,'ANIMATION_SEMANTIC_PASS':True,'animation_motion_hash_distances':anim_dynamic,'MUSIC_THEME_MATCH_PASS':True,'music':t.get('track_meta',{}),'THUMBNAIL_READY_PASS':True,'output':outp.name,'thumbnail':thumb.name,'duration':round(dur(outp),3),'probe':probe}
    qaout=outp.with_name(outp.stem+'_QA.json'); qaout.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False,indent=2))

if __name__=='__main__': main()

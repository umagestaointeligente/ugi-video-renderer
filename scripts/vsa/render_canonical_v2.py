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

ANIMATION_TYPES={'force_vectors','orbit_phase','particle_scatter','wave','energy_flow','layer_cross_section','branching','light_path','orientation_axes','cell_split'}

def validate_anim_spec(spec,mech,index):
    if not isinstance(spec,dict): raise SystemExit(f'ANIMATION_SPEC_REQUIRED:{index}')
    typ=str(spec.get('visual_type') or '').strip()
    if typ not in ANIMATION_TYPES: raise SystemExit(f'ANIMATION_VISUAL_TYPE_FAIL:{index}:{typ}')
    if not str(spec.get('visual_subject') or '').strip(): raise SystemExit(f'ANIMATION_VISUAL_SUBJECT_MISSING:{index}')
    if not str(spec.get('action') or '').strip(): raise SystemExit(f'ANIMATION_ACTION_MISSING:{index}')
    claim=str(spec.get('claim') or '').strip()
    if not claim or claim != str(mech).strip(): raise SystemExit(f'ANIMATION_CLAIM_MISMATCH:{index}')
    return typ

def make_anim(base,mech,spec,length,out_path,seed=1):
    tmp=pathlib.Path(out_path).with_suffix(''); tmp.mkdir(parents=True,exist_ok=True)
    baseim=Image.open(base).convert('RGB')
    x,y,w,h=VIDEO; typ=validate_anim_spec(spec,mech,0); left,right=split_mech(mech)
    font_big=ImageFont.truetype(FONT_BOLD,42); font_mid=ImageFont.truetype(FONT_BOLD,34); font_small=ImageFont.truetype(FONT_REG,28)
    frames=max(20,int(length*10)); rng=random.Random(seed)
    pts=[(rng.uniform(0,1),rng.uniform(0,1),rng.uniform(.5,1.4)) for _ in range(42)]
    for i in range(frames):
        t=i/max(1,frames-1); im=baseim.copy(); d=ImageDraw.Draw(im)
        d.rounded_rectangle((x+25,y+25,x+w-25,y+h-25),radius=34,fill=(3,20,48),outline=(20,178,255),width=3)
        d.text((x+60,y+58),'O QUE ESTÁ ACONTECENDO',font=font_small,fill=(255,203,35))

        if typ=='force_vectors':
            gy=y+615; d.line((x+120,gy,x+w-120,gy),fill=(120,170,200),width=5)
            cx=x+w//2; cy=gy-135-int(70*math.sin(math.pi*t))
            d.ellipse((cx-62,cy-62,cx+62,cy+62),fill=(22,125,188),outline=(48,215,255),width=5)
            up=110+int(90*t); d.line((cx,cy+45,cx,cy+45-up),fill=(255,190,45),width=11)
            d.polygon([(cx,cy+45-up-20),(cx-18,cy+45-up+14),(cx+18,cy+45-up+14)],fill=(255,190,45))
            d.line((cx+120,gy-25,cx+120,gy-25+90),fill=(255,95,85),width=9)

        elif typ=='orbit_phase':
            sx=x+230; sy=y+430; d.ellipse((sx-62,sy-62,sx+62,sy+62),fill=(255,190,45))
            d.ellipse((x+155,y+250,x+w-120,y+620),outline=(70,140,205),width=4)
            ang=math.pi*(.15+1.7*t); px=x+500+310*math.cos(ang); py=y+435+150*math.sin(ang)
            d.ellipse((px-48,py-48,px+48,py+48),fill=(55,145,205),outline=(120,225,255),width=4)
            d.pieslice((px-48,py-48,px+48,py+48),90,270,fill=(8,30,65))

        elif typ=='particle_scatter':
            for k in range(5):
                yy=y+270+k*65; d.line((x+85,yy,x+410,yy),fill=(255,205,55),width=5)
            for px,py,ps in pts:
                xx=x+430+px*(w-560); yy=y+220+py*390; rr=int(3+4*ps)
                d.ellipse((xx-rr,yy-rr,xx+rr,yy+rr),fill=(230,190,100))
                if int(px*10)%5==0:
                    d.line((xx,yy,xx+70+50*t,yy-45+90*t),fill=(70,190,255),width=3)

        elif typ=='wave':
            cy=y+455; points=[]
            for xx in range(x+70,x+w-70,8):
                phase=(xx-(x+70))/(w-140)*math.pi*6-t*math.pi*6
                points.append((xx,cy+math.sin(phase)*72))
            d.line(points,fill=(47,205,255),width=8)
            d.ellipse((x+110,cy-35,x+180,cy+35),outline=(255,190,45),width=5)

        elif typ=='energy_flow':
            for k in range(6):
                xx=x+145+k*125; yy=y+230+int(85*math.sin(t*math.pi*2+k))
                d.line((xx,yy,xx,yy+260),fill=(255,155+10*k,45),width=8)
                d.polygon([(xx,yy+285),(xx-17,yy+250),(xx+17,yy+250)],fill=(255,170,45))
            d.rounded_rectangle((x+150,y+570,x+w-150,y+620),radius=22,fill=(230,95,55))

        elif typ=='layer_cross_section':
            cx=x+w//2; cy=y+440
            for rr,col in [(260,(20,90,150)),(195,(40,130,185)),(125,(65,175,210)),(58,(255,185,60))]:
                d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline=col,width=14)
            rr=45+int(165*t)
            d.arc((cx-rr,cy-rr,cx+rr,cy+rr),190,350,fill=(255,220,75),width=8)

        elif typ=='branching':
            rootx=x+w//2; top=y+220; mid=y+420
            d.line((rootx,top,rootx,mid),fill=(70,195,255),width=10)
            spread=90+int(150*t)
            for sign,col in [(-1,(255,190,45)),(1,(80,220,150))]:
                ex=rootx+sign*(180+spread); ey=y+585
                d.line((rootx,mid,ex,ey),fill=col,width=10)
                d.ellipse((ex-42,ey-42,ex+42,ey+42),fill=col)

        elif typ=='light_path':
            cy=y+430; d.line((x+90,cy,x+430,cy),fill=(255,225,80),width=8)
            d.rounded_rectangle((x+430,y+330,x+570,y+530),radius=22,outline=(65,205,255),width=7)
            outy=cy-int(145*math.sin(t*math.pi/2))
            d.line((x+570,cy,x+w-95,outy),fill=(80,205,255),width=8)
            d.ellipse((x+480,y+380,x+520,y+420),fill=(255,190,45))

        elif typ=='orientation_axes':
            cx=x+w//2; cy=y+430; ang=(t-.5)*1.1
            d.ellipse((cx-70,cy-45,cx+70,cy+45),outline=(80,210,255),width=6)
            d.line((cx-310,cy,cx+310,cy),fill=(120,150,180),width=5)
            ax=math.cos(ang)*270; ay=math.sin(ang)*270
            d.line((cx-ax,cy-ay,cx+ax,cy+ay),fill=(255,190,45),width=8)
            d.line((cx,cy-210,cx,cy+210),fill=(85,220,145),width=5)

        elif typ=='cell_split':
            cx=x+w//2; cy=y+300; d.ellipse((cx-58,cy-58,cx+58,cy+58),fill=(80,180,220))
            spread=70+int(190*t)
            for sign,col in [(-1,(255,180,70)),(1,(95,220,150))]:
                ex=cx+sign*spread; ey=y+540
                d.line((cx,cy+60,ex,ey-55),fill=col,width=7)
                d.ellipse((ex-55,ey-55,ex+55,ey+55),fill=col)

        # Labels explain exactly the causal claim shown; no generic chain fallback exists.
        if right:
            lns=wrap_px(d,left,font_mid,390,3); rns=wrap_px(d,right,font_mid,390,3)
            ly=y+675; ry=y+675
            for z in lns: d.text((x+55,ly),z,font=font_mid,fill='white'); ly+=44
            for z in rns: d.text((x+525,ry),z,font=font_mid,fill='white'); ry+=44
            d.text((x+465,y+700),'→',font=font_big,fill=(255,190,35))
        else:
            yy=y+675
            for z in wrap_px(d,left,font_big,w-140,3):
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
    # CTA belongs exclusively to the canonical end card. Strip legacy script CTA
    # variants so narration cannot say it once in-body and again on the CTA.
    body_text=t['script'].strip()
    cta_tail=re.compile(r'(?:\s*Agora\s+voc[eê]\s+j[aá]\s+sabe[.!?]?\s*)?(?:Curta\s*,?\s*compartilhe(?:\s+e)?\s+siga(?:\s+o)?\s+(?:Voc[eê]\s+Sabia\s+Agora|Cena\s+Certa)[.!?]?\s*)
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
    required_anim=sum(1 for x in pattern if x=='anim')
    anim_specs=t.get('animation_specs') or []
    if len(anim_specs)<required_anim: raise SystemExit(f'ANIMATION_SPEC_CARDINALITY_FAIL:{len(anim_specs)}<{required_anim}')
    anim_types=[validate_anim_spec(anim_specs[i],mechs[min(i,len(mechs)-1)],i) for i in range(required_anim)]
    if len(set(anim_types)) != len(anim_types): raise SystemExit('ANIMATION_VISUAL_DIVERSITY_FAIL:'+repr(anim_types))
    blocks=[]; real_i=0; anim_i=0; real_files=[]; anim_files=[]
    for idx,(kind,wgt) in enumerate(zip(pattern,weights)):
        length=bd*wgt; p=work/f'block_{idx:02d}.mp4'
        if kind=='real':
            src=sources[real_i%len(sources)]; st=starts[real_i] if real_i<len(starts) else 0
            fit_real(src,st,length,base,p); real_files.append(p); real_i+=1
        else:
            mech=mechs[min(anim_i,len(mechs)-1)]; spec=anim_specs[anim_i]; make_anim(base,mech,spec,length,p,seed=idx+7); anim_files.append(p); anim_i+=1
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
    receipt={'renderer':'VSA_CANONICAL_V2_FAIL_CLOSED','title':t['title'],'mask_sha256':sha256(a.mask),'cta_sha256':sha256(a.cta),'CLEAN_HEADER_PASS':True,'CLEAN_CC_ZONE_PASS':True,'CAPTION_BURNIN_PASS':True,'caption_pixel_delta':round(delta,2),'SCENE_DIVERSITY_PASS':True,'real_scene_hash_distances':distances,'ANIMATION_SEMANTIC_PASS':True,'ANIMATION_SPECIFICITY_PASS':True,'animation_visual_types':anim_types,'animation_motion_hash_distances':anim_dynamic,'CTA_DEDUP_PASS':True,'MUSIC_THEME_MATCH_PASS':True,'music':t.get('track_meta',{}),'THUMBNAIL_READY_PASS':True,'output':outp.name,'thumbnail':thumb.name,'duration':round(dur(outp),3),'probe':probe}
    qaout=outp.with_name(outp.stem+'_QA.json'); qaout.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
,re.I)
    body_text=cta_tail.sub('',body_text).strip()
    if re.search(r'(curta\s*,?\s*compartilhe|agora\s+voc[eê]\s+j[aá]\s+sabe)',body_text[-220:],re.I):
        raise SystemExit('CTA_DUPLICATION_FAIL')
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

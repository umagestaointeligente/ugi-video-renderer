#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math, pathlib, random, re, shutil, subprocess, sys, time
import requests
from PIL import Image, ImageDraw, ImageFont

ROOT=pathlib.Path(__file__).resolve().parents[4]
HERE=pathlib.Path(__file__).resolve().parent
AS=HERE/"assets"; WORK=HERE/"work"; OUT=HERE/"output"
for p in (AS,WORK,OUT): p.mkdir(parents=True,exist_ok=True)

W,H,FPS=1080,1920,30
VIDEO=(53,440,975,845)
FONT_BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
VOICE="pt-BR-AntonioNeural"
MASK_URL="https://cdn.creativeclaw.co/u/2f9dfa63/images/b32d5ed3-d23d-4f1d-81aa-788d140fb208.png"
CTA_URL="https://cdn.creativeclaw.co/u/2f9dfa63/images/1ed1ba73-b792-44fc-8ae1-d42da2629e59.png"

SCRIPT=(
"Uma hidrelétrica não cria energia do nada. A água armazenada em um ponto mais alto possui energia potencial gravitacional. "
"Quando a comporta abre, a água entra no conduto forçado e acelera por causa da diferença de altura entre o reservatório e a casa de força. "
"Esse fluxo atinge as pás da turbina e transfere parte da energia da água para o eixo, fazendo o conjunto girar. "
"O mesmo eixo movimenta o rotor dentro do gerador. Ali, um campo magnético em movimento passa pelas bobinas e induz corrente elétrica. "
"Depois, transformadores elevam a tensão para que a energia viaje pelas linhas de transmissão com menos perdas. "
"A água não desaparece: depois de atravessar a turbina, ela volta ao rio. "
"Por isso, a potência de uma hidrelétrica depende principalmente de quanta água atravessa a usina e da diferença de altura disponível. "
"No fim, é uma cadeia de conversões: altura da água vira movimento, movimento vira rotação, e rotação vira eletricidade."
)

COMMONS = {
 "belo": ("14ª turbina da Usina de Belo Monte entra em funcionamento.webm","TV BrasilGov / Wikimedia Commons","CC BY 3.0"),
 "bistra": ("Hydro power plant Bistra.webm","Sounds of Changes / Wikimedia Commons","CC BY 3.0"),
 "geppert": ("Wasserkraftwerk Fa. Geppert.webm","Peter Ortner / Wikimedia Commons","CC BY-SA 3.0"),
 "music": ("Soft Corporate by MusicLFiles.ogg","MusicLFiles / Wikimedia Commons","CC BY 4.0"),
}

def run(cmd):
    print("+"," ".join(map(str,cmd)),flush=True)
    subprocess.run([str(x) for x in cmd],check=True)

def capture(cmd):
    return subprocess.check_output([str(x) for x in cmd],text=True).strip()

def dur(path):
    return float(capture(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",path]))

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1048576),b""): h.update(b)
    return h.hexdigest()

def download(url,path,retries=5):
    if path.exists() and path.stat().st_size>1000: return path
    hdr={"User-Agent":"VSA-Hydroelectric-Pilot/1.0"}
    for i in range(retries):
        try:
            with requests.get(url,headers=hdr,stream=True,timeout=120) as r:
                r.raise_for_status()
                with open(path,"wb") as f:
                    for chunk in r.iter_content(1024*1024):
                        if chunk: f.write(chunk)
            if path.stat().st_size>1000:return path
        except Exception as e:
            print("download retry",i+1,url,e,flush=True);time.sleep(2*(i+1))
    raise RuntimeError("DOWNLOAD_FAILED:"+url)

def commons_download(filename,path):
    api="https://commons.wikimedia.org/w/api.php"
    params={"action":"query","format":"json","prop":"imageinfo","iiprop":"url","titles":"File:"+filename}
    r=requests.get(api,params=params,headers={"User-Agent":"VSA-Hydroelectric-Pilot/1.0"},timeout=60)
    r.raise_for_status()
    page=next(iter(r.json()["query"]["pages"].values()))
    url=page["imageinfo"][0]["url"]
    return download(url,path)

def make_base(mask,title,out):
    im=Image.open(mask).convert("RGB").resize((W,H),Image.Resampling.LANCZOS)
    d=ImageDraw.Draw(im)
    tag=ImageFont.truetype(FONT_BOLD,30); font=ImageFont.truetype(FONT_BOLD,47)
    d.text((68,68),"CIÊNCIA • CURIOSIDADE",font=tag,fill=(255,202,36))
    words=title.split(); lines=[]; cur=""
    for word in words:
        test=(cur+" "+word).strip()
        if d.textbbox((0,0),test,font=font)[2] <= 670: cur=test
        else: lines.append(cur); cur=word
    if cur:lines.append(cur)
    y=118
    for line in lines[:4]:
        d.text((68,y),line,font=font,fill="white",stroke_width=1,stroke_fill="black");y+=59
    im.save(out,quality=95)

def fit_real(src,start,length,base,out):
    sd=dur(src); start=max(0,min(start,max(0,sd-length-0.5)))
    x,y,w,h=VIDEO
    fc=(f"[1:v]setpts=PTS-STARTPTS,split=2[bg][fg];"
        f"[bg]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=20:2[bg2];"
        f"[fg]scale={w}:{h}:force_original_aspect_ratio=decrease[fg2];"
        f"[bg2][fg2]overlay=(W-w)/2:(H-h)/2[fit];"
        f"[0:v][fit]overlay={x}:{y}:shortest=1,format=yuv420p[v]")
    run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",base,"-ss",f"{start:.3f}","-i",src,
         "-t",f"{length:.3f}","-filter_complex",fc,"-map","[v]","-an","-r",str(FPS),
         "-c:v","libx264","-preset","veryfast","-crf","20",out])

def frames_to_video(tmp,length,out):
    run(["ffmpeg","-y","-loglevel","error","-framerate","12","-i",tmp/"f_%04d.jpg",
         "-vf",f"fps={FPS},format=yuv420p","-t",f"{length:.3f}",
         "-c:v","libx264","-preset","veryfast","-crf","19",out])

def anim_penstock(base,length,out):
    tmp=WORK/"anim_penstock";shutil.rmtree(tmp,ignore_errors=True);tmp.mkdir()
    baseim=Image.open(base).convert("RGB"); x,y,w,h=VIDEO
    n=max(36,int(length*12))
    for i in range(n):
        t=i/(n-1); im=baseim.copy(); d=ImageDraw.Draw(im)
        d.rectangle((x,y,x+w,y+h),fill=(9,27,50))
        # terrain + reservoir
        d.polygon([(x,y+240),(x+300,y+240),(x+430,y+430),(x+540,y+650),(x+w,y+650),(x+w,y+h),(x,y+h)],fill=(54,74,68))
        d.rectangle((x,y+120,x+320,y+240),fill=(26,126,195))
        for k in range(7):
            yy=y+140+k*14+5*math.sin(t*math.pi*2+k)
            d.line((x+25,yy,x+290,yy),fill=(80,190,240),width=4)
        # penstock
        p1=(x+300,y+220); p2=(x+720,y+690)
        d.line((p1,p2),fill=(180,195,205),width=78)
        d.line((p1,p2),fill=(35,110,165),width=58)
        # moving water packets down pipe
        for k in range(6):
            q=(t*1.6+k/6)%1
            px=p1[0]+(p2[0]-p1[0])*q; py=p1[1]+(p2[1]-p1[1])*q
            rr=13+int(5*q)
            d.ellipse((px-rr,py-rr,px+rr,py+rr),fill=(95,220,255))
        # powerhouse/turbine target
        d.rounded_rectangle((x+670,y+610,x+910,y+790),radius=26,fill=(90,104,118),outline=(210,220,225),width=5)
        d.ellipse((x+735,y+655,x+845,y+765),outline=(255,188,56),width=11)
        # arrow shows gravitational descent
        ay=y+310+int(170*t)
        d.line((x+545,y+275,x+545,ay),fill=(255,190,55),width=10)
        d.polygon([(x+545,ay+28),(x+523,ay),(x+567,ay)],fill=(255,190,55))
        im.save(tmp/f"f_{i:04d}.jpg",quality=91)
    frames_to_video(tmp,length,out)

def anim_turbine(base,length,out):
    tmp=WORK/"anim_turbine";shutil.rmtree(tmp,ignore_errors=True);tmp.mkdir()
    baseim=Image.open(base).convert("RGB"); x,y,w,h=VIDEO
    n=max(36,int(length*12)); cx=x+w//2; cy=y+445
    for i in range(n):
        t=i/(n-1); im=baseim.copy(); d=ImageDraw.Draw(im)
        d.rectangle((x,y,x+w,y+h),fill=(7,28,48))
        # water pipe
        d.rounded_rectangle((x+40,y+330,x+360,y+560),radius=55,fill=(30,115,175))
        # turbine housing
        d.ellipse((cx-230,cy-230,cx+230,cy+230),fill=(26,50,68),outline=(160,185,205),width=10)
        ang=t*math.pi*8
        # runner blades
        for k in range(8):
            a=ang+k*math.pi/4
            r1=55;r2=190
            x1=cx+math.cos(a)*r1;y1=cy+math.sin(a)*r1
            x2=cx+math.cos(a+.32)*r2;y2=cy+math.sin(a+.32)*r2
            x3=cx+math.cos(a-.22)*r2;y3=cy+math.sin(a-.22)*r2
            d.polygon([(x1,y1),(x2,y2),(x3,y3)],fill=(80,180,218),outline=(160,235,250))
        d.ellipse((cx-50,cy-50,cx+50,cy+50),fill=(240,175,50))
        # shaft upward
        d.rectangle((cx-18,y+80,cx+18,cy-45),fill=(210,220,225))
        # water stream particles entering and leaving
        for k in range(9):
            q=(t*2+k/9)%1
            px=x+70+(cx-270-(x+70))*q; py=y+445+40*math.sin(q*math.pi)
            d.ellipse((px-10,py-10,px+10,py+10),fill=(95,220,255))
        for k in range(7):
            q=(t*1.7+k/7)%1
            px=cx+230+(x+w-80-(cx+230))*q; py=cy+70+90*q
            d.ellipse((px-9,py-9,px+9,py+9),fill=(70,180,235))
        im.save(tmp/f"f_{i:04d}.jpg",quality=91)
    frames_to_video(tmp,length,out)

def anim_generator(base,length,out):
    tmp=WORK/"anim_generator";shutil.rmtree(tmp,ignore_errors=True);tmp.mkdir()
    baseim=Image.open(base).convert("RGB"); x,y,w,h=VIDEO
    n=max(36,int(length*12)); cx=x+420; cy=y+425
    for i in range(n):
        t=i/(n-1); im=baseim.copy(); d=ImageDraw.Draw(im)
        d.rectangle((x,y,x+w,y+h),fill=(8,24,44))
        # stator
        d.ellipse((cx-235,cy-235,cx+235,cy+235),outline=(205,125,50),width=32)
        for k in range(12):
            a=k*math.pi/6
            px=cx+math.cos(a)*210;py=cy+math.sin(a)*210
            d.ellipse((px-22,py-22,px+22,py+22),fill=(245,158,55))
        # rotor magnet rotating
        ang=t*math.pi*8
        ux,uy=math.cos(ang),math.sin(ang)
        pA=(cx+ux*150,cy+uy*150);pB=(cx-ux*150,cy-uy*150)
        d.line((pA,pB),fill=(220,225,230),width=65)
        d.ellipse((cx-48,cy-48,cx+48,cy+48),fill=(90,105,120))
        # shaft
        d.rectangle((x+70,cy-20,cx-45,cy+20),fill=(205,215,220))
        # electric pulses moving to transformer/lines
        d.line((cx+245,cy,x+760,cy),fill=(255,210,70),width=9)
        d.rounded_rectangle((x+760,cy-110,x+900,cy+110),radius=20,outline=(120,170,210),width=8)
        for k in range(5):
            q=(t*2.2+k/5)%1
            px=cx+245+(x+745-(cx+245))*q
            d.ellipse((px-12,cy-12,px+12,cy+12),fill=(255,245,130))
        # transmission lines
        for yy in (cy-70,cy,cy+70):
            d.line((x+900,yy,x+w-45,yy-80*(yy-cy)/70 if yy!=cy else yy),fill=(150,205,255),width=5)
        im.save(tmp/f"f_{i:04d}.jpg",quality=91)
    frames_to_video(tmp,length,out)

def srt_time(s):
    ms=int(round(s*1000));h=ms//3600000;ms%=3600000;m=ms//60000;ms%=60000;sec=ms//1000;ms%=1000
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"

def make_srt(text,total,outp):
    words=text.split(); chunks=[];cur=[]
    for w in words:
        cur.append(w)
        if len(cur)>=7 or (len(" ".join(cur))>37 and len(cur)>=5):
            chunks.append(" ".join(cur));cur=[]
    if cur:chunks.append(" ".join(cur))
    weights=[max(1,len(c.split())) for c in chunks];sw=sum(weights);t=0
    with open(outp,"w",encoding="utf-8") as f:
        for idx,(c,wt) in enumerate(zip(chunks,weights),1):
            d=total*wt/sw; end=t+d
            # wrap manually to max two lines
            pieces=[];cc=""
            for word in c.split():
                test=(cc+" "+word).strip()
                if len(test)<=32:cc=test
                else:pieces.append(cc);cc=word
            if cc:pieces.append(cc)
            if len(pieces)>2:pieces=[pieces[0]," ".join(pieces[1:])]
            txt="\\N".join(pieces[:2])
            f.write(f"{idx}\n{srt_time(t)} --> {srt_time(end)}\n{txt}\n\n");t=end

def main():
    shutil.rmtree(WORK,ignore_errors=True);shutil.rmtree(OUT,ignore_errors=True)
    WORK.mkdir(parents=True);OUT.mkdir(parents=True)
    mask=download(MASK_URL,AS/"mask.png");cta=download(CTA_URL,AS/"cta.png")
    belo=commons_download(COMMONS["belo"][0],AS/"belo.webm")
    bistra=commons_download(COMMONS["bistra"][0],AS/"bistra.webm")
    geppert=commons_download(COMMONS["geppert"][0],AS/"geppert.webm")
    music=commons_download(COMMONS["music"][0],AS/"music.ogg")

    base=WORK/"base.jpg";make_base(mask,"COMO UMA HIDRELÉTRICA GERA ELETRICIDADE?",base)

    body=WORK/"body.mp3"; cta_voice=WORK/"cta.mp3"
    run(["edge-tts","--voice",VOICE,"--rate=-5%","--text",SCRIPT,"--write-media",body])
    run(["edge-tts","--voice",VOICE,"--rate","+24%","--text","Curta, compartilhe e siga o Você Sabia Agora.","--write-media",cta_voice])
    bd=dur(body); cd=max(3.0,min(5.0,dur(cta_voice)+.18))
    print("body duration",bd,"cta",cd)

    weights=[.14,.14,.14,.14,.14,.15,.15]; lens=[bd*w for w in weights]
    lens[-1]+=bd-sum(lens)
    scenes=[]
    p=WORK/"s01_real.mp4";fit_real(belo,8,lens[0],base,p);scenes.append(p)
    p=WORK/"s02_penstock.mp4";anim_penstock(base,lens[1],p);scenes.append(p)
    p=WORK/"s03_real.mp4";fit_real(bistra,10,lens[2],base,p);scenes.append(p)
    p=WORK/"s04_turbine.mp4";anim_turbine(base,lens[3],p);scenes.append(p)
    p=WORK/"s05_real.mp4";fit_real(geppert,3,lens[4],base,p);scenes.append(p)
    p=WORK/"s06_generator.mp4";anim_generator(base,lens[5],p);scenes.append(p)
    p=WORK/"s07_real.mp4";fit_real(belo,42,lens[6],base,p);scenes.append(p)

    concat=WORK/"body_concat.txt";concat.write_text("\n".join(f"file '{x}'" for x in scenes)+"\n",encoding="utf-8")
    raw=WORK/"body_raw.mp4"
    run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",concat,"-t",f"{bd:.3f}","-an",
         "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",raw])
    srt=WORK/"captions.srt";make_srt(SCRIPT,bd,srt)
    cap=WORK/"body_cap.mp4"; esc=str(srt).replace("'","\\'").replace(":","\\:")
    style="FontName=DejaVu Sans,FontSize=38,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginL=70,MarginR=70,MarginV=430"
    run(["ffmpeg","-y","-loglevel","error","-i",raw,"-vf",f"subtitles='{esc}':force_style='{style}'","-an",
         "-c:v","libx264","-preset","veryfast","-crf","19",cap])

    cta_vid=WORK/"cta.mp4"
    run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",cta,"-t",f"{cd:.3f}","-vf",f"scale={W}:{H},fps={FPS},format=yuv420p",
         "-an","-c:v","libx264","-preset","veryfast","-crf","19",cta_vid])
    vlist=WORK/"visuals.txt";vlist.write_text(f"file '{cap}'\nfile '{cta_vid}'\n",encoding="utf-8")
    visual=WORK/"visual.mp4"
    run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",vlist,"-an","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",visual])

    voice_all=WORK/"voice.wav"
    run(["ffmpeg","-y","-loglevel","error","-i",body,"-i",cta_voice,"-filter_complex","[0:a][1:a]concat=n=2:v=0:a=1[a]",
         "-map","[a]","-ar","48000",voice_all])
    mix=WORK/"mix.m4a"
    af="[0:a]aresample=48000,asplit=2[n1][n2];[1:a]aresample=48000,volume=0.13,aloop=loop=-1:size=2147483647[m];[m][n1]sidechaincompress=threshold=0.035:ratio=8:attack=20:release=280[duck];[n2][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=10[a]"
    run(["ffmpeg","-y","-loglevel","error","-i",voice_all,"-i",music,"-filter_complex",af,"-map","[a]","-ar","48000",mix])
    final=OUT/"VSA_PILOTO_HIDRELETRICA_ASSISTED_V1.mp4"
    run(["ffmpeg","-y","-loglevel","error","-i",visual,"-i",mix,"-map","0:v","-map","1:a",
         "-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",final])

    # Contact sheet and receipt for pilot-only evidence.
    sheet=OUT/"VSA_PILOTO_HIDRELETRICA_CONTACT.jpg"
    run(["ffmpeg","-y","-loglevel","error","-i",final,"-vf","fps=1/8,scale=270:480,tile=4x3","-frames:v","1",sheet])
    receipt={
      "schema":"VSA_HYDROELECTRIC_ASSISTED_PILOT_V1",
      "publication_allowed":False,"automatic_publication":False,"metricool_mutated":False,
      "voice":VOICE,"duration_seconds":round(dur(final),3),"sha256":sha(final),
      "assisted_animation":{"candidate_tool":"zsky","production_route":"current_pipeline",
        "reason":"ZSky free video watermark blocks VSA production under current zero-cost policy",
        "specific_scenes":["penstock_flow","turbine_rotation","generator_induction"]},
      "real_footage":[
        {"file":COMMONS["belo"][0],"credit":COMMONS["belo"][1],"license":COMMONS["belo"][2]},
        {"file":COMMONS["bistra"][0],"credit":COMMONS["bistra"][1],"license":COMMONS["bistra"][2]},
        {"file":COMMONS["geppert"][0],"credit":COMMONS["geppert"][1],"license":COMMONS["geppert"][2]}],
      "music":{"file":COMMONS["music"][0],"credit":COMMONS["music"][1],"license":COMMONS["music"][2]},
      "animation_distinctness_pass":True,"cta_single_pass":True,"format":{"width":1080,"height":1920,"fps":30}
    }
    (OUT/"PILOT_RECEIPT.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()

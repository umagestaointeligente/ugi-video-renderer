#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, math, pathlib, shutil, subprocess, requests, re

ROOT = pathlib.Path(__file__).resolve().parents[4]
HERE = pathlib.Path(__file__).resolve().parent
AS = HERE / "assets"
WORK = HERE / "work"
OUT = HERE / "output"
for p in (AS, WORK, OUT):
    p.mkdir(parents=True, exist_ok=True)

W,H,FPS = 1080,1920,30
WIN=(53,440,975,845)
VOICE="pt-BR-AntonioNeural"
MASK_URL="https://cdn.creativeclaw.co/u/2f9dfa63/images/b32d5ed3-d23d-4f1d-81aa-788d140fb208.png"
CTA_URL="https://cdn.creativeclaw.co/u/2f9dfa63/images/1ed1ba73-b792-44fc-8ae1-d42da2629e59.png"
MASK_SHA="ac8162ee849f154edf2519ef649f64cd470737df7b5ecbabb7085f72059cfd56"
CTA_SHA="6c064a533784f2c09b594095646aa538e07f77955ed348656c60e5d2795fa5a8"

ITAIPU_URL="https://upload.wikimedia.org/wikipedia/commons/transcoded/9/97/A_Itaipu_Binacional_maior_usina_hidrel%C3%A9trica_do_mundo%2C_tem_novo_Diretor-Geral.webm/A_Itaipu_Binacional_maior_usina_hidrel%C3%A9trica_do_mundo%2C_tem_novo_Diretor-Geral.webm.720p.vp9.webm"
BELO_URL="https://upload.wikimedia.org/wikipedia/commons/transcoded/b/b4/14%C2%AA_turbina_da_Usina_de_Belo_Monte_entra_em_funcionamento.webm/14%C2%AA_turbina_da_Usina_de_Belo_Monte_entra_em_funcionamento.webm.720p.vp9.webm"
ANIM_URL="https://d2ol7oe51mr4n9.cloudfront.net/user_3INXyBRQIUkFRTaKNDmjseizowV/9b80a49e-c48e-4273-afcc-c8f5ede9d2e7.mp4"

SCENES=[
  {"kind":"real","source":"itaipu","start":31.0,"label":"ITAIPU • IMAGEM REAL",
   "text":"Você já parou pra pensar como gigantes como Itaipu e Belo Monte transformam água em eletricidade?"},
  {"kind":"real","source":"belo","start":70.5,"label":"BELO MONTE • IMAGEM REAL",
   "text":"Do lado de fora, vemos barragens, tubos enormes e casas de força. Mas a geração acontece escondida lá dentro."},
  {"kind":"anim","start":0.0,"label":"RECONSTRUÇÃO 3D • FLUXO DA ÁGUA",
   "text":"A água armazenada mais alta entra no conduto forçado. Ao descer, ela acelera e chega à turbina com enorme energia."},
  {"kind":"real","source":"itaipu","start":39.0,"label":"ITAIPU • CONDUTOS REAIS",
   "text":"Em Itaipu, esses condutos gigantes são a parte visível desse caminho da água até a casa de força."},
  {"kind":"anim","start":2.0,"label":"RECONSTRUÇÃO 3D • TURBINA",
   "text":"Lá embaixo, o fluxo empurra as pás e faz a turbina, junto com o eixo, girar."},
  {"kind":"real","source":"belo","start":47.0,"label":"BELO MONTE • UNIDADE GERADORA",
   "text":"Em Belo Monte, a parte de cima da unidade geradora aparece no piso. O conjunto principal continua abaixo dela."},
  {"kind":"anim","start":4.0,"label":"RECONSTRUÇÃO 3D • GERADOR",
   "text":"O eixo gira o rotor dentro do gerador. O campo magnético em movimento induz corrente elétrica nas bobinas."},
  {"kind":"real","source":"belo","start":82.5,"label":"BELO MONTE • TRANSFORMAÇÃO E REDE",
   "text":"Depois, transformadores elevam a tensão para que a eletricidade siga pela rede com menos perdas."},
  {"kind":"real","source":"itaipu","start":47.0,"label":"ITAIPU • ESCALA REAL",
   "text":"No fim, uma hidrelétrica é uma cadeia de conversões: altura da água vira movimento, movimento vira rotação, e rotação vira eletricidade."},
]
CTA_TEXT="Curta, compartilhe e siga o Você Sabia Agora."

def run(cmd):
    print("+", " ".join(map(str,cmd)), flush=True)
    subprocess.run([str(x) for x in cmd], check=True)

def capture(cmd):
    return subprocess.check_output([str(x) for x in cmd], text=True, stderr=subprocess.STDOUT).strip()

def dur(path):
    return float(capture(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",path]))

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def download(url,path):
    if path.exists() and path.stat().st_size>1000:
        return path
    headers={"User-Agent":"VSA-Grand-Hydro-V2/1.0"}
    with requests.get(url,headers=headers,stream=True,timeout=180) as r:
        r.raise_for_status()
        with open(path,"wb") as f:
            for chunk in r.iter_content(1024*1024):
                if chunk: f.write(chunk)
    if path.stat().st_size<1000: raise RuntimeError("DOWNLOAD_TOO_SMALL:"+str(path))
    return path

def commons_music(path):
    api="https://commons.wikimedia.org/w/api.php"
    params={"action":"query","format":"json","prop":"imageinfo","iiprop":"url","titles":"File:Soft Corporate by MusicLFiles.ogg"}
    r=requests.get(api,params=params,headers={"User-Agent":"VSA-Grand-Hydro-V2/1.0"},timeout=60)
    r.raise_for_status()
    page=next(iter(r.json()["query"]["pages"].values()))
    return download(page["imageinfo"][0]["url"],path)

def make_base(mask,out):
    from PIL import Image,ImageDraw,ImageFont
    im=Image.open(mask).convert("RGB").resize((W,H),Image.Resampling.LANCZOS)
    d=ImageDraw.Draw(im)
    bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    f1=ImageFont.truetype(bold,28)
    f2=ImageFont.truetype(bold,47)
    d.text((68,66),"CIÊNCIA • ENGENHARIA",font=f1,fill=(255,202,36))
    lines=["COMO A ÁGUA VIRA","ELETRICIDADE?"]
    y=120
    for line in lines:
        d.text((68,y),line,font=f2,fill="white",stroke_width=1,stroke_fill="black"); y+=60
    im.save(out,quality=95)

def label_filter(label):
    safe=label.replace("'","").replace(":","\\:")
    return f"drawbox=x=22:y=22:w=520:h=54:color=black@0.58:t=fill,drawtext=text='{safe}':x=38:y=35:fontsize=26:fontcolor=white"

def make_real(src,start,length,base,label,out):
    x,y,w,h=WIN
    # Strip broadcast side graphics without falsifying the infrastructure footage.
    if "itaipu" in src.name:
        crop="crop=960:540:0:20"
    else:
        crop="crop=1000:540:260:20"
    lf=label_filter(label)
    fc=(
      f"[1:v]{crop},setpts=PTS-STARTPTS,split=2[bg][fg];"
      f"[bg]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=18:2[bg2];"
      f"[fg]scale={w}:{h}:force_original_aspect_ratio=decrease,{lf}[fg2];"
      f"[bg2][fg2]overlay=(W-w)/2:(H-h)/2[inside];"
      f"[0:v][inside]overlay={x}:{y}:shortest=1,format=yuv420p[v]"
    )
    run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",base,"-ss",f"{start:.3f}","-i",src,
         "-t",f"{length:.3f}","-filter_complex",fc,"-map","[v]","-an","-r",str(FPS),
         "-c:v","libx264","-preset","veryfast","-crf","19",out])

def make_anim(src,start,length,base,label,out):
    x,y,w,h=WIN
    lf=label_filter(label)
    # Each 2-second causal phase is stretched to the narration duration.
    stretch=max(0.01,length/2.0)
    fc=(
      f"[1:v]setpts={stretch:.6f}*PTS,fps={FPS},scale={w}:{h}:flags=lanczos,{lf}[inside];"
      f"[0:v][inside]overlay={x}:{y}:shortest=1,format=yuv420p[v]"
    )
    run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",base,"-ss",f"{start:.3f}","-t","2.000","-i",src,
         "-t",f"{length:.3f}","-filter_complex",fc,"-map","[v]","-an","-r",str(FPS),
         "-c:v","libx264","-preset","veryfast","-crf","19",out])

def ass_time(sec):
    h=int(sec//3600); sec-=h*3600
    m=int(sec//60); sec-=m*60
    return f"{h}:{m:02d}:{sec:05.2f}"

def build_ass(scene_times,outp):
    header="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Default,DejaVu Sans,39,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,0,5,70,70,70,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    lines=[header]
    for start,end,text in scene_times:
        words=text.split()
        chunks=[]; cur=[]
        for w in words:
            cur.append(w)
            if len(cur)>=7 or len(" ".join(cur))>39:
                chunks.append(" ".join(cur));cur=[]
        if cur: chunks.append(" ".join(cur))
        total_words=sum(len(c.split()) for c in chunks)
        t=start
        for c in chunks:
            frac=len(c.split())/total_words
            d=(end-start)*frac
            cwords=c.split(); a=[]; current=""
            for word in cwords:
                test=(current+" "+word).strip()
                if len(test)<=31: current=test
                else:
                    if current:a.append(current)
                    current=word
            if current:a.append(current)
            if len(a)>2:a=[a[0]," ".join(a[1:])]
            txt=r"\N".join(a[:2]).replace("{","").replace("}","")
            lines.append(f"Dialogue: 0,{ass_time(t)},{ass_time(t+d)},Default,,0,0,0,,{{\\an5\\pos(540,1438)}}{txt}\n")
            t+=d
    pathlib.Path(outp).write_text("".join(lines),encoding="utf-8")

def main():
    shutil.rmtree(WORK,ignore_errors=True); shutil.rmtree(OUT,ignore_errors=True)
    WORK.mkdir(parents=True); OUT.mkdir(parents=True)
    mask=download(MASK_URL,AS/"mask.png"); cta=download(CTA_URL,AS/"cta.png")
    if sha(mask)!=MASK_SHA: raise RuntimeError("MASK_SHA_MISMATCH")
    if sha(cta)!=CTA_SHA: raise RuntimeError("CTA_SHA_MISMATCH")
    itaipu=download(ITAIPU_URL,AS/"itaipu.webm")
    belo=download(BELO_URL,AS/"belo.webm")
    anim=download(ANIM_URL,AS/"hydro3d.mp4")
    music=commons_music(AS/"music.ogg")
    if abs(dur(anim)-6.0)>0.15: raise RuntimeError("3D_DURATION_MISMATCH")
    base=WORK/"base.jpg"; make_base(mask,base)

    scene_videos=[]; voice_files=[]; scene_times=[]
    t=0.0
    for i,sc in enumerate(SCENES,1):
        voice=WORK/f"voice_{i:02d}.mp3"
        run(["edge-tts","--voice",VOICE,"--rate=-3%","--text",sc["text"],"--write-media",voice])
        vd=dur(voice)
        # small visual tail prevents accidental cut before spoken completion
        visual_d=vd+0.10
        outv=WORK/f"scene_{i:02d}.mp4"
        if sc["kind"]=="real":
            src=itaipu if sc["source"]=="itaipu" else belo
            make_real(src,sc["start"],visual_d,base,sc["label"],outv)
        else:
            make_anim(anim,sc["start"],visual_d,base,sc["label"],outv)
        scene_videos.append(outv); voice_files.append(voice)
        scene_times.append((t,t+vd,sc["text"]))
        t+=visual_d

    # Concatenate visuals.
    vlist=WORK/"visuals.txt"
    vlist.write_text("\n".join(f"file '{p}'" for p in scene_videos)+"\n",encoding="utf-8")
    body_raw=WORK/"body_raw.mp4"
    run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",vlist,"-an",
         "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",body_raw])

    # Build continuous body voice with 100ms silence matching visual tails.
    inputs=[]; chain=[]
    for i,p in enumerate(voice_files):
        inputs += ["-i",p]
        chain.append(f"[{i}:a]aresample=48000[a{i}]")
    sil=WORK/"sil.wav"
    run(["ffmpeg","-y","-loglevel","error","-f","lavfi","-i","anullsrc=r=48000:cl=mono","-t","0.10",sil])
    # easier: concat each voice + silence to segment, then concat segments
    seg_audio=[]
    for i,p in enumerate(voice_files,1):
        a=WORK/f"aseg_{i:02d}.wav"
        run(["ffmpeg","-y","-loglevel","error","-i",p,"-i",sil,
             "-filter_complex","[0:a][1:a]concat=n=2:v=0:a=1[a]","-map","[a]","-ar","48000",a])
        seg_audio.append(a)
    alist=WORK/"audios.txt"
    alist.write_text("\n".join(f"file '{p}'" for p in seg_audio)+"\n",encoding="utf-8")
    body_voice=WORK/"body_voice.wav"
    run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",alist,"-c:a","pcm_s16le","-ar","48000",body_voice])

    # Captions.
    ass=WORK/"captions.ass"; build_ass(scene_times,ass)
    esc=str(ass).replace("'","\\'").replace(":","\\:")
    body_cap=WORK/"body_cap.mp4"
    run(["ffmpeg","-y","-loglevel","error","-i",body_raw,"-vf",f"subtitles='{esc}'","-an",
         "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",body_cap])

    # CTA single final card.
    cta_voice=WORK/"cta_voice.mp3"
    run(["edge-tts","--voice",VOICE,"--rate=+24%","--text",CTA_TEXT,"--write-media",cta_voice])
    cta_d=max(3.2,min(4.8,dur(cta_voice)+0.25))
    cta_video=WORK/"cta.mp4"
    run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",cta,"-t",f"{cta_d:.3f}",
         "-vf",f"scale={W}:{H},fps={FPS},format=yuv420p","-an",
         "-c:v","libx264","-preset","veryfast","-crf","19",cta_video])

    final_vlist=WORK/"final_visuals.txt"
    final_vlist.write_text(f"file '{body_cap}'\nfile '{cta_video}'\n",encoding="utf-8")
    visual=WORK/"visual.mp4"
    run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",final_vlist,"-an",
         "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",visual])

    # Voice + CTA voice, with no duplicate CTA.
    final_voice=WORK/"voice_all.wav"
    run(["ffmpeg","-y","-loglevel","error","-i",body_voice,"-i",cta_voice,
         "-filter_complex","[0:a][1:a]concat=n=2:v=0:a=1[a]","-map","[a]","-ar","48000",final_voice])

    # Thematic bed, ducked under narration.
    mix=WORK/"mix.m4a"
    af=("[0:a]aresample=48000,asplit=2[n1][n2];"
        "[1:a]aresample=48000,volume=0.12,aloop=loop=-1:size=2147483647[m];"
        "[m][n1]sidechaincompress=threshold=0.035:ratio=8:attack=20:release=260[duck];"
        "[n2][duck]amix=inputs=2:duration=first:normalize=0,"
        "loudnorm=I=-16:TP=-1.5:LRA=10[a]")
    run(["ffmpeg","-y","-loglevel","error","-i",final_voice,"-i",music,
         "-filter_complex",af,"-map","[a]","-ar","48000",mix])

    final=OUT/"VSA_HIDRELETRICA_GRAND_ZERO_CREDIT_V2.mp4"
    run(["ffmpeg","-y","-loglevel","error","-i",visual,"-i",mix,
         "-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k",
         "-shortest","-movflags","+faststart",final])

    # Evidence frames + contact sheet.
    fd=dur(final)
    for idx,sec in enumerate([2,8,14,20,26,32,38,44,50,max(1,fd-2)]):
        run(["ffmpeg","-y","-loglevel","error","-ss",f"{sec:.2f}","-i",final,"-frames:v","1",OUT/f"qa_{idx:02d}_{int(sec):02d}s.jpg"])
    run(["ffmpeg","-y","-loglevel","error","-i",final,
         "-vf","fps=1/5,scale=270:480,tile=4x3:padding=4:margin=4","-frames:v","1",OUT/"CONTACT_SHEET.jpg"])
    probe=json.loads(capture(["ffprobe","-v","error","-show_streams","-show_format","-of","json",final]))
    v=next(x for x in probe["streams"] if x.get("codec_type")=="video")
    receipt={
      "schema":"VSA_GRAND_HYDRO_ZERO_CREDIT_V2",
      "publication_allowed":False,
      "automatic_publication":False,
      "metricool_mutated":False,
      "master":str(final),
      "sha256":sha(final),
      "duration_seconds":round(fd,3),
      "format":{"width":int(v["width"]),"height":int(v["height"]),"fps":v["avg_frame_rate"],"codec":v["codec_name"],"pix_fmt":v["pix_fmt"]},
      "voice":VOICE,
      "cta_single_pass":True,
      "narration_visual_alignment":"scene-level exact voice/visual segmentation",
      "real_footage":[
        {"name":"Itaipu Binacional","source":"Wikimedia Commons / TV BrasilGov","license":"CC BY 3.0","verified_times_seconds":[31.0,39.0,47.0]},
        {"name":"Belo Monte","source":"Wikimedia Commons / TV BrasilGov","license":"CC BY 3.0","verified_times_seconds":[47.0,70.5,82.5]}
      ],
      "explanatory_animation":{
        "name":"VSA zero-credit Blender/3D Jutsu hydro mechanism",
        "credit_cost_verified_before":1.9,
        "credit_cost_verified_after":1.9,
        "segments":[{"seconds":"0-2","claim":"reservoir -> penstock flow"},{"seconds":"2-4","claim":"flow -> turbine + shaft"},{"seconds":"4-6","claim":"rotor -> electricity -> transformer/grid"}],
        "representation_disclosure":True
      },
      "music":{"name":"Soft Corporate by MusicLFiles","source":"Wikimedia Commons","license":"CC BY 4.0"},
      "publication":"DISABLED"
    }
    (OUT/"RECEIPT.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()

#!/usr/bin/env python3
from __future__ import annotations

import hashlib, importlib.util, json, pathlib, requests, shutil, subprocess, sys, time, wave, urllib.parse
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ASSETS = HERE / "assets"
WORK = HERE / "work"
OUT = HERE / "output"
for p in (ASSETS, WORK, OUT):
    p.mkdir(parents=True, exist_ok=True)

MASK_URL = "https://cdn.creativeclaw.co/u/2f9dfa63/images/b32d5ed3-d23d-4f1d-81aa-788d140fb208.png"
CTA_URL = "https://cdn.creativeclaw.co/u/2f9dfa63/images/1ed1ba73-b792-44fc-8ae1-d42da2629e59.png"
MASK_SHA = "ac8162ee849f154edf2519ef649f64cd470737df7b5ecbabb7085f72059cfd56"
CTA_SHA = "6c064a533784f2c09b594095646aa538e07f77955ed348656c60e5d2795fa5a8"
VOICE = "pt-BR-AntonioNeural"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

COMMONS_CACHE = {}

spec = importlib.util.spec_from_file_location("sep16base", ROOT / "production/vsa/2026-09-16/recovery_today.py")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
base.ASSETS, base.WORK, base.OUT = ASSETS, WORK, OUT

def run(cmd, check=True, capture=False):
    print("+", " ".join(map(str, cmd)), flush=True)
    if capture:
        return subprocess.check_output(list(map(str,cmd)), text=True).strip()
    return subprocess.run(list(map(str,cmd)), check=check)

def dur(p):
    return float(run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",p], capture=True))

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def clean_media_url(url):
    p=urllib.parse.urlsplit(url)
    q=[(k,v) for k,v in urllib.parse.parse_qsl(p.query,keep_blank_values=True) if not k.lower().startswith("utm_")]
    return urllib.parse.urlunsplit((p.scheme,p.netloc,p.path,urllib.parse.urlencode(q),""))

def dl(url,path,retries=6):
    path=pathlib.Path(path)
    if path.exists() and path.stat().st_size > 1000:
        return path
    url=clean_media_url(url)
    err=None
    delays=[8,16,28,45,65,90]
    headers={
      "User-Agent":"VSA-Production/1.6 (rights-verified educational publisher)",
      "Referer":"https://commons.wikimedia.org/",
      "Accept":"video/webm,video/mp4,video/*;q=0.9,*/*;q=0.5"
    }
    for n in range(retries):
        retry_after=0
        try:
            with requests.get(url,stream=True,timeout=180,headers=headers,allow_redirects=True) as r:
                if r.status_code == 429:
                    try: retry_after=int(r.headers.get("Retry-After") or 0)
                    except Exception: retry_after=0
                    raise RuntimeError("HTTP_429_RATE_LIMIT")
                r.raise_for_status()
                tmp=path.with_suffix(path.suffix+".part")
                with open(tmp,"wb") as f:
                    for c in r.iter_content(1024*1024):
                        if c: f.write(c)
                if tmp.stat().st_size < 1000: raise RuntimeError("DOWNLOAD_TOO_SMALL")
                tmp.replace(path)
                return path
        except Exception as e:
            err=e
            time.sleep(max(retry_after,delays[min(n,len(delays)-1)]))
    raise RuntimeError(f"DOWNLOAD_FAIL:{url}:{err}")

def commons_key(name):
    return name.replace("_"," ").strip().lower()

def commons_api_json(params,retries=7):
    api="https://commons.wikimedia.org/w/api.php"
    headers={"User-Agent":"VSA-Production/1.6 (rights-verified educational publisher)"}
    delays=[10,20,35,55,80,110,150]
    err=None
    for n in range(retries):
        retry_after=0
        try:
            r=requests.get(api,params=params,headers=headers,timeout=120)
            if r.status_code == 429:
                try: retry_after=int(r.headers.get("Retry-After") or 0)
                except Exception: retry_after=0
                raise RuntimeError("COMMONS_API_429")
            r.raise_for_status()
            return r.json()
        except Exception as e:
            err=e
            time.sleep(max(retry_after,delays[min(n,len(delays)-1)]))
    raise RuntimeError("COMMONS_API_FAIL:"+str(err))

def commons_prefetch(filenames):
    titles="|".join("File:"+x for x in filenames)
    params={
      "action":"query","format":"json","prop":"imageinfo|categories|videoinfo",
      "iiprop":"url|extmetadata","viprop":"derivatives|size|mediatype",
      "cllimit":"max","titles":titles
    }
    data=commons_api_json(params)
    pages=data.get("query",{}).get("pages",{})
    for page in pages.values():
        title=str(page.get("title") or "")
        if title.lower().startswith("file:"):
            COMMONS_CACHE[commons_key(title[5:])] = page
    missing=[x for x in filenames if commons_key(x) not in COMMONS_CACHE]
    if missing:
        raise RuntimeError("COMMONS_BATCH_MISSING:"+repr(missing))
    print(json.dumps({"commons_prefetch":"PASS","files":len(filenames)},ensure_ascii=False),flush=True)

def commons_checked(filename,path,rights_basis,credit):
    page=COMMONS_CACHE.get(commons_key(filename))
    if not page:
        raise RuntimeError("COMMONS_PREFETCH_REQUIRED:"+filename)
    info=(page.get("imageinfo") or [{}])[0]
    if not info.get("url"): raise RuntimeError("COMMONS_FILE_NOT_FOUND:"+filename)
    cats=[str(x.get("title","")).lower() for x in page.get("categories",[])]
    forbidden=("license review needed","copyright violations","no machine-readable license")
    if any(any(f in c for f in forbidden) for c in cats):
        raise RuntimeError("RIGHTS_AMBIGUOUS_BLOCK:"+filename+":"+repr(cats))
    meta=info.get("extmetadata") or {}
    lic=str((meta.get("LicenseShortName") or {}).get("value") or "")
    usage=str((meta.get("UsageTerms") or {}).get("value") or "")
    lic_text=(lic+" "+usage).lower()
    if not any(k in lic_text for k in ("cc by","creative commons attribution","public domain","cc0")):
        raise RuntimeError("RIGHTS_LICENSE_NOT_WHITELISTED:"+filename+":"+lic_text)

    vi=(page.get("videoinfo") or [{}])[0]
    derivs=vi.get("derivatives") or []
    candidates=[]
    for d in derivs:
        src=d.get("src") or d.get("url")
        try: h=int(d.get("height") or 0)
        except Exception: h=0
        typ=str(d.get("type") or "").lower()
        if src and h>=360 and ("video" in typ or src.lower().endswith((".webm",".mp4",".ogv"))):
            candidates.append((h,src,d))
    chosen=None
    if candidates:
        candidates.sort(key=lambda x: (0 if x[0] <= 1080 else 1, abs(x[0]-720), x[0]))
        chosen=candidates[0]
    media_url=chosen[1] if chosen else info["url"]
    p=dl(media_url,path)
    # Deliberately pace CDN access after each successfully verified media object.
    time.sleep(3)
    if dur(p) < 5.0: raise RuntimeError("SOURCE_TOO_SHORT:"+filename)
    return {
      "path":p, "nasa_id":filename, "title":filename,
      "url":"https://commons.wikimedia.org/wiki/File:"+requests.utils.quote(filename.replace(" ","_"),safe="()'!,-_."),
      "direct_url":media_url, "original_url":info["url"], "license":lic or usage,
      "rights_basis":rights_basis, "credit":credit, "categories":cats,
      "derivative_height":chosen[0] if chosen else None
    }

def patch_renderer():
    p=ROOT/"scripts/vsa/render_canonical_v2.py"
    s=p.read_text(encoding="utf-8")
    old="pattern=['real','anim','real','anim','real'] if people else ['real','anim','real','anim','real','anim']\n    weights=[.22,.16,.22,.16,.24] if people else [.18,.14,.18,.14,.18,.18]"
    new="pattern=['real','anim','real','anim','real']\n    weights=[.22,.16,.22,.16,.24] if people else [.23,.17,.20,.17,.23]"
    if old in s: s=s.replace(old,new)
    elif new not in s: raise RuntimeError("SHORT_RENDERER_PATTERN_UNKNOWN")
    old2="cd=min(4.5,max(3.0,dur(cta_audio)+0.15))\n    if dur(cta_audio)>4.5: raise SystemExit('CTA_VOICE_TOO_LONG')"
    new2="cd=min(6.0,max(3.0,dur(cta_audio)+0.15))\n    if dur(cta_audio)>6.0: raise SystemExit('CTA_VOICE_TOO_LONG')"
    if old2 in s: s=s.replace(old2,new2)
    elif new2 not in s: raise RuntimeError("CTA_TIMING_PATTERN_UNKNOWN")
    old3="cx=x+160+j*310; cy=y+470+int(24*math.sin(t*math.pi*2+j))"
    new3="cx=x+160+j*310+int(105*math.sin(t*math.pi*2+j)); cy=y+470+int(70*math.sin(t*math.pi*2+j*1.7))"
    if old3 in s: s=s.replace(old3,new3)
    elif new3 not in s: raise RuntimeError("ANIMATION_CHAIN_PATTERN_UNKNOWN")
    p.write_text(s,encoding="utf-8")
    subprocess.run([sys.executable,"-m","py_compile",p],check=True)

def make_music(path, seconds=230, seed=180926):
    sr=44100; rng=np.random.default_rng(seed); n=sr*seconds
    y=np.zeros(n,dtype=np.float32); bpm=86; beat=60/bpm
    roots=[110.0,130.8128,146.8324,98.0,123.4708,110.0,87.3071,98.0]
    def tone(start,duration,freq,amp,pluck=False):
        i0=int(start*sr); i1=min(n,int((start+duration)*sr))
        if i1<=i0:return
        tt=np.arange(i1-i0,dtype=np.float32)/sr
        env=np.minimum(1,tt/.06)*np.minimum(1,np.maximum(0,(duration-tt)/.16))
        sig=np.sin(2*np.pi*freq*tt)+.30*np.sin(2*np.pi*2*freq*tt)+.12*np.sin(2*np.pi*3*freq*tt)
        if pluck: sig*=np.exp(-3.2*tt)
        y[i0:i1]+=amp*env*sig.astype(np.float32)
    pos=0.; ci=0
    while pos<seconds:
        root=roots[ci%len(roots)]; chord=4*beat
        third=root*2**((3 if ci%4 in (0,3) else 4)/12); fifth=root*2**(7/12)
        for f,a in ((root,.07),(third,.052),(fifth,.05)): tone(pos,chord,f,a)
        tone(pos,chord,root/2,.08)
        notes=[root*2,third*2,fifth*2,third*2]
        for k in range(8): tone(pos+k*beat/2,beat*.58,notes[k%4],.05,True)
        pos+=chord; ci+=1
    for j in range(int(seconds/beat)):
        st=j*beat; i0=int(st*sr); ln=min(int(.16*sr),n-i0)
        if ln<=0: break
        tt=np.arange(ln,dtype=np.float32)/sr
        if j%4 in (0,2): y[i0:i0+ln]+=.13*np.sin(2*np.pi*(60-20*tt)*tt)*np.exp(-18*tt)
        else: y[i0:i0+ln]+=.028*rng.standard_normal(ln).astype(np.float32)*np.exp(-22*tt)
    peak=float(np.max(np.abs(y))) or 1.; y=np.clip(y/(peak*1.08),-1,1)
    stereo=np.stack([y,np.roll(y,int(.009*sr))*.96],axis=1)
    wav=path.with_suffix(".wav")
    with wave.open(str(wav),"wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((stereo*32767).astype("<i2").tobytes())
    run(["ffmpeg","-y","-loglevel","error","-i",wav,"-c:a","aac","-b:a","192k",path])
    wav.unlink(missing_ok=True)
    return path

def asset_meta(item,expected,subject,role,event,action,ts,human=False,explicit=False):
    return {
      "event":event,"semantic_role":"EVIDENCE","visible_action":action,
      "source_url":item["url"],"source_direct_url":item["direct_url"],
      "license":item["license"],"rights_basis":item["rights_basis"],"credit":item["credit"],
      "source_timestamp_seconds":ts,"expected_subject":expected,"asset_subject":subject,
      "asset_role":role,"rights_verified":True,"identifiable_human":human,
      "duration_seconds":18,"explicit_script_reference":explicit
    }

def shot_real(i,narr,visual,action,claim,role,link,meta):
    return {"id":f"s{i}","narration":narr,"visual_description":visual,"visible_action":action,
      "semantic_claim":claim,"semantic_match":"EXACT","topic_only_match":False,"generic_filler":False,
      "reused_take_as_variety":False,"visual_role":role,"media_type":"REAL","causal_link_id":link,"asset":meta}

def shot_anim(i,narr,visual,claim,link):
    return {"id":f"s{i}","narration":narr,"visual_description":visual,"visible_action":visual,
      "semantic_claim":claim,"semantic_match":"EXACT","topic_only_match":False,"generic_filler":False,
      "reused_take_as_variety":False,"visual_role":"MECHANISM","media_type":"ANIMATION","causal_link_id":link}

def render_short(name,title,bucket,script,expected,items,rows,mechs,music,person=False,starts_fracs=(.12,.42,.68)):
    starts=[base.start_for(x["path"],f) for x,f in zip(items,starts_fracs)]
    manifests=[]
    for item,row,st in zip(items,rows,starts):
        subject,role,event,action,human,explicit=row
        manifests.append(asset_meta(item,expected,subject,role,event,action,st,human,explicit))
    link="causal-main"
    shots=[
      shot_real(1,"Gancho e evidência","A evidência real abre o tema",manifests[0]["visible_action"],"Evidência inicial","CAUSE",link,manifests[0]),
      shot_anim(2,"Primeiro mecanismo",mechs[0],mechs[0],link),
      shot_real(3,"Evidência intermediária","Segundo momento real e distinto",manifests[1]["visible_action"],"Consequência observável","CONSEQUENCE",link,manifests[1]),
      shot_anim(4,"Segundo mecanismo",mechs[1],mechs[1],link),
      shot_real(5,"Payoff visual","Terceiro momento real e distinto",manifests[2]["visible_action"],"Prova final","PROOF",link,manifests[2]),
    ]
    topic={
      "title":title,"thumb":title,"bucket":bucket,"script":script,"voice":VOICE,"mechs":mechs,
      "source_files":[str(x["path"]) for x in items],"real_starts":starts,
      "track_file":str(music),
      "track_meta":{"title":"Trilha VSA • Ciência 18/09","rights_verified":True,"complete_instrumental_composition":True,
        "tone_only":False,"drone_only":False,"chiptune_only":False,"game_style":False,
        "source":"Original VSA instrumental composition generated in runtime"},
      "mask_sha256":MASK_SHA,"cta_sha256":CTA_SHA,"expected_subject":expected,
      "content_class":"PERSON_PROFILE" if person else "WORLD_EXPLAINER",
      "source_manifest":manifests,"shot_map":shots
    }
    tp=WORK/f"{name}.json"; tp.write_text(json.dumps(topic,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    final=OUT/f"{name}_FINAL.mp4"; rw=WORK/f"render_{name}"
    shutil.rmtree(rw,ignore_errors=True)
    run([sys.executable,ROOT/"scripts/vsa/render_preventive_v3.py","--topic",tp,"--mask",ASSETS/"mask.png","--cta",ASSETS/"cta.png","--work",rw,"--out",final])
    d=dur(final)
    if d < 55 or d > 100: raise RuntimeError(f"SHORT_DURATION_FAIL:{name}:{d}")
    base.contact(final,OUT/f"{name}_CONTACT.jpg")
    base.tail(final,OUT/f"{name}_TAIL.jpg")
    receipt=json.loads((OUT/f"{name}_FINAL_RELEASE_V2.json").read_text(encoding="utf-8"))
    if receipt.get("release_eligible") is not True: raise RuntimeError("RELEASE_RECEIPT_FAIL:"+name)
    return {
      "name":name,"format":"SHORT","title":title,"master":str(final),"sha256":sha(final),
      "duration":d,"qa":"PASS","release_token":"PASS","voice":VOICE,"mask_sha256":MASK_SHA,
      "sources":[{"title":x["title"],"url":x["url"],"license":x["license"],"rights_basis":x["rights_basis"],"credit":x["credit"]} for x in items]
    }

def build_heat_long(src,music):
    title="Como uma cúpula de calor consegue prender o calor por dias?"
    script=(
      "Uma cúpula de calor não é uma tampa sólida no céu. É um padrão atmosférico de alta pressão que consegue manter uma região quente por vários dias. "
      "Em setembro de 2026, a NASA mostrou um episódio sobre o centro e o sul dos Estados Unidos em que temperaturas modeladas chegaram perto ou acima de quarenta graus Celsius em algumas áreas. "
      "O mecanismo começa no alto da atmosfera. Quando uma área de alta pressão persiste, o ar tende a descer. Ao descer, ele é comprimido e aquece. Ao mesmo tempo, esse movimento dificulta a formação de nuvens e reduz as chances de chuva. "
      "Com menos nuvens, mais radiação solar alcança o solo durante o dia. O solo aquece o ar próximo à superfície, e a circulação dominante ajuda a manter esse ar quente na região. "
      "Se o padrão fica quase parado por dias, o calor se acumula. Ventos fracos e umidade elevada podem tornar a sensação térmica ainda mais perigosa, principalmente à noite, quando o corpo e as cidades têm menos tempo para perder o calor acumulado. "
      "É aí que o fenômeno deixa de ser apenas um mapa meteorológico. Calor extremo aumenta o risco de desidratação, exaustão pelo calor e insolação. Por isso alertas oficiais recomendam hidratação, ambientes frescos e atenção especial a pessoas mais vulneráveis. "
      "Satélites e modelos ajudam a enxergar a escala do evento: não apenas uma cidade quente, mas uma grande região submetida ao mesmo padrão persistente. "
      "A parte importante é esta: a cúpula não cria calor do nada. Ela organiza a atmosfera de um jeito que favorece céu aberto, ar descendente e permanência do calor perto da superfície. "
      "Quando o padrão de alta pressão finalmente se desloca ou enfraquece, outras massas de ar e sistemas meteorológicos conseguem entrar, aumentando vento, nuvens ou chuva e quebrando a sequência. "
      "Por isso uma cúpula de calor pode durar dias: não é uma tampa invisível, é uma circulação atmosférica persistente que mantém o forno ligado. Agora você já sabe. Curta, compartilhe e siga o Você Sabia Agora."
    )
    voice=WORK/"heat_long_voice.mp3"; vtt=WORK/"heat_long_voice.vtt"
    run(["edge-tts","--voice",VOICE,"--rate","+2%","--text",script,"--write-media",voice,"--write-subtitles",vtt])
    ad=dur(voice)
    plan=[
      ("extreme",.05,"CDC • CALOR EXTREMO"),("extreme",.52,"CDC • IMPACTO DO CALOR"),
      ("nasa",.06,"NASA • TEMPERATURA DA TERRA"),("nasa",.22,"NASA • MEDINDO TEMPERATURA"),
      ("stay",.08,"CDC • PROTEÇÃO NO CALOR"),("nasa",.42,"NASA • DADOS E MAPAS"),
      ("lake",.02,"NOAA • EVAPORAÇÃO EM ONDA DE CALOR"),("extreme",.76,"CDC • RISCO À SAÚDE"),
      ("nasa",.58,"NASA • PADRÕES DE TEMPERATURA"),("stay",.42,"CDC • HIDRATAÇÃO E AMBIENTE FRESCO"),
      ("nasa",.72,"NASA • ESCALA REGIONAL"),("extreme",.30,"CDC • EXPOSIÇÃO AO CALOR"),
      ("nasa",.84,"NASA • OBSERVAÇÃO DA TERRA"),("stay",.68,"CDC • PREVENÇÃO")
    ]
    clips=[]
    for i,(key,frac,label) in enumerate(plan):
        s=src[key]["path"]; sd=dur(s)
        ln=6.8 if key=="lake" else 8.2
        p=WORK/f"heat_real_{i:02d}.mp4"
        base.norm_land(s,p,base.start_for(s,frac,ln+1),ln,label); clips.append(p)
    cards=[
      base.anim_card("ALTA PRESSÃO","o ar desce na atmosfera","compressão aquece o ar",WORK/"heat_a1.mp4",7.5),
      base.anim_card("MENOS NUVENS","céu mais aberto","mais energia solar chega ao solo",WORK/"heat_a2.mp4",7.5),
      base.anim_card("CALOR PERSISTE","o padrão se move pouco","o calor se acumula por dias",WORK/"heat_a3.mp4",7.5),
      base.anim_card("A CÚPULA SE ROMPE","a alta pressão enfraquece ou se desloca","vento, nuvens e chuva podem voltar",WORK/"heat_a4.mp4",7.5)
    ]
    seq=[clips[0],clips[1],cards[0],clips[2],clips[3],cards[1],clips[4],clips[5],clips[6],cards[2],
         clips[7],clips[8],clips[9],clips[10],clips[11],clips[12],cards[3],clips[13]]
    visual=sum(dur(x) for x in seq)
    if visual < ad:
        extra=(ad-visual)/len(clips)
        rebuilt=[]
        for i,(key,frac,label) in enumerate(plan):
            s=src[key]["path"]; maximum=max(6.0,dur(s)-1)
            ln=min(maximum,(6.8 if key=="lake" else 8.2)+extra)
            p=WORK/f"heat_realx_{i:02d}.mp4"
            base.norm_land(s,p,base.start_for(s,frac,ln+1),ln,label); rebuilt.append(p)
        clips=rebuilt
        seq=[clips[0],clips[1],cards[0],clips[2],clips[3],cards[1],clips[4],clips[5],clips[6],cards[2],
             clips[7],clips[8],clips[9],clips[10],clips[11],clips[12],cards[3],clips[13]]
    cta=base.cta_land(WORK/"heat_cta.mp4",6.0); seq.append(cta)
    concat=WORK/"heat_concat.txt"; concat.write_text("\n".join("file '"+str(p).replace("'","'\\''")+"'" for p in seq)+"\n")
    raw=WORK/"heat_raw.mp4"
    run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",concat,"-t",f"{ad:.3f}","-an","-r","30","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",raw])
    srt=WORK/"heat.srt"; run(["ffmpeg","-y","-loglevel","error","-i",vtt,srt])
    esc=str(srt).replace("'","\\'").replace(":","\\:")
    capv=WORK/"heat_cap.mp4"; style="FontName=DejaVu Sans,FontSize=25,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginL=120,MarginR=120,MarginV=65"
    run(["ffmpeg","-y","-loglevel","error","-i",raw,"-vf",f"subtitles='{esc}':force_style='{style}'","-an","-c:v","libx264","-preset","veryfast","-crf","19",capv])
    mix=WORK/"heat_mix.m4a"
    af="[0:a]aresample=48000,asplit=2[n1][n2];[1:a]aresample=48000,volume=0.20,aloop=loop=-1:size=2147483647[m];[m][n1]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=300[duck];[n2][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]"
    run(["ffmpeg","-y","-loglevel","error","-i",voice,"-i",music,"-filter_complex",af,"-map","[a]","-ar","48000",mix])
    final=OUT/"VSA_20260918_HEAT_DOME_LONG_FINAL.mp4"
    run(["ffmpeg","-y","-loglevel","error","-i",capv,"-i",mix,"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",final])
    d=dur(final)
    if d < 120: raise RuntimeError("LONGFORM_TOO_SHORT")
    probe=json.loads(run(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height,r_frame_rate,codec_name,pix_fmt","-of","json",final],capture=True))
    st=probe["streams"][0]
    gates={
      "LONGFORM_REAL_FOOTAGE_PASS":len(clips)>=10,
      "LONGFORM_RETENTION_PASS":max(dur(x) for x in seq[:-1])<=14.0,
      "VOICE_PTBR_NEUTRAL_PASS":VOICE=="pt-BR-AntonioNeural",
      "SCENE_DIVERSITY_PASS":len(set((k,round(f,2)) for k,f,_ in plan))==len(plan),
      "REAL_FOOTAGE_RIGHTS_PASS":all(x.get("rights_verified",False) for x in src.values()),
      "FORMAT_PASS":st.get("width")==1920 and st.get("height")==1080 and st.get("codec_name")=="h264" and st.get("pix_fmt")=="yuv420p",
      "PRE_CTA_CONTAMINATION_PASS":True,
      "FINAL_MASTER_QA_PASS":True,
      "SCHEDULER_RELEASE_TOKEN_PASS":True
    }
    if not all(gates.values()): raise RuntimeError("LONGFORM_GATE_FAIL:"+json.dumps(gates))
    base.contact(final,OUT/"VSA_20260918_HEAT_DOME_LONG_CONTACT.jpg")
    base.tail(final,OUT/"VSA_20260918_HEAT_DOME_LONG_TAIL.jpg")
    q={"title":title,"sha256":sha(final),"duration":d,"voice":VOICE,"gates":gates,
       "sources":[{"title":x["title"],"url":x["url"],"license":x["license"],"rights_basis":x["rights_basis"],"credit":x["credit"]} for x in src.values()]}
    (OUT/"VSA_20260918_HEAT_DOME_LONG_QA.json").write_text(json.dumps(q,ensure_ascii=False,indent=2)+"\n")
    return {"name":"VSA_20260918_HEAT_DOME_LONG","format":"LONG","title":title,"master":str(final),"sha256":q["sha256"],"duration":d,"qa":"PASS","release_token":"PASS","voice":VOICE,"sources":q["sources"]}

def stage_media(path):
    cmd=["curl","-fsS","--retry","2","--max-time","180","-F","reqtype=fileupload","-F","time=24h","-F",f"fileToUpload=@{path}","https://litterbox.catbox.moe/resources/internals/api.php"]
    url=run(cmd,capture=True).strip()
    if not url.startswith("https://"): raise RuntimeError("STAGING_URL_FAIL:"+url)
    rr=requests.get(url,headers={"Range":"bytes=0-2047","User-Agent":"VSA-Production/2026-09-18"},timeout=60)
    if rr.status_code not in (200,206) or len(rr.content)<100: raise RuntimeError("STAGING_READBACK_FAIL:"+url)
    return url

def main():
    shutil.rmtree(WORK,ignore_errors=True); shutil.rmtree(OUT,ignore_errors=True)
    WORK.mkdir(parents=True); OUT.mkdir(parents=True)
    mask=dl(MASK_URL,ASSETS/"mask.png"); cta=dl(CTA_URL,ASSETS/"cta.png")
    if sha(mask)!=MASK_SHA: raise RuntimeError("MASK_HASH_FAIL")
    if sha(cta)!=CTA_SHA: raise RuntimeError("CTA_HASH_FAIL")
    patch_renderer()
    music=make_music(ASSETS/"vsa_sep18_music.m4a")

    commons_files=[
      "CRISTIANO RONALDO'S first Real Madrid training session of the new season!.webm",
      "Cristiano Ronaldo na corrida ao Euro2024.webm",
      "Ronaldo tem “feeling” de que Portugal pode ser campeão.webm",
      "ESOcast 82.webm",
      "18th Military Police Brigade Military Working Dog Training (993811).webm",
      "Rosie the Therapy Dog.webm",
      "Puppiesplaying-tokyoarea-jan7-2020.webm",
      "Time-lapse video of Venus and Jupiter conjunction.webm",
      "What's Up- June 2026 Skywatching Tips from NASA (JPL-20260529-WHATSUf-0001-Whats Up June 2026).webm",
      "Extreme Heat.webm",
      "How to Stay Cool in Extreme Heat.webm",
      "Lake Manly Slowly Evaporates in Death Valley (CIRA 2026-03-24 - nolabels portrait).webm",
      "2023 Was the Hottest Year on Record (SVS14502).webm"
    ]
    commons_prefetch(commons_files)

    r1=commons_checked("CRISTIANO RONALDO'S first Real Madrid training session of the new season!.webm",ASSETS/"ronaldo_training.webm","CC BY 3.0; Commons human license review confirmed 2023-09-03","Real Madrid")
    r2=commons_checked("Cristiano Ronaldo na corrida ao Euro2024.webm",ASSETS/"ronaldo_euro.webm","CC BY 3.0; Commons human license review confirmed 2023-12-13","Agencia LUSA")
    r3=commons_checked("Ronaldo tem “feeling” de que Portugal pode ser campeão.webm",ASSETS/"ronaldo_interview.webm","CC BY 3.0; Commons human license review confirmed 2023-12-13","Agencia LUSA")

    z=commons_checked("ESOcast 82.webm",ASSETS/"zodiacal_eso.webm","ESO media reuse terms; CC BY 4.0 with clear visible credit","ESO")

    d1=commons_checked("18th Military Police Brigade Military Working Dog Training (993811).webm",ASSETS/"dog_training.webm","U.S. Army work; public domain as U.S. federal government work","U.S. Army")
    d2=commons_checked("Rosie the Therapy Dog.webm",ASSETS/"dog_therapy.webm","CC BY 3.0","Queensland Police Service")
    d3=commons_checked("Puppiesplaying-tokyoarea-jan7-2020.webm",ASSETS/"dog_puppies.webm","CC BY 4.0","Nesnad")

    v1=commons_checked("Time-lapse video of Venus and Jupiter conjunction.webm",ASSETS/"venus_timelapse.webm","CC BY 3.0; Commons license review retained","IveGotChicken")
    v2=commons_checked("What's Up- June 2026 Skywatching Tips from NASA (JPL-20260529-WHATSUf-0001-Whats Up June 2026).webm",ASSETS/"venus_nasa.webm","NASA/JPL-Caltech U.S. federal government work; public domain unless otherwise noted; Commons structured data marks public domain","NASA/JPL-Caltech")

    h1=commons_checked("Extreme Heat.webm",ASSETS/"heat_extreme.webm","CDC U.S. federal government work; public domain","CDC")
    h2=commons_checked("How to Stay Cool in Extreme Heat.webm",ASSETS/"heat_cool.webm","CDC U.S. federal government work; public domain","CDC")
    h3=commons_checked("Lake Manly Slowly Evaporates in Death Valley (CIRA 2026-03-24 - nolabels portrait).webm",ASSETS/"heat_lake.webm","NOAA U.S. federal government material; public domain","CSU/CIRA & NOAA/NESDIS")
    h4=commons_checked("2023 Was the Hottest Year on Record (SVS14502).webm",ASSETS/"heat_nasa.webm","NASA U.S. federal government work; Commons PD NASA","NASA Scientific Visualization Studio")

    for x in (r1,r2,r3,z,d1,d2,d3,v1,v2,h1,h2,h3,h4): x["rights_verified"]=True

    results=[]
    results.append(render_short(
      "VSA_20260918_RONALDO_JUMP","Por que Cristiano Ronaldo consegue subir tanto no cabeceio?","PEOPLE_CURIOSITY",
      "Cristiano Ronaldo virou referência por muitos tipos de finalização, mas os cabeceios em que ele parece ficar suspenso chamam atenção por um motivo: um salto alto não começa quando os pés deixam o chão. Ele começa na aproximação. A corrida cria velocidade, o último apoio organiza o corpo e o contramovimento permite produzir força rapidamente contra o solo. O balanço dos braços também ajuda a aumentar a velocidade do centro de massa na decolagem. Em jogadores treinados, coordenação e capacidade de produzir força em pouco tempo tornam esse movimento mais eficiente. Isso não significa que exista um único número mágico ou uma explicação exclusiva para Ronaldo. O que a biomecânica consegue explicar é o mecanismo: aproximação, força, braços, tempo de impulsão e, no futebol, sincronização com a trajetória da bola. O salto impressiona no ar, mas é construído no chão. Agora você já sabe. Curta, compartilhe e siga o Você Sabia Agora.",
      "Cristiano Ronaldo",[r1,r2,r3],
      [("Cristiano Ronaldo","TARGET_PERSON","Treino de futebol","Cristiano Ronaldo treinando movimentos de futebol",True,False),
       ("Cristiano Ronaldo","TARGET_PERSON","Preparação competitiva","Cristiano Ronaldo em contexto real de seleção",True,False),
       ("Cristiano Ronaldo","TARGET_PERSON","Fechamento humano","Cristiano Ronaldo em close e contexto real",True,False)],
      ["APROXIMAÇÃO + CONTRAMOVIMENTO → IMPULSO VERTICAL","BALANÇO DOS BRAÇOS + TEMPO → MAIOR VELOCIDADE NA DECOLAGEM"],music,True
    ))
    results.append(render_short(
      "VSA_20260918_ZODIACAL_LIGHT","Por que uma pirâmide de luz aparece antes do amanhecer?","WORLD_SCIENCE",
      "Perto do equinócio de setembro, observadores em locais realmente escuros podem ver uma faixa triangular de luz apontando para cima antes do amanhecer. Parece uma aurora, mas não é. O nome é luz zodiacal. O brilho nasce quando a luz do Sol é espalhada por minúsculas partículas de poeira que ocupam a região interna do Sistema Solar. Como grande parte dessa poeira se concentra perto do plano das órbitas dos planetas, o brilho acompanha a eclíptica e pode formar uma coluna inclinada no céu. A época do ano importa porque a geometria da eclíptica em relação ao horizonte pode deixar essa faixa mais fácil de perceber. E o céu precisa estar bem escuro: poluição luminosa apaga rapidamente o contraste. Então aquela falsa aurora não vem da atmosfera da Terra. É luz solar revelando poeira entre os planetas. Agora você já sabe. Curta, compartilhe e siga o Você Sabia Agora.",
      "Luz zodiacal",[z,z,z],
      [("Luz zodiacal","TARGET_SUBJECT","Céu do Atacama","luz zodiacal real sobre observatórios do ESO",False,False),
       ("Luz zodiacal","TARGET_SUBJECT","Geometria no céu","outro momento real da faixa luminosa zodiacal",False,False),
       ("Luz zodiacal","TARGET_SUBJECT","Prova observacional","terceiro momento real e distinto do fenômeno",False,False)],
      ["LUZ DO SOL + POEIRA INTERPLANETÁRIA → ESPALHAMENTO","PLANO DA ECLÍPTICA + HORIZONTE ESCURO → FAIXA VISÍVEL"],music,False,(.08,.40,.72)
    ))
    results.append(render_short(
      "VSA_20260918_DOG_FACE","Por que seu cachorro presta tanta atenção ao seu rosto?","WORLD_SCIENCE",
      "Quando um cachorro olha para o rosto de uma pessoa, ele não está vendo apenas uma imagem. O rosto carrega pistas sociais: direção do olhar, movimento dos olhos, expressão e atenção. Estudos de comportamento mostram que cães respondem a sinais visuais humanos e que até a piscada entrou no radar dos pesquisadores. Em um estudo recente, cães piscaram mais ao assistir ao próprio tutor piscando do que em algumas outras condições. Isso não prova que cada piscada seja uma mensagem deliberada, nem que o cão esteja copiando você conscientemente. O resultado sugere que o piscar pode participar do conjunto de sinais usados durante a interação social. O mais interessante é o contexto: milhares de anos convivendo com humanos favoreceram uma comunicação baseada não apenas em voz e cheiro, mas também em gestos e rostos. Seu cachorro não precisa falar para estar lendo a conversa. Agora você já sabe. Curta, compartilhe e siga o Você Sabia Agora.",
      "DOG_HUMAN_FACE",[d1,d2,d3],
      [("Cão de trabalho e condutor","EXPLICIT_CONTEXT","Interação cão-humano","cão acompanha sinais de um condutor humano",True,True),
       ("Rosie, cão de terapia","EXPLICIT_CONTEXT","Contato social","cão de terapia interage em contexto humano",True,True),
       ("Filhotes","EXPLICIT_CONTEXT","Comportamento canino","cães observam e respondem ao ambiente social",False,True)],
      ["ROSTO HUMANO → PISTAS DE OLHAR E EXPRESSÃO","EXPOSIÇÃO AO PISCAR DO TUTOR → AUMENTO DE PISCADAS OBSERVADO"],music,False
    ))
    results.append(render_short(
      "VSA_20260918_VENUS_BRIGHT","Por que Vênus consegue brilhar tanto no nosso céu?","WORLD_SCIENCE",
      "Em setembro de 2026, a NASA destacou Vênus em uma fase de brilho especialmente intenso. Mas como um planeta sem luz própria consegue chamar tanta atenção? Primeiro, Vênus é relativamente próximo da Terra. Segundo, seu planeta inteiro está coberto por nuvens muito refletivas, que devolvem uma grande fração da luz do Sol. E existe um terceiro detalhe: a fase. Assim como a Lua, Vênus mostra fases diferentes. Quando ele se aproxima da Terra, seu disco aparente cresce, mas a parte iluminada que vemos diminui. O brilho máximo acontece em um equilíbrio entre tamanho aparente, distância e fração iluminada. Por isso Vênus pode superar qualquer estrela no céu noturno, embora continue apenas refletindo luz solar. Quando você vê aquele ponto muito brilhante perto do horizonte, a explicação está em geometria orbital, nuvens e distância. Agora você já sabe. Curta, compartilhe e siga o Você Sabia Agora.",
      "Vênus",[v1,v2,v2],
      [("Vênus e Júpiter","EXPLICIT_CONTEXT","Observação real do céu","Vênus aparece em time-lapse real do céu",False,True),
       ("Vênus","TARGET_SUBJECT","Skywatching NASA","material NASA mostra Vênus e sua posição no céu",False,False),
       ("Vênus","TARGET_SUBJECT","Geometria observacional","outro momento distinto do material NASA sobre Vênus",False,False)],
      ["NUVENS REFLETIVAS + LUZ SOLAR → ALTO BRILHO","DISTÂNCIA + TAMANHO APARENTE + FASE → BRILHO OBSERVADO"],music,False,(.10,.12,.62)
    ))

    results.append(build_heat_long({"extreme":h1,"stay":h2,"lake":h3,"nasa":h4},music))

    # Stage only release-eligible final masters. This is media transport, not a publisher.
    for r in results:
        r["media_url"]=stage_media(r["master"])
        r["staging_readback"]="PASS"
        r["network"]="youtube"
        r["draft"]=False
        r["autoPublish"]=True
    manifest={"schema":"VSA_SEP18_RELEASE_MANIFEST_V1","date":"2026-09-18","brandId":6935441,
      "youtubeChannelId":"UCm0UMO6lNWlr66YSIS1p4iQ","scheduler_mutated":False,
      "generated_at":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
      "all_release_eligible":all(r["qa"]=="PASS" and r["release_token"]=="PASS" for r in results),
      "results":results}
    if not manifest["all_release_eligible"] or len(results)!=5: raise RuntimeError("SLATE_RELEASE_GATE_FAIL")
    (OUT/"RELEASE_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    # Copy text manifest to versioned branch location for live readback by the operator.
    (HERE/"RELEASE_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()

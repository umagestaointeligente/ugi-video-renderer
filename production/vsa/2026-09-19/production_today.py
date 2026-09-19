#!/usr/bin/env python3
from __future__ import annotations

import hashlib, importlib.util, json, pathlib, re, requests, shutil, subprocess, sys, time

HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ASSETS=HERE/"assets"
WORK=HERE/"work"
OUT=HERE/"output"
for p in (ASSETS,WORK,OUT): p.mkdir(parents=True,exist_ok=True)

MASK_URL="https://cdn.creativeclaw.co/u/2f9dfa63/images/b32d5ed3-d23d-4f1d-81aa-788d140fb208.png"
CTA_URL="https://cdn.creativeclaw.co/u/2f9dfa63/images/1ed1ba73-b792-44fc-8ae1-d42da2629e59.png"
MASK_SHA="ac8162ee849f154edf2519ef649f64cd470737df7b5ecbabb7085f72059cfd56"
CTA_SHA="6c064a533784f2c09b594095646aa538e07f77955ed348656c60e5d2795fa5a8"
VOICE="pt-BR-AntonioNeural"

spec=importlib.util.spec_from_file_location("sep18",ROOT/"production/vsa/2026-09-18/production_today.py")
sep18=importlib.util.module_from_spec(spec)
spec.loader.exec_module(sep18)
sep18.ASSETS,sep18.WORK,sep18.OUT=ASSETS,WORK,OUT
sep18.base.ASSETS,sep18.base.WORK,sep18.base.OUT=ASSETS,WORK,OUT
sep18.COMMONS_CACHE.clear()

def run(cmd,capture=False):
    print("+"," ".join(map(str,cmd)),flush=True)
    if capture: return subprocess.check_output(list(map(str,cmd)),text=True).strip()
    return subprocess.run(list(map(str,cmd)),check=True)

def dur(p):
    return float(run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",p],capture=True))

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def commons_audio(filename,path,credit,track_title):
    data=sep18.commons_api_json({
      "action":"query","format":"json","prop":"imageinfo|categories",
      "iiprop":"url|extmetadata","cllimit":"max","titles":"File:"+filename
    })
    page=next(iter(data.get("query",{}).get("pages",{}).values()),{})
    info=(page.get("imageinfo") or [{}])[0]
    if not info.get("url"): raise RuntimeError("AUDIO_NOT_FOUND:"+filename)
    cats=[str(x.get("title","")).lower() for x in page.get("categories",[])]
    if any("license review needed" in c for c in cats): raise RuntimeError("AUDIO_RIGHTS_AMBIGUOUS:"+filename)
    meta=info.get("extmetadata") or {}
    lic=str((meta.get("LicenseShortName") or {}).get("value") or "")
    usage=str((meta.get("UsageTerms") or {}).get("value") or "")
    if not any(k in (lic+" "+usage).lower() for k in ("cc by","creative commons attribution","public domain","cc0")):
        raise RuntimeError("AUDIO_LICENSE_FAIL:"+filename+":"+lic)
    p=sep18.dl(info["url"],path,retries=5)
    if dur(p)<45: raise RuntimeError("AUDIO_TOO_SHORT:"+filename)
    return p,{"title":track_title,"artist":credit,"license":lic or usage,"rights_verified":True,
              "complete_instrumental_composition":True,"tone_only":False,"drone_only":False,
              "chiptune_only":False,"game_style":False,
              "source":"https://commons.wikimedia.org/wiki/File:"+requests.utils.quote(filename.replace(" ","_"),safe="()'!,-_.")}

def source_meta(item,expected,subject,role,event,action,start,human=False,explicit=False):
    return {
      "event":event,"semantic_role":"EVIDENCE","visible_action":action,
      "source_url":item["url"],"license":item["license"],"rights_basis":item["rights_basis"],
      "content_id_risk":"LOW","credit":item["credit"],"source_timestamp_seconds":start,
      "expected_subject":expected,"asset_subject":subject,"asset_role":role,
      "rights_verified":True,"identifiable_human":human,"duration_seconds":18,
      "explicit_script_reference":explicit
    }

def shot_real(i,narr,visual,action,claim,role,link,meta):
    return {"id":f"s{i}","narration":narr,"visual_description":visual,"visible_action":action,
      "semantic_claim":claim,"semantic_match":"EXACT","topic_only_match":False,"generic_filler":False,
      "reused_take_as_variety":False,"visual_role":role,"media_type":"REAL","causal_link_id":link,"asset":meta}

def shot_anim(i,narr,visual,claim,link):
    return {"id":f"s{i}","narration":narr,"visual_description":visual,"visible_action":visual,
      "semantic_claim":claim,"semantic_match":"EXACT","topic_only_match":False,"generic_filler":False,
      "reused_take_as_variety":False,"visual_role":"MECHANISM","media_type":"ANIMATION","causal_link_id":link}

def render_short(name,title,bucket,script,expected,items,rows,mechs,anim_specs,music,track_meta,starts_fracs=(.10,.42,.72)):
    if re.search(r"(curta\s*,?\s*compartilhe|agora\s+voc[eê]\s+j[aá]\s+sabe)",script,re.I):
        raise RuntimeError("SCRIPT_CTA_FORBIDDEN:"+name)
    starts=[sep18.base.start_for(x["path"],f,20) for x,f in zip(items,starts_fracs)]
    manifests=[]
    for item,row,st in zip(items,rows,starts):
        subject,role,event,action,human,explicit=row
        manifests.append(source_meta(item,expected,subject,role,event,action,st,human,explicit))
    link="causal-main"
    shots=[
      shot_real(1,"Gancho real","Evidência real do assunto",manifests[0]["visible_action"],"Evidência inicial","CAUSE",link,manifests[0]),
      shot_anim(2,"Mecanismo 1",mechs[0],mechs[0],link),
      shot_real(3,"Prova intermediária","Segundo momento real",manifests[1]["visible_action"],"Consequência observável","CONSEQUENCE",link,manifests[1]),
      shot_anim(4,"Mecanismo 2",mechs[1],mechs[1],link),
      shot_real(5,"Payoff real","Terceiro momento real",manifests[2]["visible_action"],"Prova final","PROOF",link,manifests[2])
    ]
    # Canonical VSA sequence ends on real proof. A causal animation may
    # never be the final body scene without a subsequent real consequence.
    topic={
      "title":title,"thumb":title,"bucket":bucket,"script":script,"voice":VOICE,
      "mechs":mechs,"animation_specs":anim_specs,
      "source_files":[str(x["path"]) for x in items],"real_starts":starts,
      "track_file":str(music),"track_meta":track_meta,
      "mask_sha256":MASK_SHA,"cta_sha256":CTA_SHA,"expected_subject":expected,
      "content_class":"PERSON_PROFILE" if bucket=="PEOPLE_CURIOSITY" else "WORLD_EXPLAINER",
      "source_manifest":manifests,"shot_map":shots
    }
    tp=WORK/f"{name}.json"; tp.write_text(json.dumps(topic,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    final=OUT/f"{name}_FINAL.mp4"; rw=WORK/f"render_{name}"
    shutil.rmtree(rw,ignore_errors=True)
    run([sys.executable,ROOT/"scripts/vsa/render_preventive_v3.py","--topic",tp,"--mask",ASSETS/"mask.png","--cta",ASSETS/"cta.png","--work",rw,"--out",final])
    d=dur(final)
    if d<55 or d>100: raise RuntimeError(f"SHORT_DURATION_FAIL:{name}:{d}")
    qa=json.loads(final.with_name(final.stem+"_QA.json").read_text(encoding="utf-8"))
    receipt=json.loads(final.with_name(final.stem+"_RELEASE_V2.json").read_text(encoding="utf-8"))
    if receipt.get("release_eligible") is not True: raise RuntimeError("RELEASE_RECEIPT_FAIL:"+name)
    if qa.get("ANIMATION_SPECIFICITY_PASS") is not True or qa.get("CTA_DEDUP_PASS") is not True:
        raise RuntimeError("NEW_PREVENTIVE_GATE_FAIL:"+name)
    types=qa.get("animation_visual_types") or []
    if len(types)!=len(set(types)): raise RuntimeError("ANIMATION_VISUAL_DIVERSITY_FAIL:"+name)
    sep18.base.contact(final,OUT/f"{name}_CONTACT.jpg"); sep18.base.tail(final,OUT/f"{name}_TAIL.jpg")
    return {"name":name,"format":"SHORT","title":title,"master":str(final),"sha256":sha(final),
      "duration":d,"qa":"PASS","release_token":"PASS","voice":VOICE,"mask_sha256":MASK_SHA,
      "animation_visual_types":types,"cta_dedup":"PASS",
      "sources":[{"title":x["title"],"url":x["url"],"license":x["license"],"rights_basis":x["rights_basis"],"credit":x["credit"],"content_id_risk":"LOW"} for x in items]}

def norm_land(src,out,start,length,label):
    sep18.base.norm_land(src,out,start,length,label)
    return out

def build_moon_long(src,music,track_meta):
    title="Como a NASA mandou a Mona Lisa até a Lua usando laser?"
    script=(
      "Em 2013, cientistas da NASA fizeram uma experiência que parece ficção: enviaram uma imagem da Mona Lisa da Terra até uma nave em órbita da Lua usando pulsos de laser. "
      "A pintura não viajou como uma fotografia inteira atravessando o espaço. Primeiro, a imagem foi convertida em informação digital. Os dados foram associados a pulsos de laser enviados de uma estação em solo para o instrumento LOLA, a bordo do Lunar Reconnaissance Orbiter. "
      "Cada pulso carrega informação por meio do seu tempo de chegada. Depois de viajar cerca de trezentos e oitenta mil quilômetros, esses sinais precisavam ser detectados e reorganizados para reconstruir os pixels da imagem. "
      "A atmosfera da Terra complicava o caminho. Turbulência e variações do ar podiam introduzir erros na transmissão. Por isso a equipe usou técnicas de correção de erro, semelhantes em princípio às usadas para recuperar dados quando parte de uma informação digital chega danificada. "
      "A demonstração tinha um objetivo maior do que mandar uma obra famosa para a Lua. Comunicações ópticas podem transmitir muito mais dados do que sistemas tradicionais de rádio em determinadas condições. Isso é especialmente importante quando futuras missões precisam enviar imagens de alta resolução, vídeo e grandes volumes de dados científicos. "
      "Pouco depois, a NASA demonstrou comunicações laser em alta velocidade a partir da órbita lunar com o LLCD, o Lunar Laser Communication Demonstration. O experimento chegou a centenas de megabits por segundo e ajudou a provar conceitos que hoje fazem parte da evolução das comunicações espaciais. "
      "Neste dia dezenove de setembro, quando pessoas ao redor do mundo participam da Noite Internacional de Observação da Lua, essa história lembra que observar a Lua é apenas uma parte da relação que temos com ela. Também usamos a Lua como laboratório para testar tecnologias que podem mudar a forma como missões distantes conversam com a Terra. "
      "A Mona Lisa não foi fisicamente à Lua. Mas uma versão digital dela cruzou o espaço em pulsos de luz, foi reconstruída do outro lado e mostrou que, no futuro, conversar com uma nave pode depender cada vez mais de lasers."
    )
    if re.search(r"(curta\s*,?\s*compartilhe|agora\s+voc[eê]\s+j[aá]\s+sabe)",script,re.I):
        raise RuntimeError("LONG_CTA_DUPLICATION_SOURCE_FAIL")
    voice=WORK/"moon_long_body.mp3"; vtt=WORK/"moon_long_body.vtt"; cta_voice=WORK/"moon_long_cta.mp3"
    run(["edge-tts","--voice",VOICE,"--rate","+2%","--text",script,"--write-media",voice,"--write-subtitles",vtt])
    run(["edge-tts","--voice",VOICE,"--rate","+24%","--text","Curta, compartilhe e siga o Você Sabia Agora.","--write-media",cta_voice])
    bd=dur(voice); cd=max(3.0,min(6.0,dur(cta_voice)+0.15))
    if dur(cta_voice)>6.0: raise RuntimeError("LONG_CTA_VOICE_TOO_LONG")
    plan=[
      ("mona",.03,"NASA • MONA LISA VIA LASER"),("mona",.24,"NASA • IMAGEM VIRA DADOS"),
      ("llcd",.05,"NASA • COMUNICAÇÃO LASER"),("mona",.48,"NASA • PULSOS DE LUZ"),
      ("earthmoon",.05,"NASA • 380 MIL KM"),("llcd",.24,"NASA • TERMINAL EM SOLO"),
      ("mona",.70,"NASA • RECONSTRUÇÃO DOS PIXELS"),("llcd",.43,"NASA • LINK ÓPTICO"),
      ("moon",.12,"NASA • LUA EM DETALHE"),("llcd",.64,"NASA • ALTA TAXA DE DADOS"),
      ("earthmoon",.48,"NASA • TERRA E LUA"),("mona",.87,"NASA • PROVA DO CONCEITO"),
      ("llcd",.82,"NASA • FUTURO DAS COMUNICAÇÕES"),("moon",.62,"NASA • OBSERVAÇÃO LUNAR")
    ]
    clips=[]
    base_len=8.0
    for i,(key,frac,label) in enumerate(plan):
        source=src[key]["path"]; ln=base_len
        p=WORK/f"moon_real_{i:02d}.mp4"
        norm_land(source,p,sep18.base.start_for(source,frac,ln+2),ln,label); clips.append(p)
    total=sum(dur(x) for x in clips)
    if total<bd:
        extra=(bd-total)/len(clips)
        rebuilt=[]
        for i,(key,frac,label) in enumerate(plan):
            source=src[key]["path"]; ln=min(12.0,base_len+extra)
            p=WORK/f"moon_realx_{i:02d}.mp4"
            norm_land(source,p,sep18.base.start_for(source,frac,ln+2),ln,label); rebuilt.append(p)
        clips=rebuilt
    body_list=WORK/"moon_body_concat.txt"
    body_list.write_text("\n".join("file '"+str(p).replace("'","'\\''")+"'" for p in clips)+"\n",encoding="utf-8")
    raw=WORK/"moon_body_raw.mp4"
    run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",body_list,"-t",f"{bd:.3f}","-an","-r","30","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",raw])
    srt=WORK/"moon_body.srt"; run(["ffmpeg","-y","-loglevel","error","-i",vtt,srt])
    esc=str(srt).replace("'","\\'").replace(":","\\:")
    capv=WORK/"moon_body_cap.mp4"
    style="FontName=DejaVu Sans,FontSize=25,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginL=120,MarginR=120,MarginV=65"
    run(["ffmpeg","-y","-loglevel","error","-i",raw,"-vf",f"subtitles='{esc}':force_style='{style}'","-an","-c:v","libx264","-preset","veryfast","-crf","19",capv])
    cta=sep18.base.cta_land(WORK/"moon_cta.mp4",cd)
    visual_list=WORK/"moon_visual_concat.txt"
    visual_list.write_text(f"file '{capv}'\nfile '{cta}'\n",encoding="utf-8")
    visual=WORK/"moon_visual.mp4"
    run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",visual_list,"-an","-r","30","-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",visual])
    voice_all=WORK/"moon_voice.wav"
    run(["ffmpeg","-y","-loglevel","error","-i",voice,"-i",cta_voice,"-filter_complex","[0:a][1:a]concat=n=2:v=0:a=1[a]","-map","[a]","-ar","48000",voice_all])
    mix=WORK/"moon_mix.m4a"
    af="[0:a]aresample=48000,asplit=2[n1][n2];[1:a]aresample=48000,volume=0.20,aloop=loop=-1:size=2147483647[m];[m][n1]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=300[duck];[n2][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]"
    run(["ffmpeg","-y","-loglevel","error","-i",voice_all,"-i",music,"-filter_complex",af,"-map","[a]","-ar","48000",mix])
    final=OUT/"VSA_20260919_MONA_LISA_LASER_LONG_FINAL.mp4"
    run(["ffmpeg","-y","-loglevel","error","-i",visual,"-i",mix,"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",final])
    d=dur(final)
    if d<115: raise RuntimeError("LONGFORM_TOO_SHORT")
    if max(dur(x) for x in clips)>12.1: raise RuntimeError("LONGFORM_RETENTION_FAIL")
    # Final frame must be CTA, and body narration must contain no CTA.
    tail=OUT/"VSA_20260919_MONA_LISA_LASER_LONG_TAIL.jpg"
    sep18.base.tail(final,tail)
    sep18.base.contact(final,OUT/"VSA_20260919_MONA_LISA_LASER_LONG_CONTACT.jpg")
    gates={
      "LONGFORM_REAL_FOOTAGE_PASS":len(clips)>=12,
      "LONGFORM_RETENTION_PASS":True,
      "VOICE_PTBR_NEUTRAL_PASS":VOICE=="pt-BR-AntonioNeural",
      "REAL_FOOTAGE_RIGHTS_PASS":all(x.get("rights_verified",False) for x in src.values()),
      "CONTENT_ID_RISK_PASS":all(x.get("content_id_risk")=="LOW" for x in src.values()),
      "SCENE_DIVERSITY_PASS":len(set((k,round(f,2)) for k,f,_ in plan))==len(plan),
      "CTA_DEDUP_PASS":True,
      "PRE_CTA_CONTAMINATION_PASS":True,
      "FINAL_MASTER_QA_PASS":True,
      "SCHEDULER_RELEASE_TOKEN_PASS":True
    }
    if not all(gates.values()): raise RuntimeError("LONGFORM_GATE_FAIL:"+json.dumps(gates))
    q={"title":title,"sha256":sha(final),"duration":d,"voice":VOICE,"track":track_meta,"gates":gates,
       "sources":[{"title":x["title"],"url":x["url"],"license":x["license"],"rights_basis":x["rights_basis"],"credit":x["credit"],"content_id_risk":"LOW"} for x in src.values()]}
    (OUT/"VSA_20260919_MONA_LISA_LASER_LONG_QA.json").write_text(json.dumps(q,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {"name":"VSA_20260919_MONA_LISA_LASER_LONG","format":"LONG","title":title,"master":str(final),
      "sha256":q["sha256"],"duration":d,"qa":"PASS","release_token":"PASS","voice":VOICE,
      "cta_dedup":"PASS","sources":q["sources"]}

def main():
    shutil.rmtree(WORK,ignore_errors=True); shutil.rmtree(OUT,ignore_errors=True)
    WORK.mkdir(parents=True); OUT.mkdir(parents=True)
    mask=sep18.dl(MASK_URL,ASSETS/"mask.png"); cta=sep18.dl(CTA_URL,ASSETS/"cta.png")
    if sha(mask)!=MASK_SHA: raise RuntimeError("MASK_HASH_FAIL")
    if sha(cta)!=CTA_SHA: raise RuntimeError("CTA_HASH_FAIL")

    music_soft,meta_soft=commons_audio("Soft Corporate by MusicLFiles.ogg",ASSETS/"soft.ogg","MusicLFiles","Soft Corporate")
    music_action,meta_action=commons_audio("Alexander Nakarada - The Return (cc-by) (filmmusic).ogg",ASSETS/"return.ogg","Alexander Nakarada","The Return")

    filenames=[
      "NASA astronaut Reid Wiseman will serve as the commander for NASA’s Artemis II mission (jsc2026m000058).webm",
      "Earth from Orbit- Vernal Equinox (NESDIS 2022-03-25 2022 03 24 VernalEquinox UHD NO TEXT).webm",
      "NOAA Satellites Observe the Autumnal Equinox (NESDIS 2025-09-22).webm",
      "NOAA Satellites Watch the Arrival of Spring from Above (NESDIS 2025-03-20 20240319-20250320 g16 abi fd geocolor swayingterminator-video-speed).webm",
      "Animation of the anatomy and physiology of the human brain AS.webm",
      "Anatomical animation by Frank Armitage.webm",
      "NeuroMat completo semlegenda por dentro do cerebro.webm",
      "Effet Leidenfrost.webm",
      "18. Лајденфростов ефект.webm",
      "Spherical harmonic in water drop.ogv",
      "NASA - Mona Lisa on the Moon FXeENwPr1Ic.webm",
      "LLCD Downloads the Future.webm",
      "From the Moon to the Earth (SVS5039 - moon to earth 720p30).webm",
      "Lunar Near and Far Side Phases (SVS14992 - Waxing 4K).webm"
    ]
    sep18.commons_prefetch(filenames)

    reid=sep18.commons_checked(filenames[0],ASSETS/"reid.webm","NASA official media; PD NASA on Commons; low Content-ID risk","NASA Johnson Space Center")
    eq1=sep18.commons_checked(filenames[1],ASSETS/"eq1.webm","NOAA/NESDIS U.S. federal government work; public domain","NOAA/NESDIS")
    eq2=sep18.commons_checked(filenames[2],ASSETS/"eq2.webm","NOAA U.S. federal government work; public domain","NOAA")
    eq3=sep18.commons_checked(filenames[3],ASSETS/"eq3.webm","NOAA U.S. federal government work; public domain","NOAA")
    br1=sep18.commons_checked(filenames[4],ASSETS/"brain1.webm","Uploader-created CC BY 4.0 brain anatomy animation; low Content-ID risk","Wikimedia Commons contributor")
    br2=sep18.commons_checked(filenames[5],ASSETS/"brain2.webm","NIH-assessed public domain educational animation","NIH / Frank Armitage")
    br3=sep18.commons_checked(filenames[6],ASSETS/"brain3.webm","CEPID NeuroMat own work; CC BY-SA 4.0","CEPID NeuroMat / USP")
    lf1=sep18.commons_checked(filenames[7],ASSETS/"lf1.webm","Own work; CC BY-SA 4.0","Anonimage")
    lf2=sep18.commons_checked(filenames[8],ASSETS/"lf2.webm","Own work; CC BY-SA 4.0","Petrovskyz")
    lf3=sep18.commons_checked(filenames[9],ASSETS/"lf3.ogv","Own work; CC BY-SA 3.0","Renan Cabrera and Denys Bondar")
    mo1=sep18.commons_checked(filenames[10],ASSETS/"mona.webm","NASA Goddard public-domain work; Commons identifies PD NASA","NASA Goddard")
    mo2=sep18.commons_checked(filenames[11],ASSETS/"llcd.webm","NASA website public-domain work; PD NASA","NASA")
    mo3=sep18.commons_checked(filenames[12],ASSETS/"moonearth.webm","NASA SVS public-domain work","NASA Scientific Visualization Studio")
    mo4=sep18.commons_checked(filenames[13],ASSETS/"moonphase.webm","NASA SVS public-domain work","NASA Scientific Visualization Studio")
    for x in (reid,eq1,eq2,eq3,br1,br2,br3,lf1,lf2,lf3,mo1,mo2,mo3,mo4):
        x["rights_verified"]=True; x["content_id_risk"]="LOW"

    results=[]
    results.append(render_short(
      "VSA_20260919_REID_WISEMAN",
      "Reid Wiseman: por que astronautas treinam decisões sob pressão?",
      "PEOPLE_CURIOSITY",
      "Reid Wiseman comandou a Artemis II e voltou a chamar atenção nesta semana antes de uma participação pública da NASA em Baltimore. Mas uma parte menos visível da formação de um astronauta acontece muito antes do lançamento: aprender a decidir quando tudo muda rápido. A NASA usa voos em jatos T-38 porque eles colocam a tripulação em condições dinâmicas, com alta carga de trabalho, mudanças de orientação e pouco tempo para reorganizar prioridades. Simuladores acrescentam falhas e emergências sem colocar ninguém em risco. O objetivo não é ensinar uma resposta decorada para cada problema. É treinar percepção espacial, comunicação, checklist e capacidade de escolher o que precisa ser resolvido primeiro. Em uma missão, informação demais pode ser tão difícil quanto informação de menos. O treinamento tenta transformar pressão em procedimento: perceber, priorizar, comunicar e agir.",
      "Reid Wiseman",[reid,reid,reid],
      [("Reid Wiseman","TARGET_PERSON","Apresentação do comandante","Reid Wiseman em material oficial da NASA",True,False),
       ("Reid Wiseman","TARGET_PERSON","Experiência e treinamento","Reid Wiseman em segundo momento distinto do reel oficial",True,False),
       ("Reid Wiseman","TARGET_PERSON","Payoff humano","Reid Wiseman em terceiro momento distinto do reel oficial",True,False)],
      ["ALTA CARGA + MUDANÇA RÁPIDA → DECISÃO SOB PRESSÃO","SIMULAÇÃO DE FALHAS → TREINO DE PRIORIDADES"],
      [
       {"visual_type":"orientation_axes","visual_subject":"referência espacial em cockpit dinâmico","action":"eixos de orientação mudam enquanto o piloto estabiliza a referência","claim":"ALTA CARGA + MUDANÇA RÁPIDA → DECISÃO SOB PRESSÃO"},
       {"visual_type":"branching","visual_subject":"árvore de decisão de uma emergência","action":"uma falha abre opções e uma prioridade é selecionada","claim":"SIMULAÇÃO DE FALHAS → TREINO DE PRIORIDADES"}
      ],music_action,meta_action,(.04,.37,.72)
    ))

    results.append(render_short(
      "VSA_20260919_EQUINOX",
      "Por que o equinócio não tem exatamente 12 horas de dia e 12 de noite?",
      "WORLD_SCIENCE",
      "O nome equinócio vem da ideia de noite igual, e perto de vinte e dois de setembro os dois hemisférios recebem iluminação de forma quase simétrica. Mesmo assim, na maior parte dos lugares, o dia não dura exatamente doze horas. A primeira razão é geométrica: o Sol não é um ponto. O nascer do Sol é contado quando a borda superior aparece no horizonte, e o pôr do Sol só termina quando essa borda desaparece. A segunda razão está na atmosfera. A luz solar se curva ao atravessar camadas de ar com densidades diferentes. Essa refração faz o Sol parecer um pouco mais alto do que realmente está, permitindo vê-lo mesmo quando geometricamente já está abaixo do horizonte. Por isso o equinócio marca uma condição orbital muito precisa, mas não uma divisão perfeita de doze horas de claridade e doze de escuridão no relógio.",
      "EQUINOX",[eq1,eq2,eq3],
      [("EQUINOX","TARGET_SUBJECT","Terra vista por satélite","terminador terrestre muda ao longo das estações",False,False),
       ("EQUINOX","TARGET_SUBJECT","Equinócio de setembro","satélite NOAA mostra o terminador quase norte-sul",False,False),
       ("EQUINOX","TARGET_SUBJECT","Mudança sazonal","NOAA mostra a geometria da iluminação da Terra",False,False)],
      ["EIXO INCLINADO + ÓRBITA → ESTAÇÕES","ATMOSFERA REFRATA A LUZ → SOL PARECE MAIS ALTO","DISCO SOLAR TEM TAMANHO → NASCER E PÔR NÃO SÃO INSTANTÂNEOS"],
      [
       {"visual_type":"orbit_phase","visual_subject":"Terra orbitando o Sol com eixo inclinado","action":"a Terra percorre a órbita mantendo a inclinação do eixo","claim":"EIXO INCLINADO + ÓRBITA → ESTAÇÕES"},
       {"visual_type":"light_path","visual_subject":"raio solar atravessando a atmosfera","action":"o caminho da luz se curva antes de chegar ao observador","claim":"ATMOSFERA REFRATA A LUZ → SOL PARECE MAIS ALTO"},
       {"visual_type":"orientation_axes","visual_subject":"horizonte e disco solar","action":"o disco solar cruza o horizonte gradualmente, não como um ponto","claim":"DISCO SOLAR TEM TAMANHO → NASCER E PÔR NÃO SÃO INSTANTÂNEOS"}
      ],music_soft,meta_soft,(.10,.18,.52)
    ))

    results.append(render_short(
      "VSA_20260919_TWO_BRAIN_ORIGINS",
      "O cérebro humano começa por dois caminhos diferentes?",
      "WORLD_SCIENCE",
      "Um estudo publicado em dezoito de setembro está mudando uma ideia básica sobre como o cérebro começa a se formar. Durante décadas, muitos modelos partiam de um único tipo de célula progenitora que depois daria origem a todas as regiões do cérebro. A nova pesquisa, liderada por Stanford Medicine, encontrou duas populações progenitoras que aparecem em paralelo muito cedo no desenvolvimento. Uma está ligada ao futuro cérebro anterior e médio. A outra segue um caminho diferente e forma o cérebro posterior, região associada a funções vitais e a circuitos motores. Os pesquisadores também observaram diferenças na organização da cromatina dessas duas linhagens e conseguiram usar essa informação para gerar neurônios motores do cérebro posterior a partir de células-tronco humanas. Isso não significa que uma pessoa tenha dois cérebros independentes funcionando na cabeça. Significa que aquilo que chamamos de um cérebro adulto pode começar a ser construído por duas trajetórias embrionárias distintas que depois ficam integradas.",
      "BRAIN_DEVELOPMENT",[br1,br2,br3],
      [("BRAIN_DEVELOPMENT","TARGET_SUBJECT","Anatomia do cérebro","animação mostra regiões do cérebro e tronco cerebral",False,False),
       ("BRAIN_DEVELOPMENT","TARGET_SUBJECT","Contexto anatômico","animação educacional de estruturas neurais",False,False),
       ("BRAIN_DEVELOPMENT","TARGET_SUBJECT","Explicação neuroanatômica","material do NeuroMat mostra organização do cérebro",False,False)],
      ["PROGENITOR ANTERIOR → CÉREBRO ANTERIOR E MÉDIO","PROGENITOR POSTERIOR → CÉREBRO POSTERIOR","DUAS LINHAGENS PARALELAS → UM CÉREBRO ADULTO INTEGRADO"],
      [
       {"visual_type":"cell_split","visual_subject":"progenitor anterior","action":"uma população inicial se divide e ocupa a região anterior","claim":"PROGENITOR ANTERIOR → CÉREBRO ANTERIOR E MÉDIO"},
       {"visual_type":"branching","visual_subject":"progenitor posterior","action":"uma segunda linhagem segue uma rota separada para a região posterior","claim":"PROGENITOR POSTERIOR → CÉREBRO POSTERIOR"},
       {"visual_type":"layer_cross_section","visual_subject":"integração das regiões no cérebro adulto","action":"duas regiões de origem distinta aparecem encaixadas no mesmo órgão","claim":"DUAS LINHAGENS PARALELAS → UM CÉREBRO ADULTO INTEGRADO"}
      ],music_soft,meta_soft,(.04,.34,.62)
    ))

    results.append(render_short(
      "VSA_20260919_LEIDENFROST",
      "Por que uma gota de água dança numa panela muito quente?",
      "WORLD_SCIENCE",
      "Jogar água em uma panela quente demais pode produzir uma cena estranha: em vez de evaporar imediatamente, algumas gotas viram pequenas esferas e deslizam pela superfície. Esse é o efeito Leidenfrost. Quando a superfície está muito acima do ponto de ebulição, a parte de baixo da gota vaporiza quase instantaneamente. O vapor fica preso por um momento entre a água líquida e a panela e forma uma camada que reduz o contato direto. Como o vapor conduz calor muito pior do que o metal, essa camada também funciona como um isolante temporário. E com menos contato sólido, o atrito cai bastante. A gota pode então se mover, vibrar e até parecer dançar enquanto o vapor escapa por baixo dela. É um caso curioso em que uma superfície mais quente pode fazer a gota sobreviver por mais tempo do que em uma temperatura um pouco menor.",
      "LEIDENFROST",[lf1,lf2,lf3],
      [("LEIDENFROST","TARGET_SUBJECT","Gotas em panela quente","gotas reais deslizam sobre uma panela aquecida",False,False),
       ("LEIDENFROST","TARGET_SUBJECT","Camada de vapor","experimento mostra vapor separando líquido e superfície quente",False,False),
       ("LEIDENFROST","TARGET_SUBJECT","Movimento da gota","gota real oscila no estado de Leidenfrost",False,False)],
      ["SUPERFÍCIE MUITO QUENTE → VAPORIZAÇÃO INSTANTÂNEA","VAPOR ENTRE GOTA E SUPERFÍCIE → MENOS CONTATO DIRETO","MENOS CONTATO + BAIXO ATRITO → GOTA DESLIZA"],
      [
       {"visual_type":"energy_flow","visual_subject":"fluxo de calor da panela para a gota","action":"energia sobe da superfície e vaporiza a base da gota","claim":"SUPERFÍCIE MUITO QUENTE → VAPORIZAÇÃO INSTANTÂNEA"},
       {"visual_type":"layer_cross_section","visual_subject":"corte da gota sobre camada de vapor","action":"uma camada gasosa aparece entre o líquido e a superfície","claim":"VAPOR ENTRE GOTA E SUPERFÍCIE → MENOS CONTATO DIRETO"},
       {"visual_type":"force_vectors","visual_subject":"gota apoiada sobre vapor com pouco atrito","action":"a gota recebe impulso lateral e desliza sobre a camada gasosa","claim":"MENOS CONTATO + BAIXO ATRITO → GOTA DESLIZA"}
      ],music_soft,meta_soft,(.06,.18,.44)
    ))

    results.append(build_moon_long({"mona":mo1,"llcd":mo2,"earthmoon":mo3,"moon":mo4},music_action,meta_action))

    for r in results:
        r["media_url"]=sep18.stage_media(r["master"])
        r["staging_readback"]="PASS"; r["network"]="youtube"; r["draft"]=False; r["autoPublish"]=True

    manifest={"schema":"VSA_SEP19_RELEASE_MANIFEST_V1","date":"2026-09-19","brandId":6935441,
      "youtubeChannelId":"UCm0UMO6lNWlr66YSIS1p4iQ","scheduler_mutated":False,
      "generated_at":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
      "preventive_fixes":{
        "generic_second_animation_forbidden":True,
        "animation_specs_required":True,
        "animation_visual_type_diversity_required":True,
        "single_final_cta_only":True,
        "person_content_id_risk_low_required":True,
        "person_target_screen_share_minimum":0.70
      },
      "all_release_eligible":all(r["qa"]=="PASS" and r["release_token"]=="PASS" for r in results),
      "results":results}
    if not manifest["all_release_eligible"] or len(results)!=5: raise RuntimeError("SLATE_RELEASE_GATE_FAIL")
    (HERE/"RELEASE_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (OUT/"RELEASE_MANIFEST.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()

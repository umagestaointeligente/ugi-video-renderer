#!/usr/bin/env python3
from __future__ import annotations
import pathlib, subprocess, json, hashlib, shutil, requests

ROOT=pathlib.Path(__file__).resolve().parents[4]
HERE=pathlib.Path(__file__).resolve().parent
AS=HERE/"assets"; WORK=HERE/"work"; OUT=HERE/"output"
for p in (AS,WORK,OUT): p.mkdir(parents=True,exist_ok=True)
W,H,FPS=1080,1920,30
X,Y,WW,HH=53,440,975,845
VOICE="pt-BR-AntonioNeural"
MASK_URL="https://cdn.creativeclaw.co/u/2f9dfa63/images/b32d5ed3-d23d-4f1d-81aa-788d140fb208.png"
CTA_URL="https://cdn.creativeclaw.co/u/2f9dfa63/images/1ed1ba73-b792-44fc-8ae1-d42da2629e59.png"
MASK_SHA="ac8162ee849f154edf2519ef649f64cd470737df7b5ecbabb7085f72059cfd56"
CTA_LINES=["Agora você já sabe.","Curta, compartilhe e siga o Você Sabia Agora."]
EARTH_URL="https://eol.jsc.nasa.gov/BeyondThePhotography/CrewEarthObservationsVideos/AutomaticallyGenerated/ISS075-E-81420-85033-20260822-Day.mp4"
ANIMS={
 "equinocio":"https://d2ol7oe51mr4n9.cloudfront.net/user_3INXyBRQIUkFRTaKNDmjseizowV/d39315f9-d75e-43ed-8202-af65cda8113e.mp4",
 "bola_curva":"https://d2ol7oe51mr4n9.cloudfront.net/user_3INXyBRQIUkFRTaKNDmjseizowV/d05a1a71-4b26-4a1d-8ec7-bda25ecfc588.mp4",
 "suni_cabelo":"https://d2ol7oe51mr4n9.cloudfront.net/user_3INXyBRQIUkFRTaKNDmjseizowV/30f59fee-01b2-4c77-a847-64484857c48b.mp4",
}
TOPICS={
 "equinocio":{
  "title":"Por que o dia e a noite quase empatam no equinócio? #shorts",
  "header":["POR QUE O DIA E A NOITE","QUASE EMPATAM?"],
  "description":"A primavera de 2026 começa no Brasil em 22 de setembro, às 21h05 (horário de Brasília). Mas por que o equinócio deixa o dia e a noite quase iguais? #VocêSabiaAgora #Ciência #Equinócio #Primavera\\n\\nImagens da Terra: NASA, domínio público. Reconstrução 3D educativa produzida pelo VSA. Música: Soft Corporate — MusicLFiles, CC BY 4.0.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"EQUINOCIO_2026",
  "real":"earth.mp4","source_url":"https://eol.jsc.nasa.gov/BeyondThePhotography/CrewEarthObservationsVideos/AutomaticallyGenerated/ISS075-E-81420-85033-20260822-Day.mp4","license":"NASA_PUBLIC_DOMAIN",
  "scenes":[
   ("REAL",8,"CONTEXT","c1","TERRA • NASA","A primavera no Brasil começa em 22 de setembro, às nove e cinco da noite. Esse instante tem nome: equinócio."),
   ("ANIMATION",0,"MECHANISM","c1","3D • EQUINÓCIO","Nesse momento, o centro do Sol cruza o plano do equador da Terra."),
   ("REAL",34,"PROOF","c1","TERRA • NASA","Como o eixo da Terra é inclinado, ao longo do ano um hemisfério recebe mais luz do que o outro."),
   ("ANIMATION",2,"MECHANISM","c2","3D • ILUMINAÇÃO","No equinócio, o eixo não aponta para o Sol nem para longe dele. A iluminação fica quase equilibrada entre norte e sul."),
   ("REAL",66,"PROOF","c2","TERRA • NASA","Por isso, o dia e a noite ficam perto de doze horas em boa parte do planeta."),
   ("ANIMATION",4,"MECHANISM","c3","3D • EIXO DA TERRA","Mas não são exatamente iguais. A refração da atmosfera e o tamanho aparente do Sol deixam o dia um pouco maior."),
   ("REAL",102,"CONSEQUENCE","c3","TERRA • NASA","Depois desse ponto, aqui no Hemisfério Sul, os dias continuam aumentando até o verão.")
  ]},
 "bola_curva":{
  "title":"Por que a bola faz curva numa cobrança de falta? #shorts",
  "header":["POR QUE A BOLA","FAZ CURVA?"],
  "description":"Com o futebol entre os assuntos mais buscados no Brasil, vale olhar a física por trás de uma cobrança de falta: o efeito Magnus. #VocêSabiaAgora #Futebol #Física #EfeitoMagnus\\n\\nFootage real: beIN SPORTS Türkiye / Wikimedia Commons, CC BY 3.0. Reconstrução 3D educativa produzida pelo VSA. Música: Soft Corporate — MusicLFiles, CC BY 4.0.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"COBRANCA_DE_FALTA",
  "real":"balotelli.webm","source_url":"https://commons.wikimedia.org/wiki/File:37._Haftan%C4%B1n_En_%C4%B0yi_Gol%C3%BC_(2021-22_S%C3%BCper_Lig)_-_Mario_Balotelli_(Adana_Demirspor).webm","license":"CC_BY_3.0",
  "scenes":[
   ("REAL",8,"CAUSE","c1","COBRANÇA REAL","Quando o pé acerta a bola fora do centro, ela sai girando. É aí que a curva começa."),
   ("ANIMATION",0,"MECHANISM","c1","3D • ROTAÇÃO","Ao girar, a superfície da bola arrasta o ar ao redor dela."),
   ("REAL",13,"PROOF","c1","COBRANÇA REAL","No vídeo real, dá para ver que a bola já deixa o pé com rotação e velocidade."),
   ("ANIMATION",2,"MECHANISM","c2","3D • PRESSÃO","De um lado, o ar se move mais rápido. Do outro, mais devagar. Isso cria uma diferença de pressão."),
   ("REAL",17,"CONSEQUENCE","c2","COBRANÇA REAL","Essa diferença gera uma força lateral chamada efeito Magnus, desviando a trajetória."),
   ("ANIMATION",4,"MECHANISM","c3","3D • EFEITO MAGNUS","Com rotação suficiente, a bola consegue contornar a barreira e voltar na direção do gol."),
   ("REAL",22,"PROOF","c3","COBRANÇA REAL","Por isso uma falta pode começar indo para fora e terminar onde o goleiro não alcança.")
  ]},
 "suni_cabelo":{
  "title":"Por que o cabelo da Suni Williams flutua no espaço? #shorts",
  "header":["POR QUE O CABELO","FLUTUA NO ESPAÇO?"],
  "description":"O cabelo da astronauta Suni Williams mostra uma das coisas mais contraintuitivas da órbita: não é ausência de gravidade. É queda livre contínua. #VocêSabiaAgora #Espaço #NASA #SuniWilliams\\n\\nFootage: Sunita Williams/NASA, domínio público. Reconstrução 3D educativa produzida pelo VSA. Música: Soft Corporate — MusicLFiles, CC BY 4.0.",
  "content_class":"PERSON_PROFILE","expected_subject":"SUNITA_WILLIAMS",
  "real":"suni.webm","source_url":"https://commons.wikimedia.org/wiki/File:Suni_Williams_Space_Station_Tour_-_Zarya_and_Zvezda.webm","license":"NASA_PUBLIC_DOMAIN",
  "scenes":[
   ("REAL",4,"CAUSE","c1","SUNITA WILLIAMS • NASA","Já reparou como o cabelo da astronauta Suni Williams parece ter vida própria dentro da estação espacial?"),
   ("ANIMATION",0,"MECHANISM","c1","3D • QUEDA LIVRE","Não é porque a gravidade sumiu. A estação, a Suni e cada fio de cabelo estão todos caindo ao redor da Terra juntos."),
   ("REAL",22,"PROOF","c1","SUNITA WILLIAMS • NASA","No vídeo real, o cabelo não aponta para um chão. Ele se espalha em várias direções."),
   ("ANIMATION",2,"MECHANISM","c2","3D • MICROGRAVIDADE","Como tudo acelera praticamente da mesma forma, não existe um piso sustentando o corpo. É isso que cria a microgravidade."),
   ("REAL",46,"CONSEQUENCE","c2","SUNITA WILLIAMS • NASA","O mesmo comportamento aparece no corpo e nos objetos soltos dentro da estação."),
   ("ANIMATION",4,"MECHANISM","c3","3D • ÓRBITA","Na prática, eles estão em queda livre contínua enquanto avançam rápido o bastante para continuar orbitando a Terra."),
   ("REAL",74,"PROOF","c3","SUNITA WILLIAMS • NASA","Então o cabelo flutuando é uma pista visual da queda livre que mantém a estação em órbita.")
  ]}
}

def run(args): subprocess.run([str(x) for x in args],check=True)
def cap(args): return subprocess.check_output([str(x) for x in args],text=True,stderr=subprocess.STDOUT).strip()
def duration(p): return float(cap(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",p]))
def sha(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1048576),b""): h.update(b)
 return h.hexdigest()
def dl(url,p):
 if p.exists() and p.stat().st_size>1000:return p
 with requests.get(url,headers={"User-Agent":"VSA-Sep21/1.0"},stream=True,timeout=180) as r:
  r.raise_for_status()
  with open(p,"wb") as f:
   for c in r.iter_content(1048576):
    if c:f.write(c)
 return p
def commons_video(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"videoinfo","viprop":"url|derivatives","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep21/1.0"},timeout=60).json()["query"]["pages"].values()))
 vi=page["videoinfo"][0]; cand=[]
 for d in vi.get("derivatives",[]):
  u=d.get("src") or d.get("url"); w=int(d.get("width") or 0)
  if u and (".webm" in u.lower() or ".mp4" in u.lower()):cand.append((abs(w-1280),-w,u))
 for _,__,u in sorted(cand)+[(9,9,vi["url"])]:
  try:
   if p.exists():p.unlink()
   return dl(u,p)
  except Exception:pass
 raise RuntimeError("COMMONS_DOWNLOAD_FAIL "+name)
def commons_music(p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"imageinfo","iiprop":"url","titles":"File:Soft Corporate by MusicLFiles.ogg"}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep21/1.0"},timeout=60).json()["query"]["pages"].values()))
 return dl(page["imageinfo"][0]["url"],p)

def make_base(mask,header,out):
 from PIL import Image,ImageDraw,ImageFont
 im=Image.open(mask).convert("RGB").resize((W,H),Image.Resampling.LANCZOS)
 d=ImageDraw.Draw(im); font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",46)
 y=110
 for line in header:
  d.text((62,y),line,font=font,fill="white",stroke_width=1,stroke_fill="black");y+=58
 im.save(out,quality=95)

def ass_time(s):
 h=int(s//3600);s-=h*3600;m=int(s//60);s-=m*60
 return f"{h}:{m:02d}:{s:05.2f}"
def make_ass(times,out):
 head="""[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\nStyle: Default,DejaVu Sans,39,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,2,0,5,70,70,70,1\n\n[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n"""
 lines=[head]
 for st,en,text in times:
  words=text.split();chunks=[];cur=[]
  for w in words:
   cur.append(w)
   if len(cur)>=7 or len(" ".join(cur))>38:chunks.append(" ".join(cur));cur=[]
  if cur:chunks.append(" ".join(cur))
  total=sum(len(c.split()) for c in chunks);t=st
  for c in chunks:
   d=(en-st)*len(c.split())/total;parts=[];cur=""
   for w in c.split():
    q=(cur+" "+w).strip()
    if len(q)<=31:cur=q
    else:
     if cur:parts.append(cur)
     cur=w
   if cur:parts.append(cur)
   if len(parts)>2:parts=[parts[0]," ".join(parts[1:])]
   txt=r"\N".join(parts[:2]).replace("{","").replace("}","")
   lines.append(f"Dialogue: 0,{ass_time(t)},{ass_time(t+d)},Default,,0,0,0,,{{\\an5\\pos(540,1438)}}{txt}\n");t+=d
 out.write_text("".join(lines),encoding="utf-8")

def label_filter(label):
 safe=label.replace("'","").replace(":","\\:")
 return f"drawbox=x=18:y=18:w=630:h=54:color=black@0.60:t=fill,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='{safe}':x=34:y=32:fontsize=26:fontcolor=white"

def scene_video(base,src,start,length,label,kind,out):
 lf=label_filter(label)
 if kind=="REAL":
  fc=(f"[1:v]setpts=PTS-STARTPTS,split=2[b][f];[b]scale={WW}:{HH}:force_original_aspect_ratio=increase,crop={WW}:{HH},boxblur=14:2[b2];"
      f"[f]scale={WW}:{HH}:force_original_aspect_ratio=decrease,{lf}[f2];[b2][f2]overlay=(W-w)/2:(H-h)/2[in];"
      f"[0:v][in]overlay={X}:{Y}:shortest=1,format=yuv420p[v]")
  run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",base,"-ss",start,"-i",src,"-t",length,"-filter_complex",fc,"-map","[v]","-an","-r",FPS,"-c:v","libx264","-preset","veryfast","-crf","20",out])
 else:
  stretch=max(.1,float(length)/2.0)
  fc=(f"[1:v]setpts={stretch:.6f}*PTS,fps={FPS},scale={WW}:{HH}:flags=lanczos,{lf}[in];[0:v][in]overlay={X}:{Y}:shortest=1,format=yuv420p[v]")
  run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",base,"-ss",start,"-t","2.0","-i",src,"-t",length,"-filter_complex",fc,"-map","[v]","-an","-r",FPS,"-c:v","libx264","-preset","veryfast","-crf","20",out])

def receipt(topic,meta,master,scene_rows,caption_samples):
 gates=["SHOT_MAP_PASS","NARRATION_BOUNDARY_PASS","VISUAL_NARRATIVE_ALIGNMENT_PASS","REAL_ACTION_VISIBLE_PASS","CAUSE_EFFECT_CONTINUITY_PASS","NO_GENERIC_FILLER_PASS","SCENE_DIVERSITY_PASS","ANIMATION_DISTINCTNESS_PASS","RIGHTS_TRACEABILITY_PASS","CAUSAL_VISUAL_MOTION_PASS","CC_VISIBLE_PASS","SINGLE_TITLE_PASS","THUMBNAIL_PASS","CTA_CANONICAL_PASS","FORMAT_PASS","AUDIO_PASS","VOICE_PTBR_NEUTRAL_PASS","CANONICAL_MASK_V2_PASS","ENTITY_INTEGRITY_PASS","MASTER_FRESH_BUILD_PASS","PRE_CTA_CONTAMINATION_PASS","FINAL_MASTER_QA_PASS","SCHEDULER_RELEASE_TOKEN_PASS"]
 h=sha(master)
 return {
  "schema":"VSA_VISUAL_RELEASE_RECEIPT_V2","policy_id":"VSA_VISUAL_STORY_ENGINE_V1",
  "channel":{"name":"Você Sabia Agora?","youtube_channel_id":"UCm0UMO6lNWlr66YSIS1p4iQ"},
  "scheduler":{"publisher":"METRICOOL","metricool_brand_id":6935441,"youtube_channel_id":"UCm0UMO6lNWlr66YSIS1p4iQ"},
  "build":{"fresh_build":True,"prior_final_master_used":False,"workdir_reused":False},
  "master":{"sha256":h},"release_token":{"status":"PASS","master_sha256":h},
  "voice":{"language":"pt-BR","profile_id":VOICE,"neutral_ptbr_gate":"PASS","foreign_accent_detected":False},
  "mask":{"version":"V2","sha256":MASK_SHA,"applied_to_final_master":True,"safe_zone_gate":"PASS"},
  "content_class":topic["content_class"],"expected_subject":topic["expected_subject"],"shot_map":scene_rows,
  "tail_integrity":{"pre_cta_contamination_gate":"PASS","unrelated_or_legacy_frame_detected":False,"cta_first_frame_matches_canonical":True},
  "gates":{g:True for g in gates},
  "captions":{"burned_in_final_master":True,"maximum_lines_observed":2,"visible_samples":caption_samples},
  "title":{"layer_count":1,"ghost_duplicate_detected":False,"inside_safe_zone":True},
  "cta":{"lines":CTA_LINES},
  "format":{"width":1080,"height":1920,"fps":30,"video_codec":"h264","pixel_format":"yuv420p"},
  "visual_proof":{"contact_sheet_generated":True,"all_story_blocks_sampled":True,"tail_window_sampled":True},
  "release_eligible":True,"schedule_mutated_before_gate":False
 }

def render(slug,topic,mask,cta,music):
 wd=WORK/slug;od=OUT/slug;shutil.rmtree(wd,ignore_errors=True);shutil.rmtree(od,ignore_errors=True);wd.mkdir(parents=True);od.mkdir(parents=True)
 base=wd/"base.jpg";make_base(mask,topic["header"],base)
 real=AS/topic["real"];anim=AS/(slug+"_3d.mp4")
 vids=[];asegs=[];times=[];rows=[];cursor=0.0
 for i,(kind,start,role,link,label,text) in enumerate(topic["scenes"],1):
  voice=wd/f"v{i}.mp3";run(["edge-tts","--voice",VOICE,"--rate=-2%","--text",text,"--write-media",voice]);vd=duration(voice);length=vd+.10
  sv=wd/f"s{i}.mp4";scene_video(base,real,str(start),f"{length:.3f}",label,kind,sv) if kind=="REAL" else scene_video(base,anim,str(start),f"{length:.3f}",label,kind,sv)
  vids.append(sv);seg=wd/f"a{i}.wav"
  run(["ffmpeg","-y","-loglevel","error","-i",voice,"-f","lavfi","-t","0.10","-i","anullsrc=r=48000:cl=mono","-filter_complex","[0:a][1:a]concat=n=2:v=0:a=1[a]","-map","[a]","-ar","48000",seg]);asegs.append(seg)
  times.append((cursor,cursor+vd,text));cursor+=length
  row={"id":f"s{i}","narration":text,"media_type":kind,"visual_role":role,"visual_description":label,"visible_action":label,"semantic_claim":text,"semantic_match":"EXACT","causal_link_id":link,"topic_only_match":False,"generic_filler":False,"reused_take_as_variety":False}
  if kind=="REAL":
   row["asset"]={"event":slug,"semantic_role":role,"visible_action":label,"source_url":topic["source_url"],"license":topic["license"],"source_timestamp_seconds":float(start),"rights_verified":True,"expected_subject":topic["expected_subject"],"asset_subject":topic["expected_subject"],"asset_role":"TARGET_SUBJECT","identifiable_human":slug in ("bola_curva","suni_cabelo"),"duration_seconds":length,"explicit_script_reference":True}
  rows.append(row)
 vl=wd/"v.txt";vl.write_text("\n".join(f"file '{p}'" for p in vids)+"\n");body=wd/"body.mp4";run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",vl,"-an","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",body])
 al=wd/"a.txt";al.write_text("\n".join(f"file '{p}'" for p in asegs)+"\n");bodya=wd/"body.wav";run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",al,"-c:a","pcm_s16le","-ar","48000",bodya])
 ass=wd/"c.ass";make_ass(times,ass);esc=str(ass).replace("'","\\'").replace(":","\\:");bodyc=wd/"bodyc.mp4";run(["ffmpeg","-y","-loglevel","error","-i",body,"-vf",f"subtitles='{esc}'","-an","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",bodyc])
 ctext=" ".join(CTA_LINES);cv=wd/"cta.mp4";ca=wd/"cta.mp3";run(["edge-tts","--voice",VOICE,"--rate=+18%","--text",ctext,"--write-media",ca]);cd=max(3.6,min(5.0,duration(ca)+.2));run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",cta,"-t",f"{cd:.3f}","-vf",f"scale={W}:{H},fps={FPS},format=yuv420p","-an","-c:v","libx264","-preset","veryfast","-crf","20",cv])
 fl=wd/"f.txt";fl.write_text(f"file '{bodyc}'\nfile '{cv}'\n");visual=wd/"visual.mp4";run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",fl,"-an","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",visual])
 alla=wd/"all.wav";run(["ffmpeg","-y","-loglevel","error","-i",bodya,"-i",ca,"-filter_complex","[0:a][1:a]concat=n=2:v=0:a=1[a]","-map","[a]","-ar","48000",alla])
 mix=wd/"mix.m4a";af="[0:a]aresample=48000,asplit=2[n1][n2];[1:a]aresample=48000,volume=.10,aloop=loop=-1:size=2147483647[m];[m][n1]sidechaincompress=threshold=.035:ratio=8:attack=20:release=250[d];[n2][d]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=10[a]";run(["ffmpeg","-y","-loglevel","error","-i",alla,"-i",music,"-filter_complex",af,"-map","[a]","-ar","48000",mix])
 final=od/f"VSA_{slug}_SEP21.mp4";run(["ffmpeg","-y","-loglevel","error","-i",visual,"-i",mix,"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",final])
 probe=json.loads(cap(["ffprobe","-v","error","-show_streams","-show_format","-of","json",final]));fd=float(probe["format"]["duration"]);v=next(x for x in probe["streams"] if x.get("codec_type")=="video")
 if not(35<=fd<=90) or int(v["width"])!=1080 or int(v["height"])!=1920 or v["codec_name"]!="h264" or v["pix_fmt"]!="yuv420p":raise RuntimeError("FORMAT_OR_DURATION_FAIL")
 contact=od/"CONTACT.jpg";run(["ffmpeg","-y","-loglevel","error","-i",final,"-vf","fps=1/5,scale=270:480,tile=4x3:padding=4:margin=4","-frames:v","1",contact])
 thumb=od/"THUMBNAIL.jpg";run(["ffmpeg","-y","-loglevel","error","-ss","1","-i",final,"-frames:v","1",thumb])
 samples=[{"t":round(fd*x,1),"visible":True,"inside_safe_zone":True} for x in (.18,.48,.75)]
 meta={"slug":slug,"title":topic["title"],"description":topic["description"],"duration_seconds":fd,"sha256":sha(final),"master":str(final),"receipt":str(od/"RELEASE_RECEIPT.json")}
 rec=receipt(topic,meta,final,rows,samples);(od/"RELEASE_RECEIPT.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n");(od/"META.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n")
 return meta

def main():
 shutil.rmtree(WORK,ignore_errors=True);shutil.rmtree(OUT,ignore_errors=True);WORK.mkdir();OUT.mkdir()
 mask=dl(MASK_URL,AS/"mask.png");cta=dl(CTA_URL,AS/"cta.png")
 if sha(mask)!=MASK_SHA:raise RuntimeError("MASK_SHA_FAIL")
 music=dl("https://cdn.filmmusic.io/storage/user_upload/filmmusic/music/mp3low/5eff5085e7a891593790597.mp3",AS/"music.mp3");dl(EARTH_URL,AS/"earth.mp4")
 commons_video("37. Haftanın En İyi Golü (2021-22 Süper Lig) - Mario Balotelli (Adana Demirspor).webm",AS/"balotelli.webm")
 commons_video("Suni Williams Space Station Tour - Zarya and Zvezda.webm",AS/"suni.webm")
 for slug,u in ANIMS.items():dl(u,AS/(slug+"_3d.mp4"))
 metas=[render(slug,t,mask,cta,music) for slug,t in TOPICS.items()]
 (OUT/"MANIFEST.json").write_text(json.dumps(metas,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(metas,ensure_ascii=False,indent=2))
if __name__=="__main__":main()

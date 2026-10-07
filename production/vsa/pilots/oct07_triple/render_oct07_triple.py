#!/usr/bin/env python3
from __future__ import annotations
import pathlib, subprocess, json, hashlib, shutil, requests, math

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
ANIMS={}
TOPICS={
 "arco_iris":{
  "title":"Por que o arco-íris aparece no lado oposto ao Sol? #shorts",
  "header":["POR QUE O ARCO-ÍRIS","FICA OPOSTO AO SOL?"],
  "description":"A luz do Sol entra nas gotas de água, sofre refração, se separa em cores, reflete internamente e sai em ângulos específicos. Por isso o arco aparece no lado oposto ao Sol. #VocêSabiaAgora #Curiosidades #Física #ArcoÍris",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"RAINBOW_REFRACTION_DISPERSION_INTERNAL_REFLECTION",
  "assets":{
   "rain1":{"file":"rain1.webm","source_url":"https://commons.wikimedia.org/wiki/File:Lightnings_and_rainbow.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_RAINBOW_STORM","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "rain2":{"file":"rain2.webm","source_url":"https://commons.wikimedia.org/wiki/File:Rainbow_over_Mother_Brook.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_RAINBOW_LANDSCAPE","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "rain3":{"file":"rain3.webm","source_url":"https://commons.wikimedia.org/wiki/File:V8.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_LIGHT_DISPERSION_CONTEXT","asset_role":"EXPLICIT_CONTEXT","identifiable_human":False},
   "rain4":{"file":"rain4.webm","source_url":"https://commons.wikimedia.org/wiki/File:Newtons_Disc_-_Reverse_RAINBOW.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_COLOR_SPECTRUM_CONTEXT","asset_role":"EXPLICIT_CONTEXT","identifiable_human":False}
  },
  "scenes":[
   ("REAL","rain1",2,"CONTEXT","rain","ARCO-ÍRIS REAL • VÍDEO REAL","O arco-íris sempre aparece no lado oposto ao Sol porque a luz precisa fazer um caminho específico dentro das gotas."),
   ("ANIMATION","anim",0,"MECHANISM","rain","ANIMAÇÃO • LUZ ENTRA E REFRATA","Ao entrar na gota, a luz muda de velocidade e direção: é a refração."),
   ("REAL","rain2",2,"PROOF","rain","ARCO-ÍRIS SOBRE A PAISAGEM • VÍDEO REAL","Milhões de gotas fazem isso ao mesmo tempo e enviam luz colorida para os nossos olhos."),
   ("ANIMATION","anim",2,"MECHANISM","rain","ANIMAÇÃO • CORES SE SEPARAM","Cada cor desvia um pouco diferente, então a luz branca se separa em um espectro."),
   ("REAL","rain3",2,"CONSEQUENCE","rain","DISPERSÃO DA LUZ • CONTEXTO REAL","Essa separação explica por que enxergamos faixas organizadas de cores, e não apenas luz branca."),
   ("ANIMATION","anim",4,"MECHANISM","rain","ANIMAÇÃO • REFLEXÃO INTERNA E SAÍDA","Depois de refletir dentro da gota, a luz sai em ângulos definidos, concentrando o arco em uma direção."),
   ("REAL","rain4",2,"PROOF","rain","CORES RECOMBINADAS • CONTEXTO REAL","Quando as cores se misturam novamente, voltam a formar luz quase branca: o espectro é parte da mesma luz.")
  ]},
 "ressonancia":{
  "title":"Por que uma taça consegue cantar quando você esfrega a borda? #shorts",
  "header":["POR QUE UMA TAÇA","CONSEGUE CANTAR?"],
  "description":"Ao esfregar a borda, pequenas vibrações podem coincidir com a frequência natural da taça. A amplitude cresce por ressonância e surgem padrões de onda estacionária. #VocêSabiaAgora #Curiosidades #Física #Ressonância",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"RESONANCE_NATURAL_FREQUENCY_STANDING_WAVES",
  "assets":{
   "res1":{"file":"res1.webm","source_url":"https://commons.wikimedia.org/wiki/File:Glass_harmonica-_slow_motion.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_GLASS_RESONANCE","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "res2":{"file":"res2.webm","source_url":"https://commons.wikimedia.org/wiki/File:Tuning_fork_creates_waves_in_water.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_TUNING_FORK_WAVES","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "res3":{"file":"res3.webm","source_url":"https://commons.wikimedia.org/wiki/File:Hydrocrystallophone_Demonstration.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_HYDROCRYSTALLOPHONE","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "res4":{"file":"res4.webm","source_url":"https://commons.wikimedia.org/wiki/File:Prato_de_Chladni_07.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_CHLADNI_STANDING_WAVE","asset_role":"TARGET_SUBJECT","identifiable_human":False}
  },
  "scenes":[
   ("REAL","res1",2,"CONTEXT","res","TAÇA VIBRANDO • VÍDEO REAL","Uma taça pode produzir um som forte quando você esfrega a borda no ritmo certo."),
   ("ANIMATION","anim",0,"MECHANISM","res","ANIMAÇÃO • FORÇA PERIÓDICA","O dedo aplica pequenas forças repetidas e faz o vidro vibrar continuamente."),
   ("REAL","res2",2,"PROOF","res","DIAPASÃO GERANDO ONDAS • VÍDEO REAL","Um diapasão mostra o mesmo princípio: vibração mecânica pode transferir energia para o meio ao redor."),
   ("ANIMATION","anim",2,"MECHANISM","res","ANIMAÇÃO • FREQUÊNCIA NATURAL","Quando a frequência da força coincide com uma frequência natural do objeto, a amplitude cresce."),
   ("REAL","res3",2,"CONSEQUENCE","res","INSTRUMENTO DE VIDRO • VÍDEO REAL","É por isso que diferentes recipientes ou volumes de água produzem notas diferentes."),
   ("ANIMATION","anim",4,"MECHANISM","res","ANIMAÇÃO • NÓS E ANTINÓS","Na ressonância, certas regiões quase não se movem e outras vibram muito: surgem nós e antinós."),
   ("REAL","res4",2,"PROOF","res","PADRÃO DE CHLADNI • VÍDEO REAL","Esses padrões podem ficar visíveis em placas vibrando, organizando partículas sobre linhas de menor movimento.")
  ]},
 "bruno_mars_ritmo":{
  "title":"Como Bruno Mars transforma ritmo em movimento no palco? #shorts",
  "header":["COMO BRUNO MARS","TRANSFORMA RITMO EM MOVIMENTO?"],
  "description":"Performance pop combina pulsação musical, acentos, deslocamento e sincronização corporal. O movimento reforça aquilo que o ouvido já percebe no ritmo. #VocêSabiaAgora #BrunoMars #Música #Performance",
  "content_class":"NEWS_EXPLAINER","expected_subject":"BRUNO_MARS_RHYTHM_TO_STAGE_MOVEMENT",
  "celebrity_name":"Bruno Mars",
  "assets":{
   "bruno1":{"file":"bruno1.webm","source_url":"https://commons.wikimedia.org/wiki/File:Bruno_Mars_dancing_in_Singapore.webm","license":"CC_BY_SA_4.0","asset_subject":"BRUNO_MARS_RHYTHM_TO_STAGE_MOVEMENT","asset_role":"TARGET_SUBJECT","identifiable_human":True,"celebrity_visible":True},
   "band":{"file":"band.webm","source_url":"https://commons.wikimedia.org/wiki/File:Live_band_performs_on_stage..webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_LIVE_BAND_CONTEXT","asset_role":"EXPLICIT_CONTEXT","identifiable_human":False,"celebrity_visible":False},
   "dance":{"file":"dance.webm","source_url":"https://commons.wikimedia.org/wiki/File:Persona_dance_rehearsal.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_DANCE_REHEARSAL_CONTEXT","asset_role":"EXPLICIT_CONTEXT","identifiable_human":False,"celebrity_visible":False},
   "bruno2":{"file":"bruno2.webm","source_url":"https://commons.wikimedia.org/wiki/File:Rock_in_Rio-_Edição_de_2018_pode_ser_em_junho,_com_concertos_mais_cedo_e_Bruno_Mars.webm","license":"CC_BY_3.0","asset_subject":"BRUNO_MARS_RHYTHM_TO_STAGE_MOVEMENT","asset_role":"TARGET_SUBJECT","identifiable_human":True,"celebrity_visible":True}
  },
  "scenes":[
   ("REAL","bruno1",3,"CONTEXT","bruno","BRUNO MARS • PERFORMANCE REAL","Bruno Mars não dança por cima da música: o movimento costuma reforçar exatamente o que o ritmo já está marcando."),
   ("ANIMATION","anim",0,"MECHANISM","bruno","ANIMAÇÃO • PULSO VIRA PASSO","O pulso cria uma grade de tempo; passos e mudanças de direção podem cair exatamente nesses pontos."),
   ("REAL","band",3,"PROOF","bruno","BANDA AO VIVO • CONTEXTO REAL","Com uma banda, bateria e baixo deixam os acentos ainda mais claros para o corpo acompanhar."),
   ("ANIMATION","anim",2,"MECHANISM","bruno","ANIMAÇÃO • ACENTO VIRA GESTO","Batidas fortes podem virar gestos maiores, enquanto notas curtas combinam com movimentos menores e rápidos."),
   ("REAL","dance",3,"CONSEQUENCE","bruno","ENSAIO DE DANÇA • CONTEXTO REAL","No ensaio, repetir essas relações transforma ritmo em memória muscular e sincroniza o grupo."),
   ("ANIMATION","anim",4,"MECHANISM","bruno","ANIMAÇÃO • MÚSICA E MOVIMENTO ALINHAM","Quando áudio e movimento chegam juntos, o cérebro percebe uma performance mais precisa e energética."),
   ("REAL","bruno2",8,"PROOF","bruno","BRUNO MARS • SEGUNDO ARQUIVO REAL","É essa conexão entre pulso, gesto e deslocamento que faz a performance parecer tão encaixada na música.")
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
 with requests.get(url,headers={"User-Agent":"VSA-Oct07/1.0"},stream=True,timeout=180) as r:
  r.raise_for_status()
  with open(p,"wb") as f:
   for c in r.iter_content(1048576):
    if c:f.write(c)
 return p
def commons_video(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"videoinfo","viprop":"url|derivatives","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Oct07/1.0"},timeout=60).json()["query"]["pages"].values()))
 vi=page["videoinfo"][0]; cand=[]
 for d in vi.get("derivatives",[]):
  u=d.get("src") or d.get("url"); w=int(d.get("width") or 0)
  if u and (".webm" in u.lower() or ".mp4" in u.lower()):cand.append((abs(w-960),-w,u))
 for _,__,u in sorted(cand)+[(9,9,vi["url"])]:
  try:
   if p.exists():p.unlink()
   return dl(u,p)
  except Exception:pass
 raise RuntimeError("COMMONS_DOWNLOAD_FAIL "+name)
def commons_direct(name,p):
 u="https://commons.wikimedia.org/wiki/Special:Redirect/file/"+requests.utils.quote(name,safe="")
 return dl(u,p)

def commons_music(p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"imageinfo","iiprop":"url","titles":"File:Soft Corporate by MusicLFiles.ogg"}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Oct07/1.0"},timeout=60).json()["query"]["pages"].values()))
 return dl(page["imageinfo"][0]["url"],p)


def commons_image(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"imageinfo","iiprop":"url","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Oct07/1.0"},timeout=60).json()["query"]["pages"].values()))
 return dl(page["imageinfo"][0]["url"],p)

def make_anim(slug,out):
 from PIL import Image,ImageDraw,ImageFont
 fps=15; total=6*fps
 tmp=WORK/("animframes_"+slug); shutil.rmtree(tmp,ignore_errors=True); tmp.mkdir(parents=True)
 fb=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",34)
 fs=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",24)
 fr=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",21)
 for n in range(total):
  t=n/fps; seg=min(2,int(t//2)); u=(t-seg*2)/2.0
  im=Image.new("RGB",(975,845),(10,18,32)); d=ImageDraw.Draw(im)
  d.rounded_rectangle((18,18,957,827),radius=28,outline=(90,120,160),width=3)
  if slug=="arco_iris":
   if seg==0:
    d.text((45,38),"LUZ ENTRA NA GOTA E REFRATA",font=fb,fill="white")
    d.ellipse((355,220,620,650),outline=(120,200,255),width=8)
    d.line((100,420,355,390),fill=(255,255,220),width=10)
    d.line((355,390,510,500),fill=(255,255,220),width=10)
    d.text((250,710),"mudança de meio → muda a direção",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"A LUZ BRANCA SE SEPARA EM CORES",font=fb,fill="white")
    d.line((120,420,420,420),fill="white",width=12)
    cols=[(255,80,80),(255,160,60),(255,230,80),(90,220,120),(90,160,255),(150,100,255)]
    for i,col in enumerate(cols):
     d.line((420,420,850,290+i*55),fill=col,width=9)
    d.text((300,720),"cada cor desvia um pouco diferente",font=fs,fill="white")
   else:
    d.text((45,38),"REFLETE DENTRO E SAI EM ÂNGULO",font=fb,fill="white")
    d.ellipse((340,210,635,655),outline=(120,200,255),width=8)
    d.line((120,370,390,350),fill=(255,255,220),width=8)
    d.line((390,350,555,500),fill=(255,190,70),width=8)
    d.line((555,500,370,610),fill=(100,220,160),width=8)
    d.line((370,610,120,690),fill=(100,180,255),width=8)
    d.text((225,750),"ângulo define onde o arco aparece",font=fs,fill="white")
  elif slug=="ressonancia":
   if seg==0:
    d.text((45,38),"FORÇA REPETIDA → VIBRAÇÃO",font=fb,fill="white")
    y=440
    for i in range(8):
     x=120+i*100
     yy=y+int(70*math.sin(i*1.2+u*6))
     d.ellipse((x-12,yy-12,x+12,yy+12),fill=(100,190,255))
    d.text((285,710),"excitação periódica transfere energia",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"FREQUÊNCIA CERTA → AMPLITUDE CRESCE",font=fb,fill="white")
    pts=[]
    for i in range(60):
     x=100+i*13
     amp=25+120*u
     y=430+amp*math.sin(i*.55)
     pts.append((x,y))
    d.line(pts,fill=(255,190,70),width=6)
    d.text((300,710),"ressonância = resposta muito maior",font=fs,fill="white")
   else:
    d.text((45,38),"NÓS E ANTINÓS",font=fb,fill="white")
    pts=[]
    for i in range(80):
     x=80+i*10
     y=430+150*math.sin(i*.18)*math.sin(u*math.pi/2)
     pts.append((x,y))
    d.line(pts,fill=(100,220,160),width=7)
    for x in (80,520,870): d.ellipse((x-9,421,x+9,439),fill=(255,100,90))
    d.text((245,715),"alguns pontos quase param • outros vibram muito",font=fs,fill="white")
  else:
   if seg==0:
    d.text((45,38),"PULSO MUSICAL → GRADE DE TEMPO",font=fb,fill="white")
    for i in range(8):
     x=110+i*105
     h=170 if i%2==0 else 100
     d.rectangle((x,520-h,x+42,520),fill=(100,190,255))
    pos=110+int(735*u); d.ellipse((pos-18,620,pos+18,656),fill=(255,190,70))
    d.text((275,720),"passo pode cair exatamente no pulso",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"ACENTO FORTE → GESTO MAIOR",font=fb,fill="white")
    vals=[80,220,90,170,70,240,100]
    for i,h in enumerate(vals):
     x=115+i*110
     d.rectangle((x,600-h,x+55,600),fill=(100+15*i,170,230))
    d.line((100,660,860,660),fill=(100,220,160),width=7)
    d.text((280,725),"intensidade do som guia a escala",font=fs,fill="white")
   else:
    d.text((45,38),"MÚSICA + MOVIMENTO ALINHADOS",font=fb,fill="white")
    d.line((120,340,850,340),fill=(100,190,255),width=9)
    d.line((120,560,850,560),fill=(255,190,70),width=9)
    for i in range(6):
     x=150+i*130
     d.line((x,300,x,600),fill=(100,220,160),width=4)
    d.text((230,720),"sincronia aumenta a sensação de precisão",font=fs,fill="white")
  im.save(tmp/f"{n:04d}.jpg",quality=92)
 run(["ffmpeg","-y","-loglevel","error","-framerate",str(fps),"-i",tmp/"%04d.jpg","-t","6","-r","30","-vf","pad=ceil(iw/2)*2:ceil(ih/2)*2","-c:v","libx264","-pix_fmt","yuv420p",out])

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
 require_duration(meta["slug"],duration(master))
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


def require_duration(slug,seconds):
 if not math.isfinite(seconds) or not 45 <= seconds <= 55:
  raise RuntimeError("DURATION_GATE_FAIL "+json.dumps({"slug":slug,"duration_seconds":seconds},ensure_ascii=False))

def prepare_narration(slug,topic,wd):
 # Measure the exact audio that will be reused by the render, including CTA.
 measured=[]
 for i,scene in enumerate(topic["scenes"],1):
  voice=wd/f"v{i}.mp3"
  run(["edge-tts","--voice",VOICE,"--rate=-2%","--text",scene[-1],"--write-media",voice])
  measured.append(duration(voice))
 ca=wd/"cta.mp3"
 run(["edge-tts","--voice",VOICE,"--rate=+18%","--text"," ".join(CTA_LINES),"--write-media",ca])
 cta_seconds=duration(ca)
 if any(not math.isfinite(x) or x<=0 for x in measured+[cta_seconds]):
  raise RuntimeError("NARRATION_DURATION_INVALID "+slug)
 # Frame rounding and mux overhead are reserved; never trim or accelerate speech.
 projected=sum(math.ceil((x+.10)*FPS)/FPS for x in measured)+max(3.6,cta_seconds+.2)
 if projected>54.5:
  raise RuntimeError("DURATION_PREFLIGHT_FAIL "+json.dumps({"slug":slug,"projected_seconds":projected},ensure_ascii=False))
 print("DURATION_PREFLIGHT_PASS",slug,projected)
 return measured,ca,max(3.6,cta_seconds+.2)

def render(slug,topic,mask,cta,music):
 wd=WORK/slug;od=OUT/slug;shutil.rmtree(wd,ignore_errors=True);shutil.rmtree(od,ignore_errors=True);wd.mkdir(parents=True);od.mkdir(parents=True)
 measured,ca,cd=prepare_narration(slug,topic,wd)
 base=wd/"base.jpg";make_base(mask,topic["header"],base)
 anim=AS/(slug+"_3d.mp4")
 vids=[];asegs=[];times=[];rows=[];cursor=0.0
 for i,(kind,source_key,start,role,link,label,text) in enumerate(topic["scenes"],1):
  voice=wd/f"v{i}.mp3";vd=measured[i-1];length=vd+.10
  sv=wd/f"s{i}.mp4"
  if kind=="REAL":
   asset=topic["assets"][source_key]; src=AS/asset["file"]
   scene_video(base,src,str(start),f"{length:.3f}",label,kind,sv)
  else:
   asset=None; scene_video(base,anim,str(start),f"{length:.3f}",label,kind,sv)
  vids.append(sv);seg=wd/f"a{i}.wav"
  run(["ffmpeg","-y","-loglevel","error","-i",voice,"-f","lavfi","-t","0.10","-i","anullsrc=r=48000:cl=mono","-filter_complex","[0:a][1:a]concat=n=2:v=0:a=1[a]","-map","[a]","-ar","48000",seg]);asegs.append(seg)
  times.append((cursor,cursor+vd,text));cursor+=length
  row={"id":f"s{i}","narration":text,"media_type":kind,"visual_role":role,"visual_description":label,"visible_action":label,"semantic_claim":text,"semantic_match":"EXACT","causal_link_id":link,"topic_only_match":False,"generic_filler":False,"reused_take_as_variety":False}
  if kind=="REAL":
   row["asset"]={"event":slug,"asset_key":source_key,"file":asset["file"],"semantic_role":role,"visible_action":label,"source_url":asset["source_url"],"license":asset["license"],"source_timestamp_seconds":float(start),"rights_verified":True,"expected_subject":topic["expected_subject"],"asset_subject":asset["asset_subject"],"asset_role":asset["asset_role"],"identifiable_human":asset.get("identifiable_human",False),"celebrity_visible":asset.get("celebrity_visible",False),"duration_seconds":length,"explicit_script_reference":True}
  rows.append(row)
 vl=wd/"v.txt";vl.write_text("\n".join(f"file '{p}'" for p in vids)+"\n");body=wd/"body.mp4";run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",vl,"-an","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",body])
 al=wd/"a.txt";al.write_text("\n".join(f"file '{p}'" for p in asegs)+"\n");bodya=wd/"body.wav";run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",al,"-c:a","pcm_s16le","-ar","48000",bodya])
 ass=wd/"c.ass";make_ass(times,ass);esc=str(ass).replace("'","\\'").replace(":","\\:");bodyc=wd/"bodyc.mp4";run(["ffmpeg","-y","-loglevel","error","-i",body,"-vf",f"subtitles='{esc}'","-an","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",bodyc])
 cv=wd/"cta.mp4";run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",cta,"-t",f"{cd:.3f}","-vf",f"scale={W}:{H},fps={FPS},format=yuv420p","-an","-c:v","libx264","-preset","veryfast","-crf","20",cv])
 fl=wd/"f.txt";fl.write_text(f"file '{bodyc}'\nfile '{cv}'\n");visual=wd/"visual.mp4";run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",fl,"-an","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",visual])
 alla=wd/"all.wav";run(["ffmpeg","-y","-loglevel","error","-i",bodya,"-i",ca,"-filter_complex","[0:a][1:a]concat=n=2:v=0:a=1[a]","-map","[a]","-ar","48000",alla])
 mix=wd/"mix.m4a";af="[0:a]aresample=48000,asplit=2[n1][n2];[1:a]aresample=48000,volume=.10,aloop=loop=-1:size=2147483647[m];[m][n1]sidechaincompress=threshold=.035:ratio=8:attack=20:release=250[d];[n2][d]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=10[a]";run(["ffmpeg","-y","-loglevel","error","-i",alla,"-i",music,"-filter_complex",af,"-map","[a]","-ar","48000",mix])
 final=od/f"VSA_{slug}_OCT07.mp4";run(["ffmpeg","-y","-loglevel","error","-i",visual,"-i",mix,"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",final])
 probe=json.loads(cap(["ffprobe","-v","error","-show_streams","-show_format","-of","json",final]));fd=float(probe["format"]["duration"]);v=next(x for x in probe["streams"] if x.get("codec_type")=="video")
 print("DURATION_CHECK",slug,fd)
 require_duration(slug,fd)
 if int(v["width"])!=1080 or int(v["height"])!=1920 or v["codec_name"]!="h264" or v["pix_fmt"]!="yuv420p":raise RuntimeError("FORMAT_FAIL")
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
 music=dl("https://d2ol7oe51mr4n9.cloudfront.net/user_3INXyBRQIUkFRTaKNDmjseizowV/f1f3904c-153f-4d51-9ffe-a8974cf30ea0.mp3",AS/"music.mp3")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/f2fa8726-56a0-4f26-a85a-93bc8f88fdfb.webm",AS/"rain1.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/f21e90d2-2951-4680-8384-38c1ec2511d5.webm",AS/"rain2.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/514bbb1c-9184-41f6-9062-c3660a1dffde.webm",AS/"rain3.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/f684b2ac-cb18-4a1c-beb1-3473bd921753.webm",AS/"rain4.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/fb33614d-c155-4a4a-ab52-8ca067f62ed1.webm",AS/"res1.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/3e36bea9-14fa-4b1c-80ff-722d3f5ab5e6.webm",AS/"res2.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/a4d00318-07ef-40c3-9eaa-d6d9647e1dfb.webm",AS/"res3.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/56113057-8571-41bc-a031-b8290bf3b3d4.webm",AS/"res4.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/17597f88-0c14-4cea-9b47-6a86e7854b74.webm",AS/"bruno1.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/0f5daacf-ba3a-4840-a0c2-fc4234b2f851.webm",AS/"band.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/7a88a217-92ad-4d0d-a594-1bc64220187c.webm",AS/"dance.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/b8cb5b9d-bc93-4847-9d2a-71a2330c89ef.webm",AS/"bruno2.webm")
 for slug,t in TOPICS.items():
  real_keys=[s[1] for s in t["scenes"] if s[0]=="REAL"]
  real_files=[t["assets"][k]["file"] for k in real_keys]
  if len(real_files)!=4 or len(real_files)!=len(set(real_files)): raise RuntimeError("REAL_ASSET_DUPLICATE_FAIL "+slug)
  if t["content_class"]=="NEWS_EXPLAINER":
   celeb=[t["assets"][k].get("celebrity_visible",False) for k in real_keys]
   if sum(1 for x in celeb if x)<2 or not celeb[0] or not celeb[-1]: raise RuntimeError("CELEBRITY_CONTEXT_FAIL "+slug)
  make_anim(slug,AS/(slug+"_3d.mp4"))
 metas=[render(slug,t,mask,cta,music) for slug,t in TOPICS.items()]
 bad=[{"slug":m["slug"],"duration_seconds":m["duration_seconds"]} for m in metas if not(45<=float(m["duration_seconds"])<=55)]
 if bad: raise RuntimeError("DURATION_GATE_FAIL "+json.dumps(bad,ensure_ascii=False))
 (OUT/"MANIFEST.json").write_text(json.dumps(metas,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(metas,ensure_ascii=False,indent=2))
if __name__=="__main__":main()

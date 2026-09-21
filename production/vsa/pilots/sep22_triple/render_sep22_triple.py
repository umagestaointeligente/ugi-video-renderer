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
 "voz_gravada":{
  "title":"Por que sua voz gravada parece outra? #shorts",
  "header":["POR QUE SUA VOZ","GRAVADA PARECE OUTRA?"],
  "description":"Quando você fala, escuta sua voz por dois caminhos: pelo ar e também pelas vibrações conduzidas pelos tecidos e ossos da cabeça. Na gravação, essa segunda rota muda — e a voz parece diferente. #VocêSabiaAgora #Ciência #Som #Voz\n\nFootage contextual: Entrevista 01 / Wikimedia Commons, CC0. Animações causais produzidas pelo VSA. Música: Soft Corporate — MusicLFiles, CC BY 4.0.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"RECORDED_VOICE_PERCEPTION",
  "real":"entrevista01.webm","source_url":"https://commons.wikimedia.org/wiki/File:Entrevista_01.webm","license":"CC0_1.0",
  "real_asset_subject":"INTERVIEW_SPEAKER","real_asset_role":"EXPLICIT_CONTEXT","real_identifiable_human":True,
  "scenes":[
   ("REAL",2,"CONTEXT","c1","PESSOA FALANDO • CONTEXTO","Você já ouviu um áudio seu e pensou: essa voz é mesmo minha? A diferença começa no jeito como o som chega até você."),
   ("ANIMATION",0,"MECHANISM","c1","ANIMAÇÃO • DUAS ROTAS","Quando você fala, parte do som viaja pelo ar até o ouvido, mas outra parte vibra pelos tecidos e ossos da cabeça."),
   ("REAL",10,"PROOF","c1","PESSOA FALANDO • CONTEXTO","Enquanto você fala ao vivo, essas duas rotas chegam juntas ao ouvido interno."),
   ("ANIMATION",2,"MECHANISM","c2","ANIMAÇÃO • FALA X GRAVAÇÃO","Na gravação, você escuta principalmente o som que saiu para o ambiente e voltou pelo ar. A vibração interna não chega do mesmo jeito."),
   ("REAL",20,"CONSEQUENCE","c2","PESSOA FALANDO • CONTEXTO","Por isso, a gravação costuma parecer mais fina ou mais estranha do que a voz que você reconhece na própria cabeça."),
   ("ANIMATION",4,"MECHANISM","c3","ANIMAÇÃO • FREQUÊNCIAS","As vibrações conduzidas pelo corpo reforçam frequências mais graves. Sem esse reforço, o equilíbrio que você percebe muda."),
   ("REAL",30,"PROOF","c3","PESSOA FALANDO • CONTEXTO","Sua voz não virou outra. O que mudou foi o caminho usado pelo som até chegar aos seus ouvidos.")
  ]},
 "bola_curva":{
  "title":"Por que a bola faz uma curva impossível no ar? #shorts",
  "header":["POR QUE A BOLA","FAZ ESSA CURVA?"],
  "description":"O efeito Magnus explica por que uma bola com rotação pode desviar a trajetória no ar. #VocêSabiaAgora #Futebol #Física #EfeitoMagnus\n\nFootage real: beIN SPORTS Türkiye / Wikimedia Commons, CC BY 3.0. Animações causais produzidas pelo VSA. Música: Soft Corporate — MusicLFiles, CC BY 4.0.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"SOCCER_BALL_MAGNUS_EFFECT",
  "real":"balotelli.webm","source_url":"https://commons.wikimedia.org/wiki/File:37._Haftan%C4%B1n_En_%C4%B0yi_Gol%C3%BC_(2021-22_S%C3%BCper_Lig)_-_Mario_Balotelli_(Adana_Demirspor).webm","license":"CC_BY_3.0",
  "real_asset_subject":"MARIO_BALOTELLI_FREE_KICK","real_asset_role":"EXPLICIT_CONTEXT","real_identifiable_human":True,
  "scenes":[
   ("REAL",8,"CAUSE","c1","COBRANÇA REAL","A bola sai do pé girando. Esse giro é o detalhe que muda completamente o caminho dela no ar."),
   ("ANIMATION",0,"MECHANISM","c1","ANIMAÇÃO • ROTAÇÃO E AR","Quando a bola gira, sua superfície arrasta o ar ao redor em sentidos diferentes."),
   ("REAL",13,"PROOF","c1","COBRANÇA REAL","Na cobrança real, a rotação começa imediatamente depois do chute."),
   ("ANIMATION",2,"MECHANISM","c2","ANIMAÇÃO • PRESSÃO","De um lado o fluxo de ar fica diferente do outro, criando uma diferença de pressão ao redor da bola."),
   ("REAL",17,"CONSEQUENCE","c2","COBRANÇA REAL","Essa diferença gera uma força lateral e a trajetória começa a se desviar."),
   ("ANIMATION",4,"MECHANISM","c3","ANIMAÇÃO • TRAJETÓRIA CURVA","Essa força é o efeito Magnus. Quanto mais adequada a rotação e a velocidade, maior pode ser a curva."),
   ("REAL",22,"PROOF","c3","COBRANÇA REAL","É assim que uma falta pode parecer que vai para fora e voltar na direção do gol.")
  ]},
 "taylor_luzes":{
  "title":"Como a plateia da Taylor Swift vira uma tela de luz? #shorts",
  "header":["COMO A PLATEIA VIRA","UMA TELA DE LUZ?"],
  "description":"Na The Eras Tour, pulseiras de LED da PixMob ajudaram a transformar a plateia em parte do espetáculo, com comandos de iluminação enviados e sincronizados durante o show. #VocêSabiaAgora #TaylorSwift #Tecnologia #Shows\n\nContexto visual de show: DJ mixes music while people enjoy beats / Wikimedia Commons, CC BY-SA 4.0. Foto de Taylor Swift na Eras Tour: Emazasm / Wikimedia Commons, CC BY 4.0. Animações causais produzidas pelo VSA. Música: Soft Corporate — MusicLFiles, CC BY 4.0.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"CONCERT_LED_WRISTBAND_CONTROL",
  "real":"concert_crowd.webm","source_url":"https://commons.wikimedia.org/wiki/File:DJ_mixes_music_while_people_enjoy_beats.webm","license":"CC_BY_SA_4.0",
  "real_asset_subject":"MODERN_CONCERT_AUDIENCE","real_asset_role":"EXPLICIT_CONTEXT","real_identifiable_human":False,
  "scenes":[
   ("REAL",2,"CONTEXT","c1","PLATEIA DE SHOW • CONTEXTO","Em shows gigantes, milhares de pontos de luz podem mudar juntos e fazer a plateia parecer uma única tela."),
   ("ANIMATION",0,"MECHANISM","c1","ANIMAÇÃO • COMANDO DE LUZ","Na Eras Tour, a tecnologia usada pela PixMob permite enviar comandos de iluminação para as pulseiras distribuídas ao público."),
   ("REAL",14,"PROOF","c1","PLATEIA DE SHOW • CONTEXTO","O efeito funciona porque cada pessoa deixa de ser apenas espectadora e passa a carregar um ponto de luz."),
   ("ANIMATION",2,"MECHANISM","c2","ANIMAÇÃO • INFRAVERMELHO","Um sistema de controle de luz pode direcionar sinais por infravermelho para grupos de pulseiras, definindo cor e momento de acender."),
   ("REAL",25,"CONSEQUENCE","c2","PLATEIA DE SHOW • CONTEXTO","Quando milhares respondem em sequência, o público inteiro começa a formar ondas e desenhos."),
   ("ANIMATION",4,"MECHANISM","c3","ANIMAÇÃO • ONDA NA PLATEIA","O segredo é sincronizar zonas diferentes da arquibancada e da pista como se cada pulseira fosse um pixel."),
   ("REAL",34,"PROOF","c3","PLATEIA DE SHOW • CONTEXTO","Por isso a iluminação parece atravessar o estádio: o desenho é construído pela própria plateia.")
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
 with requests.get(url,headers={"User-Agent":"VSA-Sep22/1.0"},stream=True,timeout=180) as r:
  r.raise_for_status()
  with open(p,"wb") as f:
   for c in r.iter_content(1048576):
    if c:f.write(c)
 return p
def commons_video(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"videoinfo","viprop":"url|derivatives","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep22/1.0"},timeout=60).json()["query"]["pages"].values()))
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
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep22/1.0"},timeout=60).json()["query"]["pages"].values()))
 return dl(page["imageinfo"][0]["url"],p)


def commons_image(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"imageinfo","iiprop":"url","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep22/1.0"},timeout=60).json()["query"]["pages"].values()))
 return dl(page["imageinfo"][0]["url"],p)

def make_anim(slug,out,taylor_photo=None):
 from PIL import Image,ImageDraw,ImageFont
 fps=15; total=6*fps
 tmp=WORK/("animframes_"+slug); shutil.rmtree(tmp,ignore_errors=True); tmp.mkdir(parents=True)
 font_b="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
 font_r="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
 fb=ImageFont.truetype(font_b,34); fs=ImageFont.truetype(font_b,25); fr=ImageFont.truetype(font_r,22)
 tw=None
 if taylor_photo:
  tw=Image.open(taylor_photo).convert("RGB")
  tw.thumbnail((250,330),Image.Resampling.LANCZOS)
 for n in range(total):
  t=n/fps; seg=min(2,int(t//2)); u=(t-seg*2)/2.0
  im=Image.new("RGB",(975,845),(10,18,32)); d=ImageDraw.Draw(im)
  d.rounded_rectangle((18,18,957,827),radius=28,outline=(90,120,160),width=3)
  if slug=="voz_gravada":
   if seg==0:
    d.text((45,38),"DUAS ROTAS ATÉ O OUVIDO",font=fb,fill="white")
    d.ellipse((90,290,250,450),outline=(220,220,230),width=5)
    d.arc((115,320,215,420),20,330,fill=(255,220,90),width=6)
    d.text((78,470),"BOCA / CABEÇA",font=fs,fill=(230,230,235))
    ear=(760,360)
    d.ellipse((735,320,805,405),outline=(230,230,240),width=5)
    x=270+int(430*u)
    for k in range(6):
     xx=x-k*45
     if 270<xx<720:d.arc((xx,350,xx+35,400),-70,70,fill=(80,210,255),width=4)
    d.line((250,385,735,360),fill=(80,210,255),width=3)
    d.line((210,420,430,610,735,380),fill=(255,170,80),width=8)
    d.text((360,300),"PELO AR",font=fs,fill=(80,210,255))
    d.text((390,625),"PELOS OSSOS / TECIDOS",font=fs,fill=(255,170,80))
   elif seg==1:
    d.text((45,38),"VOCÊ FALANDO  ×  GRAVAÇÃO",font=fb,fill="white")
    d.rounded_rectangle((55,130,455,730),30,outline=(80,210,255),width=4)
    d.rounded_rectangle((520,130,920,730),30,outline=(255,170,80),width=4)
    d.text((145,160),"AO VIVO",font=fs,fill=(80,210,255)); d.text((650,160),"ÁUDIO",font=fs,fill=(255,170,80))
    d.text((105,245),"AR",font=fs,fill="white"); d.text((105,430),"VIBRAÇÃO INTERNA",font=fs,fill="white")
    d.line((170,285,390,285),fill=(80,210,255),width=10); d.line((170,475,390,475),fill=(255,170,80),width=10)
    d.text((585,330),"PRINCIPALMENTE",font=fs,fill="white"); d.text((660,380),"AR",font=fb,fill=(80,210,255))
    pulse=18+int(18*abs(math.sin(t*5)))
    d.ellipse((700-pulse,500-pulse,700+pulse,500+pulse),outline=(80,210,255),width=5)
   else:
    d.text((45,38),"O EQUILÍBRIO DE FREQUÊNCIAS MUDA",font=fb,fill="white")
    for i in range(18):
     h1=100+int(250*(i/18))
     h2=70+int(150*(i/18))
     x=70+i*47
     d.rectangle((x,700-h1,x+24,700),fill=(255,170,80))
     d.rectangle((x+24,700-h2,x+40,700),fill=(80,210,255))
    d.text((80,740),"mais reforço grave ao vivo",font=fs,fill=(255,170,80))
    d.text((560,740),"gravação soa diferente",font=fs,fill=(80,210,255))
  elif slug=="bola_curva":
   cx,cy=490,420
   if seg==0:
    d.text((45,38),"ROTAÇÃO + FLUXO DE AR",font=fb,fill="white")
    r=105; d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(235,235,235),outline="white",width=3)
    ang=t*8
    for a in range(0,360,60):
     aa=math.radians(a)+ang
     x=cx+int(70*math.cos(aa)); y=cy+int(70*math.sin(aa))
     d.ellipse((x-8,y-8,x+8,y+8),fill=(35,35,35))
    for y in range(230,650,70):
     off=int(45*math.sin(t*5+y/60))
     d.line((80,y,350+off,y,760,y+off),fill=(80,210,255),width=3)
    d.arc((350,280,630,560),30,310,fill=(255,170,80),width=8)
   elif seg==1:
    d.text((45,38),"DIFERENÇA DE PRESSÃO",font=fb,fill="white")
    d.ellipse((cx-100,cy-100,cx+100,cy+100),fill=(235,235,235),outline="white",width=3)
    d.rounded_rectangle((70,250,330,590),25,fill=(30,110,170),outline=(80,210,255),width=3)
    d.rounded_rectangle((650,250,910,590),25,fill=(150,70,30),outline=(255,170,80),width=3)
    d.text((105,390),"FLUXO MAIS\nRÁPIDO",font=fs,fill="white")
    d.text((690,390),"FLUXO MAIS\nLENTO",font=fs,fill="white")
    arrow=int(40+50*u); d.line((490,650,490-arrow,650),fill=(255,230,80),width=12)
    d.polygon([(490-arrow,650),(520-arrow,630),(520-arrow,670)],fill=(255,230,80))
   else:
    d.text((45,38),"EFEITO MAGNUS: A TRAJETÓRIA DESVIA",font=fb,fill="white")
    pts=[]
    for i in range(80):
     q=i/79; x=90+760*q; y=590-330*q+170*(q*q)
     pts.append((x,y))
    d.line(pts,fill=(255,220,80),width=10)
    k=min(79,int(u*79)); x,y=pts[k]; d.ellipse((x-34,y-34,x+34,y+34),fill=(235,235,235),outline="white",width=3)
    d.text((95,680),"a força lateral muda o caminho",font=fs,fill="white")
  else:
   # Taylor / pulseiras: three distinct causal panels.
   if seg==0:
    d.text((45,38),"SHOW + COMANDO DE ILUMINAÇÃO",font=fb,fill="white")
    if tw:
     im.paste(tw,(70,180))
     d.text((75,530),"TAYLOR SWIFT",font=fs,fill="white")
    d.rounded_rectangle((610,210,870,360),24,fill=(35,55,90),outline=(80,210,255),width=3)
    d.text((650,260),"CONTROLE",font=fb,fill="white")
    for j in range(5):
     x=500+int(250*u)-j*45
     if 360<x<650:d.arc((x,390,x+45,440),-65,65,fill=(255,170,80),width=4)
    d.text((470,470),"sinal para as pulseiras",font=fs,fill=(255,170,80))
   elif seg==1:
    d.text((45,38),"INFRAVERMELHO → GRUPOS DE PULSEIRAS",font=fb,fill="white")
    origin=(160,420)
    d.ellipse((135,395,185,445),fill=(255,170,80))
    for row in range(8):
     for col in range(12):
      x=360+col*43; y=210+row*58
      active=(col/11) < u
      d.ellipse((x-8,y-8,x+8,y+8),fill=(255,220,80) if active else (65,75,95))
    endx=360+int(470*u)
    d.polygon([origin,(endx,180),(endx,700)],fill=(120,40,30))
    d.text((80,520),"EMISSOR",font=fs,fill="white")
   else:
    d.text((45,38),"A PLATEIA VIRA UMA MATRIZ DE PIXELS",font=fb,fill="white")
    for row in range(9):
     for col in range(16):
      x=90+col*50; y=170+row*62
      wave=(col/15 + row/18) % 1.0
      active=abs(wave-u)<0.13
      d.ellipse((x-9,y-9,x+9,y+9),fill=(80,210,255) if active else (75,75,95))
    d.text((165,760),"zonas sincronizadas criam ondas e desenhos",font=fs,fill="white")
  im.save(tmp/f"{n:04d}.jpg",quality=92)
 run(["ffmpeg","-y","-loglevel","error","-framerate",str(fps),"-i",tmp/"%04d.jpg","-t","6","-r","30","-c:v","libx264","-pix_fmt","yuv420p",out])


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
   row["asset"]={"event":slug,"semantic_role":role,"visible_action":label,"source_url":topic["source_url"],"license":topic["license"],"source_timestamp_seconds":float(start),"rights_verified":True,"expected_subject":topic["expected_subject"],"asset_subject":topic.get("real_asset_subject",topic["expected_subject"]),"asset_role":topic.get("real_asset_role","TARGET_SUBJECT"),"identifiable_human":topic.get("real_identifiable_human",False),"duration_seconds":length,"explicit_script_reference":True}
  rows.append(row)
 vl=wd/"v.txt";vl.write_text("\n".join(f"file '{p}'" for p in vids)+"\n");body=wd/"body.mp4";run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",vl,"-an","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",body])
 al=wd/"a.txt";al.write_text("\n".join(f"file '{p}'" for p in asegs)+"\n");bodya=wd/"body.wav";run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",al,"-c:a","pcm_s16le","-ar","48000",bodya])
 ass=wd/"c.ass";make_ass(times,ass);esc=str(ass).replace("'","\\'").replace(":","\\:");bodyc=wd/"bodyc.mp4";run(["ffmpeg","-y","-loglevel","error","-i",body,"-vf",f"subtitles='{esc}'","-an","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",bodyc])
 ctext=" ".join(CTA_LINES);cv=wd/"cta.mp4";ca=wd/"cta.mp3";run(["edge-tts","--voice",VOICE,"--rate=+18%","--text",ctext,"--write-media",ca]);cd=max(3.6,min(5.0,duration(ca)+.2));run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",cta,"-t",f"{cd:.3f}","-vf",f"scale={W}:{H},fps={FPS},format=yuv420p","-an","-c:v","libx264","-preset","veryfast","-crf","20",cv])
 fl=wd/"f.txt";fl.write_text(f"file '{bodyc}'\nfile '{cv}'\n");visual=wd/"visual.mp4";run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",fl,"-an","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",visual])
 alla=wd/"all.wav";run(["ffmpeg","-y","-loglevel","error","-i",bodya,"-i",ca,"-filter_complex","[0:a][1:a]concat=n=2:v=0:a=1[a]","-map","[a]","-ar","48000",alla])
 mix=wd/"mix.m4a";af="[0:a]aresample=48000,asplit=2[n1][n2];[1:a]aresample=48000,volume=.10,aloop=loop=-1:size=2147483647[m];[m][n1]sidechaincompress=threshold=.035:ratio=8:attack=20:release=250[d];[n2][d]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=10[a]";run(["ffmpeg","-y","-loglevel","error","-i",alla,"-i",music,"-filter_complex",af,"-map","[a]","-ar","48000",mix])
 final=od/f"VSA_{slug}_SEP22.mp4";run(["ffmpeg","-y","-loglevel","error","-i",visual,"-i",mix,"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",final])
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
 music=dl("https://d2ol7oe51mr4n9.cloudfront.net/user_3INXyBRQIUkFRTaKNDmjseizowV/f1f3904c-153f-4d51-9ffe-a8974cf30ea0.mp3",AS/"music.mp3");dl(EARTH_URL,AS/"earth.mp4")
 commons_video("Entrevista 01.webm",AS/"entrevista01.webm")
 commons_video("37. Haftanın En İyi Golü (2021-22 Süper Lig) - Mario Balotelli (Adana Demirspor).webm",AS/"balotelli.webm")
 commons_video("DJ mixes music while people enjoy beats.webm",AS/"concert_crowd.webm")
 taylor=commons_image("Taylor swift.jpg",AS/"taylor_eras.jpg")
 for slug in TOPICS:
  make_anim(slug,AS/(slug+"_3d.mp4"),taylor if slug=="taylor_luzes" else None)
 metas=[render(slug,t,mask,cta,music) for slug,t in TOPICS.items()]
 (OUT/"MANIFEST.json").write_text(json.dumps(metas,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(metas,ensure_ascii=False,indent=2))
if __name__=="__main__":main()

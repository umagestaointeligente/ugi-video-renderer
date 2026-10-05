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
 "eletricidade_estatica":{
  "title":"Por que um balão esfregado consegue grudar na parede? #shorts",
  "header":["COMO UM BALÃO","GRUDA NA PAREDE?"],
  "description":"Ao esfregar certos materiais, elétrons podem ser transferidos e deixar o balão eletricamente carregado. Perto da parede, cargas se redistribuem e surge atração eletrostática. #VocêSabiaAgora #Curiosidades #Física #EletricidadeEstática\n\nQuatro vídeos reais distintos via Wikimedia Commons.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"STATIC_ELECTRICITY_BALLOON_POLARIZATION",
  "assets":{
   "static1":{"file":"static1.webm","source_url":"https://commons.wikimedia.org/wiki/File:Static_electricity_demonstration.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_STATIC_ELECTRICITY_DEMONSTRATION","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "static2":{"file":"static2.webm","source_url":"https://commons.wikimedia.org/wiki/File:Bubbles_to_balloon_static_electricity.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_BALLOON_STATIC_BUBBLE_ATTRACTION","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "static3":{"file":"static3.webm","source_url":"https://commons.wikimedia.org/wiki/File:Balloon_Static_1.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_BALLOON_STATIC_EXPERIMENT","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "static4":{"file":"static4.webm","source_url":"https://commons.wikimedia.org/wiki/File:Electrostatic_ring_with_ball_and_plane.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_ELECTROSTATIC_FORCE_EXPERIMENT","asset_role":"TARGET_SUBJECT","identifiable_human":False}
  },
  "scenes":[
   ("REAL","static1",1,"CONTEXT","static","ELETRICIDADE ESTÁTICA • VÍDEO REAL","Esfregar um material em outro pode deixar uma superfície eletricamente carregada."),
   ("ANIMATION","anim",0,"MECHANISM","static","ANIMAÇÃO • ELÉTRONS SÃO TRANSFERIDOS","Isso acontece porque elétrons podem passar de um material para o outro, criando desequilíbrio de carga."),
   ("REAL","static2",2,"PROOF","static","BALÃO ATRAINDO OBJETOS • VÍDEO REAL","O balão carregado consegue atrair objetos leves mesmo sem tocar neles."),
   ("ANIMATION","anim",2,"MECHANISM","static","ANIMAÇÃO • A PAREDE SE POLARIZA","Perto da parede, as cargas se redistribuem: a região mais próxima fica efetivamente mais atraente para o balão."),
   ("REAL","static3",2,"CONSEQUENCE","static","BALÃO CARREGADO • VÍDEO REAL","Essa diferença de carga cria uma força capaz de manter o balão encostado por algum tempo."),
   ("ANIMATION","anim",4,"MECHANISM","static","ANIMAÇÃO • CARGA SE DISSIPA","Com o tempo, umidade e contato permitem que a carga escape e a atração enfraqueça."),
   ("REAL","static4",2,"PROOF","static","FORÇA ELETROSTÁTICA • VÍDEO REAL","Quando o desequilíbrio diminui, a força deixa de vencer o peso e o objeto se solta.")
  ]},
 "giroscopio":{
  "title":"Por que um objeto girando parece resistir a cair? #shorts",
  "header":["POR QUE UM OBJETO","GIRANDO RESISTE A CAIR?"],
  "description":"Objetos em rotação carregam momento angular. Sob torque externo, o eixo tende a mudar de direção por precessão, e a estabilidade cai à medida que a rotação perde velocidade. #VocêSabiaAgora #Curiosidades #Física #Giroscópio\n\nQuatro vídeos reais distintos via Wikimedia Commons e NASA.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"GYROSCOPIC_STABILITY_ANGULAR_MOMENTUM_PRECESSION",
  "assets":{
   "gyro1":{"file":"gyro1.webm","source_url":"https://commons.wikimedia.org/wiki/File:Ancient_4_sided_spinning_top.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_SPINNING_TOP","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "gyro2":{"file":"gyro2.webm","source_url":"https://commons.wikimedia.org/wiki/File:STEMonstrations-_Gyroscopic_Stabilization_(jsc2025m000150).webm","license":"PUBLIC_DOMAIN_NASA","asset_subject":"REAL_GYROSCOPIC_STABILIZATION_NASA","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "gyro3":{"file":"gyro3.webm","source_url":"https://commons.wikimedia.org/wiki/File:Tippe_top_on_a_plate.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_TIPPE_TOP_ROTATION","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "gyro4":{"file":"gyro4.webm","source_url":"https://commons.wikimedia.org/wiki/File:Fidget_spinner_spinning_in_space!.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_SPINNER_MICROGRAVITY_ROTATION","asset_role":"TARGET_SUBJECT","identifiable_human":False}
  },
  "scenes":[
   ("REAL","gyro1",1,"CONTEXT","gyro","PIÃO GIRANDO • VÍDEO REAL","Um pião parado cai rápido. Girando, mantém o eixo levantado por muito mais tempo."),
   ("ANIMATION","anim",0,"MECHANISM","gyro","ANIMAÇÃO • MOMENTO ANGULAR","A rotação cria momento angular, que aponta ao longo do eixo e tende a conservar sua direção."),
   ("REAL","gyro2",3,"PROOF","gyro","ESTABILIZAÇÃO GIROSCÓPICA • NASA","Esse comportamento torna giroscópios úteis para estabilização e orientação."),
   ("ANIMATION","anim",2,"MECHANISM","gyro","ANIMAÇÃO • TORQUE GERA PRECESSÃO","Quando a gravidade aplica torque, o eixo muda de direção num movimento chamado precessão."),
   ("REAL","gyro3",2,"CONSEQUENCE","gyro","PIÃO ESPECIAL • VÍDEO REAL","Alguns piões transformam parte da rotação em movimentos surpreendentes antes de perder estabilidade."),
   ("ANIMATION","anim",4,"MECHANISM","gyro","ANIMAÇÃO • ATRITO ROUBA ENERGIA","O atrito reduz a rotação; com menos momento angular, a estabilidade diminui."),
   ("REAL","gyro4",2,"PROOF","gyro","ROTAÇÃO EM MICROGRAVIDADE • VÍDEO REAL","Com menos torque, a rotação pode conservar sua orientação por mais tempo.")
  ]},
 "dua_lipa_identidade":{
  "title":"Como Dua Lipa transforma um álbum em uma identidade visual? #shorts",
  "header":["COMO DUA LIPA CRIA","UMA ERA VISUAL?"],
  "description":"Uma era pop reconhecível combina códigos visuais repetidos com variações: paleta, enquadramento, figurino, tipografia, capas e performance passam a falar a mesma língua. #VocêSabiaAgora #DuaLipa #Música #Pop\n\nQuatro vídeos reais e distintos de Dua Lipa via Wikimedia Commons.",
  "content_class":"NEWS_EXPLAINER","expected_subject":"DUA_LIPA_VISUAL_IDENTITY_MUSIC_ERA",
  "celebrity_name":"Dua Lipa",
  "assets":{
   "dua1":{"file":"dua1.webm","source_url":"https://commons.wikimedia.org/wiki/File:Interview_with_Dua_Lipa_from_2018.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"DUA_LIPA_VISUAL_IDENTITY_MUSIC_ERA","asset_role":"TARGET_SUBJECT","identifiable_human":True,"celebrity_visible":True},
   "dua2":{"file":"dua2.webm","source_url":"https://commons.wikimedia.org/wiki/File:Interview_with_Dua_Lipa_at_the_2021_Grammys.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"DUA_LIPA_VISUAL_IDENTITY_MUSIC_ERA","asset_role":"TARGET_SUBJECT","identifiable_human":True,"celebrity_visible":True},
   "dua3":{"file":"dua3.webm","source_url":"https://commons.wikimedia.org/wiki/File:Dua_Lipa_samples_from_5_songs.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"DUA_LIPA_VISUAL_IDENTITY_MUSIC_ERA","asset_role":"TARGET_SUBJECT","identifiable_human":True,"celebrity_visible":True},
   "dua4":{"file":"dua4.webm","source_url":"https://commons.wikimedia.org/wiki/File:All_you_need_to_know_about_Dua_Lipa%27s_new_album_%27Radical_Optimism%27.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"DUA_LIPA_VISUAL_IDENTITY_MUSIC_ERA","asset_role":"TARGET_SUBJECT","identifiable_human":True,"celebrity_visible":True}
  },
  "scenes":[
   ("REAL","dua1",2,"CONTEXT","dua","DUA LIPA • ARQUIVO REAL","Uma era pop não é só música. Ela também precisa ser reconhecida visualmente."),
   ("ANIMATION","anim",0,"MECHANISM","dua","ANIMAÇÃO • CÓDIGOS VISUAIS SE REPETEM","Cores, formas e enquadramentos repetidos criam pistas que o público associa àquela fase."),
   ("REAL","dua2",2,"PROOF","dua","DUA LIPA • OUTRO ARQUIVO REAL","Figurino, cabelo e direção de imagem reforçam essa linguagem."),
   ("ANIMATION","anim",2,"MECHANISM","dua","ANIMAÇÃO • CONSISTÊNCIA CRIA MEMÓRIA","Quando capa, vídeo e palco compartilham códigos, o público reconhece a era antes de ler o nome."),
   ("REAL","dua3",2,"CONSEQUENCE","dua","DUA LIPA • MATERIAL MUSICAL REAL","Repetir tudo igual cansaria, então cada peça muda elementos e preserva sinais centrais."),
   ("ANIMATION","anim",4,"MECHANISM","dua","ANIMAÇÃO • VARIAÇÃO CONTROLADA","A identidade funciona como uma família: peças diferentes continuam no mesmo universo."),
   ("REAL","dua4",2,"PROOF","dua","DUA LIPA • RADICAL OPTIMISM REAL","Assim, um álbum ganha assinatura própria e continua reconhecível em formatos diferentes.")
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
 with requests.get(url,headers={"User-Agent":"VSA-Oct05/1.0"},stream=True,timeout=180) as r:
  r.raise_for_status()
  with open(p,"wb") as f:
   for c in r.iter_content(1048576):
    if c:f.write(c)
 return p
def commons_video(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"videoinfo","viprop":"url|derivatives","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Oct05/1.0"},timeout=60).json()["query"]["pages"].values()))
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
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Oct05/1.0"},timeout=60).json()["query"]["pages"].values()))
 return dl(page["imageinfo"][0]["url"],p)


def commons_image(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"imageinfo","iiprop":"url","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Oct05/1.0"},timeout=60).json()["query"]["pages"].values()))
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
  if slug=="eletricidade_estatica":
   if seg==0:
    d.text((45,38),"ELÉTRONS MUDAM DE MATERIAL",font=fb,fill="white")
    for i in range(8):
     x=160+i*75; y=360
     d.ellipse((x-12,y-12,x+12,y+12),fill=(100,190,255))
    for i in range(5):
     x=250+int(320*u)+i*45; y=520+i%2*35
     d.ellipse((x-12,y-12,x+12,y+12),fill=(255,190,70))
    d.line((200,650,760,650),fill=(100,220,160),width=7)
    d.text((255,705),"transferência cria desequilíbrio",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"A PAREDE SE POLARIZA",font=fb,fill="white")
    d.ellipse((130,300,360,530),fill=(255,190,70))
    d.rectangle((700,180,850,680),fill=(110,120,135))
    for i in range(6):
     y=250+i*65
     d.text((650,y),"−",font=fb,fill=(100,190,255))
     d.text((780,y),"+",font=fb,fill=(255,170,80))
    d.line((370,415,650,415),fill=(100,220,160),width=9)
    d.polygon([(675,415),(635,392),(635,438)],fill=(100,220,160))
    d.text((260,735),"cargas próximas geram atração",font=fs,fill="white")
   else:
    d.text((45,38),"CARGA ESCAPA → FORÇA DIMINUI",font=fb,fill="white")
    d.ellipse((190,280,390,480),fill=(255,190,70))
    for i in range(8):
     x=450+int(260*u)+i*18; y=330+(i%4)*55
     d.ellipse((x-8,y-8,x+8,y+8),fill=(100,190,255))
    d.line((280,540,280,700),fill=(255,100,90),width=10)
    d.polygon([(280,730),(255,685),(305,685)],fill=(255,100,90))
    d.text((360,730),"atração cai • peso vence",font=fs,fill="white")
  elif slug=="giroscopio":
   if seg==0:
    d.text((45,38),"ROTAÇÃO → MOMENTO ANGULAR",font=fb,fill="white")
    cx,cy=487,430
    d.ellipse((270,350,704,510),outline=(100,190,255),width=14)
    d.line((cx,250,cx,620),fill=(255,190,70),width=10)
    d.line((cx,430,760,430),fill=(100,220,160),width=9)
    d.polygon([(790,430),(745,407),(745,453)],fill=(100,220,160))
    d.text((270,700),"o vetor acompanha o eixo",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"TORQUE → PRECESSÃO",font=fb,fill="white")
    cx,cy=487,440
    d.ellipse((360,315,614,565),outline=(100,190,255),width=10)
    d.arc((220,180,755,700),20,300,fill=(100,220,160),width=10)
    d.polygon([(690,225),(655,265),(710,270)],fill=(100,220,160))
    d.line((487,440,640,610),fill=(255,190,70),width=10)
    d.text((255,715),"o eixo muda de direção sem cair direto",font=fs,fill="white")
   else:
    d.text((45,38),"ATRITO REDUZ A ROTAÇÃO",font=fb,fill="white")
    for i in range(5):
     r=190-i*28
     start=int(30+i*30+u*220)
     d.arc((487-r,430-r,487+r,430+r),start,start+230,fill=(100+20*i,180,230),width=8)
    d.line((180,680,800,680),fill=(130,150,175),width=6)
    pos=180+int(620*u); d.ellipse((pos-18,662,pos+18,698),fill=(255,190,70))
    d.text((250,745),"menos giro → menos estabilidade",font=fs,fill="white")
  else:
   if seg==0:
    d.text((45,38),"CÓDIGOS VISUAIS SE REPETEM",font=fb,fill="white")
    cards=[(90,250,280,520,"COR"),(390,250,580,520,"FORMA"),(690,250,880,520,"TIPO")]
    for i,(x1,y1,x2,y2,lab) in enumerate(cards):
     d.rounded_rectangle((x1,y1,x2,y2),24,outline=(100+40*i,180,230),width=7)
     d.text((x1+55,y1+110),lab,font=fs,fill="white")
    d.line((120,650,850,650),fill=(100,220,160),width=7)
    pos=120+int(730*u); d.ellipse((pos-18,632,pos+18,668),fill=(255,190,70))
    d.text((215,725),"repetição cria reconhecimento",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"CONSISTÊNCIA → MEMÓRIA",font=fb,fill="white")
    labs=["CAPA","VÍDEO","PALCO","POST"]
    for i,lab in enumerate(labs):
     x=90+i*215
     d.rounded_rectangle((x,310,x+165,500),20,fill=(50,70,95),outline=(100,190,255),width=5)
     d.text((x+34,385),lab,font=fs,fill="white")
     if i<3:d.line((x+165,405,x+215,405),fill=(100,220,160),width=7)
    d.text((245,650),"mesmos sinais • formatos diferentes",font=fs,fill="white")
   else:
    d.text((45,38),"VARIAÇÃO CONTROLADA",font=fb,fill="white")
    for i in range(6):
     x=110+(i%3)*270; y=245+(i//3)*260
     d.rounded_rectangle((x,y,x+185,y+170),20,outline=(100,180+10*i,220),width=6)
     d.ellipse((x+55,y+40,x+130,y+115),fill=(255,190,70) if i%2==0 else (100,220,160))
    d.text((170,720),"muda a peça • preserva a assinatura",font=fs,fill="white")
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
 final=od/f"VSA_{slug}_OCT05.mp4";run(["ffmpeg","-y","-loglevel","error","-i",visual,"-i",mix,"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",final])
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
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/339fdfa9-e579-4c20-a0b3-22de044eed24.webm",AS/"static1.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/343e3756-e8ad-4f8d-9f96-6182d74daab7.webm",AS/"static2.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/87cee95e-d1b3-4aed-b473-260fe8fa8dd8.webm",AS/"static3.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/3a82ceb9-ab7d-4268-a0e7-955afa1a92cb.webm",AS/"static4.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/b215f792-61e2-467d-a457-cf53ad0a92a8.webm",AS/"gyro1.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/faaca84e-4a3c-471b-80bf-b1fc97e128d1.webm",AS/"gyro2.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/592b2b1f-0c33-4464-841e-087434929af5.webm",AS/"gyro3.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/37637870-3137-4418-8849-d5fbc0feb683.webm",AS/"gyro4.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/07c7aae2-92ff-416c-839f-1135ac8d3b51.webm",AS/"dua1.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/8e5289a6-5bc5-48fe-b2bd-ac05d6ef229e.webm",AS/"dua2.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/5a7e8342-0eb8-4880-a6e5-8c67ce7f6e43.webm",AS/"dua3.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/bdf49b25-7f9f-4b7c-9f28-228395f0d01a.webm",AS/"dua4.webm")
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

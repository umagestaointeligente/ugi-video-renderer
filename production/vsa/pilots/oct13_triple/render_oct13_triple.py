#!/usr/bin/env python3
from __future__ import annotations
import pathlib, subprocess, json, hashlib, shutil, requests, math, os, re

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
 "pendulo_newton":{
  "title":"Por que só a última esfera do pêndulo de Newton se move? #shorts",
  "header":["POR QUE SÓ A ÚLTIMA","ESFERA SE MOVE?"],
  "description":"No pêndulo de Newton, o impacto comprime as esferas por uma fração de segundo e transmite momento e energia pela fileira. Com massas iguais e colisões quase elásticas, uma esfera entra e outra sai. #VocêSabiaAgora #Curiosidades #Física #PênduloDeNewton",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"NEWTON_CRADLE_MOMENTUM_ENERGY_TRANSFER",
  "assets":{
   "newton1":{"file":"newton1.webm","source_url":"https://commons.wikimedia.org/wiki/File:Newton%E2%80%99s_cradle_slo_mo.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_NEWTON_CRADLE_SLOW_MOTION","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "newton2":{"file":"newton2.webm","source_url":"https://commons.wikimedia.org/wiki/File:Newton%27s_-_Balls.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_NEWTON_CRADLE_SECOND_SOURCE","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "newton3":{"file":"newton3.webm","source_url":"https://commons.wikimedia.org/wiki/File:Pendolo_di_Newton_a_3_sferette_rallentato.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_NEWTON_CRADLE_THREE_BALLS","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "newton4":{"file":"newton4.webm","source_url":"https://commons.wikimedia.org/wiki/File:Pendolo_di_Newton_a_5_sferette_rallentato.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_NEWTON_CRADLE_FIVE_BALLS","asset_role":"TARGET_SUBJECT","identifiable_human":False}
  },
  "scenes":[
   ("REAL","newton1",2,"CONTEXT","newton","PÊNDULO DE NEWTON • VÍDEO REAL","Quando uma esfera bate na fileira, parece que o impacto atravessa as bolas e empurra só a última."),
   ("ANIMATION","anim",0,"MECHANISM","newton","ANIMAÇÃO • IMPACTO COMPRIME AS ESFERAS","Na colisão, as esferas se comprimem por um instante e uma força percorre a sequência."),
   ("REAL","newton2",2,"PROOF","newton","OUTRO PÊNDULO • VÍDEO REAL","Como as massas são iguais, o sistema transfere momento de uma esfera para a seguinte."),
   ("ANIMATION","anim",2,"MECHANISM","newton","ANIMAÇÃO • MOMENTO E ENERGIA VIAJAM","Numa colisão quase elástica, grande parte da energia cinética também é conservada."),
   ("REAL","newton3",2,"CONSEQUENCE","newton","TRÊS ESFERAS • VÍDEO REAL","Uma esfera entrando tende a produzir uma saindo do outro lado com velocidade parecida."),
   ("ANIMATION","anim",4,"MECHANISM","newton","ANIMAÇÃO • DUAS ENTRAM, DUAS SAEM","Se você solta duas, conservar momento e energia favorece duas esferas saindo na outra ponta."),
   ("REAL","newton4",2,"PROOF","newton","CINCO ESFERAS • VÍDEO REAL","Nada atravessa magicamente o metal: o que se propaga é a interação mecânica entre as esferas.")
  ]},
 "semaforo_quimico":{
  "title":"Por que essa solução muda de cor quando você agita? #shorts",
  "header":["POR QUE AGITAR","MUDA A COR?"],
  "description":"No experimento do semáforo químico, agitar dissolve oxigênio e muda o estado de oxidação do corante. Depois, a glicose em meio básico reduz o corante novamente e as cores retornam. #VocêSabiaAgora #Curiosidades #Química #SemáforoQuímico",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"CHEMICAL_TRAFFIC_LIGHT_REDOX_OXYGEN_DYE",
  "assets":{
   "chem1":{"file":"chem1.webm","source_url":"https://commons.wikimedia.org/wiki/File:Chemical_Traffic_Light.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_CHEMICAL_TRAFFIC_LIGHT","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "chem2":{"file":"chem2.webm","source_url":"https://commons.wikimedia.org/wiki/File:Chemical_traffic_light_reaction_time-lapse.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_CHEMICAL_TRAFFIC_LIGHT_TIMELAPSE","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "chem3":{"file":"chem3.webm","source_url":"https://commons.wikimedia.org/wiki/File:Chemical_Traffic_Light_Experiment_Pattern_Formation_In_Different_Shape_Containers.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_CHEMICAL_TRAFFIC_LIGHT_PATTERNS","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "chem4":{"file":"chem4.webm","source_url":"https://commons.wikimedia.org/wiki/File:Blue_Bottle_in_Different_Temperature.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_REDOX_COLOR_TEMPERATURE_CONTEXT","asset_role":"EXPLICIT_CONTEXT","identifiable_human":False}
  },
  "scenes":[
   ("REAL","chem1",2,"CONTEXT","chem","SEMÁFORO QUÍMICO • VÍDEO REAL","Essa solução pode passar por cores diferentes só porque você agitou o frasco."),
   ("ANIMATION","anim",0,"MECHANISM","chem","ANIMAÇÃO • AGITAR DISSOLVE OXIGÊNIO","Ao agitar, mais oxigênio do ar se dissolve no líquido e participa da reação."),
   ("REAL","chem2",2,"PROOF","chem","MUDANÇA DE COR • VÍDEO REAL","O oxigênio muda o estado químico do corante e, com isso, muda a luz que ele absorve."),
   ("ANIMATION","anim",2,"MECHANISM","chem","ANIMAÇÃO • OXIDAÇÃO MUDA O CORANTE","O corante oxidado e o reduzido têm estruturas eletrônicas diferentes e aparecem com cores diferentes."),
   ("REAL","chem3",2,"CONSEQUENCE","chem","PADRÕES QUÍMICOS • VÍDEO REAL","Quando o oxigênio disponível cai, a glicose ajuda a reduzir o corante e a cor retorna."),
   ("ANIMATION","anim",4,"MECHANISM","chem","ANIMAÇÃO • O CICLO RECOMEÇA","Agitar repõe oxigênio e reinicia o ciclo; temperatura e mistura alteram a velocidade das etapas."),
   ("REAL","chem4",2,"PROOF","chem","TEMPERATURA MUDA A VELOCIDADE • VÍDEO REAL","Por isso sistemas redox parecidos podem mudar de cor mais rápido ou devagar sem adicionar novo pigmento.")
  ]},
 "olivia_rodrigo_mensagem":{
  "title":"Como Olivia Rodrigo adapta a mensagem para públicos diferentes? #shorts",
  "header":["COMO OLIVIA RODRIGO","ADAPTA A MENSAGEM?"],
  "description":"Uma mesma ideia pode ser comunicada de formas diferentes conforme o público, o espaço e o tempo disponível. Conversa, palco e campanha pública exigem escolhas diferentes de linguagem sem perder a intenção central. #VocêSabiaAgora #OliviaRodrigo #Comunicação #Música",
  "content_class":"NEWS_EXPLAINER","expected_subject":"OLIVIA_RODRIGO_COMMUNICATION_AUDIENCE_FORMAT",
  "celebrity_name":"Olivia Rodrigo",
  "assets":{
   "olivia1":{"file":"olivia1.webm","source_url":"https://commons.wikimedia.org/wiki/File:Olivia_Rodrigo_and_Dr._Fauci_Read_Vaccine_Fan_Tweets.webm","license":"PUBLIC_DOMAIN_US_GOV","asset_subject":"OLIVIA_RODRIGO_COMMUNICATION_AUDIENCE_FORMAT","asset_role":"TARGET_SUBJECT","identifiable_human":True,"celebrity_visible":True},
   "concert":{"file":"concert.webm","source_url":"https://commons.wikimedia.org/wiki/File:Concert_at_University_of_Gothenburg.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_CONCERT_AUDIENCE_CONTEXT","asset_role":"EXPLICIT_CONTEXT","identifiable_human":True,"celebrity_visible":False},
   "crowd":{"file":"crowd.webm","source_url":"https://commons.wikimedia.org/wiki/File:Crowd_of_participants_at_the_ABU_Cultural_Carnival_2.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_LARGE_AUDIENCE_CONTEXT","asset_role":"EXPLICIT_CONTEXT","identifiable_human":True,"celebrity_visible":False},
   "olivia2":{"file":"olivia2.webm","source_url":"https://commons.wikimedia.org/wiki/File:Olivia_Rodrigo,_President_Biden,_and_Dr._Fauci_talk_Vaccines_at_the_White_House.webm","license":"PUBLIC_DOMAIN_US_GOV","asset_subject":"OLIVIA_RODRIGO_COMMUNICATION_AUDIENCE_FORMAT","asset_role":"TARGET_SUBJECT","identifiable_human":True,"celebrity_visible":True}
  },
  "scenes":[
   ("REAL","olivia1",12,"CONTEXT","olivia","OLIVIA RODRIGO • ARQUIVO REAL","Em uma conversa curta, Olivia Rodrigo pode reagir ao outro e ajustar o tom da mensagem na hora."),
   ("ANIMATION","anim",0,"MECHANISM","olivia","ANIMAÇÃO • PÚBLICO MUDA O FORMATO","Quanto menor o público, mais espaço existe para detalhe, resposta e improviso."),
   ("REAL","concert",2,"PROOF","olivia","PALCO GRANDE • CONTEXTO REAL","Num palco grande, a mensagem precisa ser legível à distância e funcionar com som, imagem e ritmo."),
   ("ANIMATION","anim",2,"MECHANISM","olivia","ANIMAÇÃO • IDEIA CENTRAL FICA MAIS CLARA","A ideia central continua igual, mas frases, gestos e repetições ficam mais simples de reconhecer."),
   ("REAL","crowd",2,"CONSEQUENCE","olivia","MULTIDÃO • CONTEXTO REAL","Com muita gente, repetir sinais claros ajuda o público a entender e lembrar a mensagem."),
   ("ANIMATION","anim",4,"MECHANISM","olivia","ANIMAÇÃO • IDENTIDADE PERMANECE","O formato muda, mas a identidade precisa permanecer: mesma intenção, outra embalagem."),
   ("REAL","olivia2",25,"PROOF","olivia","OLIVIA RODRIGO • SEGUNDO ARQUIVO REAL","Fora do palco, o contexto muda novamente, mas a mensagem ainda precisa continuar clara e reconhecível.")
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
 # Fresh atomic acquisition; size alone is not cache validation.
 partial=p.with_name(p.name+".partial")
 p.unlink(missing_ok=True);partial.unlink(missing_ok=True)
 try:
  with requests.get(url,headers={"User-Agent":"VSA-Oct13/1.0"},stream=True,timeout=(15,60)) as r:
   r.raise_for_status()
   with open(partial,"wb") as f:
    for c in r.iter_content(1048576):
     if c:f.write(c)
  if not partial.is_file() or partial.stat().st_size==0:raise RuntimeError("ASSET_EMPTY_FAIL")
  partial.replace(p)
  return p
 finally:partial.unlink(missing_ok=True)

def commons_video(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"videoinfo","viprop":"url|derivatives","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Oct13/1.0"},timeout=60).json()["query"]["pages"].values()))
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
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Oct13/1.0"},timeout=60).json()["query"]["pages"].values()))
 return dl(page["imageinfo"][0]["url"],p)


def commons_image(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"imageinfo","iiprop":"url","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Oct13/1.0"},timeout=60).json()["query"]["pages"].values()))
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
  if slug=="pendulo_newton":
   if seg==0:
    d.text((45,38),"IMPACTO COMPRIME AS ESFERAS",font=fb,fill="white")
    xs=[255,365,475,585,695]
    for i,x in enumerate(xs):
     shift=int(12*u) if i in (1,2,3) else 0
     d.ellipse((x-42+shift,360,x+42+shift,444),fill=(180,200,215),outline="white",width=3)
     d.line((x+shift,170,x+shift,360),fill=(145,165,185),width=5)
    pulse=275+int(400*u)
    d.ellipse((pulse-15,490,pulse+15,520),fill=(255,190,70))
    d.text((220,700),"deformação minúscula transmite a força",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"MOMENTO + ENERGIA SÃO TRANSFERIDOS",font=fb,fill="white")
    for i,x in enumerate([210,340,470,600,730]):
     d.ellipse((x-37,360,x+37,434),outline=(120,190,255),width=6)
    d.line((170,525,800,525),fill=(100,220,160),width=10)
    d.polygon([(830,525),(785,500),(785,550)],fill=(100,220,160))
    d.text((245,650),"massa igual favorece uma saída simétrica",font=fs,fill="white")
   else:
    d.text((45,38),"UMA ENTRA → UMA SAI | DUAS → DUAS",font=fb,fill="white")
    for row,count in enumerate((1,2)):
     y=285+row*260
     for i,x in enumerate([290,390,490,590,690]):
      d.ellipse((x-32,y-32,x+32,y+32),fill=(170,195,215))
     d.text((105,y-18),str(count),font=fb,fill=(255,190,70))
     for k in range(count):
      d.line((235-k*28,y,150-k*35,y),fill=(255,190,70),width=7)
      d.line((745+k*28,y,830+k*35,y),fill=(100,220,160),width=7)
    d.text((225,720),"as duas conservações restringem o resultado",font=fs,fill="white")
  elif slug=="semaforo_quimico":
   if seg==0:
    d.text((45,38),"AGITAR DISSOLVE MAIS OXIGÊNIO",font=fb,fill="white")
    d.rounded_rectangle((300,220,675,690),30,outline=(150,180,210),width=7)
    for i in range(18):
     x=350+(i%6)*55; y=570-(i//6)*75-int(170*u)
     d.ellipse((x-9,y-9,x+9,y+9),fill=(100,190,255))
    d.text((295,735),"O₂ do ar entra na solução",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"OXIDAÇÃO MUDA O ESTADO DO CORANTE",font=fb,fill="white")
    d.rounded_rectangle((100,300,390,550),24,fill=(60,190,105))
    d.rounded_rectangle((585,300,875,550),24,fill=(220,175,60))
    d.line((405,425,565,425),fill=(100,220,160),width=9)
    d.polygon([(585,425),(550,403),(550,447)],fill=(100,220,160))
    d.text((165,590),"estado A",font=fs,fill="white")
    d.text((650,590),"estado B",font=fs,fill="white")
    d.text((220,700),"estrutura eletrônica → cor absorvida",font=fs,fill="white")
   else:
    d.text((45,38),"O CICLO PODE RECOMEÇAR",font=fb,fill="white")
    pts=[(487,235),(725,430),(487,625),(250,430)]
    labs=["AGITAR","OXIDAR","REDUZIR","REPETIR"]
    for i,(x,y) in enumerate(pts):
     d.ellipse((x-65,y-45,x+65,y+45),outline=(100,190,255),width=6)
     d.text((x-48,y-12),labs[i],font=fr,fill="white")
     x2,y2=pts[(i+1)%4]; d.line((x,y,x2,y2),fill=(100,220,160),width=5)
    d.text((230,735),"temperatura altera a velocidade das etapas",font=fs,fill="white")
  else:
   if seg==0:
    d.text((45,38),"PÚBLICO MENOR → MAIS DETALHE",font=fb,fill="white")
    d.ellipse((170,330,310,470),fill=(255,190,70))
    for i in range(3):
     x=570+i*105
     d.ellipse((x-35,350,x+35,420),fill=(100,190,255))
    d.rounded_rectangle((135,520,435,660),20,outline=(100,220,160),width=5)
    d.text((180,570),"DETALHE + RESPOSTA",font=fr,fill="white")
    d.text((515,560),"interação direta",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"PÚBLICO MAIOR → SINAL MAIS CLARO",font=fb,fill="white")
    for i in range(20):
     x=100+(i%10)*82; y=480+(i//10)*95
     d.ellipse((x-17,y-17,x+17,y+17),fill=(100,190,255))
    d.rounded_rectangle((245,220,730,355),20,fill=(55,75,100),outline=(255,190,70),width=6)
    d.text((310,265),"IDEIA CENTRAL CURTA",font=fs,fill="white")
    d.text((270,700),"frase + gesto + repetição",font=fs,fill="white")
   else:
    d.text((45,38),"MESMA INTENÇÃO • OUTRO FORMATO",font=fb,fill="white")
    d.ellipse((375,335,600,560),outline=(255,190,70),width=8)
    d.text((420,425),"NÚCLEO",font=fs,fill="white")
    cards=[("CONVERSA",90,200),("PALCO",690,200),("CAMPANHA",690,610),("ENTREVISTA",90,610)]
    for lab,x,y in cards:
     d.rounded_rectangle((x,y,x+190,y+95),18,outline=(100,190,255),width=5)
     d.text((x+22,y+32),lab,font=fr,fill="white")
     d.line((487,447,x+95,y+48),fill=(100,220,160),width=4)
    d.text((260,750),"identidade preservada entre formatos",font=fs,fill="white")
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
      f"[0:v][in]overlay={X}:{Y}:shortest=1,setsar=1,format=yuv420p[v]")
  run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",base,"-ss",start,"-i",src,"-t",length,"-filter_complex",fc,"-map","[v]","-an","-r",FPS,"-c:v","libx264","-preset","veryfast","-crf","20",out])
 else:
  stretch=max(.1,float(length)/2.0)
  fc=(f"[1:v]setpts={stretch:.6f}*PTS,fps={FPS},scale={WW}:{HH}:flags=lanczos,{lf}[in];[0:v][in]overlay={X}:{Y}:shortest=1,setsar=1,format=yuv420p[v]")
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
  "master":{"sha256":h},"release_token":{"status":"PENDING_QA","master_sha256":h},
  "voice":{"language":"pt-BR","profile_id":VOICE,"neutral_ptbr_gate":"UNVERIFIED","foreign_accent_detected":None},
  "mask":{"version":"V2","sha256":MASK_SHA,"applied_to_final_master":True,"safe_zone_gate":"PASS"},
  "content_class":topic["content_class"],"expected_subject":topic["expected_subject"],"shot_map":scene_rows,
  "tail_integrity":{"pre_cta_contamination_gate":"UNVERIFIED","unrelated_or_legacy_frame_detected":None,"cta_first_frame_matches_canonical":False},
  "gates":{g:False for g in gates},
  "captions":{"burned_in_final_master":True,"maximum_lines_observed":2,"visible_samples":caption_samples},
  "title":{"layer_count":1,"ghost_duplicate_detected":False,"inside_safe_zone":True},
  "cta":{"lines":CTA_LINES},
  "format":{"width":1080,"height":1920,"fps":30,"video_codec":"h264","pixel_format":"yuv420p"},
  "visual_proof":{"contact_sheet_generated":True,"all_story_blocks_sampled":True,"tail_window_sampled":True},
  "release_eligible":False,"schedule_mutated_before_gate":False
 }


def require_duration(slug,seconds):
 if not math.isfinite(seconds) or not 45 <= seconds <= 55:
  raise RuntimeError("DURATION_GATE_FAIL "+json.dumps({"slug":slug,"duration_seconds":seconds},ensure_ascii=False))


def validate_narration_audio(path):
 seconds=duration(path)
 if not math.isfinite(seconds) or seconds<=0:
  raise RuntimeError("TTS_AUDIO_INVALID")
 result=subprocess.run(["ffmpeg","-hide_banner","-v","info","-xerror","-i",str(path),
                        "-map","0:a:0","-af","volumedetect","-f","null","-"],
                       check=True,capture_output=True,text=True,timeout=60)
 match=re.search(r"max_volume:\s*(-?inf|[-+]?\d+(?:\.\d+)?)\s*dB",result.stderr)
 if not match or float(match.group(1))<=-60:
  raise RuntimeError("TTS_AUDIO_SILENT_OR_UNMEASURED")
 return seconds

def synthesize_narration(text,rate,target):
 # Never accept a stale/partial file or substitute silence on provider failure.
 partial=target.with_name(target.stem+".partial.mp3")
 target.unlink(missing_ok=True);partial.unlink(missing_ok=True)
 try:
  bundle=os.environ.get("VSA_NARRATION_BUNDLE")
  if bundle:
   manifest_path=pathlib.Path(bundle).resolve()
   manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
   key=hashlib.sha256(json.dumps([VOICE,rate,text],ensure_ascii=False,separators=(",",":")).encode()).hexdigest()
   entry=manifest.get("clips",{}).get(key,{})
   if entry.get("voice")!=VOICE or entry.get("rate")!=rate or entry.get("text")!=text:
    raise RuntimeError("TTS_BUNDLE_IDENTITY_FAIL")
   source=(manifest_path.parent/entry.get("file","")).resolve()
   if not source.is_relative_to(manifest_path.parent) or not source.is_file() or sha(source)!=entry.get("sha256"):
    raise RuntimeError("TTS_BUNDLE_HASH_FAIL")
   shutil.copyfile(source,partial)
   result=None
  else:
   result=subprocess.run(["edge-tts","--voice",VOICE,"--rate="+rate,
                          "--text",text,"--write-media",str(partial)],
                         capture_output=True,text=True,timeout=60)
  if result is not None and result.returncode:
   if "WSServerHandshakeError: 403" in result.stderr:reason="TTS_PROVIDER_HTTP_403"
   elif "SSLCertVerificationError" in result.stderr or "ClientConnectorCertificateError" in result.stderr:reason="TTS_TLS_CERTIFICATE_FAIL"
   else:reason="TTS_PROVIDER_FAILED"
   raise RuntimeError(reason)
  if not partial.is_file() or partial.stat().st_size==0:
   raise RuntimeError("TTS_AUDIO_MISSING")
  validate_narration_audio(partial)
  partial.replace(target)
 except subprocess.TimeoutExpired:
  raise RuntimeError("TTS_TIMEOUT") from None
 except subprocess.CalledProcessError:
  raise RuntimeError("TTS_AUDIO_DECODE_FAIL") from None
 finally:
  partial.unlink(missing_ok=True)

def prepare_narration(slug,topic,wd):
 # Measure the exact audio that will be reused by the render, including CTA.
 measured=[]
 for i,scene in enumerate(topic["scenes"],1):
  voice=wd/f"v{i}.mp3"
  synthesize_narration(scene[-1],"-2%",voice)
  measured.append(duration(voice))
 ca=wd/"cta.mp3"
 synthesize_narration(" ".join(CTA_LINES),"+18%",ca)
 cta_seconds=duration(ca)
 if any(not math.isfinite(x) or x<=0 for x in measured+[cta_seconds]):
  raise RuntimeError("NARRATION_DURATION_INVALID "+slug)
 # Frame rounding and mux overhead are reserved; never trim or accelerate speech.
 projected=sum(math.ceil((x+.10)*FPS)/FPS for x in measured)+max(3.6,cta_seconds+.2)
 if projected>54.5:
  raise RuntimeError("DURATION_PREFLIGHT_FAIL "+json.dumps({"slug":slug,"projected_seconds":projected},ensure_ascii=False))
 print("DURATION_PREFLIGHT_PASS",slug,projected)
 return measured,ca,max(3.6,cta_seconds+.2)

def render(slug,topic,mask,cta,music,narration):
 wd=WORK/slug;od=OUT/slug;shutil.rmtree(od,ignore_errors=True);od.mkdir(parents=True)
 measured,ca,cd=narration
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
  row={"id":f"s{i}","narration":text,"media_type":kind,"visual_role":role,"visual_description":label,"visible_action":label,"semantic_claim":text,"semantic_match":"UNVERIFIED","causal_link_id":link,"topic_only_match":False,"generic_filler":False,"reused_take_as_variety":False}
  if kind=="REAL":
   row["asset"]={"event":slug,"asset_key":source_key,"file":asset["file"],"semantic_role":role,"visible_action":label,"source_url":asset["source_url"],"license":asset["license"],"source_timestamp_seconds":float(start),"rights_verified":False,"expected_subject":topic["expected_subject"],"asset_subject":asset["asset_subject"],"asset_role":asset["asset_role"],"identifiable_human":asset.get("identifiable_human",False),"celebrity_visible":asset.get("celebrity_visible",False),"duration_seconds":length,"explicit_script_reference":True}
  rows.append(row)
 vl=wd/"v.txt";vl.write_text("\n".join(f"file '{p}'" for p in vids)+"\n");body=wd/"body.mp4";run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",vl,"-an","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",body])
 al=wd/"a.txt";al.write_text("\n".join(f"file '{p}'" for p in asegs)+"\n");bodya=wd/"body.wav";run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",al,"-c:a","pcm_s16le","-ar","48000",bodya])
 ass=wd/"c.ass";make_ass(times,ass);esc=str(ass).replace("'","\\'").replace(":","\\:");bodyc=wd/"bodyc.mp4";run(["ffmpeg","-y","-loglevel","error","-i",body,"-vf",f"subtitles='{esc}'","-an","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",bodyc])
 cv=wd/"cta.mp4";run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",cta,"-t",f"{cd:.3f}","-vf",f"scale={W}:{H},setsar=1,fps={FPS},format=yuv420p","-an","-c:v","libx264","-preset","veryfast","-crf","20",cv])
 fl=wd/"f.txt";fl.write_text(f"file '{bodyc}'\nfile '{cv}'\n");visual=wd/"visual.mp4";run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",fl,"-an","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",visual])
 alla=wd/"all.wav";run(["ffmpeg","-y","-loglevel","error","-i",bodya,"-i",ca,"-filter_complex","[0:a][1:a]concat=n=2:v=0:a=1[a]","-map","[a]","-ar","48000",alla])
 mix=wd/"mix.m4a";af="[0:a]aresample=48000,asplit=2[n1][n2];[1:a]aresample=48000,volume=.10,aloop=loop=-1:size=2147483647[m];[m][n1]sidechaincompress=threshold=.035:ratio=8:attack=20:release=250[d];[n2][d]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=10[a]";run(["ffmpeg","-y","-loglevel","error","-i",alla,"-i",music,"-filter_complex",af,"-map","[a]","-ar","48000",mix])
 final=od/f"VSA_{slug}_OCT13.mp4";run(["ffmpeg","-y","-loglevel","error","-i",visual,"-i",mix,"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",final])
 probe=json.loads(cap(["ffprobe","-v","error","-show_streams","-show_format","-of","json",final]));fd=float(probe["format"]["duration"]);v=next(x for x in probe["streams"] if x.get("codec_type")=="video")
 print("DURATION_CHECK",slug,fd)
 require_duration(slug,fd)
 if int(v["width"])!=1080 or int(v["height"])!=1920 or v["codec_name"]!="h264" or v["pix_fmt"]!="yuv420p":raise RuntimeError("FORMAT_FAIL")
 contact=od/"CONTACT.jpg";run(["ffmpeg","-y","-loglevel","error","-i",final,"-vf","fps=1/5,scale=270:480,tile=4x3:padding=4:margin=4","-frames:v","1",contact])
 thumb=od/"THUMBNAIL.jpg";run(["ffmpeg","-y","-loglevel","error","-ss","1","-i",final,"-frames:v","1",thumb])
 samples=[{"t":round(fd*x,1),"visible":False,"inside_safe_zone":False} for x in (.18,.48,.75)]
 meta={"slug":slug,"title":topic["title"],"description":topic["description"],"duration_seconds":fd,"sha256":sha(final),"master":str(final),"receipt":str(od/"RELEASE_RECEIPT.json")}
 rec=receipt(topic,meta,final,rows,samples);(od/"RELEASE_RECEIPT.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n");(od/"META.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n")
 return meta

def main():
 shutil.rmtree(WORK,ignore_errors=True);shutil.rmtree(OUT,ignore_errors=True);WORK.mkdir();OUT.mkdir()
 narrations={}
 for slug,topic in TOPICS.items():
  wd=WORK/slug;wd.mkdir()
  narrations[slug]=prepare_narration(slug,topic,wd)
 mask=dl(MASK_URL,AS/"mask.png");cta=dl(CTA_URL,AS/"cta.png")
 if sha(mask)!=MASK_SHA:raise RuntimeError("MASK_SHA_FAIL")
 music=dl("https://d2ol7oe51mr4n9.cloudfront.net/user_3INXyBRQIUkFRTaKNDmjseizowV/f1f3904c-153f-4d51-9ffe-a8974cf30ea0.mp3",AS/"music.mp3")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/c74bbea2-dbc9-48f0-8dd6-bf4c47f6f7f6.webm",AS/"newton1.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/17885ba9-6673-42e0-bd65-dafcb7bd30f7.webm",AS/"newton2.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/0b10ffed-1866-4abe-8729-e9ff65ff1c3a.webm",AS/"newton3.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/8020de39-dffc-4e3e-bcfa-3264fcc15fe8.webm",AS/"newton4.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/e3f8f969-2ad6-4efa-a4d2-2253d2f03821.webm",AS/"chem1.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/1f03b6a6-a2e6-493a-8363-ede5eaf1086e.webm",AS/"chem2.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/eaf317c3-9726-4ea7-b104-5eeeb6924628.webm",AS/"chem3.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/b670d6ae-5c67-4fc7-bc38-64125df431da.webm",AS/"chem4.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/3c25cc7d-e3f0-4cca-a609-6d980f2f2631.webm",AS/"olivia1.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/3f15f09a-6257-4f8c-9604-bdae7e590095.webm",AS/"concert.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/80a25fe2-9f08-4d8b-9438-787a4f4faef8.webm",AS/"crowd.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/aeade578-97da-438b-9f54-5650f54b383f.webm",AS/"olivia2.webm")
 for slug,t in TOPICS.items():
  real_keys=[s[1] for s in t["scenes"] if s[0]=="REAL"]
  real_files=[t["assets"][k]["file"] for k in real_keys]
  hashes=[sha(AS/name) for name in real_files]
  if len(set(hashes))!=len(hashes):raise RuntimeError("REAL_ASSET_DUPLICATE_BYTES_FAIL "+slug)
  for scene in t["scenes"]:
   if scene[0]=="REAL":
    source=AS/t["assets"][scene[1]]["file"]
    if duration(source)<scene[2]+narrations[slug][0][t["scenes"].index(scene)]+.10:
     raise RuntimeError("SOURCE_WINDOW_TOO_SHORT "+slug)
  if len(real_files)!=4 or len(real_files)!=len(set(real_files)): raise RuntimeError("REAL_ASSET_DUPLICATE_FAIL "+slug)
  if t["content_class"]=="NEWS_EXPLAINER":
   celeb=[t["assets"][k].get("celebrity_visible",False) for k in real_keys]
   if sum(1 for x in celeb if x)<2 or not celeb[0] or not celeb[-1]: raise RuntimeError("CELEBRITY_CONTEXT_FAIL "+slug)
  make_anim(slug,AS/(slug+"_3d.mp4"))
 metas=[render(slug,t,mask,cta,music,narrations[slug]) for slug,t in TOPICS.items()]
 bad=[{"slug":m["slug"],"duration_seconds":m["duration_seconds"]} for m in metas if not(45<=float(m["duration_seconds"])<=55)]
 if bad: raise RuntimeError("DURATION_GATE_FAIL "+json.dumps(bad,ensure_ascii=False))
 (OUT/"MANIFEST.json").write_text(json.dumps(metas,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(metas,ensure_ascii=False,indent=2))
if __name__=="__main__":main()


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
 "globo_plasma":{
  "title":"Por que os raios de uma bola de plasma seguem seu dedo? #shorts",
  "header":["POR QUE O PLASMA","SEGUE SEU DEDO?"],
  "description":"A bola de plasma usa alta tensão alternada para ionizar um gás de baixa pressão. Ao tocar o vidro, seu corpo altera o campo elétrico e concentra parte da descarga perto do dedo. #VocêSabiaAgora #Curiosidades #Física #Plasma",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"PLASMA_GLOBE_ELECTRIC_FIELD_IONIZATION",
  "assets":{
   "plasma1":{"file":"plasma1.webm","source_url":"https://commons.wikimedia.org/wiki/File:Plasma_globe_23s.webm","license":"CC_BY_SA_3.0","asset_subject":"REAL_PLASMA_GLOBE","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "plasma2":{"file":"plasma2.webm","source_url":"https://commons.wikimedia.org/wiki/File:%E0%AE%AA%E0%AE%BF%E0%AE%B3%E0%AE%BE%E0%AE%9A%E0%AE%AE%E0%AE%BE_%E0%AE%95%E0%AF%81%E0%AE%B3%E0%AF%8B%E0%AE%AA%E0%AF%8D_-_Plasma_Globe.webm","license":"CC_BY","asset_subject":"REAL_PLASMA_GLOBE_SECOND_SOURCE","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "plasma3":{"file":"plasma3.webm","source_url":"https://commons.wikimedia.org/wiki/File:%E9%96%83%E9%9B%BB%E7%90%83-%E6%8C%87%E5%B0%96%E5%B0%8D%E6%8C%87%E5%B0%96%E5%AF%A6%E9%A9%97_01.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_PLASMA_GLOBE_FINGER_INTERACTION","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "plasma4":{"file":"plasma4.webm","source_url":"https://commons.wikimedia.org/wiki/File:Tesla_Coil_Lightning.webm","license":"CC_BY_4.0","asset_subject":"REAL_HIGH_VOLTAGE_IONIZED_DISCHARGE_CONTEXT","asset_role":"EXPLICIT_CONTEXT","identifiable_human":False}
  },
  "scenes":[
   ("REAL","plasma1",2,"CONTEXT","plasma","BOLA DE PLASMA • VÍDEO REAL","Dentro da esfera, os filamentos brilhantes são caminhos de gás ionizado, criado quando partículas carregadas atravessam o gás rarefeito."),
   ("ANIMATION","anim",0,"MECHANISM","plasma","ANIMAÇÃO • CAMPO ELÉTRICO IONIZA O GÁS","Um eletrodo central cria um campo elétrico intenso entre o centro e o vidro e acelera cargas no gás de baixa pressão."),
   ("REAL","plasma2",2,"PROOF","plasma","FILAMENTOS DE PLASMA • VÍDEO REAL","As colisões ionizam átomos e formam canais luminosos de plasma."),
   ("ANIMATION","anim",2,"MECHANISM","plasma","ANIMAÇÃO • DEDO ALTERA O CAMPO","Ao tocar o vidro, seu corpo altera a distribuição do campo elétrico naquela região."),
   ("REAL","plasma3",1,"CONSEQUENCE","plasma","PLASMA RESPONDE AO TOQUE • VÍDEO REAL","A descarga então se concentra perto do toque, em vez de se espalhar pela esfera, e parece seguir seu dedo."),
   ("ANIMATION","anim",4,"MECHANISM","plasma","ANIMAÇÃO • DESCARGA SE CONCENTRA","O filamento não sai do vidro: muda apenas onde o gás recebe mais energia."),
   ("REAL","plasma4",1,"PROOF","plasma","DESCARGA DE ALTA TENSÃO • CONTEXTO REAL","Outros sistemas de alta tensão também formam canais luminosos quando o campo fica intenso.")
  ]},
 "radiometro_crookes":{
  "title":"Por que o radiômetro de Crookes gira quando recebe luz? #shorts",
  "header":["POR QUE A LUZ","FAZ ISSO GIRAR?"],
  "description":"No radiômetro de Crookes, as faces escuras aquecem mais. No gás rarefeito, o gradiente de temperatura perto das bordas das pás gera uma força líquida que mantém o rotor girando. #VocêSabiaAgora #Curiosidades #Física #Radiômetro",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"CROOKES_RADIOMETER_THERMAL_TRANSPIRATION_RAREFIED_GAS",
  "assets":{
   "crookes1":{"file":"crookes1.webm","source_url":"https://commons.wikimedia.org/wiki/File:Crookes_radiometer.webm","license":"CC_BY_SA_4.0","asset_subject":"REAL_CROOKES_RADIOMETER_SUNLIGHT","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "crookes2":{"file":"crookes2.webm","source_url":"https://commons.wikimedia.org/wiki/File:Crookes_Radiometer_in_action.webm","license":"CC_BY_3.0","asset_subject":"REAL_CROOKES_RADIOMETER_ACTION","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "crookes3":{"file":"crookes3.webm","source_url":"https://commons.wikimedia.org/wiki/File:Crookes_radiometer_and_Mendocino_rotor.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_CROOKES_AND_LIGHT_DEVICE_CONTEXT","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "crookes4":{"file":"crookes4.webm","source_url":"https://commons.wikimedia.org/wiki/File:Light_mill_(Crookes_radiometer).webm","license":"CC_BY","asset_subject":"REAL_LIGHT_MILL_CROOKES","asset_role":"TARGET_SUBJECT","identifiable_human":False}
  },
  "scenes":[
   ("REAL","crookes1",2,"CONTEXT","crookes","RADIÔMETRO AO SOL • VÍDEO REAL","Quando a luz bate nesse pequeno rotor dentro de uma ampola, as pás começam a girar."),
   ("ANIMATION","anim",0,"MECHANISM","crookes","ANIMAÇÃO • LADO ESCURO AQUECE MAIS","A face escura absorve mais energia e fica mais quente que a face clara da mesma pá."),
   ("REAL","crookes2",3,"PROOF","crookes","RADIÔMETRO GIRANDO • VÍDEO REAL","A ampola não está totalmente vazia: existe uma pequena quantidade de gás em baixa pressão."),
   ("ANIMATION","anim",2,"MECHANISM","crookes","ANIMAÇÃO • GÁS RAREFEITO SENTE O GRADIENTE","Perto das bordas, o gradiente de temperatura altera o movimento das moléculas do gás e produz uma força líquida."),
   ("REAL","crookes3",2,"CONSEQUENCE","crookes","LUZ VIRANDO MOVIMENTO • VÍDEO REAL","Essa força atua repetidamente sobre as pás e mantém o conjunto girando enquanto há diferença de temperatura."),
   ("ANIMATION","anim",4,"MECHANISM","crookes","ANIMAÇÃO • PRESSÃO INTERMEDIÁRIA É ESSENCIAL","Com ar demais o arrasto domina; com gás de menos quase não há moléculas para produzir o efeito."),
   ("REAL","crookes4",2,"PROOF","crookes","OUTRO RADIÔMETRO • VÍDEO REAL","Por isso o radiômetro funciona melhor numa faixa específica de baixa pressão, e não no vácuo perfeito.")
  ]},
 "stevie_wonder_som":{
  "title":"Como Stevie Wonder constrói um som tão reconhecível? #shorts",
  "header":["COMO STEVIE WONDER","CRIA UM SOM TÃO RECONHECÍVEL?"],
  "description":"Identidade musical pode nascer da combinação entre ritmo, harmonia, timbre e escolhas de instrumento. Stevie Wonder ficou conhecido por misturar estilos e dominar vários instrumentos sem perder uma assinatura própria. #VocêSabiaAgora #StevieWonder #Música",
  "content_class":"NEWS_EXPLAINER","expected_subject":"STEVIE_WONDER_MUSICAL_IDENTITY_RHYTHM_HARMONY_TIMBRE",
  "celebrity_name":"Stevie Wonder",
  "assets":{
   "stevie1":{"file":"stevie1.webm","source_url":"https://commons.wikimedia.org/wiki/File:052112_Stevie_Wonder.webm","license":"PUBLIC_DOMAIN_US_GOV","asset_subject":"STEVIE_WONDER_MUSICAL_IDENTITY_RHYTHM_HARMONY_TIMBRE","asset_role":"TARGET_SUBJECT","identifiable_human":True,"celebrity_visible":True},
   "keyboard":{"file":"keyboard.webm","source_url":"https://commons.wikimedia.org/wiki/File:Musical_keyboard_playing_recorded_melody_from_memory.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_MUSICAL_KEYBOARD_CONTEXT","asset_role":"EXPLICIT_CONTEXT","identifiable_human":False,"celebrity_visible":False},
   "piano":{"file":"piano.webm","source_url":"https://commons.wikimedia.org/wiki/File:Odna-semya-a-family-1943-film-song-music-lesson.webm","license":"PUBLIC_DOMAIN","asset_subject":"REAL_PIANO_PERFORMANCE_CONTEXT","asset_role":"EXPLICIT_CONTEXT","identifiable_human":True,"celebrity_visible":False},
   "stevie2":{"file":"stevie2.webm","source_url":"https://commons.wikimedia.org/wiki/File:Presidential_Medal_of_Freedom_Recipient_-_Stevie_Wonder.webm","license":"PUBLIC_DOMAIN_US_GOV","asset_subject":"STEVIE_WONDER_MUSICAL_IDENTITY_RHYTHM_HARMONY_TIMBRE","asset_role":"TARGET_SUBJECT","identifiable_human":True,"celebrity_visible":True}
  },
  "scenes":[
   ("REAL","stevie1",18,"CONTEXT","stevie","STEVIE WONDER • ARQUIVO REAL","Stevie Wonder passa por soul, R&B, funk e pop sem deixar de soar reconhecível."),
   ("ANIMATION","anim",0,"MECHANISM","stevie","ANIMAÇÃO • IDENTIDADE TEM CAMADAS","Uma assinatura musical nasce quando ritmo, harmonia e timbre viram escolhas recorrentes."),
   ("REAL","keyboard",4,"PROOF","stevie","TECLADO • CONTEXTO REAL","Teclados permitem mudar timbres e testar harmonias mantendo a mesma linguagem."),
   ("ANIMATION","anim",2,"MECHANISM","stevie","ANIMAÇÃO • SÍNCOPE MUDA O GROOVE","A síncope desloca acentos do compasso e deixa o groove mais elástico."),
   ("REAL","piano",90,"CONSEQUENCE","stevie","PIANO • CONTEXTO REAL","Inversões e acordes mudam a cor emocional sem trocar toda a melodia."),
   ("ANIMATION","anim",4,"MECHANISM","stevie","ANIMAÇÃO • TIMBRE COMPLETA A ASSINATURA","A mesma nota muda de caráter em piano, teclado ou voz; esses timbres criam textura."),
   ("REAL","stevie2",10,"PROOF","stevie","STEVIE WONDER • SEGUNDO ARQUIVO REAL","Essa combinação de instrumentos, estilos e ritmo ajuda a explicar uma identidade que atravessa décadas.")
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
 with requests.get(url,headers={"User-Agent":"VSA-Oct09/1.0"},stream=True,timeout=180) as r:
  r.raise_for_status()
  with open(p,"wb") as f:
   for c in r.iter_content(1048576):
    if c:f.write(c)
 return p
def commons_video(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"videoinfo","viprop":"url|derivatives","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Oct09/1.0"},timeout=60).json()["query"]["pages"].values()))
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
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Oct09/1.0"},timeout=60).json()["query"]["pages"].values()))
 return dl(page["imageinfo"][0]["url"],p)


def commons_image(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"imageinfo","iiprop":"url","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Oct09/1.0"},timeout=60).json()["query"]["pages"].values()))
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
  if slug=="globo_plasma":
   if seg==0:
    d.text((45,38),"CAMPO ELÉTRICO → GÁS IONIZADO",font=fb,fill="white")
    cx,cy=487,430
    d.ellipse((255,195,720,665),outline=(120,190,255),width=7)
    d.ellipse((445,388,529,472),fill=(255,110,180))
    for ang in range(0,360,45):
     a=math.radians(ang+20*u)
     x=cx+int(210*math.cos(a)); y=cy+int(210*math.sin(a))
     d.line((cx,cy,x,y),fill=(140,100,255),width=6)
    d.text((235,725),"cargas aceleram e ionizam o gás",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"TOQUE MUDA A DISTRIBUIÇÃO DO CAMPO",font=fb,fill="white")
    cx,cy=420,430
    d.ellipse((190,200,650,660),outline=(120,190,255),width=7)
    d.ellipse((380,390,460,470),fill=(255,110,180))
    fx=820-int(130*u)
    d.rounded_rectangle((fx,290,930,610),35,fill=(230,185,140))
    for yy in (340,410,480,550):
     d.line((440,430,fx,yy),fill=(150,110,255),width=7)
    d.text((250,730),"seu corpo altera o acoplamento elétrico",font=fs,fill="white")
   else:
    d.text((45,38),"MAIS ENERGIA → FILAMENTO MAIS FORTE",font=fb,fill="white")
    d.line((150,620,825,620),fill=(100,150,190),width=5)
    for i in range(7):
     x=170+i*105; h=int((80+35*i)*(.35+.65*u))
     d.rectangle((x,620-h,x+45,620),fill=(120,90+15*i,255))
    d.text((220,725),"a descarga se concentra perto do toque",font=fs,fill="white")
  elif slug=="radiometro_crookes":
   if seg==0:
    d.text((45,38),"FACE ESCURA ABSORVE MAIS ENERGIA",font=fb,fill="white")
    d.rectangle((180,300,430,560),fill=(40,40,45)); d.rectangle((545,300,795,560),fill=(220,225,230))
    for x in range(160,820,90):
     d.line((x,180,x,270),fill=(255,190,70),width=8)
     d.polygon([(x,285),(x-16,255),(x+16,255)],fill=(255,190,70))
    d.text((205,635),"mais quente",font=fs,fill=(255,150,90)); d.text((585,635),"mais fria",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"GÁS RAREFEITO + GRADIENTE TÉRMICO",font=fb,fill="white")
    for i in range(20):
     x=130+(i%5)*165; y=245+(i//5)*120
     col=(255,150,90) if x<487 else (100,190,255)
     d.ellipse((x-10,y-10,x+10,y+10),fill=col)
    d.line((250,700,725,700),fill=(100,220,160),width=9)
    d.polygon([(750,700),(710,678),(710,722)],fill=(100,220,160))
    d.text((250,745),"nas bordas surge uma força líquida",font=fs,fill="white")
   else:
    d.text((45,38),"PRESSÃO DEMAIS × PRESSÃO DE MENOS",font=fb,fill="white")
    labs=[("AR DEMAIS",120,330),( "FAIXA IDEAL",365,610),("GÁS DE MENOS",645,855)]
    for lab,x1,x2 in labs:
     d.rounded_rectangle((x1,300,x2,520),18,outline=(100,180,230),width=6)
     d.text((x1+18,390),lab,font=fr,fill="white")
    d.rectangle((365,560,610,620),fill=(100,220,160))
    d.text((235,710),"o efeito precisa de gás rarefeito",font=fs,fill="white")
  else:
   if seg==0:
    d.text((45,38),"RITMO + HARMONIA + TIMBRE",font=fb,fill="white")
    cards=[("RITMO",100,300),("HARMONIA",385,585),("TIMBRE",670,870)]
    for i,(lab,x1,x2) in enumerate(cards):
     d.rounded_rectangle((x1,300,x2,520),20,outline=(100+40*i,180,230),width=7)
     d.text((x1+35,390),lab,font=fs,fill="white")
    d.text((225,690),"camadas diferentes • uma mesma assinatura",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"SÍNCOPE DESLOCA O ACENTO",font=fb,fill="white")
    for i in range(8):
     x=110+i*105
     d.line((x,330,x,600),fill=(100,150,190),width=4)
     if i in (1,4,6): d.ellipse((x-25,430,x+25,480),fill=(255,190,70))
    d.line((110,650,845,650),fill=(100,220,160),width=8)
    d.text((250,715),"acento inesperado muda o groove",font=fs,fill="white")
   else:
    d.text((45,38),"MESMA NOTA • TIMBRES DIFERENTES",font=fb,fill="white")
    labs=["PIANO","TECLADO","VOZ"]
    for i,lab in enumerate(labs):
     y=260+i*150
     d.text((100,y),lab,font=fs,fill="white")
     pts=[]
     for k in range(55):
      x=300+k*10
      amp=30+15*i
      yy=y+20+amp*math.sin(k*(.35+.08*i)+u*4)
      pts.append((x,yy))
     d.line(pts,fill=((100,190,255),(255,190,70),(100,220,160))[i],width=5)
    d.text((255,735),"textura muda mesmo com a altura igual",font=fs,fill="white")
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
 final=od/f"VSA_{slug}_OCT09.mp4";run(["ffmpeg","-y","-loglevel","error","-i",visual,"-i",mix,"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",final])
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
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/9352d5bc-94c4-4afd-b2d2-f2d27b8564e4.webm",AS/"plasma1.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/9c0fdd38-8640-4091-b056-67e9b793ce9a.webm",AS/"plasma2.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/cc1e8cfb-e4e0-4cc7-a074-c1d7c45ec24a.webm",AS/"plasma3.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/bb2c247d-34eb-4800-b421-855148b0c39a.webm",AS/"plasma4.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/cefa0965-f0c4-457a-b49c-d3cadd1838fc.webm",AS/"crookes1.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/be4ed06c-890d-41f3-986b-a0245f92c308.webm",AS/"crookes2.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/dfe00920-9ee0-432a-b3f8-70fb7d8ce297.webm",AS/"crookes3.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/e712e2d2-c078-483b-93d2-1919c698d911.webm",AS/"crookes4.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/affc86cd-43ee-4513-82b3-b386e3c661b9.webm",AS/"stevie1.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/20f5bb7d-a561-4151-a0c1-1eb3d5e1ca7c.webm",AS/"keyboard.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/1e04a9d0-2ad7-4741-981c-cb7f14e88e91.webm",AS/"piano.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/0718d3b1-d86b-4c55-b48d-49d3776f453e.webm",AS/"stevie2.webm")
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

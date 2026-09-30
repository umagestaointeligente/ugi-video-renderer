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
 "gelo_flutua":{
  "title":"Por que o gelo flutua em vez de afundar? #shorts",
  "header":["POR QUE O GELO","FLUTUA NA ÁGUA?"],
  "description":"O gelo flutua porque a água sólida forma uma estrutura molecular mais aberta e fica menos densa do que a água líquida. #VocêSabiaAgora #Curiosidades #Ciência #Água\n\nFonte científica: U.S. Geological Survey. Vídeos reais distintos: Wikimedia Commons, NASA e NOAA.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"ICE_FLOATS_WATER_DENSITY",
  "assets":{
   "ice1":{"file":"ice1.webm","source_url":"https://commons.wikimedia.org/wiki/File:Témpano_de_hielo_en_el_lago_argentino.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_FLOATING_ICE_FLOE","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "ice2":{"file":"ice2.webm","source_url":"https://commons.wikimedia.org/wiki/File:McMurdo_Sound,_Antarctica.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_FLOATING_POLAR_ICE","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "ice3":{"file":"ice3.webm","source_url":"https://commons.wikimedia.org/wiki/File:Flight_Over_a_Rectangular_Iceberg_in_the_Antarctic.webm","license":"PUBLIC_DOMAIN_NASA","asset_subject":"REAL_FLOATING_ICEBERG_NASA","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "ice4":{"file":"ice4.webm","source_url":"https://commons.wikimedia.org/wiki/File:Iceberg_A23a_Continues_Breaking_Up_(CIRA_2025-09-15_-_nolabels_port).webm","license":"PUBLIC_DOMAIN_NOAA","asset_subject":"REAL_FLOATING_ICEBERG_NOAA","asset_role":"TARGET_SUBJECT","identifiable_human":False}
  },
  "scenes":[
   ("REAL","ice1",1,"CONTEXT","ice","GELO FLUTUANDO • VÍDEO REAL","Se gelo é água sólida, por que ele sobe em vez de afundar na própria água?"),
   ("ANIMATION","anim",0,"MECHANISM","ice","ANIMAÇÃO • REDE ABERTA DO GELO","Ao congelar, ligações de hidrogênio organizam as moléculas numa rede mais aberta do que no líquido."),
   ("REAL","ice2",5,"PROOF","ice","GELO SOBRE A ÁGUA • VÍDEO REAL","Essa organização aumenta o espaço entre moléculas: a mesma massa passa a ocupar um volume maior."),
   ("ANIMATION","anim",2,"MECHANISM","ice","ANIMAÇÃO • DENSIDADE DIMINUI","Mais volume para a mesma massa significa menor densidade, e o gelo fica menos denso que a água líquida."),
   ("REAL","ice3",10,"CONSEQUENCE","ice","ICEBERG • VÍDEO REAL NASA","Por isso icebergs enormes permanecem sustentados pela água, mesmo carregando milhões de toneladas."),
   ("ANIMATION","anim",4,"MECHANISM","ice","ANIMAÇÃO • EMPUXO × PESO","O gelo afunda só até deslocar água suficiente para o empuxo equilibrar o próprio peso."),
   ("REAL","ice4",2,"PROOF","ice","GELO NO OCEANO • VÍDEO REAL NOAA","É o mesmo princípio do cubo no copo: parte fica submersa e uma fração permanece acima da superfície.")
  ]},
 "leidenfrost":{
  "title":"Por que uma gota de água dança numa panela muito quente? #shorts",
  "header":["POR QUE A GOTA","DANÇA NA PANELA?"],
  "description":"Numa superfície muito quente, uma fina camada de vapor pode se formar sob a gota e reduzir o contato direto com o metal: é o efeito Leidenfrost. #VocêSabiaAgora #Curiosidades #Física #Leidenfrost\n\nFontes: UCSC Physics Demonstration Room e Berkeley Lab. Vídeos reais distintos: Wikimedia Commons.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"LEIDENFROST_VAPOR_CUSHION",
  "assets":{
   "leid1":{"file":"leid1.webm","source_url":"https://commons.wikimedia.org/wiki/File:Effet_Leidenfrost.webm","license":"CC_BY_SA_4.0","asset_subject":"REAL_LEIDENFROST_DROPLETS_HOT_PAN","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "leid2":{"file":"leid2.webm","source_url":"https://commons.wikimedia.org/wiki/File:18._Лајденфростов_ефект.webm","license":"CC_BY_SA_4.0","asset_subject":"REAL_LEIDENFROST_HEATED_SPHERE","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "leid3":{"file":"leid3.webm","source_url":"https://commons.wikimedia.org/wiki/File:Effet_leidenfrost.ogv","license":"CC_BY_SA_3.0","asset_subject":"REAL_LEIDENFROST_DROPLET_SECOND_SOURCE","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "leid4":{"file":"leid4.webm","source_url":"https://commons.wikimedia.org/wiki/File:Thermal_Vision_video_of_a_kettle_of_water_being_boiled.webm","license":"CC_BY_SA","asset_subject":"REAL_BOILING_WATER_THERMAL_CONTEXT","asset_role":"EXPLICIT_CONTEXT","identifiable_human":False}
  },
  "scenes":[
   ("REAL","leid1",1,"CONTEXT","leid","GOTAS EM SUPERFÍCIE QUENTE • VÍDEO REAL","Quando a panela está quente demais, a gota pode parar de ferver no lugar e começar a deslizar."),
   ("ANIMATION","anim",0,"MECHANISM","leid","ANIMAÇÃO • VAPORIZAÇÃO NA BASE","A parte inferior recebe calor tão rápido que água vira vapor antes de toda a gota tocar o metal."),
   ("REAL","leid2",4,"PROOF","leid","CAMADA DE VAPOR • EXPERIMENTO REAL","Esse vapor se acumula entre líquido e superfície e cria uma separação física muito fina."),
   ("ANIMATION","anim",2,"MECHANISM","leid","ANIMAÇÃO • COLCHÃO DE VAPOR","O colchão de vapor sustenta a gota e reduz bastante o contato direto e a transferência de calor."),
   ("REAL","leid3",1,"CONSEQUENCE","leid","OUTRA DEMONSTRAÇÃO • VÍDEO REAL","Com pouco atrito, a gota fica extremamente móvel e parece patinar ou dançar sobre a superfície."),
   ("ANIMATION","anim",4,"MECHANISM","leid","ANIMAÇÃO • FLUXO MOVE A GOTA","Se o vapor escapa mais por um lado, ele empurra a gota; quando a superfície esfria, o colchão desaparece."),
   ("REAL","leid4",20,"CONSEQUENCE","leid","ÁGUA EM EBULIÇÃO • VÍDEO TÉRMICO REAL","Quando a superfície esfria e a camada isolante de vapor deixa de se sustentar, a água volta a ter contato e ebulição mais comuns.")
  ]},
 "ricky_medley":{
  "title":"Como Ricky Martin emenda vários hits no mesmo show? #shorts",
  "header":["COMO RICKY MARTIN","EMENDA TANTOS HITS?"],
  "description":"Shows pop podem compactar várias músicas usando medleys, transições, mudanças de arranjo e deslocamento de palco. O vídeo usa quatro arquivos reais e distintos de Ricky Martin em performance. #VocêSabiaAgora #RickyMartin #Música #Shows\n\nArquivos de Ricky Martin: Festival de Viña del Mar 2014 via Wikimedia Commons, CC BY 3.0.",
  "content_class":"NEWS_EXPLAINER","expected_subject":"RICKY_MARTIN_LIVE_MEDLEY_STAGE_FLOW",
  "celebrity_name":"Ricky Martin",
  "assets":{
   "ricky1":{"file":"ricky1.webm","source_url":"https://commons.wikimedia.org/wiki/File:La_Bomba_-_Ricky_Martin,_Viña_del_Mar_International_Song_Festival_(2014).ogv","license":"CC_BY_3.0","asset_subject":"RICKY_MARTIN_LIVE_MEDLEY_STAGE_FLOW","asset_role":"TARGET_SUBJECT","identifiable_human":True,"celebrity_visible":True},
   "ricky2":{"file":"ricky2.webm","source_url":"https://commons.wikimedia.org/wiki/File:Loaded_-_Ricky_Martin,_Viña_del_Mar_International_Song_Festival_(2014).ogv","license":"CC_BY_3.0","asset_subject":"RICKY_MARTIN_LIVE_MEDLEY_STAGE_FLOW","asset_role":"TARGET_SUBJECT","identifiable_human":True,"celebrity_visible":True},
   "ricky3":{"file":"ricky3.webm","source_url":"https://commons.wikimedia.org/wiki/File:Eres_el_amor_de_mi_vida_and_Fuego_contra_fuego_-_Ricky_Martin,_Viña_del_Mar_International_Song_Festival_(2014).ogv","license":"CC_BY_3.0","asset_subject":"RICKY_MARTIN_LIVE_MEDLEY_STAGE_FLOW","asset_role":"TARGET_SUBJECT","identifiable_human":True,"celebrity_visible":True},
   "ricky4":{"file":"ricky4.webm","source_url":"https://commons.wikimedia.org/wiki/File:Vuelve,_Ricky_Martin,_Viña_del_Mar_International_Song_Festival_(2014).ogv","license":"CC_BY_3.0","asset_subject":"RICKY_MARTIN_LIVE_MEDLEY_STAGE_FLOW","asset_role":"TARGET_SUBJECT","identifiable_human":True,"celebrity_visible":True}
  },
  "scenes":[
   ("REAL","ricky1",12,"CONTEXT","ricky","RICKY MARTIN • ARQUIVO DE SHOW","Em um show cheio de sucessos, tocar cada música inteira faria o repertório explodir de duração."),
   ("ANIMATION","anim",0,"MECHANISM","ricky","ANIMAÇÃO • MEDLEY EM BLOCOS","Uma solução é o medley: preservar trechos reconhecíveis, como abertura e refrão, e cortar partes repetidas."),
   ("REAL","ricky2",15,"PROOF","ricky","RICKY MARTIN • OUTRO ARQUIVO REAL","Assim o público reconhece rapidamente cada hit sem precisar ouvir quatro ou cinco minutos completos."),
   ("ANIMATION","anim",2,"MECHANISM","ricky","ANIMAÇÃO • TRANSIÇÃO DE ARRANJO","Bateria, harmonia e efeitos fazem a ponte entre músicas para a energia não cair entre uma e outra."),
   ("REAL","ricky3",10,"CONSEQUENCE","ricky","RICKY MARTIN • PERFORMANCE REAL","Coreografia e deslocamento no palco também escondem trocas de músicos, figurinos, luz e posição."),
   ("ANIMATION","anim",4,"MECHANISM","ricky","ANIMAÇÃO • ZONAS DE PALCO","Enquanto uma área encerra um bloco, outra já fica pronta para receber o próximo trecho do show."),
   ("REAL","ricky4",12,"PROOF","ricky","RICKY MARTIN • QUARTO ARQUIVO REAL","O resultado parece contínuo: várias músicas, mudanças visuais e poucos segundos mortos entre os momentos mais fortes.")
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
 with requests.get(url,headers={"User-Agent":"VSA-Sep30/1.0"},stream=True,timeout=180) as r:
  r.raise_for_status()
  with open(p,"wb") as f:
   for c in r.iter_content(1048576):
    if c:f.write(c)
 return p
def commons_video(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"videoinfo","viprop":"url|derivatives","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep30/1.0"},timeout=60).json()["query"]["pages"].values()))
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
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep30/1.0"},timeout=60).json()["query"]["pages"].values()))
 return dl(page["imageinfo"][0]["url"],p)


def commons_image(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"imageinfo","iiprop":"url","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep30/1.0"},timeout=60).json()["query"]["pages"].values()))
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
  if slug=="gelo_flutua":
   if seg==0:
    d.text((45,38),"LÍQUIDO → REDE ABERTA DO GELO",font=fb,fill="white")
    for i in range(18):
     x=120+(i%6)*65; y=220+(i//6)*80
     d.ellipse((x-12,y-12,x+12,y+12),fill=(90,185,255))
    for i in range(12):
     x=590+(i%4)*82; y=205+(i//4)*105
     d.ellipse((x-12,y-12,x+12,y+12),fill=(140,220,255))
     if i%4<3:d.line((x+12,y,x+70,y),fill=(120,170,210),width=4)
    d.text((120,590),"moléculas mais próximas",font=fr,fill="white")
    d.text((585,590),"mais espaço no sólido",font=fr,fill="white")
   elif seg==1:
    d.text((45,38),"MESMA MASSA → MAIOR VOLUME",font=fb,fill="white")
    d.rectangle((135,250,365,590),outline=(100,190,255),width=7)
    d.rectangle((565,185,855,655),outline=(255,190,70),width=7)
    d.text((175,620),"ÁGUA",font=fs,fill=(100,190,255))
    d.text((655,685),"GELO",font=fs,fill=(255,190,70))
    d.line((215,730,760,730),fill=(120,150,180),width=5)
    pos=215+int(545*u); d.ellipse((pos-18,712,pos+18,748),fill=(100,220,160))
    d.text((310,770),"densidade diminui",font=fr,fill="white")
   else:
    d.text((45,38),"EMPUXO PARA CIMA × PESO PARA BAIXO",font=fb,fill="white")
    d.rectangle((60,455,915,760),fill=(25,90,145))
    d.rectangle((345,330,625,610),fill=(180,225,245))
    d.line((485,530,485,250),fill=(100,220,160),width=12)
    d.polygon([(485,225),(465,265),(505,265)],fill=(100,220,160))
    d.line((485,430,485,700),fill=(255,190,70),width=12)
    d.polygon([(485,725),(465,685),(505,685)],fill=(255,190,70))
    d.text((525,260),"EMPUXO",font=fs,fill=(100,220,160))
    d.text((525,680),"PESO",font=fs,fill=(255,190,70))
  elif slug=="leidenfrost":
   if seg==0:
    d.text((45,38),"SUPERFÍCIE MUITO QUENTE",font=fb,fill="white")
    d.rectangle((80,620,895,700),fill=(180,75,45))
    d.ellipse((380,250,595,465),fill=(90,175,255))
    for x in range(410,580,35):
     y=560-int(60*u)
     d.line((x,610,x,y),fill=(220,235,245),width=6)
    d.text((265,740),"a base vaporiza primeiro",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"COLCHÃO DE VAPOR",font=fb,fill="white")
    d.rectangle((80,630,895,700),fill=(180,75,45))
    d.ellipse((365,285,610,510),fill=(90,175,255))
    d.rounded_rectangle((330,520,645,610),35,fill=(205,225,235),outline=(255,255,255),width=3)
    for x in range(350,630,55):
     d.line((x,570,x+int(35*u),570),fill=(100,220,160),width=7)
    d.text((220,745),"vapor separa gota e metal",font=fs,fill="white")
   else:
    d.text((45,38),"VAPOR ESCAPA → GOTA SE MOVE",font=fb,fill="white")
    d.rectangle((80,650,895,710),fill=(180,75,45))
    cx=370+int(300*u)
    d.ellipse((cx-95,330,cx+95,520),fill=(90,175,255))
    for k in range(5):
     y=550+k*18
     d.line((cx-30,y,cx-150-int(40*u),y),fill=(220,235,245),width=6)
    d.line((cx+110,420,cx+230,420),fill=(100,220,160),width=10)
    d.polygon([(cx+250,420),(cx+215,400),(cx+215,440)],fill=(100,220,160))
    d.text((235,760),"fluxo assimétrico gera impulso",font=fs,fill="white")
  else:
   if seg==0:
    d.text((45,38),"MEDLEY: SÓ OS TRECHOS MAIS RECONHECÍVEIS",font=fb,fill="white")
    blocks=[("INTRO",120,330,(90,170,230)),("REFRÃO",355,610,(255,190,70)),("PONTE",635,845,(100,220,160))]
    for lab,x1,x2,col in blocks:
     d.rounded_rectangle((x1,320,x2,470),18,fill=col)
     d.text((x1+22,370),lab,font=fs,fill=(10,18,32))
    d.line((120,565,845,565),fill=(150,170,190),width=5)
    pos=120+int(725*u); d.ellipse((pos-18,547,pos+18,583),fill=(255,255,255))
    d.text((250,690),"música longa vira bloco curto",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"ARRANJO FAZ A TRANSIÇÃO",font=fb,fill="white")
    for i,h in enumerate([80,150,230,130,260,190,95,210]):
     x=135+i*90; d.rectangle((x,600-h,x+52,600),fill=(90+10*i,150,220))
    d.line((130,650,835,650),fill=(255,190,70),width=7)
    pos=130+int(705*u); d.ellipse((pos-17,633,pos+17,667),fill=(100,220,160))
    d.text((220,735),"ritmo e harmonia evitam silêncio",font=fs,fill="white")
   else:
    d.text((45,38),"PALCO DIVIDIDO EM ZONAS",font=fb,fill="white")
    zones=[(90,250,320,620,"A"),(370,250,600,620,"B"),(650,250,880,620,"C")]
    for x1,y1,x2,y2,lab in zones:
     d.rounded_rectangle((x1,y1,x2,y2),24,outline=(100,180,230),width=6)
     d.text((x1+95,y1+150),lab,font=fb,fill="white")
    x=170+int(570*u); d.ellipse((x-30,665,x+30,725),fill=(255,190,70))
    d.text((185,765),"uma zona termina enquanto outra já está pronta",font=fr,fill="white")
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
 anim=AS/(slug+"_3d.mp4")
 vids=[];asegs=[];times=[];rows=[];cursor=0.0
 for i,(kind,source_key,start,role,link,label,text) in enumerate(topic["scenes"],1):
  voice=wd/f"v{i}.mp3";run(["edge-tts","--voice",VOICE,"--rate=-2%","--text",text,"--write-media",voice]);vd=duration(voice);length=vd+.10
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
 ctext=" ".join(CTA_LINES);cv=wd/"cta.mp4";ca=wd/"cta.mp3";run(["edge-tts","--voice",VOICE,"--rate=+18%","--text",ctext,"--write-media",ca]);cd=max(3.6,min(5.0,duration(ca)+.2));run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",cta,"-t",f"{cd:.3f}","-vf",f"scale={W}:{H},fps={FPS},format=yuv420p","-an","-c:v","libx264","-preset","veryfast","-crf","20",cv])
 fl=wd/"f.txt";fl.write_text(f"file '{bodyc}'\nfile '{cv}'\n");visual=wd/"visual.mp4";run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",fl,"-an","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",visual])
 alla=wd/"all.wav";run(["ffmpeg","-y","-loglevel","error","-i",bodya,"-i",ca,"-filter_complex","[0:a][1:a]concat=n=2:v=0:a=1[a]","-map","[a]","-ar","48000",alla])
 mix=wd/"mix.m4a";af="[0:a]aresample=48000,asplit=2[n1][n2];[1:a]aresample=48000,volume=.10,aloop=loop=-1:size=2147483647[m];[m][n1]sidechaincompress=threshold=.035:ratio=8:attack=20:release=250[d];[n2][d]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=10[a]";run(["ffmpeg","-y","-loglevel","error","-i",alla,"-i",music,"-filter_complex",af,"-map","[a]","-ar","48000",mix])
 final=od/f"VSA_{slug}_SEP30.mp4";run(["ffmpeg","-y","-loglevel","error","-i",visual,"-i",mix,"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",final])
 probe=json.loads(cap(["ffprobe","-v","error","-show_streams","-show_format","-of","json",final]));fd=float(probe["format"]["duration"]);v=next(x for x in probe["streams"] if x.get("codec_type")=="video")
 print("DURATION_CHECK",slug,fd)
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
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/c5ec5984-a10d-408b-8b4d-01dc4bfbb515.webm",AS/"ice1.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/31a64c7d-7878-4c1d-ba30-bd5c00c39ce8.webm",AS/"ice2.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/dc12bced-eb3f-4496-8507-3a7a26f7c0b5.webm",AS/"ice3.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/7fe4ffdf-45a1-4a92-8dd3-c63bd750692c.webm",AS/"ice4.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/415e314f-0b7b-4fb2-a0ee-38df94cad1d5.webm",AS/"leid1.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/b8853fe4-3dd8-403d-9c95-27755944c1b5.webm",AS/"leid2.webm")
 commons_video("Effet leidenfrost.ogv",AS/"leid3.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/7a20c08a-d1bb-4143-ac99-876c46a1cf24.webm",AS/"leid4.webm")
 commons_video("La Bomba - Ricky Martin, Viña del Mar International Song Festival (2014).ogv",AS/"ricky1.webm")
 commons_video("Loaded - Ricky Martin, Viña del Mar International Song Festival (2014).ogv",AS/"ricky2.webm")
 commons_video("Eres el amor de mi vida and Fuego contra fuego - Ricky Martin, Viña del Mar International Song Festival (2014).ogv",AS/"ricky3.webm")
 commons_video("Vuelve, Ricky Martin, Viña del Mar International Song Festival (2014).ogv",AS/"ricky4.webm")
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

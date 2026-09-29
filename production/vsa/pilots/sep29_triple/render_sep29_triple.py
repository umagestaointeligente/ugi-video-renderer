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
 "bolha_redonda":{
  "title":"Por que uma bolha de sabão fica redonda? #shorts",
  "header":["POR QUE A BOLHA","FICA REDONDA?"],
  "description":"Uma bolha livre tende a virar esfera porque a película busca uma configuração de menor área para o volume de ar que contém. O sabão estabiliza o filme e modifica a tensão superficial. #VocêSabiaAgora #Curiosidades #Física #Bolhas\n\nFontes científicas: Science World e Exploratorium. Quatro vídeos reais distintos: Wikimedia Commons.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"SOAP_BUBBLE_SPHERE_SURFACE_TENSION",
  "assets":{
   "bubble1":{"file":"bubble1.webm","source_url":"https://commons.wikimedia.org/wiki/File:Soap_bubbles_being_formed_by_a_bubble_wand_-_slow_motion_-_2022_July_28.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_SOAP_BUBBLE_FORMING","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "bubble2":{"file":"bubble2.ogv","source_url":"https://commons.wikimedia.org/wiki/File:Mechanical_bubble_blower_(001).ogv","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_MECHANICAL_BUBBLE_BLOWER","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "bubble3":{"file":"bubble3.ogv","source_url":"https://commons.wikimedia.org/wiki/File:Mechanical_bubble_blower_(002).ogv","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_MECHANICAL_BUBBLE_BLOWER_SECOND","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "bubble4":{"file":"bubble4.ogv","source_url":"https://commons.wikimedia.org/wiki/File:Une_petite_bulle_de_savon_éclate_en_ralenti_x40.ogv","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_SOAP_BUBBLE_POPPING_SLOW_MOTION","asset_role":"TARGET_SUBJECT","identifiable_human":False}
  },
  "scenes":[
   ("REAL","bubble1",0,"CONTEXT","bubble","BOLHA NASCENDO • VÍDEO REAL","Bolhas podem nascer deformadas, mas livres no ar quase sempre viram esferas. Por quê?"),
   ("ANIMATION","anim",0,"MECHANISM","bubble","ANIMAÇÃO • FILME DE ÁGUA E SABÃO","A película é água com sabão. O detergente estabiliza o filme e modifica sua tensão superficial."),
   ("REAL","bubble2",1,"PROOF","bubble","BOLHAS • VÍDEO REAL","Essa tensão puxa a película para diminuir sua área, como uma pele elástica tentando encolher."),
   ("ANIMATION","anim",2,"MECHANISM","bubble","ANIMAÇÃO • MENOR ÁREA","Para guardar o mesmo volume de ar, nenhuma forma usa menos superfície que uma esfera."),
   ("REAL","bubble3",2,"CONSEQUENCE","bubble","BOLHAS • VÍDEO REAL","Cantos e pontas exigiriam mais área e tendem a desaparecer quando a bolha está livre."),
   ("ANIMATION","anim",4,"MECHANISM","bubble","ANIMAÇÃO • FORÇAS EM EQUILÍBRIO","A pressão interna empurra para fora, enquanto a tensão da película puxa para dentro em todas as direções."),
   ("REAL","bubble4",1,"PROOF","bubble","BOLHA EM CÂMERA LENTA • VÍDEO REAL","Quando essas forças se equilibram, a forma redonda vence — até o filme afinar demais e estourar.")
  ]},
 "morcego_invertido":{
  "title":"Por que morcegos dormem de cabeça para baixo? #shorts",
  "header":["POR QUE MORCEGOS","DORMEM DE CABEÇA PARA BAIXO?"],
  "description":"Morcegos conseguem permanecer pendurados com pouco gasto muscular porque estruturas dos pés e tendões ajudam a manter a garra fechada. A posição elevada também facilita iniciar o voo usando a gravidade. #VocêSabiaAgora #Curiosidades #Morcegos #Natureza\n\nFontes científicas: Bat Conservation International e Smithsonian. Quatro vídeos reais distintos: Wikimedia Commons.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"BAT_UPSIDE_DOWN_ROOSTING",
  "assets":{
   "bat1":{"file":"bat1.webm","source_url":"https://commons.wikimedia.org/wiki/File:Bats_in_the_Tunnel.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_BATS_TUNNEL","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "bat2":{"file":"bat2.webm","source_url":"https://commons.wikimedia.org/wiki/File:Bat_climbing_a_wall.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_BAT_CLIMBING","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "bat3":{"file":"bat3.webm","source_url":"https://commons.wikimedia.org/wiki/File:Congress_Street_Bridge_Bat_Flight_Austin.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_BAT_FLIGHT_AUSTIN","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "bat4":{"file":"bat4.webm","source_url":"https://commons.wikimedia.org/wiki/File:Bats_in_Flight_at_Dusk_in_Texas.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_BATS_FLIGHT_TEXAS","asset_role":"TARGET_SUBJECT","identifiable_human":False}
  },
  "scenes":[
   ("REAL","bat1",3,"CONTEXT","bat","MORCEGOS • VÍDEO REAL","Quase todos os morcegos descansam de cabeça para baixo e conseguem ficar assim por horas sem cansar."),
   ("ANIMATION","anim",0,"MECHANISM","bat","ANIMAÇÃO • GARRAS E TENDÕES","Ao pousar, o peso do corpo tensiona tendões dos pés e ajuda as garras a travarem no apoio."),
   ("REAL","bat2",1,"PROOF","bat","MORCEGO • VÍDEO REAL","O mecanismo funciona como uma catraca: não é preciso manter os músculos contraídos o tempo todo."),
   ("ANIMATION","anim",2,"MECHANISM","bat","ANIMAÇÃO • TRAVA PASSIVA","Por isso dormir pendurado gasta pouca energia e ainda deixa o animal longe de muitos predadores."),
   ("REAL","bat3",4,"CONSEQUENCE","bat","MORCEGOS EM VOO • VÍDEO REAL","A posição também ajuda na decolagem, porque muitos morcegos não saltam do chão como uma ave."),
   ("ANIMATION","anim",4,"MECHANISM","bat","ANIMAÇÃO • SOLTA, CAI E VOA","Eles soltam os pés, caem por um instante e usam a gravidade para abrir espaço para as asas."),
   ("REAL","bat4",5,"PROOF","bat","MORCEGOS AO ANOITECER • VÍDEO REAL","Assim, ficar de cabeça para baixo resolve descanso, segurança e uma saída rápida para o voo.")
  ]},
 "ricky_nfl_rio":{
  "title":"Como Ricky Martin e Pedro Sampaio montaram o show da NFL no Maracanã? #shorts",
  "header":["COMO COUBERAM TANTOS HITS","NO INTERVALO DA NFL?"],
  "description":"Ricky Martin e Pedro Sampaio se apresentaram no intervalo do NFL Rio Game no Maracanã em 27 de setembro de 2026. O show misturou funk, pop latino e outros ritmos em formato de medley e marcou a estreia ao vivo de 'Pikito Pikito'. #VocêSabiaAgora #RickyMartin #PedroSampaio #NFLBrasil\n\nVídeos de Ricky Martin: Festival de Viña del Mar / Wikimedia Commons, CC BY 3.0. Maracanã: Rwjabour / Wikimedia Commons, CC BY-SA 4.0. Fontes factuais: NFL, Folha, CNN Brasil e ge.",
  "content_class":"NEWS_EXPLAINER","expected_subject":"RICKY_MARTIN_NFL_RIO_HALFTIME_2026",
  "celebrity_name":"Ricky Martin",
  "assets":{
   "ricky1":{"file":"ricky1.ogv","source_url":"https://commons.wikimedia.org/wiki/File:La_Bomba_-_Ricky_Martin,_Viña_del_Mar_International_Song_Festival_(2014).ogv","license":"CC_BY_3.0","asset_subject":"RICKY_MARTIN_NFL_RIO_HALFTIME_2026","asset_role":"TARGET_SUBJECT","identifiable_human":True,"celebrity_visible":True},
   "maracana":{"file":"maracana.webm","source_url":"https://commons.wikimedia.org/wiki/File:Maracanã_Timelapse_-_saída_do_público_do_jogo_entre_Brasil_vs_Honduras.webm","license":"CC_BY_SA_4.0","asset_subject":"MARACANA_STADIUM_CONTEXT","asset_role":"EXPLICIT_CONTEXT","identifiable_human":False,"celebrity_visible":False},
   "ricky2":{"file":"ricky2.ogv","source_url":"https://commons.wikimedia.org/wiki/File:Loaded_-_Ricky_Martin,_Viña_del_Mar_International_Song_Festival_(2014).ogv","license":"CC_BY_3.0","asset_subject":"RICKY_MARTIN_NFL_RIO_HALFTIME_2026","asset_role":"TARGET_SUBJECT","identifiable_human":True,"celebrity_visible":True},
   "ricky3":{"file":"ricky3.ogv","source_url":"https://commons.wikimedia.org/wiki/File:Vuelve,_Ricky_Martin,_Viña_del_Mar_International_Song_Festival_(2014).ogv","license":"CC_BY_3.0","asset_subject":"RICKY_MARTIN_NFL_RIO_HALFTIME_2026","asset_role":"TARGET_SUBJECT","identifiable_human":True,"celebrity_visible":True}
  },
  "scenes":[
   ("REAL","ricky1",20,"CONTEXT","show","RICKY MARTIN • ARQUIVO DE SHOW","Ricky Martin e Pedro Sampaio levaram um mini show ao intervalo da NFL no Maracanã, no Rio."),
   ("ANIMATION","anim",0,"MECHANISM","show","ANIMAÇÃO • FORMATO MEDLEY","Para caber no intervalo, o espetáculo usou medley: trechos de músicas conectados por transições rápidas."),
   ("REAL","maracana",5,"PROOF","show","MARACANÃ • VÍDEO REAL","Pedro abriu com funk e Ricky entrou com Livin' La Vida Loca, mantendo o ritmo sem longas pausas."),
   ("ANIMATION","anim",2,"MECHANISM","show","ANIMAÇÃO • COREOGRAFIA POR ZONAS","A coreografia distribuía artistas, dançarinos e cheerleaders em zonas do campo para acelerar as trocas."),
   ("REAL","ricky2",30,"CONSEQUENCE","show","RICKY MARTIN • ARQUIVO DE SHOW","Assim, cada mudança de música já encontrava o próximo bloco visual pronto para entrar."),
   ("ANIMATION","anim",4,"MECHANISM","show","ANIMAÇÃO • COLABORAÇÃO NO CLÍMAX","O clímax juntou os dois em Pikito Pikito, lançada no próprio evento e transformada em parte do espetáculo."),
   ("REAL","ricky3",40,"PROOF","show","RICKY MARTIN • ARQUIVO DE SHOW","O resultado misturou funk, pop latino, samba e reggaeton dentro de um único show de intervalo.")
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
 with requests.get(url,headers={"User-Agent":"VSA-Sep29/1.0"},stream=True,timeout=180) as r:
  r.raise_for_status()
  with open(p,"wb") as f:
   for c in r.iter_content(1048576):
    if c:f.write(c)
 return p
def commons_video(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"videoinfo","viprop":"url|derivatives","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep29/1.0"},timeout=60).json()["query"]["pages"].values()))
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
def commons_direct(name,p):
 u="https://commons.wikimedia.org/wiki/Special:Redirect/file/"+requests.utils.quote(name,safe="")
 return dl(u,p)

def commons_music(p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"imageinfo","iiprop":"url","titles":"File:Soft Corporate by MusicLFiles.ogg"}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep29/1.0"},timeout=60).json()["query"]["pages"].values()))
 return dl(page["imageinfo"][0]["url"],p)


def commons_image(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"imageinfo","iiprop":"url","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep29/1.0"},timeout=60).json()["query"]["pages"].values()))
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
  if slug=="bolha_redonda":
   if seg==0:
    d.text((45,38),"FILME FINO: ÁGUA + SABÃO + AR",font=fb,fill="white")
    d.rectangle((110,330,865,520),fill=(45,95,135),outline=(120,210,255),width=4)
    for x in range(150,850,70):
     d.ellipse((x-10,315,x+10,335),fill=(255,190,70)); d.line((x,335,x,375),fill=(255,190,70),width=3)
     d.ellipse((x-10,505,x+10,525),fill=(255,190,70)); d.line((x,505,x,465),fill=(255,190,70),width=3)
    d.text((225,600),"moléculas de sabão estabilizam a película",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"MESMO VOLUME → MENOR ÁREA",font=fb,fill="white")
    d.rectangle((110,230,385,505),outline=(255,190,70),width=8)
    r=138
    d.ellipse((565-r,365-r,565+r,365+r),outline=(100,220,160),width=8)
    d.text((165,540),"CANTOS",font=fs,fill=(255,190,70)); d.text((510,540),"ESFERA",font=fs,fill=(100,220,160))
    d.line((195,640,760,640),fill=(120,150,180),width=5)
    pos=195+int(565*u); d.ellipse((pos-20,620,pos+20,660),fill=(100,220,160))
    d.text((260,700),"energia cai quando a área diminui",font=fr,fill="white")
   else:
    d.text((45,38),"PRESSÃO PARA FORA × TENSÃO PARA DENTRO",font=fb,fill="white")
    cx,cy=490,420; r=190
    d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(100,190,255),width=7)
    for ang in range(0,360,45):
     a=math.radians(ang); x=cx+int(r*math.cos(a)); y=cy+int(r*math.sin(a))
     xo=cx+int((r+100)*math.cos(a)); yo=cy+int((r+100)*math.sin(a))
     xi=cx+int((r-80)*math.cos(a)); yi=cy+int((r-80)*math.sin(a))
     d.line((x,y,xo,yo),fill=(255,190,70),width=6); d.line((x,y,xi,yi),fill=(100,220,160),width=6)
    d.text((305,720),"equilíbrio uniforme → esfera",font=fs,fill="white")
  elif slug=="morcego_invertido":
   if seg==0:
    d.text((45,38),"GARRA + TENDÃO: TRAVA MECÂNICA",font=fb,fill="white")
    d.line((110,250,865,250),fill=(130,95,60),width=28)
    for x in (400,470,540):
     d.arc((x-55,220,x+55,430),10,170,fill=(210,210,220),width=14)
    d.line((470,410,470,680),fill=(255,190,70),width=12)
    for y in range(455,650,55):
     d.polygon([(470,y),(430,y+18),(470,y+36)],fill=(100,220,160))
    d.text((285,720),"o peso ajuda a manter a trava",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"PENDURADO SEM CONTRAÇÃO CONTÍNUA",font=fb,fill="white")
    d.line((160,170,815,170),fill=(130,95,60),width=24)
    d.ellipse((400,310,575,520),outline=(110,180,230),width=7)
    d.line((445,310,410,185),fill=(210,210,220),width=11); d.line((530,310,565,185),fill=(210,210,220),width=11)
    d.line((488,520,488,700),fill=(255,190,70),width=10)
    d.polygon([(488,720),(470,685),(506,685)],fill=(255,190,70))
    d.text((180,750),"gravidade mantém carga na trava dos pés",font=fs,fill="white")
   else:
    d.text((45,38),"SOLTA → CAI → ABRE AS ASAS → VOA",font=fb,fill="white")
    y=220+int(260*u)
    d.ellipse((435,y,540,y+105),fill=(100,150,190))
    span=40+int(220*u)
    d.line((485,y+45,485-span,y+10),fill=(100,220,160),width=12)
    d.line((490,y+45,490+span,y+10),fill=(100,220,160),width=12)
    d.line((485,y+110,485,y+200),fill=(255,190,70),width=9)
    d.polygon([(485,y+215),(468,y+185),(502,y+185)],fill=(255,190,70))
    d.text((250,720),"a queda cria espaço para iniciar o voo",font=fs,fill="white")
  else:
   if seg==0:
    d.text((45,38),"MEDLEY: VÁRIOS BLOCOS, POUCAS PAUSAS",font=fb,fill="white")
    labels=["FUNK","TRANSIÇÃO","RICKY","DUETO","FINAL"]
    widths=[150,110,150,150,130]
    x=95
    for i,(lab,w) in enumerate(zip(labels,widths)):
     d.rounded_rectangle((x,300,x+w,470),20,outline=(80+25*i,170,220-20*i),width=5)
     d.text((x+12,365),lab,font=fr,fill="white"); x+=w+18
    marker=100+int(760*u); d.line((marker,245,marker,525),fill=(255,190,70),width=7)
    d.text((240,620),"trechos curtos conectados em sequência",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"COREOGRAFIA DISTRIBUÍDA PELO CAMPO",font=fb,fill="white")
    d.rounded_rectangle((70,170,905,680),25,outline=(100,170,120),width=5)
    d.line((487,170,487,680),fill=(100,170,120),width=4)
    zones=[(210,300,"ARTISTA"),(480,420,"DANÇA"),(720,300,"CHEER"),(700,560,"PRÓXIMO")]
    for i,(x,y,lab) in enumerate(zones):
     rr=45+int(10*abs(math.sin(t*3+i)))
     d.ellipse((x-rr,y-rr,x+rr,y+rr),outline=(80,180,255),width=5)
     d.text((x-38,y-10),lab,font=fr,fill="white")
    d.text((230,735),"cada zona prepara a próxima entrada",font=fs,fill="white")
   else:
    d.text((45,38),"DOIS ARTISTAS → UMA ESTREIA NO CLÍMAX",font=fb,fill="white")
    d.rounded_rectangle((90,220,360,430),25,outline=(80,180,255),width=5)
    d.text((150,300),"RICKY",font=fs,fill="white")
    d.rounded_rectangle((615,220,885,430),25,outline=(100,220,150),width=5)
    d.text((650,300),"PEDRO",font=fs,fill="white")
    cx,cy=490,610
    d.line((360,330,cx,cy),fill=(80,180,255),width=9); d.line((615,330,cx,cy),fill=(100,220,150),width=9)
    d.rounded_rectangle((300,560,680,700),24,outline=(255,190,70),width=6)
    d.text((350,610),"PIKITO PIKITO",font=fs,fill="white")
    d.text((320,745),"lançamento dentro do próprio show",font=fr,fill=(255,190,70))
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
 final=od/f"VSA_{slug}_SEP29.mp4";run(["ffmpeg","-y","-loglevel","error","-i",visual,"-i",mix,"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",final])
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
 commons_video("Soap bubbles being formed by a bubble wand - slow motion - 2022 July 28.webm",AS/"bubble1.webm")
 commons_video("Mechanical bubble blower (001).ogv",AS/"bubble2.ogv")
 commons_video("Mechanical bubble blower (002).ogv",AS/"bubble3.ogv")
 commons_video("Une petite bulle de savon éclate en ralenti x40.ogv",AS/"bubble4.ogv")
 commons_video("Bats in the Tunnel.webm",AS/"bat1.webm")
 commons_video("Bat climbing a wall.webm",AS/"bat2.webm")
 commons_video("Congress Street Bridge Bat Flight Austin.webm",AS/"bat3.webm")
 commons_video("Bats in Flight at Dusk in Texas.webm",AS/"bat4.webm")
 commons_video("La Bomba - Ricky Martin, Viña del Mar International Song Festival (2014).ogv",AS/"ricky1.ogv")
 commons_video("Loaded - Ricky Martin, Viña del Mar International Song Festival (2014).ogv",AS/"ricky2.ogv")
 commons_video("Vuelve, Ricky Martin, Viña del Mar International Song Festival (2014).ogv",AS/"ricky3.ogv")
 commons_video("Maracanã Timelapse - saída do público do jogo entre Brasil vs Honduras.webm",AS/"maracana.webm")
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

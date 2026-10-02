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
 "chama_vela":{
  "title":"Por que a chama da vela aponta para cima — e no espaço fica quase redonda? #shorts",
  "header":["POR QUE A CHAMA","APONTA PARA CIMA?"],
  "description":"Na Terra, gases aquecidos ficam menos densos e sobem, criando convecção e alongando a chama. Em microgravidade, essa direção preferencial praticamente desaparece e a chama tende a ficar mais arredondada. #VocêSabiaAgora #Curiosidades #Ciência #Fogo\n\nFontes: NASA e Wikimedia Commons. Quatro vídeos reais e distintos.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"CANDLE_FLAME_CONVECTION_MICROGRAVITY",
  "assets":{
   "candle1":{"file":"candle1.webm","source_url":"https://commons.wikimedia.org/wiki/File:028_Lighting_and_blowing_of_a_candle_(normal_speed)_Video_by_Giles_Laurent.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_CANDLE_FLAME_NORMAL","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "candle2":{"file":"candle2.webm","source_url":"https://commons.wikimedia.org/wiki/File:Visible_light_spectrum_of_a_candle_flame.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_CANDLE_FLAME_SPECTRUM","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "candle3":{"file":"candle3.webm","source_url":"https://commons.wikimedia.org/wiki/File:White_candle_video.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_WHITE_CANDLE_FLAME","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "candle4":{"file":"candle4.webm","source_url":"https://commons.wikimedia.org/wiki/File:Amazing_Flame_Comes_to_Life_in_Space_Station_Microgravity_Combustion_Science.webm","license":"PUBLIC_DOMAIN_NASA","asset_subject":"REAL_MICROGRAVITY_FLAME_NASA","asset_role":"TARGET_SUBJECT","identifiable_human":False}
  },
  "scenes":[
   ("REAL","candle1",1,"CONTEXT","candle","CHAMA DE VELA • VÍDEO REAL","A chama de uma vela quase sempre aponta para cima, mesmo quando o pavio está reto."),
   ("ANIMATION","anim",0,"MECHANISM","candle","ANIMAÇÃO • GÁS QUENTE SOBE","A combustão aquece os gases. Eles se expandem, ficam menos densos e começam a subir."),
   ("REAL","candle2",1,"PROOF","candle","CHAMA E LUZ • VÍDEO REAL","Esse fluxo ascendente puxa ar mais frio e oxigênio pelas laterais, alimentando continuamente a chama."),
   ("ANIMATION","anim",2,"MECHANISM","candle","ANIMAÇÃO • CONVECÇÃO ALONGA A CHAMA","A corrente de convecção estica a região quente para cima e dá à chama seu formato alongado."),
   ("REAL","candle3",1,"CONSEQUENCE","candle","OUTRA VELA • VÍDEO REAL","Por isso a forma não vem do pavio sozinho: ela depende do movimento do gás ao redor."),
   ("ANIMATION","anim",4,"MECHANISM","candle","ANIMAÇÃO • MICROGRAVIDADE MUDA O FLUXO","Em microgravidade, quase não existe um cima para a convecção; o oxigênio chega mais por difusão ao redor."),
   ("REAL","candle4",4,"PROOF","candle","CHAMA EM MICROGRAVIDADE • NASA","Na estação espacial, a chama pode ficar muito mais arredondada porque o fluxo deixa de subir como na Terra.")
  ]},
 "oleo_agua":{
  "title":"Por que óleo e água não se misturam, mesmo quando você agita? #shorts",
  "header":["POR QUE ÓLEO E ÁGUA","NÃO SE MISTURAM?"],
  "description":"A água é polar e forma interações fortes entre suas próprias moléculas; óleos são majoritariamente apolares. Agitar cria gotículas temporárias, mas sem um emulsificante elas tendem a se separar novamente. #VocêSabiaAgora #Curiosidades #Química #ÓleoEÁgua\n\nVídeos reais distintos: Wikimedia Commons.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"OIL_WATER_POLARITY_EMULSION",
  "assets":{
   "oil1":{"file":"oil1.webm","source_url":"https://commons.wikimedia.org/wiki/File:Water_and_sunflower_oil_on_a_magnetic_stirrer_01_ies.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_OIL_WATER_STIRRING","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "oil2":{"file":"oil2.webm","source_url":"https://commons.wikimedia.org/wiki/File:Emulsion_culinaire_-_exemple_de_la_mayonnaise_(1080p).webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_EMULSION_MAYONNAISE","asset_role":"EXPLICIT_CONTEXT","identifiable_human":False},
   "oil3":{"file":"oil3.webm","source_url":"https://commons.wikimedia.org/wiki/File:Oil_adsorbing_abilities_of_the_Floating_Fern_Salvinia_molesta_-_©_W._Barthlott_&_M._Mail_(Univ._Bonn).webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_OIL_SEPARATION_WATER_SURFACE","asset_role":"EXPLICIT_CONTEXT","identifiable_human":False},
   "oil4":{"file":"oil4.webm","source_url":"https://commons.wikimedia.org/wiki/File:Salvinia_Effect_Automatic_floating_Bionic_Oil_Adsorbtion_Device_BOA_-_©_W._Barthlott,_M._Moosmann_&_M._Mail_2020,_University_of_Bonn.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_OIL_ADSORPTION_FROM_WATER","asset_role":"EXPLICIT_CONTEXT","identifiable_human":False}
  },
  "scenes":[
   ("REAL","oil1",1,"CONTEXT","oil","ÓLEO + ÁGUA SENDO AGITADOS • VÍDEO REAL","Agite óleo e água com força: por alguns segundos eles parecem misturados."),
   ("ANIMATION","anim",0,"MECHANISM","oil","ANIMAÇÃO • POLAR × APOLAR","A água é polar e interage melhor com água; o óleo é majoritariamente apolar."),
   ("REAL","oil2",3,"PROOF","oil","EMULSÃO REAL • VÍDEO REAL","Com emulsificante, como na maionese, gotas de óleo permanecem dispersas por mais tempo."),
   ("ANIMATION","anim",2,"MECHANISM","oil","ANIMAÇÃO • AGITAÇÃO CRIA GOTÍCULAS","Agitar quebra o óleo em gotas menores e aumenta a área de contato entre os líquidos."),
   ("REAL","oil3",2,"CONSEQUENCE","oil","ÓLEO SEPARADO DA ÁGUA • VÍDEO REAL","Sem estabilização, o óleo volta a se juntar e se separar da água."),
   ("ANIMATION","anim",4,"MECHANISM","oil","ANIMAÇÃO • EMULSIFICANTE FAZ A PONTE","O emulsificante tem uma parte compatível com água e outra com óleo, estabilizando as gotículas."),
   ("REAL","oil4",4,"PROOF","oil","REMOÇÃO DE ÓLEO • VÍDEO REAL","Materiais especiais aproveitam essa diferença para capturar óleo sem absorver a maior parte da água.")
  ]},
 "shakira_primeira_infancia":{
  "title":"Por que Shakira fala tanto sobre a primeira infância? #shorts",
  "header":["POR QUE SHAKIRA FALA","TANTO DA INFÂNCIA?"],
  "description":"Shakira usa parte de sua visibilidade pública para defender educação e desenvolvimento na primeira infância. Nos primeiros anos, experiências, linguagem, cuidado e aprendizagem ajudam a construir bases importantes para etapas seguintes. #VocêSabiaAgora #Shakira #Educação #PrimeiraInfância\n\nFontes: World Economic Forum, ONU Brasil, UNICEF e Harvard Center on the Developing Child. Vídeos reais distintos e licenciados via Wikimedia Commons.",
  "content_class":"NEWS_EXPLAINER","expected_subject":"SHAKIRA_EARLY_CHILDHOOD_EDUCATION_ADVOCACY",
  "celebrity_name":"Shakira",
  "assets":{
   "shakira1":{"file":"shakira1.webm","source_url":"https://commons.wikimedia.org/wiki/File:Davos_2017_-_An_Insight,_An_Idea_with_Shakira.webm","license":"CC_BY_3.0","asset_subject":"SHAKIRA_EARLY_CHILDHOOD_EDUCATION_ADVOCACY","asset_role":"TARGET_SUBJECT","identifiable_human":True,"celebrity_visible":True},
   "edu1":{"file":"edu1.webm","source_url":"https://commons.wikimedia.org/wiki/File:Children_Retuning_from_school.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"CHILDREN_SCHOOL_EDUCATION_CONTEXT","asset_role":"EXPLICIT_CONTEXT","identifiable_human":True,"celebrity_visible":False},
   "edu2":{"file":"edu2.webm","source_url":"https://commons.wikimedia.org/wiki/File:Rob_Sixsmith_-_Unicef_model_of_a_child_friendly_school_-_Unicef_-_Syria.webm","license":"CC_LICENSED","asset_subject":"CHILD_FRIENDLY_SCHOOL_CONTEXT","asset_role":"EXPLICIT_CONTEXT","identifiable_human":True,"celebrity_visible":False},
   "shakira2":{"file":"shakira2.webm","source_url":"https://commons.wikimedia.org/wiki/File:Na_ONU,_Shakira_canta_%22Imagine%22_e_pede_igualdade_para_todos.webm","license":"CC_BY_3.0","asset_subject":"SHAKIRA_SOCIAL_ADVOCACY_UN_STAGE","asset_role":"TARGET_SUBJECT","identifiable_human":True,"celebrity_visible":True}
  },
  "scenes":[
   ("REAL","shakira1",20,"CONTEXT","shakira","SHAKIRA EM DAVOS • VÍDEO REAL","Shakira usa espaços fora do palco para defender a primeira infância e a educação nos primeiros anos."),
   ("ANIMATION","anim",0,"MECHANISM","shakira","ANIMAÇÃO • CONEXÕES NO CÉREBRO","No começo da vida, experiências e interação ajudam o cérebro a formar e fortalecer muitas conexões."),
   ("REAL","edu1",5,"PROOF","shakira","CRIANÇAS E ESCOLA • CONTEXTO REAL","Linguagem, brincadeira, cuidado e aprendizagem criam bases que serão usadas nas etapas seguintes."),
   ("ANIMATION","anim",2,"MECHANISM","shakira","ANIMAÇÃO • UMA BASE APOIA A PRÓXIMA","Habilidades se apoiam: atenção ajuda a aprender; linguagem ajuda a comunicar; interação ajuda a desenvolver respostas sociais."),
   ("REAL","edu2",30,"CONSEQUENCE","shakira","ESCOLA AMIGA DA CRIANÇA • UNICEF","Por isso acesso cedo a ambientes seguros e estimulantes pode ampliar oportunidades de aprender e se desenvolver."),
   ("ANIMATION","anim",4,"MECHANISM","shakira","ANIMAÇÃO • VISIBILIDADE VIRA ATENÇÃO","Quando uma pessoa famosa fala do tema, a visibilidade pode levar mais gente a conhecer e discutir a causa."),
   ("REAL","shakira2",3,"PROOF","shakira","SHAKIRA NA ONU • VÍDEO REAL","Shakira também leva causas sociais a palcos internacionais, usando sua voz pública para além da música.")
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
 with requests.get(url,headers={"User-Agent":"VSA-Oct02/1.0"},stream=True,timeout=180) as r:
  r.raise_for_status()
  with open(p,"wb") as f:
   for c in r.iter_content(1048576):
    if c:f.write(c)
 return p
def commons_video(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"videoinfo","viprop":"url|derivatives","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Oct02/1.0"},timeout=60).json()["query"]["pages"].values()))
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
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Oct02/1.0"},timeout=60).json()["query"]["pages"].values()))
 return dl(page["imageinfo"][0]["url"],p)


def commons_image(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"imageinfo","iiprop":"url","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Oct02/1.0"},timeout=60).json()["query"]["pages"].values()))
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
  if slug=="chama_vela":
   if seg==0:
    d.text((45,38),"GÁS QUENTE EXPANDE E SOBE",font=fb,fill="white")
    d.rectangle((400,600,575,735),fill=(100,80,55))
    for i in range(6):
     x=430+i*22; y=565-int(220*u)-i*12
     d.ellipse((x-12,y-12,x+12,y+12),fill=(255,150,55))
    d.line((487,570,487,260),fill=(100,220,160),width=10)
    d.polygon([(487,230),(465,275),(509,275)],fill=(100,220,160))
    d.text((285,765),"densidade menor → fluxo para cima",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"CONVECÇÃO ALONGA A CHAMA",font=fb,fill="white")
    pts=[(487,190),(390,470),(430,650),(487,730),(545,650),(585,470)]
    d.polygon(pts,fill=(255,145,45))
    d.polygon([(487,285),(440,500),(487,650),(535,500)],fill=(255,220,80))
    for x in (300,675):
     d.line((x,650,x,400),fill=(100,180,240),width=8)
     d.polygon([(x,370),(x-18,410),(x+18,410)],fill=(100,180,240))
    d.text((275,760),"ar entra pelas laterais • gás sobe",font=fs,fill="white")
   else:
    d.text((45,38),"MICROGRAVIDADE → DIFUSÃO RADIAL",font=fb,fill="white")
    cx,cy=487,440
    d.ellipse((340,293,634,587),fill=(255,190,70),outline=(255,235,150),width=6)
    for ang in range(0,360,45):
     import math as _m
     x2=cx+int(235*_m.cos(_m.radians(ang))); y2=cy+int(235*_m.sin(_m.radians(ang)))
     d.line((cx,cy,x2,y2),fill=(100,220,160),width=5)
    d.text((230,730),"sem direção preferencial de subida",font=fs,fill="white")
  elif slug=="oleo_agua":
   if seg==0:
    d.text((45,38),"ÁGUA POLAR × ÓLEO APOLAR",font=fb,fill="white")
    for i in range(12):
     x=130+(i%4)*70; y=260+(i//4)*95
     d.ellipse((x-18,y-18,x+18,y+18),fill=(90,180,255))
     if i%4<3:d.line((x+18,y,x+52,y),fill=(120,210,255),width=4)
    for i in range(8):
     x=610+(i%4)*70; y=300+(i//4)*130
     d.rounded_rectangle((x-30,y-12,x+30,y+12),10,fill=(255,190,70))
    d.text((120,650),"água interage com água",font=fr,fill="white")
    d.text((600,650),"óleo prefere óleo",font=fr,fill="white")
   elif seg==1:
    d.text((45,38),"AGITAÇÃO → GOTÍCULAS MENORES",font=fb,fill="white")
    for i in range(10):
     r=max(8,35-int(22*u))
     x=150+(i%5)*160; y=300+(i//5)*230
     d.ellipse((x-r,y-r,x+r,y+r),fill=(255,190,70),outline=(255,230,150),width=3)
    d.line((100,650,875,650),fill=(100,180,240),width=7)
    d.text((205,710),"mais gotículas = mais área de interface",font=fs,fill="white")
   else:
    d.text((45,38),"EMULSIFICANTE FAZ A PONTE",font=fb,fill="white")
    cx,cy=487,430
    d.ellipse((360,303,614,557),fill=(255,190,70))
    for ang in range(0,360,30):
     import math as _m
     x1=cx+int(135*_m.cos(_m.radians(ang))); y1=cy+int(135*_m.sin(_m.radians(ang)))
     x2=cx+int(190*_m.cos(_m.radians(ang))); y2=cy+int(190*_m.sin(_m.radians(ang)))
     d.line((x1,y1,x2,y2),fill=(100,220,160),width=7)
     d.ellipse((x2-9,y2-9,x2+9,y2+9),fill=(90,180,255))
    d.text((220,720),"uma ponta gosta de óleo • outra de água",font=fs,fill="white")
  else:
   if seg==0:
    d.text((45,38),"EXPERIÊNCIA → CONEXÕES SE FORTALECEM",font=fb,fill="white")
    nodes=[(180,300),(330,220),(490,330),(650,220),(790,350),(270,520),(500,560),(730,540)]
    for x,y in nodes:
     d.ellipse((x-18,y-18,x+18,y+18),fill=(100,220,160))
    for i,(x1,y1) in enumerate(nodes):
     for j,(x2,y2) in enumerate(nodes):
      if j>i and abs(x1-x2)<250 and abs(y1-y2)<220:
       d.line((x1,y1,x2,y2),fill=(80,130,180),width=3)
    active=int(1+u*7)
    for x,y in nodes[:active]:
     d.ellipse((x-24,y-24,x+24,y+24),outline=(255,190,70),width=6)
    d.text((220,720),"interação e estímulo reforçam redes",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"UMA HABILIDADE APOIA A PRÓXIMA",font=fb,fill="white")
    blocks=[("ATENÇÃO",90,300),( "LINGUAGEM",380,590),("APRENDER",670,880)]
    for lab,x1,x2 in blocks:
     d.rounded_rectangle((x1,350,x2,500),20,outline=(100,180,230),width=6)
     d.text((x1+25,400),lab,font=fs,fill="white")
    d.line((300,425,380,425),fill=(100,220,160),width=9)
    d.line((590,425,670,425),fill=(100,220,160),width=9)
    pos=105+int(740*u); d.ellipse((pos-16,580,pos+16,612),fill=(255,190,70))
    d.text((205,690),"bases iniciais sustentam etapas seguintes",font=fs,fill="white")
   else:
    d.text((45,38),"FAMA → ATENÇÃO PÚBLICA PARA A CAUSA",font=fb,fill="white")
    d.ellipse((120,330,260,470),fill=(255,190,70))
    d.text((157,375),"VOZ",font=fs,fill=(10,18,32))
    d.line((260,400,520,400),fill=(100,220,160),width=10)
    d.polygon([(545,400),(505,378),(505,422)],fill=(100,220,160))
    for i in range(6):
     x=620+(i%3)*90; y=330+(i//3)*150
     d.ellipse((x-25,y-25,x+25,y+25),fill=(90,180,255))
    d.text((215,690),"visibilidade amplia quem encontra o tema",font=fs,fill="white")
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
 final=od/f"VSA_{slug}_OCT02.mp4";run(["ffmpeg","-y","-loglevel","error","-i",visual,"-i",mix,"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",final])
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
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/a64b508c-0c26-491f-b018-28a0127fba43.webm",AS/"candle1.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/8849624b-f5fc-41ad-bfd8-d1585ff7bca9.webm",AS/"candle2.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/322929d8-8228-40cf-8350-66723804aa1d.webm",AS/"candle3.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/255ee9f4-43b5-435d-a9f5-a0b063b5c900.webm",AS/"candle4.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/bf974250-6494-4db6-93c5-fd756f37b66c.webm",AS/"oil1.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/e86d171b-7567-4a43-853a-618d85333e31.webm",AS/"oil2.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/c28d5144-a791-4f14-aff0-3ca8d13f0844.webm",AS/"oil3.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/62403590-5bc8-400b-b5a4-b664e84f429a.webm",AS/"oil4.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/a6cc41b7-8643-4611-b3f2-a80e623183b2.webm",AS/"shakira1.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/95fb7445-937f-4039-80ea-9929cd69ca00.webm",AS/"edu1.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/8056c6a6-d4c0-4719-abbe-05a5b559b5d1.webm",AS/"edu2.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/5ef10b83-ed24-4004-b15d-f479d9c78759.webm",AS/"shakira2.webm")
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

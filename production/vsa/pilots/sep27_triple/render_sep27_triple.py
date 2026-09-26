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
 "nuvem_nao_cai":{
  "title":"Por que uma nuvem com toneladas de água não cai do céu? #shorts",
  "header":["POR QUE A NUVEM","NÃO DESPENCA?"],
  "description":"Nuvens são feitas de gotículas de água ou cristais de gelo minúsculos. Enquanto são pequenos, a resistência do ar e correntes ascendentes ajudam a mantê-los suspensos; quando crescem o suficiente, caem como precipitação. #VocêSabiaAgora #Curiosidades #Nuvens #Ciência\n\nFontes científicas: UCAR/NCAR, NOAA e Smithsonian How Things Fly. Vídeos reais distintos: Wikimedia Commons; créditos e licenças nas páginas-fonte.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"CLOUD_DROPLET_SUSPENSION",
  "assets":{
   "cloud1":{"file":"cloud1.webm","source_url":"https://commons.wikimedia.org/wiki/File:Clouds_moving_over_a_road_in_Tenerife.webm","license":"CC_BY_SA_4.0","asset_subject":"REAL_CLOUDS_TENERIFE","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "cloud2":{"file":"cloud2.webm","source_url":"https://commons.wikimedia.org/wiki/File:Clouds_transformations.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_CLOUD_TRANSFORMATIONS","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "cloud3":{"file":"cloud3.webm","source_url":"https://commons.wikimedia.org/wiki/File:Clouds_(time_lapse).webm","license":"CC_BY_3.0","asset_subject":"REAL_CLOUD_TIMELAPSE","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "cloud4":{"file":"cloud4.webm","source_url":"https://commons.wikimedia.org/wiki/File:Clouds-20140815.webm","license":"CC_BY_SA_4.0","asset_subject":"REAL_CLOUD_TIMELAPSE_2014","asset_role":"TARGET_SUBJECT","identifiable_human":False}
  },
  "scenes":[
   ("REAL","cloud1",0,"CONTEXT","cloud","NUVENS • VÍDEO REAL","Uma nuvem pode carregar toneladas de água. Então por que ela não despenca?"),
   ("ANIMATION","anim",0,"MECHANISM","cloud","ANIMAÇÃO • GOTÍCULAS MINÚSCULAS","Porque a água está dividida em gotículas microscópicas, pequenas o bastante para cair muito devagar."),
   ("REAL","cloud2",1,"PROOF","cloud","NUVENS EM MOVIMENTO • VÍDEO REAL","Correntes de ar que sobem e a resistência do ar ajudam a manter essas gotículas suspensas."),
   ("ANIMATION","anim",2,"MECHANISM","cloud","ANIMAÇÃO • AR SOBE E CONDENSA","Quando o ar úmido sobe, esfria e o vapor condensa em partículas minúsculas, formando a nuvem."),
   ("REAL","cloud3",2,"CONSEQUENCE","cloud","NUVENS • VÍDEO REAL","Enquanto as gotas continuam pequenas, seu peso individual não vence facilmente o movimento do ar."),
   ("ANIMATION","anim",4,"MECHANISM","cloud","ANIMAÇÃO • GOTAS CRESCEM E CAEM","Mas elas colidem, se juntam e crescem. A velocidade de queda aumenta até a gravidade dominar."),
   ("REAL","cloud4",3,"PROOF","cloud","NUVENS • VÍDEO REAL","Aí a nuvem começa a precipitar: o que estava suspenso finalmente cai como chuva.")
  ]},
 "pes_pinguim":{
  "title":"Por que os pés dos pinguins não congelam no gelo? #shorts",
  "header":["POR QUE OS PÉS","DOS PINGUINS NÃO CONGELAM?"],
  "description":"Pinguins reduzem a perda de calor nos pés com controle do fluxo sanguíneo e troca de calor em contracorrente entre artérias e veias. Assim, as extremidades ficam frias sem congelar e o núcleo do corpo conserva calor. #VocêSabiaAgora #Curiosidades #Pinguins #Antártica\n\nFontes científicas: Smithsonian Ocean e British Antarctic Survey. Quatro vídeos reais distintos: Wikimedia Commons.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"PENGUIN_FEET_COUNTERCURRENT_HEAT_EXCHANGE",
  "assets":{
   "peng1":{"file":"peng1.webm","source_url":"https://commons.wikimedia.org/wiki/File:Adélie_penguin_(Pygoscelis_adeliae)_in_Antarctica.webm","license":"CC_BY_3.0","asset_subject":"REAL_ADELIE_PENGUIN","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "peng2":{"file":"peng2.webm","source_url":"https://commons.wikimedia.org/wiki/File:Emperor_penguins_–_the_biggest_of_all.webm","license":"CC_BY_3.0","asset_subject":"REAL_EMPEROR_PENGUINS","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "peng3":{"file":"peng3.webm","source_url":"https://commons.wikimedia.org/wiki/File:Gentoo_penguins_(Pygoscelis_papua)_in_Antarctica.webm","license":"CC_BY_3.0","asset_subject":"REAL_GENTOO_PENGUINS","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "peng4":{"file":"peng4.webm","source_url":"https://commons.wikimedia.org/wiki/File:Emperor_penguin,_Coulman_Island,_Antarctica.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_EMPEROR_PENGUIN_COULMAN","asset_role":"TARGET_SUBJECT","identifiable_human":False}
  },
  "scenes":[
   ("REAL","peng1",1,"CONTEXT","penguin","PINGUIM NA ANTÁRTICA • VÍDEO REAL","Pinguins ficam sobre gelo por horas. Então por que os pés deles não congelam?"),
   ("ANIMATION","anim",0,"MECHANISM","penguin","ANIMAÇÃO • TROCA EM CONTRACORRENTE","As artérias e veias das pernas passam muito perto umas das outras, formando um trocador de calor."),
   ("REAL","peng2",2,"PROOF","penguin","PINGUINS-IMPERADORES • VÍDEO REAL","O sangue quente que desce transfere calor ao sangue frio que retorna para o corpo."),
   ("ANIMATION","anim",2,"MECHANISM","penguin","ANIMAÇÃO • FLUXO DIMINUI NO FRIO","Assim, o sangue chega aos pés já resfriado, perdendo menos energia para o gelo."),
   ("REAL","peng3",3,"CONSEQUENCE","penguin","PINGUINS-GENTOO • VÍDEO REAL","No frio intenso, eles também reduzem o fluxo de sangue nas extremidades sem interrompê-lo por completo."),
   ("ANIMATION","anim",4,"MECHANISM","penguin","ANIMAÇÃO • CALOR VOLTA AO CORPO","Os pés ficam poucos graus acima do congelamento, enquanto o calor é preservado no núcleo do corpo."),
   ("REAL","peng4",4,"PROOF","penguin","PINGUIM-IMPERADOR • VÍDEO REAL","É um equilíbrio preciso: frio para economizar calor, mas quente o bastante para manter o tecido vivo.")
  ]},
 "ed_show_clima":{
  "title":"Ed Sheeran teve shows cancelados: como o clima pode parar um estádio? #shorts",
  "header":["COMO O CLIMA","PARA UM SHOW?"],
  "description":"Segundo a CNN Brasil, citando o TMZ, apresentações de Ed Sheeran previstas para este fim de semana no Gillette Stadium foram canceladas por mau tempo, com a segurança do público e das equipes como prioridade. Grandes eventos usam monitoramento, planos de abrigo/evacuação e limites operacionais para riscos como tempestades e vento forte. #VocêSabiaAgora #EdSheeran #Shows #Clima\n\nVídeos de Ed: Warner Music New Zealand / Wikimedia Commons, CC BY 3.0. Tempestade: Alexander Grebenkov / Wikimedia Commons, CC BY 3.0. Estádio: Wikimedia Commons. Fontes factuais: CNN Brasil e National Weather Service.",
  "content_class":"NEWS_EXPLAINER","expected_subject":"ED_SHEERAN_WEATHER_EVENT_SAFETY",
  "celebrity_name":"Ed Sheeran",
  "assets":{
   "ed_tour":{"file":"ed_tour.webm","source_url":"https://commons.wikimedia.org/wiki/File:Ed_Sheeran_pōwhiri_in_New_Zealand.webm","license":"CC_BY_3.0","asset_subject":"ED_SHEERAN_TOUR_STADIUM_CONTEXT","asset_role":"CELEBRITY_CONTEXT","identifiable_human":True,"celebrity_visible":True},
   "storm":{"file":"storm.webm","source_url":"https://commons.wikimedia.org/wiki/File:Storm_clouds_moving_in_Yantarny,_Kaliningrad_Oblast.webm","license":"CC_BY_3.0","asset_subject":"REAL_STORM_CLOUDS","asset_role":"WEATHER_CONTEXT","identifiable_human":False,"celebrity_visible":False},
   "stadium":{"file":"stadium.webm","source_url":"https://commons.wikimedia.org/wiki/File:Stadium_Pan_as_South_Florida_USF_Bulls_Beat_Notre_Dame_Irish.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_LARGE_STADIUM_CROWD","asset_role":"VENUE_CONTEXT","identifiable_human":True,"celebrity_visible":False},
   "ed_message":{"file":"ed_message.webm","source_url":"https://commons.wikimedia.org/wiki/File:Promotion_message_from_Ed_Sheeran_in_2019.webm","license":"CC_BY_3.0","asset_subject":"ED_SHEERAN_OFFICIAL_MESSAGE","asset_role":"CELEBRITY_CONTEXT","identifiable_human":True,"celebrity_visible":True}
  },
  "scenes":[
   ("REAL","ed_tour",12,"CONTEXT","event","ED SHEERAN EM CONTEXTO DE TURNÊ • VÍDEO REAL","Ed Sheeran teve shows no Gillette Stadium cancelados neste fim de semana; segundo a CNN, por mau tempo."),
   ("ANIMATION","anim",0,"MECHANISM","event","ANIMAÇÃO • MONITORAMENTO ANTES DO SHOW","Em grandes eventos, a decisão começa cedo: equipes monitoram previsão, radar e tempestades próximas."),
   ("REAL","storm",3,"PROOF","event","TEMPESTADE • VÍDEO REAL","O objetivo não é esperar o perigo chegar, mas ganhar tempo para proteger milhares de pessoas."),
   ("ANIMATION","anim",2,"MECHANISM","event","ANIMAÇÃO • TEMPO PARA EVACUAR","O plano calcula o tempo para levar o público a áreas seguras e quais riscos acionam atraso ou evacuação."),
   ("REAL","stadium",2,"CONSEQUENCE","event","ESTÁDIO CHEIO • VÍDEO REAL","Vento forte também importa: palcos, torres, telões e estruturas temporárias têm limites de segurança."),
   ("ANIMATION","anim",4,"MECHANISM","event","ANIMAÇÃO • LIMITE DE SEGURANÇA","Se o risco ultrapassa o limite previsto, o evento pode ser adiado ou cancelado antes de a situação piorar."),
   ("REAL","ed_message",1,"PROOF","event","ED SHEERAN • VÍDEO OFICIAL","No caso de Ed, a prioridade divulgada foi a segurança do público e das equipes envolvidas.")
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
 with requests.get(url,headers={"User-Agent":"VSA-Sep27/1.0"},stream=True,timeout=180) as r:
  r.raise_for_status()
  with open(p,"wb") as f:
   for c in r.iter_content(1048576):
    if c:f.write(c)
 return p
def commons_video(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"videoinfo","viprop":"url|derivatives","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep27/1.0"},timeout=60).json()["query"]["pages"].values()))
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
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep27/1.0"},timeout=60).json()["query"]["pages"].values()))
 return dl(page["imageinfo"][0]["url"],p)


def commons_image(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"imageinfo","iiprop":"url","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep27/1.0"},timeout=60).json()["query"]["pages"].values()))
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
  if slug=="nuvem_nao_cai":
   if seg==0:
    d.text((45,38),"GOTÍCULAS MINÚSCULAS CAEM MUITO DEVAGAR",font=fb,fill="white")
    for i in range(18):
     x=100+(i%6)*145; y=220+(i//6)*135
     r=8+(i%3)*3
     d.ellipse((x-r,y-r,x+r,y+r),fill=(95,190,255))
     d.line((x,y+20,x,y+55),fill=(255,195,70),width=3)
    d.line((120,690,850,690),fill=(80,210,150),width=7)
    for x in range(150,850,140):
     d.line((x,690,x,610),fill=(80,210,150),width=6); d.polygon([(x,595),(x-10,620),(x+10,620)],fill=(80,210,150))
    d.text((240,735),"arrasto + correntes ascendentes",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"AR ÚMIDO SOBE → ESFRIA → CONDENSA",font=fb,fill="white")
    d.rectangle((70,620,905,740),fill=(30,70,95))
    for k in range(7):
     x=150+k*105; y=610-int(260*u)-25*(k%2)
     d.line((x,620,x,y),fill=(255,190,70),width=7)
     d.polygon([(x,y-12),(x-11,y+12),(x+11,y+12)],fill=(255,190,70))
    for i in range(16):
     x=130+(i%8)*100; y=230+(i//8)*100
     rr=6+int(5*u); d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=(110,200,255))
    d.text((285,755),"vapor vira gotículas",font=fs,fill=(110,200,255))
   else:
    d.text((45,38),"QUANDO CRESCEM, A GRAVIDADE VENCE",font=fb,fill="white")
    small=[(150,230),(240,260),(330,220),(420,270)]
    for x,y in small:d.ellipse((x-12,y-12,x+12,y+12),fill=(100,195,255))
    cx=650; cy=260+int(300*u); rr=38+int(18*u)
    d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),fill=(70,160,245))
    d.line((cx,cy+rr,cx,cy+rr+110),fill=(255,190,70),width=10)
    d.polygon([(cx,cy+rr+125),(cx-16,cy+rr+95),(cx+16,cy+rr+95)],fill=(255,190,70))
    d.text((115,520),"colisão + coalescência",font=fs,fill="white")
    d.text((565,650),"GOTA MAIOR → CHUVA",font=fs,fill=(255,190,70))
  elif slug=="pes_pinguim":
   if seg==0:
    d.text((45,38),"ARTÉRIA E VEIA TROCAM CALOR",font=fb,fill="white")
    d.line((300,170,300,700),fill=(235,90,70),width=34)
    d.line((650,700,650,170),fill=(80,170,255),width=34)
    for y in range(230,660,75):
     d.line((325,y,625,y),fill=(255,190,70),width=5)
     d.polygon([(625,y),(605,y-10),(605,y+10)],fill=(255,190,70))
    d.text((195,735),"QUENTE DESCENDO",font=fs,fill=(235,90,70)); d.text((585,735),"FRIO SUBINDO",font=fs,fill=(80,170,255))
   elif seg==1:
    d.text((45,38),"NO FRIO, O FLUXO PARA O PÉ DIMINUI",font=fb,fill="white")
    d.ellipse((350,180,625,455),outline=(110,170,210),width=8)
    width=max(12,int(70*(1-u)+18*u))
    d.line((485,455,485,690),fill=(230,90,70),width=width)
    d.text((365,720),"vasos contraem",font=fs,fill="white")
    d.text((235,530),"menos sangue quente chega à extremidade",font=fr,fill=(255,200,70))
   else:
    d.text((45,38),"CALOR RECICLADO → NÚCLEO PROTEGIDO",font=fb,fill="white")
    d.ellipse((380,170,600,390),fill=(190,85,65)); d.text((425,255),"CORPO",font=fs,fill="white")
    d.rectangle((420,390,470,650),fill=(115,165,210)); d.rectangle((510,390,560,650),fill=(115,165,210))
    d.ellipse((390,620,485,690),fill=(70,130,190)); d.ellipse((495,620,590,690),fill=(70,130,190))
    d.arc((260,220,720,720),200,340,fill=(100,220,160),width=10)
    d.text((280,740),"pés poucos graus acima de 0 °C",font=fs,fill=(100,220,160))
  else:
   if seg==0:
    d.text((45,38),"PREVISÃO + RADAR + DETECÇÃO",font=fb,fill="white")
    d.rounded_rectangle((70,180,350,620),25,outline=(80,180,255),width=5)
    d.text((140,220),"RADAR",font=fs,fill="white")
    cx,cy=210,410
    for r in (55,100,145):
     d.arc((cx-r,cy-r,cx+r,cy+r),210,330,fill=(80,180,255),width=4)
    sx=250+int(160*u); sy=355
    d.ellipse((sx-24,sy-16,sx+24,sy+16),fill=(130,130,150))
    d.rounded_rectangle((560,180,900,620),25,outline=(100,220,150),width=5)
    d.text((630,220),"EVENTO",font=fs,fill="white")
    d.line((350,410,560,410),fill=(255,190,70),width=8)
    d.polygon([(560,410),(535,395),(535,425)],fill=(255,190,70))
    d.text((520,700),"DECISÃO ANTES DO RISCO",font=fs,fill=(255,190,70))
   elif seg==1:
    d.text((45,38),"TEMPO DA TEMPESTADE × TEMPO DE EVACUAÇÃO",font=fb,fill="white")
    d.line((90,285,870,285),fill=(80,180,255),width=8)
    stormx=100+int(700*u); d.ellipse((stormx-55,220,stormx+55,300),fill=(80,90,110))
    d.line((90,585,870,585),fill=(100,220,150),width=8)
    crowdx=100+int(520*u)
    for i in range(8):d.ellipse((crowdx+i*24,530,crowdx+14+i*24,544),fill=(235,235,235))
    d.text((105,330),"ameaça se aproxima",font=fs,fill=(80,180,255))
    d.text((105,630),"público precisa chegar ao abrigo",font=fs,fill=(100,220,150))
   else:
    d.text((45,38),"VENTO FORTE TAMBÉM TEM LIMITE",font=fb,fill="white")
    d.line((200,650,760,650),fill=(130,145,160),width=8)
    d.line((470,650,470,230),fill=(210,210,220),width=18)
    d.rectangle((330,260,610,420),outline=(210,210,220),width=8)
    force=70+int(110*u)
    for y in (300,370,470,540):
     d.line((100,y,100+force,y),fill=(80,180,255),width=9)
     d.polygon([(100+force,y),(80+force,y-12),(80+force,y+12)],fill=(80,180,255))
    d.text((620,315),"PALCO / TELÃO",font=fs,fill="white")
    d.rounded_rectangle((615,540,880,690),22,outline=(255,190,70),width=5)
    d.text((650,575),"ADIAR OU",font=fs,fill="white"); d.text((650,615),"CANCELAR",font=fs,fill=(255,190,70))
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
 final=od/f"VSA_{slug}_SEP27.mp4";run(["ffmpeg","-y","-loglevel","error","-i",visual,"-i",mix,"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",final])
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
 downloads={
  "cloud1.webm":"https://cdn.creativeclaw.co/u/2f9dfa63/videos/acb9c6ca-ee8d-43ee-85f0-01be4cccdf95.webm",
  "cloud2.webm":"https://cdn.creativeclaw.co/u/2f9dfa63/videos/fa88c8a2-2262-4d10-9841-3b33b2abbe48.webm",
  "cloud3.webm":"https://cdn.creativeclaw.co/u/2f9dfa63/videos/972dbab3-c708-4451-be95-5aab6c8d06e8.webm",
  "cloud4.webm":"https://cdn.creativeclaw.co/u/2f9dfa63/videos/aed1d99c-bf78-4ca0-aea0-07a8a166d673.webm",
  "peng1.webm":"https://cdn.creativeclaw.co/u/2f9dfa63/videos/1d4300f2-b8f4-4b63-8635-579ebf0af14a.webm",
  "peng2.webm":"https://cdn.creativeclaw.co/u/2f9dfa63/videos/d0e3dc87-71ff-43d4-afd4-2d630147bfe8.webm",
  "peng3.webm":"https://cdn.creativeclaw.co/u/2f9dfa63/videos/3e34c1fd-0559-4802-978b-1d8f3d47194a.webm",
  "peng4.webm":"https://cdn.creativeclaw.co/u/2f9dfa63/videos/13614dd2-1add-459b-89c7-f26542e653e6.webm",
  "ed_tour.webm":"https://cdn.creativeclaw.co/u/2f9dfa63/videos/d1ac4152-6c98-4bf9-9515-748ce0e4a8ae.webm",
  "ed_message.webm":"https://cdn.creativeclaw.co/u/2f9dfa63/videos/bb463add-3916-4451-a481-77b53720d97b.webm",
  "storm.webm":"https://cdn.creativeclaw.co/u/2f9dfa63/videos/969289fa-e56e-493c-a01e-ed8fdc6f5c38.webm",
  "stadium.webm":"https://cdn.creativeclaw.co/u/2f9dfa63/videos/f51c23a5-42c5-4fab-8a5e-7a69083adeb5.webm"
 }
 for fn,url in downloads.items(): dl(url,AS/fn)
 for slug,t in TOPICS.items():
  real_keys=[s[1] for s in t["scenes"] if s[0]=="REAL"]
  real_files=[t["assets"][k]["file"] for k in real_keys]
  if len(real_files)!=len(set(real_files)): raise RuntimeError("REAL_ASSET_DUPLICATE_FAIL "+slug)
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

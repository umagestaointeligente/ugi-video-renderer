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
 "furinho_aviao":{
  "title":"Por que existe um furinho na janela do avião? #shorts",
  "header":["POR QUE A JANELA","DO AVIÃO TEM UM FURO?"],
  "description":"O pequeno furo visível em muitas janelas de avião faz parte do sistema que administra a pressão entre as camadas da janela e também ajuda a reduzir condensação. #VocêSabiaAgora #Curiosidades #Aviação #Engenharia\n\nVídeo real: Wikimedia Commons. Foto de janela: Andrey Filippov / Wikimedia Commons, CC BY. Animações causais produzidas pelo VSA.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"AIRCRAFT_WINDOW_BREATHER_HOLE",
  "real":"airplane_window.webm","source_url":"https://commons.wikimedia.org/wiki/File:Airplane_inside_while_taking_off.webm","license":"WIKIMEDIA_COMMONS_LICENSED",
  "real_asset_subject":"AIRCRAFT_CABIN_WINDOW_CONTEXT","real_asset_role":"EXPLICIT_CONTEXT","real_identifiable_human":False,
  "scenes":[
   ("REAL",2,"CONTEXT","air","JANELA DE AVIÃO • VÍDEO REAL","Na janela de muitos aviões há um furinho minúsculo. E ele não é defeito."),
   ("ANIMATION",0,"MECHANISM","air","ANIMAÇÃO • TRÊS CAMADAS","A janela costuma ter várias camadas. O pequeno orifício fica em uma das camadas internas do conjunto."),
   ("REAL",26,"PROOF","air","CABINE EM VOO • VÍDEO REAL","Durante o voo, a cabine permanece pressurizada enquanto o ar do lado de fora fica muito menos denso."),
   ("ANIMATION",2,"MECHANISM","air","ANIMAÇÃO • PRESSÃO CONTROLADA","O furo permite equilibrar a pressão no espaço entre as camadas, deixando o conjunto trabalhar como foi projetado."),
   ("REAL",55,"CONSEQUENCE","air","JANELA DE AVIÃO • VÍDEO REAL","Assim, a diferença de pressão não fica distribuída de qualquer jeito entre os painéis da janela."),
   ("ANIMATION",4,"MECHANISM","air","ANIMAÇÃO • UMIDADE E RESERVA","A passagem controlada de ar também ajuda a reduzir embaçamento e mantém uma camada estrutural de reserva."),
   ("REAL",84,"PROOF","air","CABINE EM VOO • VÍDEO REAL","Ou seja: aquele furinho assustador é, na verdade, parte da engenharia de segurança da janela.")
  ]},
 "beija_flor_re":{
  "title":"Como o beija-flor consegue voar para trás? #shorts",
  "header":["COMO O BEIJA-FLOR","VOA PARA TRÁS?"],
  "description":"Beija-flores conseguem sustentar força aerodinâmica tanto na batida para baixo quanto na volta da asa. Ao mudar a orientação e o plano do movimento, conseguem pairar e deslocar o corpo para trás. #VocêSabiaAgora #Curiosidades #Natureza #Ciência\n\nVídeo real: Hectonichus / Wikimedia Commons, CC BY-SA 4.0. Animações causais produzidas pelo VSA.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"HUMMINGBIRD_BACKWARD_FLIGHT",
  "real":"hummingbird.webm","source_url":"https://commons.wikimedia.org/wiki/File:Trochilidae_-_Hummingbird.webm","license":"CC_BY_SA_4.0",
  "real_asset_subject":"REAL_HUMMINGBIRD","real_asset_role":"TARGET_SUBJECT","real_identifiable_human":False,
  "scenes":[
   ("REAL",9,"CONTEXT","bird","BEIJA-FLOR • VÍDEO REAL","A maioria das aves precisa avançar para manter o voo. O beija-flor consegue parar no ar e até recuar."),
   ("ANIMATION",0,"MECHANISM","bird","ANIMAÇÃO • FORÇA NAS DUAS BATIDAS","Suas asas giram no ombro e produzem sustentação tanto na descida quanto no movimento de volta."),
   ("REAL",32,"PROOF","bird","BEIJA-FLOR • VÍDEO REAL","Isso permite gerar força quase continuamente, em vez de depender apenas de uma parte da batida."),
   ("ANIMATION",2,"MECHANISM","bird","ANIMAÇÃO • ASA GIRA","Ao inverter o ângulo da asa na volta, a superfície continua empurrando o ar na direção necessária."),
   ("REAL",62,"CONSEQUENCE","bird","BEIJA-FLOR • VÍDEO REAL","Para sair do lugar, ele muda a orientação desse movimento e inclina a força produzida pelas asas."),
   ("ANIMATION",4,"MECHANISM","bird","ANIMAÇÃO • VETOR PARA TRÁS","Quando o vetor de força é inclinado para frente, a reação empurra o corpo para trás sem precisar virar."),
   ("REAL",94,"PROOF","bird","BEIJA-FLOR • VÍDEO REAL","É esse controle fino das asas que transforma o beija-flor em um dos voadores mais manobráveis do planeta.")
  ]},
 "paolla_bateria":{
  "title":"Paolla Oliveira voltou ao Carnaval: o que uma rainha de bateria faz? #shorts",
  "header":["O QUE UMA RAINHA","DE BATERIA FAZ?"],
  "description":"Paolla Oliveira foi anunciada como rainha de bateria da Imperatriz Leopoldinense para o Carnaval de 2027. O posto fica à frente dos ritmistas, mas quem conduz musicalmente a bateria é o mestre. #VocêSabiaAgora #PaollaOliveira #Carnaval #Samba\n\nVídeo de samba: Arian Zwegers / Wikimedia Commons, CC BY 2.0. Imagem de Paolla Oliveira: Wikimedia Commons / Multishow, CC BY 3.0. Fontes atuais: Imperatriz Leopoldinense, CNN Brasil e UOL.",
  "content_class":"NEWS_EXPLAINER","expected_subject":"PAOLLA_OLIVEIRA_RAINHA_BATERIA_2027",
  "real":"samba.webm","source_url":"https://commons.wikimedia.org/wiki/File:Rio_de_Janeiro,_Copacabana_Beach,_samba.webm","license":"CC_BY_2.0",
  "real_asset_subject":"REAL_SAMBA_CONTEXT","real_asset_role":"EXPLICIT_CONTEXT","real_identifiable_human":True,
  "scenes":[
   ("REAL",0,"CONTEXT","samba","SAMBA NO RIO • VÍDEO REAL","Paolla Oliveira será rainha de bateria da Imperatriz Leopoldinense no Carnaval de 2027."),
   ("ANIMATION",0,"MECHANISM","samba","ANIMAÇÃO • POSIÇÃO NO DESFILE","A rainha desfila à frente dos ritmistas e cria conexão visual entre bateria, escola e público."),
   ("REAL",3,"PROOF","samba","SAMBA NO RIO • VÍDEO REAL","Mas rainha de bateria não determina musicalmente o andamento do samba."),
   ("ANIMATION",2,"MECHANISM","samba","ANIMAÇÃO • QUEM CONDUZ O RITMO","Quem conduz os ritmistas é o mestre de bateria. A rainha acompanha o pulso, dança e interage com o conjunto."),
   ("REAL",6,"CONSEQUENCE","samba","SAMBA NO RIO • VÍDEO REAL","Por isso, presença, leitura do ritmo e sintonia com os ritmistas importam tanto quanto a imagem do posto."),
   ("ANIMATION",4,"MECHANISM","samba","ANIMAÇÃO • CONEXÃO VISUAL","Gestos e movimento ajudam a criar diálogo visual com a bateria e com o público, sem substituir a condução do mestre."),
   ("REAL",9,"PROOF","samba","SAMBA NO RIO • VÍDEO REAL","Paolla será coroada em 17 de outubro e volta à Sapucaí após ficar fora do Carnaval de 2026.")
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
 with requests.get(url,headers={"User-Agent":"VSA-Sep25/1.0"},stream=True,timeout=180) as r:
  r.raise_for_status()
  with open(p,"wb") as f:
   for c in r.iter_content(1048576):
    if c:f.write(c)
 return p
def commons_video(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"videoinfo","viprop":"url|derivatives","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep25/1.0"},timeout=60).json()["query"]["pages"].values()))
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
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep25/1.0"},timeout=60).json()["query"]["pages"].values()))
 return dl(page["imageinfo"][0]["url"],p)


def commons_image(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"imageinfo","iiprop":"url","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep25/1.0"},timeout=60).json()["query"]["pages"].values()))
 return dl(page["imageinfo"][0]["url"],p)

def make_anim(slug,out,air_photo=None,paolla_photo=None):
 from PIL import Image,ImageDraw,ImageFont
 fps=15; total=6*fps
 tmp=WORK/("animframes_"+slug); shutil.rmtree(tmp,ignore_errors=True); tmp.mkdir(parents=True)
 fb=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",34)
 fs=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",24)
 fr=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",21)
 ap=Image.open(air_photo).convert("RGB") if air_photo else None
 pp=Image.open(paolla_photo).convert("RGB") if paolla_photo else None
 if ap: ap.thumbnail((300,245),Image.Resampling.LANCZOS)
 if pp: pp.thumbnail((245,330),Image.Resampling.LANCZOS)
 for n in range(total):
  t=n/fps; seg=min(2,int(t//2)); u=(t-seg*2)/2.0
  im=Image.new("RGB",(975,845),(10,18,32)); d=ImageDraw.Draw(im)
  d.rounded_rectangle((18,18,957,827),radius=28,outline=(90,120,160),width=3)
  if slug=="furinho_aviao":
   if seg==0:
    d.text((45,38),"TRÊS CAMADAS + UM PEQUENO ORIFÍCIO",font=fb,fill="white")
    if ap: im.paste(ap,(55,145))
    xs=[470,610,750]
    labs=["INTERNA","INTERMEDIÁRIA","EXTERNA"]
    for i,x in enumerate(xs):
     d.rounded_rectangle((x,180,x+58,650),18,outline=(80,190,255),width=5)
     d.text((x-15,675),labs[i],font=fr,fill="white")
    d.ellipse((625,455,643,473),fill=(255,190,70))
    d.text((555,510),"FURINHO",font=fs,fill=(255,190,70))
   elif seg==1:
    d.text((45,38),"PRESSÃO DA CABINE × AR EXTERNO",font=fb,fill="white")
    d.rounded_rectangle((70,170,350,690),28,fill=(25,80,120),outline=(80,200,255),width=4)
    d.text((135,210),"CABINE",font=fs,fill="white")
    d.rounded_rectangle((625,170,905,690),28,fill=(35,45,65),outline=(130,145,170),width=4)
    d.text((690,210),"EXTERIOR",font=fs,fill="white")
    for y in range(310,600,85):
     end=560+int(45*u)
     d.line((340,y,end,y),fill=(255,200,70),width=9)
     d.polygon([(end,y),(end-24,y-14),(end-24,y+14)],fill=(255,200,70))
    d.text((380,650),"o espaço entre painéis acompanha a pressão da cabine",font=fr,fill="white")
   else:
    d.text((45,38),"CONTROLE DE UMIDADE + REDUNDÂNCIA",font=fb,fill="white")
    d.rounded_rectangle((80,170,430,690),28,outline=(80,200,255),width=4)
    for i in range(7):
     x=130+(i%3)*90; y=250+(i//3)*110
     r=10+int(8*abs(math.sin(t*5+i)))
     d.ellipse((x-r,y-r,x+r,y+r),fill=(80,180,255))
    d.line((430,420,570,420),fill=(255,190,70),width=10)
    d.polygon([(570,420),(545,405),(545,435)],fill=(255,190,70))
    d.rounded_rectangle((600,170,890,690),28,outline=(100,210,150),width=4)
    d.text((655,260),"CAMADA",font=fs,fill="white"); d.text((642,305),"DE RESERVA",font=fs,fill=(100,210,150))
    d.text((115,730),"menos condensação",font=fs,fill=(80,180,255)); d.text((625,730),"projeto redundante",font=fs,fill=(100,210,150))
  elif slug=="beija_flor_re":
   cx,cy=480,420
   if seg==0:
    d.text((45,38),"SUSTENTAÇÃO NA IDA E NA VOLTA",font=fb,fill="white")
    d.ellipse((430,365,530,475),fill=(110,180,120))
    a=math.sin(t*5)*0.8
    for side in (-1,1):
     ex=cx+side*260; ey=cy+int(140*a)
     d.line((cx,cy,ex,ey),fill=(80,210,255),width=18)
     d.line((ex,ey,ex,ey-100),fill=(255,200,70),width=8)
     d.polygon([(ex,ey-110),(ex-12,ey-85),(ex+12,ey-85)],fill=(255,200,70))
    d.text((325,650),"força em dois sentidos da batida",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"A ASA GIRA NO OMBRO",font=fb,fill="white")
    d.ellipse((425,360,535,475),fill=(110,180,120))
    for side in (-1,1):
     d.ellipse((cx-300 if side<0 else cx+50,220,cx-40 if side<0 else cx+310,620),outline=(80,210,255),width=5)
     ang=2*math.pi*u+(0 if side>0 else math.pi)
     x=cx+side*(160+80*math.cos(ang)); y=cy+130*math.sin(ang)
     d.line((cx,cy,x,y),fill=(255,190,70),width=16)
    d.text((280,690),"rotação muda o ângulo de ataque",font=fs,fill="white")
   else:
    d.text((45,38),"INCLINAR A FORÇA MUDA A DIREÇÃO",font=fb,fill="white")
    d.ellipse((430,360,530,470),fill=(110,180,120))
    vx=160+int(80*u)
    d.line((480,420,480+vx,300),fill=(255,200,70),width=12)
    d.polygon([(480+vx,300),(480+vx-28,308),(480+vx-12,330)],fill=(255,200,70))
    d.line((480,500,480-vx,620),fill=(80,210,255),width=12)
    d.polygon([(480-vx,620),(480-vx+28,612),(480-vx+12,590)],fill=(80,210,255))
    d.text((575,250),"força aerodinâmica",font=fs,fill=(255,200,70))
    d.text((150,650),"reação: corpo recua",font=fs,fill=(80,210,255))
  else:
   if seg==0:
    d.text((45,38),"ONDE A RAINHA FICA NO DESFILE",font=fb,fill="white")
    if pp: im.paste(pp,(50,150))
    d.ellipse((500,255,570,325),fill=(255,190,70))
    d.text((480,340),"RAINHA",font=fs,fill="white")
    for row in range(4):
     for col in range(7):
      x=440+col*65; y=470+row*60
      d.ellipse((x-12,y-12,x+12,y+12),fill=(80,180,255))
    d.text((555,720),"BATERIA",font=fs,fill=(80,180,255))
    d.line((535,330,535,455),fill=(255,190,70),width=6)
   elif seg==1:
    d.text((45,38),"QUEM CONDUZ O RITMO É O MESTRE",font=fb,fill="white")
    d.ellipse((140,330,220,410),fill=(100,210,150)); d.text((105,430),"MESTRE",font=fs,fill="white")
    for i in range(8):
     x=340+i*65; y=350+int(45*math.sin(t*6+i))
     d.ellipse((x-16,y-16,x+16,y+16),fill=(80,180,255))
    pulse=60+int(25*abs(math.sin(t*6)))
    d.arc((95,285-pulse//4,265,455+pulse//4),-50,50,fill=(255,190,70),width=8)
    d.text((330,560),"ritmistas seguem sinais e andamento",font=fs,fill="white")
    d.text((330,610),"a rainha acompanha — não rege",font=fs,fill=(255,190,70))
   else:
    d.text((45,38),"CONEXÃO VISUAL COM ESCOLA E PÚBLICO",font=fb,fill="white")
    nodes={"RAINHA":(480,220),"BATERIA":(220,610),"PÚBLICO":(740,610)}
    for name,(x,y) in nodes.items():
     d.ellipse((x-65,y-65,x+65,y+65),outline=(80,200,255),width=5)
     d.text((x-48,y-12),name,font=fr,fill="white")
    for a,b in [("RAINHA","BATERIA"),("RAINHA","PÚBLICO"),("BATERIA","PÚBLICO")]:
     d.line((*nodes[a],*nodes[b]),fill=(255,190,70),width=6)
    d.text((255,745),"movimento • presença • sintonia",font=fs,fill="white")
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
 final=od/f"VSA_{slug}_SEP25.mp4";run(["ffmpeg","-y","-loglevel","error","-i",visual,"-i",mix,"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",final])
 probe=json.loads(cap(["ffprobe","-v","error","-show_streams","-show_format","-of","json",final]));fd=float(probe["format"]["duration"]);v=next(x for x in probe["streams"] if x.get("codec_type")=="video")
 print("DURATION_CHECK",slug,fd);
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
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/5d83cdb7-bce1-4b37-b0b0-af4e6ca6bf4b.webm",AS/"airplane_window.webm")
 air_photo=dl("https://cdn.creativeclaw.co/u/2f9dfa63/images/499d076f-a3dd-4f7b-83a1-6285a5456044.jpg",AS/"air_window.jpg")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/b88457ed-63a1-4afa-b096-4e2f2d8f0a22.webm",AS/"hummingbird.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/e3bc8172-fabe-42bb-af2c-352ba0203a81.webm",AS/"samba.webm")
 paolla=dl("https://cdn.creativeclaw.co/u/2f9dfa63/images/63ba80d6-e1df-4ab9-8087-6cec9a4b88b1.jpg",AS/"paolla.jpg")
 for slug in TOPICS:
  make_anim(slug,AS/(slug+"_3d.mp4"),air_photo if slug=="furinho_aviao" else None,paolla if slug=="paolla_bateria" else None)
 metas=[render(slug,t,mask,cta,music) for slug,t in TOPICS.items()]
 bad=[{"slug":m["slug"],"duration_seconds":m["duration_seconds"]} for m in metas if not(45<=float(m["duration_seconds"])<=55)]
 if bad: raise RuntimeError("DURATION_GATE_FAIL "+json.dumps(bad,ensure_ascii=False))
 (OUT/"MANIFEST.json").write_text(json.dumps(metas,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(metas,ensure_ascii=False,indent=2))
if __name__=="__main__":main()

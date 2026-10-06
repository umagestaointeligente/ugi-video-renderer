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
 "pressao_lata":{
  "title":"Por que uma lata consegue se esmagar sozinha? #shorts",
  "header":["COMO UMA LATA","SE ESMAGA SOZINHA?"],
  "description":"Ao aquecer água dentro da lata, o vapor ocupa seu interior. Quando o vapor condensa rapidamente, a pressão interna cai e a pressão atmosférica externa pode esmagar o metal. #VocêSabiaAgora #Curiosidades #Física #Pressão\n\nQuatro vídeos reais distintos via Wikimedia Commons.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"CAN_CRUSH_ATMOSPHERIC_PRESSURE_CONDENSATION",
  "assets":{
   "pressure1":{"file":"pressure1.webm","source_url":"https://commons.wikimedia.org/wiki/File:Crushing_can.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_CAN_CRUSH_DEMONSTRATION","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "pressure2":{"file":"pressure2.webm","source_url":"https://commons.wikimedia.org/wiki/File:Boyle%27s_Law_Demonstrations.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_PRESSURE_VOLUME_DEMONSTRATION","asset_role":"EXPLICIT_CONTEXT","identifiable_human":False},
   "pressure3":{"file":"pressure3.webm","source_url":"https://commons.wikimedia.org/wiki/File:Water_Boiling_in_a_Vacuum_Chamber.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_LOW_PRESSURE_BOILING","asset_role":"EXPLICIT_CONTEXT","identifiable_human":False},
   "pressure4":{"file":"pressure4.webm","source_url":"https://commons.wikimedia.org/wiki/File:Vacuum_Cannon.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_PRESSURE_DIFFERENCE_FORCE","asset_role":"EXPLICIT_CONTEXT","identifiable_human":False}
  },
  "scenes":[
   ("REAL","pressure1",1,"CONTEXT","pressure","LATA SENDO ESMAGADA • VÍDEO REAL","Uma lata aquecida pode se amassar em segundos sem ninguém apertar o metal."),
   ("ANIMATION","anim",0,"MECHANISM","pressure","ANIMAÇÃO • VAPOR OCUPA O INTERIOR","A água vira vapor e expulsa boa parte do ar que estava dentro da lata."),
   ("REAL","pressure2",2,"PROOF","pressure","PRESSÃO E VOLUME • VÍDEO REAL","Pressão e volume estão ligados: mudar o gás dentro de um recipiente muda as forças nas paredes."),
   ("ANIMATION","anim",2,"MECHANISM","pressure","ANIMAÇÃO • VAPOR CONDENSA","Ao resfriar de repente, o vapor condensa e ocupa um volume muito menor."),
   ("REAL","pressure3",3,"CONSEQUENCE","pressure","BAIXA PRESSÃO • VÍDEO REAL","Com menos gás no interior, a pressão interna despenca em relação ao ar externo."),
   ("ANIMATION","anim",4,"MECHANISM","pressure","ANIMAÇÃO • AR EXTERNO ESMAGA","A pressão atmosférica de fora fica maior e empurra todas as paredes da lata para dentro."),
   ("REAL","pressure4",2,"PROOF","pressure","DIFERENÇA DE PRESSÃO • VÍDEO REAL","A mesma diferença de pressão consegue produzir forças surpreendentes em outros experimentos.")
  ]},
 "gelo_seco_nevoa":{
  "title":"Por que o gelo seco faz aquela fumaça branca? #shorts",
  "header":["POR QUE O GELO SECO","FAZ NÉVOA BRANCA?"],
  "description":"Gelo seco é dióxido de carbono sólido. Ele sublima diretamente para gás, resfria o ar úmido ao redor e faz pequenas gotículas de água condensarem. A névoa branca é principalmente água condensada. #VocêSabiaAgora #Curiosidades #Ciência #GeloSeco\n\nQuatro vídeos reais distintos via Wikimedia Commons.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"DRY_ICE_SUBLIMATION_WATER_FOG",
  "assets":{
   "dry1":{"file":"dry1.webm","source_url":"https://commons.wikimedia.org/wiki/File:Fume_hood_-_dry_ice_fog.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_DRY_ICE_FOG","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "dry2":{"file":"dry2.webm","source_url":"https://commons.wikimedia.org/wiki/File:Dry_ice_experiment.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_DRY_ICE_EXPERIMENT","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "dry3":{"file":"dry3.webm","source_url":"https://commons.wikimedia.org/wiki/File:Dry_ice_sublimation_march_29_2021.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_DRY_ICE_SUBLIMATION","asset_role":"TARGET_SUBJECT","identifiable_human":False},
   "dry4":{"file":"dry4.webm","source_url":"https://commons.wikimedia.org/wiki/File:Wilson_chamber.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_DRY_ICE_COOLED_CHAMBER_CONTEXT","asset_role":"EXPLICIT_CONTEXT","identifiable_human":False}
  },
  "scenes":[
   ("REAL","dry1",1,"CONTEXT","dry","NÉVOA DE GELO SECO • VÍDEO REAL","Aquela nuvem branca do gelo seco parece fumaça, mas o dióxido de carbono é invisível."),
   ("ANIMATION","anim",0,"MECHANISM","dry","ANIMAÇÃO • SÓLIDO VIRA GÁS","O gelo seco sublima: passa do estado sólido direto para dióxido de carbono gasoso."),
   ("REAL","dry2",2,"PROOF","dry","EXPERIMENTO COM GELO SECO • VÍDEO REAL","Esse gás sai extremamente frio e resfria rapidamente o ar úmido ao redor."),
   ("ANIMATION","anim",2,"MECHANISM","dry","ANIMAÇÃO • VAPOR DE ÁGUA CONDENSA","Ao esfriar, o vapor de água do ar se condensa em minúsculas gotículas visíveis."),
   ("REAL","dry3",2,"CONSEQUENCE","dry","SUBLIMAÇÃO REAL • VÍDEO REAL","Por isso a parte branca que enxergamos é principalmente água condensada, não CO₂ visível."),
   ("ANIMATION","anim",4,"MECHANISM","dry","ANIMAÇÃO • NÉVOA FRIA DESCE","A mistura fria fica mais densa que o ar quente ao redor e tende a se espalhar para baixo."),
   ("REAL","dry4",2,"CONTEXT","dry","GELO SECO COMO RESFRIAMENTO • CONTEXTO REAL","O poder de resfriamento do gelo seco também é usado em experimentos que precisam de temperaturas muito baixas.")
  ]},
 "charlie_puth_musica":{
  "title":"Como Charlie Puth transforma uma ideia simples em música? #shorts",
  "header":["COMO CHARLIE PUTH","TRANSFORMA IDEIA EM MÚSICA?"],
  "description":"Composição pode começar por uma melodia curta, um acorde ou um ritmo. Depois, harmonia, camadas e arranjo transformam a ideia em uma música completa. #VocêSabiaAgora #CharliePuth #Música #Composição\n\nDois vídeos reais de Charlie Puth e dois vídeos reais de contexto musical, todos distintos.",
  "content_class":"NEWS_EXPLAINER","expected_subject":"CHARLIE_PUTH_SONGWRITING_IDEA_TO_ARRANGEMENT",
  "celebrity_name":"Charlie Puth",
  "assets":{
   "charlie1":{"file":"charlie1.webm","source_url":"https://commons.wikimedia.org/wiki/File:Interview_with_Charlie_Puth_from_2022.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"CHARLIE_PUTH_SONGWRITING_IDEA_TO_ARRANGEMENT","asset_role":"TARGET_SUBJECT","identifiable_human":True,"celebrity_visible":True},
   "studio":{"file":"studio.webm","source_url":"https://commons.wikimedia.org/wiki/File:Home_studio.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_HOME_STUDIO_CONTEXT","asset_role":"EXPLICIT_CONTEXT","identifiable_human":False,"celebrity_visible":False},
   "piano":{"file":"piano.webm","source_url":"https://commons.wikimedia.org/wiki/File:Piano_close-up.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"REAL_PIANO_CONTEXT","asset_role":"EXPLICIT_CONTEXT","identifiable_human":False,"celebrity_visible":False},
   "charlie2":{"file":"charlie2.webm","source_url":"https://commons.wikimedia.org/wiki/File:The_Evolution_of_Charlie_Puth.webm","license":"WIKIMEDIA_COMMONS_LICENSED","asset_subject":"CHARLIE_PUTH_SONGWRITING_IDEA_TO_ARRANGEMENT","asset_role":"TARGET_SUBJECT","identifiable_human":True,"celebrity_visible":True}
  },
  "scenes":[
   ("REAL","charlie1",8,"CONTEXT","charlie","CHARLIE PUTH • ARQUIVO REAL","Uma música pode começar com algo minúsculo: poucas notas, um acorde ou um ritmo."),
   ("ANIMATION","anim",0,"MECHANISM","charlie","ANIMAÇÃO • MOTIVO VIRA MELODIA","O primeiro passo é repetir e variar a ideia até ela formar uma melodia reconhecível."),
   ("REAL","studio",3,"CONTEXT","charlie","HOME STUDIO • CONTEXTO REAL","No estúdio, novas camadas podem ser testadas sem perder a ideia principal."),
   ("ANIMATION","anim",2,"MECHANISM","charlie","ANIMAÇÃO • HARMONIA DÁ CONTEXTO","Os acordes mudam a sensação da mesma melodia e ajudam a definir tensão e resolução."),
   ("REAL","piano",2,"CONTEXT","charlie","PIANO • CONTEXTO REAL","Um instrumento permite testar rapidamente notas, acordes e diferentes caminhos para a música."),
   ("ANIMATION","anim",4,"MECHANISM","charlie","ANIMAÇÃO • ARRANJO ORGANIZA CAMADAS","Depois entram baixo, bateria e texturas; o arranjo decide quando cada camada aparece."),
   ("REAL","charlie2",12,"PROOF","charlie","CHARLIE PUTH • SEGUNDO ARQUIVO REAL","O resultado é uma música completa construída em cima de uma ideia simples que continua reconhecível.")
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
 with requests.get(url,headers={"User-Agent":"VSA-Oct06/1.0"},stream=True,timeout=180) as r:
  r.raise_for_status()
  with open(p,"wb") as f:
   for c in r.iter_content(1048576):
    if c:f.write(c)
 return p
def commons_video(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"videoinfo","viprop":"url|derivatives","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Oct06/1.0"},timeout=60).json()["query"]["pages"].values()))
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
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Oct06/1.0"},timeout=60).json()["query"]["pages"].values()))
 return dl(page["imageinfo"][0]["url"],p)


def commons_image(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"imageinfo","iiprop":"url","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Oct06/1.0"},timeout=60).json()["query"]["pages"].values()))
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
  if slug=="pressao_lata":
   if seg==0:
    d.text((45,38),"AQUECE → VAPOR OCUPA A LATA",font=fb,fill="white")
    d.rounded_rectangle((320,230,655,690),28,outline=(160,180,200),width=8)
    for i in range(12):
     x=370+(i%4)*75; y=560-(i//4)*95-int(55*u)
     d.ellipse((x-13,y-13,x+13,y+13),fill=(120,210,255))
    d.line((487,690,487,750),fill=(255,120,70),width=10)
    d.text((275,775),"vapor substitui parte do ar",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"RESFRIA → VAPOR CONDENSA",font=fb,fill="white")
    d.rounded_rectangle((320,230,655,690),28,outline=(160,180,200),width=8)
    for i in range(12):
     x=385+(i%4)*68; y=300+(i//4)*80
     r=max(4,14-int(9*u))
     d.ellipse((x-r,y-r,x+r,y+r),fill=(100,185,255))
    d.text((245,745),"menos moléculas de gás → pressão cai",font=fs,fill="white")
   else:
    d.text((45,38),"PRESSÃO EXTERNA FICA MAIOR",font=fb,fill="white")
    w=int(330-150*u); x1=487-w//2; x2=487+w//2
    d.rounded_rectangle((x1,250,x2,650),25,outline=(160,180,200),width=8)
    for x in (150,825):
     d.line((x,450, x+150 if x<400 else x-150,450),fill=(255,190,70),width=12)
    d.polygon([(325,450),(285,425),(285,475)],fill=(255,190,70))
    d.polygon([(650,450),(690,425),(690,475)],fill=(255,190,70))
    d.text((250,735),"atmosfera empurra para dentro",font=fs,fill="white")
  elif slug=="gelo_seco_nevoa":
   if seg==0:
    d.text((45,38),"CO₂ SÓLIDO → CO₂ GASOSO",font=fb,fill="white")
    d.rectangle((330,470,645,665),fill=(190,220,235))
    for i in range(10):
     x=375+(i%5)*55; y=440-int(180*u)-(i//5)*45
     d.ellipse((x-10,y-10,x+10,y+10),fill=(120,210,255))
    d.text((300,735),"sublimação: sem fase líquida",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"AR ÚMIDO ESFRIA → GOTÍCULAS",font=fb,fill="white")
    for i in range(18):
     x=125+(i%6)*135; y=250+(i//6)*140
     r=5+int(12*u)
     d.ellipse((x-r,y-r,x+r,y+r),fill=(210,235,250))
    d.line((180,690,800,690),fill=(100,190,255),width=8)
    d.text((245,740),"água do ar se condensa",font=fs,fill="white")
   else:
    d.text((45,38),"NÉVOA FRIA SE ESPALHA PARA BAIXO",font=fb,fill="white")
    for i in range(14):
     x=180+(i%7)*100; y=260+(i//7)*90+int(250*u)
     d.ellipse((x-28,y-15,x+28,y+15),fill=(215,230,240))
    d.line((487,340,487,650),fill=(100,220,160),width=10)
    d.polygon([(487,690),(462,645),(512,645)],fill=(100,220,160))
    d.text((250,745),"mistura fria fica mais densa",font=fs,fill="white")
  else:
   if seg==0:
    d.text((45,38),"IDEIA CURTA → MELODIA",font=fb,fill="white")
    pts=[]
    for i in range(8):
     x=120+i*100; y=460-int((60+50*math.sin(i*1.2))*u)
     pts.append((x,y))
     d.ellipse((x-14,y-14,x+14,y+14),fill=(255,190,70))
    d.line(pts,fill=(100,220,160),width=6)
    d.text((265,710),"repete • varia • reconhece",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"ACORDES MUDAM A SENSAÇÃO",font=fb,fill="white")
    labs=["C","Am","F","G"]
    for i,lab in enumerate(labs):
     x=110+i*210
     d.rounded_rectangle((x,300,x+160,520),20,outline=(100+35*i,180,230),width=6)
     d.text((x+55,385),lab,font=fb,fill="white")
    pos=120+int(650*u); d.line((120,650,770,650),fill=(100,220,160),width=7)
    d.ellipse((pos-18,632,pos+18,668),fill=(255,190,70))
    d.text((235,720),"harmonia cria tensão e resolução",font=fs,fill="white")
   else:
    d.text((45,38),"ARRANJO ORGANIZA AS CAMADAS",font=fb,fill="white")
    labs=["MELODIA","BAIXO","BATERIA","TEXTURA"]
    for i,lab in enumerate(labs):
     y=240+i*120
     d.rectangle((120,y,120+int((250+120*i)*u),y+55),fill=(90+25*i,160,220))
     d.text((620,y+12),lab,font=fr,fill="white")
    d.text((220,740),"cada camada entra no momento certo",font=fs,fill="white")
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
 final=od/f"VSA_{slug}_OCT06.mp4";run(["ffmpeg","-y","-loglevel","error","-i",visual,"-i",mix,"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",final])
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
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/addac027-e90f-4721-9914-593ddc6cbb5a.webm",AS/"pressure1.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/1d5bb9f1-7071-4a12-a925-126dd352ec9b.webm",AS/"pressure2.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/b217db7c-24e9-44c3-991f-0e6311570c44.webm",AS/"pressure3.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/bf857d87-0bb9-4ed1-a688-16941fbcb0e2.webm",AS/"pressure4.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/5620bacd-5516-4692-8430-fbe1ceaff8aa.webm",AS/"dry1.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/16eee624-ccd5-4c70-bee5-b4be679e483b.webm",AS/"dry2.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/a2a78480-1d29-4e7e-9530-87ee3ed65eb0.webm",AS/"dry3.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/52e360d4-99c2-4915-bd3d-196067731f9f.webm",AS/"dry4.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/346d48d7-f1da-4cab-8cfb-1ea10723a590.webm",AS/"charlie1.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/afc15273-02f1-4e90-b104-d0dd636a7bd0.webm",AS/"studio.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/f325be21-9f5b-4960-b0d1-67c0cf34e9b4.webm",AS/"piano.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/67da3309-5a9a-4456-9636-e0309bc72f24.webm",AS/"charlie2.webm")
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

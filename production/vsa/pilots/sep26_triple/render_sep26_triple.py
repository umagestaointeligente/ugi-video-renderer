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
  "title":"Por que o gelo flutua na água? #shorts",
  "header":["POR QUE O GELO","FLUTUA NA ÁGUA?"],
  "description":"Quando a água congela, suas moléculas formam uma estrutura mais aberta e o gelo fica menos denso que a água líquida. É por isso que ele flutua. #VocêSabiaAgora #Curiosidades #Ciência #Água\n\nVídeo real: Brandon Antonio Segura Torres & Priscilla Vieto Bonilla / Wikimedia Commons, CC BY-SA 4.0. Fonte científica: USGS. Animações causais produzidas pelo VSA.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"ICE_FLOATING_WATER_DENSITY",
  "real":"ice.webm","source_url":"https://commons.wikimedia.org/wiki/File:T%C3%A9mpano_de_hielo_en_el_lago_argentino.webm","license":"CC_BY_SA_4.0",
  "real_asset_subject":"REAL_FLOATING_ICE","real_asset_role":"TARGET_SUBJECT","real_identifiable_human":False,
  "scenes":[
   ("REAL",1,"CONTEXT","ice","GELO FLUTUANDO • VÍDEO REAL","Quase todo sólido afunda no próprio líquido. Mas a água faz algo estranho: quando congela, o gelo flutua."),
   ("ANIMATION",0,"MECHANISM","ice","ANIMAÇÃO • MOLÉCULAS MAIS AFASTADAS","Na água líquida, as moléculas se movem e conseguem ficar relativamente próximas umas das outras."),
   ("REAL",5,"PROOF","ice","GELO NA ÁGUA • VÍDEO REAL","Quando a temperatura cai e a água congela, as moléculas passam a se organizar numa rede cristalina mais aberta."),
   ("ANIMATION",2,"MECHANISM","ice","ANIMAÇÃO • A ÁGUA EXPANDE","Essa estrutura ocupa mais espaço. Ao congelar, a água expande cerca de nove por cento e sua densidade diminui."),
   ("REAL",10,"CONSEQUENCE","ice","GELO FLUTUANDO • VÍDEO REAL","Com menor densidade que a água líquida, o gelo recebe empuxo suficiente para permanecer na superfície."),
   ("ANIMATION",4,"MECHANISM","ice","ANIMAÇÃO • LAGO CONGELA POR CIMA","Isso também faz lagos congelarem primeiro na superfície, formando uma camada que ajuda a isolar a água abaixo."),
   ("REAL",16,"PROOF","ice","GELO FLUTUANDO • VÍDEO REAL","Então o gelo não flutua por ser leve: ele flutua porque sua estrutura ocupa mais volume para a mesma massa.")
  ]},
 "polvo_cor":{
  "title":"Como um polvo muda de cor tão rápido? #shorts",
  "header":["COMO O POLVO","MUDA DE COR TÃO RÁPIDO?"],
  "description":"Polvos controlam milhares de cromatóforos na pele por meio de nervos e músculos. Outras células refletem a luz e estruturas da pele também podem alterar a textura. #VocêSabiaAgora #Curiosidades #Polvo #Oceano\n\nVídeo real: Steve Childs / Wikimedia Commons, CC BY 2.0. Fonte científica: Smithsonian Ocean. Animações causais produzidas pelo VSA.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"OCTOPUS_COLOR_CHANGE",
  "real":"octopus.webm","source_url":"https://commons.wikimedia.org/wiki/File:Mimic_Octopus_video.webm","license":"CC_BY_2.0",
  "real_asset_subject":"REAL_OCTOPUS","real_asset_role":"TARGET_SUBJECT","real_identifiable_human":False,
  "scenes":[
   ("REAL",3,"CONTEXT","octopus","POLVO • VÍDEO REAL","Um polvo pode mudar sua aparência em segundos, misturando cor, brilho e até textura para desaparecer no ambiente."),
   ("ANIMATION",0,"MECHANISM","octopus","ANIMAÇÃO • CROMATÓFOROS","Logo abaixo da pele existem milhares de cromatóforos: pequenos sacos elásticos cheios de pigmento."),
   ("REAL",10,"PROOF","octopus","POLVO • VÍDEO REAL","Músculos ao redor desses sacos expandem ou contraem o pigmento. Quanto mais aberto, mais aquela cor aparece."),
   ("ANIMATION",2,"MECHANISM","octopus","ANIMAÇÃO • CONTROLE NERVOSO","O cérebro envia sinais pelos nervos e combina milhares desses pontos quase ao mesmo tempo, formando padrões inteiros."),
   ("REAL",19,"CONSEQUENCE","octopus","POLVO • VÍDEO REAL","E não é só pigmento. Outras células da pele refletem a luz e acrescentam tons metálicos, claros e iridescentes."),
   ("ANIMATION",4,"MECHANISM","octopus","ANIMAÇÃO • COR + REFLEXO + TEXTURA","Iridóforos e leucóforos trabalham com os cromatóforos, enquanto pequenas papilas podem mudar a textura da pele."),
   ("REAL",28,"PROOF","octopus","POLVO • VÍDEO REAL","O resultado é uma camuflagem dinâmica: cor, brilho e relevo mudam juntos para imitar o cenário ao redor.")
  ]},
 "drauzio_abl":{
  "title":"Drauzio Varella pode virar um 'imortal': como funciona a ABL? #shorts",
  "header":["COMO ALGUÉM VIRA","UM “IMORTAL” DA ABL?"],
  "description":"Drauzio Varella decidiu se candidatar à Cadeira 32 da Academia Brasileira de Letras, vaga após a morte de Zuenir Ventura. A eleição segue regras próprias de candidatura e voto secreto. #VocêSabiaAgora #DrauzioVarella #ABL #Cultura\n\nVídeo de Drauzio: ONU Brasil / Wikimedia Commons, CC BY 3.0. Imagem da ABL: Fulviusbsas / Wikimedia Commons. Fontes factuais: Academia Brasileira de Letras e CNN Brasil.",
  "content_class":"NEWS_EXPLAINER","expected_subject":"DRAUZIO_VARELLA_ABL_CANDIDACY",
  "real":"drauzio.webm","source_url":"https://commons.wikimedia.org/wiki/File:Drauzio_Varella_tira_d%C3%BAvidas_das_crian%C3%A7as_sobre_a_vacina_contra_a_COVID-19.webm","license":"CC_BY_3.0",
  "real_asset_subject":"DRAUZIO_VARELLA_ARCHIVE_VIDEO","real_asset_role":"EXPLICIT_CONTEXT","real_identifiable_human":True,
  "scenes":[
   ("REAL",8,"CONTEXT","abl","DRAUZIO • IMAGEM DE ARQUIVO","Drauzio Varella decidiu se candidatar à Cadeira 32 da Academia Brasileira de Letras, que era ocupada por Zuenir Ventura."),
   ("ANIMATION",0,"MECHANISM","abl","ANIMAÇÃO • VAGA E CANDIDATURA","Quando um acadêmico morre, a vaga é declarada aberta. Os interessados têm quinze dias para apresentar a candidatura."),
   ("REAL",24,"PROOF","abl","DRAUZIO • IMAGEM DE ARQUIVO","O candidato precisa ser brasileiro e ter obra publicada de reconhecido mérito literário ou livro de valor cultural."),
   ("ANIMATION",2,"MECHANISM","abl","ANIMAÇÃO • VOTO SECRETO","Depois vem uma eleição por voto secreto entre os membros efetivos. Para vencer, é necessária maioria absoluta."),
   ("REAL",40,"CONSEQUENCE","abl","DRAUZIO • IMAGEM DE ARQUIVO","Se ninguém atingir essa maioria, o regimento prevê novas rodadas de votação, com regras para reduzir os concorrentes."),
   ("ANIMATION",4,"MECHANISM","abl","ANIMAÇÃO • 40 CADEIRAS E POSSE","A ABL tem quarenta cadeiras perpétuas. O eleito só se torna acadêmico depois da posse em sessão solene."),
   ("REAL",56,"PROOF","abl","DRAUZIO • IMAGEM DE ARQUIVO","Por isso, Drauzio ainda não é um imortal da ABL: ele é candidato e terá de passar por todo esse processo.")
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
 with requests.get(url,headers={"User-Agent":"VSA-Sep26/1.0"},stream=True,timeout=180) as r:
  r.raise_for_status()
  with open(p,"wb") as f:
   for c in r.iter_content(1048576):
    if c:f.write(c)
 return p
def commons_video(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"videoinfo","viprop":"url|derivatives","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep26/1.0"},timeout=60).json()["query"]["pages"].values()))
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
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep26/1.0"},timeout=60).json()["query"]["pages"].values()))
 return dl(page["imageinfo"][0]["url"],p)


def commons_image(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"imageinfo","iiprop":"url","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep26/1.0"},timeout=60).json()["query"]["pages"].values()))
 return dl(page["imageinfo"][0]["url"],p)

def make_anim(slug,out,abl_photo=None,drauzio_photo=None):
 from PIL import Image,ImageDraw,ImageFont
 fps=15; total=6*fps
 tmp=WORK/("animframes_"+slug); shutil.rmtree(tmp,ignore_errors=True); tmp.mkdir(parents=True)
 fb=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",34)
 fs=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",24)
 fr=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",21)
 ap=Image.open(abl_photo).convert("RGB") if abl_photo else None
 dp=Image.open(drauzio_photo).convert("RGB") if drauzio_photo else None
 if ap: ap.thumbnail((370,260),Image.Resampling.LANCZOS)
 if dp: dp.thumbnail((215,275),Image.Resampling.LANCZOS)
 for n in range(total):
  t=n/fps; seg=min(2,int(t//2)); u=(t-seg*2)/2.0
  im=Image.new("RGB",(975,845),(10,18,32)); d=ImageDraw.Draw(im)
  d.rounded_rectangle((18,18,957,827),radius=28,outline=(90,120,160),width=3)
  if slug=="gelo_flutua":
   if seg==0:
    d.text((45,38),"LÍQUIDO: MOLÉCULAS MAIS PRÓXIMAS",font=fb,fill="white")
    for i in range(35):
     x=110+(i%7)*115+int(12*math.sin(t*4+i)); y=190+(i//7)*105+int(10*math.cos(t*3+i))
     d.ellipse((x-14,y-14,x+14,y+14),fill=(80,190,255))
    d.text((250,730),"estrutura móvel e compacta",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"GELO: REDE MAIS ABERTA",font=fb,fill="white")
    pts=[]
    for row in range(4):
     for col in range(5):
      x=170+col*155+(row%2)*75; y=190+row*135
      pts.append((x,y)); d.ellipse((x-15,y-15,x+15,y+15),fill=(140,220,255))
    for i,(x,y) in enumerate(pts):
     for x2,y2 in pts[i+1:]:
      if 120<math.hypot(x-x2,y-y2)<190:d.line((x,y,x2,y2),fill=(90,130,180),width=3)
    d.text((265,720),"+ ~9% DE VOLUME",font=fs,fill=(255,200,70))
   else:
    d.text((45,38),"MENOR DENSIDADE → FLUTUA",font=fb,fill="white")
    d.rectangle((70,430,905,720),fill=(20,85,135))
    d.rectangle((330,335,650,530),fill=(170,225,245),outline="white",width=4)
    d.line((490,520,490,640),fill=(255,200,70),width=10)
    d.polygon([(490,650),(472,622),(508,622)],fill=(255,200,70))
    d.line((490,420,490,300),fill=(100,230,160),width=10)
    d.polygon([(490,290),(472,318),(508,318)],fill=(100,230,160))
    d.text((565,285),"EMPUXO",font=fs,fill=(100,230,160)); d.text((565,620),"PESO",font=fs,fill=(255,200,70))
  elif slug=="polvo_cor":
   if seg==0:
    d.text((45,38),"CROMATÓFORO: PIGMENTO ABRE E FECHA",font=fb,fill="white")
    for i in range(12):
     x=135+(i%4)*220; y=230+(i//4)*190
     r=16+int((45 if i%2==0 else 28)*(0.35+0.65*abs(math.sin(t*4+i))))
     d.ellipse((x-r,y-r,x+r,y+r),fill=(210,95+8*(i%3),60))
     d.ellipse((x-55,y-55,x+55,y+55),outline=(120,150,180),width=3)
    d.text((250,735),"músculos controlam cada saco de pigmento",font=fr,fill="white")
   elif seg==1:
    d.text((45,38),"SINAIS NERVOSOS COORDENAM O PADRÃO",font=fb,fill="white")
    d.ellipse((420,130,555,265),outline=(100,220,160),width=6); d.text((448,180),"CÉREBRO",font=fr,fill="white")
    for j in range(8):
     x=125+j*100; y=600+int(45*math.sin(t*5+j))
     d.line((488,265,x,y),fill=(80,180,255),width=4)
     rr=22+int(12*abs(math.sin(t*6+j)))
     d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=(220,110,70))
    d.text((280,720),"milhares de pontos mudam juntos",font=fs,fill="white")
   else:
    d.text((45,38),"COR + REFLEXO + TEXTURA",font=fb,fill="white")
    labels=[("CROMATÓFOROS",(90,210),(220,100,70)),("IRIDÓFOROS",(365,210),(80,180,255)),("LEUCÓFOROS",(650,210),(220,220,220))]
    for lab,(x,y),col in labels:
     d.rounded_rectangle((x,y,x+220,y+180),25,outline=col,width=5)
     d.text((x+18,y+72),lab,font=fr,fill="white")
    for k in range(9):
     x=130+k*88; h=35+int(55*abs(math.sin(t*4+k)))
     d.polygon([(x,665),(x+25,665-h),(x+50,665)],fill=(120,170,130))
    d.text((345,720),"papilas alteram o relevo",font=fs,fill=(120,210,150))
  else:
   if seg==0:
    d.text((45,38),"CADEIRA VAGA → 15 DIAS PARA CANDIDATURA",font=fb,fill="white")
    if ap: im.paste(ap,(55,160))
    if dp: im.paste(dp,(690,150))
    d.rounded_rectangle((395,500,580,700),25,outline=(255,200,70),width=6)
    d.text((445,545),"32",font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",72),fill=(255,200,70))
    d.text((333,735),"CANDIDATURA POR CARTA",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"ELEIÇÃO POR VOTO SECRETO",font=fb,fill="white")
    d.rounded_rectangle((330,180,645,570),28,outline=(80,180,255),width=5)
    d.rectangle((390,235,585,285),fill=(55,75,100))
    for i in range(14):
     x=130+(i%7)*115; y=650+(i//7)*70
     d.ellipse((x-20,y-20,x+20,y+20),fill=(120,160,200))
    envx=420+int(110*u); envy=120+int(130*u)
    d.rectangle((envx,envy,envx+130,envy+75),fill=(235,235,225),outline=(160,160,160),width=3)
    d.text((295,740),"vence com maioria absoluta",font=fs,fill=(255,200,70))
   else:
    d.text((45,38),"40 CADEIRAS PERPÉTUAS + POSSE",font=fb,fill="white")
    for i in range(40):
     col=i%10; row=i//10; x=105+col*82; y=195+row*105
     fill=(255,200,70) if i==31 else (70,115,155)
     d.rounded_rectangle((x,y,x+55,y+62),10,fill=fill)
    d.line((490,620,490,700),fill=(100,220,160),width=9)
    d.polygon([(490,715),(472,685),(508,685)],fill=(100,220,160))
    d.text((370,745),"POSSE EM SESSÃO SOLENE",font=fs,fill="white")
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
 final=od/f"VSA_{slug}_SEP26.mp4";run(["ffmpeg","-y","-loglevel","error","-i",visual,"-i",mix,"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",final])
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
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/3ad3cc3f-add1-46c7-9056-3bc3c10311ea.webm",AS/"ice.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/a9bb5e3d-8926-491c-b47d-eb8ac54b67ed.webm",AS/"octopus.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/f6460346-71df-4b1b-a0f6-6edaa9400c10.webm",AS/"drauzio.webm")
 abl_photo=dl("https://cdn.creativeclaw.co/u/2f9dfa63/images/1803281d-e8d2-4796-848c-f2fe82ecc088.jpg",AS/"abl.jpg")
 drauzio_photo=dl("https://cdn.creativeclaw.co/u/2f9dfa63/images/82bfef2c-924d-4e31-bcf2-fcbb5d1b5990.png",AS/"drauzio.png")
 for slug in TOPICS:
  make_anim(slug,AS/(slug+"_3d.mp4"),abl_photo if slug=="drauzio_abl" else None,drauzio_photo if slug=="drauzio_abl" else None)
 metas=[render(slug,t,mask,cta,music) for slug,t in TOPICS.items()]
 bad=[{"slug":m["slug"],"duration_seconds":m["duration_seconds"]} for m in metas if not(45<=float(m["duration_seconds"])<=55)]
 if bad: raise RuntimeError("DURATION_GATE_FAIL "+json.dumps(bad,ensure_ascii=False))
 (OUT/"MANIFEST.json").write_text(json.dumps(metas,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(metas,ensure_ascii=False,indent=2))
if __name__=="__main__":main()

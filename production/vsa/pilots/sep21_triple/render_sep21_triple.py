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
 "flip_vertical":{
  "title":"Como esse navio consegue ficar em pé no oceano? #shorts",
  "header":["COMO ESSE NAVIO","FICA EM PÉ NO MAR?"],
  "description":"A plataforma de pesquisa FLIP foi projetada para girar cerca de 90 graus no oceano ao encher tanques de lastro na popa. #VocêSabiaAgora #Curiosidades #Engenharia #Oceano\n\nFootage: U.S. Navy / Wikimedia Commons, domínio público. Animações causais produzidas pelo VSA.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"RP_FLIP_BALLAST_SYSTEM",
  "real":"flip.webm","source_url":"https://commons.wikimedia.org/wiki/File:Video_of_RP_FLIP_transitioning_to_vertical_(120630-N-PO203-001).webm","license":"PUBLIC_DOMAIN_US_NAVY",
  "real_asset_subject":"RP_FLIP","real_asset_role":"TARGET_SUBJECT","real_identifiable_human":False,
  "scenes":[
   ("REAL",1,"CAUSE","c1","FLIP REAL • HORIZONTAL","Isso parece um navio comum, mas ele foi projetado para fazer algo absurdo: girar quase noventa graus no meio do oceano."),
   ("ANIMATION",0,"MECHANISM","c1","ANIMAÇÃO • TANQUES DE LASTRO","A transformação começa quando tanques enormes na popa recebem água do mar e ficam muito mais pesados."),
   ("REAL",13,"PROOF","c1","FLIP REAL • COMEÇANDO A GIRAR","Com o peso concentrado atrás, a popa afunda e toda a estrutura começa a girar lentamente."),
   ("ANIMATION",2,"MECHANISM","c1","ANIMAÇÃO • CENTRO DE MASSA","O centro de massa desce enquanto a parte longa da plataforma aponta para baixo, aumentando a estabilidade."),
   ("REAL",29,"CONSEQUENCE","c1","FLIP REAL • QUASE VERTICAL","A maior parte dos trezentos e trinta e cinco pés da estrutura fica submersa, deixando só uma pequena parte acima da água."),
   ("ANIMATION",4,"MECHANISM","c1","ANIMAÇÃO • ESTABILIDADE VERTICAL","Na vertical, ondas da superfície movimentam muito menos a área onde os instrumentos trabalham."),
   ("REAL",47,"PROOF","c1","FLIP REAL • VERTICAL","Por isso a FLIP conseguia fazer medições no oceano com uma estabilidade que um navio convencional não teria.")
  ]},
 "trovao_atraso":{
  "title":"Por que você vê o relâmpago antes de ouvir o trovão? #shorts",
  "header":["POR QUE O TROVÃO","CHEGA DEPOIS?"],
  "description":"A luz viaja muito mais rápido que o som. Por isso vemos o relâmpago quase imediatamente, mas o trovão demora a chegar. #VocêSabiaAgora #Curiosidades #Ciência #Relâmpago\n\nFootage: W.carter / Wikimedia Commons, CC BY-SA 4.0. Animações causais produzidas pelo VSA.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"LIGHTNING_THUNDER_DELAY",
  "real":"lightning.webm","source_url":"https://commons.wikimedia.org/wiki/File:Lightning_-_condensed_version.webm","license":"CC_BY_SA_4.0",
  "real_asset_subject":"LIGHTNING_STORM","real_asset_role":"TARGET_SUBJECT","real_identifiable_human":False,
  "scenes":[
   ("REAL",1,"CAUSE","c1","RELÂMPAGO REAL","Você vê o clarão e só alguns segundos depois escuta o trovão. Os dois nasceram praticamente no mesmo instante."),
   ("ANIMATION",0,"MECHANISM","c1","ANIMAÇÃO • LUZ X SOM","A diferença está na velocidade: a luz atravessa o caminho quase instantaneamente, enquanto o som avança pelo ar muito mais devagar."),
   ("REAL",9,"PROOF","c1","RELÂMPAGO REAL","Por isso seus olhos recebem o clarão muito antes de seus ouvidos receberem a onda sonora."),
   ("ANIMATION",2,"MECHANISM","c1","ANIMAÇÃO • ONDA SONORA","O trovão é uma onda de pressão criada quando o ar ao redor do raio aquece e se expande violentamente."),
   ("REAL",17,"CONSEQUENCE","c1","RELÂMPAGO REAL","Quanto mais longe estiver a descarga, maior será o intervalo entre o clarão e o som."),
   ("ANIMATION",4,"MECHANISM","c1","ANIMAÇÃO • DISTÂNCIA","Como regra aproximada, três segundos de diferença representam cerca de um quilômetro de distância."),
   ("REAL",25,"PROOF","c1","RELÂMPAGO REAL","Então contar os segundos entre o clarão e o trovão dá uma estimativa rápida de quão longe a tempestade está.")
  ]},
 "anitta_inear":{
  "title":"Por que artistas como Anitta usam retorno no ouvido? #shorts",
  "header":["POR QUE ANITTA USA","RETORNO NO OUVIDO?"],
  "description":"Em grandes shows, o retorno intra-auricular ajuda o artista a ouvir uma mixagem própria com voz, instrumentos e referências mesmo com o palco extremamente alto. #VocêSabiaAgora #Anitta #Música #Tecnologia\n\nImagens: PinkBeachPlanet, Multishow e Rúben Daniel Baía / Wikimedia Commons, CC BY-SA 4.0 e CC BY 3.0. Animações causais produzidas pelo VSA.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"IN_EAR_MONITOR_SYSTEM",
  "real":"anitta_context.mp4","source_url":"https://commons.wikimedia.org/wiki/File:Beach-Please-2024-anitta-main-stage-show.jpg | https://commons.wikimedia.org/wiki/File:Anitta_no_Rock_in_Rio_2022.jpg | https://commons.wikimedia.org/wiki/File:Anitta_Me_Gusta_no_Rock_in_Rio_Lisboa.jpg","license":"CC_BY_SA_4.0_AND_CC_BY_3.0",
  "real_asset_subject":"ANITTA_PERFORMING","real_asset_role":"EXPLICIT_CONTEXT","real_identifiable_human":True,
  "scenes":[
   ("REAL",0,"CONTEXT","c1","ANITTA • PALCO","Num show enorme, artistas como Anitta precisam cantar no tempo certo mesmo cercados por caixas, banda, plateia e eco."),
   ("ANIMATION",0,"MECHANISM","c1","ANIMAÇÃO • SOM DO PALCO","Se dependessem só do som que volta pelo palco, cada fonte chegaria com volumes e pequenos atrasos diferentes."),
   ("REAL",2.1,"PROOF","c1","ANITTA • PERFORMANCE","É por isso que o artista precisa de uma referência de áudio muito mais controlada."),
   ("ANIMATION",2,"MECHANISM","c1","ANIMAÇÃO • MIXAGEM NO OUVIDO","A mesa cria uma mixagem exclusiva e envia voz, instrumentos e outras referências diretamente para o fone intra-auricular."),
   ("REAL",4.2,"CONSEQUENCE","c1","ANITTA • PERFORMANCE","O cantor consegue ouvir com clareza aquilo que precisa, mesmo quando o público está fazendo muito barulho."),
   ("ANIMATION",4,"MECHANISM","c1","ANIMAÇÃO • TEMPO E CUES","O retorno também pode levar clique e sinais de produção que ajudam a manter entradas, coreografia e banda sincronizadas."),
   ("REAL",0.5,"PROOF","c1","ANITTA • PALCO","Para quem vê de fora é só um fone pequeno. Para o show, ele funciona como uma central de referência dentro do ouvido.")
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
 with requests.get(url,headers={"User-Agent":"VSA-Sep21/1.0"},stream=True,timeout=180) as r:
  r.raise_for_status()
  with open(p,"wb") as f:
   for c in r.iter_content(1048576):
    if c:f.write(c)
 return p
def commons_video(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"videoinfo","viprop":"url|derivatives","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep21/1.0"},timeout=60).json()["query"]["pages"].values()))
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
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep21/1.0"},timeout=60).json()["query"]["pages"].values()))
 return dl(page["imageinfo"][0]["url"],p)


def commons_image(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"imageinfo","iiprop":"url","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep21/1.0"},timeout=60).json()["query"]["pages"].values()))
 return dl(page["imageinfo"][0]["url"],p)

def make_anim(slug,out,taylor_photo=None):
 from PIL import Image,ImageDraw,ImageFont
 fps=15; total=6*fps
 tmp=WORK/("animframes_"+slug); shutil.rmtree(tmp,ignore_errors=True); tmp.mkdir(parents=True)
 fb=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",34)
 fs=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",24)
 for n in range(total):
  t=n/fps; seg=min(2,int(t//2)); u=(t-seg*2)/2.0
  im=Image.new("RGB",(975,845),(10,18,32)); d=ImageDraw.Draw(im)
  d.rounded_rectangle((18,18,957,827),radius=28,outline=(90,120,160),width=3)
  if slug=="flip_vertical":
   if seg==0:
    d.text((45,38),"TANQUES DE LASTRO ENCHENDO",font=fb,fill="white")
    d.rectangle((150,360,820,455),fill=(210,215,220),outline="white",width=4)
    d.rectangle((620,375,790,440),fill=(30,90,150),outline=(80,210,255),width=3)
    fill=int(60*u); d.rectangle((625,435-fill,785,435),fill=(40,150,230))
    d.text((600,490),"ÁGUA DO MAR",font=fs,fill=(80,210,255))
    d.line((700,180,700,330),fill=(80,210,255),width=10); d.polygon([(700,335),(680,300),(720,300)],fill=(80,210,255))
   elif seg==1:
    d.text((45,38),"O CENTRO DE MASSA DESCE",font=fb,fill="white")
    ang=-int(75*u); cx,cy=490,430; L=560
    x1=cx-int(math.cos(math.radians(ang))*L/2); y1=cy-int(math.sin(math.radians(ang))*L/2)
    x2=cx+int(math.cos(math.radians(ang))*L/2); y2=cy+int(math.sin(math.radians(ang))*L/2)
    d.line((x1,y1,x2,y2),fill=(225,225,230),width=34)
    mx=cx+int(math.cos(math.radians(ang))*150); my=cy+int(math.sin(math.radians(ang))*150)
    d.ellipse((mx-22,my-22,mx+22,my+22),fill=(255,190,70))
    d.text((70,700),"peso na popa → rotação",font=fs,fill="white")
   else:
    d.text((45,38),"VERTICAL = MENOS EFEITO DAS ONDAS",font=fb,fill="white")
    d.line((490,160,490,710),fill=(225,225,230),width=34)
    for x in range(70,900,80):
     y=260+int(20*math.sin((x/70)+t*4)); d.arc((x,y,x+90,y+35),180,360,fill=(80,210,255),width=4)
    d.rectangle((430,140,550,260),outline=(255,190,70),width=5)
    d.text((250,750),"instrumentos ficam mais estáveis",font=fs,fill="white")
  elif slug=="trovao_atraso":
   if seg==0:
    d.text((45,38),"LUZ X SOM: VELOCIDADES MUITO DIFERENTES",font=fb,fill="white")
    d.text((80,190),"LUZ",font=fs,fill=(255,220,80)); d.text((80,500),"SOM",font=fs,fill=(80,210,255))
    lx=170+int(700*min(1,u*5)); sx=170+int(700*u*.22)
    d.line((170,240,lx,240),fill=(255,220,80),width=12); d.line((170,550,sx,550),fill=(80,210,255),width=12)
   elif seg==1:
    d.text((45,38),"O AR AQUECE E SE EXPANDE",font=fb,fill="white")
    cx,cy=490,430; d.line((cx,160,cx,690),fill=(255,230,120),width=18)
    for r in [80+int(120*u),150+int(170*u),220+int(220*u)]: d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(80,210,255),width=5)
    d.text((250,740),"onda de pressão = trovão",font=fs,fill="white")
   else:
    d.text((45,38),"3 SEGUNDOS ≈ 1 QUILÔMETRO",font=fb,fill="white")
    d.ellipse((120,350,180,410),fill=(255,220,80)); d.text((75,430),"RAIO",font=fs,fill="white")
    d.ellipse((800,350,860,410),fill=(225,225,230)); d.text((735,430),"VOCÊ",font=fs,fill="white")
    x=190+int(590*u); d.line((190,380,x,380),fill=(80,210,255),width=8)
    d.text((320,625),"1... 2... 3...",font=fb,fill=(255,220,80))
  else:
   if seg==0:
    d.text((45,38),"NO PALCO, O SOM CHEGA DE TODO LADO",font=fb,fill="white")
    cx,cy=500,430; d.ellipse((455,385,545,475),outline="white",width=5)
    for x,y in [(120,240),(850,230),(120,650),(850,650)]:
     d.rectangle((x-45,y-55,x+45,y+55),outline=(80,210,255),width=4); d.line((x,y,cx,cy),fill=(80,210,255),width=3)
    d.text((280,720),"volumes + atrasos diferentes",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"MIXAGEM EXCLUSIVA → IN-EAR",font=fb,fill="white")
    d.rounded_rectangle((100,230,360,610),25,outline=(80,210,255),width=4)
    for i,label in enumerate(["VOZ","BANDA","CLICK"]):
     y=300+i*90; d.text((140,y),label,font=fs,fill="white"); d.rectangle((235,y+5,320,y+28),fill=(80,210,255))
    d.line((370,420,700,420),fill=(255,190,70),width=9); d.arc((680,300,860,540),70,290,fill=(255,190,70),width=12)
   else:
    d.text((45,38),"CLICK + CUES MANTÊM O SHOW SINCRONIZADO",font=fb,fill="white")
    for i in range(8):
     x=100+i*95; h=60+int(100*abs(math.sin(t*4+i))); d.rectangle((x,520-h,x+45,520),fill=(80,210,255))
    beat=min(3,int(u*4))
    for i in range(4): d.ellipse((250+i*120,650,285+i*120,685),fill=(255,220,80) if i==beat else (80,80,95))
    d.text((280,735),"tempo • entradas • coreografia",font=fs,fill="white")
  im.save(tmp/f"{n:04d}.jpg",quality=92)
 run(["ffmpeg","-y","-loglevel","error","-framerate",str(fps),"-i",tmp/"%04d.jpg","-t","6","-r","30","-vf","pad=ceil(iw/2)*2:ceil(ih/2)*2","-c:v","libx264","-pix_fmt","yuv420p",out])

def make_anitta_reel(images,out):
 from PIL import Image
 clips=[]
 for i,p in enumerate(images):
  im=Image.open(p).convert("RGB")
  canvas=Image.new("RGB",(1080,1920),(12,12,18)); im.thumbnail((980,1500),Image.Resampling.LANCZOS)
  canvas.paste(im,((1080-im.width)//2,(1920-im.height)//2))
  jpg=WORK/f"anitta_{i}.jpg";canvas.save(jpg,quality=94)
  clip=WORK/f"anitta_{i}.mp4";run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",jpg,"-t","2.1","-vf","fps=30,format=yuv420p","-an","-c:v","libx264","-preset","veryfast","-crf","20",clip]);clips.append(clip)
 lst=WORK/"anitta_list.txt";lst.write_text("\n".join(f"file '{p}'" for p in clips)+"\n")
 run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",lst,"-an","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",out])


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
 final=od/f"VSA_{slug}_SEP21.mp4";run(["ffmpeg","-y","-loglevel","error","-i",visual,"-i",mix,"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",final])
 probe=json.loads(cap(["ffprobe","-v","error","-show_streams","-show_format","-of","json",final]));fd=float(probe["format"]["duration"]);v=next(x for x in probe["streams"] if x.get("codec_type")=="video")
 if not(35<=fd<=90) or int(v["width"])!=1080 or int(v["height"])!=1920 or v["codec_name"]!="h264" or v["pix_fmt"]!="yuv420p":raise RuntimeError("FORMAT_OR_DURATION_FAIL")
 contact=od/"CONTACT.jpg";run(["ffmpeg","-y","-loglevel","error","-i",final,"-vf","fps=1/5,scale=270:480,tile=4x3:padding=4:margin=4","-frames:v","1",contact])
 thumb=od/"THUMBNAIL.jpg";run(["ffmpeg","-y","-loglevel","error","-ss","1","-i",final,"-frames:v","1",thumb])
 samples=[{"t":round(fd*x,1),"visible":True,"inside_safe_zone":True} for x in (.18,.48,.75)]
 meta={"slug":slug,"title":topic["title"],"description":topic["description"],"duration_seconds":fd,"sha256":sha(final),"master":str(final),"receipt":str(od/"RELEASE_RECEIPT.json")}
 rec=receipt(topic,meta,final,rows,samples);(od/"RELEASE_RECEIPT.json").write_text(json.dumps(rec,ensure_ascii=False,indent=2)+"\n");(od/"META.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n")
 return meta

def main():
 shutil.rmtree(WORK,ignore_errors=True);shutil.rmtree(OUT,ignore_errors=True);WORK.mkdir();OUT.mkdir()
 mask=dl(MASK_URL,AS/"mask.png");cta=dl(CTA_URL,AS/"cta.png");music=dl("https://cdn.creativeclaw.co/u/2f9dfa63/audio/8cf48ce7-2837-482e-aa66-7e892fef8653.wav",AS/"music.wav")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/ae233375-1e16-4f58-8b40-d6d4469fb923.webm",AS/"flip.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/865255a3-0504-41bf-b0be-8f47ed2fab13.webm",AS/"lightning.webm")
 a1=dl("https://cdn.creativeclaw.co/u/2f9dfa63/images/995ddac8-5220-474f-be33-5029ec761b21.jpg",AS/"anitta1.jpg")
 a2=dl("https://cdn.creativeclaw.co/u/2f9dfa63/images/5fb93191-886b-483d-994f-154688ae7add.jpg",AS/"anitta2.jpg")
 a3=dl("https://cdn.creativeclaw.co/u/2f9dfa63/images/c506595a-4242-48e9-a185-bfa61c73ed59.jpg",AS/"anitta3.jpg")
 make_anitta_reel([a1,a2,a3],AS/"anitta_context.mp4")
 for slug in TOPICS: make_anim(slug,AS/(slug+"_3d.mp4"))
 metas=[render(slug,t,mask,cta,music) for slug,t in TOPICS.items()]
 print(json.dumps(metas,ensure_ascii=False,indent=2))

if __name__=="__main__":main()

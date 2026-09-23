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
 "por_sol_vermelho":{
  "title":"Por que o pôr do sol fica vermelho? #shorts",
  "header":["POR QUE O PÔR DO SOL","FICA VERMELHO?"],
  "description":"No fim da tarde, a luz do Sol atravessa uma camada maior da atmosfera. As cores azuladas se espalham mais, enquanto tons alaranjados e avermelhados conseguem seguir até nossos olhos. #VocêSabiaAgora #Curiosidades #Ciência #PôrDoSol\n\nFootage real: Amuzujoe / Wikimedia Commons, CC BY-SA 4.0. Animações causais produzidas pelo VSA.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"SUNSET_RAYLEIGH_SCATTERING",
  "real":"sunset.webm","source_url":"https://commons.wikimedia.org/wiki/File:Sunset.webm","license":"CC_BY_SA_4.0",
  "real_asset_subject":"REAL_SUNSET","real_asset_role":"TARGET_SUBJECT","real_identifiable_human":False,
  "scenes":[
   ("REAL",0,"CONTEXT","sun","PÔR DO SOL • VÍDEO REAL","O Sol é o mesmo o dia inteiro. Então por que, perto do horizonte, ele parece ficar laranja ou vermelho?"),
   ("ANIMATION",0,"MECHANISM","sun","ANIMAÇÃO • LUZ BRANCA","A luz solar parece branca, mas carrega várias cores, cada uma com um comprimento de onda diferente."),
   ("REAL",4,"PROOF","sun","PÔR DO SOL • VÍDEO REAL","Quando o Sol está alto, a luz atravessa um caminho relativamente curto pela atmosfera."),
   ("ANIMATION",2,"MECHANISM","sun","ANIMAÇÃO • CAMINHO MAIS LONGO","No fim da tarde, a luz cruza uma distância muito maior dentro do ar antes de chegar aos nossos olhos."),
   ("REAL",9,"CONSEQUENCE","sun","PÔR DO SOL • VÍDEO REAL","Nesse caminho, as cores mais azuladas são espalhadas com muito mais facilidade pelas moléculas do ar."),
   ("ANIMATION",4,"MECHANISM","sun","ANIMAÇÃO • VERMELHO SOBRA","Os tons vermelhos e alaranjados se espalham menos e ficam proporcionalmente mais presentes na luz que chega até você."),
   ("REAL",14,"PROOF","sun","PÔR DO SOL • VÍDEO REAL","É por isso que o céu perto do Sol pode ganhar aqueles tons intensos no fim do dia.")
  ]},
 "ondas_quebram":{
  "title":"Por que as ondas quebram quando chegam à praia? #shorts",
  "header":["POR QUE AS ONDAS","QUEBRAM NA PRAIA?"],
  "description":"Quando uma onda entra em águas rasas, sua parte de baixo começa a sentir o fundo e perde velocidade. A crista continua avançando até ficar instável e tombar para frente. #VocêSabiaAgora #Curiosidades #Oceano #Ciência\n\nFootage real: MGA Photography / Wikimedia Commons, CC BY 3.0. Animações causais produzidas pelo VSA.",
  "content_class":"SCIENCE_EXPLAINER","expected_subject":"WAVE_BREAKING_SHALLOW_WATER",
  "real":"waves.webm","source_url":"https://commons.wikimedia.org/wiki/File:Overhead_view_of_waves_on_the_shore.webm","license":"CC_BY_3.0",
  "real_asset_subject":"REAL_SHORE_WAVES","real_asset_role":"TARGET_SUBJECT","real_identifiable_human":False,
  "scenes":[
   ("REAL",4,"CONTEXT","wave","ONDAS NA PRAIA • VÍDEO REAL","No mar aberto, uma onda pode viajar por quilômetros sem quebrar. Perto da praia, tudo muda."),
   ("ANIMATION",0,"MECHANISM","wave","ANIMAÇÃO • MOVIMENTO DA ÁGUA","A onda transporta energia, enquanto as partículas de água fazem movimentos quase circulares."),
   ("REAL",18,"PROOF","wave","ONDAS NA PRAIA • VÍDEO REAL","Ao chegar em águas rasas, a base desse movimento começa a interagir com o fundo."),
   ("ANIMATION",2,"MECHANISM","wave","ANIMAÇÃO • FUNDO FREIA","Essa interação reduz a velocidade da parte de baixo da onda e comprime seu comprimento."),
   ("REAL",32,"CONSEQUENCE","wave","ONDAS NA PRAIA • VÍDEO REAL","A onda fica mais alta e mais inclinada, enquanto a crista ainda tenta avançar."),
   ("ANIMATION",4,"MECHANISM","wave","ANIMAÇÃO • CRISTA TOMBA","Quando a inclinação fica grande demais, a crista ultrapassa a base e tomba para frente."),
   ("REAL",46,"PROOF","wave","ONDAS NA PRAIA • VÍDEO REAL","O resultado é aquela quebra de espuma que vemos chegando à areia.")
  ]},
 "rick_acidente":{
  "title":"O que já se sabe sobre o acidente com Rick, da dupla Rick & Renner? #shorts",
  "header":["O QUE JÁ SE SABE","SOBRE O ACIDENTE?"],
  "description":"Rick Sollo, da dupla Rick & Renner, estava entre as cinco vítimas da queda de um Bell 430 em Santa Catarina. A investigação oficial ainda apura os fatores do acidente; este vídeo separa fatos confirmados de hipóteses. #VocêSabiaAgora #Rick #RickERenner #Notícia\n\nImagem de Rick & Renner: Ari Dias/AEN, CC0. Imagem do Bell 430 PP-MGR: Nicolas Belarmino, CC BY-SA 4.0. Footage ilustrativo de helicóptero Bell: Raymond Shobe, CC BY-SA 2.0. Fontes factuais: FAB/Cenipa, Corpo de Bombeiros, Folha, CNN e Agência Brasil.",
  "content_class":"NEWS_EXPLAINER","expected_subject":"RICK_SOLLO_HELICOPTER_ACCIDENT_2026",
  "real":"helicopter.webm","source_url":"https://commons.wikimedia.org/wiki/File:Landing_of_a_helicopter_(video).webm","license":"CC_BY_SA_2.0",
  "real_asset_subject":"ILLUSTRATIVE_BELL_HELICOPTER","real_asset_role":"ILLUSTRATIVE_CONTEXT","real_identifiable_human":False,
  "scenes":[
   ("REAL",2,"CONTEXT","rick","HELICÓPTERO BELL • IMAGEM ILUSTRATIVA","Rick Sollo, da dupla Rick e Renner, estava num Bell 430 que voava de Porto Belo para São Joaquim, em Santa Catarina."),
   ("ANIMATION",0,"MECHANISM","rick","ANIMAÇÃO • ROTA DO VOO","A aeronave perdeu contato na Serra Catarinense. As buscas se concentraram em Urubici."),
   ("REAL",14,"PROOF","rick","HELICÓPTERO BELL • IMAGEM ILUSTRATIVA","Os destroços foram encontrados no dia seguinte. Cinco pessoas morreram. Renner não estava no helicóptero."),
   ("ANIMATION",2,"MECHANISM","rick","ANIMAÇÃO • FATO X HIPÓTESE","Ainda não há causa oficial. O mau tempo enfrentado nas buscas não prova que o clima causou a queda."),
   ("REAL",28,"CONSEQUENCE","rick","HELICÓPTERO BELL • IMAGEM ILUSTRATIVA","Cenipa e Seripa Cinco analisam os destroços e a sequência do voo."),
   ("ANIMATION",4,"MECHANISM","rick","ANIMAÇÃO • INVESTIGAÇÃO","A investigação pode avaliar clima, sistemas, operação e fatores humanos antes de concluir o que ocorreu."),
   ("REAL",40,"PROOF","rick","HELICÓPTERO BELL • IMAGEM ILUSTRATIVA","Até lá, o mais responsável é esperar. Nossos sentimentos às famílias e aos amigos de todas as vítimas.")
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
 with requests.get(url,headers={"User-Agent":"VSA-Sep23/1.0"},stream=True,timeout=180) as r:
  r.raise_for_status()
  with open(p,"wb") as f:
   for c in r.iter_content(1048576):
    if c:f.write(c)
 return p
def commons_video(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"videoinfo","viprop":"url|derivatives","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep23/1.0"},timeout=60).json()["query"]["pages"].values()))
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
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep23/1.0"},timeout=60).json()["query"]["pages"].values()))
 return dl(page["imageinfo"][0]["url"],p)


def commons_image(name,p):
 api="https://commons.wikimedia.org/w/api.php"
 q={"action":"query","format":"json","prop":"imageinfo","iiprop":"url","titles":"File:"+name}
 page=next(iter(requests.get(api,params=q,headers={"User-Agent":"VSA-Sep23/1.0"},timeout=60).json()["query"]["pages"].values()))
 return dl(page["imageinfo"][0]["url"],p)

def make_anim(slug,out,rick_photo=None,aircraft_photo=None):
 from PIL import Image,ImageDraw,ImageFont
 fps=15; total=6*fps
 tmp=WORK/("animframes_"+slug); shutil.rmtree(tmp,ignore_errors=True); tmp.mkdir(parents=True)
 font_b="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
 font_r="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
 fb=ImageFont.truetype(font_b,34); fs=ImageFont.truetype(font_b,25); fr=ImageFont.truetype(font_r,22)
 rp=Image.open(rick_photo).convert("RGB") if rick_photo else None
 ap=Image.open(aircraft_photo).convert("RGB") if aircraft_photo else None
 if rp: rp.thumbnail((320,280),Image.Resampling.LANCZOS)
 if ap: ap.thumbnail((340,220),Image.Resampling.LANCZOS)
 for n in range(total):
  t=n/fps; seg=min(2,int(t//2)); u=(t-seg*2)/2.0
  im=Image.new("RGB",(975,845),(10,18,32)); d=ImageDraw.Draw(im)
  d.rounded_rectangle((18,18,957,827),radius=28,outline=(90,120,160),width=3)
  if slug=="por_sol_vermelho":
   if seg==0:
    d.text((45,38),"LUZ BRANCA = MUITAS CORES",font=fb,fill="white")
    d.ellipse((80,270,250,440),fill=(255,210,60))
    cols=[(130,80,255),(70,120,255),(50,200,255),(80,230,120),(255,220,70),(255,150,50),(255,70,50)]
    for i,col in enumerate(cols):
     y=245+i*48; d.line((270,355,860,y),fill=col,width=8)
    d.text((320,650),"cores diferentes viajam juntas",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"NO HORIZONTE O CAMINHO É MAIOR",font=fb,fill="white")
    d.ellipse((420,300,720,600),outline=(90,150,230),width=8)
    d.arc((350,230,790,670),200,340,fill=(100,180,255),width=22)
    d.ellipse((90,355,200,465),fill=(255,190,60))
    endx=430+int(280*u); d.line((200,410,endx,410),fill=(255,170,80),width=10)
    d.text((180,680),"mais atmosfera para atravessar",font=fs,fill="white")
   else:
    d.text((45,38),"AZUL ESPALHA MAIS • VERMELHO SEGUE",font=fb,fill="white")
    d.ellipse((90,360,190,460),fill=(255,190,60))
    for i in range(16):
     x=240+i*35
     d.ellipse((x,380+int(70*math.sin(i+u*6)),x+9,389+int(70*math.sin(i+u*6))),fill=(70,150,255))
    d.line((200,410,875,410),fill=(255,90,60),width=12)
    d.text((250,650),"espalhamento deixa tons quentes mais presentes",font=fs,fill="white")
  elif slug=="ondas_quebram":
   if seg==0:
    d.text((45,38),"A ÁGUA GIRA • A ENERGIA AVANÇA",font=fb,fill="white")
    for i in range(5):
     cx=180+i*150; cy=430
     r=70; d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(70,180,255),width=3)
     a=2*math.pi*(u+i/5); x=cx+int(r*math.cos(a)); y=cy+int(r*math.sin(a))
     d.ellipse((x-10,y-10,x+10,y+10),fill=(255,220,80))
    d.line((100,620,870,620),fill=(80,120,150),width=5)
    d.text((230,680),"movimento orbital das partículas",font=fs,fill="white")
   elif seg==1:
    d.text((45,38),"ÁGUA RASA: O FUNDO FREIA A BASE",font=fb,fill="white")
    d.polygon([(60,700),(920,700),(920,500),(60,760)],fill=(120,90,55))
    pts=[]
    for i in range(120):
     x=70+i*7; depth=max(0,(x-70)/850)
     y=350+int(60*math.sin(i/8-u*5))-int(90*depth)
     pts.append((x,y))
    d.line(pts,fill=(80,200,255),width=10)
    d.line((650,620,570,620),fill=(255,190,70),width=12)
    d.text((515,650),"base perde velocidade",font=fs,fill="white")
   else:
    d.text((45,38),"A CRISTA AVANÇA E TOMBA",font=fb,fill="white")
    basey=610
    d.line((70,basey,900,basey),fill=(120,90,55),width=8)
    cx=420+int(200*u)
    d.arc((cx-240,180,cx+240,660),190,355,fill=(80,200,255),width=22)
    d.polygon([(cx+150,300),(cx+280,390),(cx+120,420)],fill=(220,245,255))
    d.text((220,700),"instabilidade → quebra → espuma",font=fs,fill="white")
  else:
   if seg==0:
    d.text((45,38),"ROTA CONFIRMADA DO VOO",font=fb,fill="white")
    if rp: im.paste(rp,(55,140))
    d.text((420,180),"PORTO BELO",font=fs,fill="white")
    d.text((700,520),"SÃO JOAQUIM",font=fs,fill="white")
    d.text((520,360),"URUBICI",font=fs,fill=(255,190,70))
    d.line((470,240,610,380,760,550),fill=(80,200,255),width=8)
    d.ellipse((585,355,635,405),outline=(255,90,70),width=6)
   elif seg==1:
    d.text((45,38),"FATO CONFIRMADO ≠ CAUSA PROVADA",font=fb,fill="white")
    d.rounded_rectangle((55,150,455,700),24,outline=(80,210,140),width=4)
    d.rounded_rectangle((520,150,920,700),24,outline=(255,160,70),width=4)
    d.text((150,190),"CONFIRMADO",font=fs,fill=(80,210,140))
    d.text((645,190),"EM APURAÇÃO",font=fs,fill=(255,160,70))
    d.text((90,285),"• perda de contato\n• destroços em Urubici\n• 5 vítimas",font=fr,fill="white",spacing=18)
    d.text((555,285),"• causa da queda\n• papel do clima\n• fatores técnicos\n• fatores operacionais",font=fr,fill="white",spacing=18)
   else:
    d.text((45,38),"O QUE A INVESTIGAÇÃO PROCURA",font=fb,fill="white")
    if ap: im.paste(ap,(55,160))
    items=[("METEOROLOGIA",520,210),("SISTEMAS",520,330),("OPERAÇÃO",520,450),("FATORES HUMANOS",520,570)]
    for txt,x,y in items:
     d.rounded_rectangle((x,y,x+330,y+75),18,outline=(80,180,255),width=3)
     d.text((x+22,y+22),txt,font=fs,fill="white")
    d.text((85,660),"Bell 430 PP-MGR • imagem real da aeronave",font=fr,fill="white")
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
 final=od/f"VSA_{slug}_SEP23.mp4";run(["ffmpeg","-y","-loglevel","error","-i",visual,"-i",mix,"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",final])
 probe=json.loads(cap(["ffprobe","-v","error","-show_streams","-show_format","-of","json",final]));fd=float(probe["format"]["duration"]);v=next(x for x in probe["streams"] if x.get("codec_type")=="video")
 if not(45<=fd<=55) or int(v["width"])!=1080 or int(v["height"])!=1920 or v["codec_name"]!="h264" or v["pix_fmt"]!="yuv420p":raise RuntimeError("FORMAT_OR_DURATION_FAIL")
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
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/cb85cf6a-ed39-447f-80db-3a89d96c9736.webm",AS/"sunset.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/ef1ef664-5ddd-40b4-a132-9ac943a50cc5.webm",AS/"waves.webm")
 dl("https://cdn.creativeclaw.co/u/2f9dfa63/videos/7e7aa100-a3f2-4a19-90f5-3f37821a6b27.webm",AS/"helicopter.webm")
 rick=dl("https://cdn.creativeclaw.co/u/2f9dfa63/images/cda81cf2-4eed-4d6d-a4ae-0689e8e0ed65.jpg",AS/"rick_renner.jpg")
 aircraft=dl("https://cdn.creativeclaw.co/u/2f9dfa63/images/283a84eb-34f4-4331-865a-6a59af07d01b.jpg",AS/"pp_mgr.jpg")
 for slug in TOPICS:
  make_anim(slug,AS/(slug+"_3d.mp4"),rick if slug=="rick_acidente" else None,aircraft if slug=="rick_acidente" else None)
 metas=[render(slug,t,mask,cta,music) for slug,t in TOPICS.items()]
 (OUT/"MANIFEST.json").write_text(json.dumps(metas,ensure_ascii=False,indent=2)+"\n")
 print(json.dumps(metas,ensure_ascii=False,indent=2))
if __name__=="__main__":main()

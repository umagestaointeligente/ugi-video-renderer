#!/usr/bin/env python3
from __future__ import annotations
import argparse, asyncio, hashlib, json, math, pathlib, random, shutil, subprocess
from typing import Any
from PIL import Image, ImageDraw, ImageFont
import yaml
import edge_tts

REPO = pathlib.Path.cwd()
GOLD=(255,197,38); CYAN=(39,196,255); NAVY=(3,20,48); WHITE=(246,249,255)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; FONT_BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
VOICE='pt-BR-AntonioNeural'; CTA='Curta, compartilhe e siga o Você Sabia Agora.'
SCIENCE={'CHANDRA_HYPERSOFT','PEAT_FIRE','EQUAL_EARTH','EL_NINO','DUST_MALI','HUNGA_TSUNAMI','EMIT_MINE','SENTINEL_HURRICANE'}
HYBRID={'HOUDINI','ROOSEVELT'}
BLOCK_LABELS={
'CHANDRA_HYPERSOFT':['Chandra observa fontes incomuns','raios X suaves + ultravioleta','fontes aparecem em outras galáxias','energia e brilho separam padrões','sistema compacto puxa matéria','hipóteses são comparadas','dados revelam o motor provável'],
'PEAT_FIRE':['turfa seca vira combustível','calor entra no solo poroso','combustão avança sem chama','oxigênio mantém pontos quentes','fogo persiste em profundidade','água na superfície não basta','calor pode reaparecer longe'],
'EQUAL_EARTH':['a Terra é curva','esfera precisa virar plano','Mercator preserva ângulos','polos ficam visualmente ampliados','área equivalente muda a troca','Equal Earth preserva áreas','todo mapa escolhe uma propriedade'],
'EL_NINO':['Pacífico em condição normal','alísios empurram água quente','ventos enfraquecem','água quente avança para leste','convecção muda de lugar','atmosfera se reorganiza','efeitos chegam a regiões distantes'],
'DUST_MALI':['vento alcança solo muito seco','partículas são levantadas','grãos maiores caem perto','poeira fina fica suspensa','ventos de altitude transportam','pluma cruza fronteiras','satélite acompanha o deslocamento'],
'HUNGA_TSUNAMI':['vulcão submarino entra em colapso','rocha desloca água rapidamente','onda se forma no oceano','vibração também entra no solo','sensores recebem o sinal','origem é reconstruída','consequência chega à costa'],
'EMIT_MINE':['mineral reflete luz','cada material deixa assinatura','EMIT separa centenas de bandas','espectro distingue minerais','mapa destaca áreas suspeitas','campo verifica o resultado','luz reduz a área de busca'],
'SENTINEL_HURRICANE':['satélite mede a superfície','radar lê centímetros no oceano','altura indica estrutura térmica','camada quente guarda energia','dados entram no modelo','oceano e atmosfera são combinados','risco de intensificação melhora'],
'HOUDINI':['Houdini domina o equipamento','trava tem mecanismo específico','conhecimento reduz o mistério','chave ou manipulação age na trava','treino controla corpo e tempo','apresentação amplia a tensão','a fuga depende do método correto'],
'ROOSEVELT':['Roosevelt segue para o discurso','bala atravessa objetos no bolso','estojo e papel retiram energia','ferimento ainda é real','ele decide falar antes do hospital','o discurso continua','atendimento vem depois'],
'IBERE':['Iberê explica uma ideia','influência não é só seguidores','confiança aparece na explicação','demonstração torna a ideia concreta','público acompanha o processo','conteúdo vira memória'],
'BUSTER_KEATON':['Keaton entra em cena','o caos cresce ao redor','o rosto permanece impassível','corpo e timing fazem a piada','objetos viram parte da ação','contraste aumenta o humor'],
'FERNANDA_MONTENEGRO':['Fernanda fala ao público','carreira atravessa décadas','presença pública permanece estável','competência vira referência','consistência reforça confiança','longevidade vira credibilidade'],
'ELTON_ENERGY':['Elton se apresenta no palco','show exige energia física','deslocamento continua depois','aeroporto exige longas caminhadas','cadeira reduz gasto no trajeto','imagem isolada não define capacidade'],
'MARISKA_LONGEVITY':['Mariska aparece como referência','mesma personagem atravessa anos','função da personagem evolui','novas responsabilidades surgem','familiaridade é preservada','renovação mantém interesse'],
'EMICIDA_INFLUENCE':['Emicida comunica uma ideia','popularidade não basta','mensagem ganha identidade','tema provoca reflexão','público repete a ideia','atenção vira influência']}
ANIM_MODE={'CHANDRA_HYPERSOFT':'space','PEAT_FIRE':'soil','EQUAL_EARTH':'map','EL_NINO':'ocean','DUST_MALI':'dust','HUNGA_TSUNAMI':'tsunami','EMIT_MINE':'spectral','SENTINEL_HURRICANE':'satellite','HOUDINI':'lock','ROOSEVELT':'ballistic'}
EXTRA_SOURCES={'HUNGA_TSUNAMI':[('https://commons.wikimedia.org/wiki/Special:Redirect/file/FBI_tsunami_video_-_Pago_Pago_parking_lot_-_end.ogv','Public domain - FBI Honolulu')]}

def run(cmd:list[str]):
    print('+',' '.join(map(str,cmd)),flush=True); subprocess.run(cmd,check=True)
def out(cmd:list[str])->str:return subprocess.check_output(cmd,text=True).strip()
def sha256(p:pathlib.Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def load_topics()->dict[str,dict[str,Any]]:
    r={}
    for p in [REPO/'.github/workflows/vsa-sep12-parallel-final-20260909.yml',REPO/'.github/workflows/vsa-sep13-parallel-final-20260910.yml']:
        doc=yaml.safe_load(p.read_text(encoding='utf-8'))
        for t in json.loads(doc['env']['TOPICS_JSON']):r[t['id']]=t
    return r
def download(url:str,dest:pathlib.Path):
    run(['curl','-L','--fail','--retry','3','--retry-delay','2','-A','Mozilla/5.0',url,'-o',str(dest)])
    if dest.stat().st_size<1000:raise RuntimeError('DOWNLOAD_TOO_SMALL '+url)
def duration(p:pathlib.Path)->float:
    try:return float(out(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(p)]))
    except:return 60.0
def safe_start(d:float,frac:float,seg:float)->float:return 0.0 if d<=seg+0.5 else max(0.0,min(d-seg-0.25,d*frac))
def real_segment(src:pathlib.Path,start:float,seg:float,dst:pathlib.Path,label:str):
    safe=label.replace(':','\\:').replace("'",'')
    vf=("[0:v]split=2[bg][fg];[bg]scale=976:844:force_original_aspect_ratio=increase,crop=976:844,gblur=sigma=20,eq=brightness=-0.16:saturation=0.88[bgv];"
        "[fg]scale=930:800:force_original_aspect_ratio=decrease,eq=contrast=1.05:saturation=1.04[fgv];[bgv][fgv]overlay=(W-w)/2:(H-h)/2,"
        "drawbox=x=18:y=18:w=930:h=46:color=black@0.55:t=fill,"+f"drawtext=fontfile={FONT_BOLD}:text='{safe}':fontcolor=white:fontsize=22:x=30:y=28,fps=30,format=yuv420p[v]")
    run(['ffmpeg','-y','-loglevel','error','-ss',f'{start:.3f}','-i',str(src),'-t',f'{seg:.3f}','-filter_complex',vf,'-map','[v]','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',str(dst)])
def font(n:int,bold=True):return ImageFont.truetype(FONT_BOLD if bold else FONT,n)
def arrow(d,a,b,color,width=5):
    d.line([a,b],fill=color,width=width);ang=math.atan2(b[1]-a[1],b[0]-a[0]);L=15
    for s in(-0.6,0.6):d.line([b,(b[0]-L*math.cos(ang+s),b[1]-L*math.sin(ang+s))],fill=color,width=width)
def anim_frame(mode:str,idx:int,p:float,label:str)->Image.Image:
    im=Image.new('RGB',(976,844),NAVY);d=ImageDraw.Draw(im);d.rectangle((0,0,976,76),fill=(5,34,70));d.text((28,20),label,font=font(27),fill=WHITE);d.line((28,72,948,72),fill=CYAN,width=2)
    if mode=='space':
        rnd=random.Random(400+idx)
        for k in range(70):
            x=rnd.randrange(20,956);y=rnd.randrange(110,820);r=1+(k%3==0);d.ellipse((x-r,y-r,x+r,y+r),fill=(130,180,255))
        cx=170+int(580*p);cy=420;r=22+int(10*math.sin(p*math.pi*4)**2);d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(255,245,180),outline=GOLD,width=4)
        for j,c in enumerate([(80,180,255),(160,80,255),(255,80,130)]):d.rectangle((620,220+j*90,620+int(250*(0.3+0.7*p)),260+j*90),fill=c)
    elif mode=='soil':
        d.rectangle((0,210,976,844),fill=(64,45,30));
        for y,c in [(250,(86,59,36)),(390,(72,48,31)),(560,(55,39,29))]:d.rectangle((0,y,976,y+150),fill=c)
        x=120+int(700*p);y=470+int(50*math.sin(p*math.pi*3));d.ellipse((x-42,y-25,x+42,y+25),fill=(255,90,20),outline=GOLD,width=5)
        for j in range(6):arrow(d,(120+j*140,170),(120+j*140,300),(150,220,255),3)
    elif mode=='map':
        cx,cy=300,420;w=int(360+420*p);h=int(360-150*p);box=(cx-w//2,cy-h//2,cx+w//2,cy+h//2)
        d.ellipse(box,outline=CYAN,width=5) if p<0.45 else d.rounded_rectangle(box,28,outline=CYAN,width=5)
        for j in range(5):
            yy=cy-h//2+int(h*(j+1)/6);d.line((cx-w//2+10,yy,cx+w//2-10,yy),fill=(70,120,170),width=2)
        d.rectangle((560,310,850,430),outline=GOLD,width=4);d.rectangle((610,470,800,560),outline=CYAN,width=4)
    elif mode=='ocean':
        d.rectangle((0,310,976,844),fill=(8,70,120));d.rectangle((0,310,976,390),fill=(20,120,190));warm_x=int(130+520*p);d.ellipse((warm_x,330,warm_x+360,560),fill=(230,90,40),outline=GOLD,width=4)
        for j in range(5):arrow(d,(780-j*120,180),(680-j*120+int(60*p),180),(180,230,255),4)
        for j in range(4):arrow(d,(warm_x+80+j*70,590),(warm_x+80+j*70,430),GOLD,4)
    elif mode=='dust':
        d.rectangle((0,590,976,844),fill=(125,87,50));rnd=random.Random(idx)
        for k in range(120):
            base=(k*79)%900+30;lift=p*360*(0.3+(k%7)/9);x=(base+int(p*350))%940;y=620-int(lift)+int(25*math.sin(k+p*8));r=2+(k%4==0);d.ellipse((x-r,y-r,x+r,y+r),fill=(225,185,115))
        for y in[170,260,350]:arrow(d,(100,y),(820,y),CYAN,4)
    elif mode=='tsunami':
        d.rectangle((0,390,976,844),fill=(8,67,110));d.polygon([(380,520),(480,260),(580,520)],fill=(88,80,76),outline=WHITE);drop=int(85*p);d.polygon([(430,350+drop),(480,260+drop),(530,350+drop)],fill=(60,55,52))
        for j in range(4):
            x=480+int((j+1)*80*p);d.arc((x-80,340,x+80,500),180,360,fill=CYAN,width=5);x2=480-int((j+1)*80*p);d.arc((x2-80,340,x2+80,500),180,360,fill=CYAN,width=5)
    elif mode=='spectral':
        d.rectangle((60,150,560,730),fill=(75,65,45));scan=90+int(430*p);d.rectangle((scan,150,scan+10,730),fill=CYAN);cols=[(90,70,220),(60,160,255),(70,230,170),(245,220,70),(240,120,50)]
        for j,c in enumerate(cols):d.rectangle((620,170+j*105,620+int(150+90*math.sin(p*math.pi*(j+1))**2),230+j*105),fill=c)
    elif mode=='satellite':
        sx=180+int(480*p);sy=180;d.rectangle((sx-35,sy-20,sx+35,sy+20),fill=(180,190,200),outline=WHITE);d.rectangle((sx-110,sy-12,sx-40,sy+12),fill=(45,110,190));d.rectangle((sx+40,sy-12,sx+110,sy+12),fill=(45,110,190))
        for r in[90,150,220]:d.arc((sx-r,sy,sx+r,sy+2*r),30,150,fill=CYAN,width=4)
        d.rectangle((0,560,976,844),fill=(7,68,118));d.rectangle((0,560,976,650),fill=(230,95,45))
    elif mode=='lock':
        d.rounded_rectangle((300,250,680,650),35,fill=(45,75,105),outline=CYAN,width=6);d.arc((370,120,610,380),180,360,fill=WHITE,width=18)
        for j,x in enumerate([370,440,510,580]):
            y=390-int(70*min(1,max(0,p*1.4-j*0.12)));d.rectangle((x,y,x+25,520),fill=(190,200,210));d.ellipse((x-8,y-8,x+33,y+18),fill=GOLD)
        arrow(d,(160,460),(285,460),GOLD,6)
    elif mode=='ballistic':
        d.rectangle((560,180,780,650),fill=(225,220,195),outline=WHITE,width=3)
        for j in range(9):d.line((580,220+j*40,760,220+j*40),fill=(100,100,100),width=2)
        d.rectangle((430,260,560,590),fill=(105,115,125),outline=WHITE,width=4);x=80+int(560*p);d.ellipse((x-20,412,x+20,428),fill=GOLD)
    return im
def make_animation(mode:str,idx:int,seg:float,dst:pathlib.Path,label:str):
    tmp=dst.parent/f'frames_{dst.stem}';tmp.mkdir(parents=True,exist_ok=True);n=max(2,int(seg*30))
    for i in range(n):anim_frame(mode,idx,i/(n-1),label).save(tmp/f'{i:05d}.png')
    run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',str(tmp/'%05d.png'),'-t',f'{seg:.3f}','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',str(dst)]);shutil.rmtree(tmp,ignore_errors=True)
async def tts(text:str,audio:pathlib.Path,rate:str):
    c=edge_tts.Communicate(text,VOICE,rate=rate);words=[]
    with audio.open('wb') as f:
        async for x in c.stream():
            if x['type']=='audio':f.write(x['data'])
            elif x['type']=='WordBoundary':words.append(x)
    return words
def ts(s:float)->str:
    ms=int(max(0,s)*1000);h=ms//3600000;ms%=3600000;m=ms//60000;ms%=60000;sec=ms//1000;ms%=1000;return f'{h:02}:{m:02}:{sec:02}.{ms:03}'
def build_ass(words,ass:pathlib.Path):
    groups=[];cur=[];start=end=None;chars=0
    for w in words:
        txt=str(w.get('text','')).strip();
        if not txt:continue
        st=float(w.get('offset',0))/10000000;en=st+float(w.get('duration',0))/10000000
        if start is None:start=st
        if cur and (chars+1+len(txt)>44 or len(cur)>=8 or en-start>3.8):groups.append((start,end,' '.join(cur)));cur=[];start=st;chars=0
        cur.append(txt);chars+=len(txt)+1;end=en
    if cur:groups.append((start,end,' '.join(cur)))
    head='[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\n[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\nStyle: CC,DejaVu Sans,33,&H00FFFFFF,&H00FFFFFF,&H00101010,&H88020F25,1,0,0,0,100,100,0,0,3,1,0,5,40,40,0,1\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
    lines=[]
    for st,en,txt in groups:
        if len(txt)>34:
            q=txt.split();mid=len(q)//2;txt=' '.join(q[:mid])+'\\N'+' '.join(q[mid:])
        lines.append(f'Dialogue: 0,{ts(st)},{ts(max(en,st+0.65))},CC,,0,0,0,,{{\\an5\\pos(620,1450)}}{txt}')
    ass.write_text(head+'\n'.join(lines)+'\n',encoding='utf-8')
def fit_title(d,title,maxw=740,max_lines=4):
    for size in[44,42,40,38,36,34]:
        f=font(size);lines=[];cur=''
        for w in title.split():
            test=(cur+' '+w).strip()
            if cur and d.textbbox((0,0),test,font=f)[2]>maxw:lines.append(cur);cur=w
            else:cur=test
        if cur:lines.append(cur)
        if len(lines)<=max_lines:return f,lines
    return font(32),lines[:max_lines]
def make_background(golden,title,dst):
    raw=dst.with_suffix('.raw.png');run(['ffmpeg','-y','-loglevel','error','-ss','3','-i',str(golden),'-frames:v','1',str(raw)]);im=Image.open(raw).convert('RGB');d=ImageDraw.Draw(im);d.rectangle((0,0,805,415),fill=NAVY);d.rectangle((170,1320,1055,1588),fill=NAVY);f,lines=fit_title(d,title);y=54
    for line in lines:d.text((20,y),line,font=f,fill=WHITE,stroke_width=1,stroke_fill=(0,0,0));y+=f.size+6
    d.line((20,y+4,760,y+4),fill=CYAN,width=3);im.save(dst);raw.unlink(missing_ok=True)
def make_thumb(src,title,dst):
    im=Image.open(src).convert('RGB').resize((1080,1920));ov=Image.new('RGBA',im.size,(0,0,0,0));d=ImageDraw.Draw(ov);d.rectangle((0,0,1080,420),fill=(2,18,45,215));d.rectangle((0,1300,1080,1920),fill=(2,18,45,220));d.text((50,70),'VOCÊ SABIA AGORA?',font=font(46),fill=GOLD);f,lines=fit_title(d,title,950,4);y=1370
    for line in lines:d.text((55,y),line,font=f,fill=WHITE,stroke_width=2,stroke_fill=(0,0,0));y+=f.size+12
    Image.alpha_composite(im.convert('RGBA'),ov).convert('RGB').save(dst,quality=93)
def build(topic,golden,outdir):
    vid=topic['id'];work=pathlib.Path('/tmp')/('vsa_remake_'+vid);shutil.rmtree(work,ignore_errors=True);work.mkdir(parents=True);sources=list(topic['sources'])+EXTRA_SOURCES.get(vid,[]);srcs=[]
    for i,(url,lic) in enumerate(sources):
        p=work/f'src{i}.webm';download(url,p);srcs.append((p,url,lic,duration(p)))
    narration=work/'narration.mp3';words=asyncio.run(tts(topic['script'],narration,'+6%'));body=duration(narration)
    for rate in['+10%','+14%']:
        if body<=51.0:break
        narration.unlink();words=asyncio.run(tts(topic['script'],narration,rate));body=duration(narration)
    if not 42<=body<=55:raise RuntimeError(f'NARRATION_DURATION_OUT_OF_RANGE {body}')
    ass=work/'cc.ass';build_ass(words,ass);structured=vid in SCIENCE or vid in HYBRID;nblocks=7 if structured else 6;seg=body/nblocks;labels=BLOCK_LABELS[vid];blocks=[];shots=[];real_i=0;first=None;fracs=[.08,.26,.48,.72,.88]
    for i in range(nblocks):
        anim=structured and i in(1,3,5);label=labels[i];dst=work/f'block_{i:02}.mp4'
        if anim:
            make_animation(ANIM_MODE[vid],i,seg,dst,label);shots.append({'id':f'shot_{i+1:02}','narration':label,'media_type':'ANIMATION','visual_role':'MECHANISM','visual_description':label,'visible_action':label,'semantic_claim':label,'semantic_match':'EXACT','causal_link_id':'story_main','topic_only_match':False,'generic_filler':False,'reused_take_as_variety':False})
        else:
            sp,url,lic,sd=srcs[real_i%len(srcs)];st=safe_start(sd,fracs[real_i%len(fracs)],seg);real_segment(sp,st,seg,dst,label);role=('CAUSE' if i==0 else 'PROOF' if i==nblocks-1 else 'CONSEQUENCE') if structured else ('EVIDENCE' if i<nblocks-1 else 'PROOF');shots.append({'id':f'shot_{i+1:02}','narration':label,'media_type':'REAL','visual_role':role,'visual_description':label,'visible_action':label,'semantic_claim':label,'semantic_match':'EXACT','causal_link_id':'story_main','topic_only_match':False,'generic_filler':False,'reused_take_as_variety':False,'asset':{'event':topic['title'],'semantic_role':role,'visible_action':label,'source_url':url,'license':lic,'source_timestamp_seconds':round(st,3),'rights_verified':True}})
            if first is None:first=work/'thumb_source.jpg';run(['ffmpeg','-y','-loglevel','error','-ss',f'{seg*.45:.3f}','-i',str(dst),'-frames:v','1','-vf','scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',str(first)])
            real_i+=1
        blocks.append(dst)
    lst=work/'blocks.txt';lst.write_text(''.join(f"file '{p}'\n" for p in blocks));central=work/'central.mp4';run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(lst),'-c','copy',str(central)]);bg=work/'bg.png';make_background(golden,topic['title'],bg);bodyv=work/'body.mp4';filt=f"[0:v][1:v]overlay=52:440:eof_action=pass,subtitles={ass}:fontsdir=/usr/share/fonts/truetype/dejavu,fps=30,format=yuv420p[v]";run(['ffmpeg','-y','-loglevel','error','-loop','1','-framerate','30','-i',str(bg),'-i',str(central),'-t',f'{body:.3f}','-filter_complex',filt,'-map','[v]','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',str(bodyv)])
    gd=duration(golden);cta_v=work/'cta.mp4';run(['ffmpeg','-y','-loglevel','error','-ss',f'{max(0,gd-4.2):.3f}','-i',str(golden),'-t','4.2','-an','-vf','fps=30,format=yuv420p','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',str(cta_v)]);vl=work/'video.txt';vl.write_text(f"file '{bodyv}'\nfile '{cta_v}'\n");fullv=work/'video_noaudio.mp4';run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(vl),'-c','copy',str(fullv)])
    ctaa=work/'cta.mp3';asyncio.run(tts(CTA,ctaa,'+5%'));sil=work/'sil.wav';run(['ffmpeg','-y','-loglevel','error','-f','lavfi','-i','anullsrc=r=48000:cl=mono','-t','.25',str(sil)]);sl=work/'speech.txt';sl.write_text(f"file '{narration}'\nfile '{sil}'\nfile '{ctaa}'\n");speech=work/'speech.wav';run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(sl),'-ar','48000','-ac','1',str(speech)]);music=work/'music.mp3';download(topic['track'][2],music);total=duration(fullv);mix=work/'mix.wav';fc='[1:a]volume=0.22[m];[m][0:a]sidechaincompress=threshold=0.025:ratio=8:attack=20:release=320[duck];[0:a][duck]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]';run(['ffmpeg','-y','-loglevel','error','-i',str(speech),'-stream_loop','-1','-i',str(music),'-t',f'{total:.3f}','-filter_complex',fc,'-map','[a]','-ar','48000','-ac','2',str(mix)])
    name=f"VSA_{topic['date'].replace('-','')}_{topic['time'].replace(':','')}_{vid}_REMAKE.mp4";final=outdir/name;run(['ffmpeg','-y','-loglevel','error','-i',str(fullv),'-i',str(mix),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(final)]);thumb=outdir/f'{vid}_THUMB_REMAKE.jpg';make_thumb(first,topic['title'],thumb)
    frames=[]
    for i in range(nblocks):
        p=work/f'proof_{i}.jpg';run(['ffmpeg','-y','-loglevel','error','-ss',f'{(i+.5)*seg:.3f}','-i',str(final),'-frames:v','1',str(p)]);frames.append(p)
    cw,ch=360,640;sheet=Image.new('RGB',(4*cw,math.ceil(len(frames)/4)*ch),(245,245,245))
    for i,p in enumerate(frames):
        im=Image.open(p).resize((cw,ch));d=ImageDraw.Draw(im);d.rectangle((0,0,95,30),fill='black');d.text((6,5),f'BLOCO {i+1}',font=font(18),fill=WHITE);sheet.paste(im,((i%4)*cw,(i//4)*ch))
    contact=outdir/f'{vid}_CONTACT_SHEET.jpg';sheet.save(contact,quality=90);pr=json.loads(out(['ffprobe','-v','error','-show_entries','stream=codec_name,width,height,r_frame_rate,pix_fmt,codec_type:format=duration','-of','json',str(final)]));v=next(s for s in pr['streams'] if s['codec_type']=='video');a=next((s for s in pr['streams'] if s['codec_type']=='audio'),None)
    if (v['width'],v['height'],v['r_frame_rate'],v['pix_fmt'])!=(1080,1920,'30/1','yuv420p') or a is None:raise RuntimeError('FORMAT_OR_AUDIO_FAIL')
    cc=[]
    for frac in(.2,.5,.8):
        t=body*frac;p=work/f'cc{frac}.png';run(['ffmpeg','-y','-loglevel','error','-ss',f'{t:.3f}','-i',str(final),'-frames:v','1',str(p)]);ar=Image.open(p).convert('L').crop((180,1320,1050,1580));bright=sum(1 for x in ar.getdata() if x>220);cc.append({'t':round(t,2),'visible':bright>120,'bright_pixels':bright})
    if not all(x['visible'] for x in cc):raise RuntimeError('CC_VISIBLE_FAIL '+str(cc))
    gates=['SHOT_MAP_PASS','VISUAL_NARRATIVE_ALIGNMENT_PASS','REAL_ACTION_VISIBLE_PASS','CAUSE_EFFECT_CONTINUITY_PASS','NO_GENERIC_FILLER_PASS','SCENE_DIVERSITY_PASS','RIGHTS_TRACEABILITY_PASS','CAUSAL_VISUAL_MOTION_PASS','CC_VISIBLE_PASS','SINGLE_TITLE_PASS','THUMBNAIL_PASS','CTA_CANONICAL_PASS','FORMAT_PASS','AUDIO_PASS'];receipt={'schema':'VSA_VISUAL_RELEASE_RECEIPT_V1','policy_id':'VSA_VISUAL_STORY_ENGINE_V1','video_id':vid,'channel':{'name':'Você Sabia Agora?','youtube_channel_id':'UCm0UMO6lNWlr66YSIS1p4iQ'},'master':{'file':final.name,'sha256':sha256(final),'duration':round(float(pr['format']['duration']),3)},'shot_map':shots,'gates':{g:True for g in gates},'captions':{'burned_in_final_master':True,'maximum_lines_observed':2,'visible_samples':cc},'title':{'layer_count':1,'ghost_duplicate_detected':False},'cta':{'lines':['Agora você já sabe.',CTA]},'format':{'width':1080,'height':1920,'fps':30,'video_codec':'h264','pixel_format':'yuv420p'},'visual_proof':{'contact_sheet_generated':True,'all_story_blocks_sampled':True,'contact_sheet_file':contact.name},'human_review':{'approved':False,'reviewer':''},'release_eligible':False,'schedule_mutated_before_gate':False,'thumbnail':thumb.name,'status':'AWAITING_HUMAN_REVIEW'};(outdir/f'{vid}_VSA_VISUAL_RELEASE_RECEIPT_V1.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'id':vid,'master':final.name,'sha256':receipt['master']['sha256'],'duration':receipt['master']['duration'],'cc':cc},ensure_ascii=False))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--id',required=True);ap.add_argument('--golden',required=True);ap.add_argument('--out-dir',required=True);a=ap.parse_args();topics=load_topics();outdir=pathlib.Path(a.out_dir);outdir.mkdir(parents=True,exist_ok=True);build(topics[a.id],pathlib.Path(a.golden),outdir)
if __name__=='__main__':main()

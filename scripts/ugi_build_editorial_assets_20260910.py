from __future__ import annotations

import hashlib, json, math, os, subprocess, time
from pathlib import Path
from urllib.parse import quote

import numpy as np
import requests
import soundfile as sf
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from kokoro import KPipeline

OUT=Path('public/ugi/editorial/2026-09-10'); SRC=OUT/'sources'; TMP=OUT/'tmp'
for p in (OUT,SRC,TMP): p.mkdir(parents=True,exist_ok=True)
UA={'User-Agent':'UGI-Editorial/2.0 (contact: umagestaointeligente@gmail.com)'}
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
NAVY=(8,19,38); CYAN=(69,213,255); GOLD=(230,190,88); WHITE=(248,250,252); MUTED=(205,215,226)

IMAGES={
 'starbucks':{'filename':'Starbucks SOH.jpg','width':1200,'license':'CC0 1.0','author':'KratosinWiki','page':'https://commons.wikimedia.org/wiki/File:Starbucks_SOH.jpg'},
 'straykids':{'filename':'Stray Kids in 2026.png','width':1919,'license':'CC BY 4.0','author':'_TV10 / YouTube','page':'https://commons.wikimedia.org/wiki/File:Stray_Kids_in_2026.png'},
 'rayban':{'filename':'New Ray-Ban Store Miami Worldcenter.jpg','width':2560,'license':'CC BY 2.0','author':'Phillip Pessar','page':'https://commons.wikimedia.org/wiki/File:New_Ray-Ban_Store_Miami_Worldcenter.jpg'},
}
MUSIC={
 'quantum':{'filename':'Sascha Ende - I Feel It (instrumental) (cc-by) (filmmusic).ogg','license':'CC BY 4.0','author':'Sascha Ende','page':'https://commons.wikimedia.org/wiki/File:Sascha_Ende_-_I_Feel_It_(instrumental)_(cc-by)_(filmmusic).ogg'},
 'compliance':{'filename':'Nctrnm - Queue.ogg','license':'CC BY 4.0','author':'Nctrnm','page':'https://commons.wikimedia.org/wiki/File:Nctrnm_-_Queue.ogg'},
 'sp500':{'filename':'Mise - 02 - Alive Doing It Right Instrumental.ogg','license':'CC BY 4.0','author':'Mise','page':'https://commons.wikimedia.org/wiki/File:Mise_-_02_-_Alive_Doing_It_Right_Instrumental.ogg'},
 'uscanada':{'filename':'Josh Woodward - 10 - Perfect Instrumental Version.ogg','license':'CC BY 4.0','author':'Josh Woodward','page':'https://commons.wikimedia.org/wiki/File:Josh_Woodward_-_10_-_Perfect_Instrumental_Version.ogg'},
 'video':{'path':'assets/music/innovation/dreamstate_library-modern-tech-corporate-theme-469710 (1).mp3','license':'repository-approved licensed asset','author':'Dreamstate Library','page':'repository asset'},
}

def commons(filename,width=None):
    u='https://commons.wikimedia.org/wiki/Special:Redirect/file/'+quote(filename,safe='')
    if width: u+=f'?width={width}'
    return u

def download_image(key):
    s=IMAGES[key]; p=SRC/s['filename']
    if p.exists() and p.stat().st_size>50000: return p
    r=requests.get(commons(s['filename'],s['width']),headers=UA,timeout=120,allow_redirects=True); r.raise_for_status()
    if 'image' not in r.headers.get('content-type',''): raise RuntimeError(f'{key}:not image')
    p.write_bytes(r.content); return p

def download_music(key):
    s=MUSIC[key]
    if 'path' in s: return Path(s['path'])
    p=SRC/s['filename']
    if p.exists() and p.stat().st_size>50000: return p
    r=requests.get(commons(s['filename']),headers=UA,timeout=120,allow_redirects=True); r.raise_for_status(); p.write_bytes(r.content); return p

def fnt(n,b=False): return ImageFont.truetype(BOLD if b else FONT,n)

def wrap(draw,text,font,maxw):
    out=[]; cur=''
    for w in text.split():
        t=w if not cur else cur+' '+w
        if draw.textbbox((0,0),t,font=font)[2]<=maxw: cur=t
        else:
            if cur: out.append(cur)
            cur=w
    if cur: out.append(cur)
    return out

def base(w,h):
    im=Image.new('RGB',(w,h),NAVY); d=ImageDraw.Draw(im)
    for y in range(h):
        t=y/max(1,h-1); c=(int(8+10*t),int(19+18*t),int(38+28*t)); d.line((0,y,w,y),fill=c)
    for x in range(0,w,90): d.line((x,0,x,h),fill=(18,37,60),width=1)
    for y in range(0,h,90): d.line((0,y,w,y),fill=(18,37,60),width=1)
    return im

def own_art(kind,w,h):
    im=base(w,h); d=ImageDraw.Draw(im)
    if kind=='quantum':
        cx,cy=w//2,int(h*.32); d.ellipse((cx-210,cy-210,cx+210,cy+210),outline=CYAN,width=12)
        for r in (60,120,175): d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(55,105,150),width=5)
        for a in range(0,360,30):
            x=cx+int(260*math.cos(math.radians(a))); y=cy+int(260*math.sin(math.radians(a))); d.line((cx,cy,x,y),fill=(42,92,137),width=4)
    elif kind=='compliance':
        d.rounded_rectangle((150,190,w-150,720),radius=50,outline=GOLD,width=10); d.rectangle((290,330,w-290,590),outline=WHITE,width=8)
        d.line((290,330,w-290,590),fill=GOLD,width=10); d.line((w-290,330,290,590),fill=GOLD,width=10)
    elif kind=='sp500':
        pts=[]
        for i,v in enumerate([.68,.58,.61,.47,.52,.39,.32,.21]): pts.append((120+i*(w-240)//7,250+int(v*620)))
        d.line(pts,fill=CYAN,width=14,joint='curve');
        for x,y in pts: d.ellipse((x-12,y-12,x+12,y+12),fill=WHITE)
    elif kind=='uscanada':
        d.rounded_rectangle((90,180,w//2-20,650),70,fill=(32,55,88),outline=WHITE,width=5); d.rounded_rectangle((w//2+20,180,w-90,650),70,fill=(80,30,35),outline=WHITE,width=5)
        d.text((165,330),'EUA',font=fnt(80,True),fill=WHITE); d.text((w//2+95,330),'CANADÁ',font=fnt(62,True),fill=WHITE)
        d.line((260,760,w-260,760),fill=GOLD,width=16); d.polygon([(w-260,760),(w-340,715),(w-340,805)],fill=GOLD)
    elif kind=='lockedin':
        d.rounded_rectangle((130,180,w-130,1050),60,fill=(15,32,52),outline=CYAN,width=8)
        for i,y in enumerate((320,500,680,860)):
            d.rounded_rectangle((220,y,300,y+80),12,outline=WHITE,width=5); d.line((235,y+42,265,y+68),fill=CYAN,width=8); d.line((265,y+68,305,y+20),fill=CYAN,width=8)
            d.line((360,y+42,w-220,y+42),fill=(80,110,135),width=8)
    return im

def photo_canvas(path,w,h):
    src=Image.open(path).convert('RGB')
    bg=src.resize((w,h),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(28)); bg=ImageEnhance.Brightness(bg).enhance(.42)
    maxw=int(w*.92); maxh=int(h*.53); scale=min(maxw/src.width,maxh/src.height,1.0); fg=src.resize((int(src.width*scale),int(src.height*scale)),Image.Resampling.LANCZOS)
    x=(w-fg.width)//2; y=int(h*.12); bg.paste(fg,(x,y)); return bg

def text_card(im,headline,sub,source,credit=None):
    d=ImageDraw.Draw(im); w,h=im.size; m=int(w*.07); hf=fnt(68 if h>1000 else 42,True); sf=fnt(34 if h>1000 else 26); small=fnt(19 if h>1000 else 15)
    y=int(h*.62) if h>1000 else int(h*.58)
    for line in wrap(d,headline,hf,w-2*m): d.text((m,y),line,font=hf,fill=WHITE,stroke_width=2,stroke_fill=(0,0,0)); y+=int(hf.size*1.16)
    y+=16
    for line in wrap(d,sub,sf,w-2*m): d.text((m,y),line,font=sf,fill=MUTED); y+=int(sf.size*1.3)
    d.line((m,h-150,w-m,h-150),fill=(48,77,103),width=2); d.text((m,h-124),'UGI • Uma Gestão Inteligente',font=fnt(21,True),fill=WHITE); d.text((m,h-86),source,font=small,fill=MUTED)
    if credit: d.text((m,h-55),credit,font=small,fill=(170,185,200))
    return im

def save_jpg(im,name):
    p=OUT/name; im.save(p,'JPEG',quality=94,subsampling=0,optimize=True); return p

def story(kind,name,headline,sub,source,music_key):
    jpg=save_jpg(text_card(own_art(kind,1080,1920),headline,sub,source),name+'.jpg')
    mus=download_music(music_key); out=OUT/(name+'.mp4')
    subprocess.run(['ffmpeg','-y','-loop','1','-i',str(jpg),'-stream_loop','-1','-i',str(mus),'-t','8','-vf','scale=1080:1920,format=yuv420p','-c:v','libx264','-r','30','-c:a','aac','-b:a','160k','-af','volume=0.24,afade=t=out:st=7.5:d=0.5','-shortest','-movflags','+faststart',str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return out

def tts(text,name):
    pipeline=KPipeline(lang_code='p'); parts=[]
    for _,_,audio in pipeline(text,voice='pm_santa',speed=1.04): parts.append(np.asarray(audio,dtype=np.float32))
    if not parts: raise RuntimeError('tts empty')
    a=np.concatenate(parts); p=TMP/(name+'.wav'); sf.write(p,a,24000); return p,len(a)/24000.0

def scene_image(kind,photo,headline,sub,source,credit,name):
    if photo: im=photo_canvas(photo,1080,1920)
    else: im=own_art(kind,1080,1920)
    return save_jpg(text_card(im,headline,sub,source,credit),name)

def narrated_video(name,narration,scenes,music_path):
    wav,dur=tts(narration,name); n=len(scenes); each=max(3.0,dur/n); vids=[]
    for i,p in enumerate(scenes):
        v=TMP/f'{name}-{i}.mp4'; subprocess.run(['ffmpeg','-y','-loop','1','-i',str(p),'-t',str(each),'-vf',"zoompan=z='min(zoom+0.00035,1.045)':d=1:s=1080x1920:fps=30,format=yuv420p",'-an','-c:v','libx264','-r','30',str(v)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL); vids.append(v)
    lst=TMP/(name+'-concat.txt'); lst.write_text('\n'.join("file '"+str(v.resolve()).replace("'","'\\''")+"'" for v in vids),encoding='utf-8')
    video=TMP/(name+'-video.mp4'); subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(lst),'-c','copy',str(video)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    out=OUT/(name+'.mp4'); subprocess.run(['ffmpeg','-y','-i',str(video),'-i',str(wav),'-stream_loop','-1','-i',str(music_path),'-filter_complex','[1:a]volume=1.0[v];[2:a]volume=0.10[m];[v][m]amix=inputs=2:duration=first:dropout_transition=2[a]','-map','0:v:0','-map','[a]','-t',str(dur),'-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return out

def carousel_oil():
    slides=[('Petróleo acima de US$100','Isso chega ao DRE mais rápido do que parece.'),('1. Combustível e frete','Energia mais cara pode aumentar o custo de movimentar produto.'),('2. Embalagens e insumos','Materiais ligados à cadeia petroquímica podem sofrer pressão.'),('3. Inflação e juros','Energia pode contaminar preços e prolongar pressão financeira.'),('4. Preço ou margem?','Nem todo custo pode ser repassado sem perder volume.'),('Gestão: simule antes do choque','Custo, preço, estoque, fornecedor e caixa precisam de cenário.')]
    out=[]
    for i,(h,s) in enumerate(slides,1):
        im=base(1080,1350); d=ImageDraw.Draw(im); d.ellipse((80,105,230,255),outline=GOLD,width=12); d.text((125,130),'$',font=fnt(70,True),fill=GOLD)
        out.append(save_jpg(text_card(im,h,s,'Fonte: Reuters • 09/09/2026'),f'carousel-oil-1430-{i:02d}.jpg'))
    return out

def sha(p):
    h=hashlib.sha256();
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def probe(p):
    try:
        r=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,codec_name,width,height','-of','json',str(p)],text=True); return json.loads(r)
    except Exception: return None

def main():
    star=download_image('starbucks'); sk=download_image('straykids'); rb=download_image('rayban'); videomusic=download_music('video')
    finals=[]
    finals += [story('quantum','story-quantum-0830','A corrida quântica já custa bilhões.','O retorno ainda é uma aposta.','Fonte: Reuters • 09/09/2026','quantum')]
    finals += [story('compliance','story-compliance-1200','479 trabalhadores foram resgatados.','Compliance não termina no contrato.','Fonte: Ministério do Trabalho e Emprego • 09/09/2026','compliance')]
    finals += [story('sp500','story-sp500-1730','86% do S&P 500 superaram estimativas.','Resultado forte não elimina expectativa alta.','Fonte: Reuters / LSEG • 09/09/2026','sp500')]
    finals += [story('uscanada','story-uscanada-2030','Tarifas já viraram proibições.','Geopolítica também entra na operação.','Fonte: Reuters • 09/09/2026','uscanada')]

    li=photo_canvas(star,1200,627); li=text_card(li,'Recuperar clientes é só metade de um turnaround.','Starbucks: o segundo ato é transformar experiência em rentabilidade.','Fonte: Reuters • 09/09/2026','Imagem: KratosinWiki • CC0 1.0'); finals.append(save_jpg(li,'linkedin-starbucks-1400.jpg'))
    finals += carousel_oil()

    kpop_narr='Pela primeira vez em 41 anos, o Rock in Rio terá um dia inteiro dedicado ao K-pop no Palco Mundo. NEXZ, Hwasa e Stray Kids ocupam a programação de sexta-feira, e a data já está esgotada. Até os lightsticks, parte importante da cultura dos fãs de K-pop, foram incorporados à experiência do festival. Isso mostra uma mudança maior do que o line-up. Um nicho deixa de ser nicho quando ganha comunidade organizada, capacidade de mobilização e disposição para pagar por uma experiência própria. Para gestão, a lição é simples: novos mercados raramente aparecem do nada. Eles crescem primeiro nas bordas, criam linguagem, comportamento e comunidade, e só depois obrigam as grandes marcas a redesenhar produto, experiência e comunicação. Quem percebe cedo está aprendendo a reconhecer demanda antes que ela vire consenso.'
    ks=[('Quando um nicho vira mercado','Rock in Rio dedica um dia inteiro ao K-pop.'),('Comunidade antes de escala','Fãs criam linguagem, símbolos e mobilização.'),('Demanda organizada muda o jogo','A data esgotada transforma sinal cultural em mercado.'),('Grandes marcas percebem as bordas','Produto e experiência mudam quando a comunidade ganha força.'),('Gestão: enxergue antes do consenso','Mercados novos parecem pequenos até deixarem de ser.')]
    ksc=[]
    for i,(h,s) in enumerate(ks): ksc.append(scene_image('',sk,h,s,'Fonte: UOL • 09/09/2026','Imagem contextual: Stray Kids, _TV10 • CC BY 4.0',f'kpop-scene-{i}.jpg'))
    finals.append(narrated_video('reel-kpop-1015',kpop_narr,ksc,videomusic))

    lock_narr='O TikTok colocou o locked in entre os sinais culturais de 2026. A lógica é simples: pessoas assumem um compromisso em público, mostram o processo e usam a comunidade como cobrança e motivação. Mas no trabalho existe uma diferença importante. Foco não é encher a agenda, responder tudo rápido ou passar o dia em reunião. Foco é escolher o que merece energia e conseguir provar avanço. Se você terminou o dia cansado, mas não consegue dizer qual resultado moveu, talvez você não estivesse focado. Talvez estivesse só ocupado. A pergunta útil para amanhã é: qual entrega, se avançar de verdade, muda o seu resultado? Comece por ela.'
    ls=[('Foco real ou aparência?','Agenda cheia não é evidência de avanço.'),('Compromisso público','A tendência locked in usa comunidade como accountability.'),('Atividade não é resultado','Responder tudo rápido pode esconder falta de prioridade.'),('Foco é escolha','Escolha uma entrega que realmente muda o resultado.'),('Prove avanço','No fim do dia, o que efetivamente mudou?')]
    lsc=[scene_image('lockedin',None,h,s,'Fonte: TikTok Next 2026',None,f'lockedin-scene-{i}.jpg') for i,(h,s) in enumerate(ls)]
    finals.append(narrated_video('tiktok-lockedin-1130',lock_narr,lsc,videomusic))

    gov_narr='A EssilorLuxottica, dona da Ray-Ban, virou um caso interessante de governança. Leonardo Maria Del Vecchio, filho do fundador, criticou publicamente a liderança e pediu mais transparência e mudanças estratégicas. O conselho respondeu de forma unânime: reafirmou confiança no CEO Francesco Milleri e na direção da empresa. O ponto aqui não é escolher um lado. É entender que família, propriedade, conselho e gestão são papéis diferentes. Ter sobrenome, participação econômica ou legado não significa controlar sozinho a decisão executiva. E um conselho que existe só para concordar também não cumpre seu papel. Governança funciona quando as regras de poder estão claras antes do conflito. Porque, quando a crise chega, descobrir quem decide já é tarde demais.'
    gs=[('Filho do fundador x CEO','O conselho tomou posição.'),('Família, propriedade e gestão','São papéis diferentes.'),('Conselho não é decoração','Ele precisa decidir quando há conflito.'),('Governança define poder','Antes da crise, não durante.'),('A pergunta central','Quando todos discordam, quem tem mandato para decidir?')]
    gsc=[scene_image('',rb,h,s,'Fonte: Reuters • 09/09/2026','Imagem: Phillip Pessar • CC BY 2.0',f'essilor-scene-{i}.jpg') for i,(h,s) in enumerate(gs)]
    finals.append(narrated_video('tiktok-essilor-1945',gov_narr,gsc,videomusic))

    pub=[p for p in finals if p.exists()]
    manifest={'schema':'UGI_EDITORIAL_ASSET_PROVENANCE_V2','date':'2026-09-10','state':'FINAL_ASSETS_BUILT_QA_PENDING','batchScopedPreviewWaiver':True,'waiverBasis':'Paulo explicitly authorized direct scheduling of the Sep10 batch without sending intermediate previews in chat; general future approval policy remains unchanged.','images':IMAGES,'music':MUSIC,'rules':{'globalAntiRepeatDays':60,'noGenericCompanyVisual':True,'starbucksIdentifiable':True,'visibleCopyControlledRenderer':True,'storyMusicDistinct':True,'videosNarratedPtBr':True},'finals':[]}
    for p in pub:
        manifest['finals'].append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'probe':probe(p)})
    (OUT/'asset-provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'publishable':len(pub),'files':[str(x) for x in pub]},ensure_ascii=False,indent=2))

if __name__=='__main__': main()

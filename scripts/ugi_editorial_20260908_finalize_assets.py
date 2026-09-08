#!/usr/bin/env python3
from pathlib import Path
import subprocess, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'public/ugi/editorial/2026-09-08'
OUT.mkdir(parents=True, exist_ok=True)
TMP = Path('/tmp/ugi_20260908_finalize')
TMP.mkdir(parents=True, exist_ok=True)

FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
GREEN = '#76B900'

def font(path, size): return ImageFont.truetype(path, size)

def wrap(draw, text, fnt, maxw):
    words=text.split(); lines=[]; cur=''
    for w in words:
        cand=(cur+' '+w).strip()
        if draw.textbbox((0,0),cand,font=fnt)[2] <= maxw: cur=cand
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines

def download(url, dst):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 UGI/1.0'})
    with urllib.request.urlopen(req,timeout=120) as r, open(dst,'wb') as f:
        while True:
            b=r.read(1024*1024)
            if not b: break
            f.write(b)

def make_nvidia_story():
    # Same real NVIDIA Santa Clara headquarters visual approved by Paulo in the V2 company-context Story.
    url='https://iprsoftwaremedia.com/219/files/20225/62993f2db3aed3337e54cd27_DH1L4494-HDR-20220531-r4/DH1L4494-HDR-20220531-r4_53597373-2db9-451f-b98b-543c97856fa7-prv.jpg?v=53597373-2db9-451f-b98b-543c97856fa7'
    src=TMP/'nvidia_hq.jpg'; download(url,src)
    hero=Image.open(src).convert('RGB')
    scale=1080/hero.width; hero=hero.resize((1080,round(hero.height*scale)),Image.Resampling.LANCZOS)
    if hero.height < 760:
        bg=Image.new('RGB',(1080,760),'black'); bg.paste(hero,(0,0)); hero=bg
    else: hero=hero.crop((0,0,1080,760))
    im=Image.new('RGB',(1080,1920),'#050505'); im.paste(hero,(0,0))
    # bottom fade on hero
    fade=Image.new('RGBA',(1080,240),(0,0,0,0)); px=fade.load()
    for y in range(240):
        a=int(230*(y/239)**1.7)
        for x in range(1080): px[x,y]=(5,5,5,a)
    im=Image.alpha_composite(im.convert('RGBA'), Image.new('RGBA',(1080,1920),(0,0,0,0)))
    im.alpha_composite(fade,(0,520)); d=ImageDraw.Draw(im)
    d.text((58,58),'UGI • ESTRATÉGIA + IA',font=font(BOLD,24),fill=GREEN)
    y=720
    f=font(BOLD,66)
    d.text((58,y),'A vantagem da',font=f,fill='white'); w=d.textbbox((58,y),'A vantagem da ',font=f)[2]-58
    d.text((58+w,y),'NVIDIA',font=f,fill=GREEN)
    y+=70; d.text((58,y),'está sendo testada',font=f,fill='white')
    y+=70; d.text((58,y),'na China.',font=f,fill='white')
    y+=100; d.text((58,y),'≈55% de participação no mercado chinês de chips de IA',font=font(BOLD,32),fill=GREEN)
    y+=70
    body='Concorrentes locais aceleram. Para a gestão, a discussão vai além da tecnologia: concentração de fornecedor, poder de negociação e capacidade real de substituição.'
    bf=font(FONT,29)
    for line in wrap(d,body,bf,930): d.text((58,y),line,font=bf,fill='#EFEFEF'); y+=41
    # Insight box
    d.rectangle((58,1568,1022,1778),fill='#111111'); d.rectangle((58,1568,64,1778),fill=GREEN)
    d.text((88,1596),'INSIGHT UGI',font=font(BOLD,24),fill='white')
    insight='Sua operação estaria preparada se o fornecedor hoje dominante deixasse de ser insubstituível?'
    iy=1644; inf=font(FONT,28)
    for line in wrap(d,insight,inf,875): d.text((88,iy),line,font=inf,fill='white'); iy+=37
    d.text((58,1840),'UGI   Uma Gestão Inteligente',font=font(BOLD,18),fill='white')
    d.text((760,1840),'Fonte: Reuters • 07/09/2026',font=font(FONT,18),fill='#A6A6A6')
    out=OUT/'story-nvidia-company-approved-v2.png'; im.convert('RGB').save(out,quality=95)
    return out

def make_semicon_linkedin():
    src=OUT/'semicon_probe/source.mp4'
    frame=TMP/'semicon_frame.jpg'
    subprocess.run(['ffmpeg','-y','-ss','20','-i',str(src),'-frames:v','1','-q:v','2',str(frame)],check=True)
    bg=Image.open(frame).convert('RGB')
    # cover 1200x628 while preserving event scene; no destructive zoom beyond cover crop.
    scale=max(1200/bg.width,628/bg.height); bg=bg.resize((round(bg.width*scale),round(bg.height*scale)),Image.Resampling.LANCZOS)
    left=(bg.width-1200)//2; top=(bg.height-628)//2; bg=bg.crop((left,top,left+1200,top+628))
    im=bg.convert('RGBA')
    overlay=Image.new('RGBA',(1200,628),(0,0,0,0)); od=ImageDraw.Draw(overlay)
    # left-to-right cinematic readability gradient
    for x in range(760):
        a=int(232*(1-x/760)**0.65)
        od.rectangle((x,0,x+1,628),fill=(0,0,0,a))
    od.rectangle((0,0,1200,76),fill=(0,0,0,125))
    im=Image.alpha_composite(im,overlay); d=ImageDraw.Draw(im)
    d.text((54,26),'UGI • ESTRATÉGIA • CADEIA DE SUPRIMENTO',font=font(BOLD,21),fill='white')
    y=128; hf=font(BOLD,51)
    for line in ['TAIWAN ESTÁ NO','CENTRO DA CORRIDA','GLOBAL POR CHIPS.']:
        d.text((54,y),line,font=hf,fill='white'); y+=58
    d.text((54,326),'SEMICON TAIWAN 2026',font=font(BOLD,30),fill='#7DFF8A')
    body='Mais de 1.300 expositores — e uma lição de gestão: a mesma concentração que cria vantagem também cria dependência.'
    y=372; bf=font(FONT,25)
    for line in wrap(d,body,bf,615): d.text((54,y),line,font=bf,fill='white'); y+=34
    d.rectangle((54,511,670,576),fill=(9,20,14,220)); d.rectangle((54,511,60,576),fill='#76B900')
    d.text((79,529),'VANTAGEM + DEPENDÊNCIA = RISCO ESTRATÉGICO',font=font(BOLD,18),fill='white')
    d.text((54,592),'UGI • Uma Gestão Inteligente',font=font(BOLD,16),fill='white')
    d.text((870,592),'SEMICON Taiwan 2026',font=font(FONT,15),fill='#DDDDDD')
    out=OUT/'linkedin-semicon-taiwan-company-context-v1.png'; im.convert('RGB').save(out,quality=95)
    return out

if __name__=='__main__':
    a=make_nvidia_story(); b=make_semicon_linkedin(); print(a); print(b)

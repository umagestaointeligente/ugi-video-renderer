#!/usr/bin/env python3
from __future__ import annotations

import json, os, subprocess, textwrap
from pathlib import Path
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "control-plane/instagram-20260901/assets"
MUSIC_DIR = ASSET_DIR / "_music"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

MUSIC = {
    "Running Out of Time": "https://assets.mixkit.co/music/77/77.mp3",
    "Your Breath": "https://assets.mixkit.co/music/634/634.mp3",
    "The Boss": "https://assets.mixkit.co/music/479/479.mp3",
    "Motivating Mornings": "https://assets.mixkit.co/music/33/33.mp3",
    "Stay With Me": "https://assets.mixkit.co/music/838/838.mp3",
}
LICENSE = {"source":"Mixkit","license":"Mixkit License","catalog":"https://mixkit.co/free-stock-music/corporate-music/"}
APPLE_PHOTO = "https://www.apple.com/newsroom/images/2026/04/tim-cook-to-become-apple-executive-chairman-john-ternus-to-become-apple-ceo/article/Apple-John-Ternus-Tim-Cook_Full-Bleed-Image.jpg.large.jpg"

STORIES = [
 {"id":"UGI-20260901-IG-STORY-01-NEPAL","due":"2026-09-01T09:00:00-03:00","kicker":"GESTÃO DE CRISE","metric":"14 MIN","title":"UM ALERTA.\n900+ ALUNOS EVACUADOS.","body":"No Nepal, uma escola teve minutos para agir antes da enchente. Processo, sinal e decisão rápida mudaram o desfecho.","cta":"Sua empresa saberia o que fazer em 14 minutos?","music":"Running Out of Time","accent":"#EF8A62"},
 {"id":"UGI-20260901-IG-STORY-02-AI-VALUE","due":"2026-09-01T11:00:00-03:00","kicker":"IA + GESTÃO","metric":"94%","title":"IA NÃO CRIA VALOR\nSOZINHA.","body":"A McKinsey aponta que 94% das empresas ainda não geraram valor relevante com IA. O gargalo é gestão, fluxo e execução.","cta":"Ferramenta sem redesenho vira custo sofisticado.","music":"Your Breath","accent":"#4EC6FF"},
 {"id":"UGI-20260901-IG-STORY-03-NVIDIA","due":"2026-09-01T14:30:00-03:00","kicker":"ESTRATÉGIA","metric":"US$ 3,5 BI","title":"ÀS VEZES, CRESCER É\nFORTALECER O ECOSSISTEMA.","body":"A Nvidia investiu na MediaTek enquanto clientes buscam chips próprios. Estratégia também é escolher onde continuar indispensável.","cta":"Integração pode ser mais valiosa que controle total.","music":"The Boss","accent":"#7BD56B"},
 {"id":"UGI-20260901-IG-STORY-04-APPLE","due":"2026-09-01T17:00:00-03:00","kicker":"SUCESSÃO","metric":"15 ANOS","title":"O LÍDER MUDA.\nO SISTEMA PRECISA FICAR.","body":"Tim Cook encerra 15 anos como CEO e John Ternus assume. Uma sucessão bem preparada começa antes do anúncio.","cta":"Às 18h: o que essa transição ensina no carrossel.","music":"Motivating Mornings","accent":"#D6A85F"},
 {"id":"UGI-20260901-IG-STORY-05-COMMERCE","due":"2026-09-01T20:30:00-03:00","kicker":"UGI NA PRÁTICA","metric":"AÇÃO","title":"GESTÃO BOA PRECISA\nVIRAR SISTEMA.","body":"Frameworks, checklists e materiais UGI para liderança, delegação, decisões e IA aplicada ao trabalho.","cta":"Materiais no link da bio. Acesse e compre o seu hoje.","music":"Stay With Me","accent":"#43B9F5"},
]

CAROUSEL = {
 "id":"UGI-20260901-IG-CAROUSEL-APPLE-SUCCESSION",
 "due":"2026-09-01T18:00:00-03:00",
 "audioMode":"NONE_AUTOMATED_NATIVE_CAROUSEL_UNSUPPORTED",
 "caption":"15 anos no comando. Uma sucessão preparada muito antes do anúncio. Em 1º de setembro, John Ternus assume como CEO da Apple e Tim Cook passa a Executive Chairman. O ponto UGI não é idolatrar um líder: é observar como continuidade, sucessão e autonomia são construídas antes da troca de cadeira. O legado que escala é sistema, não dependência. Salve este carrossel para a próxima conversa sobre sucessão e liderança. #UmaGestaoInteligente #Lideranca #Gestao #Sucessao #Apple",
 "slides":[
  ("SUCESSÃO","15 ANOS NO COMANDO.\nO QUE FICA QUANDO\nO LÍDER SAI?","A Apple troca de CEO em 1º de setembro. A pergunta de gestão é maior que o cargo."),
  ("CONTEXTO","A SUCESSÃO COMEÇOU\nANTES DE HOJE.","A Apple anunciou a transição em abril. Sucessão robusta não começa quando a cadeira fica vazia."),
  ("TRANSIÇÃO","TIM COOK NÃO\nDESAPARECE.","Ele passa a Executive Chairman. Transição pode preservar contexto sem impedir o novo líder de liderar."),
  ("CONTINUIDADE","JOHN TERNUS ASSUME\nDE DENTRO.","Depois de 25 anos na Apple, o sucessor conhece produto, cultura e operação. Pipeline de liderança também é estratégia."),
  ("LEGADO","O QUE ESCALA É\nSISTEMA, NÃO PRESENÇA.","Processos, critérios e pessoas preparadas valem mais que uma empresa dependente de uma única figura."),
  ("PERGUNTA","SUA EMPRESA FUNCIONARIA\nBEM SEM VOCÊ?","Se decisões, clientes e prioridades param quando o líder sai, o problema não é ausência. É desenho de gestão."),
  ("UGI","LIDERANÇA MELHOR\nSE CONSTRÓI EM PRÁTICA.","Frameworks, checklists e materiais UGI estão no link da bio. Acesse e compre o seu."),
 ]
}

SOURCES = {
 "nepal":"https://www.reuters.com/business/environment/last-minute-flood-warning-saved-over-900-nepal-students-school-head-says-2026-08-31/",
 "ai":"https://www.mckinsey.com/capabilities/tech-and-ai/our-insights/the-new-management-playbook-for-ai-how-to-move-faster-and-create-more-value",
 "nvidia":"https://www.reuters.com/world/asia-pacific/nvidia-invests-35-billion-mediatek-convertible-bonds-2026-08-31/",
 "apple":"https://www.apple.com/newsroom/2026/04/tim-cook-to-become-apple-executive-chairman-john-ternus-to-become-apple-ceo/"
}

def f(path,size): return ImageFont.truetype(path,size)
def wrap(draw,text,font,maxw):
    out=[]
    for para in text.split('\n'):
        cur=''
        for word in para.split():
            nxt=(cur+' '+word).strip()
            if draw.textbbox((0,0),nxt,font=font)[2] <= maxw: cur=nxt
            else:
                if cur: out.append(cur)
                cur=word
        if cur: out.append(cur)
    return out

def dl(url,path):
    r=requests.get(url,timeout=120); r.raise_for_status(); path.write_bytes(r.content)
    if path.stat().st_size < 10000: raise RuntimeError(f"download too small {url}")

def story_card(path,s):
    W,H=1080,1920
    im=Image.new('RGB',(W,H),(4,17,31)); d=ImageDraw.Draw(im)
    # premium gradient + controlled shapes; no generated/background text
    for y in range(H):
        t=y/(H-1); d.line((0,y,W,y),fill=(4+int(6*t),17+int(14*t),31+int(24*t)))
    accent=tuple(int(s['accent'].lstrip('#')[i:i+2],16) for i in (0,2,4))
    d.ellipse((670,-140,1210,410),fill=(7,45,70)); d.ellipse((-280,1360,430,2060),fill=(6,33,52))
    d.rounded_rectangle((58,85,390,145),radius=30,outline=accent,width=2)
    d.text((82,102),s['kicker'],font=f(BOLD,21),fill=(223,237,245))
    d.text((62,260),s['metric'],font=f(SERIF_BOLD,104),fill=accent)
    d.line((62,400,170,400),fill=accent,width=8)
    y=495; tf=f(BOLD,64)
    for line in wrap(d,s['title'],tf,950):
        d.text((62,y),line,font=tf,fill=(249,251,253)); y+=78
    y+=35; bf=f(REG,34)
    for line in wrap(d,s['body'],bf,950):
        d.text((62,y),line,font=bf,fill=(211,225,235)); y+=49
    d.line((62,1570,1018,1570),fill=(54,77,96),width=2)
    cf=f(BOLD,30); yy=1610
    for line in wrap(d,s['cta'],cf,950):
        d.text((62,yy),line,font=cf,fill=(230,239,245)); yy+=42
    d.text((62,1815),'UGI | UMA GESTÃO INTELIGENTE',font=f(BOLD,18),fill=(165,195,213))
    im.save(path,optimize=True)

def make_mp4(img,music,out,duration=9):
    vf=f"scale=1080:1920,zoompan=z='min(zoom+0.00055,1.025)':d={duration*30}:s=1080x1920:fps=30,format=yuv420p"
    af=f"atrim=0:{duration},afade=t=in:st=0:d=0.4,afade=t=out:st={duration-0.8}:d=0.8,loudnorm=I=-15:TP=-1.5:LRA=7"
    subprocess.run(['ffmpeg','-y','-loglevel','error','-loop','1','-i',str(img),'-stream_loop','-1','-i',str(music),'-t',str(duration),'-vf',vf,'-af',af,'-c:v','libx264','-crf','20','-preset','medium','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)],check=True)

def cover_from_apple(photo:Image.Image, slide_no:int):
    W,H=1080,1350
    # crop photo as background focusing Tim Cook on right half
    scale=max(W/photo.width,H/photo.height); p=photo.resize((int(photo.width*scale),int(photo.height*scale)))
    left=max(0,(p.width-W)//2); top=max(0,(p.height-H)//2); p=p.crop((left,top,left+W,top+H)).convert('RGB')
    overlay=Image.new('RGBA',(W,H),(3,18,34,0)); od=ImageDraw.Draw(overlay)
    for x in range(W):
        alpha=int(232*(1-x/W)**1.25)+40
        od.line((x,0,x,H),fill=(3,18,34,min(245,alpha)))
    return Image.alpha_composite(p.convert('RGBA'),overlay).convert('RGB')

def carousel_slide(path, idx, kick, title, body, photo):
    W,H=1080,1350
    if idx in (1,2,3,4): im=cover_from_apple(photo,idx)
    elif idx==6:
        # transition: blurred Apple photo, no frontal endorsement-like use
        im=cover_from_apple(photo,idx).filter(ImageFilter.GaussianBlur(10))
    else:
        im=Image.new('RGB',(W,H),(5,20,36)) if idx==5 else Image.new('RGB',(W,H),(247,244,238))
    d=ImageDraw.Draw(im)
    dark = idx != 7
    if idx==7:
        # UGI-only CTA; no person/company image
        d.ellipse((700,-100,1160,360),fill=(225,232,238)); d.ellipse((-250,1000,320,1500),fill=(232,238,242))
    accent=(210,163,94) if dark else (20,74,103)
    fg=(250,250,248) if dark else (9,35,53)
    bodyc=(219,228,235) if dark else (41,72,91)
    d.rounded_rectangle((62,70,330,122),radius=24,outline=accent,width=2)
    d.text((82,84),kick,font=f(BOLD,19),fill=fg)
    tf=f(SERIF_BOLD,55 if idx!=1 else 61); y=220
    for line in wrap(d,title,tf,910):
        d.text((62,y),line,font=tf,fill=fg); y+=68
    y+=34; bf=f(REG,29)
    for line in wrap(d,body,bf,900):
        d.text((62,y),line,font=bf,fill=bodyc); y+=42
    if idx==7:
        d.rounded_rectangle((62,1015,650,1090),radius=18,outline=accent,width=2)
        d.text((88,1038),'ACESSE O LINK DA BIO',font=f(BOLD,24),fill=accent)
    d.line((62,1248,1018,1248),fill=accent,width=2)
    d.text((62,1272),'UGI | UMA GESTÃO INTELIGENTE',font=f(BOLD,16),fill=fg)
    d.text((960,1272),f'{idx}/7',font=f(BOLD,16),fill=fg)
    im.save(path,optimize=True)

def probe(path):
    cp=subprocess.run(['ffprobe','-v','error','-show_entries','stream=codec_type,codec_name,width,height','-of','json',str(path)],check=True,capture_output=True,text=True)
    return json.loads(cp.stdout)

def main():
    ASSET_DIR.mkdir(parents=True,exist_ok=True); MUSIC_DIR.mkdir(exist_ok=True)
    for i,s in enumerate(STORIES,1):
        img=ASSET_DIR/f'story-{i:02d}.png'; mp3=MUSIC_DIR/f'story-{i:02d}.mp3'; out=ASSET_DIR/f'story-{i:02d}.mp4'
        story_card(img,s)
        dl(MUSIC[s['music']],mp3)
        make_mp4(img,mp3,out)
        pr=probe(out); types={x.get('codec_type') for x in pr.get('streams',[])}
        if not {'video','audio'} <= types: raise RuntimeError(f'AV QA failed {out}')
    ap=ASSET_DIR/'apple-tim-cook-john-ternus.jpg'; dl(APPLE_PHOTO,ap)
    photo=Image.open(ap).convert('RGB')
    for i,(k,t,b) in enumerate(CAROUSEL['slides'],1): carousel_slide(ASSET_DIR/f'carousel-{i:02d}.png',i,k,t,b,photo)
    manifest={
      'date':'2026-09-01','timezone':'America/Sao_Paulo','stories':STORIES,'carousel':CAROUSEL,
      'musicLicense':LICENSE,'sources':SOURCES,
      'hardGates':{
        'antiRepeatDays':15,'ghostTextForbidden':True,'foreignBackgroundTextForbidden':True,
        'storyMusicUnique':True,'chiptuneForbidden':True,'carouselFirstSlideOnlyAudioForbidden':True,
        'publicFigureContinuityRequired':True,'ctaSlidePublicFigureForbidden':True
      },
      'qa':{'storiesAV':'PASS','carouselTextLayer':'DETERMINISTIC_PIL','carouselAudio':'INTENTIONALLY_NONE'}
    }
    (ASSET_DIR/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'ok':True,'assetDir':str(ASSET_DIR),'stories':len(STORIES),'carouselSlides':7},ensure_ascii=False))

if __name__=='__main__': main()

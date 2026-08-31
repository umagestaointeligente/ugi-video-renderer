#!/usr/bin/env python3
from __future__ import annotations

import argparse, base64, datetime as dt, json, os, subprocess, textwrap, time
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
from PIL import Image, ImageDraw, ImageFont

WORKER = "https://lola-operacional-ugi.umagestaointeligente.workers.dev"
ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "control-plane/instagram-20260831/assets"
RECEIPT = ROOT / "control-plane/instagram-20260831/receipts/ugi-20260831-growth.json"
RAW_BASE = "https://raw.githubusercontent.com/umagestaointeligente/ugi-video-renderer/main/control-plane/instagram-20260831/assets"

MUSIC = {
    "Close Up": "https://assets.mixkit.co/music/1167/1167.mp3",
    "Motivating Mornings": "https://assets.mixkit.co/music/33/33.mp3",
    "Your Breath": "https://assets.mixkit.co/music/634/634.mp3",
    "Running Out of Time": "https://assets.mixkit.co/music/77/77.mp3",
    "Stay With Me": "https://assets.mixkit.co/music/838/838.mp3",
    "The Boss": "https://assets.mixkit.co/music/479/479.mp3",
}
LICENSE = {"source": "Mixkit", "license": "Mixkit License", "catalog": "https://mixkit.co/free-stock-music/corporate-music/"}

STORIES = [
    {"id":"UGI-20260831-IG-STORY-01-GOVERNANCE","due":"2026-08-31T08:45:00-03:00","kicker":"GOVERNANÇA","title":"IA AVANÇOU.\nA GOVERNANÇA ACOMPANHOU?","body":"Antes de dar autonomia: acesso, limites, aprovação e responsabilidade.","cta":"Governar antes de escalar.","music":"Close Up","accent":"#2eb7f5"},
    {"id":"UGI-20260831-IG-STORY-02-KPMG","due":"2026-08-31T11:40:00-03:00","kicker":"CONFIANÇA","title":"UMA FALHA ÉTICA PODE\nCOBRAR POR ANOS.","body":"No caso KPMG Austrália, perda de contratos, pressão sobre receita e cortes mostram que confiança também chega ao P&L.","cta":"Às 15h: o custo da confiança no carrossel.","music":"Running Out of Time","accent":"#51c7ff"},
    {"id":"UGI-20260831-IG-STORY-03-VW","due":"2026-08-31T17:35:00-03:00","kicker":"MUDANÇA","title":"ESTRATÉGIA SEM INFORMAÇÃO\nVIRA RESISTÊNCIA.","body":"Em uma transformação, o vazio vira rumor. Explique por quê, o que muda e o que ainda não está decidido.","cta":"Reel às 19h.","music":"Motivating Mornings","accent":"#36aeea"},
    {"id":"UGI-20260831-IG-STORY-04-PHYSICAL-AI","due":"2026-08-31T20:20:00-03:00","kicker":"PRÓXIMA ONDA","title":"IA JÁ ESTÁ SAINDO\nDA TELA.","body":"Robôs, máquinas e sistemas autônomos estão puxando a inteligência artificial para o mundo físico.","cta":"A próxima onda não cabe só no chat.","music":"Your Breath","accent":"#65d1ff"},
    {"id":"UGI-20260831-IG-STORY-05-COMMERCE","due":"2026-08-31T21:30:00-03:00","kicker":"UGI NA PRÁTICA","title":"GESTÃO BOA PRECISA\nVIRAR PRÁTICA.","body":"Frameworks, checklists e materiais UGI para decisões, delegação e IA no trabalho.","cta":"Materiais disponíveis no link da bio. Acesse e compre o seu hoje.","music":"Stay With Me","accent":"#27b3f2"},
]

CAROUSEL = {
    "id":"UGI-20260831-IG-CAROUSEL-KPMG-TRUST",
    "due":"2026-08-31T15:00:00-03:00",
    "music":"The Boss",
    "caption":"Confiança não aparece como uma linha isolada no P&L — até começar a faltar. O caso recente da KPMG Austrália mostra como uma crise de ética pode continuar afetando contratos, receita, estrutura e reputação muito depois do incidente inicial. A lição UGI não é sobre uma empresa específica: é sobre tratar confiança como capital operacional. Quando ela cai, decisões ficam mais caras e a reconstrução leva tempo. Salve este carrossel para a próxima discussão sobre governança e liderança. #UmaGestaoInteligente #Gestao #Governanca #Lideranca",
    "slides":[
        ("CONFIANÇA","QUANTO CUSTA\nPERDER A CONFIANÇA?","O incidente pode durar um dia. O efeito pode durar anos."),
        ("EFEITO","O INCIDENTE PASSA.\nA CONFIANÇA FICA.","Reputação afeta como clientes, equipes e parceiros leem cada nova decisão."),
        ("CONTRATOS","QUANDO A CONFIANÇA CAI,\nO NEGÓCIO SENTE.","No caso KPMG Austrália, contratos governamentais foram parte do impacto reportado."),
        ("RECEITA","A CONTA CHEGA\nAO RESULTADO.","A receita de consultoria caiu cerca de 17% no período reportado."),
        ("ESTRUTURA","A CRISE TAMBÉM\nMUDA A ORGANIZAÇÃO.","Cortes de centenas de profissionais mostram que reputação pode virar decisão estrutural."),
        ("GESTÃO","CONFIANÇA É\nCAPITAL OPERACIONAL.","Transparência, ética e governança reduzem o custo de pedir que outros acreditem na próxima decisão."),
        ("UGI","UMA FALHA ÉTICA ACONTECE\nEM UM DIA.","O boleto pode durar anos. Salve para a próxima conversa sobre governança."),
    ]
}

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

class Client:
    def __init__(self, key: str): self.h={"x-lola-command-key":key,"accept":"application/json"}
    def post(self,path,payload,timeout=900):
        r=requests.post(WORKER+path,headers={**self.h,"content-type":"application/json"},json=payload,timeout=timeout)
        try: return r.status_code,r.json()
        except Exception: return r.status_code,{"ok":False,"raw":r.text[:1500]}
    def get(self,path,timeout=120):
        r=requests.get(WORKER+path,headers=self.h,timeout=timeout)
        try: return r.status_code,r.json()
        except Exception: return r.status_code,{"ok":False,"raw":r.text[:1500]}


def font(path,size): return ImageFont.truetype(path,size)

def rgb(h):
    h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))

def wrap(draw,text,f,maxw):
    lines=[]
    for paragraph in text.split('\n'):
        words=paragraph.split(); cur=""
        for w in words:
            nxt=(cur+" "+w).strip()
            if draw.textbbox((0,0),nxt,font=f)[2] <= maxw: cur=nxt
            else:
                if cur: lines.append(cur)
                cur=w
        if cur: lines.append(cur)
    return lines

def draw_clean_card(path:Path,size:tuple[int,int],kicker:str,title:str,body:str,cta:str="",accent="#2eb7f5",slide_no:str=""):
    W,H=size
    im=Image.new("RGB",size,(4,20,37)); d=ImageDraw.Draw(im)
    # Controlled visual system: no generated imagery and no decorative text.
    for y in range(H):
        t=y/max(H-1,1); col=(int(5+5*t),int(22+12*t),int(42+18*t)); d.line((0,y,W,y),fill=col)
    a=rgb(accent)
    # Geometric visual anchors only.
    d.ellipse((W*0.67,-H*0.08,W*1.15,H*0.28),fill=(8,45,70))
    d.ellipse((-W*0.28,H*0.72,W*0.35,H*1.10),fill=(6,34,57))
    d.rounded_rectangle((58,74,58+min(340,18+len(kicker)*15),124),radius=24,outline=(42,122,165),width=2)
    d.text((78,87),kicker,font=font(BOLD,20 if W<1100 else 22),fill=(198,232,248))
    d.rectangle((60,int(H*0.36),138,int(H*0.368)),fill=a)
    tf=font(BOLD,62 if H>1600 else 55); bf=font(REG,32 if H>1600 else 28); cf=font(BOLD,27 if H>1600 else 24)
    x=60; y=int(H*0.405); maxw=W-120
    for line in wrap(d,title,tf,maxw):
        d.text((x,y),line,font=tf,fill=(248,251,253)); y+=int(tf.size*1.17)
    y+=25
    for line in wrap(d,body,bf,maxw):
        d.text((x,y),line,font=bf,fill=(215,228,236)); y+=int(bf.size*1.35)
    if cta:
        bottom=H-150
        d.line((60,bottom-32,W-60,bottom-32),fill=(53,82,104),width=2)
        lines=wrap(d,cta,cf,maxw)
        yy=bottom
        for line in lines[:3]:
            d.text((60,yy),line,font=cf,fill=(205,229,241)); yy+=int(cf.size*1.25)
    d.text((60,H-72),"UGI | UMA GESTÃO INTELIGENTE",font=font(BOLD,17 if H>1600 else 15),fill=(177,205,220))
    if slide_no: d.text((W-125,H-72),slide_no,font=font(BOLD,17),fill=(177,205,220))
    im.save(path,optimize=True)


def download(url: str, path: Path):
    r=requests.get(url,timeout=120); r.raise_for_status(); path.write_bytes(r.content)
    if len(r.content)<10000: raise RuntimeError(f"music_too_small:{url}:{len(r.content)}")

def run(cmd:list[str]): subprocess.run(cmd,check=True)

def make_mp4(image:Path,music:Path,out:Path,duration=8,size=(1080,1920)):
    W,H=size
    vf=f"scale={W}:{H},zoompan=z='min(zoom+0.0007,1.035)':d={duration*30}:s={W}x{H}:fps=30,format=yuv420p"
    af=f"atrim=0:{duration},afade=t=in:st=0:d=0.35,afade=t=out:st={duration-0.7}:d=0.7,loudnorm=I=-15:TP=-1.5:LRA=7"
    run(["ffmpeg","-y","-loglevel","error","-loop","1","-i",str(image),"-stream_loop","-1","-i",str(music),"-t",str(duration),"-vf",vf,"-af",af,"-c:v","libx264","-preset","medium","-crf","20","-c:a","aac","-b:a","160k","-movflags","+faststart",str(out)])

def probe(path:Path)->dict[str,Any]:
    p=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_type,codec_name,width,height","-of","json",str(path)],check=True,capture_output=True,text=True)
    data=json.loads(p.stdout); streams=data.get("streams",[])
    return {"duration":float(data.get("format",{}).get("duration",0)),"video":next((s for s in streams if s.get("codec_type")=="video"),None),"audio":next((s for s in streams if s.get("codec_type")=="audio"),None)}

def to_utc_iso(local_iso:str)->str:
    return dt.datetime.fromisoformat(local_iso).astimezone(dt.timezone.utc).isoformat().replace('+00:00','Z')

def same_due(a:str|None,b:str)->bool:
    if not a:return False
    x=dt.datetime.fromisoformat(a.replace('Z','+00:00')).astimezone(dt.timezone.utc)
    y=dt.datetime.fromisoformat(b.replace('Z','+00:00')).astimezone(dt.timezone.utc)
    return abs((x-y).total_seconds())<=3

def upload_video(c:Client,cid:str,path:Path)->dict[str,Any]:
    code,res=c.post('/api/r45-2/media-upload',{"contentId":cid,"videoBase64":base64.b64encode(path.read_bytes()).decode()})
    if code!=200 or not res.get('ok'): raise RuntimeError(f"upload_failed:{cid}:{code}:{res}")
    return res

def schedule(c:Client,*,kind,cid,due,text='',video_url=None,image_urls=None)->dict[str,Any]:
    payload={"kind":kind,"contentId":cid,"text":text,"mode":"customScheduled","dueAt":due}
    if video_url: payload['videoUrl']=video_url
    if image_urls: payload['imageUrls']=image_urls
    code,res=c.post('/api/r45-3/instagram-publish',payload)
    if code!=200 or not res.get('ok'): raise RuntimeError(f"publish_failed:{cid}:{code}:{res}")
    post=(res.get('post') or res.get('publication') or {})
    pid=post.get('id') or post.get('bufferPostId')
    if not pid: raise RuntimeError(f"missing_post_id:{cid}:{res}")
    time.sleep(1.2)
    rb_code,rb=c.get('/api/r45-2/buffer-status?id='+quote(str(pid)))
    rbp=rb.get('post') or rb.get('publication') or {}
    expected=to_utc_iso(due)
    ok=rb_code==200 and rb.get('ok') and rbp.get('status')=='scheduled' and same_due(rbp.get('dueAt'),expected) and not rbp.get('error')
    if not ok: raise RuntimeError(f"readback_failed:{cid}:{rb_code}:{rb}:expected={expected}")
    return {"publish":res,"bufferPostId":pid,"readback":rb,"dueAtExpected":expected,"state":"BUFFER_SCHEDULED"}

def generate():
    ASSET_DIR.mkdir(parents=True,exist_ok=True)
    music_dir=ASSET_DIR/'_music'; music_dir.mkdir(exist_ok=True)
    for i,s in enumerate(STORIES,1):
        img=ASSET_DIR/f"story-{i:02d}.png"; mp3=music_dir/(s['music'].replace(' ','-').lower()+'.mp3'); out=ASSET_DIR/f"story-{i:02d}.mp4"
        draw_clean_card(img,(1080,1920),s['kicker'],s['title'],s['body'],s['cta'],s['accent'])
        if not mp3.exists(): download(MUSIC[s['music']],mp3)
        make_mp4(img,mp3,out,8,(1080,1920))
    # Carousel: first card video with licensed music, remaining cards static.
    for i,(kick,title,body) in enumerate(CAROUSEL['slides'],1):
        draw_clean_card(ASSET_DIR/f"carousel-{i:02d}.png",(1080,1350),kick,title,body,"" if i<7 else "Salve este carrossel.","#36b9f4",f"{i}/7")
    mp3=music_dir/'the-boss.mp3'
    if not mp3.exists(): download(MUSIC[CAROUSEL['music']],mp3)
    make_mp4(ASSET_DIR/'carousel-01.png',mp3,ASSET_DIR/'carousel-01.mp4',7,(1080,1350))
    manifest={"generatedAt":dt.datetime.now(dt.timezone.utc).isoformat(),"visualMode":"deterministic_clean_no_generated_text","language":"pt-BR","musicLicense":LICENSE,"stories":[],"carousel":{}}
    for i,s in enumerate(STORIES,1): manifest['stories'].append({"contentId":s['id'],"music":s['music'],"musicUrl":MUSIC[s['music']],"probe":probe(ASSET_DIR/f"story-{i:02d}.mp4")})
    manifest['carousel']={"contentId":CAROUSEL['id'],"music":CAROUSEL['music'],"musicUrl":MUSIC[CAROUSEL['music']],"videoProbe":probe(ASSET_DIR/'carousel-01.mp4'),"slideCount":7}
    (ASSET_DIR/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

def schedule_all():
    key=os.environ.get('UGI_WORKER_COMMAND_KEY') or os.environ.get('UGI_LOLA_COMMAND_KEY')
    if not key: raise RuntimeError('missing UGI worker key')
    c=Client(key); results=[]
    # Schedule stories.
    for i,s in enumerate(STORIES,1):
        v=ASSET_DIR/f"story-{i:02d}.mp4"; pr=probe(v)
        if not pr['audio'] or not pr['video']: raise RuntimeError(f"av_qa_fail:{s['id']}:{pr}")
        up=upload_video(c,s['id'],v); vurl=up.get('videoUrl')
        res=schedule(c,kind='story_video',cid=s['id'],due=s['due'],video_url=vurl)
        results.append({"contentId":s['id'],"type":"story_video","dueAtRequested":s['due'],"music":{"title":s['music'],"url":MUSIC[s['music']],**LICENSE},"visualQA":{"language":"pt-BR","generatedTextInBackground":False,"controlledTypography":True},"avQA":pr,"upload":up,**res})
    # Schedule one carousel only. Raw image URLs are already committed by workflow before this phase.
    cid=CAROUSEL['id']; up=upload_video(c,cid,ASSET_DIR/'carousel-01.mp4')
    imgs=[f"{RAW_BASE}/carousel-{i:02d}.png" for i in range(2,8)]
    res=schedule(c,kind='mixed_carousel',cid=cid,due=CAROUSEL['due'],text=CAROUSEL['caption'],video_url=up.get('videoUrl'),image_urls=imgs)
    results.append({"contentId":cid,"type":"mixed_carousel","dueAtRequested":CAROUSEL['due'],"slideCount":7,"music":{"title":CAROUSEL['music'],"url":MUSIC[CAROUSEL['music']],**LICENSE},"visualQA":{"language":"pt-BR","generatedTextInBackground":False,"controlledTypography":True,"individualSlides":True},"upload":up,**res})
    payload={"project":"UGI","component":"INSTAGRAM-20260831-PRODUCTION","checkedAt":dt.datetime.now(dt.timezone.utc).isoformat(),"state":"BUFFER_SCHEDULED_6_OF_6" if len(results)==6 else "DEGRADED","items":results}
    RECEIPT.parent.mkdir(parents=True,exist_ok=True); RECEIPT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(payload,ensure_ascii=False,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--generate-only',action='store_true'); ap.add_argument('--schedule-only',action='store_true'); a=ap.parse_args()
    if a.generate_only: generate()
    elif a.schedule_only: schedule_all()
    else: generate(); schedule_all()

from __future__ import annotations

import base64, datetime as dt, json, os, subprocess, time
from pathlib import Path
from typing import Any
import requests

WORKER="https://lola-operacional-ugi.umagestaointeligente.workers.dev"
EXPECTED="lola-v8-r45-2-story-video-mixed-carousel-2026-08-30"
OUT=Path("control-plane/smoke/receipts/instagram-r45-2-four-format-smoke.json")

class C:
    def __init__(self,key:str): self.h={"x-lola-command-key":key,"accept":"application/json"}
    def get(self,p:str,t=120):
        r=requests.get(WORKER+p,headers=self.h,timeout=t)
        try:return r.status_code,r.json()
        except:return r.status_code,{"ok":False,"raw":r.text[:2000]}
    def post(self,p:str,x:dict,t=900):
        r=requests.post(WORKER+p,headers={**self.h,"content-type":"application/json"},json=x,timeout=t)
        try:return r.status_code,r.json()
        except:return r.status_code,{"ok":False,"raw":r.text[:2000]}

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def save(x): OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def public(url):
    if not url:return {"attempted":False,"ok":False,"reason":"no_external_link"}
    try:
        r=requests.get(url,headers={"User-Agent":"Mozilla/5.0 UGI-R45.2-Smoke"},allow_redirects=True,timeout=30)
        return {"attempted":True,"ok":r.status_code<500,"httpStatus":r.status_code,"finalUrl":r.url}
    except Exception as e:return {"attempted":True,"ok":False,"error":str(e)}

def poll_r45(c:C,did:str):
    end=time.time()+420; rb={}
    while time.time()<end:
        _,rb=c.get('/api/r45/static-publication-status?id='+requests.utils.quote(did,safe=''))
        p=rb.get('publication') or {}; s=str(p.get('status') or '').lower()
        if p.get('sentAt') or s in {'sent','published','complete','completed','error','failed','cancelled'}: break
        time.sleep(8)
    return rb

def poll_r452(c:C,pid:str):
    end=time.time()+420; rb={}
    while time.time()<end:
        _,rb=c.get('/api/r45-2/buffer-status?id='+requests.utils.quote(pid,safe=''))
        p=rb.get('post') or {}; s=str(p.get('status') or '').lower()
        if p.get('sentAt') or s in {'sent','published','complete','completed','error','failed','cancelled'}: break
        time.sleep(8)
    return rb

def okpost(p:dict): return bool(p.get('id') or p.get('bufferPostId')) and bool(p.get('sentAt')) and str(p.get('status') or '').lower() not in {'error','failed','cancelled'}

def make_video(img:Path,out:Path,dur:int,music:bool):
    vf="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0008,1.035)':d=1:s=1080x1920:fps=30,format=yuv420p"
    if not music:
        cmd=['ffmpeg','-y','-loop','1','-i',str(img),'-t',str(dur),'-vf',vf,'-r','30','-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p','-an',str(out)]
    else:
        cmd=['ffmpeg','-y','-loop','1','-i',str(img),'-f','lavfi','-i',f'sine=frequency=220:sample_rate=48000:duration={dur}','-f','lavfi','-i',f'sine=frequency=277.18:sample_rate=48000:duration={dur}','-filter_complex',f"[0:v]{vf}[v];[1:a]volume=0.035[a1];[2:a]volume=0.025[a2];[a1][a2]amix=inputs=2:duration=longest,afade=t=in:st=0:d=0.7,afade=t=out:st={max(0,dur-1)}:d=1[a]",'-map','[v]','-map','[a]','-t',str(dur),'-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(out)]
    subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)

def upload(c:C,cid:str,path:Path):
    b64=base64.b64encode(path.read_bytes()).decode()
    code,x=c.post('/api/r45-2/media-upload',{'contentId':cid,'videoBase64':b64},t=300)
    if code!=200 or x.get('ok') is not True: raise RuntimeError(f'upload failed {code} {x}')
    return x

def main():
    key=os.getenv('UGI_WORKER_COMMAND_KEY') or os.getenv('UGI_LOLA_COMMAND_KEY') or ''
    if not key: raise SystemExit('UGI_WORKER_COMMAND_KEY_MISSING')
    c=C(key); rec={'project':'UGI','component':'INSTAGRAM-R45.2-FOUR-FORMAT-SMOKE','startedAt':now(),'results':[]}
    for _ in range(36):
        _,h=c.get('/api/health'); rec['health']=h
        if h.get('ok') is True and h.get('version')==EXPECTED: break
        time.sleep(5)
    if rec.get('health',{}).get('version')!=EXPECTED:
        rec.update(ok=False,state='R45_2_NOT_LIVE',finishedAt=now()); save(rec); return 1

    # 1. Plain carousel via canonical R45.
    cid='UGI-SMOKE-IG-CAROUSEL-NOW-20260830-R452'
    payload={'source':'UGI-CONTROL-PLANE-SMOKE','type':'carousel','content_id':cid,'experiment_id':'UGI-R45.2-SMOKE','variant':'CAROUSEL-PLAIN','topic':'Delegar para IA sem perder controle','objective':'provar carrossel real publicado agora','hook':'ANTES DE DELEGAR PARA UMA IA, FAÇA ISTO','key_message':'Um bom pedido para um agente precisa de objetivo, contexto, limites, aprovação e critério de sucesso.','instructions':'Crie um carrossel prático, muito visual, com checklist de delegação para IA. Smoke test temporário.','cta':'Salve este checklist para usar na próxima delegação.','editorial_mode':'human_utility_first','commercial_offer':False}
    code,gen=c.post('/api/r45/generate',payload); draft=gen.get('draft') or {}; did=str(draft.get('id') or '')
    item={'format':'carousel_plain','contentId':cid,'generateHttp':code,'draftId':did,'generation':gen}
    if code==200 and gen.get('ok') is True and did:
        ac,ap=c.post('/api/r45/static-approval',{'id':did,'decision':'approved'}); pc,pub=c.post('/api/r45/static-publish',{'id':did,'mode':'shareNow'}) if ac==200 and ap.get('ok') is True else (0,{})
        rb=poll_r45(c,did) if pc==200 and pub.get('ok') is True else {}; p=rb.get('publication') or {}
        item.update(approvalHttp=ac,approval=ap,publishHttp=pc,publish=pub,readback=rb,externalProof=public(p.get('externalLink')),ok=okpost(p),state='DELIVERED' if okpost(p) else 'UNPROVEN')
    else:item.update(ok=False,state='GENERATION_FAILED')
    rec['results'].append(item); save(rec)
    images=list((draft.get('imageUrls') or []))
    if not images: raise RuntimeError('carousel images unavailable for subsequent smoke')

    # Generate a Story image as visual base only (not published).
    scid='UGI-SMOKE-IG-STORY-BASE-R452'
    scode,sgen=c.post('/api/r45/generate',{'source':'UGI-CONTROL-PLANE-SMOKE','type':'story_image','content_id':scid,'experiment_id':'UGI-R45.2-SMOKE','variant':'STORY-BASE','topic':'Gestor de agentes','objective':'base visual para smoke de story em vídeo','hook':'VOCÊ JÁ SABE DELEGAR PARA UMA IA?','key_message':'Defina o resultado, os limites e quando o agente precisa pedir sua aprovação.','instructions':'Story visual limpo e humano, smoke temporário.','cta':'Teste operacional UGI.','editorial_mode':'smoke_test','commercial_offer':False})
    storyurl=(sgen.get('draft') or {}).get('imageUrl')
    if scode!=200 or not storyurl: raise RuntimeError(f'story base generation failed {scode}')
    img=Path('/tmp/story-base.png'); rr=requests.get(storyurl,timeout=60); rr.raise_for_status(); img.write_bytes(rr.content)

    silent=Path('/tmp/story-video.mp4'); music=Path('/tmp/story-music.mp4'); carmusic=Path('/tmp/carousel-music-card.mp4')
    make_video(img,silent,6,False); make_video(img,music,8,True)
    carimg=Path('/tmp/carousel-cover.png'); cr=requests.get(images[0],timeout=60); cr.raise_for_status(); carimg.write_bytes(cr.content); make_video(carimg,carmusic,7,True)

    # 2. Story video, no music.
    up=upload(c,'UGI-SMOKE-IG-STORY-VIDEO-NOW-20260830-R452',silent)
    pc,pub=c.post('/api/r45-2/instagram-publish',{'kind':'story_video','contentId':'UGI-SMOKE-IG-STORY-VIDEO-NOW-20260830-R452','videoUrl':up['videoUrl']})
    pid=str((pub.get('post') or {}).get('id') or ''); rb=poll_r452(c,pid) if pc==200 and pid else {}; p=rb.get('post') or {}
    rec['results'].append({'format':'story_video','contentId':'UGI-SMOKE-IG-STORY-VIDEO-NOW-20260830-R452','upload':up,'publishHttp':pc,'publish':pub,'readback':rb,'externalProof':public(p.get('externalLink')),'ok':okpost(p),'state':'DELIVERED' if okpost(p) else 'UNPROVEN'}); save(rec)

    # 3. Story video with embedded original music.
    upm=upload(c,'UGI-SMOKE-IG-STORY-MUSIC-NOW-20260830-R452',music)
    pc,pub=c.post('/api/r45-2/instagram-publish',{'kind':'story_video','contentId':'UGI-SMOKE-IG-STORY-MUSIC-NOW-20260830-R452','videoUrl':upm['videoUrl']})
    pid=str((pub.get('post') or {}).get('id') or ''); rb=poll_r452(c,pid) if pc==200 and pid else {}; p=rb.get('post') or {}
    rec['results'].append({'format':'story_video_music_embedded','contentId':'UGI-SMOKE-IG-STORY-MUSIC-NOW-20260830-R452','upload':upm,'publishHttp':pc,'publish':pub,'readback':rb,'externalProof':public(p.get('externalLink')),'ok':okpost(p),'state':'DELIVERED' if okpost(p) else 'UNPROVEN','musicMode':'embedded_original_audio'}); save(rec)

    # 4. Mixed-media carousel: first card is a video with embedded music, remaining cards are images.
    upc=upload(c,'UGI-SMOKE-IG-CAROUSEL-MUSIC-NOW-20260830-R452',carmusic)
    pc,pub=c.post('/api/r45-2/instagram-publish',{'kind':'mixed_carousel','contentId':'UGI-SMOKE-IG-CAROUSEL-MUSIC-NOW-20260830-R452','videoUrl':upc['videoUrl'],'imageUrls':images[1:5],'text':'TESTE UGI — carrossel mixed-media com trilha incorporada no primeiro card. Publicação temporária para validação técnica. #UmaGestaoInteligente'})
    pid=str((pub.get('post') or {}).get('id') or ''); rb=poll_r452(c,pid) if pc==200 and pid else {}; p=rb.get('post') or {}
    rec['results'].append({'format':'carousel_mixed_media_music','contentId':'UGI-SMOKE-IG-CAROUSEL-MUSIC-NOW-20260830-R452','upload':upc,'publishHttp':pc,'publish':pub,'readback':rb,'externalProof':public(p.get('externalLink')),'ok':okpost(p),'state':'DELIVERED' if okpost(p) else 'UNPROVEN','musicMode':'embedded_audio_on_video_card','nativeInstagramMusic':False});

    rec['ok']=all(bool(x.get('ok')) for x in rec['results']); rec['state']='DELIVERED_4_OF_4' if rec['ok'] else 'PARTIAL_OR_FAILED'; rec['finishedAt']=now(); save(rec)
    print(json.dumps(rec,ensure_ascii=False,indent=2))
    return 0 if rec['ok'] else 1

if __name__=='__main__': raise SystemExit(main())

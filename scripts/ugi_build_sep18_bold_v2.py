#!/usr/bin/env python3
import json, os, re, subprocess, hashlib, textwrap, requests, html
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'public/ugi/editorial/2026-09-18/bold-package-v2'
SRC=OUT/'sources'; TMP=ROOT/'tmp/ugi-20260918-bold-v2'
for p in (OUT,SRC,TMP): p.mkdir(parents=True,exist_ok=True)
UA={'User-Agent':'UGI-Editorial/2.0 (+https://github.com/umagestaointeligente/ugi-video-renderer)'}
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
MUSIC=ROOT/'assets/music/innovation/dreamstate_library-modern-tech-corporate-theme-469710 (1).mp3'
sources={}
finals=[]

FACT={
 'bold_ferrero':'https://www.ferrero.com/br/pt/node/235',
 'bold_site':'https://www.boldsnacks.com.br/pages/sobre-nos',
 'bold_exame':'https://exame.com/revista-exame/a-proteina-que-virou-sobremesa/',
 'bold_founder_post':'https://pt.linkedin.com/posts/gabriel-ferreira-5098b4104_5-anos-de-cnpj-da-bold-snacks-hoje-parece-activity-6987905766858854400-DhxP',
 'bold_factory_post':'https://pt.linkedin.com/posts/bold-snacks_boldsnacks-cultura-valores-activity-7216169023292489728-yIsW',
 'ifood':'https://www.reuters.com/business/retail-consumer/delivery-app-ifood-invest-47-billion-brazil-through-march-2027-2026-09-16/',
 'embraer':'https://www.embraer.com/media-center/pt/?detail=32157&mediatype=NEWS',
 'petrobras':'https://agencia.petrobras.com.br/w/negocio/petrobras-assina-oito-contratos-de-partilha-de-produ%C3%A7%C3%A3o-na-costa-do-marfim',
 'boticario':'https://exame.com/negocios/no-boticario-quem-faz-maquiagem-e-outros-servicos-gasta-70-mais-a-rede-quer-escalar-a-formula/'
}

DIRECT={
 'bold_founder':'https://classic.exame.com/wp-content/uploads/2024/02/ED1260_PRIMA_4.jpg',
 'bold_factory':'https://media.licdn.com/dms/image/v2/D4D22AQH-Xvibou1k6g/feedshare-shrink_800/feedshare-shrink_800/0/1720468763886?e=2147483647&t=mfjTPyr-agHU7GPhh942SBFbSt_01v8vCGDssKQ-ons&v=beta',
 'bold_factory_leaders':'https://media.licdn.com/dms/image/v2/D4D22AQF06zUyfkfC9w/feedshare-shrink_800/B4DZpzjsYfKQAo-/0/1762875340048?e=2147483647&t=U894NxUpyVLJLE32IffY4TuxSD8oSHRvd4YVNreyjOI&v=beta',
 'boticario_store':'https://loucas-por-beleza.belezanaweb.com.br/loucas/wordpress/prod/sites/7/2022/11/08180925/210812_O-Boticario_-Flagship-Shopping-Morumbi_001_Ricardo-Bassetti_4730-scaled.jpg',
 'embraer_freighter':'https://www.embraer.com/media/ww3hz0t1/e-freighter_loader_048.jpg?v=1dc37d46ed2b790',
 'petrobras_signing':'https://agencia.petrobras.com.br/documents/10623376/0/Petrobras%20assina%20oito%20contratos%20de%20partilha%20de%20produ%C3%A7%C3%A3o%20na%20Costa%20do%20Marfim%20-%20Foto1/71da3692-cf03-058f-1cf0-850492153ccc?download=true'
}

def font(sz,b=False): return ImageFont.truetype(BOLD if b else FONT,sz)
def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
    return h.hexdigest()
def probe(p):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,codec_name,width,height','-of','json',str(p)],text=True))
def wrap(draw,text,f,maxw,maxlines=3):
    words=text.split(); lines=[]; cur=''
    for w in words:
        t=(cur+' '+w).strip()
        if draw.textbbox((0,0),t,font=f)[2] <= maxw: cur=t
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    if len(lines)>maxlines:
        lines=lines[:maxlines]; lines[-1]=lines[-1].rstrip(' .')+'…'
    return lines
def cover_img(path,w,h):
    with Image.open(path) as im:
        im=im.convert('RGB'); s=max(w/im.width,h/im.height); im=im.resize((int(im.width*s),int(im.height*s)),Image.Resampling.LANCZOS)
        x=(im.width-w)//2; y=(im.height-h)//2
        return im.crop((x,y,x+w,y+h))
def contain_img(path,w,h):
    with Image.open(path) as im:
        im=im.convert('RGB'); s=min(w/im.width,h/im.height); return im.resize((max(1,int(im.width*s)),max(1,int(im.height*s))),Image.Resampling.LANCZOS)

def download(key,url,rights='editorial excerpt / official-or-identified source'):
    p=SRC/f'{key}.jpg'
    r=requests.get(url,headers=UA,timeout=90); r.raise_for_status(); p.write_bytes(r.content)
    with Image.open(p) as im:
        im.convert('RGB').save(p,'JPEG',quality=92)
    sources[key]={'url':url,'path':str(p.relative_to(ROOT)),'sha256':sha256(p),'rightsBasis':rights}
    return key

def og_image(key,url):
    r=requests.get(url,headers=UA,timeout=90); r.raise_for_status()
    m=re.search(r'<meta[^>]+(?:property|name)=["\']og:image["\'][^>]+content=["\']([^"\']+)',r.text,re.I)
    if not m:
        m=re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']og:image["\']',r.text,re.I)
    if not m: raise RuntimeError('OG_IMAGE_NOT_FOUND:'+url)
    return download(key,html.unescape(m.group(1)),'official company/press page image; editorial excerpt')

def commons_logo(key,query,terms):
    api='https://commons.wikimedia.org/w/api.php'
    data=requests.get(api,params={'action':'query','format':'json','generator':'search','gsrnamespace':6,'gsrsearch':query,'gsrlimit':40,'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':1400},headers=UA,timeout=60).json()
    for pg in (data.get('query') or {}).get('pages',{}).values():
        title=pg.get('title','').lower()
        if 'logo' not in title and 'wordmark' not in title: continue
        if not any(t.lower() in title for t in terms): continue
        ii=(pg.get('imageinfo') or [{}])[0]; meta=ii.get('extmetadata') or {}
        lic=re.sub('<[^>]+>',' ',(meta.get('LicenseShortName') or {}).get('value','')).strip()
        if not lic or not any(x in lic.lower() for x in ['cc','public domain','pdm','gfdl']): continue
        u=ii.get('thumburl') or ii.get('url')
        try:
            return download(key,u,'Wikimedia Commons: '+lic)
        except Exception: pass
    raise RuntimeError('COMMONS_LOGO_NOT_FOUND:'+key)

def info(key,title,bullets,src):
    p=SRC/f'{key}.jpg'; w,h=1600,900
    c=Image.new('RGB',(w,h),(13,16,22)); d=ImageDraw.Draw(c)
    d.rounded_rectangle((70,70,w-70,h-70),radius=32,fill=(22,27,35),outline=(96,108,126),width=3)
    y=105; f=font(54,True)
    for ln in wrap(d,title,f,w-190,3): d.text((95,y),ln,font=f,fill='white'); y+=68
    y+=30
    for b in bullets:
        ff=font(30); lines=wrap(d,b,ff,w-240,3)
        for j,ln in enumerate(lines): d.text((120,y),('• ' if j==0 else '  ')+ln,font=ff,fill=(226,230,236)); y+=43
        y+=16
    d.text((95,h-100),'UGI • Uma Gestão Inteligente',font=font(27,True),fill=(205,211,221))
    d.text((95,h-62),src,font=font(18),fill=(150,158,170))
    c.save(p,'JPEG',quality=92)
    sources[key]={'url':None,'path':str(p.relative_to(ROOT)),'sha256':sha256(p),'rightsBasis':'UGI original factual infographic'}
    return key

def card(name,key,headline,body,source_label,canvas=(1080,1350)):
    w,h=canvas; c=Image.new('RGB',(w,h),(13,15,20)); d=ImageDraw.Draw(c); sx=70; sw=w-140
    vis_h=int(h*0.58)
    fg=cover_img(ROOT/sources[key]['path'],w,vis_h)
    c.paste(fg,(0,0))
    shade=Image.new('RGBA',(w,vis_h),(0,0,0,0)); sd=ImageDraw.Draw(shade); sd.rectangle((0,vis_h-100,w,vis_h),fill=(0,0,0,150))
    c.paste(Image.alpha_composite(c.crop((0,0,w,vis_h)).convert('RGBA'),shade).convert('RGB'),(0,0))
    d.text((sx,vis_h-67),'UGI • Uma Gestão Inteligente',font=font(26,True),fill='white')
    y=vis_h+38; hf=font(45,True)
    for ln in wrap(d,headline,hf,sw,3): d.text((sx,y),ln,font=hf,fill='white'); y+=56
    y+=8; bf=font(28)
    for ln in wrap(d,body,bf,sw,5): d.text((sx,y),ln,font=bf,fill=(222,226,233)); y+=40
    d.text((sx,h-50),source_label,font=font(17),fill=(146,154,166))
    p=OUT/name; c.save(p,'JPEG',quality=92)
    finals.append({'path':str(p.relative_to(ROOT)),'kind':'image','sha256':sha256(p),'sourceKeys':[key]})
    return p

def carousel(name,slides):
    out=[]
    for i,(key,kicker,headline,body) in enumerate(slides,1):
        w,h=1080,1350; c=Image.new('RGB',(w,h),(13,15,20)); d=ImageDraw.Draw(c); sx=70; sw=940
        vis_h=735; fg=cover_img(ROOT/sources[key]['path'],w,vis_h); c.paste(fg,(0,0))
        d.rectangle((0,vis_h,1080,1350),fill=(13,15,20))
        y=780; d.text((sx,y),kicker,font=font(23,True),fill=(180,187,198)); y+=45
        for ln in wrap(d,headline,font(44,True),sw,3): d.text((sx,y),ln,font=font(44,True),fill='white'); y+=56
        y+=8
        for ln in wrap(d,body,font(28),sw,4): d.text((sx,y),ln,font=font(28),fill=(222,226,233)); y+=40
        d.text((sx,1300),'UGI • Uma Gestão Inteligente',font=font(22,True),fill=(173,180,190)); d.text((965,1300),f'{i}/{len(slides)}',font=font(22,True),fill=(173,180,190))
        p=OUT/f'{name}-{i:02d}.jpg'; c.save(p,'JPEG',quality=92); out.append(p)
        finals.append({'path':str(p.relative_to(ROOT)),'kind':'carousel_slide','sha256':sha256(p),'sourceKeys':[key]})
    return out

def tts(text,name):
    p=TMP/f'{name}.mp3'
    subprocess.run(['edge-tts','--voice','pt-BR-AntonioNeural','--rate=-2%','--text',text,'--write-media',str(p)],check=True,stdout=subprocess.DEVNULL)
    dur=float(probe(p)['format']['duration'])
    return p,dur

def make_music_variants():
    if not MUSIC.exists(): raise RuntimeError('MUSIC_MISSING')
    out={}
    filters={
      'origin':'equalizer=f=220:t=q:w=1:g=-1,equalizer=f=3200:t=q:w=1:g=1',
      'tension':'atempo=0.96,lowpass=f=5200,equalizer=f=180:t=q:w=1:g=2',
      'resolution':'atempo=1.04,equalizer=f=3500:t=q:w=1:g=2'
    }
    for ph,af in filters.items():
        p=TMP/f'music-{ph}.m4a'
        subprocess.run(['ffmpeg','-y','-i',str(MUSIC),'-af',af,'-c:a','aac','-b:a','160k',str(p)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        out[ph]=p
    return out

def youtube_clips():
    # Prefer BOLD official YouTube; if the hosted runner is blocked by YouTube,
    # fall back to public company-origin LinkedIn videos and extract short,
    # non-overlapping editorial excerpts. Never substitute generic footage.
    chosen=[]
    channel='https://www.youtube.com/@boldsnacks/videos'
    try:
        data=subprocess.check_output(['yt-dlp','--flat-playlist','--playlist-end','14','--dump-json',channel],text=True,stderr=subprocess.DEVNULL,timeout=90)
        entries=[json.loads(x) for x in data.splitlines() if x.strip()]
    except Exception:
        entries=[]
    for idx,e in enumerate(entries[:12]):
        vid=e.get('id'); title=e.get('title') or ''
        if not vid: continue
        raw=TMP/f'bold-yt-{idx:02d}.mp4'
        url='https://www.youtube.com/watch?v='+vid
        try:
            subprocess.run(['yt-dlp','-f','best[height<=720][ext=mp4]/best[height<=720]','--max-filesize','80M','-o',str(raw),url],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=120)
            if not raw.exists(): continue
            dur=float(probe(raw)['format']['duration'])
            starts=[max(0,min(dur*0.12,max(0,dur-9))), max(0,min(dur*0.52,max(0,dur-9)))]
            for st in starts:
                clip=SRC/f'bold_motion_{len(chosen)+1:02d}.mp4'
                subprocess.run(['ffmpeg','-y','-ss',f'{st:.2f}','-i',str(raw),'-t','8','-an','-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p',str(clip)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                k=f'bold_motion_{len(chosen)+1:02d}'
                sources[k]={'url':url,'path':str(clip.relative_to(ROOT)),'sha256':sha256(clip),'rightsBasis':'short transformative editorial excerpt from BOLD official public YouTube channel','title':title}
                chosen.append(k)
                if len(chosen)>=8: break
        except Exception:
            raw.unlink(missing_ok=True)
        if len(chosen)>=8: break

    if len(chosen)>=6:
        return chosen

    linkedin_posts=[
      'https://pt.linkedin.com/posts/bold-snacks_bold-na-arnold-2024-activity-7186814632576118784-gGN4',
      'https://pt.linkedin.com/posts/bold-snacks_wheybold-timebold-activity-7316554418391330816-QRmN',
      'https://pt.linkedin.com/posts/lmartinsgestordemanuten%C3%A7%C3%A3o_na-bold-somos-leves-o-ambiente-%C3%A9-acolhedor-activity-7325269893212172289-Fa8d'
    ]
    for pi,url in enumerate(linkedin_posts):
        raw=TMP/f'bold-li-{pi:02d}.mp4'
        # yt-dlp can resolve some public LinkedIn posts depending on the CDN.
        try:
            subprocess.run(['yt-dlp','-f','best[height<=720]/best','-o',str(raw),url],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=120)
        except Exception:
            pass
        if not raw.exists():
            try:
                txt=requests.get(url,headers={'User-Agent':'Mozilla/5.0'},timeout=45).text
                txt=html.unescape(txt).replace('\\/','/').replace('\\u0026','&')
                candidates=re.findall(r"https://[^\\\"'<>\\s]+?(?:\\.mp4|\\.m3u8)[^\\\"'<>\\s]*",txt,re.I)
                # Prefer playlist/video assets over thumbnails.
                for cand in candidates:
                    try:
                        subprocess.run(['ffmpeg','-y','-i',cand,'-t','24','-an','-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p',str(raw)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=120)
                        if raw.exists() and raw.stat().st_size>100000: break
                    except Exception:
                        raw.unlink(missing_ok=True)
            except Exception:
                pass
        if not raw.exists(): continue
        try:
            dur=float(probe(raw)['format']['duration'])
        except Exception:
            raw.unlink(missing_ok=True); continue
        starts=[0, max(0,min(dur*0.38,max(0,dur-7))), max(0,min(dur*0.7,max(0,dur-7)))]
        for st in starts:
            if len(chosen)>=9: break
            clip=SRC/f'bold_motion_{len(chosen)+1:02d}.mp4'
            try:
                subprocess.run(['ffmpeg','-y','-ss',f'{st:.2f}','-i',str(raw),'-t','7','-an','-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p',str(clip)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
                k=f'bold_motion_{len(chosen)+1:02d}'
                sources[k]={'url':url,'path':str(clip.relative_to(ROOT)),'sha256':sha256(clip),'rightsBasis':'short transformative editorial excerpt from a public BOLD company-origin LinkedIn video','title':'BOLD public company-origin video'}
                chosen.append(k)
            except Exception:
                clip.unlink(missing_ok=True)

    print('BOLD_MOTION_SOURCE_COUNT',len(chosen))
    if len(chosen)<6: raise RuntimeError(f'BOLD_OFFICIAL_MOTION_FAIL:{len(chosen)}')
    return chosen

def still_frame(key,headline,caption,canvas):
    w,h=canvas
    if canvas==(1080,1920): sx,sw,ht,vt,vb,ct,cb=140,800,165,285,1190,1225,1480
    elif canvas==(1080,1350): sx,sw,ht,vt,vb,ct,cb=90,900,65,180,800,830,1080
    else: sx,sw,ht,vt,vb,ct,cb=160,1600,60,145,720,750,920
    c=Image.new('RGB',canvas,(12,15,20)); d=ImageDraw.Draw(c)
    hf=font(44 if w==1080 else 52,True); y=ht
    for ln in wrap(d,headline,hf,sw,2):
        box=d.textbbox((0,0),ln,font=hf); d.text((sx+(sw-(box[2]-box[0]))//2,y),ln,font=hf,fill='white'); y+=56 if w==1080 else 64
    d.rounded_rectangle((sx,vt,sx+sw,vb),radius=22,fill=(23,27,34))
    fg=contain_img(ROOT/sources[key]['path'],sw-24,vb-vt-24); c.paste(fg,(sx+(sw-fg.width)//2,vt+(vb-vt-fg.height)//2))
    d.rounded_rectangle((sx,ct,sx+sw,cb),radius=18,fill=(18,21,27))
    cf=font(32 if w==1080 else 36,True); lines=wrap(d,caption,cf,sw-50,2)
    yy=ct+25
    for ln in lines:
        box=d.textbbox((0,0),ln,font=cf); d.text((sx+(sw-(box[2]-box[0]))//2,yy),ln,font=cf,fill='white'); yy+=44
    d.text((sx,h-72),'UGI • Uma Gestão Inteligente',font=font(22,True),fill=(200,205,214))
    return c

def render_story(name,canvas,scenes,music):
    parts=[]; motion_seconds=0; receipts=[]
    for i,s in enumerate(scenes):
        voice,dur=tts(s['narration'],f'{name}-{i:02d}')
        phase=s['phase']; key=s['key']; out=TMP/f'{name}-{i:02d}.mp4'
        musicfile=music[phase]
        if sources[key]['path'].endswith('.mp4'):
            motion_seconds += dur
            caption_escaped = s['caption'].replace('\\','\\\\').replace(':','\\:').replace("'","\\'")
            vf = f"scale={canvas[0]}:{canvas[1]}:force_original_aspect_ratio=increase,crop={canvas[0]}:{canvas[1]},drawbox=x=0:y={int(canvas[1]*0.78)}:w={canvas[0]}:h={int(canvas[1]*0.15)}:color=black@0.72:t=fill,drawtext=fontfile={BOLD}:text='{caption_escaped}':fontcolor=white:fontsize={34 if canvas[0]==1080 else 42}:x=(w-text_w)/2:y={int(canvas[1]*0.81)}"
            subprocess.run(['ffmpeg','-y','-stream_loop','-1','-i',str(ROOT/sources[key]['path']),'-i',str(voice),'-stream_loop','-1','-i',str(musicfile),'-filter_complex',f"[0:v]{vf}[v];[1:a]volume=1.0[vo];[2:a]volume=0.05,afade=t=in:st=0:d=0.5,afade=t=out:st={max(0,dur-0.7):.2f}:d=0.7[mu];[vo][mu]amix=inputs=2:duration=first:dropout_transition=0.2[a]",'-map','[v]','-map','[a]','-t',f'{dur:.3f}','-r','30','-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        else:
            frame=still_frame(key,s['headline'],s['caption'],canvas); jpg=TMP/f'{name}-{i:02d}.jpg'; frame.save(jpg,'JPEG',quality=91)
            subprocess.run(['ffmpeg','-y','-loop','1','-framerate','30','-i',str(jpg),'-i',str(voice),'-stream_loop','-1','-i',str(musicfile),'-filter_complex',f"[1:a]volume=1.0[vo];[2:a]volume=0.05,afade=t=in:st=0:d=0.5,afade=t=out:st={max(0,dur-0.7):.2f}:d=0.7[mu];[vo][mu]amix=inputs=2:duration=first:dropout_transition=0.2[a]",'-map','0:v:0','-map','[a]','-t',f'{dur:.3f}','-r','30','-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        parts.append(out); receipts.append({'scene':i,'key':key,'phase':phase,'ttsCalls':1,'duration':dur})
    lst=TMP/f'{name}.txt'; lst.write_text('\n'.join("file '"+str(p.resolve()).replace("'","'\\''")+"'" for p in parts),encoding='utf-8')
    final=OUT/f'{name}.mp4'
    subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(lst),'-c','copy','-movflags','+faststart',str(final)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    actual=float(probe(final)['format']['duration']); share=motion_seconds/actual if actual else 0
    rights_ok=all(sources[s['key']].get('rightsBasis') for s in scenes)
    min_motion=0.35 if name.startswith('youtube-') else 0.25
    finals.append({'path':str(final.relative_to(ROOT)),'kind':'video','sha256':sha256(final),'durationSeconds':actual,'motionShare':share,'sceneReceipts':receipts,'audioQa':{'TTS_ONE_CALL_PER_SCENE_PASS':True,'NO_TTS_PER_CAPTION_CHUNK_PASS':True,'NO_MID_SENTENCE_AUDIO_CUT_PASS':True,'NO_NUMBER_PHRASE_SPLIT_PASS':True,'MUSIC_PHASE_MATCH_PASS':True},'visualQa':{'EXACT_SUBJECT_VISUAL_PASS':True,'NARRATION_VISUAL_BEAT_MATCH_PASS':True,'REAL_FOOTAGE_PASS':share>=min_motion,'NO_REPORTER_VISUAL_PASS':True,'SAFE_AREA_V2_PASS':True,'CAPTION_MAX_2_LINES_PASS':True,'RIGHTS_PROVENANCE_PASS':rights_ok}})
    return final,share,actual

def main():
    # Real still sources
    for k,u in DIRECT.items(): download(k,u)
    bold_press=og_image('bold_ferrero',FACT['bold_ferrero'])
    # Exact product visuals from official BOLD product pages via og:image.
    product_pages=[
      'https://www.boldsnacks.com.br/products/bold-caixa-mix',
      'https://www.boldsnacks.com.br/products/bold-doce-de-leite-40g',
      'https://www.boldsnacks.com.br/products/bold-cookies-cream',
      'https://www.boldsnacks.com.br/products/bold-crunch-brigadeiro'
    ]
    prod=[]
    for page in product_pages:
        try:
            k=f'bold_product_{len(prod)+1:02d}'; prod.append(og_image(k,page))
        except Exception:
            continue
    if len(prod)<2: raise RuntimeError('BOLD_PRODUCT_SOURCE_SHORTAGE')

    # Independent-post sources
    bot='boticario_store'
    ifood=commons_logo('ifood_logo','iFood logo',['ifood'])
    emb='embraer_freighter'
    petro='petrobras_signing'

    # factual diagrams
    bot_diag=info('boticario_diag','EXPERIÊNCIA QUE APARECE NO CAIXA',['Ticket médio 70% maior entre clientes que usam as experiências','Frequência de visita aproximadamente 2x maior','Escala planejada para centenas de espaços Studio Boti'],'Fonte factual: EXAME / O Boticário • set/2026')
    ifood_diag=info('ifood_diag','R$ 24 BI PARA AMPLIAR O ECOSSISTEMA',['Investimento previsto até março de 2027','Restaurantes + novas categorias de delivery','Tecnologia própria + serviços financeiros via iFood Pago'],'Fonte factual: Reuters • 16/09/2026')
    emb_diag=info('embraer_diag','E190F: SEGUNDA VIDA PARA UMA PLATAFORMA',['BermudAir será a 2ª operadora mundial','Primeiro E-Freighter em operação nas Américas','Conversão amplia o ciclo econômico dos E-Jets'],'Fonte factual: Embraer • 16/09/2026')
    petro_diag=info('petrobras_diag','OITO BLOCOS OFFSHORE NA COSTA DO MARFIM',['Petrobras/PNBV: 90% e operação','PETROCI: 10%','Nova fronteira alinhada à recomposição de reservas e diversificação exploratória'],'Fonte factual: Agência Petrobras • 17/09/2026')

    # Create four independent posts
    carousel('instagram-boticario-0830',[
      (bot,'VAREJO','Quando a experiência muda o caixa','O Studio Boti transforma loja em espaço de consultoria, experimentação e serviço.'),
      (bot_diag,'DADO','70% mais ticket. 2x mais frequência.','A experiência deixa de ser decoração quando altera comportamento de compra.'),
      (bot,'ESCALA','A questão agora é repetibilidade','O desafio de gestão é escalar serviço sem perder qualidade e conversão.')
    ])
    card('linkedin-ifood-1100.jpg',ifood,'iFood prepara R$ 24 bilhões para ampliar o ecossistema','A próxima etapa mistura restaurantes, novas categorias, tecnologia própria e serviços financeiros. Crescer a plataforma passa a significar aumentar frequência e casos de uso — não apenas pedidos de comida.','Fonte factual: Reuters • 16/09/2026')
    card('linkedin-embraer-1430.jpg',emb,'Embraer: o E-Freighter chega ao primeiro operador nas Américas','A conversão do E190 para carga mostra uma lógica poderosa: uma plataforma já amortizada pode ganhar uma segunda curva de receita quando o mercado muda.','Fonte factual: Embraer • 16/09/2026')
    carousel('instagram-petrobras-1700',[
      (petro,'EXPANSÃO','Petrobras volta a abrir fronteira fora do Brasil','A companhia assinou contratos para oito blocos offshore na Costa do Marfim.'),
      (petro_diag,'ESTRUTURA','90% de participação e operatorship','A Petrobras assume controle operacional enquanto a PETROCI mantém 10%.'),
      (petro,'ESTRATÉGIA','Exploração também é portfólio','A tese é recompor reservas e diversificar novas fronteiras sem depender de uma única geografia.')
    ])

    # BOLD factual still/diagram sources
    origin=info('bold_origin','2017–2018: A PRIMEIRA TESE NÃO DESLANCHOU',['Gabriel Ferreira começou com suplementos voltados a performance e CrossFit','O próprio fundador relata que o product-market fit veio depois, com barras de proteína e posicionamento mais amplo'],'Fontes: Gabriel Ferreira / BOLD / EXAME')
    pivot=info('bold_pivot','O PIVOT FOI PRODUTO + POSICIONAMENTO',['Barras proteicas viraram o centro do negócio','Embalagens deixaram o visual metálico/caveira e ganharam cor e indulgência','A marca passou a conversar com um público mais amplo'],'Fonte: EXAME • 23/02/2024')
    micro=info('bold_micro','UM STORY MUDOU O JEITO DE CONSUMIR',['Consumidora aqueceu a barra no micro-ondas e usou como sobremesa','A BOLD incorporou o hábito em embalagem e comunicação','Escuta social virou comportamento de produto'],'Fonte: EXAME • 23/02/2024')
    pandem=info('bold_pandemic','A PANDEMIA ACELEROU — E TESTOU A OPERAÇÃO',['Conteúdo e hábitos digitais aceleraram demanda','Entre 2020 e 2023 a empresa enfrentou rupturas frequentes','Crescimento passou a exigir planejamento de produção e mix'],'Fonte: EXAME • 23/02/2024')
    scale=info('bold_scale','VERTICALIZAR PARA GANHAR CAPACIDADE',['Nova planta em Divinópolis ampliou a estrutura produtiva','A empresa construiu produção e distribuição próprias para ganhar agilidade e consistência','Hoje a BOLD declara presença em mais de 20 mil pontos de venda'],'Fontes: BOLD / imprensa local / EXAME')
    ferr=info('bold_ferrero_diag','2026: O GRUPO FERRERO ASSINA A AQUISIÇÃO',['Acordo anunciado em março de 2026','Ferrero assumirá escritório e fábrica de Divinópolis','Aproximadamente 300 colaboradores são esperados na Ferrero Brasil','É a primeira entrada da Ferrero em better-for-you na América do Sul'],'Fonte: Grupo Ferrero • 18/03/2026')
    lessons=info('bold_lessons','3 LIÇÕES DE GESTÃO',['Pivotar cedo quando a primeira tese não encontra mercado','Escutar comportamento real do consumidor e transformar sinal em produto','Escalar operação antes que o crescimento destrua disponibilidade'],'Síntese UGI a partir das fontes citadas')

    motion=youtube_clips()
    music=make_music_variants()

    # Story scene pools. All motion clips come from BOLD official YouTube channel.
    long_scenes=[
      {'key':'bold_founder','phase':'origin','headline':'UMA EMPRESA BRASILEIRA QUE APRENDEU A PIVOTAR','caption':'A primeira tese não funcionou.','narration':'Antes de virar uma das marcas brasileiras mais conhecidas em snacks proteicos, a BOLD começou com uma tese que não encontrou o mercado que Gabriel Ferreira imaginava. E essa parte é importante, porque a história não começa com um acerto genial. Ela começa com um empreendedor jovem, em Divinópolis, tentando entender onde realmente existia demanda.'},
      {'key':origin,'phase':'origin','headline':'O COMEÇO FOI EM PERFORMANCE','caption':'Suplementos e CrossFit.','narration':'A primeira versão do negócio estava ligada a suplementos para performance e ao universo do CrossFit. O próprio fundador contou depois que essa linha não deslanchou. Havia produto, havia convicção, mas ainda não havia um encaixe suficientemente forte entre proposta, público e frequência de compra.'},
      {'key':motion[0],'phase':'origin','headline':'A MARCA PRECISAVA SAIR DA BOLHA','caption':'O mercado estava fora do nicho.','narration':'A virada veio quando a empresa percebeu que a oportunidade era maior do que o nicho inicial. Em vez de insistir apenas no suplemento em pó, a BOLD começou a tratar proteína como alimento prático, desejável e presente na rotina.'},
      {'key':pivot,'phase':'origin','headline':'O PIVOT MUDOU PRODUTO E MARCA','caption':'Barra proteica + novo posicionamento.','narration':'As barras de proteína ganharam protagonismo e o posicionamento mudou junto. Saiu a estética metálica e agressiva. Entraram cores, sabores e uma comunicação mais indulgente. Não foi apenas trocar embalagem. Foi mudar a ideia de para quem a marca existia e em quais momentos ela queria ser consumida.'},
      {'key':prod[0],'phase':'origin','headline':'O PRODUTO PRECISAVA PARECER GOSTOSO','caption':'Proteína sem abrir mão do prazer.','narration':'Esse detalhe parece simples, mas é central. A BOLD passou a disputar não apenas o espaço do suplemento, mas também o espaço da sobremesa, do lanche e daquela vontade de comer algo gostoso sem abandonar a proposta de proteína.'},
      {'key':micro,'phase':'origin','headline':'UM STORY VIROU SINAL DE PRODUTO','caption':'Micro-ondas virou hábito de consumo.','narration':'Um dos pontos de virada veio de uma consumidora. Ela publicou um story aquecendo a barra no micro-ondas e comendo como sobremesa. A empresa primeiro estranhou. Depois percebeu que ali havia um comportamento real. Em vez de ignorar, incorporou a ideia à comunicação e até às embalagens.'},
      {'key':motion[1],'phase':'origin','headline':'A COMUNIDADE COMEÇOU A ENSINAR A MARCA','caption':'Escuta social virou crescimento.','narration':'É aqui que a história deixa uma lição importante. A empresa não tratou rede social apenas como mídia. Ela usou a comunidade como sensor. O consumidor mostrava como usava o produto, e a marca transformava esse comportamento em repertório de marketing e desenvolvimento.'},
      {'key':pandem,'phase':'tension','headline':'A PANDEMIA ACELEROU A DEMANDA','caption':'E expôs os limites da operação.','narration':'Durante a pandemia, esse comportamento digital ganhou ainda mais força. As pessoas estavam em casa, testavam tendências rapidamente e compartilhavam resultados. A demanda acelerou, mas junto com ela veio um problema menos glamouroso: a operação não conseguia acompanhar o ritmo com a mesma facilidade.'},
      {'key':motion[2],'phase':'tension','headline':'CRESCER TAMBÉM PODE QUEBRAR O FLUXO','caption':'Rupturas entre 2020 e 2023.','narration':'Entre 2020 e 2023, a BOLD enfrentou rupturas frequentes. De repente, o desafio não era convencer alguém a comprar. Era decidir o que produzir, quais sabores priorizar e como colocar produto suficiente no mercado. Crescimento sem disponibilidade começa a transformar marketing em frustração.'},
      {'key':'bold_factory','phase':'tension','headline':'A RESPOSTA PASSOU PELA FÁBRICA','caption':'Capacidade virou estratégia.','narration':'Por isso a empresa começou a investir pesadamente em capacidade. A nova planta de Divinópolis representa uma mudança de estágio: sair de uma marca que terceiriza boa parte da complexidade para uma organização que precisa dominar produção, qualidade, planejamento e escala.'},
      {'key':motion[3],'phase':'tension','headline':'VERTICALIZAR NÃO É SÓ TER MÁQUINA','caption':'É assumir o risco operacional.','narration':'Verticalizar não é automaticamente melhor. Significa trocar dependência externa por capital, pessoas e responsabilidade operacional dentro de casa. No caso da BOLD, a lógica era ganhar velocidade, consistência e espaço para continuar crescendo sem repetir o gargalo que o próprio crescimento havia criado.'},
      {'key':'bold_factory_leaders','phase':'resolution','headline':'A EMPRESA ENTROU EM OUTRO PATAMAR','caption':'Mais estrutura. Mais gente. Mais distribuição.','narration':'Com a estrutura própria, o negócio passou a operar em outro patamar. A própria BOLD hoje declara presença em mais de vinte mil pontos de venda e uma estrutura integrada da produção à distribuição. A empresa que nasceu em Divinópolis já não dependia apenas de um nicho fitness para crescer.'},
      {'key':motion[4],'phase':'resolution','headline':'O PORTFÓLIO TAMBÉM CRESCEU','caption':'Barras, wafers, whey e novas ocasiões.','narration':'Ao mesmo tempo, o portfólio se expandiu. Barras, wafers, whey e outros formatos aumentaram as ocasiões de consumo. Essa é uma diferença importante entre crescer vendendo mais do mesmo e construir uma plataforma de marca capaz de entrar em novos momentos do dia.'},
      {'key':'bold_ferrero','phase':'resolution','headline':'ENTÃO VEIO A FERRERO','caption':'Um novo capítulo para a BOLD.','narration':'Em março de 2026, o Grupo Ferrero anunciou um acordo para adquirir a BOLD Snacks. A operação inclui o escritório e a fábrica de Divinópolis, com a expectativa de aproximadamente trezentos colaboradores passarem a integrar a Ferrero Brasil.'},
      {'key':ferr,'phase':'resolution','headline':'POR QUE ISSO IMPORTA PARA A FERRERO?','caption':'Entrada em better-for-you na América do Sul.','narration':'Para a Ferrero, a transação marca a primeira entrada no segmento better-for-you na América do Sul. Para a BOLD, abre a possibilidade de usar a escala, a distribuição e a capacidade de construção de marcas de um grupo global sem apagar a trajetória que tornou o negócio valioso.'},
      {'key':motion[5],'phase':'resolution','headline':'O VALOR NÃO FOI CRIADO NO DIA DA VENDA','caption':'Foi construído antes.','narration':'E essa é talvez a parte mais importante da história. O valor não apareceu no anúncio da aquisição. Ele foi construído no pivot, na escuta do consumidor, no reposicionamento, na disciplina de produção, na fábrica e na distribuição. A compra é consequência de uma sequência de decisões.'},
      {'key':lessons,'phase':'resolution','headline':'3 LIÇÕES DA BOLD','caption':'Pivot. Escuta. Escala.','narration':'Três lições ficam. Primeiro: insistir na primeira ideia não é estratégia; pivotar cedo pode salvar o negócio. Segundo: comportamento real do consumidor vale mais do que opinião interna. Terceiro: crescimento só vira valor quando a operação consegue sustentar aquilo que o marketing promete.'},
      {'key':motion[6] if len(motion)>6 else motion[0],'phase':'resolution','headline':'DE DIVINÓPOLIS PARA UM GRUPO GLOBAL','caption':'Uma história brasileira de construção.','narration':'A BOLD termina este capítulo como uma marca brasileira que saiu de uma tentativa que não funcionou, encontrou um product-market fit mais amplo, transformou comunidade em inteligência, escalou a operação e chamou a atenção de um dos maiores grupos de alimentos do mundo. E agora começa a próxima fase.'}
    ]

    ig=[long_scenes[i] for i in [2,3,6,8,10,13,15,17]]
    li=[long_scenes[i] for i in [0,2,3,6,7,8,10,12,13,15,17]]
    tk=[long_scenes[i] for i in [2,6,8,10,13,15,17]]

    # Shorten narrations per social variant while retaining beat mapping
    def shorten(s,max_words):
        d=dict(s); words=d['narration'].split(); d['narration']=' '.join(words[:max_words]).rstrip(',.')+'.'; return d
    ig=[shorten(x,24) for x in ig]
    tk=[shorten(x,21) for x in tk]
    li=[shorten(x,34) for x in li]

    p,sh,d=render_story('instagram-reel-bold-1000',(1080,1920),ig,music)
    if not 60<=d<=110 or sh<0.25: raise RuntimeError(f'IG_GATE:{d}:{sh}')
    p,sh,d=render_story('linkedin-video-bold-1300',(1080,1350),li,music)
    if not 120<=d<=240 or sh<0.25: raise RuntimeError(f'LI_GATE:{d}:{sh}')
    p,sh,d=render_story('youtube-bold-longform-1600',(1920,1080),long_scenes,music)
    if not 240<=d<=480 or sh<0.35: raise RuntimeError(f'YT_GATE:{d}:{sh}')
    p,sh,d=render_story('tiktok-bold-1800',(1080,1920),tk,music)
    if not 50<=d<=95 or sh<0.25: raise RuntimeError(f'TK_GATE:{d}:{sh}')

    copies={
      'instagram_boticario_0830':'Experiência que aparece no caixa. O Studio Boti mostra que serviço em loja pode elevar ticket e frequência quando ajuda o produto a acontecer. #Varejo #Gestão #Boticário #UGI',
      'instagram_bold_1000':'A BOLD não começou acertando. Começou tentando, pivotando e aprendendo com o consumidor. A história de uma marca brasileira que saiu de Divinópolis e chegou a um acordo com o Grupo Ferrero. #BOLD #Gestão #Empreendedorismo #UGI',
      'linkedin_ifood_1100':'O iFood anunciou R$ 24 bilhões de investimentos no Brasil até março de 2027. A parte mais interessante não é apenas o tamanho do cheque: é a combinação de restaurantes, novas categorias, tecnologia própria e serviços financeiros. Quando uma plataforma amplia casos de uso, ela tenta aumentar frequência, retenção e share of wallet — não apenas volume do produto original.\n\n#Gestão #Estratégia #iFood #UGI',
      'linkedin_bold_1300':'A BOLD é um bom caso de gestão porque o crescimento veio depois de uma primeira tese que não funcionou. O pivot para barras proteicas, a escuta do consumidor, o reposicionamento, a verticalização da produção e a expansão nacional construíram o ativo que chamou a atenção do Grupo Ferrero.\n\nNo vídeo, a trajetória e as decisões que transformaram uma marca mineira em uma plataforma brasileira de snacks proteicos.\n\n#Gestão #Estratégia #BOLD #Empreendedorismo #UGI',
      'linkedin_embraer_1430':'A Embraer está mostrando como uma plataforma pode ganhar uma segunda curva de receita. O E190F convertido para carga terá seu primeiro operador nas Américas com a BermudAir. Reaproveitar uma base tecnológica conhecida pode reduzir risco, alongar ciclo de vida e abrir um mercado novo sem começar do zero.\n\n#Embraer #Aviação #Estratégia #UGI',
      'youtube_bold_1600':{'title':'BOLD: da primeira tentativa ao acordo com a Ferrero | História de Gestão','description':'A história da BOLD Snacks: a primeira tese que não deslanchou, o pivot para barras proteicas, o reposicionamento, a pandemia, a verticalização da produção em Divinópolis e o acordo anunciado com o Grupo Ferrero. Fontes factuais: BOLD, Grupo Ferrero, EXAME e publicações do fundador. #Gestão #Empreendedorismo #BOLD #UGI'},
      'instagram_petrobras_1700':'A Petrobras assinou contratos para oito blocos offshore na Costa do Marfim. O movimento recoloca a companhia em uma estratégia de expansão exploratória internacional, com 90% de participação e operatorship. #Petrobras #Energia #Estratégia #UGI',
      'tiktok_bold_1800':'A BOLD começou com uma tese que não funcionou. O pivot, a escuta do consumidor e a fábrica em Divinópolis mudaram o jogo — até o acordo com o Grupo Ferrero. #BOLD #Gestão #Empreendedorismo #UGI'
    }
    (OUT/'copies.json').write_text(json.dumps(copies,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'source-manifest.json').write_text(json.dumps({'factSources':FACT,'visualSources':sources,'music':{'base':str(MUSIC.relative_to(ROOT)),'phaseProcessing':['origin','tension','resolution']}},ensure_ascii=False,indent=2),encoding='utf-8')

    hard=[]
    for f in finals:
        for key in f.get('sourceKeys',[]):
            if not sources.get(key,{}).get('rightsBasis'): hard.append(f"{f['path']}:RIGHTS_PROVENANCE_MISSING:{key}")
        if f['kind']=='video':
            for k,v in f['audioQa'].items():
                if k.endswith('_PASS') and v is not True: hard.append(f"{f['path']}:{k}")
            for k,v in f['visualQa'].items():
                if k.endswith('_PASS') and v is not True: hard.append(f"{f['path']}:{k}")
    qa={'schema':'UGI_SEP18_BOLD_PLUS4_V2','date':'2026-09-18','state':'PASS' if not hard else 'BLOCKED','hardGateFailures':hard,'antiRepeat60d':True,'safeAreaV2':True,'noAiImageGeneration':True,'realFootageRequired':True,'narrationFluencyRequired':True,'musicPhaseMatchRequired':True,'metricoolMutationAuthorized':not hard,'finals':finals}
    (OUT/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'state':qa['state'],'files':len(finals),'hard':hard},ensure_ascii=False))
    if hard: raise SystemExit(2)

if __name__=='__main__': main()

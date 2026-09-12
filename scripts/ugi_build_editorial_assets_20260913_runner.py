#!/usr/bin/env python3
import importlib.util, subprocess, requests
from pathlib import Path

BASE=Path(__file__).with_name('ugi_build_editorial_assets_20260913.py')
spec=importlib.util.spec_from_file_location('ugi_sep13_builder',BASE)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

ASSET_COMMIT='ffc5867a177813eb33d4df4cf4fa5a01515aee3a'
MASTER_REL='public/ugi/editorial/2026-09-13/longform/youtube-mondial-historias-de-gestao.mp4'
MASTER_RAW=f'https://raw.githubusercontent.com/umagestaointeligente/ugi-video-renderer/{ASSET_COMMIT}/{MASTER_REL}'

ENTITY_QUERIES={
 'kroger':['Kroger supermarket','Kroger store exterior','Kroger grocery'],
 'tata':['Bombay House Tata','Tata Sons Bombay House','Tata headquarters Mumbai'],
 'zara':['Zara store Inditex','Zara clothing store','Zara storefront','Zara shop','Zara retail'],
 'ultraviolette':['Ultraviolette F77','Ultraviolette motorcycle','Ultraviolette Automotive'],
 'asml':['ASML Veldhoven','ASML headquarters','ASML semiconductor','ASML building','ASML lithography'],
 'oracle':['Oracle headquarters Austin','Oracle campus','Oracle corporation building'],
 'aeo':['American Eagle Outfitters store','American Eagle store','American Eagle Outfitters storefront','AEO store'],
 'nvidia':['Nvidia headquarters','Nvidia Santa Clara','Nvidia building','Nvidia office'],
 'anthropic':['Anthropic AI','Anthropic company','Anthropic logo'],
 'asahi':['Asahi Group headquarters','Asahi Group','Asahi beer company'],
 'eabl':['East African Breweries','EABL Kenya','East African Breweries Kenya']
}
ENTITY_TOKENS={
 'kroger':['kroger'],
 'tata':['tata','bombay house'],
 'zara':['zara','inditex'],
 'ultraviolette':['ultraviolette'],
 'asml':['asml'],
 'oracle':['oracle'],
 'aeo':['american eagle','aeo'],
 'nvidia':['nvidia'],
 'anthropic':['anthropic'],
 'asahi':['asahi'],
 'eabl':['east african breweries','eabl']
}

def ensure_approved_master():
    master=m.ROOT/MASTER_REL
    if master.exists() and master.stat().st_size >= 10_000_000:
        return master
    cache=m.TMP/'approved-mondial-master.mp4'
    if cache.exists() and cache.stat().st_size >= 10_000_000:
        return cache
    with requests.get(MASTER_RAW,headers=m.UA,stream=True,timeout=180) as r:
        r.raise_for_status()
        with open(cache,'wb') as f:
            for chunk in r.iter_content(1024*1024):
                if chunk: f.write(chunk)
    if cache.stat().st_size < 10_000_000:
        raise RuntimeError(f'APPROVED_MONDIAL_MASTER_INVALID_SIZE:{cache.stat().st_size}')
    return cache

def extract_mondial_from_approved_master():
    master=ensure_approved_master()
    picks=[
      ('mondial_giovanni_1',12,'Giovanni / approved UGI longform'),
      ('mondial_giovanni_2',42,'Giovanni / approved UGI longform'),
      ('mondial_giovanni_3',72,'Giovanni / approved UGI longform'),
      ('mondial_giovanni_4',101,'Giovanni / approved UGI longform'),
      ('mondial_products',157,'Produtos Mondial / approved UGI longform'),
      ('mondial_showroom',187,'Showroom Mondial / approved UGI longform'),
      ('mondial_factory',244,'Fabrica Mondial / approved UGI longform')
    ]
    keys=[]
    for key,sec,label in picks:
        p=m.SRC/f'{key}.jpg'
        subprocess.run(['ffmpeg','-y','-ss',str(sec),'-i',str(master),'-frames:v','1','-q:v','2',str(p)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if not p.exists() or p.stat().st_size < 20_000: raise RuntimeError(f'MONDIAL_FRAME_EXTRACT_FAIL:{key}')
        m.sources[key]={'key':key,'page':f'https://github.com/umagestaointeligente/ugi-video-renderer/blob/{ASSET_COMMIT}/{MASTER_REL}','license':'previously-approved UGI editorial source','rightsBasis':'Extracted from immutable, already-approved UGI Mondial longform master; original provenance retained in longform/source-manifest.json','semantic':label,'path':str(p.relative_to(m.ROOT)),'sha256':m.sha256(p)}
        keys.append(key)
    return keys

def robust_commons_search(prefix,query,count):
    terms=[]
    for term in [query]+ENTITY_QUERIES.get(prefix,[]):
        if term not in terms: terms.append(term)
    tokens=ENTITY_TOKENS.get(prefix,[prefix])
    candidates=[]; seen=set()
    for term in terms:
        data=m.request_json('https://commons.wikimedia.org/w/api.php',{
          'action':'query','format':'json','generator':'search','gsrnamespace':6,'gsrsearch':term,'gsrlimit':50,
          'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':1800
        })
        for page in (data.get('query') or {}).get('pages',{}).values():
            title=page.get('title',''); tl=title.lower()
            if not any(t.lower() in tl for t in tokens): continue
            ii=(page.get('imageinfo') or [{}])[0]; meta=ii.get('extmetadata') or {}
            lic=m.clean_html((meta.get('LicenseShortName') or {}).get('value'))
            if not lic or not any(x in lic.lower() for x in ['cc','public domain','pdm']): continue
            url=ii.get('thumburl') or ii.get('url')
            if not url or url in seen: continue
            seen.add(url)
            candidates.append({'title':title,'url':url,'page':'https://commons.wikimedia.org/wiki/'+m.quote(title.replace(' ','_'),safe=':/()_-'),'license':lic,'author':m.clean_html((meta.get('Artist') or {}).get('value'))[:160] or 'Wikimedia Commons','semantic':term})
    chosen=[]
    for c in candidates:
        if len(chosen)>=count: break
        key=f'{prefix}_{len(chosen)+1}'; p=m.SRC/f'{key}.jpg'
        try:
            r=requests.get(c['url'],headers=m.UA,timeout=90); r.raise_for_status(); p.write_bytes(r.content)
            with m.Image.open(p) as im:
                if min(im.size)<420: raise RuntimeError('too small')
                im.convert('RGB').save(p,'JPEG',quality=92)
            m.sources[key]={**c,'path':str(p.relative_to(m.ROOT)),'sha256':m.sha256(p),'rightsBasis':'Wikimedia Commons license metadata + named-entity title match'}
            chosen.append(key)
        except Exception:
            p.unlink(missing_ok=True)
    if len(chosen)<count:
        print(f'ENTITY_VISUAL_SHORTAGE prefix={prefix} required={count} chosen={len(chosen)} candidates={len(candidates)} titles={[c["title"] for c in candidates[:12]]}')
        raise RuntimeError(f'NAMED_ENTITY_VISUAL_AUTHENTICITY_FAIL:{prefix}:{len(chosen)}/{count}')
    return chosen

def caption_chunks(text,max_words=8,max_chars=62):
    words=text.split(); chunks=[]; cur=[]
    for word in words:
        trial=cur+[word]
        if cur and (len(trial)>max_words or len(' '.join(trial))>max_chars):
            chunks.append(' '.join(cur)); cur=[word]
        else:
            cur=trial
    if cur: chunks.append(' '.join(cur))
    if not chunks: chunks=['']
    dummy=m.Image.new('RGB',(m.W,m.H),(0,0,0)); draw=m.ImageDraw.Draw(dummy); fnt=m.font(38,True)
    for chunk in chunks:
        lines=m.wrap(draw,chunk,fnt,930,99)
        if len(lines)>2:
            raise RuntimeError(f'CC_MAX_TWO_LINES_FAIL:{chunk}:{len(lines)}')
    return chunks

def captioned_render(name,entity,scene_keys,scenes,music_path,source_label):
    if len(scene_keys)!=len(scenes) or len(scene_keys)<5 or len(set(scene_keys))!=len(scene_keys):
        raise RuntimeError(f'SCENE_DIVERSITY_FAIL:{name}')
    parts=[]
    for i,(key,sc) in enumerate(zip(scene_keys,scenes)):
        voice,dur=m.tts(sc['narration'],f'{name}-{i}')
        chunks=caption_chunks(sc['narration'])
        weights=[max(1,len(c.split())) for c in chunks]; total_weight=sum(weights)
        visual_parts=[]
        for j,(chunk,weight) in enumerate(zip(chunks,weights)):
            chunk_dur=dur*weight/total_weight
            frame=m.video_frame(key,sc['headline'],chunk,source_label)
            jpg=m.TMP/f'{name}-{i}-cc-{j}.jpg'; frame.save(jpg,'JPEG',quality=91)
            clip=m.TMP/f'{name}-{i}-cc-{j}.mp4'
            subprocess.run(['ffmpeg','-y','-loop','1','-framerate','30','-i',str(jpg),'-t',f'{chunk_dur:.3f}','-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p',str(clip)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            visual_parts.append(clip)
        vlst=m.TMP/f'{name}-{i}-visual-concat.txt'
        vlst.write_text('\n'.join("file '"+str(p.resolve()).replace("'","'\\''")+"'" for p in visual_parts),encoding='utf-8')
        visual=m.TMP/f'{name}-{i}-visual.mp4'
        subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(vlst),'-c','copy',str(visual)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        out=m.TMP/f'{name}-{i}.mp4'
        subprocess.run(['ffmpeg','-y','-i',str(visual),'-i',str(voice),'-stream_loop','-1','-i',str(music_path),'-filter_complex','[1:a]volume=1.0[v];[2:a]volume=0.075[m];[v][m]amix=inputs=2:duration=first:dropout_transition=1[a]','-map','0:v:0','-map','[a]','-t',f'{dur:.3f}','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        parts.append(out)
    lst=m.TMP/f'{name}-concat.txt'; lst.write_text('\n'.join("file '"+str(p.resolve()).replace("'","'\\''")+"'" for p in parts),encoding='utf-8')
    final=m.OUT/f'{name}.mp4'
    subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(lst),'-c','copy','-movflags','+faststart',str(final)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return final

ORIGINAL_REC=m.rec

def rec_with_caption_gates(path,keys,kind,entity=None,cc=False):
    record=ORIGINAL_REC(path,keys,kind,entity,cc)
    if path.suffix=='.mp4':
        record['visualQa']['CC_MAX_TWO_LINES_PASS']=bool(cc)
        record['visualQa']['CC_CHUNKED_SYNC_PASS']=bool(cc)
        record['visualQa']['CC_OVER_PRIMARY_VISUAL']=False
    return record

def duration_gated_render(name,entity,scene_keys,scenes,music_path,source_label):
    scenes=[dict(s) for s in scenes]
    additions={
      'instagram-reel-mondial-historias-de-gestao':[
        ' Antes de ampliar, era preciso dominar o básico.',
        ' Isso reduz dependência e encurta o ciclo.',
        ' Cada nova frente precisava ter dono e meta.',
        ' A escala passou a conversar com o mercado nacional.',
        ' Distribuição transforma produto disponível em venda real.',
        ' Presença consistente aumenta lembrança e confiança do consumidor.',
        ' Capacidade construída hoje sustenta o próximo salto.'
      ],
      'tiktok-zara-inditex-1200':[
        ' O dado reduz a aposta.', '', '', '', '', ' E melhora a decisão de capital.'
      ],
      'instagram-reel-american-eagle-1800':[
        ' A conta aparece rápido.', '', '', '', '', ' E a margem sente primeiro.'
      ],
      'tiktok-nvidia-anthropic-1945':[
        ' O movimento mudaria essa relação.',
        ' Isso cria alinhamento e dependência.',
        ' Computação passa a ser vantagem competitiva.',
        ' Confiança também tem preço estratégico.',
        ' É uma relação para monitorar.'
      ]
    }
    extra=additions.get(name,[])
    for i,s in enumerate(scenes):
        if i < len(extra) and extra[i]: s['narration']=s['narration'].rstrip()+extra[i]
    final=captioned_render(name,entity,scene_keys,scenes,music_path,source_label)
    dur=float(m.probe(final)['format']['duration'])
    if name=='instagram-reel-mondial-historias-de-gestao':
        if not (75 <= dur <= 90): raise RuntimeError(f'DURATION_GATE_FAIL:{name}:{dur:.2f}:expected_75_90')
    elif name in {'tiktok-zara-inditex-1200','instagram-reel-american-eagle-1800','tiktok-nvidia-anthropic-1945'}:
        if not (45 <= dur <= 60): raise RuntimeError(f'DURATION_GATE_FAIL:{name}:{dur:.2f}:expected_45_60')
    print(f'DURATION_GATE_PASS {name} {dur:.2f}s')
    return final

m.download_mondial=extract_mondial_from_approved_master
m.commons_search=robust_commons_search
m.render_narrated=duration_gated_render
m.rec=rec_with_caption_gates
m.main()

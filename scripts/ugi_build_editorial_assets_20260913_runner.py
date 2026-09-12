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

m.download_mondial=extract_mondial_from_approved_master
m.commons_search=robust_commons_search
m.main()

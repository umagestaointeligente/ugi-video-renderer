#!/usr/bin/env python3
import importlib.util, subprocess, requests
from pathlib import Path

BASE=Path(__file__).with_name('ugi_build_editorial_assets_20260913.py')
spec=importlib.util.spec_from_file_location('ugi_sep13_builder',BASE)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

ASSET_COMMIT='ffc5867a177813eb33d4df4cf4fa5a01515aee3a'
MASTER_REL='public/ugi/editorial/2026-09-13/longform/youtube-mondial-historias-de-gestao.mp4'
MASTER_RAW=f'https://raw.githubusercontent.com/umagestaointeligente/ugi-video-renderer/{ASSET_COMMIT}/{MASTER_REL}'

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

m.download_mondial=extract_mondial_from_approved_master
m.main()

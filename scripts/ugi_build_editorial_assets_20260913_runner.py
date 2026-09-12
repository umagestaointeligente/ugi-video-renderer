#!/usr/bin/env python3
import importlib.util, subprocess
from pathlib import Path

BASE=Path(__file__).with_name('ugi_build_editorial_assets_20260913.py')
spec=importlib.util.spec_from_file_location('ugi_sep13_builder',BASE)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def extract_mondial_from_approved_master():
    master=m.ROOT/'public/ugi/editorial/2026-09-13/longform/youtube-mondial-historias-de-gestao.mp4'
    if not master.exists() or master.stat().st_size < 10_000_000:
        raise RuntimeError('APPROVED_MONDIAL_MASTER_MISSING')
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
        m.sources[key]={'key':key,'page':'public/ugi/editorial/2026-09-13/longform/youtube-mondial-historias-de-gestao.mp4','license':'previously-approved UGI editorial source','rightsBasis':'Extracted from already-approved UGI Mondial longform master; original provenance retained in longform/source-manifest.json','semantic':label,'path':str(p.relative_to(m.ROOT)),'sha256':m.sha256(p)}
        keys.append(key)
    return keys

m.download_mondial=extract_mondial_from_approved_master
m.main()

#!/usr/bin/env python3
import importlib.util, json, re, requests
from pathlib import Path
from urllib.parse import quote

BASE=Path(__file__).with_name('ugi_build_editorial_assets_20260915_v3_exact_subject.py')
spec=importlib.util.spec_from_file_location('ugi15v3',BASE)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


def exact_file(prefix, title, idx=1):
    data=m.req({'action':'query','format':'json','titles':title,'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':1800})
    pages=(data.get('query') or {}).get('pages') or {}
    if not pages: raise RuntimeError(f'EXACT_FILE_NOT_FOUND:{title}')
    page=next(iter(pages.values())); actual=page.get('title','')
    if actual.lower()!=title.lower(): raise RuntimeError(f'EXACT_FILE_TITLE_MISMATCH:{title}:{actual}')
    ii=(page.get('imageinfo') or [{}])[0]; meta=ii.get('extmetadata') or {}
    lic=m.clean((meta.get('LicenseShortName') or {}).get('value'))
    if not lic or not any(x in lic.lower() for x in ['cc','public domain','pdm','gfdl']):
        raise RuntimeError(f'EXACT_FILE_LICENSE_FAIL:{title}:{lic}')
    url=ii.get('thumburl') or ii.get('url')
    if not url: raise RuntimeError(f'EXACT_FILE_URL_FAIL:{title}')
    key=f'{prefix}_{idx}'; p=m.SRC/f'{key}.jpg'
    r=requests.get(url,headers=m.UA,timeout=90); r.raise_for_status(); p.write_bytes(r.content)
    with m.b.Image.open(p) as im:
        im.convert('RGB').save(p,'JPEG',quality=92)
    m.SOURCES[key]={
      'title':actual,'url':url,'page':'https://commons.wikimedia.org/wiki/'+quote(actual.replace(' ','_'),safe=':/()_,-'),
      'license':lic,'author':m.clean((meta.get('Artist') or {}).get('value'))[:160] or 'Wikimedia Commons',
      'semanticQuery':'exact Wikimedia Commons file title','path':str(p.relative_to(m.ROOT)),'sha256':m.b.sha256(p),
      'rightsBasis':'Wikimedia Commons exact-file lookup + license metadata',
      'exactSubjectReceipt':{'approved':True,'type':'manual_exact_file','requestedTitle':title,'resolvedTitle':actual}
    }
    return key


def strict_collect_v4(prefix, queries, count, must_any, reject=None):
    # Manual receipts for topics where a keyword-only search can be technically real but editorially wrong.
    if prefix=='stellantis':
        return [exact_file('stellantis','File:Stellantis.svg')]
    if prefix=='santos':
        return [exact_file('santos','File:Santos limited corporate logo.svg')]
    if prefix=='total':
        return [exact_file('total','File:TotalEnergies wordmark (2021-present).svg')]
    if prefix=='mps':
        return [m.info_source('mps_1','MONTE DEI PASCHI DI SIENA',['Banco citado diretamente na transação','Este slide é um identificador editorial, não uma foto substituta'],'Fonte factual: Reuters • 10/09/2026')]
    if prefix=='mediobanca':
        return [m.info_source('mediobanca_1','MEDIOBANCA',['Entidade citada diretamente na transação com MPS','Sem uso de outro banco como proxy visual'],'Fonte factual: Reuters • 10/09/2026')]
    if prefix=='intesa':
        return [m.info_source('intesa_1','INTESA SANPAOLO',['Entidade citada diretamente no movimento de consolidação','Sem imagem genérica do setor bancário'],'Fonte factual: Reuters • 10/09/2026')]
    if prefix=='lego':
        titles=[
          'File:LEGO Billund.JPG',
          'File:Lego House Billund.jpg',
          'File:Legoland Indgangen.jpg',
          'File:1x3 grey Lego brick.jpg',
          'File:Lego House, Billund 01.jpg'
        ]
        return [exact_file('lego',t,i+1) for i,t in enumerate(titles[:count])]
    return m.strict_collect(prefix,queries,count,must_any,reject)

m.strict_collect=strict_collect_v4
m.main()

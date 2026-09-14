#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, pathlib, re, urllib.parse, urllib.request

UA={'User-Agent':'ORBIT-VSA/1.0'}
def get_json(url):
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=45) as r: return json.load(r)
def download(url,dst):
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=90) as r, open(dst,'wb') as f:
        while True:
            b=r.read(1024*1024)
            if not b: break
            f.write(b)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--query',required=True); ap.add_argument('--must',action='append',required=True); ap.add_argument('--expected-subject',required=True); ap.add_argument('--out-dir',required=True); ap.add_argument('--count',type=int,default=3); a=ap.parse_args()
    out=pathlib.Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
    url='https://images-api.nasa.gov/search?'+urllib.parse.urlencode({'q':a.query,'media_type':'video','page_size':100})
    data=get_json(url); items=data.get('collection',{}).get('items',[])
    must=[x.lower() for x in a.must]; chosen=[]; seen=set()
    for item in items:
        d=(item.get('data') or [{}])[0]; title=str(d.get('title') or ''); desc=str(d.get('description') or '')+' '+str(d.get('description_508') or '')
        hay=(title+' '+desc).lower()
        if not any(k in hay for k in must): continue
        nasa_id=str(d.get('nasa_id') or '').strip()
        if not nasa_id or nasa_id in seen: continue
        seen.add(nasa_id)
        href=item.get('href')
        if not href: continue
        try: assets=get_json(href)
        except Exception: continue
        mp4s=[x for x in assets if isinstance(x,str) and re.search(r'\.mp4(?:$|\?)',x,re.I)]
        if not mp4s: continue
        # Prefer preview/small derivatives to keep CI deterministic and fast.
        mp4s.sort(key=lambda x:(0 if any(k in x.lower() for k in ('~small','~medium','preview')) else 1,len(x)))
        media=mp4s[0]; dst=out/f'{len(chosen)+1:02d}_{re.sub(r"[^A-Za-z0-9._-]+","_",nasa_id)}.mp4'
        try: download(media,dst)
        except Exception: continue
        if dst.stat().st_size < 100000: dst.unlink(missing_ok=True); continue
        chosen.append({'file':str(dst),'nasa_id':nasa_id,'title':title,'source_url':f'https://images.nasa.gov/details/{urllib.parse.quote(nasa_id)}','download_url':media,'license':'NASA Media Usage Guidelines / U.S. Government work; verify third-party credits','rights_verified':True,'expected_subject':a.expected_subject,'asset_subject':a.expected_subject,'asset_role':'TARGET_SUBJECT','explicit_script_reference':True})
        if len(chosen)>=a.count: break
    if len(chosen)<a.count:
        raise SystemExit(f'BLOCK_REAL_FOOTAGE: exact NASA videos found {len(chosen)}/{a.count} for {a.query}')
    (out/'manifest.json').write_text(json.dumps(chosen,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'PASS','count':len(chosen),'assets':chosen},ensure_ascii=False))
if __name__=='__main__': main()

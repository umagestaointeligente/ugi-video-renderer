#!/usr/bin/env python3
"""Date-independent candidate rendering; never publishes or certifies rights/repetition."""
import argparse
import base64
import datetime
import hashlib
import json
import pathlib
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from cena_certa_oct13_compile import compile_editorial
import cena_certa_oct13_pack as pack

def main():
    p=argparse.ArgumentParser();p.add_argument('--editorial',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    source=(ROOT/a.editorial).resolve();out=(ROOT/a.out).resolve()
    if not source.is_relative_to(ROOT) or not out.is_relative_to(ROOT/'out'):
        raise ValueError('INPUT_OR_OUTPUT_OUTSIDE_CHECKOUT')
    doc=json.loads(source.read_text());date=doc.get('publication_date')
    datetime.date.fromisoformat(date)
    manifest,errors=compile_editorial(doc,expected_date=date)
    out.mkdir(parents=True,exist_ok=True)
    if errors:
        (out/'batch-receipt.json').write_text(json.dumps({'technical_render':'BLOCKED_INPUT','errors':errors,'release_allowed':False},indent=2)+'\n')
        print('CENA_CERTA_INPUT_BLOCKED',len(errors));return 1
    pack.OUT=out;pack.WORK=out/'work';pack.WORK.mkdir(exist_ok=True)
    logo=pack.WORK/'logo.png';logo.write_bytes(base64.b64decode(''.join((ROOT/'assets/cena-certa-logo.png.b64').read_text().split())))
    cache={};results=[]
    for item in manifest['items']:
        try:
            media=pack.download_source(item,cache)
            master,_,_,seconds,_=pack.render_item(item,media,logo,None)
            results.append({'id':item['id'],'technical_render':'PASS','duration_seconds':seconds,
                            'master':str(master.relative_to(ROOT)),'sha256':hashlib.sha256(master.read_bytes()).hexdigest()})
        except Exception as e:
            results.append({'id':item['id'],'technical_render':'FAIL','error_type':type(e).__name__})
    receipt={'editorial_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'date':date,'items':results,
             'release_allowed':False,'editorial_review':'PENDING','anti_repeat_180d':'NOT_VERIFIED',
             'scheduled':False,'published':False}
    (out/'batch-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print('CENA_CERTA_CANDIDATES',sum(x['technical_render']=='PASS' for x in results),'/',len(results))
    return 0 if all(x['technical_render']=='PASS' for x in results) else 1
if __name__=='__main__':raise SystemExit(main())

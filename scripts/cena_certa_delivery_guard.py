"""Offline, fail-closed delivery validation. No publication or networking."""
import hashlib
import json
import math
import os
from pathlib import Path

CONTENT_GATES = ('REAL_FOOTAGE_PASS','PTBR_CONTEXT_OVERLAY_PASS','AUDIO_VISUAL_SYNC_PASS',
                 'NO_EXTRA_ZOOM_PASS','NO_AGGRESSIVE_CROP_PASS','NO_LEGACY_MASK_PASS',
                 'CTA_FINAL_PASS','EDITORIAL_PASS')
MEASURED_GATES = ('SOURCE_PASS','SOURCE_WINDOW_60D_PASS','REAL_MOTION_PASS','NO_NARRATION_PASS',
                  'NO_BLACK_PASS','NO_SILENT_TAIL_PASS','H264_AAC_PASS','NINE_BY_SIXTEEN_PASS',
                  'SCENE_SEQUENCE_60D_PASS')

def require(condition, code):
    if not condition:
        raise RuntimeError(code)

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def validate_review(summary, review, manifest_sha):
    require(isinstance(manifest_sha,str) and len(manifest_sha)==64,'QA_MANIFEST_SHA_MISSING')
    require(isinstance(review,dict) and isinstance(review.get('reviewer'),str)
            and review['reviewer'].strip() and review.get('manifest_sha256')==manifest_sha,'CONTENT_QA_PROVENANCE_FAIL')
    records=summary['items']; qa=review.get('items',{})
    require(set(qa)=={x['id'] for x in records},'CONTENT_QA_ITEM_SET_FAIL')
    for rec in records:
        item=qa[rec['id']]
        require(item.get('sha256')==rec['sha256'],'CONTENT_QA_SHA_FAIL')
        for gate in CONTENT_GATES:
            require(item.get('gates',{}).get(gate) is True,'CONTENT_QA_UNVERIFIED:'+gate)
            rec['gates'][gate]=True

def validate_delivery(out, summary, manifest, env):
    out=Path(out)
    for key,var in [('commit','GITHUB_SHA'),('run_id','GITHUB_RUN_ID'),('run_attempt','GITHUB_RUN_ATTEMPT')]:
        require(bool(env.get(var)) and summary.get(key)==env[var],'DELIVERY_PROVENANCE_FAIL:'+key)
    records=summary.get('items',[]); planned=manifest.get('items',[])
    require(len(records)==len(planned)==12,'DELIVERY_ITEM_COUNT_FAIL')
    expected={x['id']:x for x in planned}
    require(len(expected)==12 and len({x['id'] for x in records})==12
            and set(expected)=={x['id'] for x in records},'DELIVERY_ITEM_SET_FAIL')
    files=set()
    for rec in records:
        src=expected[rec['id']]
        for key in ('network','slot','title','source','source_id'):
            require(rec.get(key)==src.get(key),'DELIVERY_MANIFEST_DRIFT:'+key)
        require(rec.get('segments')==src.get('segments'),'DELIVERY_SEGMENTS_DRIFT')
        for gate in CONTENT_GATES+MEASURED_GATES:
            require(rec.get('gates',{}).get(gate) is True,'DELIVERY_GATE_MISSING:'+gate)
        target=out/rec['network']/(rec['id']+'.mp4')
        require(target.resolve().is_relative_to(out.resolve()),'DELIVERY_PATH_ESCAPE')
        require(target.is_file() and not target.is_symlink(),'DELIVERY_FILE_MISSING')
        require(digest(target)==rec.get('sha256'),'DELIVERY_SHA_FAIL')
        files.add(target)
    require(files==set(out.glob('*/*.mp4')),'DELIVERY_UNEXPECTED_FILES')
    require(summary.get('history_fingerprint_coverage')==1.0
            and summary.get('history_eligible_media',0)>0,'DELIVERY_HISTORY_FAIL')
    return True

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);ap.add_argument('--manifest',required=True)
    args=ap.parse_args()
    validate_delivery(args.out,json.loads((Path(args.out)/'summary.json').read_text()),
                      json.loads(Path(args.manifest).read_text()),os.environ)
    print('CENA_CERTA_DELIVERY_GUARD=PASS')

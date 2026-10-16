#!/usr/bin/env python3
"""Reusable UGI render, exact local assets and exact narration. No publisher."""
import argparse
import hashlib
import json
import math
import pathlib
import subprocess
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

def local(value):
    p=(ROOT/value).resolve()
    if not p.is_relative_to(ROOT) or not p.is_file():raise ValueError('LOCAL_ASSET_MISSING_OR_OUTSIDE_REPO')
    return p

def run(args):
    return subprocess.run([str(a) for a in args],check=True,capture_output=True,text=True,timeout=480)

def probe(path):
    return json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',path]).stdout)

def render(item,out):
    if not item.get('id') or not all(c.isalnum() or c in '_-' for c in item['id']):raise ValueError('ITEM_ID_INVALID')
    work=out/item['id'];work.mkdir(parents=True,exist_ok=True)
    source=local(item['source_file'])
    if sha(source)!=item['source_sha256']:raise ValueError('SOURCE_HASH_MISMATCH')
    text=local(item['text_file']).read_text().strip()
    if not text:raise ValueError('EMPTY_NARRATION_TEXT')
    if item.get('narration_file'):
        audio=local(item['narration_file'])
        if sha(audio)!=item['narration_sha256'] or hashlib.sha256(text.encode()).hexdigest()!=item['text_sha256']:
            raise ValueError('NARRATION_IDENTITY_MISMATCH')
    else:
        audio=work/'narration.mp3'
        run([sys.executable,ROOT/'scripts/media/edge_tts_worker.py','--voice','pt-BR-AntonioNeural',
             '--rate='+item.get('rate','-2%'),'--text',text,'--write-media',audio])
    length=float(probe(audio)['format']['duration'])
    if not math.isfinite(length) or not 12<=length<=300:raise ValueError('NARRATION_DURATION_INVALID')
    # Readable title through textfile, never interpolate editorial into shell/filter grammar.
    title=work/'title.txt';title.write_text(item['title'])
    w,h=(1920,1080) if item.get('orientation')=='landscape' else (1080,1920)
    filt=(f'scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,fps=30,'
          f'drawbox=x=0:y=0:w=iw:h=180:color=black@0.35:t=fill,'
          f'drawtext=fontfile={FONT}:textfile={title}:fontcolor=white:fontsize=44:x=(w-text_w)/2:y=62,'
          f'drawtext=fontfile={FONT}:text=UMA GESTÃO INTELIGENTE:fontcolor=white:fontsize=28:borderw=2:x=(w-text_w)/2:y=h-110,'
          f"drawtext=fontfile={FONT}:text=Siga para mais ideias de gestão:fontcolor=white:fontsize=30:borderw=2:x=(w-text_w)/2:y=h-170:enable='gte(t,{max(0,length-3)})'")
    master=work/'master.mp4'
    run(['ffmpeg','-y','-v','error','-filter_threads','2','-stream_loop','-1','-i',source,'-i',audio,
         '-vf',filt,'-af','loudnorm=I=-16:TP=-1.5:LRA=9','-map','0:v:0','-map','1:a:0',
         '-t',str(length),'-c:v','libx264','-threads','2','-preset','veryfast','-crf','20',
         '-pix_fmt','yuv420p','-c:a','aac','-ar','48000','-b:a','160k','-movflags','+faststart',master])
    data=probe(master);v=next(s for s in data['streams'] if s['codec_type']=='video')
    a=next(s for s in data['streams'] if s['codec_type']=='audio')
    if (v['codec_name'],v['width'],v['height'],v.get('sample_aspect_ratio'),a['codec_name'])!=('h264',w,h,'1:1','aac'):
        raise ValueError('MASTER_FORMAT_FAIL')
    if abs(float(data['format']['duration'])-length)>.3:raise ValueError('MASTER_DURATION_FAIL')
    # Decoder exit status is mandatory; a corrupt file can never gain a technical PASS.
    run(['ffmpeg','-v','error','-xerror','-i',master,'-f','null','-'])
    rec={'id':item['id'],'master':str(master.relative_to(ROOT)),'sha256':sha(master),
         'duration_seconds':float(data['format']['duration']),'technical_render':'PASS',
         'source_sha256':sha(source),'narration_sha256':sha(audio),
         'text_sha256':hashlib.sha256(text.encode()).hexdigest(),
         'editorial_review':'PENDING','anti_repeat_180d':'NOT_VERIFIED','release_allowed':False,
         'published':False,'scheduled':False}
    (work/'render-receipt.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n')
    return rec

def main():
    p=argparse.ArgumentParser();p.add_argument('--manifest',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    out=(ROOT/a.out).resolve()
    if not out.is_relative_to(ROOT/'out'):raise ValueError('OUTPUT_MUST_BE_UNDER_OUT')
    doc=json.loads(local(a.manifest).read_text())
    if doc.get('channel')!='ugi' or not doc.get('items'):raise ValueError('UGI_MANIFEST_INVALID')
    ids=[x['id'] for x in doc['items']]
    if len(ids)!=len(set(ids)):raise ValueError('DUPLICATE_ITEM_ID')
    out.mkdir(parents=True,exist_ok=True);results=[]
    for item in doc['items']:
        try:results.append(render(item,out))
        except Exception as e:
            # Keep the stage and item; do not dump provider URLs or credential-bearing stderr.
            results.append({'id':item['id'],'technical_render':'FAIL','error':type(e).__name__+':'+str(e)[:160] if not isinstance(e,subprocess.CalledProcessError) else 'COMMAND_FAILED:'+str(e.cmd[0]),'release_allowed':False})
    (out/'batch-receipt.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,ensure_ascii=False))
    return 0 if all(x['technical_render']=='PASS' for x in results) else 1
if __name__=='__main__':raise SystemExit(main())

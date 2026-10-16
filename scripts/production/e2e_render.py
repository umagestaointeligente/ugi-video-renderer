#!/usr/bin/env python3
"""Production-path media tests. RENDERED never implies approved/published/scheduled."""
import argparse,base64,hashlib,importlib.util,json,math,pathlib,subprocess,sys,textwrap,shutil,re,urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'scripts/media')]
import cena_certa_oct13_pack as cc
import ugi_render_manifest as ugi
from acquire_source import acquire,digest

def run(args,timeout=360):
 return subprocess.run([str(x) for x in args],capture_output=True,text=True,check=True,timeout=timeout)

def verify_master(path):
 data=cc.validate_master(path)
 v=next(x for x in data['streams'] if x['codec_type']=='video');a=next(x for x in data['streams'] if x['codec_type']=='audio')
 if abs(float(v.get('duration',0))-float(a.get('duration',0)))>.35:raise RuntimeError('AV_DURATION_MISMATCH')
 p=run(['ffmpeg','-v','info','-xerror','-i',path,'-map','0:a:0','-af','volumedetect','-f','null','-'])
 import re
 match=re.search(r'max_volume:\s*(-?inf|[-+]?\d+(?:\.\d+)?)\s*dB',p.stderr)
 if not match or not math.isfinite(float(match.group(1))) or float(match.group(1))<-50:raise RuntimeError('AUDIO_SILENT')
 run(['ffmpeg','-v','error','-xerror','-i',path,'-f','null','-'])
 return {'file':str(path.relative_to(ROOT)),'sha256':digest(path),'duration_seconds':float(data['format']['duration']),
         'technical_qa':'PASS','release_allowed':False,'published':False,'scheduled':False}

def timestamp(seconds):
 cs=round(seconds*100);return f'{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}'

def word_captions(metadata,output):
 words=[json.loads(x) for x in metadata.read_text().splitlines() if x.strip()]
 words=[w for w in words if w.get('type')=='WordBoundary']
 if not words:raise RuntimeError('WORD_BOUNDARIES_MISSING')
 groups=[];group=[]
 for w in words:
  if group and (len(' '.join(x['text'] for x in group+[w]))>72 or len(group)>=9):groups.append(group);group=[]
  group.append(w)
 if group:groups.append(group)
 header='''[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,43,&H00FFFFFF,&H000000FF,&H00101010,&H80000000,-1,0,0,0,100,100,0,0,1,3,1,2,65,65,310,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
 rows=[]
 for group in groups:
  text=' '.join(w['text'] for w in group);lines=textwrap.wrap(text,width=36,break_long_words=False)
  if len(lines)>2:raise RuntimeError('CAPTION_EXCEEDS_TWO_LINES')
  start=group[0]['offset']/1e7;end=(group[-1]['offset']+group[-1]['duration'])/1e7
  caption=r'\N'.join(lines).replace('{','').replace('}','')
  rows.append(f'Dialogue: 0,{timestamp(start)},{timestamp(end)},Default,,0,0,0,,{caption}\n')
 output.write_text(header+''.join(rows));return len(groups)

def cena_certa(out):
 work=out/'work';work.mkdir(parents=True,exist_ok=True);cc.WORK=work;cc.OUT=out
 # Film from the current proposed grade, a fresh public scene source, original PT-BR dialogue.
 # This is an acquisition/render test, never a substitute for rights or 180d review.
 item={'id':'CC-OCT16-FB-FELICIDADE-AQUISICAO','network':'facebook','format':'film_scene_editorial',
       'title':'À Procura da Felicidade (2006)','source':'https://globoplay.globo.com/v/4192856/',
       'source_id':'4192856','segments':[[81,125]],'hook':'🎥 À PROCURA DA FELICIDADE',
       'cta':'COMO VOCÊ LIDARIA COM ESSA PRESSÃO?','audio_mode':'ORIGINAL_SOURCE_DIALOGUE'}
 media=cc.download_source(item,{})
 logo=work/'logo.png';logo.write_bytes(base64.b64decode(''.join((ROOT/'assets/cena-certa-logo.png.b64').read_text().split())))
 path,*_=cc.render_item(item,media,logo,None)
 rec=verify_master(path);rec.update(source=item['source'],source_sha256=digest(media),source_segments=item['segments'],
   rights_to_republish='NOT_VERIFIED',anti_repeat_180d='NOT_VERIFIED',editorial_review='PENDING')
 return [rec]

def ugi_new(out):
 work=out/'work';work.mkdir(parents=True,exist_ok=True)
 source=work/'warehouse.mp4'
 origin=acquire('https://www.dvidshub.net/video/799059/azng-supports-gilbert-food-bank-warehouse-operations',source,60)
 script=ROOT/'ops/production/e2e-oct16/ugi-narration.txt';text=script.read_text().strip()
 audio=work/'narration.mp3';metadata=work/'words.jsonl'
 run([sys.executable,ROOT/'scripts/media/edge_tts_worker.py','--voice','pt-BR-AntonioNeural','--rate=-2%',
      '--text',text,'--write-media',audio,'--write-metadata',metadata],timeout=75)
 captions=work/'captions.ass';count=word_captions(metadata,captions)
 music=work/'music.mp3'
 request=urllib.request.Request('https://incompetech.com/music/royalty-free/mp3-royaltyfree/Carefree.mp3',headers={'User-Agent':'UGI production QA contact via repository'})
 with urllib.request.urlopen(request,timeout=45) as response,music.open('wb') as f:
  import shutil;shutil.copyfileobj(response,f)
 credit='Carefree — Kevin MacLeod (incompetech.com). Licensed under Creative Commons Attribution. https://incompetech.com/music/royalty-free/licenses/\nFootage: U.S. Air National Guard / Dillon Davis, DVIDS video 799059, public domain; no endorsement implied.\n'
 (out/'ATTRIBUTION.txt').write_text(credit)
 item={'id':'UGI-OCT16-CONFERENCIA','title':'CONFERIR ANTES\nEVITA RETRABALHO',
       'source_file':str(source.relative_to(ROOT)),'source_sha256':digest(source),
       'text_file':str(script.relative_to(ROOT)),'text_sha256':hashlib.sha256(text.encode()).hexdigest(),
       'narration_file':str(audio.relative_to(ROOT)),'narration_sha256':digest(audio),
       'subtitle_file':str(captions.relative_to(ROOT)),'music_file':str(music.relative_to(ROOT))}
 rec=ugi.render(item,out);path=ROOT/rec['master'];rec.update(verify_master(path));rec.update(source_origin=origin,
       word_boundary_captions=count,caption='Conferir na origem evita retrabalho na ponta. '+credit)
 return [rec]

def vsa(out):
 script=ROOT/'production/vsa/pilots/oct13_triple/render_oct13_triple.py'
 (out/'ATTRIBUTION.txt').write_text('Physical Newton demonstration: UniServeScienceVIDEO, PH ME DY TUTE 70030A V0608 Newtons Cradle Introductory Analysis, CC BY 3.0 https://creativecommons.org/licenses/by/3.0/ ; excerpted, resized, narrated and captioned. Source: https://commons.wikimedia.org/wiki/File:PH_ME_DY_TUTE_70030A_V0608_Newtons_Cradle_Introductory_Analysis.webm\nOther source licenses remain listed in the per-scene receipts and require review before release.\n')
 run([sys.executable,script],timeout=1800)
 folder=script.parent/'output';manifest=json.loads((folder/'MANIFEST.json').read_text())
 if len(manifest)!=3:raise RuntimeError('VSA_BATCH_INCOMPLETE')
 rows=[]
 for item in manifest:
  path=pathlib.Path(item['master']);rec=verify_master(path)
  if not 45<=rec['duration_seconds']<=55:raise RuntimeError('VSA_DURATION_OUTSIDE_CONTRACT')
  rec.update(slug=item['slug'],editorial_review='PENDING',anti_repeat_180d='NOT_VERIFIED');rows.append(rec)
 return rows

def stage_deliverables(rows,out):
 deliver=out/'deliverables';shutil.rmtree(deliver,ignore_errors=True);deliver.mkdir()
 if not rows:raise RuntimeError('NO_RENDERED_MASTERS')
 for i,row in enumerate(rows):
  path=(ROOT/row['file']).resolve()
  if not path.is_relative_to(ROOT) or not path.is_file():raise RuntimeError('MASTER_MISSING_OR_OUTSIDE_REPO')
  if digest(path)!=row['sha256']:raise RuntimeError('MASTER_CHANGED_AFTER_QA')
  dest=deliver/f'{i+1:02d}_{path.name}';shutil.copyfile(path,dest)
  row['artifact_file']=str(dest.relative_to(ROOT))

def main():
 p=argparse.ArgumentParser();p.add_argument('--channel',choices=['cena-certa','vsa','ugi'],required=True);a=p.parse_args()
 out=ROOT/'out/production-e2e-oct16'/a.channel;out.mkdir(parents=True,exist_ok=True)
 shutil.rmtree(out/'deliverables',ignore_errors=True)
 report={'channel':a.channel,'status':'FAIL','release_allowed':False,'published':False,'scheduled':False}
 try:
  rows={'cena-certa':cena_certa,'vsa':vsa,'ugi':ugi_new}[a.channel](out)
  stage_deliverables(rows,out)
  report.update(status='RENDERED_TECHNICAL_QA_PASS',videos=rows)
 except Exception as exc:
  code=str(exc).split(' ',1)[0][:100]
  if isinstance(exc,subprocess.CalledProcessError):
   codes=re.findall(r'(?:TTS|SOURCE|ASSET|VSA|MASK|DURATION|CAPTION)_[A-Z_]+',str(exc.stderr or ''))
   code=codes[-1] if codes else 'RENDER_SUBPROCESS_FAILED'
  report.update(error_type=type(exc).__name__,error_code=code)
 finally:
  (out/'E2E_RECEIPT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report,ensure_ascii=False))
 return 0 if report['status']=='RENDERED_TECHNICAL_QA_PASS' else 1
if __name__=='__main__':raise SystemExit(main())

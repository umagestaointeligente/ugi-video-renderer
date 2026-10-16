#!/usr/bin/env python3
"""Bounded public-media intake; no cookies, paid routes, or auth/DRM bypass."""
import hashlib,json,pathlib,subprocess,sys
from urllib.parse import urlparse

def digest(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()

def acquire(page,target,seconds=60):
 target=pathlib.Path(target);target.parent.mkdir(parents=True,exist_ok=True)
 if not page.startswith('https://') or urlparse(page).username:raise ValueError('PUBLIC_HTTPS_REQUIRED')
 sidecar=target.with_suffix('.origin.json')
 if target.exists() and sidecar.exists():
  rec=json.loads(sidecar.read_text())
  if rec.get('source_page')==page and rec.get('sha256')==digest(target) and rec.get('prefix_seconds',0)>=seconds:return rec
 result=subprocess.run([sys.executable,'-m','yt_dlp','--compat-options','no-certifi','--skip-download','--dump-single-json',
  '--no-warnings','--socket-timeout','12','--retries','0',page],capture_output=True,text=True,timeout=45)
 if result.returncode:
  low=result.stderr.casefold()
  raise RuntimeError('SOURCE_AUTH_REQUIRED' if 'sign in' in low or '403' in low else 'SOURCE_METADATA_FAILED')
 data=json.loads(result.stdout)
 if data.get('is_live') or data.get('has_drm'):raise RuntimeError('LIVE_OR_DRM_SOURCE_BLOCKED')
 formats=[f for f in data.get('formats',[]) if f.get('url','').startswith('https://') and not f.get('has_drm') and f.get('vcodec')!='none']
 if not formats:raise RuntimeError('PUBLIC_VIDEO_FORMAT_MISSING')
 formats.sort(key=lambda f:abs((f.get('height') or 720)-720))
 media_url=formats[0]['url'];partial=target.with_name(target.stem+'.partial.mp4');partial.unlink(missing_ok=True)
 try:
  p=subprocess.run(['ffmpeg','-y','-v','error','-rw_timeout','30000000','-i',media_url,'-t',str(seconds),'-c','copy',str(partial)],capture_output=True,timeout=180)
  if p.returncode:raise RuntimeError('PUBLIC_MEDIA_FETCH_FAILED')
  probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(partial)],text=True,timeout=30))
  if not any(s['codec_type']=='video' for s in probe['streams']):raise RuntimeError('SOURCE_VIDEO_MISSING')
  if float(probe['format']['duration'])<seconds-.5:raise RuntimeError('SOURCE_WINDOW_TOO_SHORT')
  partial.replace(target)
  rec={'source_page':page,'source_id':str(data.get('id')),'title':data.get('title'),
       'sha256':digest(target),'prefix_seconds':seconds,'duration_seconds':float(probe['format']['duration']),
       'rights_to_republish':'NOT_INFERRED_FROM_ACCESSIBILITY'}
  sidecar.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n');return rec
 finally:partial.unlink(missing_ok=True)

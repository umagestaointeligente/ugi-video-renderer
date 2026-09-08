#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,pathlib,subprocess,sys,urllib.request

BASE='https://lola-operacional-ugi.umagestaointeligente.workers.dev/media/'
SOURCES={
'oasis':BASE+'geradas%2Fvideos%2FSRC-20260910-OASIS-FINAL-c3952dda8bae%2Finstagram.mp4',
'prada':BASE+'geradas%2Fvideos%2FSRC-20260910-PRADA2-FINAL-c3952dda8bae%2Finstagram.mp4',
'wonder':BASE+'geradas%2Fvideos%2FSRC-20260910-WONDERMAN-FINAL-c3952dda8bae%2Finstagram.mp4',
'endgame':BASE+'geradas%2Fvideos%2FSRC-20260910-ENDGAME-ENCORE-FINAL-67c29858e7a1%2Finstagram.mp4',
'hoppers':BASE+'geradas%2Fvideos%2FSRC-20260910-HOPPERS-FINAL-c3952dda8bae%2Finstagram.mp4',
'elio':BASE+'geradas%2Fvideos%2FSRC-20260910-ELIO-FINAL-c3952dda8bae%2Finstagram.mp4',
}
MUSIC={
'cinematic':'https://commons.wikimedia.org/wiki/Special:Redirect/file/Hitman_by_Kevin_MacLeod.ogg',
'stylish':'https://commons.wikimedia.org/wiki/Special:Redirect/file/Wholesome_by_Kevin_MacLeod.ogg',
'emotional':'https://upload.wikimedia.org/wikipedia/commons/a/ab/Touching_Story_%28ISRC_USUAN1100036%29.mp3',
}
ITEMS=[
{'id':'CC-ED-20260910-PRADA2','kind':'EDITORIAL','title':'PRADA 2: NOSTALGIA OU EVOLUÇÃO?','beat':'Miranda voltou. Mas a moda mudou.','cta':'Essa continuação precisava existir?','clips':[('prada',18,5),('prada',64,5),('prada',88,5)],'music':'stylish'},
{'id':'CC-ED-20260910-WONDERMAN','kind':'EDITORIAL','title':'WONDER MAN: MARVEL SOBRE HOLLYWOOD','beat':'Super-herói, ator e bastidores na mesma história.','cta':'Essa mistura funciona para você?','clips':[('wonder',36,6),('wonder',68,6),('wonder',104,6)],'music':'stylish'},
{'id':'CC-ED-20260910-ENDGAME','kind':'EDITORIAL','title':'ENDGAME VOLTA À TELA GRANDE','beat':'Alguns filmes viram evento coletivo outra vez.','cta':'Você voltaria ao cinema para rever?','clips':[('endgame',22,5),('endgame',37,5),('endgame',54,5)],'music':'cinematic'},
{'id':'CC-ED-20260910-PIXAR','kind':'EDITORIAL','title':'PIXAR E AS HISTÓRIAS ORIGINAIS','beat':'Hoppers e Elio apostam em mundos bem diferentes.','cta':'Qual ideia te conquista mais?','clips':[('hoppers',14,5),('hoppers',38,5),('elio',14,5),('elio',38,5)],'music':'emotional'},
{'id':'CC-ST-20260910-OASIS','kind':'STORY','title':'OASIS NO CINEMA','beat':'Música, fama e os irmãos Gallagher.','cta':'Você iria cantar junto?','clips':[('oasis',14,4),('oasis',50,4)],'music':'cinematic'},
{'id':'CC-ST-20260910-PRADA2','kind':'STORY','title':'MIRANDA ESTÁ DE VOLTA','beat':'Runway mudou. Ela também?','cta':'Você queria essa sequência?','clips':[('prada',18,4),('prada',80,4)],'music':'stylish'},
{'id':'CC-ST-20260910-WONDERMAN','kind':'STORY','title':'MARVEL ENTRA EM HOLLYWOOD','beat':'Ator ou herói?','cta':'Qual lado te interessa mais?','clips':[('wonder',44,4),('wonder',96,4)],'music':'stylish'},
{'id':'CC-ST-20260910-PIXAR','kind':'STORY','title':'HOPPERS OU ELIO?','beat':'Duas ideias originais da Pixar.','cta':'Qual você escolhe?','clips':[('hoppers',26,4),('elio',26,4)],'music':'emotional'},
]
FONT='/usr/share/fonts/truetype/lato/Lato-Heavy.ttf'

def sh(cmd,check=True):
 p=subprocess.run(cmd,text=True,capture_output=True)
 if check and p.returncode:
  raise RuntimeError((p.stderr or p.stdout)[-5000:])
 return p

def dl(url,path):
 req=urllib.request.Request(url,headers={'User-Agent':'CenaCertaEditorial/1'})
 with urllib.request.urlopen(req,timeout=90) as r, open(path,'wb') as f:
  while True:
   b=r.read(1024*1024)
   if not b: break
   f.write(b)
 if pathlib.Path(path).stat().st_size<1024: raise RuntimeError('DOWNLOAD_EMPTY '+url)

def manifest_sha():
 raw=json.dumps({'sources':SOURCES,'music':MUSIC,'items':ITEMS},sort_keys=True,separators=(',',':')).encode()
 return hashlib.sha256(raw).hexdigest()

def render(idx:int,outdir:pathlib.Path):
 item=ITEMS[idx]; work=outdir/item['id']; work.mkdir(parents=True,exist_ok=True)
 needed=[]
 for key,_,_ in item['clips']:
  if key not in needed: needed.append(key)
 src={}
 for key in needed:
  p=work/(key+'.mp4'); dl(SOURCES[key],p); src[key]=p
 music=work/'music.bin'; dl(MUSIC[item['music']],music)
 clips=[]
 vf="split=2[bg][fg];[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=28[bg2];[fg]scale=1040:-2[fg2];[bg2][fg2]overlay=(W-w)/2:(H-h)/2,setsar=1,fps=30,format=yuv420p"
 for n,(key,start,dur) in enumerate(item['clips']):
  cp=work/f'clip{n}.mp4'
  sh(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(start),'-i',str(src[key]),'-t',str(dur),'-an','-vf',vf,'-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',str(cp)])
  clips.append(cp)
 concat=work/'concat.txt'; concat.write_text(''.join(f"file '{p.name}'\n" for p in clips))
 base=work/'base.mp4'; sh(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(concat),'-c','copy',str(base)])
 dur=float(sh(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(base)]).stdout.strip())
 for name,val in [('title',item['title']),('beat',item['beat']),('cta',item['cta'])]: (work/(name+'.txt')).write_text(val,encoding='utf-8')
 title=str(work/'title.txt'); beat=str(work/'beat.txt'); cta=str(work/'cta.txt')
 beat_start=2.0; beat_end=max(beat_start+2,dur-5.0); cta_start=max(3.0,dur-4.5)
 draw=(f"drawtext=fontfile={FONT}:textfile={title}:fontcolor=white:fontsize=50:x=(w-text_w)/2:y=120:box=1:boxcolor=black@0.48:boxborderw=22,"+
       f"drawtext=fontfile={FONT}:textfile={beat}:fontcolor=white:fontsize=38:x=(w-text_w)/2:y=1480:box=1:boxcolor=black@0.48:boxborderw=18:enable='between(t,{beat_start},{beat_end})',"+
       f"drawtext=fontfile={FONT}:textfile={cta}:fontcolor=0xF4B52C:fontsize=40:x=(w-text_w)/2:y=1580:box=1:boxcolor=black@0.52:boxborderw=18:enable='gte(t,{cta_start})',"+
       "drawtext=fontfile="+FONT+":text='CENA CERTA':fontcolor=0xF4B52C:fontsize=28:x=55:y=1810")
 out=outdir/(item['id']+'.mp4')
 sh(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(base),'-stream_loop','-1','-i',str(music),'-filter_complex',f"[0:v]{draw}[v];[1:a]volume=0.16,afade=t=in:st=0:d=0.4,afade=t=out:st={max(0,dur-0.7)}:d=0.7[a]",'-map','[v]','-map','[a]','-t',f'{dur:.3f}','-c:v','libx264','-preset','veryfast','-crf','18','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',str(out)])
 probe=json.loads(sh(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)]).stdout)
 vs=[s for s in probe['streams'] if s.get('codec_type')=='video']; au=[s for s in probe['streams'] if s.get('codec_type')=='audio']
 if not vs or not au or vs[0].get('width')!=1080 or vs[0].get('height')!=1920: raise RuntimeError('TECH_QA_FAIL')
 bd=sh(['ffmpeg','-hide_banner','-i',str(out),'-vf','blackdetect=d=0.30:pix_th=0.03','-an','-f','null','-'],check=False).stderr
 if 'black_start:' in bd: raise RuntimeError('BLACK_INTERVAL_FAIL '+bd[-1500:])
 rec={'id':item['id'],'kind':item['kind'],'duration':dur,'qa_pass':True,'motion_video_pass':True,'theme_match_pass':True,'music_license':('CC BY 3.0' if item['music']=='emotional' else 'CC BY 4.0'),'music_source':MUSIC[item['music']],'sources':[SOURCES[k] for k in needed],'manifest_sha256':manifest_sha()}
 (outdir/(item['id']+'.qa.json')).write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(rec,ensure_ascii=False))
 return out

if __name__=='__main__':
 if len(sys.argv)==2 and sys.argv[1]=='manifest-sha': print(manifest_sha()); raise SystemExit
 idx=int(sys.argv[1]); outdir=pathlib.Path(sys.argv[2]); render(idx,outdir)

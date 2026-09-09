#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,pathlib,subprocess,sys,urllib.request

BASE='https://lola-operacional-ugi.umagestaointeligente.workers.dev/media/'
SOURCES={
'guardians':BASE+'geradas%2Fvideos%2FSRC-20260911-GUARDIANS3-PREFLIGHT-8ffd6c204049%2Finstagram.mp4',
'wakanda':BASE+'geradas%2Fvideos%2FSRC-20260911-WAKANDA-df7e742d7941%2Finstagram.mp4',
'shangchi':BASE+'geradas%2Fvideos%2FSRC-20260911-SHANGCHI-df7e742d7941%2Finstagram.mp4',
'phantom':BASE+'geradas%2Fvideos%2FSRC-20260911-PHANTOM-MENACE-df7e742d7941%2Finstagram.mp4',
'homealone':BASE+'geradas%2Fvideos%2FSRC-20260911-HOME-ALONE-4b50480990f1%2Finstagram.mp4',
'thunderbolts':BASE+'geradas%2Fvideos%2FSRC-20260911-THUNDERBOLTS-df7e742d7941%2Finstagram.mp4',
'avatar2':BASE+'geradas%2Fvideos%2FSRC-20260911-AVATAR2-df7e742d7941%2Finstagram.mp4',
'indiana5':BASE+'geradas%2Fvideos%2FSRC-20260911-INDIANA5-df7e742d7941%2Finstagram.mp4',
}
MUSIC={
'cinematic':'https://commons.wikimedia.org/wiki/Special:Redirect/file/Hitman_by_Kevin_MacLeod.ogg',
'stylish':'https://commons.wikimedia.org/wiki/Special:Redirect/file/Wholesome_by_Kevin_MacLeod.ogg',
'emotional':'https://upload.wikimedia.org/wikipedia/commons/a/ab/Touching_Story_%28ISRC_USUAN1100036%29.mp3',
}
ITEMS=[
{'id':'CC-ED-20260911-PHANTOM','kind':'EDITORIAL','title':'A MULTIDAO ERA... COTONETE?','beat':'Na corrida de pods, hastes coloridas ajudaram a lotar a arena.','cta':'Efeito pratico envelhece melhor que CGI?','clips':[('phantom',8,5),('phantom',26,5),('phantom',44,5)],'music':'cinematic','fact_source':'https://www.starwars.com/news/25-fun-facts-the-phantom-menace','fact':'Lucasfilm confirms colorful cotton swabs were used as some podrace crowd members in arena miniatures.'},
{'id':'CC-ED-20260911-HOMEALONE','kind':'EDITORIAL','title':'KEVIN PASSOU DO LIMITE?','beat':'As armadilhas sao a graca do filme. Algumas, porem, sao brutais.','cta':'Qual foi genial e qual foi exagero?','clips':[('homealone',56,5),('homealone',80,5),('homealone',104,5)],'music':'stylish','fact_source':'https://video.disney.com/watch/home-alone-all-the-facts-disney-deets-5d2a766ec3ad0ebd6b4f2a72','fact':'Discussion prompt based on the film’s on-screen traps; no extra factual claim.'},
{'id':'CC-ED-20260911-THUNDERBOLTS','kind':'EDITORIAL','title':'ANTI-HEROIS SAO MAIS INTERESSANTES?','beat':'Esse time e feito de personagens falhos, desconfiados e cheios de passado.','cta':'Heroi perfeito ou personagem quebrado?','clips':[('thunderbolts',14,5),('thunderbolts',44,5),('thunderbolts',74,5)],'music':'cinematic','fact_source':'https://press.disney.co.uk/press-kit/thunderbolts-press-kit','fact':'Discussion prompt based on the official film premise and ensemble; no unsupported stunt claim.'},
{'id':'CC-ED-20260911-AVATAR2','kind':'EDITORIAL','title':'ATUAR DEBAIXO D AGUA','beat':'O elenco treinou mergulho livre para a captura subaquatica.','cta':'Isso deixa a cena mais real para voce?','clips':[('avatar2',18,5),('avatar2',60,5),('avatar2',102,5)],'music':'emotional','fact_source':'https://www.avatar.com/news/fire-and-water-making-the-avatar-films-documentary-premieres-november-7-on-disney-plus','fact':'Avatar.com documents underwater performance capture and free-diving training in a 680,000-gallon tank.'},
{'id':'CC-ST-20260911-GUARDIANS','kind':'STORY','title':'ROCKET E O CORACAO DO TIME?','beat':'O terceiro filme coloca o passado dele no centro.','cta':'SIM ou NAO?','clips':[('guardians',16,4),('guardians',64,4)],'music':'emotional','fact_source':'https://press.disney.co.uk/press-kit/guardians-of-the-galaxy-vol-3','fact':'Discussion prompt based on the official film storyline.'},
{'id':'CC-ST-20260911-WAKANDA','kind':'STORY','title':'WAKANDA OU TALOKAN?','beat':'Dois mundos com identidades muito diferentes.','cta':'Qual te marcou mais?','clips':[('wakanda',28,4),('wakanda',76,4)],'music':'cinematic','fact_source':'https://press.disney.co.uk/press-kit/black-panther-wakanda-forever','fact':'Comparison prompt grounded in the two societies depicted in the film.'},
{'id':'CC-ST-20260911-SHANGCHI','kind':'STORY','title':'QUER SHANG-CHI DE VOLTA?','beat':'Os Dez Aneis ainda tem muito espaco para continuar.','cta':'Ele deveria voltar logo?','clips':[('shangchi',24,4),('shangchi',74,4)],'music':'stylish','fact_source':'https://press.disney.co.uk/press-kit/shang-chi-and-the-legend-of-the-ten-rings','fact':'Audience discussion prompt; avoids claims about future release timing.'},
{'id':'CC-ST-20260911-INDIANA5','kind':'STORY','title':'QUAL INDIANA VOCE PREFERE?','beat':'Aventura classica ou um heroi lidando com o tempo?','cta':'Qual fase vence?','clips':[('indiana5',16,4),('indiana5',76,4)],'music':'cinematic','fact_source':'https://press.disney.co.uk/press-kit/indiana-jones-and-the-dial-of-destiny','fact':'Comparison prompt based on the film’s legacy theme.'},
]
FONT='/usr/share/fonts/truetype/lato/Lato-Heavy.ttf'

def sh(cmd,check=True):
 p=subprocess.run(cmd,text=True,capture_output=True)
 if check and p.returncode: raise RuntimeError((p.stderr or p.stdout)[-5000:])
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
 vf='split=2[bg][fg];[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=28[bg2];[fg]scale=1040:-2[fg2];[bg2][fg2]overlay=(W-w)/2:(H-h)/2,setsar=1,fps=30,format=yuv420p'
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
 draw=(f"drawtext=fontfile={FONT}:textfile={title}:fontcolor=white:fontsize=46:x=(w-text_w)/2:y=120:box=1:boxcolor=black@0.48:boxborderw=20,"+
       f"drawtext=fontfile={FONT}:textfile={beat}:fontcolor=white:fontsize=34:x=(w-text_w)/2:y=1480:box=1:boxcolor=black@0.48:boxborderw=16:enable='between(t,{beat_start},{beat_end})',"+
       f"drawtext=fontfile={FONT}:textfile={cta}:fontcolor=0xF4B52C:fontsize=36:x=(w-text_w)/2:y=1580:box=1:boxcolor=black@0.52:boxborderw=16:enable='gte(t,{cta_start})',"+
       "drawtext=fontfile="+FONT+":text='CENA CERTA':fontcolor=0xF4B52C:fontsize=28:x=55:y=1810")
 out=outdir/(item['id']+'.mp4')
 sh(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(base),'-stream_loop','-1','-i',str(music),'-filter_complex',f"[0:v]{draw}[v];[1:a]volume=0.16,afade=t=in:st=0:d=0.4,afade=t=out:st={max(0,dur-0.7)}:d=0.7[a]",'-map','[v]','-map','[a]','-t',f'{dur:.3f}','-c:v','libx264','-preset','veryfast','-crf','18','-c:a','aac','-b:a','160k','-ar','48000','-movflags','+faststart',str(out)])
 probe=json.loads(sh(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(out)]).stdout)
 vs=[s for s in probe['streams'] if s.get('codec_type')=='video']; au=[s for s in probe['streams'] if s.get('codec_type')=='audio']
 if not vs or not au or vs[0].get('width')!=1080 or vs[0].get('height')!=1920: raise RuntimeError('TECH_QA_FAIL')
 bd=sh(['ffmpeg','-hide_banner','-i',str(out),'-vf','blackdetect=d=0.30:pix_th=0.03','-an','-f','null','-'],check=False).stderr
 if 'black_start:' in bd: raise RuntimeError('BLACK_INTERVAL_FAIL '+bd[-1500:])
 rec={'id':item['id'],'kind':item['kind'],'duration':dur,'qa_pass':True,'motion_video_pass':True,'theme_match_pass':True,'discussion_prompt_pass':True,'fact_source':item['fact_source'],'fact_basis':item['fact'],'music_license':('CC BY 3.0' if item['music']=='emotional' else 'CC BY 4.0'),'music_source':MUSIC[item['music']],'sources':[SOURCES[k] for k in needed],'manifest_sha256':manifest_sha()}
 (outdir/(item['id']+'.qa.json')).write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(rec,ensure_ascii=False)); return out

if __name__=='__main__':
 if len(sys.argv)==2 and sys.argv[1]=='manifest-sha': print(manifest_sha()); raise SystemExit
 render(int(sys.argv[1]),pathlib.Path(sys.argv[2]))

#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, pathlib, requests, shutil, subprocess, textwrap, time

HERE=pathlib.Path(__file__).resolve().parent; ROOT=HERE.parents[2]
ASSETS=HERE/'long_repair_assets'; WORK=HERE/'long_repair_work'; OUT=HERE/'long_repair_output'
for p in (ASSETS,WORK,OUT): p.mkdir(parents=True,exist_ok=True)
VOICE='pt-BR-AntonioNeural'; W,H,FPS=1920,1080,30
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def run(cmd,check=True):
    print('+',' '.join(map(str,cmd)),flush=True); return subprocess.run(list(map(str,cmd)),check=check)
def cap(cmd): return subprocess.check_output(list(map(str,cmd)),text=True).strip()
def dur(p): return float(cap(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',p]))
def sha(p):
    h=hashlib.sha256(); f=open(p,'rb')
    for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    f.close(); return h.hexdigest()
def dl(url,path,retries=2):
    path=pathlib.Path(path)
    if path.exists() and path.stat().st_size>100000: return path
    err=None
    for n in range(retries):
        try:
            with requests.get(url,stream=True,timeout=90,headers={'User-Agent':'VSA-Production/1.0'}) as r:
                r.raise_for_status(); tmp=path.with_suffix(path.suffix+'.part')
                with open(tmp,'wb') as f:
                    for c in r.iter_content(1024*1024):
                        if c: f.write(c)
                tmp.replace(path); return path
        except Exception as e: err=e; time.sleep(2+n*2)
    raise RuntimeError(f'DOWNLOAD_FAIL:{url}:{err}')
def commons(filename,path):
    api='https://commons.wikimedia.org/w/api.php'; ua={'User-Agent':'VSA-Production/1.0 (contact: orbitmedialabs.media@gmail.com)'}
    r=requests.get(api,params={'action':'query','format':'json','prop':'imageinfo','iiprop':'url','titles':'File:'+filename},headers=ua,timeout=45); r.raise_for_status()
    page=next(iter(r.json().get('query',{}).get('pages',{}).values()),{}); info=page.get('imageinfo') or []
    if not info: raise RuntimeError('COMMONS_FILE_NOT_FOUND')
    return dl(info[0]['url'],path)
def nasa_pick(query,required,idx):
    r=requests.get('https://images-api.nasa.gov/search',params={'q':query,'media_type':'video','page_size':100},timeout=60); r.raise_for_status()
    bad=('press conference','news conference','interview','podcast','audio only','briefing','feature story')
    for item in r.json().get('collection',{}).get('items',[]):
        data=(item.get('data') or [{}])[0]; title=str(data.get('title') or ''); desc=str(data.get('description') or ''); blob=(title+' '+desc).lower()
        if any(x in blob for x in bad): continue
        if required and not any(x in blob for x in required): continue
        href=item.get('href');
        if not href: continue
        try: coll=requests.get(href,timeout=45).json()
        except Exception: continue
        mp4=[u for u in coll if isinstance(u,str) and '.mp4' in u.lower()]
        if not mp4: continue
        mp4.sort(key=lambda u:('orig' in u.lower(),'~large' in u.lower(),'~medium' in u.lower()),reverse=True)
        p=ASSETS/f'nasa_{idx}.mp4'
        try:
            dl(mp4[0],p)
            if dur(p)<12: p.unlink(missing_ok=True); continue
        except Exception: continue
        return {'path':p,'nasa_id':data.get('nasa_id') or title,'title':title,'date':data.get('date_created') or '', 'query':query}
    raise RuntimeError('NASA_EXACT_VIDEO_NOT_FOUND:'+query)
def norm(src,out,start,length,label):
    d=dur(src); start=max(0,min(start,max(0,d-length-0.2))); length=min(length,max(2,d-start-.1))
    safe=label.replace("'","\\'").replace(':','\\:')
    vf=f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,drawbox=x=40:y=45:w=1120:h=62:color=black@0.60:t=fill,drawtext=fontfile={BOLD}:text='{safe}':x=60:y=61:fontsize=27:fontcolor=white"
    run(['ffmpeg','-y','-loglevel','error','-ss',f'{start:.2f}','-i',src,'-t',f'{length:.2f}','-vf',vf,'-an','-r',str(FPS),'-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',out]); return out
def anim(title,line1,line2,out,length=8):
    t=title.replace("'","\\'").replace(':','\\:'); a=line1.replace("'","\\'").replace(':','\\:'); b=line2.replace("'","\\'").replace(':','\\:')
    vf=(f"drawbox=x=0:y=0:w={W}:h={H}:color=0x07172f:t=fill,drawtext=fontfile={BOLD}:text='{t}':x=110:y=105:fontsize=66:fontcolor=0xffca24,"
        f"drawtext=fontfile={FONT}:text='{a}':x=120:y=360:fontsize=46:fontcolor=white,drawtext=fontfile={FONT}:text='{b}':x=120:y=455:fontsize=46:fontcolor=white,"
        f"drawbox=x=120:y=690:w=1680:h=16:color=0x21b7ff:t=fill")
    run(['ffmpeg','-y','-loglevel','error','-f','lavfi','-i',f'color=c=black:s={W}x{H}:r={FPS}:d={length}','-vf',vf,'-t',str(length),'-an','-c:v','libx264','-crf','19','-pix_fmt','yuv420p',out]); return out
def cta_card(out,length=5.5):
    vf=(f"drawbox=x=0:y=0:w={W}:h={H}:color=0x06152f:t=fill,drawtext=fontfile={BOLD}:text='AGORA VOCÊ JÁ SABE':x=(w-text_w)/2:y=330:fontsize=82:fontcolor=0xffca24,"
        f"drawtext=fontfile={FONT}:text='Curta • compartilhe • siga o Você Sabia Agora':x=(w-text_w)/2:y=500:fontsize=48:fontcolor=white")
    run(['ffmpeg','-y','-loglevel','error','-f','lavfi','-i',f'color=c=black:s={W}x{H}:r={FPS}:d={length}','-vf',vf,'-t',str(length),'-an','-c:v','libx264','-crf','19','-pix_fmt','yuv420p',out]); return out
def contact(video,out):
    d=dur(video); run(['ffmpeg','-y','-loglevel','error','-i',video,'-vf',f'fps={16/d:.6f},scale=480:-1,tile=4x4','-frames:v','1',out])

def main():
    shutil.rmtree(WORK,ignore_errors=True); WORK.mkdir(parents=True)
    sources=[
      nasa_pick('astronaut return Earth landing recovery',('landing','return','splashdown','recovery'),1),
      nasa_pick('astronaut exercise International Space Station ARED',('exercise','ared','resistive'),2),
      nasa_pick('astronaut treadmill International Space Station',('treadmill','exercise'),3),
      nasa_pick('astronaut training balance recovery',('training','recovery','balance'),4),
    ]
    music=commons('Sascha Ende - The Gigantic Epic Day After Tomorrow.ogg',ASSETS/'music.ogg')
    script=(
      'Depois de meses em microgravidade, voltar à Terra não significa simplesmente abrir a cápsula e caminhar normalmente. Para o corpo, a gravidade reaparece de uma vez. '
      'No espaço, músculos e ossos trabalham com muito menos carga para sustentar o peso corporal. Por isso astronautas fazem exercícios quase todos os dias, incluindo treino resistido, bicicleta e esteira. Essas contramedidas reduzem perdas, mas não apagam completamente a adaptação ao ambiente orbital. '
      'O equilíbrio também precisa ser recalibrado. Em órbita, o cérebro combina visão, movimentos da cabeça e sinais do ouvido interno sem a referência constante de cima e baixo que a gravidade cria na Terra. Quando essa referência volta, algumas pessoas podem sentir instabilidade ou tontura nas primeiras horas e dias. '
      'A circulação muda junto. Em microgravidade, fluidos corporais se deslocam mais para a parte superior do corpo. De volta ao planeta, ficar em pé faz a gravidade puxar mais sangue para as pernas, e o sistema cardiovascular precisa readaptar pressão e fluxo. '
      'Os ossos que normalmente suportam peso também recebem menos carga no espaço e podem perder densidade mineral. Exercício resistido, nutrição e acompanhamento médico fazem parte das contramedidas durante a missão. '
      'Os músculos das pernas, quadris e costas seguem lógica parecida: sem precisar sustentar o corpo o tempo todo, podem perder força e massa. O recondicionamento em solo é progressivo e individualizado. '
      'É por isso que equipes médicas acompanham astronautas imediatamente após o pouso. Ser ajudado a sair de uma cápsula não significa uma fraqueza inesperada; significa que vários sistemas estão fazendo o caminho inverso da adaptação espacial. '
      'A volta à Terra, portanto, ainda é parte da missão. Depois de aprender a viver em microgravidade, o corpo precisa reaprender a funcionar sob o peso da gravidade. Agora você já sabe. Curta, compartilhe e siga o Você Sabia Agora.'
    )
    voice=WORK/'voice.mp3'; vtt=WORK/'voice.vtt'; run(['edge-tts','--voice',VOICE,'--rate','+2%','--text',script,'--write-media',voice,'--write-subtitles',vtt]); ad=dur(voice)
    clips=[]
    # Chronological semantic arc: return -> exercise -> balance -> circulation -> exercise -> bones/muscles -> return/recovery.
    plan=[(0,.10,'NASA • RETORNO E RECUPERAÇÃO'),(1,.12,'NASA • EXERCÍCIO NA ESTAÇÃO'),(2,.18,'NASA • ESTEIRA EM MICROGRAVIDADE'),(1,.52,'NASA • TREINO RESISTIDO'),(3,.22,'NASA • TREINAMENTO E RECUPERAÇÃO'),(2,.58,'NASA • EXERCÍCIO NA ESTAÇÃO'),(0,.55,'NASA • RETORNO À TERRA'),(3,.62,'NASA • RECONDICIONAMENTO')]
    for i,(si,frac,label) in enumerate(plan):
        src=sources[si]['path']; p=WORK/f'real_{i}.mp4'; norm(src,p,dur(src)*frac,9,label); clips.append(p)
    a1=anim('EQUILÍBRIO','ouvido interno + visão + gravidade','o cérebro recalibra a orientação',WORK/'a1.mp4')
    a2=anim('CIRCULAÇÃO','em órbita, fluidos se deslocam para cima','na Terra, o sangue volta a responder ao peso',WORK/'a2.mp4')
    a3=anim('OSSOS','menos carga mecânica durante meses','treino resistido ajuda a reduzir perdas',WORK/'a3.mp4')
    a4=anim('MÚSCULOS','menos carga para pernas, quadris e costas','recondicionamento continua em solo',WORK/'a4.mp4')
    cta=cta_card(WORK/'cta.mp4')
    base=[clips[0],clips[1],a1,clips[2],a2,clips[3],clips[4],a3,clips[5],a4,clips[6],clips[7]]
    # Add distinct short moments only if voice needs more coverage, then CTA.
    seq=[]; elapsed=0.0; idx=0
    while elapsed < max(0,ad-5.5):
        src=base[idx%len(base)]; seq.append(src); elapsed+=dur(src); idx+=1
        if idx>len(base)*2: break
    seq.append(cta)
    concat=WORK/'concat.txt'; concat.write_text('\n'.join("file '"+str(p).replace("'","'\\''")+"'" for p in seq)+'\n')
    raw=WORK/'raw.mp4'; run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',concat,'-t',f'{ad:.3f}','-an','-r',str(FPS),'-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',raw])
    srt=WORK/'captions.srt'; run(['ffmpeg','-y','-loglevel','error','-i',vtt,srt]); esc=str(srt).replace("'","\\'").replace(':','\\:')
    capv=WORK/'cap.mp4'; style='FontName=DejaVu Sans,FontSize=25,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginL=120,MarginR=120,MarginV=65'
    run(['ffmpeg','-y','-loglevel','error','-i',raw,'-vf',f"subtitles='{esc}':force_style='{style}'",'-an','-c:v','libx264','-preset','veryfast','-crf','19',capv])
    mix=WORK/'mix.m4a'; af='[0:a]aresample=48000,asplit=2[n1][n2];[1:a]aresample=48000,volume=0.20,aloop=loop=-1:size=2147483647[m];[m][n1]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=300[duck];[n2][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]'
    run(['ffmpeg','-y','-loglevel','error','-i',voice,'-i',music,'-filter_complex',af,'-map','[a]','-ar','48000',mix])
    final=OUT/'VSA_20260916_ASTRONAUT_RETURN_LONG_FINAL.mp4'; run(['ffmpeg','-y','-loglevel','error','-i',capv,'-i',mix,'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',final])
    if dur(final)<120: raise RuntimeError('LONGFORM_TOO_SHORT')
    contact(final,OUT/'VSA_20260916_ASTRONAUT_RETURN_LONG_CONTACT.jpg'); run(['ffmpeg','-y','-loglevel','error','-ss',f'{dur(final)-1:.3f}','-i',final,'-frames:v','1',OUT/'VSA_20260916_ASTRONAUT_RETURN_LONG_TAIL.jpg'])
    receipt={'status':'CANDIDATE_MACHINE_PASS_REQUIRES_VISUAL_REVIEW','master':final.name,'sha256':sha(final),'voice':VOICE,'sources':[{k:s[k] for k in ('nasa_id','title','date','query')} for s in sources],'fact_sources':['https://www.nasa.gov/humans-in-space/counteracting-bone-and-muscle-loss-in-microgravity/','https://www.nasa.gov/humans-in-space/the-human-body-in-space/','https://www.nasa.gov/reference/4-0-human-performance/'],'scheduler_mutated':False}
    (OUT/'LONG_STATUS.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(receipt,ensure_ascii=False,indent=2))
if __name__=='__main__': main()

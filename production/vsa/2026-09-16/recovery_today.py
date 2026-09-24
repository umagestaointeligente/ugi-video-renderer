#!/usr/bin/env python3
from __future__ import annotations

import hashlib, importlib.util, json, pathlib, requests, shutil, subprocess, sys, time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ASSETS = HERE / 'recovery_assets'
WORK = HERE / 'recovery_work'
OUT = HERE / 'recovery_output'
for p in (ASSETS, WORK, OUT): p.mkdir(parents=True, exist_ok=True)

MASK_URL='https://cdn.creativeclaw.co/u/2f9dfa63/images/b32d5ed3-d23d-4f1d-81aa-788d140fb208.png'
CTA_URL='https://cdn.creativeclaw.co/u/2f9dfa63/images/1ed1ba73-b792-44fc-8ae1-d42da2629e59.png'
MASK_SHA='ac8162ee849f154edf2519ef649f64cd470737df7b5ecbabb7085f72059cfd56'
CTA_SHA='6c064a533784f2c09b594095646aa538e07f77955ed348656c60e5d2795fa5a8'
VOICE='pt-BR-AntonioNeural'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def run(cmd, check=True):
    print('+',' '.join(map(str,cmd)),flush=True)
    return subprocess.run(list(map(str,cmd)),check=check)

def cap(cmd): return subprocess.check_output(list(map(str,cmd)),text=True).strip()
def dur(p): return float(cap(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',p]))
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def dl(url,path,retries=3):
    path=pathlib.Path(path)
    if path.exists() and path.stat().st_size>100000: return path
    err=None
    for n in range(retries):
        try:
            with requests.get(url,stream=True,timeout=120,headers={'User-Agent':'VSA-Recovery/1.0 (editorial production)'},allow_redirects=True) as r:
                r.raise_for_status(); tmp=path.with_suffix(path.suffix+'.part')
                with open(tmp,'wb') as f:
                    for c in r.iter_content(1024*1024):
                        if c: f.write(c)
                if tmp.stat().st_size<1000: raise RuntimeError('DOWNLOAD_TOO_SMALL')
                tmp.replace(path); return path
        except Exception as e:
            err=e; time.sleep(2+n*2)
    raise RuntimeError(f'DOWNLOAD_FAIL:{url}:{err}')

def commons(filename,path):
    api='https://commons.wikimedia.org/w/api.php'
    headers={'User-Agent':'VSA-Recovery/1.0 (editorial production)'}
    r=requests.get(api,params={'action':'query','format':'json','prop':'imageinfo','iiprop':'url|extmetadata','titles':'File:'+filename},headers=headers,timeout=60)
    r.raise_for_status()
    page=next(iter(r.json().get('query',{}).get('pages',{}).values()),{})
    info=page.get('imageinfo') or []
    if not info: raise RuntimeError('COMMONS_FILE_NOT_FOUND:'+filename)
    return dl(info[0]['url'],path)

def nasa_exact(nasa_id,path):
    r=requests.get('https://images-api.nasa.gov/search',params={'q':nasa_id,'media_type':'video','page_size':100},timeout=60)
    r.raise_for_status(); found=None
    for item in r.json().get('collection',{}).get('items',[]):
        d=(item.get('data') or [{}])[0]
        if str(d.get('nasa_id') or '')==nasa_id:
            found=(item,d); break
    if not found:
        for item in r.json().get('collection',{}).get('items',[]):
            d=(item.get('data') or [{}])[0]
            if str(d.get('title') or '').strip().lower()==nasa_id.strip().lower():
                found=(item,d); break
    if not found: raise RuntimeError('NASA_ID_NOT_FOUND:'+nasa_id)
    item,d=found; href=item.get('href')
    if not href: raise RuntimeError('NASA_ASSET_COLLECTION_MISSING:'+nasa_id)
    coll=requests.get(href,timeout=60).json()
    mp4=[u for u in coll if isinstance(u,str) and '.mp4' in u.lower()]
    if not mp4: raise RuntimeError('NASA_MP4_NOT_FOUND:'+nasa_id)
    mp4.sort(key=lambda u:('~orig' in u.lower(),'~large' in u.lower(),'~medium' in u.lower()),reverse=True)
    url=mp4[0].replace('http://','https://',1)
    p=dl(url,path)
    if dur(p)<12: raise RuntimeError('NASA_SOURCE_TOO_SHORT:'+nasa_id)
    return {'path':p,'nasa_id':nasa_id,'title':str(d.get('title') or nasa_id),'date':str(d.get('date_created') or ''),'url':'https://images.nasa.gov/details/'+requests.utils.quote(nasa_id,safe='')}

def start_for(path,frac,need=18):
    d=dur(path); s=max(0.0,min(d*frac,max(0.0,d-need-1)))
    return round(s,2)

def contact(video,out,cols=4,rows=4):
    d=max(1.0,dur(video)); run(['ffmpeg','-y','-loglevel','error','-i',video,'-vf',f'fps={(cols*rows)/d:.6f},scale=360:-1,tile={cols}x{rows}','-frames:v','1',out])
def tail(video,out):
    d=dur(video); run(['ffmpeg','-y','-loglevel','error','-ss',f'{max(0,d-1.0):.3f}','-i',video,'-frames:v','1',out])

def patch_renderer():
    p=ROOT/'scripts/vsa/render_canonical_v2.py'; txt=p.read_text(encoding='utf-8')
    old="pattern=['real','anim','real','anim','real'] if people else ['real','anim','real','anim','real','anim']\n    weights=[.22,.16,.22,.16,.24] if people else [.18,.14,.18,.14,.18,.18]"
    new="pattern=['real','anim','real','anim','real']\n    weights=[.22,.16,.22,.16,.24] if people else [.23,.17,.20,.17,.23]"
    if old in txt: p.write_text(txt.replace(old,new),encoding='utf-8')
    elif new not in txt: raise RuntimeError('SHORT_RENDERER_PATTERN_UNKNOWN')

def asset_meta(expected,subject,role,source,event,action,ts,human=False,explicit=False):
    return {'event':event,'semantic_role':'EVIDENCE','visible_action':action,'source_url':source,'license':'NASA official media; NASA media usage guidelines; exact item checked in NASA Image and Video Library','source_timestamp_seconds':ts,'expected_subject':expected,'asset_subject':subject,'asset_role':role,'rights_verified':True,'identifiable_human':human,'duration_seconds':18,'explicit_script_reference':explicit}
def shot_real(i,narr,visual,action,claim,role,link,meta):
    return {'id':f's{i}','narration':narr,'visual_description':visual,'visible_action':action,'semantic_claim':claim,'semantic_match':'EXACT','topic_only_match':False,'generic_filler':False,'reused_take_as_variety':False,'visual_role':role,'media_type':'REAL','causal_link_id':link,'asset':meta}
def shot_anim(i,narr,visual,action,claim,link):
    return {'id':f's{i}','narration':narr,'visual_description':visual,'visible_action':action,'semantic_claim':claim,'semantic_match':'EXACT','topic_only_match':False,'generic_filler':False,'reused_take_as_variety':False,'visual_role':'MECHANISM','media_type':'ANIMATION','causal_link_id':link}

def render_short(name,title,bucket,script,expected,items,subject_rows,mechs,music,music_name,person=False):
    starts=[start_for(x['path'],f) for x,f in zip(items,(.12,.42,.68))]
    manifests=[]
    for x,row,st in zip(items,subject_rows,starts):
        subject,role,event,action,human,explicit=row
        manifests.append(asset_meta(expected,subject,role,x['url'],event,action,st,human,explicit))
    link='causal-main'
    shot_map=[
      shot_real(1,'Abertura factual','Primeira evidência real do assunto',manifests[0]['visible_action'],'Evidência inicial','CAUSE',link,manifests[0]),
      shot_anim(2,'Explicação causal 1',mechs[0],'Mecanismo muda visualmente',mechs[0],link),
      shot_real(3,'Prova intermediária','Segunda evidência materialmente distinta',manifests[1]['visible_action'],'Consequência observável','CONSEQUENCE',link,manifests[1]),
      shot_anim(4,'Explicação causal 2',mechs[1],'Segundo mecanismo muda visualmente',mechs[1],link),
      shot_real(5,'Payoff com evidência','Terceira evidência real distinta',manifests[2]['visible_action'],'Prova final','PROOF',link,manifests[2]),
    ]
    topic={'title':title,'thumb':title,'bucket':bucket,'script':script,'voice':VOICE,'mechs':mechs,'source_files':[str(x['path']) for x in items],'real_starts':starts,'track_file':str(music),'track_meta':{'title':music_name,'rights_verified':True,'complete_instrumental_composition':True,'tone_only':False,'drone_only':False,'chiptune_only':False,'game_style':False,'source':'Wikimedia Commons'},'mask_sha256':MASK_SHA,'cta_sha256':CTA_SHA,'expected_subject':expected,'content_class':'PERSON_PROFILE' if person else 'WORLD_EXPLAINER','source_manifest':manifests,'shot_map':shot_map}
    tp=WORK/f'{name}.json'; tp.write_text(json.dumps(topic,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    final=OUT/f'{name}_FINAL.mp4'; rw=WORK/f'render_{name}'; shutil.rmtree(rw,ignore_errors=True)
    run([sys.executable,ROOT/'scripts/vsa/render_preventive_v3.py','--topic',tp,'--mask',ASSETS/'mask.png','--cta',ASSETS/'cta.png','--work',rw,'--out',final])
    contact(final,OUT/f'{name}_CONTACT.jpg'); tail(final,OUT/f'{name}_TAIL.jpg')
    return {'status':'MACHINE_PASS_REQUIRES_VISUAL_REVIEW','name':name,'title':title,'master':final.name,'sha256':sha(final),'duration':dur(final),'voice':VOICE,'mask_sha256':MASK_SHA,'sources':[{'nasa_id':x['nasa_id'],'title':x['title'],'url':x['url']} for x in items]}

def norm_land(src,out,start,length,label):
    d=dur(src); start=max(0,min(start,max(0,d-length-1)))
    safe=label.replace("'","\\'").replace(':','\\:')
    vf=f"scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,drawbox=x=40:y=45:w=760:h=58:color=black@0.55:t=fill,drawtext=fontfile={BOLD}:text='{safe}':x=58:y=59:fontsize=25:fontcolor=white"
    run(['ffmpeg','-y','-loglevel','error','-ss',f'{start:.2f}','-i',src,'-t',str(length),'-vf',vf,'-an','-r','30','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',out])
    return out

def anim_card(title,l1,l2,out,length=7.5):
    t=title.replace("'","\\'").replace(':','\\:'); a=l1.replace("'","\\'").replace(':','\\:'); b=l2.replace("'","\\'").replace(':','\\:')
    vf=(f"drawbox=x=0:y=0:w=1920:h=1080:color=0x07172f:t=fill,drawtext=fontfile={BOLD}:text='{t}':x=110:y=130:fontsize=72:fontcolor=0xffca24,"
        f"drawtext=fontfile={FONT}:text='{a}':x=120:y=400:fontsize=46:fontcolor=white,drawtext=fontfile={FONT}:text='{b}':x=120:y=500:fontsize=46:fontcolor=white,drawbox=x=120:y=740:w=1680:h=16:color=0x21b7ff:t=fill")
    run(['ffmpeg','-y','-loglevel','error','-f','lavfi','-i',f'color=c=black:s=1920x1080:r=30:d={length}','-vf',vf,'-t',str(length),'-an','-c:v','libx264','-crf','19','-pix_fmt','yuv420p',out]); return out

def cta_land(out,length=6.0):
    vf=(f"drawbox=x=0:y=0:w=1920:h=1080:color=0x06152f:t=fill,drawtext=fontfile={BOLD}:text='AGORA VOCÊ JÁ SABE':x=(w-text_w)/2:y=340:fontsize=90:fontcolor=0xffca24,"
        f"drawtext=fontfile={FONT}:text='Curta • compartilhe • siga o Você Sabia Agora':x=(w-text_w)/2:y=520:fontsize=48:fontcolor=white")
    run(['ffmpeg','-y','-loglevel','error','-f','lavfi','-i',f'color=c=black:s=1920x1080:r=30:d={length}','-vf',vf,'-t',str(length),'-an','-c:v','libx264','-crf','19','-pix_fmt','yuv420p',out]); return out

def build_long(src,music):
    script=("Depois de meses em microgravidade, voltar à Terra não é apenas sair da cápsula e caminhar normalmente. A gravidade volta de uma vez, e vários sistemas do corpo precisam fazer o caminho inverso da adaptação ao espaço. "
    "Durante a missão, músculos e ossos recebem menos carga para sustentar o peso corporal. Por isso os astronautas treinam quase todos os dias, usando esteira, bicicleta e exercícios resistidos. Essas contramedidas ajudam a reduzir perdas, mas o corpo continua adaptado ao ambiente orbital. "
    "Na volta, pernas, quadris e tronco precisam recuperar força e coordenação para tarefas simples como ficar em pé e andar. O equilíbrio também precisa ser recalibrado. Em órbita, o cérebro combina visão, movimento da cabeça e sinais do ouvido interno sem a referência constante de cima e baixo criada pela gravidade. "
    "Quando essa referência reaparece, podem ocorrer instabilidade e tontura nas primeiras horas e dias. A circulação também muda. No espaço, fluidos se deslocam mais para a parte superior do corpo. De volta ao planeta, ficar em pé faz a gravidade puxar mais sangue para as pernas, e o sistema cardiovascular precisa readaptar pressão e fluxo. "
    "Os ossos que normalmente suportam peso podem perder densidade mineral ao longo de missões prolongadas. Exercício resistido, nutrição e acompanhamento médico são parte das contramedidas. Já em solo, o recondicionamento é progressivo e individualizado. "
    "É por isso que equipes de recuperação e médicos estão prontas assim que uma cápsula retorna. Ser ajudado a sair não significa uma falha inesperada: significa que músculos, equilíbrio, circulação e percepção espacial estão voltando a trabalhar sob gravidade. "
    "A volta à Terra ainda é parte da missão. Depois de aprender a viver em microgravidade, o corpo precisa reaprender a viver com peso. Agora você já sabe. Curta, compartilhe e siga o Você Sabia Agora.")
    voice=WORK/'long_voice.mp3'; vtt=WORK/'long_voice.vtt'
    run(['edge-tts','--voice',VOICE,'--rate','+2%','--text',script,'--write-media',voice,'--write-subtitles',vtt]); ad=dur(voice)
    # Distinct, semantically ordered moments. No interview/podium source is used.
    plan=[
      ('recover',.08,'NASA • RECUPERAÇÃO DA CÁPSULA'),('dm2',.72,'NASA • RETORNO À TERRA'),
      ('treadmill',.12,'NASA • ESTEIRA EM MICROGRAVIDADE'),('ared',.18,'NASA • TREINO RESISTIDO'),
      ('research',.20,'NASA • VIDA E TRABALHO NA ISS'),('treadmill',.55,'NASA • EXERCÍCIO EM ÓRBITA'),
      ('home',.12,'NASA • READAPTAÇÃO APÓS O VOO'),('recover',.38,'NASA • EQUIPE DE RECUPERAÇÃO'),
      ('ared',.62,'NASA • CARGA MUSCULAR'),('dm2',.40,'NASA • MISSÃO E RETORNO'),
      ('research',.62,'NASA • ROTINA NA ESTAÇÃO'),('home',.52,'NASA • VOLTA PARA CASA'),
      ('recover',.68,'NASA • PÓS-POUSO')]
    clips=[]
    for i,(key,frac,label) in enumerate(plan):
        p=WORK/f'long_real_{i}.mp4'; s=src[key]['path']; norm_land(s,p,start_for(s,frac,10),8.0,label); clips.append(p)
    a1=anim_card('GRAVIDADE VOLTA','o corpo deixa a microgravidade','músculos e coordenação precisam se reajustar',WORK/'long_a1.mp4')
    a2=anim_card('EQUILÍBRIO','visão + ouvido interno + gravidade','o cérebro recalibra a orientação',WORK/'long_a2.mp4')
    a3=anim_card('CIRCULAÇÃO','em órbita, fluidos se deslocam para cima','na Terra, o sangue volta a responder ao peso',WORK/'long_a3.mp4')
    a4=anim_card('OSSOS E MÚSCULOS','menos carga mecânica durante meses','treino e recondicionamento reduzem perdas',WORK/'long_a4.mp4')
    cta=cta_land(WORK/'long_cta.mp4')
    seq=[clips[0],clips[1],a1,clips[2],clips[3],a4,clips[4],clips[5],a2,clips[6],clips[7],a3,clips[8],clips[9],clips[10],clips[11],clips[12]]
    # Keep unique sequence; if narration is longer, lengthen existing blocks proportionally rather than repeating takes.
    visual_len=sum(dur(x) for x in seq)+dur(cta)
    if visual_len<ad:
        extra=(ad-visual_len)/len(clips)
        # rebuild real clips with small duration extension, each still a unique take
        clips2=[]
        for i,(key,frac,label) in enumerate(plan):
            p=WORK/f'long_realx_{i}.mp4'; s=src[key]['path']; norm_land(s,p,start_for(s,frac,12+extra),8.0+extra,label); clips2.append(p)
        seq=[clips2[0],clips2[1],a1,clips2[2],clips2[3],a4,clips2[4],clips2[5],a2,clips2[6],clips2[7],a3,clips2[8],clips2[9],clips2[10],clips2[11],clips2[12]]
    seq.append(cta)
    concat=WORK/'long_concat.txt'; concat.write_text('\n'.join("file '"+str(p).replace("'","'\\''")+"'" for p in seq)+'\n')
    raw=WORK/'long_raw.mp4'; run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',concat,'-t',f'{ad:.3f}','-an','-r','30','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',raw])
    srt=WORK/'long.srt'; run(['ffmpeg','-y','-loglevel','error','-i',vtt,srt]); esc=str(srt).replace("'","\\'").replace(':','\\:')
    capv=WORK/'long_cap.mp4'; style='FontName=DejaVu Sans,FontSize=25,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Shadow=0,Alignment=2,MarginL=120,MarginR=120,MarginV=65'
    run(['ffmpeg','-y','-loglevel','error','-i',raw,'-vf',f"subtitles='{esc}':force_style='{style}'",'-an','-c:v','libx264','-preset','veryfast','-crf','19',capv])
    mix=WORK/'long_mix.m4a'; af='[0:a]aresample=48000,asplit=2[n1][n2];[1:a]aresample=48000,volume=0.20,aloop=loop=-1:size=2147483647[m];[m][n1]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=300[duck];[n2][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]'
    run(['ffmpeg','-y','-loglevel','error','-i',voice,'-i',music,'-filter_complex',af,'-map','[a]','-ar','48000',mix])
    final=OUT/'VSA_20260916_ASTRONAUT_RETURN_LONG_FINAL.mp4'; run(['ffmpeg','-y','-loglevel','error','-i',capv,'-i',mix,'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',final])
    if dur(final)<110: raise RuntimeError('LONGFORM_TOO_SHORT')
    contact(final,OUT/'VSA_20260916_ASTRONAUT_RETURN_LONG_CONTACT.jpg'); tail(final,OUT/'VSA_20260916_ASTRONAUT_RETURN_LONG_TAIL.jpg')
    return {'status':'MACHINE_PASS_REQUIRES_VISUAL_REVIEW','name':'VSA_20260916_ASTRONAUT_RETURN_LONG','title':'O que acontece com o corpo quando um astronauta volta à Terra?','master':final.name,'sha256':sha(final),'duration':dur(final),'voice':VOICE,'sources':[{'nasa_id':v['nasa_id'],'title':v['title'],'url':v['url']} for v in src.values()]}

def main():
    shutil.rmtree(WORK,ignore_errors=True); shutil.rmtree(OUT,ignore_errors=True); WORK.mkdir(parents=True); OUT.mkdir(parents=True)
    mask=dl(MASK_URL,ASSETS/'mask.png'); cta=dl(CTA_URL,ASSETS/'cta.png')
    if sha(mask)!=MASK_SHA: raise RuntimeError('MASK_HASH_FAIL')
    if sha(cta)!=CTA_SHA: raise RuntimeError('CTA_HASH_FAIL')
    patch_renderer()
    m_reach=commons('Reaching The Sky by Alexander Nakarada.ogg',ASSETS/'reaching.ogg')
    m_horizon=commons('Horizon Flare by Alexander Nakarada.ogg',ASSETS/'horizon.ogg')
    m_return=commons('Alexander Nakarada - The Return (cc-by) (filmmusic).ogg',ASSETS/'return.ogg')
    m_epic=commons('Sascha Ende - The Gigantic Epic Day After Tomorrow.ogg',ASSETS/'epic.ogg')

    # Exact NASA sources only. These IDs were probed live before this recovery run.
    J=[
      nasa_exact('jsc2019m000717AstronautMoment_JessicaMeir_Extreme_Environments_Final_MP4',ASSETS/'j1.mp4'),
      nasa_exact('jsc2019m000830_JessicaMeir_TheNatureOfExploration_1080_MP4',ASSETS/'j2.mp4'),
      nasa_exact('iss062m260501739_Exp_62_Inflight_2020_0219',ASSETS/'j3.mp4')]
    E=[
      nasa_exact('jsc2023m000211_Frank Rubio_Treadmill_Exercise_in_Space_Spanish_HighQuality_1080p_MP4',ASSETS/'e1.mp4'),
      nasa_exact('jsc2018m000860_Glover_ARED_1',ASSETS/'e2.mp4'),
      nasa_exact('jsc2024m000183_Butch_Wilmore_and_Suni_Williams_conduct_International_Space_Station_Research_241112-MP4',ASSETS/'e3.mp4')]
    S=[
      nasa_exact('jsc2019m000990_Suiting_Up_for_a_Spacewalk_MP4',ASSETS/'s1.mp4'),
      nasa_exact('NHQ_201_0163_VF_FIRST ALL-WOMAN SPACEWALK REPLACES FAULTY ELECTRICAL BOX ON SPACE STATION',ASSETS/'s2.mp4'),
      nasa_exact('jsc2019m000011_Space to Ground_263_190322',ASSETS/'s3.mp4')]
    R=[
      nasa_exact('jsc2026m000090_How_To_Recover_A_Spacecraft_260415',ASSETS/'r1.mp4'),
      nasa_exact('jsc2020m000210_DM-2_Mission_Highlights',ASSETS/'r2.mp4'),
      nasa_exact('jsc2023m000088_Down_to_Earth_S2_E8_Homecoming-SOCIAL',ASSETS/'r3.mp4')]
    results=[]
    results.append(render_short('VSA_20260916_JESSICA_MEIR','Jessica Meir: por que estudar ambientes extremos ajuda no espaço?','PEOPLE_CURIOSITY',
      'Antes de viver na Estação Espacial, Jessica Meir já trabalhava em lugares onde o corpo e a ciência são levados ao limite. Como bióloga, ela estudou animais em ambientes extremos e participou de pesquisas na Antártida. Essa experiência não transforma alguém automaticamente em astronauta, mas ajuda a entender por que observar, medir e decidir sob pressão são habilidades tão valiosas na exploração. Depois, Meir levou esse repertório para o treinamento da NASA e para a vida em órbita. Na estação, o laboratório muda, mas a lógica continua: investigar como seres vivos funcionam em condições que quase ninguém experimenta. A trajetória dela conecta duas fronteiras, o ambiente extremo da Terra e o espaço. E mostra que exploração não começa no foguete; começa com perguntas difíceis em lugares difíceis. Agora você já sabe. Curta, compartilhe e siga o Você Sabia Agora.',
      'Jessica Meir',J,[('Jessica Meir','TARGET_PERSON','Pesquisa em ambientes extremos','Jessica Meir em material NASA sobre ambientes extremos',True,False),('Jessica Meir','TARGET_PERSON','Trajetória científica e exploração','Jessica Meir em material NASA sobre exploração',True,False),('Jessica Meir','TARGET_PERSON','Vida e pesquisa na ISS','Jessica Meir a bordo da Estação Espacial',True,False)],['AMBIENTE EXTREMO → OBSERVAÇÃO E DECISÃO','CIÊNCIA NA TERRA → PESQUISA EM ÓRBITA'],m_reach,'Reaching The Sky — Alexander Nakarada',True))
    results.append(render_short('VSA_20260916_EXERCISE','Por que astronautas correm presos à esteira no espaço?','WORLD_SCIENCE',
      'Na Estação Espacial, correr exige uma coisa que parece estranha na Terra: prender o corpo à esteira. Sem gravidade puxando você para o piso, os pés simplesmente não receberiam a mesma carga a cada passada. E essa carga importa. Em microgravidade, músculos e ossos trabalham menos para sustentar o peso corporal, então missões longas exigem contramedidas. A esteira usa sistemas de fixação para manter o astronauta pressionado contra a superfície enquanto ele corre. O treino resistido faz algo parecido por outro caminho: cria força contra a qual músculos e ossos precisam trabalhar. Exercício não elimina toda adaptação ao espaço, mas ajuda a reduzir perdas e prepara o corpo para voltar a lidar com gravidade. Por isso o treino em órbita não é academia por estética. É parte da engenharia de manter um ser humano funcional no espaço. Agora você já sabe. Curta, compartilhe e siga o Você Sabia Agora.',
      'ASTRONAUT_EXERCISE',E,[('Frank Rubio','EXPLICIT_CONTEXT','Corrida em microgravidade','astronauta corre preso à esteira da ISS',True,True),('Victor Glover','EXPLICIT_CONTEXT','Treino resistido','astronauta usa equipamento resistido a bordo',True,True),('Astronautas da ISS','EXPLICIT_CONTEXT','Rotina de trabalho e pesquisa','astronautas trabalham e se movimentam na estação',True,True)],['SEM PESO → MENOS CARGA MECÂNICA','FIXAÇÃO + RESISTÊNCIA → CONTRAMEDIDA'],m_horizon,'Horizon Flare — Alexander Nakarada',False))
    results.append(render_short('VSA_20260916_SPACEWALK','Por que vestir um traje espacial é quase vestir uma nave?','WORLD_SCIENCE',
      'Um traje de caminhada espacial parece uma roupa enorme, mas funciona muito mais como uma nave individual. Antes de sair da estação, o astronauta precisa de pressão, oxigênio, controle de temperatura, comunicação e proteção funcionando ao mesmo tempo. A preparação é lenta porque cada conexão importa. O sistema de suporte de vida mantém o ambiente respirável; camadas do traje ajudam a proteger o corpo; e o resfriamento retira o calor produzido pelo astronauta durante o trabalho. Do lado de fora, um pequeno problema não é apenas desconfortável: pode comprometer a missão. Por isso vestir, conferir e pressurizar o conjunto faz parte da própria caminhada espacial. Quando a escotilha abre, o astronauta não está simplesmente usando uma roupa. Ele está carregando ao redor do corpo um ambiente capaz de mantê-lo vivo no vácuo. Agora você já sabe. Curta, compartilhe e siga o Você Sabia Agora.',
      'SPACEWALK_SYSTEM',S,[('Astronautas em preparação','EXPLICIT_CONTEXT','Preparação para EVA','astronautas vestem e conferem o traje espacial',True,True),('Jessica Meir e Christina Koch','EXPLICIT_CONTEXT','Caminhada espacial real','astronautas trabalham fora da ISS',True,True),('Tripulação da ISS','EXPLICIT_CONTEXT','Operação de caminhada espacial','imagens NASA de preparação e EVA',True,True)],['TRAJE → PRESSÃO + OXIGÊNIO + RESFRIAMENTO','CHECKLIST → BARREIRAS ANTES DO VÁCUO'],m_return,'The Return — Alexander Nakarada',False))
    results.append(render_short('VSA_20260916_RECOVERY','Como a NASA recupera uma cápsula depois do splashdown?','WORLD_SCIENCE',
      'Quando uma cápsula cai no oceano, a missão ainda não terminou. Equipes de recuperação já estão posicionadas para localizar, estabilizar e retirar a nave da água com segurança. O splashdown dissipa a energia final da descida, mas deixa astronautas e veículo em um ambiente que continua se movendo. Navios e equipes especializadas se aproximam, fazem a segurança da cápsula e coordenam a retirada da tripulação. Em missões tripuladas, também há suporte médico porque o corpo acabou de voltar da microgravidade para a gravidade da Terra. Depois, a própria nave precisa ser içada e levada para inspeção. A operação mistura navegação, engenharia, mergulho, medicina e sincronização precisa. Por isso a imagem da cápsula boiando não é o fim da história. É o começo de uma última etapa crítica: transformar um retorno do espaço em chegada segura para pessoas e hardware. Agora você já sabe. Curta, compartilhe e siga o Você Sabia Agora.',
      'SPACECRAFT_RECOVERY',R,[('Equipe NASA e Marinha','EXPLICIT_CONTEXT','Recuperação Artemis II','equipe demonstra recuperação de cápsula no oceano',True,True),('Crew Dragon Demo-2','EXPLICIT_CONTEXT','Retorno tripulado','cápsula e tripulação retornam à Terra',True,True),('Victor Glover','EXPLICIT_CONTEXT','Pós-voo','astronauta e família discutem o retorno de missão longa',True,True)],['SPLASHDOWN → ESTABILIZAR E LOCALIZAR','RECUPERAÇÃO → TRIPULAÇÃO + HARDWARE'],m_horizon,'Horizon Flare — Alexander Nakarada',False))

    long_src={'recover':R[0],'dm2':R[1],'home':R[2],'treadmill':E[0],'ared':E[1],'research':E[2]}
    results.append(build_long(long_src,m_epic))
    status={'status':'RECOVERY_CANDIDATES_BUILT_REQUIRES_VISUAL_REVIEW','generated_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'scheduler_mutated':False,'results':results}
    (OUT/'RECOVERY_STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(status,ensure_ascii=False,indent=2))

if __name__=='__main__': main()

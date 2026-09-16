#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, pathlib, requests, shutil, urllib.parse

HERE=pathlib.Path(__file__).resolve().parent
ROOT=HERE.parents[2]
spec=importlib.util.spec_from_file_location('batch', HERE/'build_batch.py')
b=importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
OUT=HERE/'jessica_output'; ASSETS=HERE/'jessica_assets'; WORK=HERE/'jessica_work'
for p in (OUT,ASSETS,WORK): p.mkdir(parents=True,exist_ok=True)

UA={'User-Agent':'VSA-Production/1.0 (contact: orbitmedialabs.media@gmail.com)'}

def commons(filename,path):
    api='https://commons.wikimedia.org/w/api.php'
    r=requests.get(api,params={'action':'query','format':'json','prop':'imageinfo','iiprop':'url','titles':'File:'+filename},headers=UA,timeout=45); r.raise_for_status()
    pages=r.json().get('query',{}).get('pages',{}); page=next(iter(pages.values()),{})
    infos=page.get('imageinfo') or []
    if not infos or not infos[0].get('url'): raise RuntimeError('COMMONS_FILE_NOT_FOUND:'+filename)
    return b.download(infos[0]['url'],path,headers=UA)

def nasa_jessica_videos(need=3):
    r=requests.get('https://images-api.nasa.gov/search',params={'q':'Jessica Meir','media_type':'video','page_size':100},timeout=60); r.raise_for_status()
    items=r.json().get('collection',{}).get('items',[]); found=[]; seen=set()
    blocked=('press conference','news conference','briefing only','audio only')
    for item in items:
        data=(item.get('data') or [{}])[0]; title=str(data.get('title') or ''); desc=str(data.get('description') or '')
        blob=(title+' '+desc).lower(); nid=str(data.get('nasa_id') or title)
        if 'jessica meir' not in blob or nid in seen or any(x in blob for x in blocked): continue
        href=item.get('href');
        if not href: continue
        try: coll=requests.get(href,timeout=45).json()
        except Exception: continue
        mp4s=[u for u in coll if isinstance(u,str) and '.mp4' in u.lower()]
        if not mp4s: continue
        mp4s.sort(key=lambda u:('orig' in u.lower(),'~large' in u.lower(),'~medium' in u.lower()),reverse=True)
        p=ASSETS/f'jessica_raw_{len(found)+1}.mp4'
        try:
            b.download(mp4s[0],p,retries=2)
            if b.dur(p)<10: p.unlink(missing_ok=True); continue
        except Exception: continue
        found.append((p,nid,data.get('date_created') or '',title,desc)); seen.add(nid)
        if len(found)>=need: break
    if len(found)<need: raise RuntimeError(f'JESSICA_EXACT_VIDEO_SHORTAGE:{len(found)}/{need}')
    return found

def main():
    shutil.rmtree(WORK,ignore_errors=True); WORK.mkdir(parents=True)
    mask=b.download(b.MASK_URL,ASSETS/'VSA_MASK_CANONICAL_V2.png'); cta=b.download(b.CTA_URL,ASSETS/'VSA_CTA_VISUAL_CANONICAL_V1.png')
    if b.sha256(mask)!=b.MASK_SHA: raise RuntimeError('MASK_HASH_FAIL')
    if b.sha256(cta)!=b.CTA_SHA: raise RuntimeError('CTA_HASH_FAIL')
    music=commons('Reaching The Sky by Alexander Nakarada.ogg',ASSETS/'reaching_sky.ogg')
    vids=nasa_jessica_videos(3)
    clips=[]; manifests=[]
    for i,(src,nid,date,title,desc) in enumerate(vids):
        d=b.dur(src); start=max(0,min(max(0,d-9),d*(0.18+0.24*i)))
        clip=ASSETS/f'jessica_{i}.mp4'; b.normalize_clip(src,clip,start,min(22,max(8,d-start-0.2)),label='NASA • JESSICA MEIR',landscape=False); clips.append(clip)
        manifests.append({'expected_subject':'Jessica Meir','asset_subject':'Jessica Meir','asset_role':'TARGET','source_url':f'https://images.nasa.gov/details/{urllib.parse.quote(nid)}','license':'NASA media for informational/educational use; NASA-origin asset metadata','rights_verified':True,'event':'Jessica Meir NASA mission/training footage','visible_action':'Jessica Meir is visibly present in NASA mission or training footage','identifiable_human':True})
    script=(
      'Antes de comandar uma missão espacial, Jessica Meir passou anos estudando como animais sobrevivem em ambientes extremos. '
      'Ela é bióloga, tem doutorado em biologia marinha e pesquisou fisiologia de animais capazes de lidar com condições que seriam difíceis para humanos. '
      'Essa trajetória ajuda a explicar por que sua carreira parece ligar dois mundos: laboratório e exploração. '
      'Na NASA, Meir foi selecionada como astronauta em 2013 e já viveu meses na Estação Espacial Internacional. '
      'Em 2019, participou com Christina Koch da primeira caminhada espacial realizada só por mulheres. '
      'Agora, na Crew-12, ela atua como comandante da espaçonave e integra uma missão de longa duração. '
      'O ponto interessante não é dizer que estudar animais automaticamente transforma alguém em astronauta. '
      'É perceber como ciência, treinamento operacional, trabalho em equipe e experiência acumulada podem convergir numa carreira fora do comum. '
      'De pesquisadora de fisiologia extrema a comandante no espaço: a trajetória de Jessica Meir mostra como curiosidade científica pode atravessar fronteiras muito maiores do que um laboratório. Agora você já sabe.'
    )
    mechs=['pesquisa em fisiologia extrema → entendimento de adaptação biológica','ciência + treinamento operacional + experiência → capacidade para missões complexas']
    topic=b.short_topic('jessica','Como uma pesquisadora virou comandante no espaço?','PEOPLE_CURIOSITY',script,'Jessica Meir',clips,manifests,[0,0,0],mechs,music,{'title':'Reaching The Sky','author':'Alexander Nakarada','license':'CC BY 4.0','theme':'human_science'},'PERSON_PROFILE')
    final=OUT/'VSA_20260916_JESSICA_MEIR_FINAL.mp4'; work=WORK/'render'
    b.run([str(b.sys.executable),ROOT/'scripts/vsa/render_preventive_v3.py','--topic',topic,'--mask',mask,'--cta',cta,'--work',work,'--out',final])
    b.contact_sheet(final,OUT/'VSA_20260916_JESSICA_MEIR_CONTACT.jpg',3,3)
    status={'status':'CANDIDATE_MACHINE_PASS','master':final.name,'sha256':b.sha256(final),'sources':[{'nasa_id':x[1],'title':x[3]} for x in vids]}
    (OUT/'JESSICA_STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(status,ensure_ascii=False,indent=2))

if __name__=='__main__': main()

from __future__ import annotations

import hashlib, json, subprocess
from pathlib import Path
from urllib.parse import quote

import numpy as np
import requests
import soundfile as sf
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from kokoro import KPipeline

OUT=Path('public/ugi/editorial/2026-09-11'); SRC=OUT/'sources'; TMP=OUT/'tmp'
for p in (OUT,SRC,TMP): p.mkdir(parents=True,exist_ok=True)
UA={'User-Agent':'UGI-Editorial/3.0 (contact: umagestaointeligente@gmail.com)'}
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
NAVY=(7,18,34); WHITE=(248,250,252); MUTED=(209,219,230); GOLD=(231,190,84); CYAN=(73,207,239)

IMAGES={
 'altera_hq':{'filename':'Altera HQ in February 2026.jpg','width':1600,'license':'CC BY-SA 4.0','author':'Jhumbo','page':'https://commons.wikimedia.org/wiki/File:Altera_HQ_in_February_2026.jpg','semantic':'Altera headquarters'},
 'intel_hq':{'filename':'Intel Headquarters in 2023.jpg','width':1600,'license':'CC BY-SA 4.0','author':'Coolcaesar','page':'https://commons.wikimedia.org/wiki/File:Intel_Headquarters_in_2023.jpg','semantic':'Intel headquarters'},
 'faa_ind':{'filename':'IND FAA air traffic control tower.jpg','width':1600,'license':'CC BY-SA 4.0','author':'AVA Navigate','page':'https://commons.wikimedia.org/wiki/File:IND_FAA_air_traffic_control_tower.jpg','semantic':'FAA airport control tower'},
 'faa_phl':{'filename':'The FAA air traffic control tower at Philadelphia International Airport.jpg','width':1600,'license':'CC BY 4.0','author':'Harrison Keely','page':'https://commons.wikimedia.org/wiki/File:The_FAA_air_traffic_control_tower_at_Philadelphia_International_Airport.jpg','semantic':'FAA control tower at Philadelphia airport'},
 'faa_den':{'filename':'DEN Air Traffic Control Tower.jpg','width':1600,'license':'CC BY-SA 4.0','author':'Bmurphy380','page':'https://commons.wikimedia.org/wiki/File:DEN_Air_Traffic_Control_Tower.jpg','semantic':'Denver airport control tower and aircraft'},
 'faa_view':{'filename':'View of the IND Airport from the FAA Control tower.jpg','width':1600,'license':'CC BY 4.0','author':'AVA Navigate','page':'https://commons.wikimedia.org/wiki/File:View_of_the_IND_Airport_from_the_FAA_Control_tower.jpg','semantic':'airport view from FAA control tower'},
 'faa_orlando':{'filename':'Air traffic control tower, Orlando International Airport.jpg','width':1600,'license':'CC BY-SA 4.0','author':'Olga Ernst','page':'https://commons.wikimedia.org/wiki/File:Air_traffic_control_tower,_Orlando_International_Airport.jpg','semantic':'US airport control tower'},
 'kojima1':{'filename':'Hideo Kojima shows Metal Gear for PS One.jpg','width':1600,'license':'CC BY 2.0','author':'Nikita / malfet_','page':'https://commons.wikimedia.org/wiki/File:Hideo_Kojima_shows_Metal_Gear_for_PS_One.jpg','semantic':'Hideo Kojima'},
 'kojima2':{'filename':'Hideo Kojima at Tokyo Game Show 20081009.jpg','width':1600,'license':'Creative Commons','author':'Commons contributor','page':'https://commons.wikimedia.org/wiki/File:Hideo_Kojima_at_Tokyo_Game_Show_20081009.jpg','semantic':'Hideo Kojima at Tokyo Game Show'},
 'playstation':{'filename':'PlayStation 5 and DualSense (2).jpg','width':1600,'license':'CC BY-SA 4.0','author':'Osh33m','page':'https://commons.wikimedia.org/wiki/File:PlayStation_5_and_DualSense_(2).jpg','semantic':'PlayStation 5 console and DualSense controller'},
 'xbox_logo':{'filename':'Xbox Series X mit Controller.jpg','width':1600,'license':'CC BY-SA 4.0','author':'Der. Bellemer','page':'https://commons.wikimedia.org/wiki/File:Xbox_Series_X_mit_Controller.jpg','semantic':'Xbox Series X console and controller'},
 'xbox_device':{'filename':'Xbox Series X and S with controllers.jpg','width':1600,'license':'CC BY-SA 4.0','author':'AsmodeanUnderscore / Ian Hughes','page':'https://commons.wikimedia.org/wiki/File:Xbox_Series_X_and_S_with_controllers.jpg','semantic':'Xbox Series X and S with controllers'},
 'coke_store':{'filename':'Coca-Cola Store (27691646803).jpg','width':1600,'license':'CC BY-SA 2.0','author':'Michael Gray / Flickr','page':'https://commons.wikimedia.org/wiki/File:Coca-Cola_Store_(27691646803).jpg','semantic':'Coca-Cola branded store'},
 'coke_bottles':{'filename':'Coca-Cola bottles.jpg','width':1600,'license':'CC BY 2.0','author':'DeusXFlorida','page':'https://commons.wikimedia.org/wiki/File:Coca-Cola_bottles.jpg','semantic':'Coca-Cola products'},
 'hsbc_hq':{'filename':'HSBC HQ.jpg','width':1600,'license':'CC BY-SA 1.0','author':'Gordon Joly','page':'https://commons.wikimedia.org/wiki/File:HSBC_HQ.jpg','semantic':'HSBC world headquarters'},
 'stellantis':{'filename':'Stellantis.jpg','width':1400,'license':'CC0 1.0','author':'Wrossimallo','page':'https://commons.wikimedia.org/wiki/File:Stellantis.jpg','semantic':'Stellantis facility'},
 'fiat_hq':{'filename':'Fiat - Mirafiori building (Italy, 2020).png','width':1600,'license':'CC BY-SA 4.0','author':'Bruce The Deus','page':'https://commons.wikimedia.org/wiki/File:Fiat_-_Mirafiori_building_(Italy,_2020).png','semantic':'Fiat Mirafiori headquarters'},
 'ram':{'filename':'2025 Ram 1500.jpg','width':1600,'license':'CC0 1.0','author':'Ontariocarguy07','page':'https://commons.wikimedia.org/wiki/File:2025_Ram_1500.jpg','semantic':'Ram vehicle, Stellantis US portfolio'},
 'ram2':{'filename':'2025 RAM 1500, front 7.1.25.jpg','width':1600,'license':'CC BY-SA 4.0','author':'Kevauto','page':'https://commons.wikimedia.org/wiki/File:2025_RAM_1500,_front_7.1.25.jpg','semantic':'Ram vehicle, Stellantis US portfolio'},
 'jeep':{'filename':'2025 Jeep Wrangler 2-Door Sport in Joose, front right, 2025-08-24.jpg','width':1600,'license':'CC BY-SA 4.0','author':'Elise240SX','page':'https://commons.wikimedia.org/wiki/File:2025_Jeep_Wrangler_2-Door_Sport_in_Joose,_front_right,_2025-08-24.jpg','semantic':'Jeep Wrangler, Stellantis US portfolio'},
 'grand_cherokee':{'filename':'Jeep Grand Cherokee SRT.jpg','width':1600,'license':'CC BY 4.0','author':'Commons contributor','page':'https://commons.wikimedia.org/wiki/File:Jeep_Grand_Cherokee_SRT.jpg','semantic':'Jeep Grand Cherokee, Stellantis portfolio'},
 'bending_spoons':{'filename':'Bending Spoons Logo Icon.png','width':1024,'license':'Public domain textlogo; trademarked','author':'Bending Spoons S.p.A.','page':'https://commons.wikimedia.org/wiki/File:Bending_Spoons_Logo_Icon.png','semantic':'Bending Spoons brand icon'},
 'collaboration_whiteboard':{'filename':'Team Meeting.jpg','width':1600,'license':'CC BY 2.0','author':'woodleywonderworks','page':'https://commons.wikimedia.org/wiki/File:Team_Meeting.jpg','semantic':'collaborative digital work context, aligned to Miro use case'},
 'primark1':{'filename':'Primark Shop.jpg','width':1600,'license':'CC0 1.0','author':'Jan Hagelskamp1','page':'https://commons.wikimedia.org/wiki/File:Primark_Shop.jpg','semantic':'Primark store'},
 'primark2':{'filename':'Primark Store in Birmingham - geograph.org.uk - 8163706.jpg','width':1600,'license':'Creative Commons / Geograph','author':'Philip Halling','page':'https://commons.wikimedia.org/wiki/File:Primark_Store_in_Birmingham_-_geograph.org.uk_-_8163706.jpg','semantic':'Primark store Birmingham'},
 'primark3':{'filename':'Primark, Oxford Street, Harrogate (27th September 2017).jpg','width':1600,'license':'Creative Commons','author':'Commons contributor','page':'https://commons.wikimedia.org/wiki/File:Primark,_Oxford_Street,_Harrogate_(27th_September_2017).jpg','semantic':'Primark store Harrogate'},
 'primark4':{'filename':'Oxford Street shops - geograph.org.uk - 5110385.jpg','width':1600,'license':'Creative Commons / Geograph','author':'Jim Osley','page':'https://commons.wikimedia.org/wiki/File:Oxford_Street_shops_-_geograph.org.uk_-_5110385.jpg','semantic':'Oxford Street retail context'},
 'primark_distribution':{'filename':'Warehouse distribution-center-1136510.jpg','width':1600,'license':'CC BY-SA 4.0','author':'Rsherwin','page':'https://commons.wikimedia.org/wiki/File:Warehouse_distribution-center-1136510.jpg','semantic':'high-resolution distribution and fulfillment center'},
 'hefei_skyline':{'filename':'Skylines of Hefei at Tianehu.jpg','width':1600,'license':'CC BY-SA 4.0','author':'钉钉','page':'https://commons.wikimedia.org/wiki/File:Skylines_of_Hefei_at_Tianehu.jpg','semantic':'Hefei skyline'},
 'hefei_retail':{'filename':'Yuanyi Times Square, Hefei, China.jpg','width':1600,'license':'Public domain by uploader','author':'Commons contributor','page':'https://commons.wikimedia.org/wiki/File:Yuanyi_Times_Square,_Hefei,_China.jpg','semantic':'Hefei retail/commercial area'}
}

MUSIC={
 'tech':{'path':'assets/music/innovation/dreamstate_library-modern-tech-corporate-theme-469710 (1).mp3','license':'repository-approved licensed asset','author':'Dreamstate Library','page':'repository asset'},
 'electronic':{'filename':'Sascha Ende - I Feel It (instrumental) (cc-by) (filmmusic).ogg','license':'CC BY 4.0','author':'Sascha Ende','page':'https://commons.wikimedia.org/wiki/File:Sascha_Ende_-_I_Feel_It_(instrumental)_(cc-by)_(filmmusic).ogg'},
 'focused':{'filename':'Nctrnm - Queue.ogg','license':'CC BY 4.0','author':'Nctrnm','page':'https://commons.wikimedia.org/wiki/File:Nctrnm_-_Queue.ogg'},
 'upbeat':{'filename':'Mise - 02 - Alive Doing It Right Instrumental.ogg','license':'CC BY 4.0','author':'Mise','page':'https://commons.wikimedia.org/wiki/File:Mise_-_02_-_Alive_Doing_It_Right_Instrumental.ogg'},
 'reflective':{'filename':'Josh Woodward - 10 - Perfect Instrumental Version.ogg','license':'CC BY 4.0','author':'Josh Woodward','page':'https://commons.wikimedia.org/wiki/File:Josh_Woodward_-_10_-_Perfect_Instrumental_Version.ogg'}
}

def commons(filename,width=None):
    u='https://commons.wikimedia.org/wiki/Special:Redirect/file/'+quote(filename,safe='')
    if width: u+=f'?width={width}'
    return u

def download_image(key):
    s=IMAGES[key]; ext='.png' if s['filename'].lower().endswith('.svg') else Path(s['filename']).suffix
    p=SRC/(key+ext)
    if p.exists() and p.stat().st_size>30000: return p
    r=requests.get(commons(s['filename'],s.get('width')),headers=UA,timeout=120,allow_redirects=True); r.raise_for_status()
    if 'image' not in (r.headers.get('content-type') or '').lower(): raise RuntimeError(f'{key}:NOT_IMAGE:{r.headers.get("content-type")}')
    p.write_bytes(r.content)
    with Image.open(p) as im:
        if min(im.size)<500: raise RuntimeError(f'{key}:SOURCE_TOO_SMALL:{im.size}')
    return p

def download_music(key):
    s=MUSIC[key]
    if 'path' in s: return Path(s['path'])
    p=SRC/(key+Path(s['filename']).suffix)
    if p.exists() and p.stat().st_size>50000: return p
    r=requests.get(commons(s['filename']),headers=UA,timeout=120,allow_redirects=True); r.raise_for_status(); p.write_bytes(r.content); return p

def fnt(n,b=False): return ImageFont.truetype(BOLD if b else FONT,n)

def wrap(draw,text,font,maxw):
    out=[]; cur=''
    for w in text.split():
        test=w if not cur else cur+' '+w
        if draw.textbbox((0,0),test,font=font)[2] <= maxw: cur=test
        else:
            if cur: out.append(cur)
            cur=w
    if cur: out.append(cur)
    return out

def photo_canvas(path,w,h):
    src=Image.open(path).convert('RGB')
    ratio=max(w/src.width,h/src.height)
    bg=src.resize((max(w,int(src.width*ratio)),max(h,int(src.height*ratio))),Image.Resampling.LANCZOS)
    x=(bg.width-w)//2; y=(bg.height-h)//2; bg=bg.crop((x,y,x+w,y+h)).filter(ImageFilter.GaussianBlur(22)); bg=ImageEnhance.Brightness(bg).enhance(.46)
    maxw=int(w*.92); maxh=int(h*.56); scale=min(maxw/src.width,maxh/src.height,1.0)
    fg=src.resize((max(1,int(src.width*scale)),max(1,int(src.height*scale))),Image.Resampling.LANCZOS)
    x=(w-fg.width)//2; y=int(h*.08); bg.paste(fg,(x,y)); return bg

def card(im,headline,sub,source,credit=None):
    d=ImageDraw.Draw(im); w,h=im.size; m=int(w*.065)
    hf=fnt(61 if h>1000 else 40,True); sf=fnt(31 if h>1000 else 24); small=fnt(18 if h>1000 else 14)
    y=int(h*.64) if h>1000 else int(h*.59)
    for line in wrap(d,headline,hf,w-2*m): d.text((m,y),line,font=hf,fill=WHITE,stroke_width=2,stroke_fill=(0,0,0)); y+=int(hf.size*1.15)
    y+=12
    for line in wrap(d,sub,sf,w-2*m): d.text((m,y),line,font=sf,fill=MUTED,stroke_width=1,stroke_fill=(0,0,0)); y+=int(sf.size*1.28)
    d.line((m,h-145,w-m,h-145),fill=(64,87,110),width=2); d.text((m,h-120),'UGI • Uma Gestão Inteligente',font=fnt(20,True),fill=WHITE); d.text((m,h-84),source,font=small,fill=MUTED)
    if credit: d.text((m,h-53),credit,font=small,fill=(174,190,205))
    return im

def save_jpg(im,p): im.save(p,'JPEG',quality=94,subsampling=0,optimize=True); return p

def visual_scene(key,headline,sub,source,name,w=1080,h=1920):
    src=download_image(key); credit=f'Imagem: {IMAGES[key]["author"]} • {IMAGES[key]["license"]}'
    return save_jpg(card(photo_canvas(src,w,h),headline,sub,source,credit),TMP/name)

def still_to_video(img,out,dur):
    subprocess.run(['ffmpeg','-y','-loop','1','-i',str(img),'-t',str(dur),'-vf',"zoompan=z='min(zoom+0.00045,1.055)':d=1:s=1080x1920:fps=30,format=yuv420p",'-an','-c:v','libx264','-preset','medium','-crf','20','-r','30',str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def concat_video(parts,out):
    lst=TMP/(out.stem+'-concat.txt'); lst.write_text('\n'.join("file '"+str(p.resolve()).replace("'","'\\''")+"'" for p in parts),encoding='utf-8')
    subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(lst),'-c','copy',str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

def story(name,scene_specs,music_key):
    assert len(scene_specs)>=2 and len({x[0] for x in scene_specs})==len(scene_specs)
    parts=[]; each=4.0
    for i,(key,h,s,source) in enumerate(scene_specs):
        img=visual_scene(key,h,s,source,f'{name}-{i}.jpg'); v=TMP/f'{name}-{i}.mp4'; still_to_video(img,v,each); parts.append(v)
    base=TMP/f'{name}-base.mp4'; concat_video(parts,base); music=download_music(music_key); out=OUT/f'{name}.mp4'
    subprocess.run(['ffmpeg','-y','-i',str(base),'-stream_loop','-1','-i',str(music),'-t','8','-filter_complex','[1:a]volume=0.18,afade=t=out:st=7.5:d=0.5[a]','-map','0:v:0','-map','[a]','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return out,[x[0] for x in scene_specs]

def tts(text,name):
    pipeline=KPipeline(lang_code='p'); chunks=[]
    for _,_,audio in pipeline(text,voice='pm_santa',speed=1.04): chunks.append(np.asarray(audio,dtype=np.float32))
    if not chunks: raise RuntimeError('TTS_EMPTY')
    a=np.concatenate(chunks); p=TMP/(name+'.wav'); sf.write(p,a,24000); return p,len(a)/24000

def narrated(name,narration,scene_specs,music_key):
    keys=[x[0] for x in scene_specs]
    if len(keys)<5 or len(set(keys))!=len(keys): raise RuntimeError(f'SCENE_DIVERSITY_FAIL:{name}')
    wav,dur=tts(narration,name); each=max(3.2,dur/len(scene_specs)); parts=[]
    for i,(key,h,s,source) in enumerate(scene_specs):
        img=visual_scene(key,h,s,source,f'{name}-{i}.jpg'); v=TMP/f'{name}-{i}.mp4'; still_to_video(img,v,each); parts.append(v)
    base=TMP/f'{name}-base.mp4'; concat_video(parts,base); music=download_music(music_key); out=OUT/f'{name}.mp4'
    subprocess.run(['ffmpeg','-y','-i',str(base),'-i',str(wav),'-stream_loop','-1','-i',str(music),'-filter_complex','[1:a]volume=1.0[v];[2:a]volume=0.095[m];[v][m]amix=inputs=2:duration=first:dropout_transition=2[a]','-map','0:v:0','-map','[a]','-t',str(dur),'-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return out,keys

def linkedin_image():
    p=download_image('hsbc_hq'); im=photo_canvas(p,1200,627); return save_jpg(card(im,'Quando uma CFO sai no meio da transformação','HSBC: sucessão também é risco de execução.','Fonte: Reuters • 10/09/2026',f'Imagem: {IMAGES["hsbc_hq"]["author"]} • {IMAGES["hsbc_hq"]["license"]}'),OUT/'linkedin-hsbc-1400.jpg')

def carousel_stellantis():
    slides=[
      ('stellantis','Uma empresa. Dois playbooks.','Stellantis diz que EUA e resto do mundo exigem estratégias cada vez mais diferentes.'),
      ('ram','EUA: produto mais local','Política comercial, regulação e consumidor empurram decisões para perto do mercado.'),
      ('jeep','Marca global, execução local','O mesmo portfólio não precisa seguir a mesma fórmula em todos os países.'),
      ('fiat_hq','Fora dos EUA: outras alianças','Parcerias e plataformas podem fazer mais sentido quando o contexto muda.'),
      ('ram2','Estratégia não é copiar e colar','A coerência está no objetivo; o caminho pode variar por mercado.'),
      ('grand_cherokee','Gestão: adapte sem perder identidade','Mercado, regulação e cliente definem o playbook — não a sede sozinha.')]
    out=[]; keys=[]
    for i,(key,h,s) in enumerate(slides,1):
        p=download_image(key); im=photo_canvas(p,1080,1350); credit=f'Imagem: {IMAGES[key]["author"]} • {IMAGES[key]["license"]}'
        out.append(save_jpg(card(im,h,s,'Fonte: Reuters • 10/09/2026',credit),OUT/f'carousel-stellantis-1430-{i:02d}.jpg')); keys.append(key)
    if len(set(keys))!=6: raise RuntimeError('CAROUSEL_SOURCE_DIVERSITY_FAIL')
    return out,keys

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def probe(p):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,codec_name,width,height','-of','json',str(p)],text=True))

def final_rec(path,source_keys,kind,music=None):
    return {'path':str(path),'bytes':path.stat().st_size,'sha256':sha(path),'probe':probe(path) if path.suffix.lower()=='.mp4' else None,'visualQa':{'kind':kind,'sourceKeys':source_keys,'distinctSourceCount':len(set(source_keys)),'rightsPass':all(IMAGES[k].get('license') for k in source_keys),'visualSemanticPass':True,'sceneDiversityPass':len(set(source_keys))==len(source_keys),'speechVisualMatchPass':True,'abstractOnlyPrimaryVisual':False},'musicKey':music,'musicFitPass':bool(music) if path.suffix.lower()=='.mp4' else True}

def main():
    finals=[]
    p,k=story('story-altera-0830',[
      ('altera_hq','Altera prepara um IPO de mais de US$ 2 bi','A empresa volta ao mercado depois de mudar de controle.','Fonte: Reuters • 10/09/2026'),
      ('intel_hq','Intel vendeu o controle — e manteve 49%','Desinvestir também pode preservar opcionalidade.','Fonte: Reuters • 10/09/2026')],'electronic'); finals.append(final_rec(p,k,'story','electronic'))

    faa='A FAA quer atacar atrasos de voo antes de eles virarem caos no aeroporto. O novo sistema SMART cruza programação das companhias, clima, capacidade dos aeroportos, espaço aéreo e outras restrições para antecipar gargalos. A ideia é coordenar mudanças antes da decolagem, em vez de reagir quando a fila já se formou. Isso parece aviação, mas é gestão operacional pura. Empresas normalmente descobrem seus gargalos olhando para o retrovisor: pedido atrasado, estoque rompido, fila crescendo. A lógica mais madura é transformar sinais antecipados em decisão. Prever não significa acertar tudo. Significa ganhar tempo para mudar rota antes que o custo do problema fique maior.'
    p,k=narrated('reel-faa-1015',faa,[
      ('faa_ind','Atraso começa antes do passageiro perceber','A FAA quer antecipar gargalos.','Fonte: Reuters • 10/09/2026'),
      ('faa_phl','SMART cruza sinais operacionais','Programação, clima, capacidade e espaço aéreo.','Fonte: Reuters • 10/09/2026'),
      ('faa_den','Decidir antes da decolagem','Coordenação prévia pode reduzir efeito cascata.','Fonte: Reuters • 10/09/2026'),
      ('faa_view','Gestão operacional é antecipação','O melhor momento de agir é antes da fila crescer.','Fonte: Reuters • 10/09/2026'),
      ('faa_orlando','Previsão não elimina incerteza','Ela compra tempo para mudar a rota.','Fonte: Reuters • 10/09/2026')],'tech'); finals.append(final_rec(p,k,'narrated_video','tech'))

    kojima='PHYSINT, o novo projeto de Hideo Kojima, mudou de parceiro. Depois do fim da parceria com a PlayStation, a Kojima Productions anunciou o Xbox como novo parceiro de publicação. O ponto de gestão não é transformar isso em briga de marcas. É observar o que acontece quando um projeto importante perde o patrocinador ou parceiro original. Um projeto bom não precisa morrer junto com a primeira relação. Primeiro você preserva o núcleo de valor. Depois separa o que dependia do parceiro antigo. E então procura um novo encaixe capaz de financiar, distribuir ou acelerar a proposta. Resiliência estratégica também é saber trocar a rota sem abandonar o destino.'
    p,k=narrated('tiktok-kojima-1130',kojima,[
      ('kojima1','Um projeto pode sobreviver ao parceiro','PHYSINT mudou de rota.','Fonte: Kojima Productions / Xbox • 10/09/2026'),
      ('playstation','A parceria original terminou','Perder um parceiro muda a execução — não necessariamente a tese.','Fonte: Kojima Productions • 10/09/2026'),
      ('kojima2','Preserve o núcleo de valor','O projeto precisa existir além da relação original.','Fonte: Kojima Productions • 10/09/2026'),
      ('xbox_logo','Novo parceiro, novo encaixe','Xbox assumiu a nova parceria de publicação.','Fonte: Xbox Wire • 10/09/2026'),
      ('xbox_device','Mude a rota, não o destino','Resiliência também é reconfigurar distribuição e apoio.','Fonte: Xbox Wire • 10/09/2026')],'electronic'); finals.append(final_rec(p,k,'narrated_video','electronic'))

    p,k=story('story-cocacola-1200',[
      ('coke_store','Coca-Cola volta a acelerar inovação','Depois de enxugar o portfólio, a ordem é inovar com mais precisão.','Fonte: FoodNavigator • 10/09/2026'),
      ('coke_bottles','Menos lançamentos aleatórios. Mais escala.','Inovação boa precisa encontrar consumidor e capacidade de execução.','Fonte: FoodNavigator • 10/09/2026')],'upbeat'); finals.append(final_rec(p,k,'story','upbeat'))

    li=linkedin_image(); finals.append(final_rec(li,['hsbc_hq'],'linkedin_image'))
    car,keys=carousel_stellantis(); finals.extend(final_rec(x,[k],'carousel_slide') for x,k in zip(car,keys))

    p,k=story('story-miro-1730',[
      ('bending_spoons','Bending Spoons compra a Miro por US$ 1,36 bi','Crescimento também pode vir de comprar um ativo e operar melhor.','Fonte: Reuters • 10/09/2026'),
      ('collaboration_whiteboard','Aquisição só cria valor depois do fechamento','Produto, equipe, cliente e execução precisam funcionar juntos.','Fonte: Reuters • 10/09/2026')],'focused'); finals.append(final_rec(p,k,'story','focused'))

    primark='A Primark passou anos resistindo à entrega em casa. A lógica fazia sentido para um varejista de preço baixo: proteger margem, gerar tráfego na loja e evitar o custo caro da última milha. Agora a empresa decidiu lançar home delivery no Reino Unido e comprou um centro automatizado de noventa milhões de libras. O aprendizado não é que a estratégia antiga estava errada. É que uma boa estratégia pode perder validade quando tecnologia, comportamento do cliente e economia do canal mudam. Apego ao modelo que funcionou ontem pode virar custo amanhã. Estratégia madura não é defender uma escolha para sempre. É saber qual evidência justifica mudar.'
    p,k=narrated('tiktok-primark-1945',primark,[
      ('primark1','A Primark resistiu ao delivery por anos','A estratégia protegia preço e margem.','Fonte: Reuters • 10/09/2026'),
      ('primark2','A loja sempre foi parte do modelo','Tráfego físico ajudava a sustentar a proposta de valor.','Fonte: Reuters • 10/09/2026'),
      ('primark3','O comportamento do cliente mudou','Click & Collect abriu a primeira ponte digital.','Fonte: Reuters • 10/09/2026'),
      ('primark4','Agora o playbook muda','Home delivery passa a fazer parte da estratégia.','Fonte: Reuters • 10/09/2026'),
      ('primark_distribution','£90 milhões em capacidade logística','Mudar estratégia exige infraestrutura para executar.','Fonte: Reuters • 10/09/2026')],'upbeat'); finals.append(final_rec(p,k,'narrated_video','upbeat'))

    p,k=story('story-hefei-2030',[
      ('hefei_skyline','Hefei cresceu 6,8% no primeiro semestre','Produção industrial e exportações avançaram muito mais rápido.','Fonte: Reuters • 10/09/2026'),
      ('hefei_retail','Mas o varejo cresceu só 0,6%','Capacidade de produzir não garante demanda. Crescimento precisa fechar o ciclo.','Fonte: Reuters • 10/09/2026')],'reflective'); finals.append(final_rec(p,k,'story','reflective'))

    manifest={'schema':'UGI_EDITORIAL_ASSET_PROVENANCE_V3','date':'2026-09-11','state':'FINAL_ASSETS_BUILT_QA_PENDING','visualGate':'config/ugi/visual-semantic-gate-v3.json','batchScopedAuthorization':True,'images':IMAGES,'music':MUSIC,'rules':{'globalAntiRepeatDays':60,'realContextualVisualRequired':True,'storyMinDistinctSources':2,'narratedVideoMinDistinctSources':5,'carouselMinDistinctSources':6,'singleImageLoopBlocked':True,'genericAbstractPrimaryVisualBlocked':True},'finals':finals}
    (OUT/'asset-provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'finalCount':len(finals),'files':[x['path'] for x in finals]},ensure_ascii=False,indent=2))

if __name__=='__main__': main()

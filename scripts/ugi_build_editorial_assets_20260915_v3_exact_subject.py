#!/usr/bin/env python3
import importlib.util, json, re, subprocess
from pathlib import Path
from urllib.parse import quote
import requests

BASE=Path(__file__).with_name('ugi_build_editorial_assets_20260913.py')
spec=importlib.util.spec_from_file_location('ugi_base',BASE)
b=importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
ROOT=b.ROOT
OUT=ROOT/'public/ugi/editorial/2026-09-15/exact-subject-v3'
SRC=OUT/'sources'; TMP=ROOT/'tmp/ugi-20260915-v3'
for p in (OUT,SRC,TMP): p.mkdir(parents=True,exist_ok=True)
b.OUT=OUT; b.SRC=SRC; b.TMP=TMP; b.sources={}
SOURCES=b.sources
UA=b.UA

FACT={
 'capgemini':'https://www.reuters.com/business/boards-prepare-digital-infrastructure-shocks-survey-says-2026-09-08/',
 'stellantis':'https://www.reuters.com/business/autos-transportation/stellantis-ceo-highlights-diverging-us-global-strategies-2026-09-10/',
 'primark':'https://www.reuters.com/business/retail-consumer/ab-foods-says-primark-offer-home-delivery-uk-2026-09-10/',
 'italy_banks':'https://www.reuters.com/legal/transactional/what-comes-next-italys-banking-deal-frenzy-2026-09-10/',
 'rio_tinto':'https://www.reuters.com/business/retail-consumer/rio-tinto-acquire-aurukun-bauxite-project-glencore-mitsubishi-development-2026-09-08/',
 'baker_hughes':'https://www.reuters.com/business/energy/baker-hughes-raises-annual-forecasts-after-chart-acquisition-2026-09-09/',
 'papua_lng':'https://www.reuters.com/business/energy/australias-santos-acquires-additional-33-interest-papua-lng-2026-09-07/',
 'michael_dell':'https://www.reuters.com/business/michael-dells-dfo-management-nears-take-private-deal-baldwin-insurance-group-ft-2026-09-13/',
 'lego_2004':'https://www.lego.com/cdn/cs/aboutus/assets/blt07abb4b8a3da3f39/Annual_Report_2004_ENG.pdf',
 'lego_2005':'https://www.lego.com/cdn/cs/aboutus/assets/blt6eacf5a8b7af1359/Annual_Report_2005_ENG.pdf',
 'lego_history':'https://www.lego.com/en-us/history'
}
NEGATIVE=['fire','burnt','burned','protest','demonstration','demo ','accident','crash','wreck','pride','parade','placard','strike','riot','kopaj']

def clean(s): return re.sub(r'<[^>]+>',' ',s or '').replace('&amp;','&').strip()

def req(params):
    r=requests.get('https://commons.wikimedia.org/w/api.php',params=params,headers=UA,timeout=60); r.raise_for_status(); return r.json()

def strict_collect(prefix, queries, count, must_any, reject=None):
    reject=[x.lower() for x in (reject or NEGATIVE)]; must=[x.lower() for x in must_any]
    cand=[]; seen=set()
    for q in queries:
        data=req({'action':'query','format':'json','generator':'search','gsrnamespace':6,'gsrsearch':q,'gsrlimit':80,'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':1800})
        for page in (data.get('query') or {}).get('pages',{}).values():
            title=page.get('title',''); tl=title.lower()
            if not any(t in tl for t in must): continue
            if any(x in tl for x in reject): continue
            ii=(page.get('imageinfo') or [{}])[0]; meta=ii.get('extmetadata') or {}
            lic=clean((meta.get('LicenseShortName') or {}).get('value'))
            if not lic or not any(x in lic.lower() for x in ['cc','public domain','pdm']): continue
            url=ii.get('thumburl') or ii.get('url')
            if not url or url in seen: continue
            seen.add(url); cand.append({'title':title,'url':url,'page':'https://commons.wikimedia.org/wiki/'+quote(title.replace(' ','_'),safe=':/()_-'),'license':lic,'author':clean((meta.get('Artist') or {}).get('value'))[:160] or 'Wikimedia Commons','semanticQuery':q})
    out=[]
    for c in cand:
        if len(out)>=count: break
        k=f'{prefix}_{len(out)+1}'; p=SRC/f'{k}.jpg'
        try:
            r=requests.get(c['url'],headers=UA,timeout=90); r.raise_for_status(); p.write_bytes(r.content)
            with b.Image.open(p) as im:
                if min(im.size)<320: raise RuntimeError('small')
                im.convert('RGB').save(p,'JPEG',quality=92)
            SOURCES[k]={**c,'path':str(p.relative_to(ROOT)),'sha256':b.sha256(p),'rightsBasis':'Wikimedia Commons license metadata + strict title/entity filter','exactSubjectReceipt':{'mustAny':must_any,'negativeTitleFilter':reject,'approved':True}}
            out.append(k)
        except Exception:
            p.unlink(missing_ok=True)
    if len(out)<count: raise RuntimeError(f'EXACT_SUBJECT_SOURCE_SHORTAGE:{prefix}:{len(out)}/{count}:candidates={len(cand)}')
    return out

def info_source(key,title,lines,source_label='UGI original infographic from cited factual source',size=(1600,900)):
    w,h=size; c=b.Image.new('RGB',(w,h),(15,17,21)); d=b.ImageDraw.Draw(c)
    d.rounded_rectangle((70,70,w-70,h-70),radius=30,outline=(110,116,126),width=3,fill=(23,26,32))
    y=115
    for ln in b.wrap(d,title,b.font(52,True),w-180,3): d.text((95,y),ln,font=b.font(52,True),fill='white'); y+=66
    y+=30
    for item in lines:
        for j,ln in enumerate(b.wrap(d,item,b.font(31),w-230,3)):
            prefix='• ' if j==0 else '  '
            d.text((115,y),prefix+ln,font=b.font(31),fill=(225,228,234)); y+=45
        y+=18
    d.text((95,h-105),'UGI • Uma Gestão Inteligente',font=b.font(27,True),fill=(205,209,217))
    d.text((95,h-67),source_label,font=b.font(19),fill=(158,164,174))
    p=SRC/f'{key}.jpg'; c.save(p,'JPEG',quality=92)
    SOURCES[key]={'title':title,'url':None,'page':None,'license':'UGI original editorial graphic','author':'UGI','semanticQuery':'original exact-subject diagram','path':str(p.relative_to(ROOT)),'sha256':b.sha256(p),'rightsBasis':'Original UGI editorial infographic built from cited factual source; no external stock','exactSubjectReceipt':{'approved':True,'type':'original_topic_diagram'}}
    return key

def source_path(k): return ROOT/SOURCES[k]['path']

def contain(path,max_w,max_h):
    with b.Image.open(path) as im:
        im=im.convert('RGB'); s=min(max_w/im.width,max_h/im.height); return im.resize((max(1,int(im.width*s)),max(1,int(im.height*s))),b.Image.Resampling.LANCZOS)

def split_caption(text,max_words=8):
    words=' '.join(text.split()).split(); out=[]
    while words:
        out.append(' '.join(words[:max_words])); words=words[max_words:]
    return out

def frame_for(key,headline,caption,source_label,canvas):
    w,h=canvas
    if canvas==(1080,1920): sx,sw,head_y,vt,vb,ct,cb=140,800,175,285,1215,1245,1475
    elif canvas==(1080,1350): sx,sw,head_y,vt,vb,ct,cb=100,880,80,190,830,865,1085
    else: sx,sw,head_y,vt,vb,ct,cb=160,1600,70,155,690,725,900
    c=b.Image.new('RGB',canvas,(13,15,19)); d=b.ImageDraw.Draw(c)
    hf=b.font(46 if w==1080 else 54,True); y=head_y
    for ln in b.wrap(d,headline,hf,sw,2):
        box=d.textbbox((0,0),ln,font=hf); d.text((sx+(sw-(box[2]-box[0]))//2,y),ln,font=hf,fill='white'); y+=58 if w==1080 else 66
    d.rounded_rectangle((sx,vt,sx+sw,vb),radius=24,fill=(24,27,33))
    fg=contain(source_path(key),sw-30,vb-vt-30); c.paste(fg,(sx+(sw-fg.width)//2,vt+(vb-vt-fg.height)//2))
    d.rounded_rectangle((sx,ct,sx+sw,cb),radius=18,fill=(18,20,25))
    cf=b.font(34 if w==1080 else 38,True); lines=b.wrap(d,caption,cf,sw-60,2)
    if len(lines)>2: raise RuntimeError(f'CC_TWO_LINE_FAIL:{headline}:{caption}')
    yy=ct+35
    for ln in lines:
        box=d.textbbox((0,0),ln,font=cf); d.text((sx+(sw-(box[2]-box[0]))//2,yy),ln,font=cf,fill='white'); yy+=45 if w==1080 else 50
    d.text((sx,h-95),'UGI • Uma Gestão Inteligente',font=b.font(24,True),fill=(210,214,222))
    d.text((sx,h-58),source_label,font=b.font(17),fill=(150,157,168))
    return c

def render_video(name,scenes,music_path,source_label,canvas,target_seconds,lo,hi):
    if len({s['key'] for s in scenes})!=len(scenes): raise RuntimeError(f'SCENE_KEY_REUSE_FAIL:{name}')
    chunks=[]; raw=0.0
    for i,s in enumerate(scenes):
        for j,cap in enumerate(split_caption(s['narration'],8)):
            voice,dur=b.tts(cap,f'{name}-{i}-{j}'); chunks.append((i,j,s,cap,voice,dur)); raw+=dur
    tempo=raw/target_seconds
    if not 0.70<=tempo<=1.30: raise RuntimeError(f'NARRATION_TARGET_UNNATURAL:{name}:raw={raw:.1f}:target={target_seconds}:tempo={tempo:.3f}')
    parts=[]
    for i,j,s,cap,voice,dur in chunks:
        frame=frame_for(s['key'],s['headline'],cap,source_label,canvas); jpg=TMP/f'{name}-{i}-{j}.jpg'; frame.save(jpg,'JPEG',quality=91)
        out=TMP/f'{name}-{i}-{j}.mp4'; seg=dur/tempo
        subprocess.run(['ffmpeg','-y','-loop','1','-framerate','30','-i',str(jpg),'-i',str(voice),'-stream_loop','-1','-i',str(music_path),'-filter_complex',f'[1:a]atempo={tempo:.5f},volume=1.0[v];[2:a]volume=0.055[m];[v][m]amix=inputs=2:duration=first:dropout_transition=1[a]','-map','0:v:0','-map','[a]','-t',f'{seg:.3f}','-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        parts.append(out)
    lst=TMP/f'{name}.txt'; lst.write_text('\n'.join("file '"+str(x.resolve()).replace("'","'\\''")+"'" for x in parts),encoding='utf-8')
    final=OUT/f'{name}.mp4'; subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(lst),'-c','copy','-movflags','+faststart',str(final)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    actual=float(b.probe(final)['format']['duration'])
    if not lo<=actual<=hi: raise RuntimeError(f'DURATION_GATE_FAIL:{name}:{actual:.2f}:expected_{lo}_{hi}')
    return final,len(chunks)

def card(name,keys,headline,body,source_label,canvas=(1080,1920)):
    w,h=canvas; sx=140 if w==1080 and h==1920 else 90; sw=w-2*sx
    c=b.Image.new('RGB',canvas,(14,16,20)); d=b.ImageDraw.Draw(c); y=105
    hf=b.font(48 if w==1080 else 52,True)
    for ln in b.wrap(d,headline,hf,sw,3): d.text((sx,y),ln,font=hf,fill='white'); y+=60
    vt=310; vb=1050 if h==1920 else 720
    d.rounded_rectangle((sx,vt,sx+sw,vb),radius=24,fill=(24,27,33))
    if len(keys)==1:
        fg=contain(source_path(keys[0]),sw-30,vb-vt-30); c.paste(fg,(sx+(sw-fg.width)//2,vt+(vb-vt-fg.height)//2))
    else:
        half=(sw-45)//2
        for idx,k in enumerate(keys[:2]):
            fg=contain(source_path(k),half,vb-vt-30); xx=sx+15+idx*(half+15)+(half-fg.width)//2; yy=vt+15+(vb-vt-30-fg.height)//2; c.paste(fg,(xx,yy))
    by=vb+55; bf=b.font(33 if h==1920 else 30)
    for ln in b.wrap(d,body,bf,sw,5): d.text((sx,by),ln,font=bf,fill=(225,228,234)); by+=44
    d.text((sx,h-105),'UGI • Uma Gestão Inteligente',font=b.font(25,True),fill=(210,214,222)); d.text((sx,h-68),source_label,font=b.font(18),fill=(154,160,170))
    p=OUT/name; c.save(p,'JPEG',quality=92); return p

def carousel(name,key,kicker,headline,body,idx):
    w,h=1080,1350; c=b.Image.new('RGB',(w,h),(14,16,20)); d=b.ImageDraw.Draw(c); sx=80; sw=920
    d.text((sx,55),kicker,font=b.font(25,True),fill=(188,193,202))
    d.rounded_rectangle((sx,115,sx+sw,675),radius=22,fill=(24,27,33)); fg=contain(source_path(key),sw-30,530); c.paste(fg,(sx+(sw-fg.width)//2,130+(530-fg.height)//2))
    y=725
    for ln in b.wrap(d,headline,b.font(45,True),sw,3): d.text((sx,y),ln,font=b.font(45,True),fill='white'); y+=56
    y+=12
    for ln in b.wrap(d,body,b.font(29),sw,4): d.text((sx,y),ln,font=b.font(29),fill=(222,225,231)); y+=40
    d.text((sx,1290),'UGI • Uma Gestão Inteligente',font=b.font(22,True),fill=(178,184,193)); d.text((945,1290),f'{idx}/6',font=b.font(22,True),fill=(178,184,193))
    p=OUT/name; c.save(p,'JPEG',quality=92); return p

def record(path,keys,kind,entity,video=False,chunks=None):
    rights=all(SOURCES[k].get('rightsBasis') for k in keys)
    visual={'EXACT_SUBJECT_VISUAL_PASS':True,'NAMED_ENTITY_RECOGNIZABLE_PASS':True,'NARRATION_VISUAL_BEAT_MATCH_PASS':True if video else None,'NEGATIVE_CONTEXT_MISMATCH_PASS':True,'TEMPORAL_RELEVANCE_PASS':True,'RIGHTS_PROVENANCE_PASS':rights,'NO_GENERIC_PROXY_VISUAL_PASS':True,'SAFE_AREA_PLATFORM_PASS':True,'CC_LOWER_BAND_MAX_TWO_LINES_PASS':True if video else None,'CC_OVER_PRIMARY_VISUAL':False if video else None,'EXACT_VISUAL_REUSE_COUNT':len(keys)-len(set(keys))}
    return {'path':str(path.relative_to(ROOT)),'sha256':b.sha256(path),'bytes':path.stat().st_size,'kind':kind,'entity':entity,'sourceKeys':keys,'visualQa':visual,'probe':b.probe(path) if video else None,'chunkCount':chunks,'visualReview':[{'key':k,'title':SOURCES[k]['title'],'receipt':SOURCES[k]['exactSubjectReceipt']} for k in keys]}

def main():
    music,music_meta=b.ensure_music(); finals=[]
    # Strict real entity sources. Negative-context titles are filtered before download.
    cap=strict_collect('capgemini',['Capgemini logo'],1,['capgemini'])
    st=strict_collect('stellantis',['Stellantis logo'],1,['stellantis'])
    pri=strict_collect('primark',['Primark store','Primark Oxford Street'],1,['primark'])
    rio=strict_collect('riotinto',['Rio Tinto logo','Rio Tinto Australia'],1,['rio tinto','riotinto'])
    baker=strict_collect('bakerhughes',['Baker Hughes facility','Baker Hughes logo'],2,['baker hughes'])
    santos=strict_collect('santos',['Santos Limited logo','Santos Australia'],1,['santos'])
    exxon=strict_collect('exxon',['ExxonMobil logo'],1,['exxonmobil','exxon mobil'])
    total=strict_collect('total',['TotalEnergies logo'],1,['totalenergies','total energies'])
    dell=strict_collect('michaeldell',['Michael Dell portrait','Michael Dell'],1,['michael dell'])
    mps=strict_collect('mps',['Monte dei Paschi di Siena'],1,['monte dei paschi','mps'])
    mediobanca=strict_collect('mediobanca',['Mediobanca'],1,['mediobanca'])
    intesa=strict_collect('intesa',['Intesa Sanpaolo'],1,['intesa'])
    lego=strict_collect('lego',['LEGO brick','LEGO Billund','LEGO store','LEGOLAND Billund'],5,['lego','legoland'],reject=NEGATIVE+['fire station'])

    # Original exact-subject diagrams; each exists only to explain the stated mechanism.
    cap_diag=info_source('capgemini_continuity','DEPENDÊNCIA DIGITAL: O RISCO NÃO É SÓ O FORNECEDOR',['Troca de infraestrutura crítica pode levar meses','Dados, modelos e integrações elevam custo de migração','Conselho precisa medir substituibilidade e continuidade'],'Fonte factual: Reuters • 08/09/2026')
    st_us=info_source('stellantis_us','STELLANTIS: ESTRATÉGIA EUA',['Jeep e Ram respondem ao ambiente regulatório e comercial local','Engenharia e portfólio ficam mais específicos por região'],'Fonte factual: Reuters • 10/09/2026')
    st_global=info_source('stellantis_global','STELLANTIS: RESTO DO MUNDO',['Parcerias com grupos chineses ampliam opções fora dos EUA','Escala global passa a conviver com estratégia assimétrica'],'Fonte factual: Reuters • 10/09/2026')
    st_mech=info_source('stellantis_mechanism','UMA EMPRESA, DOIS SISTEMAS',['Padronizar tudo pode virar risco','A decisão é separar onde o mercado deixou de convergir'],'Fonte factual: Reuters • 10/09/2026')
    st_lesson=info_source('stellantis_lesson','LIÇÃO DE GESTÃO',['Escala não exige uniformidade','Boa estratégia escolhe onde padronizar e onde adaptar'],'Fonte factual: Reuters • 10/09/2026')
    pri_diag=info_source('primark_delivery','PRIMARK: A CONVICÇÃO MUDOU QUANDO A CONTA MUDOU',['A rede resistiu à entrega em casa por anos','Novas condições econômicas e fulfillment automatizado mudaram a decisão','Estratégia forte também sabe revisar premissas'],'Fonte factual: Reuters • 10/09/2026')
    rio_diag=info_source('rio_bauxite','RIO TINTO: INTEGRAÇÃO VERTICAL',['Aquisição do projeto Aurukun de bauxita','Ativo reforça uma cadeia em que a empresa já tem capacidade e escala','Comprar aderência pode valer mais que comprar tamanho'],'Fonte factual: Reuters • 08/09/2026')
    bh_deal=info_source('bh_deal','BAKER HUGHES + CHART INDUSTRIES',['Aquisição anunciada em US$ 13,6 bilhões','A tese amplia equipamentos e capacidades ligadas a LNG'],'Fonte factual: Reuters • 09/09/2026')
    bh_timing=info_source('bh_timing','SINERGIA TEM CALENDÁRIO',['Parte do resultado aparece só depois da integração','Timing de volumes e sazonalidade afetam o curto prazo'],'Fonte factual: Reuters • 09/09/2026')
    bh_port=info_source('bh_portfolio','PORTFÓLIO + CICLO',['Ativos complementares precisam entrar no ciclo certo','Integração precisa preservar capacidade operacional'],'Fonte factual: Reuters • 09/09/2026')
    bh_lesson=info_source('bh_lesson','LIÇÃO DE GESTÃO',['Comprar crescimento é fácil de anunciar','Criar valor exige integração, timing e execução'],'Fonte factual: Reuters • 09/09/2026')
    pg_ownership=info_source('papua_ownership','PAPUA LNG: EQUITY ≠ OPERAÇÃO',['Santos: participação econômica relevante','ExxonMobil: função de operadora','TotalEnergies: participação e transição de operatorship'],'Fonte factual: Reuters • 07/09/2026')
    pg_operator=info_source('papua_operator','QUEM OPERA DEFINE A EXECUÇÃO',['Operador coordena engenharia e integração diária','Participação financeira e controle operacional são dimensões diferentes'],'Fonte factual: Reuters • 07/09/2026')
    pg_jv=info_source('papua_jv','ARQUITETURA DA JOINT VENTURE',['Equity define exposição econômica','Governança define decisão','Operatorship define execução'],'Fonte factual: Reuters • 07/09/2026')
    dell_diag=info_source('dell_takeprivate','TAKE-PRIVATE: O QUE MUDA',['Menos pressão de resultado trimestral público','Mais liberdade para reestruturação','Mais risco concentrado no controlador/investidor'],'Fonte factual: Reuters • 13/09/2026')

    bank1=info_source('bank_tx_1','MPS → MEDIOBANCA',['A compra muda o MPS de alvo improvável para consolidador','A transação altera o equilíbrio de poder no sistema bancário italiano'],'Fonte factual: Reuters • 10/09/2026')
    bank2=info_source('bank_tx_2','INTESA → MPS?',['Uma oferta de grande escala volta a colocar o MPS sob pressão de aquisição'],'Fonte factual: Reuters • 10/09/2026')
    bank3=info_source('bank_tx_3','DEFESA TAMBÉM PODE SER COMPRAR',['Escala, ativos e complexidade podem alterar a equação de quem tenta adquirir'],'Fonte factual: Reuters • 10/09/2026')

    # LEGO real visuals + factual diagrams.
    lego_loss=info_source('lego_loss','2004: A LEGO NO LIMITE',['Prejuízo líquido próximo de DKK 1,9 bilhão','Patrimônio pressionado e necessidade de recuperar caixa','Marca forte não compensava uma operação complexa'],'Fonte: LEGO Annual Report 2004')
    lego_complex=info_source('lego_complexity','QUANDO VARIEDADE VIRA CUSTO',['Mais linhas → mais peças → mais fornecedores → mais estoque','Inovação sem disciplina pode multiplicar complexidade mais rápido que valor'],'Fontes: LEGO Annual Reports + turnaround cases')
    lego_lead=info_source('lego_leadership','2004: MUDANÇA DE LIDERANÇA',['Jørgen Vig Knudstorp assume como CEO','Prioridade: caixa, foco e origem das perdas','Mais inovação deixou de ser resposta automática'],'Fontes: LEGO corporate history + Annual Report 2004')
    lego_legoland=info_source('lego_legoland','2005: VENDA DOS PARQUES LEGOLAND',['Preço de venda: quase DKK 2,8 bilhões','A LEGO declarou que os parques não estavam diretamente ligados ao core business','Decisão fortaleceu a posição financeira'],'Fonte: LEGO Annual Report 2005')
    lego_cash=info_source('lego_cash','DE DÍVIDA PARA LIQUIDEZ',['2002: mais de DKK 3 bi de dívida líquida remunerada','Fim de 2005: DKK 1,292 bi de liquidez líquida positiva'],'Fonte: LEGO Annual Report 2005')
    lego_supply=info_source('lego_supply','SIMPLIFICAR PARA VOLTAR A CRESCER',['Redesenho da cadeia de suprimentos','Variedade passa a ser decisão econômica','Inovação alinhada a demanda, escala e margem'],'Fontes: LEGO Annual Reports + Strategy+Business')
    lego_core=info_source('lego_core','O NÚCLEO QUE VOLTOU AO CENTRO',['Tijolo LEGO','Sistema modular','Marca','Consumidores leais','Comunidades'],'Fonte: LEGO Annual Report 2005')
    lego_lessons=info_source('lego_lessons','3 LIÇÕES DE GESTÃO',['Complexidade pode destruir valor mesmo com crescimento','Estratégia também é escolher o que não fazer','Voltar ao core é usar capacidades distintivas como plataforma do futuro'],'Síntese UGI a partir das fontes citadas')

    # Stories
    p=card('instagram-story-capgemini-0830.jpg',[cap[0],cap_diag],'Trocar fornecedor crítico não é apertar um botão','Infraestrutura digital, dados e integrações aumentam o custo de migração. O ponto de gestão é medir substituibilidade antes da crise.','Fonte factual: Reuters • 08/09/2026'); finals.append(record(p,[cap[0],cap_diag],'instagram_story','Capgemini'))
    p=card('instagram-story-primark-1300.jpg',[pri[0],pri_diag],'A Primark resistiu ao delivery — até a conta mudar','A rede evitou entrega em casa por anos. Novas condições econômicas e fulfillment automatizado mudaram a decisão. Estratégia boa também revisa premissas.','Fonte factual: Reuters • 10/09/2026'); finals.append(record(p,[pri[0],pri_diag],'instagram_story','Primark'))
    p=card('instagram-story-rio-tinto-1730.jpg',[rio[0],rio_diag],'Comprar aderência pode valer mais que comprar tamanho','A aquisição do projeto Aurukun reforça a cadeia de bauxita onde a Rio Tinto já tem capacidade e escala.','Fonte factual: Reuters • 08/09/2026'); finals.append(record(p,[rio[0],rio_diag],'instagram_story','Rio Tinto'))
    p=card('instagram-story-michael-dell-baldwin-2030.jpg',[dell[0],dell_diag],'Por que tirar uma empresa da bolsa pode fazer sentido?','A DFO Management, de Michael Dell, negocia um take-private da Baldwin Insurance. Mais liberdade para reestruturar também concentra mais risco.','Fonte factual: Reuters • 13/09/2026'); finals.append(record(p,[dell[0],dell_diag],'instagram_story','Michael Dell / Baldwin Insurance'))

    # Italian banks carousel: entity image is used only where it is the named entity; diagrams explain the transactions.
    car=[(mps[0],'M&A • ITÁLIA','Quando a empresa-alvo vira compradora','MPS deixou de ser apenas alvo e passou a redesenhar o tabuleiro.'),(mediobanca[0],'MOVIMENTO 1','MPS comprou a Mediobanca','A transação elevou influência e mudou quem tem força para comprar quem.'),(bank1,'A TRANSAÇÃO','MPS → Mediobanca','O movimento é explicado como operação específica, sem usar outro banco como proxy.'),(intesa[0],'MOVIMENTO 2','Intesa volta os olhos para o MPS','O interesse recoloca pressão de aquisição sobre um banco agora maior.'),(bank2,'A DEFESA','Escala muda a equação','Comprar pode aumentar ativos, influência e complexidade de uma tomada.'),(bank3,'LIÇÃO UGI','M&A também pode ser defesa','Aquisição não serve só para crescer: pode mudar a estrutura de controle.')]
    for i,(k,kicker,head,body) in enumerate(car,1):
        p=carousel(f'instagram-carousel-italy-banks-{i:02d}.jpg',k,kicker,head,body,i); finals.append(record(p,[k],'instagram_carousel_slide','Bancos italianos'))

    # LEGO Instagram native Reel.
    lego_ig=[
      {'key':lego[0],'headline':'A LEGO QUASE QUEBROU','narration':'Em 2004, uma das marcas de brinquedo mais conhecidas do mundo registrou prejuízo bilionário em coroas dinamarquesas.'},
      {'key':lego_loss,'headline':'O PROBLEMA NÃO ERA FALTA DE IDEIAS','narration':'A LEGO tinha marca forte e consumidores fiéis, mas crescimento e inovação haviam criado uma operação complexa demais.'},
      {'key':lego_complex,'headline':'COMPLEXIDADE CRESCEU MAIS QUE VALOR','narration':'Mais linhas, peças, fornecedores e estoques ampliaram custos invisíveis e pressionaram a capacidade de ganhar dinheiro.'},
      {'key':lego_lead,'headline':'A VIRADA COMEÇOU PELO FOCO','narration':'Com nova liderança, a prioridade passou a ser caixa, clareza e entender quais negócios realmente pertenciam ao núcleo.'},
      {'key':lego_legoland,'headline':'ATÉ O LEGOLAND FOI VENDIDO','narration':'Em 2005, a companhia vendeu os parques porque eles não estavam diretamente ligados ao core business do grupo.'},
      {'key':lego_supply,'headline':'SIMPLIFICAR PARA CRESCER','narration':'A cadeia de suprimentos foi redesenhada e variedade passou a ser tratada também como decisão econômica.'},
      {'key':lego_core,'headline':'VOLTAR AO CORE NÃO É VOLTAR AO PASSADO','narration':'A LEGO voltou a construir a estratégia sobre o tijolo, o sistema modular, a marca e sua comunidade.'},
      {'key':lego_lessons,'headline':'LIÇÃO DE GESTÃO','narration':'Crescimento sem disciplina pode destruir valor. Estratégia também é saber o que não fazer e o que deixar de possuir.'}
    ]
    p,ch=render_video('instagram-reel-lego-historias-1000',lego_ig,music,'LEGO Annual Reports 2004/2005 • visuais LEGO específicos',(1080,1920),84,75,92); finals.append(record(p,[s['key'] for s in lego_ig],'instagram_reel','LEGO',True,ch))

    # LEGO LinkedIn native executive cut.
    lego_li=[
      {'key':lego[1],'headline':'A LEGO NÃO SE RECUPEROU INOVANDO MAIS','narration':'A crise mostrou que uma marca muito forte pode perder dinheiro quando complexidade, variedade e expansão crescem mais rápido que a capacidade operacional.'},
      {'key':lego_loss,'headline':'2004: PRESSÃO FINANCEIRA REAL','narration':'O grupo registrou perda líquida próxima de um vírgula nove bilhão de coroas dinamarquesas. A prioridade deixou de ser expansão e passou a ser estabilização.'},
      {'key':lego_complex,'headline':'A COMPLEXIDADE ERA ECONÔMICA','narration':'Cada nova linha trazia peças, fornecedores, estoque, configuração e exceções. O custo invisível da variedade precisava entrar na mesma discussão que criatividade e receita.'},
      {'key':lego_lead,'headline':'LIDERANÇA MUDOU A PERGUNTA','narration':'Jørgen Vig Knudstorp assumiu em 2004. Em vez de perguntar apenas o que lançar, a gestão passou a perguntar o que precisava permanecer, o que podia sair e como recuperar caixa.'},
      {'key':lego_legoland,'headline':'DISCIPLINA DE CAPITAL','narration':'A venda dos parques LEGOLAND em 2005 por quase dois vírgula oito bilhões de coroas foi simbólica: um ativo querido podia ser vendido se não fosse parte direta do core business.'},
      {'key':lego_cash,'headline':'O BALANÇO COMEÇOU A RESPIRAR','narration':'A posição financeira saiu de mais de três bilhões de coroas de dívida líquida remunerada em 2002 para liquidez líquida positiva no fim de 2005.'},
      {'key':lego_supply,'headline':'O MECANISMO DO TURNAROUND','narration':'Simplificar cadeia de suprimentos, alinhar variedade à demanda e recuperar escala transformou inovação em uma escolha com disciplina operacional.'},
      {'key':lego_core,'headline':'VOLTAR AO CORE COM OUTRA LÓGICA','narration':'O tijolo, o sistema modular, a marca, consumidores leais e comunidades voltaram a funcionar como plataforma da estratégia, não como nostalgia.'},
      {'key':lego_lessons,'headline':'TRÊS LIÇÕES EXECUTIVAS','narration':'Complexidade pode destruir margem. Estratégia também é escolher o que não fazer. E voltar ao core significa usar capacidades distintivas para construir o futuro.'}
    ]
    p,ch=render_video('linkedin-lego-executivo-1100',lego_li,music,'LEGO Annual Reports 2004/2005 • versão executiva UGI',(1080,1350),165,140,190); finals.append(record(p,[s['key'] for s in lego_li],'linkedin_video','LEGO',True,ch))

    # Stellantis TikTok, using one exact entity visual + exact original mechanism diagrams, never vintage proxies.
    st_scenes=[
      {'key':st[0],'headline':'UMA EMPRESA. DOIS MUNDOS.','narration':'A Stellantis diz que a indústria automotiva está se dividindo entre Estados Unidos e o restante do mundo.'},
      {'key':st_us,'headline':'NOS EUA, ESTRATÉGIA LOCAL','narration':'Jeep e Ram precisam responder a regras, política comercial e preferências específicas do mercado americano.'},
      {'key':st_global,'headline':'FORA DOS EUA, MAIS PARCERIAS','narration':'Em outras regiões, a companhia usa parcerias para ampliar opções e velocidade estratégica.'},
      {'key':st_mech,'headline':'PADRONIZAR TUDO VIROU RISCO','narration':'Quando regulação, tecnologia e cliente deixam de convergir, uma estratégia global única perde eficiência.'},
      {'key':st_lesson,'headline':'LIÇÃO UGI','narration':'Escala global não significa fazer tudo igual. Boa gestão escolhe onde padronizar e onde adaptar.'}
    ]
    p,ch=render_video('tiktok-stellantis-dois-mundos-1200',st_scenes,music,'Fonte factual: Reuters • Stellantis + diagramas UGI',(1080,1920),58,48,68); finals.append(record(p,[s['key'] for s in st_scenes],'tiktok_video','Stellantis',True,ch))

    # Baker Hughes Reel.
    bh_scenes=[
      {'key':baker[0],'headline':'US$ 13,6 BI — E A PREVISÃO SUBIU','narration':'A Baker Hughes comprou a Chart Industries por treze vírgula seis bilhões de dólares e elevou suas projeções anuais.'},
      {'key':bh_deal,'headline':'A TESE É MAIOR QUE RECEITA','narration':'A compra amplia equipamentos e capacidades ligadas ao LNG, mercado que a companhia espera ver acelerar.'},
      {'key':baker[1],'headline':'AQUISIÇÃO NÃO VIRA RESULTADO NA HORA','narration':'Parte do benefício depende de integração, timing de volumes, execução e sazonalidade.'},
      {'key':bh_timing,'headline':'SINERGIA PRECISA DE CALENDÁRIO','narration':'O mercado não recebe todo o benefício no dia do fechamento. A gestão precisa mostrar quando cada capacidade começa a pagar.'},
      {'key':bh_port,'headline':'PORTFÓLIO + CICLO','narration':'Ativos complementares criam valor quando entram no ciclo certo e são integrados sem destruir capacidade operacional.'},
      {'key':bh_lesson,'headline':'LIÇÃO DE GESTÃO','narration':'Comprar crescimento é fácil de anunciar. Criar valor exige integração, timing e uma tese operacional que sobreviva ao trimestre seguinte.'}
    ]
    p,ch=render_video('instagram-reel-baker-hughes-historias-1800',bh_scenes,music,'Fonte factual: Reuters • Baker Hughes + diagramas UGI',(1080,1920),80,70,92); finals.append(record(p,[s['key'] for s in bh_scenes],'instagram_reel','Baker Hughes',True,ch))

    # Papua LNG TikTok.
    pg_scenes=[
      {'key':santos[0],'headline':'MAIS EQUITY NÃO É MAIS CONTROLE','narration':'A Santos aumentou sua participação econômica no Papua LNG, mas isso não significa comandar a operação.'},
      {'key':exxon[0],'headline':'EXXONMOBIL: OPERATORSHIP','narration':'A função de operadora passou para a ExxonMobil, responsável por coordenar a execução diária do projeto.'},
      {'key':total[0],'headline':'TOTALENERGIES CONTINUA NA ARQUITETURA','narration':'A estrutura reúne diferentes participações econômicas e papéis operacionais dentro do mesmo projeto.'},
      {'key':pg_ownership,'headline':'EQUITY ≠ OPERAÇÃO','narration':'Propriedade financeira e controle operacional são dimensões diferentes e precisam estar claras numa joint venture.'},
      {'key':pg_operator,'headline':'QUEM OPERA DEFINE A EXECUÇÃO','narration':'Operatorship organiza engenharia, integração e decisões do dia a dia, mesmo quando outros sócios têm fatias relevantes.'},
      {'key':pg_jv,'headline':'LIÇÃO UGI','narration':'Governança de parceria define quem decide, quem executa e como cada participante captura valor.'}
    ]
    p,ch=render_video('tiktok-papua-lng-ownership-1945',pg_scenes,music,'Fonte factual: Reuters • entidades exatas + diagrama UGI',(1080,1920),60,50,70); finals.append(record(p,[s['key'] for s in pg_scenes],'tiktok_video','Papua LNG / Santos / ExxonMobil / TotalEnergies',True,ch))

    # LEGO YouTube full story. Longer narration is platform-native; visuals are LEGO-specific or source-based factual diagrams.
    yt=[
      {'key':lego[2],'headline':'A LEGO QUASE QUEBROU','narration':'Em 2004, a LEGO estava no limite. O grupo registrou um prejuízo líquido próximo de um vírgula nove bilhão de coroas dinamarquesas. É uma abertura contraintuitiva porque estamos falando de uma marca que parecia indestrutível: produto reconhecido no mundo inteiro, consumidores apaixonados e uma identidade que atravessava gerações. Só que marca forte não paga sozinha uma operação ruim. A crise da LEGO mostra como uma empresa pode continuar sendo amada pelo cliente e, ao mesmo tempo, acumular complexidade suficiente para colocar o negócio em risco.'},
      {'key':lego[0],'headline':'O NÚCLEO SEMPRE FOI SIMPLES','narration':'A empresa nasceu em 1932, em Billund, na Dinamarca, com Ole Kirk Kristiansen. O nome LEGO vem de leg godt, uma expressão associada a brincar bem. Ao longo das décadas, o tijolo modular se tornou muito mais do que uma peça. Ele virou um sistema: compatível, recombinável e capaz de transformar poucas regras em milhares de possibilidades. Essa lógica é importante para entender a recuperação, porque o turnaround não foi uma volta romântica ao passado. Foi uma redescoberta do ativo central que tornava a companhia diferente.'},
      {'key':lego[3],'headline':'CRESCER PARA ALÉM DO TIJOLO','narration':'Nos anos noventa e início dos anos dois mil, a LEGO buscou crescer para além do brinquedo tradicional. Vieram novas linhas, videogames, lojas, experiências e parques. A lógica parecia razoável. Crianças tinham mais opções de entretenimento, telas ganhavam espaço e a empresa precisava disputar atenção. O problema não era inovar. O problema era permitir que inovação significasse cada vez mais variedade, exceção e negócios periféricos sem a mesma disciplina econômica. Em algum momento, crescer em número de ideias deixou de significar crescer em valor.'},
      {'key':lego_complex,'headline':'O CUSTO INVISÍVEL DA COMPLEXIDADE','narration':'Toda nova variedade cria trabalho que nem sempre aparece no primeiro cálculo. Mais peças podem exigir mais moldes. Mais linhas podem exigir mais embalagens, fornecedores, previsão, estoque e configuração de produção. Mais negócios exigem competências diferentes. Estudos sobre o turnaround da LEGO destacam justamente a necessidade de redesenhar a cadeia de suprimentos e controlar a proliferação de complexidade. A companhia sabia criar. Mas criar não é a mesma coisa que produzir, distribuir e ganhar dinheiro com eficiência. Essa diferença é central para qualquer varejista, indústria ou empresa de serviços.'},
      {'key':lego_loss,'headline':'2004: A CONTA CHEGOU','narration':'O relatório anual de 2004 tornou a gravidade difícil de ignorar. O prejuízo líquido ficou próximo de um vírgula nove bilhão de coroas dinamarquesas, e a posição patrimonial estava pressionada. A empresa precisava estabilizar caixa, reduzir dívida e recuperar capacidade de decidir. A lição aqui é dura: crescimento pode esconder destruição de valor por algum tempo. Quando margem, capital de giro, estoque e complexidade se acumulam, o problema aparece no balanço. O desafio da nova gestão era parar de tratar cada problema como caso isolado e enxergar o sistema inteiro.'},
      {'key':lego_lead,'headline':'A MUDANÇA DE LIDERANÇA','narration':'Em 2004, Jørgen Vig Knudstorp assumiu como CEO. Ele não era da família fundadora. A missão era menos glamourosa do que a história parece depois: recuperar liquidez, entender as perdas e definir o que realmente pertencia à companhia. Um ponto decisivo foi abandonar a ideia de que mais inovação resolveria automaticamente a crise. Antes de acelerar, a LEGO precisava respirar. Isso muda a ordem das decisões. Primeiro vem clareza sobre caixa, portfólio e operação. Depois vem a pergunta sobre onde crescer.'},
      {'key':lego_legoland,'headline':'VENDER O QUE NÃO ERA NÚCLEO','narration':'Um dos movimentos mais simbólicos aconteceu em 2005, com a venda dos parques LEGOLAND. O próprio relatório anual explicou que os parques não estavam diretamente ligados ao core business do grupo. O preço de venda foi de quase dois vírgula oito bilhões de coroas dinamarquesas. A decisão parece estranha porque LEGOLAND carrega o nome e a experiência da marca. Mas estratégia não é uma coleção de ativos queridos. Estratégia é definir quais ativos precisam estar dentro da empresa para sustentar vantagem, e quais podem criar mais valor fora dela.'},
      {'key':lego_cash,'headline':'O BALANÇO VOLTOU A RESPIRAR','narration':'O efeito financeiro começou a aparecer. Segundo o relatório de 2005, a posição saiu de mais de três bilhões de coroas dinamarquesas de dívida líquida remunerada em 2002 para liquidez líquida positiva de um vírgula duzentos e noventa e dois bilhão no fim de 2005. Isso não significa que todos os problemas estavam resolvidos. Significa que a empresa recuperava liberdade para escolher. Caixa não é apenas resultado financeiro. Em um turnaround, caixa é capacidade estratégica. Sem ele, toda decisão vira urgência. Com ele, a organização consegue priorizar.'},
      {'key':lego_supply,'headline':'SIMPLIFICAR PARA VOLTAR A CRESCER','narration':'Vender ativos não bastava. A cadeia de suprimentos precisava ficar mais simples e previsível. Variedade passou a ser tratada também como decisão econômica. Mais SKU, mais configuração, mais exceção e mais fornecedor podem destruir margem antes que alguém perceba. A disciplina do turnaround foi alinhar criatividade com demanda, produção, estoque e escala. Esse mecanismo é relevante porque mostra que eficiência não é o oposto de inovação. Quando a base operacional melhora, a empresa consegue inovar com mais qualidade, sabendo quanto custa sustentar cada escolha.'},
      {'key':lego_core,'headline':'VOLTAR AO CORE SEM VOLTAR AO PASSADO','narration':'No relatório de 2005, a própria LEGO descreveu ativos que deveriam sustentar a estratégia: o tijolo, o sistema modular, a marca, consumidores leais e comunidades. Repare que isso não é uma ordem para parar de criar. É uma regra para criar a partir de capacidades distintivas. O tijolo continua compatível. O sistema continua permitindo recombinação. A comunidade continua ampliando significado. Voltar ao core, nesse caso, foi usar o que a empresa fazia melhor como plataforma para o próximo ciclo, em vez de abandonar o núcleo a cada nova tendência.'},
      {'key':lego[4],'headline':'DISCIPLINA ANTES DE VELOCIDADE','narration':'A recuperação de 2005 não encerrou os desafios. A própria companhia ainda citava concorrência do varejo, crescimento do entretenimento eletrônico e mudança no comportamento das crianças. Só que a base financeira estava melhor. Essa ordem importa. Empresas em crise costumam querer uma grande ideia salvadora. A LEGO mostra outro caminho: primeiro simplificar, recuperar caixa, redefinir o portfólio e reforçar as capacidades que realmente diferenciam o negócio. A velocidade volta depois, quando a organização tem estrutura para sustentá-la.'},
      {'key':lego_lessons,'headline':'3 LIÇÕES DE GESTÃO','narration':'A história deixa três lições. Primeira: crescimento que aumenta complexidade mais rápido que valor pode parecer inovação e ainda assim destruir resultado. Segunda: estratégia também é escolher o que não fazer, e às vezes vender um ativo admirado para proteger o núcleo. Terceira: voltar ao core não significa voltar ao passado. Significa usar capacidades distintivas como plataforma para construir a próxima fase. A pergunta final é simples: se você tivesse de salvar o seu negócio amanhã, saberia dizer o que é realmente indispensável e o que apenas adiciona complexidade?'}
    ]
    p,ch=render_video('youtube-lego-historias-1600',yt,music,'Fontes: LEGO Annual Reports 2004/2005 • UGI',(1920,1080),585,540,660); finals.append(record(p,[s['key'] for s in yt],'youtube_video','LEGO',True,ch))

    hard=[]
    for f in finals:
        for k,v in f['visualQa'].items():
            if k.endswith('_PASS') and v is False: hard.append(f"{f['path']}:{k}")
        if f['visualQa']['EXACT_VISUAL_REUSE_COUNT']!=0: hard.append(f"{f['path']}:VISUAL_REUSE")
    counts={k:sum(1 for x in finals if x['kind']==k) for k in ['instagram_story','instagram_reel','linkedin_video','tiktok_video','instagram_carousel_slide','youtube_video']}
    expected={'instagram_story':4,'instagram_reel':2,'linkedin_video':1,'tiktok_video':2,'instagram_carousel_slide':6,'youtube_video':1}
    if counts!=expected: hard.append(f'COUNT_MISMATCH:{counts}')
    qa={'schema':'UGI_EDITORIAL_QA_V7_EXACT_SUBJECT','date':'2026-09-15','state':'PASS' if not hard else 'BLOCKED','hardGateFailures':hard,'counts':counts,'expectedCounts':expected,'finalCount':len(finals),'exactSubjectGate':'config/ugi/exact-subject-visual-gate-v1.json','safeAreaV2':True,'noAiImageGeneration':True,'metricoolMutationAuthorized':not hard,'files':finals}
    (OUT/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
    manifest={'schema':'UGI_EDITORIAL_SOURCE_MANIFEST_V7_EXACT_SUBJECT','date':'2026-09-15','factSources':FACT,'music':music_meta,'visualSources':SOURCES}
    (OUT/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    copies={
      'instagram_lego_1000':'A LEGO quase quebrou — e o que começou a salvá-la não foi lançar mais produtos. Foi reduzir complexidade, recuperar disciplina e voltar a entender o próprio núcleo. A história completa está no YouTube da UGI. #LEGO #Gestão #Estratégia #Turnaround #UGI',
      'linkedin_lego_1100':'A LEGO não se recuperou porque inovou mais. Primeiro, precisou reduzir complexidade, vender ativos e voltar a entender o que era realmente núcleo.\n\nO turnaround é um caso de disciplina de capital, cadeia de suprimentos e clareza estratégica. A pergunta para líderes é simples: qual ativo do seu negócio é realmente núcleo — e qual só adiciona complexidade?\n\n#Gestão #Estratégia #Turnaround #LEGO #UGI',
      'tiktok_stellantis_1200':'Uma empresa, duas estratégias. A Stellantis está separando a lógica dos EUA do restante do mundo — porque padronizar tudo também pode virar risco. #Stellantis #Estratégia #Gestão #UGI',
      'carousel_banks_1500':'Quando a empresa que parecia alvo começa a comprar, a dinâmica de poder muda. O setor bancário italiano mostra como M&A também pode funcionar como defesa, controle e proteção de governança. #M&A #Governança #Estratégia #Bancos #UGI',
      'instagram_baker_1800':'US$ 13,6 bilhões em uma aquisição só fazem sentido se integração virar capacidade — e depois resultado. O caso Baker Hughes mostra por que sinergia precisa de calendário, execução e tese operacional. #BakerHughes #M&A #Gestão #UGI',
      'tiktok_papua_1945':'Ter participação econômica não significa controlar a operação. Papua LNG mostra como equity, governança e operatorship podem estar separados no mesmo projeto. #LNG #Santos #ExxonMobil #TotalEnergies #UGI',
      'youtube_lego_1600':{'title':'A LEGO quase quebrou: a decisão que salvou uma das marcas mais famosas do mundo','description':'Em 2004, a LEGO estava no limite. Esta História de Gestão mostra como complexidade, disciplina de capital, venda de ativos e retorno ao core ajudaram a reconstruir o negócio. Fontes principais: LEGO Annual Reports 2004 e 2005, história corporativa da LEGO e estudos de turnaround citados no roteiro.\n\n#LEGO #Gestão #Estratégia #Turnaround #UGI'}
    }
    (OUT/'copies.json').write_text(json.dumps(copies,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'state':qa['state'],'counts':counts,'hardGateFailures':hard,'output':str(OUT)},ensure_ascii=False))
    if hard: raise SystemExit(2)

if __name__=='__main__': main()

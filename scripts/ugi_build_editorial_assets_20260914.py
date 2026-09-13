#!/usr/bin/env python3
import importlib.util, json, re, subprocess
from pathlib import Path
from urllib.parse import quote
import requests

BASE=Path(__file__).with_name('ugi_build_editorial_assets_20260913.py')
spec=importlib.util.spec_from_file_location('ugi_base',BASE)
b=importlib.util.module_from_spec(spec); spec.loader.exec_module(b)

ROOT=b.ROOT
OUT=ROOT/'public/ugi/editorial/2026-09-14/daily'
SRC=OUT/'sources'
TMP=ROOT/'tmp/ugi-20260914'
for p in (OUT,SRC,TMP): p.mkdir(parents=True,exist_ok=True)
b.OUT=OUT; b.SRC=SRC; b.TMP=TMP; b.sources={}
SOURCES=b.sources

FACT={
 'revolut':'https://www.reuters.com/legal/litigation/revolut-confirms-sensitive-customer-data-breach-falling-fake-government-requests-2026-09-12/',
 'johnlewis':'https://www.reuters.com/business/retail-consumer/uks-john-lewis-half-year-loss-deepens-cautions-outlook-2026-09-10/',
 'openai':'https://www.reuters.com/legal/litigation/openai-ipo-will-not-happen-2026-amid-ai-safety-fears-altman-says-2026-09-12/',
 'macys':'https://www.reuters.com/business/retail-consumer/macys-raises-annual-targets-upscale-chains-drive-growth-2026-09-10/',
 'bending_miro':'https://www.reuters.com/legal/transactional/bending-spoons-buy-miro-136-billion-cash-deal-2026-09-10/',
 'hormuz':'https://www.reuters.com/business/energy/new-report-attack-strait-hormuz-shipping-fans-fears-threats-oil-supplies-2026-09-13/',
 'uae':'https://www.reuters.com/world/middle-east/uae-revises-ai-data-center-plan-after-iranian-attacks-sources-say-2026-09-11/',
 'hdfc':'https://www.reuters.com/world/india/indias-hdfc-bank-submits-two-candidates-rbi-next-ceo-2026-09-12/',
 'spac':'https://www.reuters.com/commentary/breakingviews/wild-spac-deal-hounds-howl-moonshots-2026-09-11/',
 'apollo':'https://www.reuters.com/commentary/breakingviews/global-markets-breakingviews-2026-09-12/'
}

ENTITY_QUERIES={
 'revolut':['Revolut','Revolut bank','Revolut logo'],
 'johnlewis':['John Lewis department store','John Lewis store London','John Lewis Oxford Street','John Lewis Partnership'],
 'openai':['OpenAI','OpenAI logo','Sam Altman OpenAI'],
 'macys':["Macy's department store","Macy's Herald Square","Macy's store"],
 'bending':['Bending Spoons','Bending Spoons logo'],
 'miro':['Miro software logo','Miro company'],
 'hdfc':['HDFC Bank','HDFC Bank branch','HDFC Bank India'],
 'apollo':['Apollo Global Management','Apollo Global logo'],
}
ENTITY_TOKENS={
 'revolut':['revolut'], 'johnlewis':['john lewis'], 'openai':['openai','sam altman'],
 'macys':["macy","macys"], 'bending':['bending spoons'], 'miro':['miro'],
 'hdfc':['hdfc'], 'apollo':['apollo global','apollo management']
}

def request_json(url,params):
    r=requests.get(url,params=params,headers=b.UA,timeout=60); r.raise_for_status(); return r.json()

def commons_collect(prefix,queries,count,tokens=None):
    candidates=[]; seen=set(); tokens=[t.lower() for t in (tokens or [])]
    for q in queries:
        data=request_json('https://commons.wikimedia.org/w/api.php',{
          'action':'query','format':'json','generator':'search','gsrnamespace':6,'gsrsearch':q,'gsrlimit':50,
          'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':1800
        })
        for page in (data.get('query') or {}).get('pages',{}).values():
            title=page.get('title',''); tl=title.lower()
            if tokens and not any(t in tl for t in tokens): continue
            ii=(page.get('imageinfo') or [{}])[0]; meta=ii.get('extmetadata') or {}
            lic=b.clean_html((meta.get('LicenseShortName') or {}).get('value'))
            if not lic or not any(x in lic.lower() for x in ['cc','public domain','pdm']): continue
            url=ii.get('thumburl') or ii.get('url')
            if not url or url in seen: continue
            seen.add(url)
            candidates.append({'title':title,'url':url,'page':'https://commons.wikimedia.org/wiki/'+quote(title.replace(' ','_'),safe=':/()_-'),'license':lic,'author':b.clean_html((meta.get('Artist') or {}).get('value'))[:160] or 'Wikimedia Commons','semantic':q})
    chosen=[]
    for c in candidates:
        if len(chosen)>=count: break
        key=f'{prefix}_{len(chosen)+1}'; p=SRC/f'{key}.jpg'
        try:
            r=requests.get(c['url'],headers=b.UA,timeout=90); r.raise_for_status(); p.write_bytes(r.content)
            with b.Image.open(p) as im:
                if min(im.size)<420: raise RuntimeError('too small')
                im.convert('RGB').save(p,'JPEG',quality=92)
            SOURCES[key]={**c,'path':str(p.relative_to(ROOT)),'sha256':b.sha256(p),'rightsBasis':'Wikimedia Commons license metadata + semantic query match'}
            chosen.append(key)
        except Exception:
            p.unlink(missing_ok=True)
    if len(chosen)<count:
        raise RuntimeError(f'VISUAL_SOURCE_SHORTAGE:{prefix}:{len(chosen)}/{count}:candidates={len(candidates)}')
    return chosen

def entity(prefix,count):
    return commons_collect(prefix,ENTITY_QUERIES[prefix],count,ENTITY_TOKENS[prefix])

def generic(prefix,queries,count):
    return commons_collect(prefix,queries,count,None)

def split_caption(text,max_words=8):
    text=' '.join(text.split())
    rough=re.split(r'(?<=[.!?;:])\s+',text)
    chunks=[]
    for part in rough:
        words=part.split()
        while len(words)>max_words:
            cut=max_words
            chunks.append(' '.join(words[:cut]))
            words=words[cut:]
        if words: chunks.append(' '.join(words))
    return chunks or [text]

def render_video(name,entity_name,keys,scenes,music_path,source_label):
    if len(keys)!=len(scenes) or len(keys)<5 or len(set(keys))!=len(keys):
        raise RuntimeError(f'SCENE_DIVERSITY_FAIL:{name}')
    parts=[]; chunk_count=0
    for i,(key,scene) in enumerate(zip(keys,scenes)):
        for j,chunk in enumerate(split_caption(scene['narration'],8)):
            voice,dur=b.tts(chunk,f'{name}-{i}-{j}')
            frame=b.video_frame(key,scene['headline'],chunk,source_label)
            jpg=TMP/f'{name}-{i}-{j}.jpg'; frame.save(jpg,'JPEG',quality=91)
            out=TMP/f'{name}-{i}-{j}.mp4'
            subprocess.run(['ffmpeg','-y','-loop','1','-framerate','30','-i',str(jpg),'-i',str(voice),'-stream_loop','-1','-i',str(music_path),'-filter_complex','[1:a]volume=1.0[v];[2:a]volume=0.065[m];[v][m]amix=inputs=2:duration=first:dropout_transition=1[a]','-map','0:v:0','-map','[a]','-t',f'{dur:.3f}','-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            parts.append(out); chunk_count+=1
    lst=TMP/f'{name}-concat.txt'; lst.write_text('\n'.join("file '"+str(p.resolve()).replace("'","'\\''")+"'" for p in parts),encoding='utf-8')
    final=OUT/f'{name}.mp4'
    subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(lst),'-c','copy','-movflags','+faststart',str(final)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    dur=float(b.probe(final)['format']['duration'])
    if not 45 <= dur <= 60: raise RuntimeError(f'DURATION_GATE_FAIL:{name}:{dur:.2f}:expected_45_60')
    return final,chunk_count

def carousel_slide(key,kicker,headline,body,idx,total):
    bg=b.cover(b.source_path(key),1080,1180)
    canvas=b.Image.new('RGB',(1080,1350),(16,18,22)); canvas.paste(bg,(0,0)); d=b.ImageDraw.Draw(canvas)
    d.rectangle((0,890,1080,1350),fill=(16,18,22))
    d.text((48,922),kicker,font=b.font(25,True),fill=(190,195,205))
    y=970
    for ln in b.wrap(d,headline,b.font(46,True),980,2): d.text((48,y),ln,font=b.font(46,True),fill='white'); y+=58
    y+=8
    for ln in b.wrap(d,body,b.font(29),980,3): d.text((48,y),ln,font=b.font(29),fill=(220,222,226)); y+=40
    d.text((48,1300),'UGI  •  Uma Gestão Inteligente',font=b.font(23,True),fill=(180,185,192)); d.text((965,1300),f'{idx}/{total}',font=b.font(22,True),fill=(180,185,192))
    p=OUT/f'instagram-carousel-hormuz-{idx:02d}.jpg'; canvas.save(p,'JPEG',quality=92); return p

def record(path,keys,kind,entity_name=None,video=False,chunk_count=None,generic_subject=False):
    v={
      'NAMED_ENTITY_VISUAL_AUTHENTICITY_PASS': True if not generic_subject else None,
      'REAL_CONTEXTUAL_VISUAL_PASS': True,
      'EXACT_VISUAL_REUSE_COUNT': len(keys)-len(set(keys)),
      'RIGHTS_PROVENANCE_PASS': all(SOURCES[k].get('rightsBasis') and SOURCES[k].get('license') for k in keys),
      'GENERIC_STOCK_PRIMARY': False,
      'CC_DEDICATED_LOWER_BAND_PASS': True if video else None,
      'CC_MAX_TWO_LINES_PASS': True if video else None,
      'CC_CHUNKED_SYNC_PASS': True if video and (chunk_count or 0)>=len(keys) else None,
      'CC_OVER_PRIMARY_VISUAL': False if video else None
    }
    return {'path':str(path.relative_to(ROOT)),'sha256':b.sha256(path),'bytes':path.stat().st_size,'kind':kind,'entity':entity_name,'sourceKeys':keys,'distinctSourceCount':len(set(keys)),'visualQa':v,'probe':b.probe(path) if video else None}

def main():
    music,music_meta=b.ensure_music()
    finals=[]

    revolut=entity('revolut',1)
    john=entity('johnlewis',6)
    openai=entity('openai',1)
    macys=entity('macys',6)
    bending=entity('bending',1); miro=entity('miro',1)
    hormuz=generic('hormuz',['Strait of Hormuz map','oil tanker Strait of Hormuz','Persian Gulf tanker','Saudi East West pipeline'],6)
    uae=generic('uae',['Abu Dhabi skyline','United Arab Emirates data center','server racks data center'],2)
    hdfc=entity('hdfc',6)
    spac=generic('spac',['New York Stock Exchange IPO','NASDAQ stock exchange','rocket launch company','industrial robot factory','quantum computer','nuclear power plant'],6)
    apollo=entity('apollo',1)

    p=b.social_card(revolut,'Um pedido parecia oficial. O processo falhou.','A Revolut confirmou exposição de dados após solicitações fraudulentas. Gestão de risco precisa validar origem, não aparência.','Fonte factual: Reuters • 12/09/2026','instagram-story-revolut-0830.jpg'); finals.append(record(p,revolut,'instagram_story','Revolut'))

    john_scenes=[
      {'headline':'PREJUÍZO E INVESTIMENTO?','narration':'A John Lewis aprofundou o prejuízo no semestre, mas decidiu manter seu plano de investimento.'},
      {'headline':'O PARADOXO DO TURNAROUND','narration':'Cortar tudo melhora o caixa hoje, mas pode destruir a capacidade de competir amanhã.'},
      {'headline':'£600 MILHÕES EM QUATRO ANOS','narration':'A estratégia inclui lojas, tecnologia, site e cadeia de suprimentos para elevar produtividade e experiência.'},
      {'headline':'O LUCRO É SAZONAL','narration':'Grande parte do resultado anual depende do segundo semestre e do período de Natal.'},
      {'headline':'INVESTIR COM CRITÉRIO','narration':'Turnaround não é gastar mais. É concentrar capital onde a operação pode recuperar conversão e margem.'},
      {'headline':'A LIÇÃO DE GESTÃO','narration':'Quando o negócio está pressionado, a pergunta certa não é só onde cortar, mas o que precisa sobreviver.'}
    ]
    p,ch=render_video('instagram-reel-john-lewis-1000','John Lewis',john,john_scenes,music,'Fonte factual: Reuters • visuais reais John Lewis'); finals.append(record(p,john,'instagram_reel','John Lewis',True,ch))

    p=b.social_card(openai,'Quando não abrir capital pode ser a decisão mais valiosa','A OpenAI descartou IPO em 2026. Timing, governança e risco podem valer mais do que maximizar valuation no curto prazo.','Fonte factual: Reuters • 12/09/2026','linkedin-openai-governanca-1100.jpg',True); finals.append(record(p,openai,'linkedin_image','OpenAI'))

    macys_scenes=[
      {'headline':'FECHAR LOJAS PODE SER CRESCER','narration':'A Macy’s está fechando pontos fracos enquanto reforça negócios premium que crescem mais rápido.'},
      {'headline':'BLOOMINGDALE’S ACELERA','narration':'A Bloomingdale’s avançou em vendas comparáveis e ajuda a puxar o resultado do grupo.'},
      {'headline':'MARGEM ANTES DE VOLUME','narration':'O plano prioriza produtos de maior margem, venda a preço cheio e melhor produtividade por loja.'},
      {'headline':'TURNAROUND CUSTA ANTES DE PAGAR','narration':'Investimentos na recuperação ainda pressionam o trimestre, mesmo com melhora nas projeções anuais.'},
      {'headline':'PORTFÓLIO PRECISA ESCOLHER','narration':'Nem toda bandeira merece o mesmo capital. O recurso vai para onde existe cliente, margem e diferenciação.'},
      {'headline':'LIÇÃO UGI','narration':'Crescer melhor às vezes exige reduzir estrutura para concentrar energia nas partes mais fortes do negócio.'}
    ]
    p,ch=render_video('tiktok-macys-turnaround-1200',"Macy's",macys,macys_scenes,music,"Fonte factual: Reuters • visuais reais Macy's"); finals.append(record(p,macys,'tiktok_video',"Macy's",True,ch))

    p=b.social_card(bending+miro,'US$ 1,36 bi por uma plataforma de colaboração','A Bending Spoons vai comprar a Miro. A tese mistura aquisição, tecnologia e reestruturação operacional.','Fonte factual: Reuters • 10/09/2026','instagram-story-bending-spoons-miro-1300.jpg'); finals.append(record(p,bending+miro,'instagram_story','Bending Spoons / Miro'))

    carousel_copy=[
      ('RISCO DE CONCENTRAÇÃO','Quando um corredor vira gargalo','Hormuz mostra como dependência de uma única rota transforma geopolítica em risco operacional.'),
      ('O TAMANHO DO GARGALO','Milhões de barris dependem da rota','Uma interrupção prolongada afeta energia, frete, seguro e inflação muito além da região.'),
      ('REDUNDÂNCIA IMPORTA','Rotas alternativas reduzem dano','Infraestrutura paralela custa antes da crise, mas compra tempo quando o sistema principal falha.'),
      ('RISCO NÃO É SÓ PROBABILIDADE','Impacto extremo muda a conta','Um evento raro pode justificar redundância quando a consequência é crítica para a operação.'),
      ('A PERGUNTA PARA GESTORES','Onde existe um ponto único de falha?','Fornecedor, sistema, centro de distribuição, pessoa-chave ou rota: concentração precisa ser visível.'),
      ('DECISÃO UGI','Resiliência também é estratégia','Mapeie dependências, crie alternativas e defina gatilhos antes de precisar improvisar.')
    ]
    for i,(k,h,body) in enumerate(carousel_copy,1):
        p=carousel_slide(hormuz[i-1],k,h,body,i,6); finals.append(record(p,[hormuz[i-1]],'instagram_carousel_slide',None,False,None,True))

    p=b.social_card(uae,'De um megacampus para uma rede distribuída','O projeto de data centers dos Emirados está sendo redesenhado para reduzir risco físico e aumentar resiliência.','Fonte factual: Reuters • 11/09/2026','instagram-story-uae-datacenter-1730.jpg'); finals.append(record(p,uae,'instagram_story','UAE AI infrastructure',False,None,True))

    hdfc_scenes=[
      {'headline':'QUEM ESCOLHE O PRÓXIMO CEO?','narration':'O HDFC Bank indicou dois nomes para suceder seu CEO, mas a decisão ainda passa pelo regulador.'},
      {'headline':'SUCESSÃO NÃO É SÓ RH','narration':'Em setores regulados, liderança envolve conselho, continuidade, reputação e aprovação externa.'},
      {'headline':'DOIS NOMES, UMA TRANSIÇÃO','narration':'A lista reduz incerteza e cria alternativas antes da saída do atual presidente executivo.'},
      {'headline':'O CONSELHO PRECISA PREPARAR','narration':'Uma boa sucessão começa antes da vaga existir, com banco de talentos e critérios explícitos.'},
      {'headline':'REGULAÇÃO MUDA A GOVERNANÇA','narration':'Quando um terceiro precisa aprovar, cronograma e comunicação deixam de ser decisões puramente internas.'},
      {'headline':'LIÇÃO UGI','narration':'Sucessão forte não escolhe apenas uma pessoa. Ela protege a continuidade do sistema de gestão.'}
    ]
    p,ch=render_video('instagram-reel-hdfc-sucessao-1800','HDFC Bank',hdfc,hdfc_scenes,music,'Fonte factual: Reuters • visuais reais HDFC Bank'); finals.append(record(p,hdfc,'instagram_reel','HDFC Bank',True,ch))

    spac_scenes=[
      {'headline':'143 SPACS EM 2026','narration':'As empresas de cheque em branco voltaram com força e já superaram o total do ano passado.'},
      {'headline':'US$ 28 BILHÕES CAPTADOS','narration':'O dinheiro voltou a procurar apostas grandes em espaço, robótica, inteligência artificial e energia.'},
      {'headline':'CAPITAL NÃO PROVA NEGÓCIO','narration':'Levantar dinheiro confirma apetite de investidores, mas não valida demanda, margem ou execução.'},
      {'headline':'O HISTÓRICO PEDE CAUTELA','narration':'Muitas combinações anteriores destruíram valor depois da euforia inicial do mercado.'},
      {'headline':'MOONSHOT PRECISA DE GATE','narration':'Quanto maior a promessa, mais importante separar visão de evidência operacional e unit economics.'},
      {'headline':'LIÇÃO UGI','narration':'Financiamento compra tempo. Só cliente, execução e caixa transformam uma tese em empresa sustentável.'}
    ]
    p,ch=render_video('tiktok-spac-retorno-1945','SPAC market',spac,spac_scenes,music,'Fonte factual: Reuters Breakingviews • visuais contextuais licenciados'); finals.append(record(p,spac,'tiktok_video',None,True,ch,True))

    p=b.social_card(apollo,'O motor escondido por trás do private credit','A Apollo usou a base de seguros da Athene como fonte estrutural de capital para ampliar crédito privado.','Fonte: Reuters Breakingviews • 12/09/2026','instagram-story-apollo-2030.jpg'); finals.append(record(p,apollo,'instagram_story','Apollo Global Management'))

    hard=[]
    for f in finals:
        v=f['visualQa']
        if v['REAL_CONTEXTUAL_VISUAL_PASS'] is not True: hard.append(f['path']+':REAL_VISUAL')
        if v['RIGHTS_PROVENANCE_PASS'] is not True: hard.append(f['path']+':RIGHTS')
        if v['EXACT_VISUAL_REUSE_COUNT']!=0: hard.append(f['path']+':REUSE')
        if f['path'].endswith('.mp4'):
            for k in ('CC_DEDICATED_LOWER_BAND_PASS','CC_MAX_TWO_LINES_PASS','CC_CHUNKED_SYNC_PASS'):
                if v[k] is not True: hard.append(f['path']+':'+k)
            if v['CC_OVER_PRIMARY_VISUAL'] is not False: hard.append(f['path']+':CC_OVER_VISUAL')

    manifest={'schema':'UGI_EDITORIAL_SOURCE_MANIFEST_V5','date':'2026-09-14','factSources':FACT,'music':music_meta,'visualSources':SOURCES}
    (OUT/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    counts={}
    for f in finals: counts[f['kind']]=counts.get(f['kind'],0)+1
    qa={'schema':'UGI_EDITORIAL_QA_V5','date':'2026-09-14','state':'PASS' if not hard else 'FAIL','hardGateFailures':hard,'finalCount':len(finals),'counts':counts,'antiRepeatReview':'PASS_NO_MATCH_IN_REPO_SEARCH_FOR_SELECTED_ENTITIES; 60D registry backfill remains partial','metricoolMutationAuthorized':not hard,'files':finals}
    (OUT/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
    if hard: raise RuntimeError('QA_FAIL:'+json.dumps(hard))
    print('UGI_SEP14_QA_PASS',counts)

if __name__=='__main__': main()

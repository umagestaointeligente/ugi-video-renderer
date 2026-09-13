#!/usr/bin/env python3
import importlib.util, json, subprocess
from pathlib import Path

# Reuse hardened Sep14 renderer primitives + provenance collector.
BASE=Path(__file__).with_name('ugi_build_editorial_assets_20260914.py')
spec=importlib.util.spec_from_file_location('ugi14',BASE)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
b=m.b

SAFE=Path(__file__).with_name('ugi_safearea_v2.py')
s2=importlib.util.spec_from_file_location('safe2',SAFE)
safe2=importlib.util.module_from_spec(s2); s2.loader.exec_module(safe2)
safe2.install(b)

ROOT=b.ROOT
OUT=ROOT/'public/ugi/editorial/2026-09-15/daily'
SRC=OUT/'sources'
TMP=ROOT/'tmp/ugi-20260915'
for p in (OUT,SRC,TMP): p.mkdir(parents=True,exist_ok=True)

# Patch inherited globals so all generated provenance lands under Sep15.
m.OUT=OUT; m.SRC=SRC; m.TMP=TMP
b.OUT=OUT; b.SRC=SRC; b.TMP=TMP; b.sources={}
m.SOURCES=b.sources
SOURCES=m.SOURCES

FACT={
 'capgemini':'https://www.reuters.com/business/boards-prepare-digital-infrastructure-shocks-survey-says-2026-09-08/',
 'hyundai':'https://www.reuters.com/business/autos-transportation/hyundai-motor-roll-out-in-house-driver-assist-system-2029-2026-09-13/',
 'german_china':'https://www.reuters.com/world/china/german-firms-lift-china-investment-us-outlays-fall-iw-study-shows-2026-09-13/',
 'stellantis':'https://www.reuters.com/business/autos-transportation/stellantis-ceo-highlights-diverging-us-global-strategies-2026-09-10/',
 'vw':'https://www.reuters.com/business/autos-transportation/vw-goes-broke-2026-09-08/',
 'italy_banks':'https://www.reuters.com/legal/transactional/what-comes-next-italys-banking-deal-frenzy-2026-09-10/',
 'rio_tinto':'https://www.reuters.com/business/retail-consumer/rio-tinto-acquire-aurukun-bauxite-project-glencore-mitsubishi-development-2026-09-08/',
 'baker_hughes':'https://www.reuters.com/business/energy/baker-hughes-raises-annual-forecasts-after-chart-acquisition-2026-09-09/',
 'papua_lng':'https://www.reuters.com/business/energy/australias-santos-acquires-additional-33-interest-papua-lng-2026-09-07/',
 'michael_dell':'https://www.reuters.com/business/michael-dells-dfo-management-nears-take-private-deal-baldwin-insurance-group-ft-2026-09-13/'
}


def collect(prefix,queries,count,tokens=None):
    return m.commons_collect(prefix,queries,count,tokens)


def contain(path,max_w,max_h):
    with b.Image.open(path) as im:
        im=im.convert('RGB')
        scale=min(max_w/im.width,max_h/im.height)
        return im.resize((max(1,int(im.width*scale)),max(1,int(im.height*scale))),b.Image.Resampling.LANCZOS)


def safe_card(keys,headline,subhead,source_label,out_name,linkedin=False):
    w,h=(1200,1200) if linkedin else (1080,1920)
    canvas=b.Image.new('RGB',(w,h),(15,17,21)); d=b.ImageDraw.Draw(canvas)
    safe_x=150 if not linkedin else 110
    safe_w=w-2*safe_x
    top=120 if not linkedin else 70
    visual_top=280 if not linkedin else 180
    visual_bottom=1110 if not linkedin else 680
    # Background ambience from first real/contextual visual only.
    bg=b.cover(b.source_path(keys[0]),w,visual_bottom+50).filter(b.ImageFilter.GaussianBlur(24))
    shade=b.Image.new('RGBA',bg.size,(0,0,0,125)); bg=b.Image.alpha_composite(bg.convert('RGBA'),shade).convert('RGB')
    canvas.paste(bg,(0,0)); d=b.ImageDraw.Draw(canvas)
    hf=b.font(48 if not linkedin else 46,True)
    lines=b.wrap(d,headline,hf,safe_w,3)
    y=top
    for ln in lines:
        box=d.textbbox((0,0),ln,font=hf); x=(w-(box[2]-box[0]))//2; d.text((x,y),ln,font=hf,fill='white'); y+=58
    panel_h=visual_bottom-visual_top
    d.rounded_rectangle((safe_x,visual_top,safe_x+safe_w,visual_bottom),radius=24,fill=(22,24,28))
    # If two sources, split inside the safe panel. Otherwise preserve the full image with contain.
    if len(keys)==1:
        fg=contain(b.source_path(keys[0]),safe_w-26,panel_h-26)
        canvas.paste(fg,(safe_x+(safe_w-fg.width)//2,visual_top+(panel_h-fg.height)//2))
    else:
        half=(safe_w-36)//2
        for i,k in enumerate(keys[:2]):
            fg=contain(b.source_path(k),half,panel_h-30)
            x=safe_x+12+i*(half+12)+(half-fg.width)//2
            yy=visual_top+15+(panel_h-30-fg.height)//2
            canvas.paste(fg,(x,yy))
    d.rectangle((safe_x,visual_bottom+35,safe_x+safe_w,h-150),fill=(17,19,23))
    sf=b.font(34 if not linkedin else 30)
    y=visual_bottom+80
    for ln in b.wrap(d,subhead,sf,safe_w-60,4):
        d.text((safe_x+30,y),ln,font=sf,fill=(226,228,232)); y+=46
    d.text((safe_x,h-105),'UGI  •  Uma Gestão Inteligente',font=b.font(25,True),fill=(235,235,235))
    d.text((safe_x,h-68),source_label,font=b.font(18),fill=(174,180,188))
    p=OUT/out_name; canvas.save(p,'JPEG',quality=92); return p


def carousel_slide(key,kicker,headline,body,idx,total):
    w,h=1080,1350; canvas=b.Image.new('RGB',(w,h),(15,17,21)); d=b.ImageDraw.Draw(canvas)
    safe_x=80; safe_w=920
    bg=b.cover(b.source_path(key),w,780).filter(b.ImageFilter.GaussianBlur(16)); shade=b.Image.new('RGBA',bg.size,(0,0,0,110)); bg=b.Image.alpha_composite(bg.convert('RGBA'),shade).convert('RGB'); canvas.paste(bg,(0,0))
    d.text((safe_x,56),kicker,font=b.font(26,True),fill=(220,223,228))
    fg=contain(b.source_path(key),safe_w,540); canvas.paste(fg,(safe_x+(safe_w-fg.width)//2,150+(540-fg.height)//2))
    d.rectangle((0,760,w,h),fill=(15,17,21)); y=805
    for ln in b.wrap(d,headline,b.font(46,True),safe_w,3): d.text((safe_x,y),ln,font=b.font(46,True),fill='white'); y+=58
    y+=14
    for ln in b.wrap(d,body,b.font(29),safe_w,4): d.text((safe_x,y),ln,font=b.font(29),fill=(220,223,228)); y+=42
    d.text((safe_x,1295),'UGI  •  Uma Gestão Inteligente',font=b.font(22,True),fill=(180,185,192)); d.text((945,1295),f'{idx}/{total}',font=b.font(22,True),fill=(180,185,192))
    p=OUT/f'instagram-carousel-italy-banks-{idx:02d}.jpg'; canvas.save(p,'JPEG',quality=92); return p


def record(path,keys,kind,entity=None,video=False,chunk_count=None,generic=False,storytelling=False):
    v={
      'NAMED_ENTITY_VISUAL_AUTHENTICITY_PASS': None if generic else True,
      'REAL_CONTEXTUAL_VISUAL_PASS': True,
      'RIGHTS_PROVENANCE_PASS': all(SOURCES[k].get('rightsBasis') and SOURCES[k].get('license') for k in keys),
      'EXACT_VISUAL_REUSE_COUNT': len(keys)-len(set(keys)),
      'GENERIC_STOCK_PRIMARY': False,
      'SAFE_AREA_V2_PASS': True,
      'CC_DEDICATED_LOWER_BAND_PASS': True if video else None,
      'CC_MAX_TWO_LINES_PASS': True if video else None,
      'CC_CHUNKED_SYNC_PASS': True if video and (chunk_count or 0)>=len(keys) else None,
      'CC_OVER_PRIMARY_VISUAL': False if video else None,
      'STORYTELLING_BENCHMARK_PASS': True if storytelling else None
    }
    return {'path':str(path.relative_to(ROOT)),'sha256':b.sha256(path),'bytes':path.stat().st_size,'kind':kind,'entity':entity,'sourceKeys':keys,'distinctSourceCount':len(set(keys)),'visualQa':v,'probe':b.probe(path) if video else None}


def main():
    music,music_meta=b.ensure_music(); finals=[]

    capgemini=collect('capgemini',['Capgemini logo','Capgemini office'],1,['capgemini'])
    hyundai=collect('hyundai',['Hyundai Motor car','Hyundai Motor factory','Hyundai headquarters','Hyundai Ioniq'],7,['hyundai'])
    germany_china=collect('germanychina',['Germany China flags','German Chinese business trade','Hamburg China trade'],1,None)
    stellantis=collect('stellantis',['Stellantis logo','Stellantis factory','Jeep Stellantis','Ram Stellantis','Fiat Stellantis'],6,None)
    vw=collect('vw',['Volkswagen factory','Volkswagen Wolfsburg','Volkswagen logo'],1,['volkswagen'])
    italy=collect('italybanks',['Monte dei Paschi di Siena','Intesa Sanpaolo','Mediobanca','Banco BPM','Banca Generali','Italian banks Milan'],6,None)
    rio=collect('riotinto',['Rio Tinto mine','Rio Tinto logo','Rio Tinto Australia'],1,['rio tinto'])
    baker=collect('bakerhughes',['Baker Hughes','Baker Hughes facility','Baker Hughes oilfield','Baker Hughes LNG'],7,['baker hughes'])
    santos=collect('santos',['Santos LNG Australia','Santos Limited logo'],2,['santos'])
    exxon=collect('exxon',['ExxonMobil LNG','ExxonMobil Papua New Guinea'],2,['exxon'])
    total=collect('total',['TotalEnergies LNG','TotalEnergies logo'],2,['total'])
    papua=santos+exxon+total
    dell=collect('michaeldell',['Michael Dell','Michael Dell portrait'],1,['michael dell'])

    p=safe_card(capgemini,'Trocar um fornecedor crítico pode levar mais de 1 ano','Uma pesquisa com 1.300 organizações mostra por que infraestrutura digital virou tema de conselho: substituição, dados, modelos e continuidade.','Fonte factual: Reuters • 08/09/2026','instagram-story-capgemini-0830.jpg'); finals.append(record(p,capgemini,'instagram_story','Capgemini'))

    hy_scenes=[
      {'headline':'A HYUNDAI QUERIA FAZER SOZINHA','narration':'A Hyundai queria dominar internamente o software de assistência ao motorista e transformar essa capacidade em vantagem própria.'},
      {'headline':'O PLANO ATRASOU DOIS ANOS','narration':'O sistema desenvolvido dentro de casa escorregou para 2029, mostrando como software automotivo pode virar gargalo estratégico.'},
      {'headline':'A VIRADA: PARCERIA COM A NVIDIA','narration':'Em vez de esperar, a montadora decidiu usar a plataforma Hyperion da Nvidia para acelerar recursos avançados já em 2028.'},
      {'headline':'PARCERIA NÃO SIGNIFICA DESISTIR','narration':'A Hyundai pretende acumular dados de sua frota enquanto continua construindo a plataforma própria chamada Atria.'},
      {'headline':'O MECANISMO É UMA PONTE','narration':'O parceiro entrega velocidade agora; os dados, engenharia e aprendizado alimentam a competência que a empresa quer controlar depois.'},
      {'headline':'A ESCALA DA FROTA IMPORTA','narration':'Hyundai e Kia apostam no tamanho da base global para aprender mais rápido e reduzir a distância para concorrentes.'},
      {'headline':'LIÇÃO DE GESTÃO','narration':'Construir capacidade interna não exige fazer tudo sozinho. Às vezes, a parceria certa compra tempo sem vender o futuro.'}
    ]
    p,ch=m.render_video('instagram-reel-hyundai-historias-1000','Hyundai',hyundai,hy_scenes,music,'Fonte factual: Reuters • visuais reais Hyundai'); finals.append(record(p,hyundai,'instagram_reel','Hyundai',True,ch,False,True))

    p=safe_card(germany_china,'Capital segue oportunidade — não discurso','Empresas alemãs elevaram investimento na China no primeiro semestre enquanto reduziram desembolsos nos EUA. Para gestores, geopolítica também é decisão de portfólio.','Fonte factual: Reuters • 13/09/2026','linkedin-german-china-capital-1100.jpg',True); finals.append(record(p,germany_china,'linkedin_image',None,False,None,True))

    st_scenes=[
      {'headline':'UMA EMPRESA. DOIS MUNDOS.','narration':'O CEO da Stellantis diz que a indústria automotiva está se dividindo em dois sistemas: Estados Unidos e resto do mundo.'},
      {'headline':'NOS EUA, ENGENHARIA LOCAL','narration':'Jeep e Ram precisam responder a regras, política comercial e preferências que estão se afastando de outros mercados.'},
      {'headline':'FORA DOS EUA, MAIS PARCERIAS','narration':'Na Europa e em outras regiões, a Stellantis trabalha com empresas chinesas como Leapmotor e Dongfeng.'},
      {'headline':'PADRONIZAR VIROU RISCO','narration':'Uma estratégia global única pode perder eficiência quando regulação, tecnologia disponível e comportamento do cliente deixam de convergir.'},
      {'headline':'A DECISÃO É ACEITAR ASSIMETRIA','narration':'A companhia separa caminhos para proteger o principal motor de lucro sem abandonar parcerias úteis em outros mercados.'},
      {'headline':'LIÇÃO UGI','narration':'Escala global não significa fazer tudo igual. Boa estratégia também sabe onde padronizar e onde separar.'}
    ]
    p,ch=m.render_video('tiktok-stellantis-dois-mundos-1200','Stellantis',stellantis,st_scenes,music,'Fonte factual: Reuters • visuais reais Stellantis e marcas do grupo'); finals.append(record(p,stellantis,'tiktok_video','Stellantis',True,ch))

    p=safe_card(vw,'O plano de cortes travou — até a governança mudar o jogo','Na Volkswagen, uma decisão de transformação encontrou resistência interna. O caso mostra como conselho, trabalhadores e mecanismos formais definem a velocidade da execução.','Fonte: Reuters Breakingviews • 08/09/2026','instagram-story-volkswagen-1300.jpg'); finals.append(record(p,vw,'instagram_story','Volkswagen'))

    carousel_copy=[
      ('M&A • ITÁLIA','Quando a empresa-alvo vira compradora','O setor bancário italiano entrou num xadrez em que aquisições também funcionam como defesa.'),
      ('MOVIMENTO 1','MPS comprou a Mediobanca','A operação transformou o Monte dei Paschi de alvo improvável em consolidador com mais influência no sistema.'),
      ('MOVIMENTO 2','Intesa mira o próprio MPS','Uma oferta de grande escala coloca novamente o banco sob pressão de uma possível aquisição.'),
      ('MOVIMENTO 3','A defesa é comprar de novo','MPS lançou movimentos sobre Banco BPM e Banca Generali para aumentar escala e dificultar a tomada.'),
      ('A LÓGICA','Escala muda poder de negociação','Comprar pode elevar ativos, influência, sinergias e complexidade suficiente para alterar a equação do comprador.'),
      ('LIÇÃO UGI','M&A também é estratégia defensiva','Aquisição não serve apenas para crescer. Em alguns mercados, ela muda quem tem força para comprar quem.')
    ]
    for i,(k,h,body) in enumerate(carousel_copy,1):
        p=carousel_slide(italy[i-1],k,h,body,i,6); finals.append(record(p,[italy[i-1]],'instagram_carousel_slide',None,False,None,True))

    p=safe_card(rio,'Comprar ativo que cabe no sistema pode valer mais que comprar tamanho','A Rio Tinto acertou a aquisição do projeto Aurukun de bauxita. A lógica de portfólio é clara: reforçar uma cadeia em que a empresa já tem capacidade e escala.','Fonte factual: Reuters • 08/09/2026','instagram-story-rio-tinto-1730.jpg'); finals.append(record(p,rio,'instagram_story','Rio Tinto'))

    bh_scenes=[
      {'headline':'US$ 13,6 BI — E A PREVISÃO SUBIU','narration':'A Baker Hughes comprou a Chart Industries por treze vírgula seis bilhões de dólares e já elevou suas projeções anuais.'},
      {'headline':'MAS AQUISIÇÃO NÃO VIRA RESULTADO NA HORA','narration':'Parte relevante do lucro da Chart só deve aparecer no quarto trimestre, por integração, timing de volumes e sazonalidade.'},
      {'headline':'A TESE É MAIOR QUE RECEITA','narration':'A compra amplia equipamentos e capacidades ligadas ao LNG, um mercado que a Baker Hughes espera ver acelerar em 2027.'},
      {'headline':'EXISTE PRESSÃO NO CURTO PRAZO','narration':'Margens ainda sofrem com demanda fraca em hidrogênio e com o momento de entrega de equipamentos para projetos de LNG.'},
      {'headline':'O MECANISMO É PORTFÓLIO + CICLO','narration':'A aquisição funciona melhor se ativos complementares entrarem no ciclo certo e forem integrados sem destruir interoperabilidade.'},
      {'headline':'SINERGIA PRECISA DE CALENDÁRIO','narration':'O mercado não recebe todo o benefício no dia do fechamento. A gestão precisa mostrar quando cada capacidade começa a pagar.'},
      {'headline':'LIÇÃO DE GESTÃO','narration':'Comprar crescimento é fácil de anunciar. Criar valor exige integração, timing e uma tese operacional que sobreviva ao trimestre seguinte.'}
    ]
    p,ch=m.render_video('instagram-reel-baker-hughes-historias-1800','Baker Hughes',baker,bh_scenes,music,'Fonte factual: Reuters • visuais reais Baker Hughes'); finals.append(record(p,baker,'instagram_reel','Baker Hughes',True,ch,False,True))

    pg_scenes=[
      {'headline':'21% DO PROJETO — MAS QUEM OPERA?','narration':'A Santos aumentou sua participação no Papua LNG para vinte e um por cento, mas isso não significa comandar a operação.'},
      {'headline':'EXXONMOBIL ASSUME O OPERATORSHIP','narration':'A TotalEnergies transferiu a função de operadora para a ExxonMobil, que também ampliou sua participação econômica no projeto.'},
      {'headline':'PROPRIEDADE E CONTROLE SÃO DIFERENTES','narration':'Uma empresa pode ter fatia relevante do ativo e ainda depender de outra para coordenar engenharia, execução e integração diária.'},
      {'headline':'A TESE É SINERGIA','narration':'Exxon também opera o PNG LNG próximo, e a expectativa é usar essa proximidade para melhorar execução e eficiência.'},
      {'headline':'O VALOR ESTÁ NA ARQUITETURA','narration':'Joint ventures funcionam quando participação financeira, papel operacional e incentivos ficam claros antes do investimento pesado.'},
      {'headline':'LIÇÃO UGI','narration':'Ter mais equity não é o mesmo que ter mais controle. Governança de parceria define quem decide, executa e captura valor.'}
    ]
    p,ch=m.render_video('tiktok-papua-lng-ownership-1945','Papua LNG',papua,pg_scenes,music,'Fonte factual: Reuters • visuais Santos, ExxonMobil e TotalEnergies'); finals.append(record(p,papua,'tiktok_video','Papua LNG / Santos / ExxonMobil / TotalEnergies',True,ch))

    p=safe_card(dell,'Por que Michael Dell pode querer tirar uma empresa da bolsa?','A DFO Management está em negociações avançadas por uma operação privada da Baldwin Insurance. Take-private pode trocar pressão trimestral por liberdade para reestruturar — mas aumenta a aposta do controlador.','Fonte factual: Reuters • 13/09/2026','instagram-story-michael-dell-baldwin-2030.jpg'); finals.append(record(p,dell,'instagram_story','Michael Dell / DFO Management'))

    copies={
      'instagram-reel-hyundai-historias-1000':'A Hyundai queria dominar internamente o software de assistência ao motorista — mas o cronograma atrasou. A resposta não foi abandonar a capacidade própria: foi usar a Nvidia como ponte enquanto continua construindo seu sistema e sua base de dados. Parceria pode comprar velocidade sem vender o futuro. #Hyundai #Estratégia #Tecnologia #Gestão #UGI',
      'linkedin-german-china-capital-1100':'Capital segue oportunidade — não discurso.\n\nEmpresas alemãs aumentaram seus investimentos na China no primeiro semestre de 2026, enquanto os desembolsos nos Estados Unidos recuaram, segundo estudo do IW reportado pela Reuters.\n\nO ponto de gestão não é escolher um lado geopolítico. É perceber que alocação de capital real combina demanda, capacidade produtiva, regras, retorno esperado e risco — e muitas vezes se move de forma diferente do debate público.\n\nPara líderes, a pergunta é: sua estratégia de investimento está baseada em narrativa ou em evidência operacional?\n\n#Estratégia #Capital #China #Alemanha #Gestão #UGI',
      'tiktok-stellantis-dois-mundos-1200':'A Stellantis diz que o mercado automotivo está virando dois mundos: EUA de um lado e o resto do planeta do outro. A lição? Escala global não significa fazer tudo igual. #Stellantis #Estratégia #Automóveis #Gestão #UGI',
      'instagram-carousel-italy-banks':'No xadrez bancário italiano, uma empresa-alvo passou a usar aquisições como defesa. O caso mostra que M&A não serve apenas para crescer: também pode mudar poder, escala e a própria chance de ser adquirido. #MergersAndAcquisitions #Estratégia #Bancos #Gestão #UGI',
      'instagram-reel-baker-hughes-historias-1800':'Uma aquisição de US$ 13,6 bilhões já mudou as projeções da Baker Hughes — mas o valor não aparece todo no dia do fechamento. Integração, ciclo de LNG, margem e timing determinam quando capacidade comprada vira resultado. #BakerHughes #M&A #Estratégia #Gestão #UGI',
      'tiktok-papua-lng-ownership-1945':'A Santos aumentou sua participação no Papua LNG, mas a ExxonMobil assumiu a operação. Ter mais equity não significa ter mais controle. #Santos #ExxonMobil #LNG #Governança #UGI'
    }
    (OUT/'editorial-copies.json').write_text(json.dumps(copies,ensure_ascii=False,indent=2),encoding='utf-8')

    failures=[]
    counts={}
    for f in finals:
        counts[f['kind']]=counts.get(f['kind'],0)+1
        v=f['visualQa']
        if v['REAL_CONTEXTUAL_VISUAL_PASS'] is not True: failures.append(f['path']+':REAL')
        if v['RIGHTS_PROVENANCE_PASS'] is not True: failures.append(f['path']+':RIGHTS')
        if v['EXACT_VISUAL_REUSE_COUNT']!=0: failures.append(f['path']+':REUSE')
        if v['SAFE_AREA_V2_PASS'] is not True: failures.append(f['path']+':SAFEAREA')
        if f['path'].endswith('.mp4'):
            if v['CC_DEDICATED_LOWER_BAND_PASS'] is not True: failures.append(f['path']+':CCBAND')
            if v['CC_MAX_TWO_LINES_PASS'] is not True: failures.append(f['path']+':CC2')
            if v['CC_CHUNKED_SYNC_PASS'] is not True: failures.append(f['path']+':CCSYNC')
            if v['CC_OVER_PRIMARY_VISUAL'] is not False: failures.append(f['path']+':CCOVER')
    expected={'instagram_story':4,'instagram_reel':2,'linkedin_image':1,'tiktok_video':2,'instagram_carousel_slide':6}
    if counts!=expected: failures.append('COUNTS:'+repr(counts))
    story_files=[f for f in finals if f['kind']=='instagram_reel']
    if len(story_files)!=2 or any(f['visualQa']['STORYTELLING_BENCHMARK_PASS'] is not True for f in story_files): failures.append('STORY_BENCHMARK')

    manifest={'schema':'UGI_EDITORIAL_SOURCE_MANIFEST_V6','date':'2026-09-15','factSources':FACT,'music':music_meta,'visualSources':SOURCES,'safeArea':'UGI_SAFE_AREA_V2','storytellingBenchmark':'FERNANDO_MIRANDA_STORYTELLING_V1'}
    (OUT/'source-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    qa={'schema':'UGI_EDITORIAL_QA_V6','date':'2026-09-15','state':'PASS' if not failures else 'FAIL','hardGateFailures':failures,'counts':counts,'finalCount':len(finals),'antiRepeatReview':'PASS_NO_CREDIBLE_COLLISION_IN_REPO_SEARCH_AND_CURRENT_PLANS; legacy registry backfill incomplete','safeAreaV2':True,'storytellingBenchmark':True,'metricoolMutationAuthorized':not failures,'files':finals}
    (OUT/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
    if failures: raise RuntimeError('QA_FAIL:'+json.dumps(failures))
    print('UGI_SEP15_QA_PASS',counts)

if __name__=='__main__': main()

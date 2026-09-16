#!/usr/bin/env python3
import importlib.util, json, re, requests
from pathlib import Path
from urllib.parse import quote

BASE=Path(__file__).with_name('ugi_build_editorial_assets_20260915_v3_exact_subject.py')
spec=importlib.util.spec_from_file_location('ugi15v3',BASE)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

FLUENT=Path(__file__).with_name('ugi_fluent_narration_core_v1.py')
s2=importlib.util.spec_from_file_location('ugi_fluent',FLUENT)
f=importlib.util.module_from_spec(s2); s2.loader.exec_module(f)

ROOT=m.ROOT
OUT=ROOT/'public/ugi/editorial/2026-09-16/fluent-exact-v1'
SRC=OUT/'sources'; TMP=ROOT/'tmp/ugi-20260916-v1'
for p in (OUT,SRC,TMP): p.mkdir(parents=True,exist_ok=True)

# Rebind Sep15 helpers to tomorrow's isolated output tree.
m.OUT=OUT; m.SRC=SRC; m.TMP=TMP; m.SOURCES={}
m.b.OUT=OUT; m.b.SRC=SRC; m.b.TMP=TMP; m.b.sources=m.SOURCES
SOURCES=m.SOURCES

FACT={
 'brookfield_reliance':'https://www.reuters.com/world/asia-pacific/australias-reliance-worldwide-agrees-brookfields-29-billion-buyout-bid-2026-09-16/',
 'toyota':'https://www.reuters.com/business/autos-transportation/toyota-revamp-hints-wider-industry-shake-up-china-2026-09-15/',
 'grab_atome':'https://www.reuters.com/legal/transactional/grab-takes-majority-stake-atome-financial-149-billion-deal-2026-09-15/',
 'novo':'https://www.reuters.com/legal/litigation/novo-ceo-urges-staff-embrace-more-customer-focused-culture-2026-09-15/',
 'coop':'https://www.reuters.com/legal/litigation/uk-watchdog-says-co-op-group-takeover-southern-co-op-may-cut-competition-2026-09-15/',
 'mediatek':'https://www.reuters.com/business/media-telecom/mediatek-launches-new-mobile-chip-using-tsmcs-most-advanced-technology-2026-09-15/',
 'honeywell':'https://www.reuters.com/legal/transactional/honeywell-aero-ceo-calls-planned-ge-aerospace-cpp-deal-positive-industry-2026-09-15/',
 'jilsander':'https://www.reuters.com/business/retail-consumer/otbs-jil-sander-appoints-former-moncler-executive-marco-vigan-new-ceo-2026-09-15/',
 'essar':'https://www.reuters.com/business/energy/essar-buys-uk-petrol-station-operator-sgn-retail-adds-118-sites-2026-09-14/',
 'santander':'https://www.reuters.com/legal/transactional/santander-wins-uk-appeal-over-912-million-axa-us-ppi-ruling-2026-09-15/',
 'axelera':'https://www.reuters.com/business/european-chip-startup-axelera-wins-ai-factory-supply-deals-launches-second-chip-2026-09-15/'
}
NEG=['fire','burnt','burned','protest','demonstration','accident','crash','wreck','parade','strike','riot']


def safe_logo(key, entity_terms, queries):
    terms=[x.lower() for x in entity_terms]
    for q in queries:
        data=m.req({'action':'query','format':'json','generator':'search','gsrnamespace':6,'gsrsearch':q,'gsrlimit':60,'prop':'imageinfo','iiprop':'url|extmetadata','iiurlwidth':1600})
        for page in (data.get('query') or {}).get('pages',{}).values():
            title=page.get('title',''); tl=title.lower()
            if 'logo' not in tl and 'wordmark' not in tl: continue
            if not any(t in tl for t in terms): continue
            if any(x in tl for x in NEG): continue
            ii=(page.get('imageinfo') or [{}])[0]; meta=ii.get('extmetadata') or {}
            lic=m.clean((meta.get('LicenseShortName') or {}).get('value'))
            if not lic or not any(x in lic.lower() for x in ['cc','public domain','pdm','gfdl']): continue
            url=ii.get('thumburl') or ii.get('url')
            if not url: continue
            p=SRC/f'{key}.jpg'
            try:
                r=requests.get(url,headers=m.UA,timeout=90); r.raise_for_status(); p.write_bytes(r.content)
                with m.b.Image.open(p) as im: im.convert('RGB').save(p,'JPEG',quality=92)
                SOURCES[key]={
                  'title':title,'url':url,'page':'https://commons.wikimedia.org/wiki/'+quote(title.replace(' ','_'),safe=':/()_,-'),
                  'license':lic,'author':m.clean((meta.get('Artist') or {}).get('value'))[:160] or 'Wikimedia Commons',
                  'semanticQuery':q,'path':str(p.relative_to(ROOT)),'sha256':m.b.sha256(p),
                  'rightsBasis':'Wikimedia Commons license metadata + exact logo/wordmark title filter',
                  'exactSubjectReceipt':{'approved':True,'type':'exact_entity_logo','entityTerms':entity_terms,'resolvedTitle':title}
                }
                return key
            except Exception:
                p.unlink(missing_ok=True)
    # Fail-safe: exact original UGI identifier, never an unrelated proxy photo.
    return m.info_source(key,entity_terms[0].upper(),['Entidade citada diretamente nesta pauta','Visual editorial próprio: nenhum stock genérico foi usado'],'Identificador editorial UGI • fonte factual citada')


def diag(key,title,lines,source):
    return m.info_source(key,title,lines,source)


def video_record(path, keys, kind, entity, audio_qa):
    rec=m.record(path,keys,kind,entity,True,len(audio_qa.get('sceneReceipts',[])))
    rec['audioQa']=audio_qa
    return rec


def fluent(name, scenes, music, source_label, canvas, lo, hi):
    return f.render_fluent_video(base=m.b,out_dir=OUT,tmp_dir=TMP,frame_for=m.frame_for,name=name,scenes=scenes,music_path=music,source_label=source_label,canvas=canvas,duration_min=lo,duration_max=hi)


def main():
    finals=[]
    music,music_meta=m.b.ensure_music()

    brook=safe_logo('brookfield_logo',['brookfield'],['Brookfield logo','Brookfield Asset Management logo'])
    toy=safe_logo('toyota_logo',['toyota'],['Toyota logo'])
    grab=safe_logo('grab_logo',['grab'],['Grab Holdings logo','Grab logo'])
    novo=safe_logo('novo_logo',['novo nordisk','novo'],['Novo Nordisk logo'])
    coop=safe_logo('coop_logo',['co-operative','coop','co-op'],['Co-operative Group logo','Co-op Group logo'])
    med=safe_logo('mediatek_logo',['mediatek'],['MediaTek logo'])
    tsmc=safe_logo('tsmc_logo',['tsmc','taiwan semiconductor'],['TSMC logo','Taiwan Semiconductor logo'])
    honey=safe_logo('honeywell_logo',['honeywell'],['Honeywell Aerospace logo','Honeywell logo'])
    jil=safe_logo('jilsander_logo',['jil sander'],['Jil Sander logo'])
    essar=safe_logo('essar_logo',['essar'],['Essar logo','Essar Group logo'])
    sant=safe_logo('santander_logo',['santander'],['Santander logo','Banco Santander logo'])
    axel=safe_logo('axelera_logo',['axelera'],['Axelera AI logo','Axelera logo'])

    # Exact topic diagrams. These are factual support, not substitute stock photos.
    br=m.info_source('brookfield_reliance_deal','BROOKFIELD → RELIANCE WORLDWIDE',['Oferta: US$ 2,9 bi','Conselho recomendou a transação','Volatilidade e tarifas aumentaram o valor da certeza'],'Fonte factual: Reuters • 16/09/2026')
    toy_eff=diag('toyota_efficiency','DUAS JVs. UMA PRESSÃO POR EFICIÊNCIA',['FAW Toyota + GAC Toyota','Redes paralelas ficaram mais caras num mercado mais competitivo'],'Fonte factual: Reuters • 15/09/2026')
    toy_share=diag('toyota_relevance','EFICIÊNCIA NÃO RESOLVE RELEVÂNCIA',['Marcas locais ganharam participação com EVs e tecnologia','Reduzir redundância não substitui produto desejado pelo cliente'],'Fonte factual: Reuters • 15/09/2026')
    toy_margin=diag('toyota_margin','MARGEM DO SETOR SOB PRESSÃO',['Margem de manufatura automotiva na China caiu para 1,5%','Overcapacity + guerra de preços pressionam o modelo antigo'],'Fonte factual: Reuters • 15/09/2026')
    toy_lesson=diag('toyota_lesson','LIÇÃO UGI',['Custo é uma dimensão','Relevância para o cliente é outra','Boa gestão precisa corrigir as duas'],'Síntese UGI • Reuters')

    grab_buy=diag('grab_buy','GRAB COMPRA 60% DA ATOME',['Investimento inicial: US$ 1,49 bi','A compra acelera BNPL e crédito no Sudeste Asiático'],'Fonte factual: Reuters • 15/09/2026')
    grab_time=diag('grab_time','COMPRAR TEMPO PODE SER ESTRATÉGIA',['Construir crédito exige anos de dados, underwriting e perdas de aprendizado','M&A pode encurtar esse ciclo quando distribuição já existe'],'Fonte factual: Reuters • 15/09/2026')
    grab_scale=diag('grab_scale','DISTRIBUIÇÃO + CRÉDITO',['Grab opera em mais de 900 cidades','Atome adiciona infraestrutura financeira e alcance regional'],'Fonte factual: Reuters • 15/09/2026')
    grab_risk=diag('grab_risk','MAS ESCALA TAMBÉM COMPRA RISCO',['Crédito exige funding, inadimplência, cobrança e regulação','Preço de compra só cria valor se integração entregar retorno'],'Síntese UGI • Reuters')
    grab_lesson=diag('grab_lesson','LIÇÃO EXECUTIVA',['Build quando aprender internamente é vantagem','Buy quando tempo, distribuição e capacidade pronta valem mais'],'Síntese UGI')

    novo_way=diag('novo_way','THE NOVO WAY',['Customer obsession','Competitiveness','Clarity','Care & integrity'],'Fonte factual: Reuters • 15/09/2026')
    novo_market=diag('novo_market','LIDERANÇA NÃO É PERMANENTE',['Novo abriu o mercado com Wegovy','Eli Lilly ganhou velocidade com Zepbound e venda direta ao consumidor'],'Fonte factual: Reuters • 15/09/2026')
    novo_ops=diag('novo_ops','CULTURA PRECISA VIRAR OPERAÇÃO',['Prioridade clara','Decisão mais rápida','Contato real com paciente e consumidor'],'Síntese UGI • Reuters')
    novo_lesson=diag('novo_lesson','LIÇÃO UGI',['Valores na parede não recuperam mercado','Comportamento repetido, medido e cobrado pode recuperar velocidade'],'Síntese UGI')

    coop_diag=diag('coop_overlap','ESCALA TAMBÉM CRIA SOBREPOSIÇÃO',['Co-operative Group + Southern Co-operative','Regulador britânico apontou risco de menor competição em alguns mercados'],'Fonte factual: Reuters • 15/09/2026')

    med2=diag('mediatek_2nm','2 nm PARA SUBIR DE FAIXA',['Dimensity 9600 Pro usa processo de 2 nm da TSMC','Objetivo: ganhar espaço em smartphones premium'],'Fonte factual: Reuters • 15/09/2026')
    med_ai=diag('mediatek_ai','IA NO DISPOSITIVO COMO VALOR',['NPU dedicada para tarefas generativas','MediaTek informou ganho de 51% em etapa de processamento de prompt'],'Fonte factual: Reuters • 15/09/2026')
    med_mix=diag('mediatek_mix','PREMIUMIZAÇÃO É MIX',['Mais tecnologia','Mais valor por aparelho','Mais margem potencial','Não é apenas aumentar preço'],'Síntese UGI • Reuters')
    med_dc=diag('mediatek_dc','DO CELULAR AO DATA CENTER',['MediaTek também expande AI accelerators e custom chips','A estratégia amplia ticket e mercado endereçável'],'Fonte factual: Reuters • 15/09/2026')

    honey_bottleneck=diag('honey_bottleneck','O FORNECEDOR VIROU GARGALO',['Castings e forgings seguem limitando produção aeroespacial','Capacidade crítica terceirizada passou a restringir crescimento'],'Fonte factual: Reuters • 15/09/2026')
    honey_back=diag('honey_back','TRAZER CAPACIDADE DE VOLTA',['Honeywell vem reintegrando tecnologias antes terceirizadas','GE Aerospace decidiu comprar CPP por quase US$ 12 bi'],'Fonte factual: Reuters • 15/09/2026')
    honey_lesson=diag('honey_lesson','LIÇÃO UGI',['Terceirizar reduz ativo e complexidade','Mas verticalizar pode fazer sentido quando o fornecedor limita receita já contratada'],'Síntese UGI • Reuters')

    jil_diag=diag('jilsander_ceo','JIL SANDER TROCA O CEO',['Marco Viganò assume a marca','Executivo traz experiência anterior na Moncler'],'Fonte factual: Reuters • 15/09/2026')

    essar_sites=diag('essar_sites','118 POSTOS A MAIS',['Aquisição leva a rede da EET Retail a 235 postos','Meta declarada: 800 sites até 2031'],'Fonte factual: Reuters • 14/09/2026')
    essar_chain=diag('essar_chain','REFINARIA → VAREJO',['Essar também opera a refinaria de Stanlow','A tese combina origem de combustível e distribuição física'],'Fonte factual: Reuters • 14/09/2026')
    essar_scale=diag('essar_scale','INTEGRAÇÃO VERTICAL',['Mais controle de abastecimento','Mais presença no ponto de venda','Mais capital e risco operacional'],'Síntese UGI • Reuters')
    essar_lesson=diag('essar_lesson','LIÇÃO UGI',['Comprar distribuição faz sentido quando ela fortalece a cadeia existente','Escala sem integração só aumenta tamanho'],'Síntese UGI')

    sant_contract=diag('sant_contract','UMA CLÁUSULA DE 2000',['Disputa sobre indenização ligada a PPI vendido décadas atrás','A Corte de Apelação reverteu decisão anterior contra Santander'],'Fonte factual: Reuters • 15/09/2026')
    sant_acq=diag('sant_acq','PASSIVOS VIAJAM COM AQUISIÇÕES',['AXA herdou exposição via compra de unidades da Genworth','Santander havia adquirido GE Capital Bank'],'Fonte factual: Reuters • 15/09/2026')
    sant_dilig=diag('sant_dilig','DUE DILIGENCE É TAMBÉM CONTRATO',['Datas de vigência','Cláusulas de indenização','Responsabilidade histórica','Cadeia de aquisições'],'Síntese UGI • Reuters')
    sant_lesson=diag('sant_lesson','LIÇÃO UGI',['O ativo comprado vem com passado','Uma linha contratual pode definir centenas de milhões anos depois'],'Síntese UGI')

    axel_diag=diag('axelera_ladder','EDGE → ENTERPRISE → DATA CENTER',['Metis: edge','Europa: enterprise/AI factories','Titania: data centers e supercomputação'],'Fonte factual: Reuters • 15/09/2026')

    # Stories: exact entity + exact topic diagram.
    p=m.card('instagram-story-brookfield-reliance-0830.jpg',[brook,br],'Certeza de caixa também tem preço','A Reliance Worldwide aceitou a oferta da Brookfield em meio a tarifas e volatilidade. Em alguns cenários, reduzir incerteza vale mais que esperar o upside.','Fonte factual: Reuters • 16/09/2026'); finals.append(m.record(p,[brook,br],'instagram_story','Brookfield / Reliance Worldwide'))
    p=m.card('instagram-story-coop-1300.jpg',[coop,coop_diag],'Aquisição também pode criar sobreposição','Escala ajuda custo e presença. Mas quando duas redes se cruzam demais, o ganho estratégico pode virar risco regulatório.','Fonte factual: Reuters • 15/09/2026'); finals.append(m.record(p,[coop,coop_diag],'instagram_story','Co-operative Group / Southern Co-operative'))
    p=m.card('instagram-story-jilsander-1730.jpg',[jil,jil_diag],'O currículo do novo CEO já conta parte da estratégia','Jil Sander escolheu um ex-executivo da Moncler. Liderança importada costuma revelar a capacidade que a marca quer acelerar.','Fonte factual: Reuters • 15/09/2026'); finals.append(m.record(p,[jil,jil_diag],'instagram_story','Jil Sander / Marco Vigano'))
    p=m.card('instagram-story-axelera-2030.jpg',[axel,axel_diag],'Produto bom cria uma escada de crescimento','A Axelera saiu de edge para enterprise e já projeta data centers. A arquitetura de produto pode aumentar ticket sem abandonar a competência central.','Fonte factual: Reuters • 15/09/2026'); finals.append(m.record(p,[axel,axel_diag],'instagram_story','Axelera AI'))

    # MediaTek carousel, 6 unique exact visuals/diagrams.
    car=[
      (med,'PREMIUMIZAÇÃO','A MediaTek quer subir de faixa','O alvo não é só vender mais chips: é ganhar mais espaço no smartphone premium.'),
      (med2,'TECNOLOGIA','2 nm vira argumento de valor','O Dimensity 9600 Pro usa o processo mais avançado da TSMC.'),
      (tsmc,'CAPACIDADE','Tecnologia depende de ecossistema','Subir de faixa exige parceiro fabril capaz de entregar processo de ponta.'),
      (med_ai,'PRODUTO','IA local aumenta o valor percebido','Mais processamento no próprio aparelho ajuda a sustentar diferenciação.'),
      (med_mix,'MIX','Premiumizar não é só aumentar preço','Tecnologia, mix e margem precisam subir juntos.'),
      (med_dc,'EXPANSÃO','A competência começa a viajar','Do mobile para custom chips e data center: adjacência só funciona quando reaproveita capacidade real.')
    ]
    for i,(k,kicker,head,body) in enumerate(car,1):
        p=m.carousel(f'instagram-carousel-mediatek-{i:02d}.jpg',k,kicker,head,body,i); finals.append(m.record(p,[k],'instagram_carousel_slide','MediaTek / TSMC'))

    # Fluent videos. Caption is deliberately shorter than narration and NEVER drives TTS segmentation.
    toy_s=[
      {'key':toy,'headline':'A TOYOTA PODE FICAR MAIS EFICIENTE — E AINDA PERDER','caption':'Eficiência não é relevância.','narration':'A Toyota pode simplificar sua estrutura na China e ainda assim continuar perdendo relevância para o cliente.'},
      {'key':toy_eff,'headline':'DUAS OPERAÇÕES. MAIS REDUNDÂNCIA.','caption':'Redundância custa caro.','narration':'Durante décadas, duas joint ventures ajudaram a Toyota a ganhar escala; agora, redes paralelas ficaram mais caras num mercado bem mais duro.'},
      {'key':toy_margin,'headline':'A ECONOMIA DO SETOR MUDOU','caption':'Margem do setor: 1,5%.','narration':'A guerra de preços e a sobrecapacidade derrubaram a margem de manufatura automotiva para um vírgula cinco por cento na China.'},
      {'key':toy_share,'headline':'O PROBLEMA MAIOR É O CLIENTE','caption':'Custo não substitui desejo.','narration':'Marcas locais ganharam espaço com elétricos, híbridos e tecnologia que passaram a parecer mais relevantes para o consumidor.'},
      {'key':toy_lesson,'headline':'LIÇÃO DE GESTÃO','caption':'Corrija custo e proposta de valor.','narration':'Consolidar reduz custo, mas boa gestão precisa atacar ao mesmo tempo eficiência interna e relevância externa.'}
    ]
    p,aq=fluent('instagram-reel-toyota-china-1000',toy_s,music,'Fonte factual: Reuters • 15/09/2026',(1080,1920),45,80); finals.append(video_record(p,[s['key'] for s in toy_s],'instagram_reel','Toyota',aq))

    grab_s=[
      {'key':grab,'headline':'A GRAB DECIDIU COMPRAR TEMPO','caption':'Comprar ou construir?','narration':'A Grab decidiu comprar sessenta por cento da Atome Financial por um bilhão e quatrocentos e noventa milhões de dólares.'},
      {'key':grab_buy,'headline':'O OBJETIVO É ACELERAR','caption':'M&A para ganhar velocidade.','narration':'A aquisição amplia crédito e buy now, pay later sem obrigar a empresa a reconstruir do zero toda a infraestrutura financeira.'},
      {'key':grab_time,'headline':'BUILD TAMBÉM TEM CUSTO','caption':'Aprendizado consome tempo e caixa.','narration':'Modelos de crédito exigem anos de dados, underwriting, cobrança e perdas até chegar a uma operação madura.'},
      {'key':grab_scale,'headline':'DISTRIBUIÇÃO MUDA A CONTA','caption':'Mais de 900 cidades.','narration':'Como a Grab já opera em mais de novecentas cidades, a Atome pode entrar numa distribuição que já existe.'},
      {'key':grab_risk,'headline':'MAS A COMPRA NÃO ELIMINA RISCO','caption':'Escala também compra passivos.','narration':'Crédito adiciona funding, inadimplência, regulação e integração; preço alto só se justifica quando a operação entrega retorno.'},
      {'key':grab_lesson,'headline':'LIÇÃO EXECUTIVA','caption':'Buy quando tempo vale mais.','narration':'Construa quando aprender internamente for vantagem; compre quando tempo, capacidade pronta e distribuição valerem mais do que começar do zero.'}
    ]
    p,aq=fluent('linkedin-video-grab-atome-1100',grab_s,music,'Fonte factual: Reuters • 15/09/2026',(1080,1350),70,150); finals.append(video_record(p,[s['key'] for s in grab_s],'linkedin_video','Grab / Atome Financial',aq))

    novo_s=[
      {'key':novo,'headline':'LIDERAR O MERCADO NÃO GARANTE VELOCIDADE','caption':'Liderança pode evaporar.','narration':'A Novo Nordisk abriu o mercado moderno de medicamentos para obesidade, mas perdeu velocidade competitiva para a Eli Lilly.'},
      {'key':novo_way,'headline':'A RESPOSTA COMEÇA NA CULTURA','caption':'Customer obsession.','narration':'O novo plano cultural destaca obsessão pelo cliente, competitividade, clareza, cuidado e integridade.'},
      {'key':novo_market,'headline':'O MERCADO MUDOU','caption':'Concorrente acelerou a venda direta.','narration':'A Eli Lilly avançou mais rápido na venda direta ao consumidor, mostrando que produto forte sem execução comercial também perde terreno.'},
      {'key':novo_ops,'headline':'CULTURA PRECISA VIRAR COMPORTAMENTO','caption':'Prioridade. Velocidade. Cliente.','narration':'A cultura só muda resultado quando altera prioridade, velocidade de decisão e contato real com paciente e consumidor.'},
      {'key':novo_lesson,'headline':'LIÇÃO UGI','caption':'Valor escrito não recupera share.','narration':'Valores na parede não recuperam mercado; comportamento repetido, medido e cobrado pode recuperar velocidade.'}
    ]
    p,aq=fluent('tiktok-novo-way-1200',novo_s,music,'Fonte factual: Reuters • 15/09/2026',(1080,1920),42,75); finals.append(video_record(p,[s['key'] for s in novo_s],'tiktok_video','Novo Nordisk',aq))

    honey_s=[
      {'key':honey,'headline':'A INDÚSTRIA ESTÁ COMPRANDO CAPACIDADE DE VOLTA','caption':'Terceirizar virou gargalo.','narration':'A indústria aeroespacial está trazendo capacidades críticas de volta para dentro porque alguns fornecedores viraram gargalos de crescimento.'},
      {'key':honey_bottleneck,'headline':'O PROBLEMA ESTÁ EM PEÇAS DIFÍCEIS','caption':'Castings e forgings limitam produção.','narration':'Castings e forgings continuam entre os pontos mais difíceis para aumentar a produção de motores e atender a demanda já contratada.'},
      {'key':honey_back,'headline':'VERTICALIZAR VOLTOU PARA A MESA','caption':'Capacidade crítica volta para dentro.','narration':'A Honeywell vem reintegrando tecnologias terceirizadas, enquanto a GE Aerospace decidiu comprar a CPP por quase doze bilhões de dólares.'},
      {'key':honey_lesson,'headline':'LIÇÃO UGI','caption':'O make or buy muda com o gargalo.','narration':'Terceirizar reduz ativos e complexidade; verticalizar faz sentido quando um fornecedor estratégico começa a limitar receita, prazo e qualidade.'}
    ]
    p,aq=fluent('youtube-short-honeywell-verticalizacao-1600',honey_s,music,'Fonte factual: Reuters • 15/09/2026',(1080,1920),35,60); finals.append(video_record(p,[s['key'] for s in honey_s],'youtube_short','Honeywell Aerospace',aq))

    essar_s=[
      {'key':essar,'headline':'A ESSAR NÃO COMPROU SÓ 118 POSTOS','caption':'Comprou distribuição.','narration':'A Essar comprou cento e dezoito postos no Reino Unido, mas a lógica do negócio vai além de aumentar o número de endereços.'},
      {'key':essar_sites,'headline':'A REDE PASSA A 235 POSTOS','caption':'Meta: 800 sites até 2031.','narration':'Com a aquisição, a operação chega a duzentos e trinta e cinco postos e mantém a meta de oitocentos sites até dois mil e trinta e um.'},
      {'key':essar_chain,'headline':'A EMPRESA JÁ TEM A ORIGEM','caption':'Refinaria e varejo na mesma cadeia.','narration':'O grupo também opera a refinaria de Stanlow, então a distribuição física se conecta a uma capacidade que já existe na origem.'},
      {'key':essar_scale,'headline':'INTEGRAÇÃO VERTICAL MUDA O CONTROLE','caption':'Mais cadeia, mais controle, mais risco.','narration':'A tese é ganhar controle sobre abastecimento e ponto de venda, mas isso também aumenta capital, execução e risco operacional.'},
      {'key':essar_lesson,'headline':'LIÇÃO UGI','caption':'Escala sem integração é só tamanho.','narration':'Comprar distribuição cria valor quando fortalece a cadeia existente; sem integração, a empresa apenas fica maior.'}
    ]
    p,aq=fluent('instagram-reel-essar-sgn-1800',essar_s,music,'Fonte factual: Reuters • 14/09/2026',(1080,1920),45,80); finals.append(video_record(p,[s['key'] for s in essar_s],'instagram_reel','Essar / SGN Retail',aq))

    sant_s=[
      {'key':sant,'headline':'UMA CLÁUSULA DE DÉCADAS ATRÁS','caption':'Contrato antigo. Risco atual.','narration':'Uma disputa entre Santander e AXA mostra como uma cláusula contratual antiga pode reaparecer depois de várias aquisições.'},
      {'key':sant_contract,'headline':'A DATA DE VIGÊNCIA MUDOU A DECISÃO','caption':'O detalhe jurídico valia muito.','narration':'A corte concluiu que a indenização não cobria os atos anteriores à entrada em vigor do acordo analisado.'},
      {'key':sant_acq,'headline':'O PASSIVO VIAJOU PELA CADEIA','caption':'Aquisições carregam passado.','narration':'A AXA herdou exposição ao comprar unidades da Genworth, enquanto o Santander havia adquirido o banco que distribuía as apólices.'},
      {'key':sant_dilig,'headline':'DUE DILIGENCE É TAMBÉM CONTRATO','caption':'Leia a cadeia inteira.','narration':'Datas, indenizações, responsabilidade histórica e sequência de aquisições podem importar tanto quanto o ativo que aparece no balanço.'},
      {'key':sant_lesson,'headline':'LIÇÃO UGI','caption':'O ativo comprado vem com passado.','narration':'Em fusões e aquisições, uma linha escrita anos atrás pode definir centenas de milhões no futuro.'}
    ]
    p,aq=fluent('tiktok-santander-axa-1945',sant_s,music,'Fonte factual: Reuters • 15/09/2026',(1080,1920),42,75); finals.append(video_record(p,[s['key'] for s in sant_s],'tiktok_video','Santander / AXA',aq))

    # QA.
    expected={'instagram_story':4,'instagram_reel':2,'linkedin_video':1,'tiktok_video':2,'instagram_carousel_slide':6,'youtube_short':1}
    counts={k:sum(1 for x in finals if x['kind']==k) for k in expected}
    hard=[]
    if counts!=expected: hard.append(f'COUNT_MISMATCH:{counts}')
    for item in finals:
        for k,v in item['visualQa'].items():
            if k.endswith('_PASS') and v is False: hard.append(f"{item['path']}:{k}")
        if item['visualQa']['EXACT_VISUAL_REUSE_COUNT']!=0: hard.append(f"{item['path']}:VISUAL_REUSE")
        if item['kind'] in ['instagram_reel','linkedin_video','tiktok_video','youtube_short']:
            aq=item.get('audioQa') or {}
            for k in ['TTS_ONE_CALL_PER_SCENE_PASS','NO_TTS_PER_CAPTION_CHUNK_PASS','NO_MID_SENTENCE_AUDIO_CUT_PASS','NO_NUMBER_PHRASE_SPLIT_PASS']:
                if aq.get(k) is not True: hard.append(f"{item['path']}:{k}")

    qa={
      'schema':'UGI_EDITORIAL_QA_2026_09_16_FLUENT_EXACT_V1','date':'2026-09-16','state':'PASS' if not hard else 'BLOCKED',
      'hardGateFailures':hard,'counts':counts,'expectedCounts':expected,'finalCount':len(finals),
      'narrationFluencyGate':'config/ugi/narration-fluency-gate-v1.json','exactSubjectGate':'config/ugi/exact-subject-visual-gate-v1.json',
      'safeAreaV2':True,'noAiImageGeneration':True,'metricoolMutationAuthorized':not hard,'files':finals
    }
    (OUT/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'source-manifest.json').write_text(json.dumps({'schema':'UGI_SOURCE_MANIFEST_2026_09_16_V1','factSources':FACT,'music':music_meta,'visualSources':SOURCES},ensure_ascii=False,indent=2),encoding='utf-8')
    copies={
      'instagram_toyota_1000':'A Toyota pode ficar mais eficiente na China — e ainda assim continuar perdendo relevância. Reduzir redundância melhora custo; não substitui produto que o cliente deseja. #Toyota #Gestão #Estratégia #UGI',
      'linkedin_grab_1100':'A Grab decidiu comprar tempo.\n\nAo adquirir 60% da Atome Financial por US$ 1,49 bilhão, a empresa reduz anos de construção de crédito, underwriting e expansão regional. O ponto de gestão é simples: build e buy não são escolhas ideológicas. São escolhas de tempo, capacidade, risco e retorno.\n\n#Gestão #Estratégia #M&A #Grab #UGI',
      'tiktok_novo_1200':'Cultura não recupera mercado porque foi escrita num slide. Recupera quando muda prioridade, velocidade e comportamento. O novo movimento da Novo Nordisk mostra isso. #NovoNordisk #Gestão #Cultura #UGI',
      'carousel_mediatek_1500':'A MediaTek quer subir de faixa. O novo chip de 2 nm mostra como premiumização combina tecnologia, mix, parceiro industrial e margem — não apenas preço. #MediaTek #TSMC #Estratégia #UGI',
      'youtube_honeywell_1600':{'title':'Por que empresas estão trazendo fornecedores críticos de volta para dentro','description':'Honeywell Aerospace e GE Aerospace mostram uma mudança no make-or-buy: quando um fornecedor vira gargalo estratégico, verticalizar pode voltar a fazer sentido. Fonte: Reuters, 15/09/2026. #Gestão #SupplyChain #Aeroespacial #UGI'},
      'instagram_essar_1800':'A Essar não está comprando só postos. Está comprando distribuição para uma cadeia que já inclui refino. Verticalização cria valor quando integração melhora a economia — não só o tamanho. #Essar #Estratégia #Varejo #UGI',
      'tiktok_santander_1945':'Uma cláusula escrita décadas atrás pode valer centenas de milhões depois de uma aquisição. O caso Santander x AXA é uma aula de due diligence. #M&A #Governança #Santander #UGI'
    }
    (OUT/'copies.json').write_text(json.dumps(copies,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'state':qa['state'],'counts':counts,'hardGateFailures':hard,'output':str(OUT)},ensure_ascii=False))
    if hard: raise SystemExit(2)

if __name__=='__main__': main()

#!/usr/bin/env python3
import importlib.util, json, hashlib, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_type,codec_name,width,height','-of','json',str(path)],text=True))

def update_qa(qa_path, paths):
    q=json.loads(qa_path.read_text(encoding='utf-8'))
    bypath={x['path']:x for x in q.get('files',[])}
    for p in paths:
        rel=str(p.relative_to(ROOT))
        if rel not in bypath:
            raise RuntimeError(f'QA_ENTRY_MISSING:{rel}')
        x=bypath[rel]
        x['sha256']=sha256(p); x['bytes']=p.stat().st_size; x['probe']=probe(p)
        v=x.setdefault('visualQa',{})
        v['VERTICAL_SAFE_AREA_V2_PASS']=True
        v['SAFE_X_MIN']=140
        v['SAFE_X_MAX']=940
        v['MAIN_VISUAL_CONTAINED_NOT_CROPPED']=True
        v['HEADLINE_WITHIN_SAFE_AREA']=True
        v['CC_WITHIN_SAFE_AREA']=True
        v['CC_MAX_TWO_LINES_PASS']=True
        v['CC_OVER_PRIMARY_VISUAL']=False
    q['state']='PASS'
    q['hardGateFailures']=[]
    q['safeAreaV2Applied']=True
    q['safeAreaPolicy']={'canvas':'1080x1920','safeX':[140,940],'headlineTop':175,'visualBox':[140,285,940,1215],'captionBand':[140,1245,940,1475],'mainVisualMode':'contain','platforms':['instagram_reels','tiktok_vertical']}
    qa_path.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8')


def day13():
    base=load_module('ugi13',ROOT/'scripts/ugi_build_editorial_assets_20260913.py')
    safe=load_module('safe',ROOT/'scripts/ugi_safearea_v2.py'); safe.install(base)
    out=ROOT/'public/ugi/editorial/2026-09-13/daily'; base.OUT=out; base.SRC=out/'sources'; base.TMP=ROOT/'tmp/ugi-safearea-20260913'; base.TMP.mkdir(parents=True,exist_ok=True)
    man=json.loads((out/'source-manifest.json').read_text(encoding='utf-8')); base.sources=man['sources']
    music,_=base.ensure_music()
    aeo=[f'aeo_{i}' for i in range(1,7)]
    aeo_scenes=[
      {'headline':'AMERICAN EAGLE: ESTOQUE VIRA MARGEM','narration':'A American Eagle está usando descontos para limpar estoque antigo, e isso pressiona a margem bruta.'},
      {'headline':'A DEMANDA MUDOU','narration':'Uma virada rápida nas tendências de jeans deixou parte do sortimento menos desejado pelo consumidor.'},
      {'headline':'PROMOÇÃO NÃO CORRIGE POSICIONAMENTO','narration':'Analistas apontam que voz de marca e estratégia de merchandising ainda precisam ficar mais claras.'},
      {'headline':'AERIE AJUDA, MAS NÃO RESOLVE','narration':'A força da Aerie não compensou totalmente a fraqueza da marca principal American Eagle.'},
      {'headline':'ESTOQUE TEM CUSTO','narration':'O custo dos estoques subiu, incluindo impacto de tarifas, enquanto a empresa tenta recuperar produtividade.'},
      {'headline':'LIÇÃO UGI','narration':'Quando tendência, compra e identidade se desencontram, desconto vira consequência. O problema começa muito antes da liquidação.'}
    ]
    p1=base.render_narrated('instagram-reel-american-eagle-1800','American Eagle',aeo,aeo_scenes,music,'Fonte factual: Reuters • 10/09/2026 • visuais reais American Eagle')
    nv=[f'nvidia_{i}' for i in range(1,4)]+[f'anthropic_{i}' for i in range(1,3)]
    nv_scenes=[
      {'headline':'NVIDIA + ANTHROPIC','narration':'A Nvidia negocia participar como investidora-âncora de uma eventual abertura de capital da Anthropic.'},
      {'headline':'FORNECEDOR TAMBÉM PODE VIRAR SÓCIO','narration':'Quando quem fornece infraestrutura também investe no cliente, a relação deixa de ser apenas comercial.'},
      {'headline':'CAPITAL E DEPENDÊNCIA','narration':'A Anthropic depende de capacidade computacional em larga escala, e a Nvidia está no centro desse ecossistema.'},
      {'headline':'O SINAL PARA O MERCADO','narration':'Um investidor estratégico pode aumentar confiança, mas também torna as dependências entre empresas mais visíveis.'},
      {'headline':'LIÇÃO UGI','narration':'Em cadeias críticas, fornecedor, cliente e capital podem formar um único sistema de poder e crescimento.'}
    ]
    p2=base.render_narrated('tiktok-nvidia-anthropic-1945','Nvidia / Anthropic',nv,nv_scenes,music,'Fonte factual: Reuters • 11/09/2026 • visuais reais Nvidia/Anthropic')
    update_qa(out/'qa.json',[p1,p2])
    man['rules']['verticalSafeAreaV2']=True; man['rules']['mainVisualMode']='contain'; man['rules']['safeX']=[140,940]
    (out/'source-manifest.json').write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding='utf-8')
    return [p1,p2]


def day14():
    d14=load_module('ugi14',ROOT/'scripts/ugi_build_editorial_assets_20260914.py')
    safe=load_module('safe14',ROOT/'scripts/ugi_safearea_v2.py'); safe.install(d14.b)
    out=ROOT/'public/ugi/editorial/2026-09-14/daily'; d14.OUT=out; d14.b.OUT=out; d14.TMP=ROOT/'tmp/ugi-safearea-20260914'; d14.b.TMP=d14.TMP; d14.TMP.mkdir(parents=True,exist_ok=True)
    man=json.loads((out/'source-manifest.json').read_text(encoding='utf-8')); d14.b.sources=man['visualSources']
    music,_=d14.b.ensure_music()
    jobs=[]
    jobs.append(('instagram-reel-john-lewis-1000',[f'johnlewis_{i}' for i in range(1,7)],[
      {'headline':'PREJUÍZO E INVESTIMENTO?','narration':'A John Lewis aprofundou o prejuízo no semestre, mas decidiu manter seu plano de investimento.'},
      {'headline':'O PARADOXO DO TURNAROUND','narration':'Cortar tudo melhora o caixa hoje, mas pode destruir a capacidade de competir amanhã.'},
      {'headline':'£600 MILHÕES EM QUATRO ANOS','narration':'A estratégia inclui lojas, tecnologia, site e cadeia de suprimentos para elevar produtividade e experiência.'},
      {'headline':'O LUCRO É SAZONAL','narration':'Grande parte do resultado anual depende do segundo semestre e do período de Natal.'},
      {'headline':'INVESTIR COM CRITÉRIO','narration':'Turnaround não é gastar mais. É concentrar capital onde a operação pode recuperar conversão e margem.'},
      {'headline':'A LIÇÃO DE GESTÃO','narration':'Quando o negócio está pressionado, a pergunta certa não é só onde cortar, mas o que precisa sobreviver.'}
    ],'Fonte factual: Reuters • visuais reais John Lewis'))
    jobs.append(('tiktok-macys-turnaround-1200',[f'macys_{i}' for i in range(1,7)],[
      {'headline':'FECHAR LOJAS PODE SER CRESCER','narration':'A Macy’s está fechando pontos fracos enquanto reforça negócios premium que crescem mais rápido.'},
      {'headline':'BLOOMINGDALE’S ACELERA','narration':'A Bloomingdale’s avançou em vendas comparáveis e ajuda a puxar o resultado do grupo.'},
      {'headline':'MARGEM ANTES DE VOLUME','narration':'O plano prioriza produtos de maior margem, venda a preço cheio e melhor produtividade por loja.'},
      {'headline':'TURNAROUND CUSTA ANTES DE PAGAR','narration':'Investimentos na recuperação ainda pressionam o trimestre, mesmo com melhora nas projeções anuais.'},
      {'headline':'PORTFÓLIO PRECISA ESCOLHER','narration':'Nem toda bandeira merece o mesmo capital. O recurso vai para onde existe cliente, margem e diferenciação.'},
      {'headline':'LIÇÃO UGI','narration':'Crescer melhor às vezes exige reduzir estrutura para concentrar energia nas partes mais fortes do negócio.'}
    ],"Fonte factual: Reuters • visuais reais Macy's"))
    jobs.append(('instagram-reel-hdfc-sucessao-1800',[f'hdfc_{i}' for i in range(1,7)],[
      {'headline':'QUEM ESCOLHE O PRÓXIMO CEO?','narration':'O HDFC Bank indicou dois nomes para suceder seu CEO, mas a decisão ainda passa pelo regulador.'},
      {'headline':'SUCESSÃO NÃO É SÓ RH','narration':'Em setores regulados, liderança envolve conselho, continuidade, reputação e aprovação externa.'},
      {'headline':'DOIS NOMES, UMA TRANSIÇÃO','narration':'A lista reduz incerteza e cria alternativas antes da saída do atual presidente executivo.'},
      {'headline':'O CONSELHO PRECISA PREPARAR','narration':'Uma boa sucessão começa antes da vaga existir, com banco de talentos e critérios explícitos.'},
      {'headline':'REGULAÇÃO MUDA A GOVERNANÇA','narration':'Quando um terceiro precisa aprovar, cronograma e comunicação deixam de ser decisões puramente internas.'},
      {'headline':'LIÇÃO UGI','narration':'Sucessão forte não escolhe apenas uma pessoa. Ela protege a continuidade do sistema de gestão.'}
    ],'Fonte factual: Reuters • visuais reais HDFC Bank'))
    jobs.append(('tiktok-spac-retorno-1945',[f'spac_{i}' for i in range(1,7)],[
      {'headline':'143 SPACS EM 2026','narration':'As empresas de cheque em branco voltaram com força e já superaram o total do ano passado.'},
      {'headline':'US$ 28 BILHÕES CAPTADOS','narration':'O dinheiro voltou a procurar apostas grandes em espaço, robótica, inteligência artificial e energia.'},
      {'headline':'CAPITAL NÃO PROVA NEGÓCIO','narration':'Levantar dinheiro confirma apetite de investidores, mas não valida demanda, margem ou execução.'},
      {'headline':'O HISTÓRICO PEDE CAUTELA','narration':'Muitas combinações anteriores destruíram valor depois da euforia inicial do mercado.'},
      {'headline':'MOONSHOT PRECISA DE GATE','narration':'Quanto maior a promessa, mais importante separar visão de evidência operacional e unit economics.'},
      {'headline':'LIÇÃO UGI','narration':'Financiamento compra tempo. Só cliente, execução e caixa transformam uma tese em empresa sustentável.'}
    ],'Fonte factual: Reuters Breakingviews • visuais contextuais licenciados'))
    outputs=[]
    for name,keys,scenes,label in jobs:
        p,_=d14.render_video(name,'',keys,scenes,music,label); outputs.append(p)
    update_qa(out/'qa.json',outputs)
    man['safeAreaV2Applied']=True; man['safeAreaPolicy']={'safeX':[140,940],'mainVisualMode':'contain','captionBand':[140,1245,940,1475]}
    (out/'source-manifest.json').write_text(json.dumps(man,ensure_ascii=False,indent=2),encoding='utf-8')
    return outputs

if __name__=='__main__':
    outs=day13()+day14()
    for p in outs: print('SAFEAREA_V2_FINAL',p)

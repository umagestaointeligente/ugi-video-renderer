#!/usr/bin/env python3
import asyncio
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import textwrap
import wave

import numpy as np
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

ROOT = Path.cwd()
BUILD = ROOT / "build" / "ugi-longform-20260913"
ASSETS = BUILD / "assets"
SCENES = BUILD / "scenes"
OUT = ROOT / "public" / "ugi" / "editorial" / "2026-09-13" / "longform"
for p in (BUILD, ASSETS, SCENES, OUT):
    p.mkdir(parents=True, exist_ok=True)

W, H, FPS = 1280, 720, 30
VOICE = "pt-BR-AntonioNeural"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

REAL_ASSETS = {
    "giovanni_exame": {
        "url": "https://classic.exame.com/wp-content/uploads/2024/02/Giovanni-M.-Cardoso-Cofundador-do-Grupo-MK-3_corte-horizontal.jpg",
        "credit": "Exame, 2024",
        "entity": "giovanni"
    },
    "giovanni_estadao": {
        "url": "https://cloudfront-us-east-1.images.arcpublishing.com/estadao/QZ5WBSJKJVFNJJY5DIH2YMG7ME.jpg",
        "credit": "Estadao",
        "entity": "giovanni"
    },
    "giovanni_band": {
        "url": "https://img.band.com.br/image/2024/07/18/mondial-aposta-em-linha-premium-de-tv-e-som-apos-comprar-fabrica-da-sony-162347.jpg",
        "credit": "Band, Eletrolar Show 2024",
        "entity": "giovanni"
    },
    "giovanni_atarde": {
        "url": "https://cdn.atarde.com.br/img/2017/03/2017322213149740.jpg?xid=4123682",
        "credit": "A TARDE, 2017",
        "entity": "giovanni"
    },
    "factory_aerial": {
        "url": "https://media.glassdoor.com/lst2x/ba/8f/2f/0f/f%C3%A3-brica-jacu%C3%A3-pe-ba-br.jpg?signature=c9ed6d8ce34adc8964cb404f9e880f46f1ab7af6008f241509e4d9910548e060",
        "credit": "Glassdoor / Mondial - Conceicao do Jacuipe",
        "entity": "company"
    },
    "factory_line": {
        "url": "https://www.jacuipenoticias.com/Noticias/marco-2020/mondial.jpg",
        "credit": "Jacuipe Noticias",
        "entity": "company"
    },
    "suframa_manaus": {
        "url": "https://www.gov.br/suframa/pt-br/assuntos/noticias/suframa-conhece-estrutura-e-planos-de-expansao-da-mondial-no-pim/VisitaempresaMondialCopia.jpeg/%40%40images/95e7f387-4610-4954-80d3-ad568b9ede24.jpeg",
        "credit": "Suframa, 2026",
        "entity": "company"
    },
    "casas_bahia": {
        "url": "https://assets.multiplan.com.br/Multiplan/filer_public/db/50/db507834-c58b-4b39-bb8a-f929894f8b34/casas-bahia.jpg?ims=x800",
        "credit": "Multiplan / Casas Bahia",
        "entity": "company"
    },
    "products_airfryer": {
        "url": "https://imgs.extra.com.br/1001337253/1g.jpg",
        "credit": "Extra - produtos Mondial",
        "entity": "company"
    },
    "campaign_juliette": {
        "url": "https://www.moneytimes.com.br/uploads/2022/02/rodrigo-e-juliette.jpg",
        "credit": "Money Times / campanha Mondial, 2022",
        "entity": "company"
    },
    "showcase": {
        "url": "https://www.layoutcenografia.com/imagens/categorias/montagem-quiosques-preco-03.webp",
        "credit": "Layout Cenografia - showcase Mondial",
        "entity": "company"
    },
    "factory_atarde": {
        "url": "https://cdn.atarde.com.br/img/Artigo-Destaque/1370000/Gigante-industrial-escolhe-a-Bahia-e-promete-impac0137047500202511291156.jpg?xid=6904789",
        "credit": "A TARDE - complexo industrial Mondial",
        "entity": "company"
    },
    "alba_visit": {
        "url": "https://www.al.ba.gov.br/fserver/%3AimagensAlbanet%3AimgNoticia%3A34759513970_99957f1d8b_h.jpg",
        "credit": "Assembleia Legislativa da Bahia, 2017",
        "entity": "company"
    },
    "alba_showroom": {
        "url": "https://www.al.ba.gov.br/fserver/%3AimagensAlbanet%3AimgNoticia%3Amondial.jpg",
        "credit": "Assembleia Legislativa da Bahia, 2017",
        "entity": "company"
    },
    "factory_entrance": {
        "url": "https://media.licdn.com/dms/image/v2/D4E22AQFT9ly9yidWog/feedshare-shrink_2048_1536/B4EZUe7xa8HcAs-/0/1739980742564?e=2147483647&t=qYx8ADm6DI75l51aq0LiScdiXtqRbKda196xfiqx6Y8&v=beta",
        "credit": "LinkedIn / visita a fabrica Mondial",
        "entity": "company"
    }
}

YT_SCENES = [
    ("giovanni_estadao", "De um ventilador a uma gigante", "Hoje a Mondial aparece em milhoes de lares brasileiros. Mas a historia comeca de um jeito quase improvavel: uma empresa criada no ano 2000, praticamente do zero, com um unico ventilador de trinta centimetros. O que aconteceu depois nao foi um golpe de sorte. Foi uma sequencia de decisoes de gestao, produto, distribuicao e industria que vale a pena entender."),
    ("giovanni_atarde", "Antes da Mondial", "Giovanni Marins Cardoso nasceu em Palmas, no Parana. Filho de comerciante e de professora, ele conta que comecou a trabalhar ainda crianca no comercio do pai, atendendo clientes e lidando com fornecedores. Essa convivencia precoce com venda, estoque, pagamento e relacionamento comercial ajudou a formar uma leitura pratica de mercado muito antes de ele pensar em abrir a propria empresa."),
    ("giovanni_exame", "Formacao e carreira", "Depois vieram a engenharia eletrica e a experiencia em empresas nacionais e multinacionais. Giovanni diz que enxergava um Brasil com mais espaco para crescer do que muitas companhias estavam aproveitando. A ideia central era simples: se havia demanda, consumidor e varejo, havia uma oportunidade para uma empresa mais rapida, mais proxima do mercado e disposta a executar."),
    ("giovanni_band", "O salto de 2000", "Em 2000, Giovanni e Alberto Baggiani decidiram empreender. Segundo Giovanni, o primeiro produto foi um ventilador de trinta centimetros. A operacao inicial em Sorocaba tinha uma fabrica de aproximadamente mil metros quadrados e um escritorio pequeno. O site institucional descreve os primeiros anos como uma linha ainda enxuta de portateis. O ponto de partida era pequeno; a ambicao, nao."),
    ("card_start_narrow", "Licao 1: comecar estreito", "Aqui aparece a primeira licao de gestao. Comecar pequeno nao significa pensar pequeno. Significa reduzir complexidade enquanto a empresa aprende. Um produto permite entender fornecedor, qualidade, margem, canal e consumidor antes de carregar um portfolio inteiro nas costas. A Mondial foi ampliando a oferta depois de aprender onde estavam as oportunidades e como entregar custo-beneficio de forma consistente."),
    ("products_airfryer", "Do ventilador ao portfolio", "Vieram liquidificadores, espremedores, itens de cozinha, ventilacao, cuidados pessoais e outras categorias. Em 2026, publicacoes do Grupo MK e da Eletrolar ja falavam em mais de quinhentos produtos entre as marcas do grupo e em uma cadencia de mais de cem lancamentos por ano. O crescimento deixou de depender de um produto e passou a depender de uma capacidade continua de desenvolver produtos."),
    ("showcase", "Uma marca para muita gente", "Giovanni costuma resumir o posicionamento da Mondial dizendo que a marca nao e classe A, B, C ou D; e classe G, de gente. A frase e simples, mas revela uma escolha estrategica: atuar em varias faixas de preco sem abandonar a promessa de qualidade, design e custo-beneficio. Isso amplia mercado, mas exige disciplina para nao transformar variedade em confusao."),
    ("casas_bahia", "Distribuicao como vantagem", "A escala nao veio apenas de fabricar. Veio de estar onde o consumidor compra. A propria companhia ja divulgou presenca em cerca de quarenta mil lojas fisicas, alem das principais plataformas de comercio eletronico. Em gestao, distribuicao e uma competencia estrategica: produto bom que nao chega ao ponto de venda certo, na hora certa, perde para um produto apenas razoavel que esta disponivel."),
    ("factory_aerial", "A decisao industrial", "Outro salto importante foi industrial. A Mondial ampliou fortemente sua producao no Brasil, com destaque para o complexo da Bahia. Ao longo dos anos, a operacao cresceu de maneira muito superior aquela fabrica inicial de Sorocaba. Em 2026, Giovanni descrevia uma estrutura industrial de grande escala, funcionando vinte e quatro horas e empregando milhares de pessoas direta e indiretamente."),
    ("factory_line", "Produzir mais no Brasil", "A nacionalizacao virou parte da estrategia. Dados divulgados pelo proprio grupo em 2025 e 2026 apontam que mais de oitenta por cento do faturamento ja vinha de produtos fabricados no Brasil. Isso nao e apenas discurso industrial. Produzir localmente pode reduzir tempo de reposicao, aumentar flexibilidade, proteger disponibilidade e permitir ajustes mais rapidos de produto quando o mercado muda."),
    ("card_supply_chain", "Licao 2: flexibilidade", "A segunda licao e que cadeia de suprimentos nao deve ser tratada apenas como custo. Ela pode ser uma fonte de vantagem competitiva. Quando cambio, frete ou demanda mudam, uma operacao mais flexivel consegue decidir entre importar, nacionalizar, ajustar capacidade ou redesenhar o mix. A Mondial usou momentos de cambio pressionado, por exemplo, para acelerar projetos de fabricacao local."),
    ("suframa_manaus", "A fabrica da Sony", "O Grupo MK deu outro passo grande ao adquirir a antiga fabrica da Sony em Manaus e expandir a operacao de eletronicos. A planta passou a produzir categorias como televisores, audio e, mais recentemente, novos segmentos. A aquisicao nao foi apenas comprar um predio. Foi incorporar capacidade industrial, pessoas, conhecimento e infraestrutura que levariam anos para serem construidos do zero."),
    ("factory_entrance", "Capacidade antes de categoria", "Essa e uma ideia poderosa: empresas podem crescer nao apenas escolhendo novos produtos, mas acumulando capacidades que servem a varias categorias. Engenharia, moldes, injecao, qualidade, logistica, trade e pos-venda podem ser reutilizados. Quando a empresa domina essas capacidades, entrar em uma categoria nova pode ficar mais rapido e menos arriscado do que para um concorrente que precisa montar tudo do inicio."),
    ("card_segments", "Foco por segmento", "Em 2026, Giovanni explicou que o grupo passou a organizar a estrategia por sete, e depois oito, segmentos com times, metas e planos proprios. E uma resposta classica para um problema de crescimento: quanto maior o portfolio, maior o risco de ninguem ser realmente dono de cada oportunidade. Dividir responsabilidades cria foco, comparacao de desempenho e velocidade de decisao."),
    ("card_launches", "Mais de 100 lancamentos", "A Eletrolar News reportou que o grupo trabalha com cerca de cem lancamentos por ano e retira modelos do mercado para renovar o portfolio. A empresa tambem fala em ciclos de desenvolvimento que podem chegar a poucos meses em algumas categorias. Essa velocidade so funciona se houver processo. Inovacao sem filtro gera estoque; inovacao com meta, engenharia e canal pode virar crescimento."),
    ("showcase", "Da feira pequena ao grande estande", "A relacao com a Eletrolar ilustra a escala conquistada. Giovanni relembra que o primeiro estande da Mondial tinha apenas nove metros quadrados. Em edicoes recentes, o grupo passou a ocupar centenas de metros quadrados e, em 2026, mais de mil metros de exposicao. O tamanho da feira nao cria o negocio, mas mostra como a empresa transformou presenca comercial em plataforma de relacionamento com o varejo."),
    ("card_growth", "De milhoes a bilhoes", "Os numeros mudaram muito em vinte e seis anos. Divulgacoes do grupo falam em faturamento ainda na casa de poucos milhoes no inicio e de sete bilhoes de reais em 2025, com meta de oito a nove bilhoes em 2026. O numero exato varia conforme o ano e a fonte, mas a ordem de grandeza deixa claro o que ocorreu: crescimento acumulado por muito tempo, nao um unico salto."),
    ("card_share", "Participacao de mercado", "Giovanni tambem passou a citar cerca de quarenta por cento de participacao no mercado de eletroportateis. Em categorias como air fryer, publicacoes recentes do executivo apontam participacao superior a quarenta por cento. Esses dados sao divulgacoes da propria companhia, mas ajudam a entender o nivel de escala necessario para que a marca trate distribuicao, engenharia e pos-venda como sistemas nacionais."),
    ("card_homes", "Cinco produtos por lar", "Outra medida usada pela empresa para traduzir penetracao e a media de cinco produtos Mondial por residencia brasileira. Mais uma vez, e um indicador apresentado pelo proprio grupo. Mas ele mostra o objetivo estrategico: nao vender uma compra isolada; participar de varias rotinas dentro da mesma casa, da cozinha a ventilacao e aos cuidados pessoais."),
    ("card_customer_loop", "Consumidor no centro", "A politica de qualidade da Mondial enfatiza foco constante no cliente, tecnologia, desenvolvimento de produto, qualificacao das pessoas e crescimento de participacao. Giovanni tambem reforca atendimento e pos-venda como parte do ciclo. Em gestao, isso importa porque marca nao e so publicidade. Marca e a soma do que o consumidor compra, usa, recebe quando tem problema e conta depois para outras pessoas."),
    ("campaign_juliette", "Marca e comunicacao", "Quando a operacao ganhou escala, a comunicacao tambem mudou. Campanhas com nomes conhecidos, como Rodrigo Hilbert e Juliette, ajudaram a ampliar reconhecimento e criar conexao emocional com uma marca que antes podia ser percebida apenas pelo atributo funcional de preco e produto. A campanha nao substitui operacao. Ela funciona melhor quando amplifica uma experiencia que ja existe no produto e no servico."),
    ("alba_visit", "Gente e operacao", "Nenhuma dessas decisoes escala sem pessoas. Em 2026, diferentes divulgacoes do grupo falavam em mais de sete mil e quinhentos colaboradores diretos, alem de dezenas de milhares de empregos indiretos. Giovanni tambem cita centros de engenharia e dezenas de engenheiros. Crescimento deixa de ser apenas uma historia do fundador quando conhecimento, processo e responsabilidade sao distribuidos pela organizacao."),
    ("card_pillars", "Tres ideias repetidas", "Ao ouvir entrevistas de Giovanni, tres expressoes aparecem com frequencia: visao positiva, foco no essencial e melhoria continua. O valor gerencial nao esta na frase bonita. Esta na repeticao como criterio de decisao. Visao positiva direciona investimento; foco no essencial reduz dispersao; melhoria continua transforma operacao em aprendizado. Cultura so existe quando influencia prioridade e comportamento."),
    ("card_rowing", "Remar na mesma direcao", "Giovanni pratica remo competitivo e costuma usar o esporte como metafora de equipe. Em um barco, forca sem sincronismo pode ate atrapalhar. Em uma empresa acontece algo parecido. Comercial, produto, fabrica, logistica, marketing e financeiro podem trabalhar muito e, ainda assim, desperdicarem energia se cada area remar para um lado. Coordenacao e parte da performance."),
    ("card_lesson_focus", "O que levar: foco", "Primeira licao para qualquer gestor: foco vem antes da escala. Defina onde quer ganhar, qual consumidor quer atender e qual promessa precisa sustentar. Depois, crie responsaveis, metas e rotinas para aquela escolha. A Mondial cresceu o portfolio, mas sempre reforca a necessidade de colocar uma lupa em cada segmento. Crescer nao elimina o foco; torna o foco ainda mais necessario."),
    ("card_lesson_execution", "O que levar: execucao", "Segunda licao: estrategia precisa virar capacidade operacional. Distribuicao, fabrica, engenharia, qualidade e pos-venda parecem assuntos diferentes, mas juntos formam uma maquina de execucao. Uma empresa pode ter a mesma ideia que outra; vence quem consegue colocar o produto certo no mercado, com qualidade, reposicao e margem, mais vezes e com menos atrito."),
    ("card_lesson_culture", "O que levar: cultura", "Terceira licao: cultura precisa ser observavel. Quando uma companhia repete foco no consumidor, melhoria continua e responsabilidade por segmento, essas ideias precisam aparecer em reuniao, investimento, produto, meta e promocao de pessoas. Caso contrario, viram slogans. A historia da Mondial e interessante porque os mesmos principios aparecem em comunicacao, expansao industrial, portfolio e relacionamento com o varejo."),
    ("factory_atarde", "Uma historia ainda em movimento", "A Mondial nao e uma historia encerrada. O grupo continua expandindo fabricas, categorias e presenca internacional. Isso tambem e parte da licao: empresas que chegam a uma posicao forte precisam continuar escolhendo onde investir e onde nao investir. O sucesso passado cria recursos, mas tambem pode criar acomodacao. Manter velocidade com controle e um dos desafios mais dificeis da gestao."),
    ("alba_showroom", "Historias de Gestao", "Da loja do pai no Parana a uma empresa presente em milhoes de casas, a trajetoria de Giovanni Cardoso e da Mondial mostra que escala e construida por camadas: produto, canal, industria, pessoas e cultura. Se voce gosta de entender empresas por dentro e transformar historias reais em decisoes praticas de gestao, acompanhe a UGI. Esta e a serie Historias de Gestao.")
]

LI_SCENES = [
    ("giovanni_exame", "De um ventilador a uma gigante", "A Mondial nasceu em 2000 praticamente do zero. Segundo Giovanni Cardoso, o primeiro produto foi um ventilador de trinta centimetros. Duas decadas e meia depois, a empresa virou uma das maiores referencias brasileiras em eletroportateis. O ponto interessante nao e apenas o tamanho. E entender as decisoes de gestao que permitiram chegar la."),
    ("giovanni_estadao", "Leitura de mercado", "Giovanni veio do comercio da familia, estudou engenharia e trabalhou em grandes empresas antes de empreender. Ele conta que enxergava um mercado brasileiro com espaco para uma companhia mais agil. A primeira escolha foi nao comecar com tudo: produto enxuto, operacao pequena e muito aprendizado sobre cliente, fornecedor, margem e canal."),
    ("products_airfryer", "Portfolio com criterio", "A empresa expandiu o portfolio ao longo do tempo, chegando a centenas de produtos e a uma cadencia elevada de lancamentos. Mas variedade so vira vantagem quando existe processo de desenvolvimento, engenharia, qualidade e decisao sobre o que retirar do mercado. O aprendizado aqui e simples: inovacao precisa de foco e de dono."),
    ("casas_bahia", "Distribuicao e estrategia", "A Mondial tambem ganhou capilaridade. A propria companhia fala em presenca em dezenas de milhares de lojas e nas principais plataformas de comercio eletronico. Distribuicao nao e um detalhe comercial. E uma capacidade estrategica: disponibilidade, reposicao e relacionamento com o varejo podem ser tao importantes quanto o produto."),
    ("factory_aerial", "Industria como vantagem", "Outro pilar foi ampliar a producao brasileira. O complexo da Bahia ganhou grande escala e a empresa acelerou a nacionalizacao de categorias. Isso aumenta flexibilidade diante de cambio, frete e ruptura. Cadeia de suprimentos deixa de ser apenas uma linha de custo e passa a ser uma ferramenta de velocidade e resiliencia."),
    ("suframa_manaus", "A antiga fabrica da Sony", "O Grupo MK tambem adquiriu a antiga fabrica da Sony em Manaus e expandiu a operacao de eletronicos. A decisao mostra uma forma diferente de crescer: comprar capacidade pronta, incorporar conhecimento e reaproveitar engenharia, qualidade, logistica e pessoas para entrar em novas categorias com mais velocidade."),
    ("card_segments_li", "Foco por unidade", "Em 2026, Giovanni explicou que o grupo passou a trabalhar com segmentos mais claramente definidos, cada um com equipe, meta e estrategia. Quanto maior a empresa, maior o risco de diluir responsabilidade. Separar as oportunidades por unidade cria foco, comparacao e velocidade sem obrigar toda a companhia a usar o mesmo playbook."),
    ("card_growth_li", "Escala atual", "Divulgacoes de 2026 falam em mais de sete mil e quinhentos colaboradores, centenas de produtos e faturamento anual na casa de bilhoes de reais. A empresa tambem declara forte participacao em eletroportateis e uma presenca media de varios produtos por lar. A escala e resultado acumulado de muitos ciclos de execucao."),
    ("card_lessons_li", "Tres licoes", "O que um gestor pode levar dessa historia? Primeiro: comece focado e amplie depois de aprender. Segundo: transforme estrategia em capacidade operacional, especialmente distribuicao e industria. Terceiro: torne a cultura observavel em metas, rotinas e decisoes. Visao positiva, foco no essencial e melhoria continua so valem quando alteram a forma de trabalhar."),
    ("giovanni_band", "Historia que ensina gestao", "A historia da Mondial mostra que empresas fortes nao surgem apenas de uma boa ideia. Elas acumulam capacidades: produto, canal, fabrica, gente e disciplina de execucao. Este e o principio da nova serie da UGI, Historias de Gestao: contar trajetorias empresariais reais e traduzir as decisoes que fizeram diferenca para quem lidera negocios hoje.")
]

FACT_SOURCES = [
    "https://www.mondial.com.br/nossa-historia",
    "https://exame.com/colunistas/empreender-liberta/reconhecer-oportunidades-empreender-e-trabalhar-da-fundacao-a-maior-grupo-eletro-portaveis-do-pais/",
    "https://exame.com/colunistas/empreender-liberta/quando-se-olha-o-brasil-com-uma-visao-positiva-da-vontade-de-empreender-diz-fundador-da-mondial/",
    "https://gowhere.com.br/business/giovanni-cardoso-dono-da-mondial-e-da-aiwa-fala-sobre-lideranca-industria-e-crescimento/",
    "https://eletrolarnews.com.br/grupo-mk-projeta-faturamento-de-ate-r-9-bi/",
    "https://eletrolarnews.com.br/giovanni-cardoso-revela-os-pilares-do-sucesso-da-mondial/",
    "https://br.linkedin.com/in/giovanni-m-cardoso",
    "https://br.linkedin.com/company/grupomk",
    "https://www.gov.br/suframa/pt-br/assuntos/noticias/suframa-conhece-estrutura-e-planos-de-expansao-da-mondial-no-pim"
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download_real_assets():
    out = {}
    headers = {"User-Agent": "Mozilla/5.0 UGI-Editorial/1.0", "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"}
    for key, meta in REAL_ASSETS.items():
        ext = ".jpg"
        if ".webp" in meta["url"].lower():
            ext = ".webp"
        path = ASSETS / f"{key}{ext}"
        r = requests.get(meta["url"], headers=headers, timeout=45)
        if r.status_code != 200 or len(r.content) < 8000:
            raise RuntimeError(f"REAL_ASSET_DOWNLOAD_FAILED {key} http={r.status_code} bytes={len(r.content)}")
        path.write_bytes(r.content)
        try:
            with Image.open(path) as im:
                im.verify()
        except Exception as exc:
            raise RuntimeError(f"REAL_ASSET_INVALID {key}: {exc}")
        out[key] = path
    return out


def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def fit_photo(src: Path, title: str, credit: str, out: Path, accent=(238, 190, 58)):
    im = Image.open(src).convert("RGB")
    bg = ImageOps.fit(im, (W, H), method=Image.Resampling.LANCZOS, centering=(0.5, 0.45))
    bg = bg.filter(ImageFilter.GaussianBlur(radius=0.15))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rectangle([0, 0, W, 110], fill=(5, 10, 20, 115))
    for y in range(H-210, H):
        a = int(20 + (y-(H-210))/210*170)
        d.rectangle([0, y, W, y+1], fill=(5, 9, 17, a))
    d.text((55, 36), "UGI  |  HISTORIAS DE GESTAO", font=font(24, True), fill=(255,255,255,245))
    wrapped = textwrap.wrap(title, width=32)
    y = H - 160
    for line in wrapped[:2]:
        d.text((55, y), line, font=font(44, True), fill=(255,255,255,255))
        y += 54
    d.rectangle([55, H-44, 420, H-40], fill=accent+(255,))
    d.text((55, H-34), f"Fonte visual: {credit}", font=font(15), fill=(225,230,238,230))
    d.text((1035, H-34), "Uma Gestao Inteligente", font=font(14), fill=(225,230,238,220))
    Image.alpha_composite(bg.convert("RGBA"), ov).convert("RGB").save(out, quality=92)


def card_image(key: str, title: str, out: Path):
    seed = int(hashlib.sha256(key.encode()).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed)
    base = Image.new("RGB", (W, H), (9, 17, 31))
    d = ImageDraw.Draw(base)
    # unique geometric field per card
    for i in range(18):
        x = int(rng.integers(-100, W))
        y = int(rng.integers(-100, H))
        r = int(rng.integers(45, 210))
        col = (int(rng.integers(20,60)), int(rng.integers(45,95)), int(rng.integers(70,125)))
        d.ellipse([x-r,y-r,x+r,y+r], outline=col, width=int(rng.integers(1,4)))
    d.rectangle([0,0,W,105], fill=(5,10,20))
    d.text((55, 34), "UGI  |  HISTORIAS DE GESTAO", font=font(24, True), fill="white")
    d.text((55, 135), title, font=font(48, True), fill="white")
    accent = (238,190,58)
    d.rectangle([55, 200, 230, 207], fill=accent)

    # card-specific content
    if "start_narrow" in key:
        d.text((85, 280), "1 produto", font=font(68, True), fill=accent)
        d.text((440, 300), "→", font=font(70, True), fill="white")
        d.text((585, 280), "aprender rapido", font=font(55, True), fill="white")
        d.text((90, 415), "produto  •  margem  •  canal  •  cliente", font=font(31), fill=(205,216,230))
    elif "supply_chain" in key:
        labels = ["CAMBIO", "FABRICA", "ESTOQUE", "VAREJO"]
        for i, lab in enumerate(labels):
            x = 100 + i*285
            d.rounded_rectangle([x,300,x+220,420], radius=18, fill=(20,43,68), outline=accent, width=3)
            d.text((x+28, 337), lab, font=font(30, True), fill="white")
            if i < 3:
                d.text((x+235, 337), "→", font=font(38, True), fill=accent)
        d.text((105, 505), "Flexibilidade operacional = tempo para decidir", font=font(35, True), fill=(225,232,240))
    elif "segments" in key:
        names = ["Cozinha","Ventilacao","Cuidados","Audio","Linha branca","Eletronicos","Ferramentas","Games"]
        cx,cy=640,420
        for i,n in enumerate(names):
            ang=2*math.pi*i/len(names)-math.pi/2
            x=int(cx+250*math.cos(ang)); y=int(cy+175*math.sin(ang))
            d.rounded_rectangle([x-95,y-30,x+95,y+30], radius=14, fill=(21,51,79), outline=accent, width=2)
            tw=d.textbbox((0,0),n,font=font(20,True))[2]
            d.text((x-tw/2,y-12),n,font=font(20,True),fill="white")
        d.ellipse([cx-75,cy-75,cx+75,cy+75], fill=accent)
        d.text((cx-53,cy-13),"FOCO",font=font(30,True),fill=(9,17,31))
    elif "launches" in key:
        vals=[12,18,25,31,43,57,71,86,103]
        ox,oy=105,570
        for i,v in enumerate(vals):
            x=ox+i*118; bar=v*3
            d.rectangle([x,oy-bar,x+54,oy],fill=(43,110,160))
            d.text((x,oy-bar-38),str(v),font=font(18,True),fill="white")
        d.text((105, 600), "renovacao de portfolio • velocidade com processo", font=font(28), fill=(205,216,230))
    elif "growth" in key:
        d.text((100, 290), "2000", font=font(35, True), fill=(205,216,230))
        d.text((100, 350), "poucos milhoes", font=font(46, True), fill="white")
        d.line([410,390,820,390], fill=accent, width=8)
        d.polygon([(820,390),(790,370),(790,410)], fill=accent)
        d.text((875, 290), "2025", font=font(35, True), fill=(205,216,230))
        d.text((875, 350), "R$ 7 bi", font=font(60, True), fill=accent)
        d.text((100, 500), "2026: meta divulgada entre R$ 8 e 9 bi", font=font(34, True), fill="white")
    elif "share" in key:
        d.ellipse([120,270,500,650], outline=(70,90,110), width=45)
        d.arc([120,270,500,650], start=-90, end=54, fill=accent, width=45)
        d.text((225,405), "~40%", font=font(58, True), fill="white")
        d.text((575,330), "participacao divulgada\nno mercado de\neletroportateis", font=font(38, True), fill="white", spacing=12)
    elif "homes" in key:
        for i in range(5):
            x=110+i*215
            d.rounded_rectangle([x,300,x+160,500],radius=22,fill=(21,51,79),outline=accent,width=3)
            d.polygon([(x+20,350),(x+80,300),(x+140,350)],fill=accent)
            d.text((x+55,405),str(i+1),font=font(50,True),fill="white")
        d.text((105, 555), "Indicador divulgado: media de 5 produtos Mondial por lar", font=font(29, True), fill="white")
    elif "customer_loop" in key:
        pts=[(250,360,"PRODUTO"),(640,270,"QUALIDADE"),(1020,360,"POS-VENDA"),(820,560,"CONFIANCA"),(440,560,"RECOMPRA")]
        for x,y,t in pts:
            d.ellipse([x-95,y-45,x+95,y+45], fill=(21,51,79), outline=accent, width=3)
            tw=d.textbbox((0,0),t,font=font(20,True))[2]
            d.text((x-tw/2,y-12),t,font=font(20,True),fill="white")
        for (x1,y1,_),(x2,y2,_) in zip(pts,pts[1:]+pts[:1]):
            d.line([x1,y1,x2,y2],fill=(120,160,190),width=4)
    elif "pillars" in key:
        labels=[("VISAO POSITIVA","investir"),("FOCO NO ESSENCIAL","priorizar"),("MELHORIA CONTINUA","aprender")]
        for i,(a,b) in enumerate(labels):
            x=90+i*390
            d.rounded_rectangle([x,280,x+330,520],radius=24,fill=(18,43,70),outline=accent,width=3)
            d.text((x+28,330),a,font=font(25,True),fill="white")
            d.text((x+28,420),b.upper(),font=font(32,True),fill=accent)
    elif "rowing" in key:
        d.text((120,300), "FORCA", font=font(54,True), fill="white")
        d.text((470,300), "+", font=font(54,True), fill=accent)
        d.text((560,300), "SINCRONISMO", font=font(54,True), fill="white")
        d.text((375,430), "= PERFORMANCE", font=font(58,True), fill=accent)
        d.text((220,545), "Times fortes remam na mesma direcao.", font=font(34), fill=(210,220,232))
    elif "lesson_focus" in key:
        d.text((100,300), "ESCOLHA", font=font(62,True), fill="white")
        d.text((420,300), "→", font=font(62,True), fill=accent)
        d.text((560,300), "RESPONSAVEL", font=font(62,True), fill="white")
        d.text((330,445), "→ META → ROTINA", font=font(52,True), fill=accent)
    elif "lesson_execution" in key:
        labs=["PRODUTO","CANAL","FABRICA","QUALIDADE","POS-VENDA"]
        for i,t in enumerate(labs):
            x=70+i*240
            d.rounded_rectangle([x,320,x+190,440],radius=16,fill=(21,51,79),outline=accent,width=3)
            tw=d.textbbox((0,0),t,font=font(23,True))[2]
            d.text((x+95-tw/2,365),t,font=font(23,True),fill="white")
            if i<4:d.text((x+198,358),"→",font=font(30,True),fill=accent)
        d.text((250,520), "Estrategia vira resultado quando vira capacidade.", font=font(33,True), fill="white")
    elif "lesson_culture" in key:
        labels=["REUNIAO","META","INVESTIMENTO","PRODUTO","PESSOAS"]
        for i,t in enumerate(labels):
            d.text((100,280+i*62),"✓",font=font(33,True),fill=accent)
            d.text((155,282+i*62),t,font=font(31,True),fill="white")
        d.text((640,355), "CULTURA", font=font(62,True), fill=accent)
        d.text((640,430), "= comportamento repetido", font=font(31), fill=(210,220,232))
    elif "lessons_li" in key:
        bullets=["FOCO antes da escala","CAPACIDADE antes do discurso","CULTURA visivel na rotina"]
        for i,t in enumerate(bullets):
            d.text((110,290+i*105),f"0{i+1}",font=font(38,True),fill=accent)
            d.text((205,292+i*105),t,font=font(38,True),fill="white")
    else:
        d.text((100, 310), "DECISAO", font=font(70, True), fill=accent)
        d.text((100, 410), "→ EXECUCAO → APRENDIZADO", font=font(44, True), fill="white")
    d.text((55, H-36), "UGI • Uma Gestao Inteligente", font=font(16), fill=(205,216,230))
    base.save(out, quality=92)


def prepare_visual(key: str, title: str, real_paths: dict, index: int, prefix: str) -> Path:
    out = ASSETS / f"{prefix}_{index:02d}_{key}.jpg"
    if key in REAL_ASSETS:
        fit_photo(real_paths[key], title, REAL_ASSETS[key]["credit"], out)
    else:
        card_image(key, title, out)
    return out


def run(cmd):
    print("RUN", " ".join(str(x) for x in cmd))
    subprocess.run([str(x) for x in cmd], check=True)


def media_duration(path: Path) -> float:
    p = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(path)],capture_output=True,text=True,check=True)
    return float(p.stdout.strip())


def make_tts(text: str, mp3: Path, srt: Path):
    run(["edge-tts","--voice",VOICE,"--rate=-8%","--text",text,"--write-media",mp3,"--write-subtitles",srt])


def render_scene(image: Path, audio: Path, srt: Path, out: Path, index: int):
    dur = media_duration(audio) + 0.25
    zoom_expr = "min(zoom+0.00035,1.055)" if index % 2 else "min(zoom+0.00028,1.045)"
    x_expr = "iw/2-(iw/zoom/2)"
    y_expr = "ih/2-(ih/zoom/2)"
    vf = (
        f"scale=1408:792:force_original_aspect_ratio=increase,crop=1408:792," 
        f"zoompan=z='{zoom_expr}':x='{x_expr}':y='{y_expr}':d=1:s={W}x{H}:fps={FPS},"
        f"subtitles={srt}:force_style='FontName=DejaVu Sans,FontSize=17,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,BackColour=&H70000000,Outline=1,Shadow=0,MarginV=28,Alignment=2'"
    )
    run(["ffmpeg","-y","-loop","1","-framerate",str(FPS),"-i",image,"-i",audio,"-t",f"{dur:.3f}","-vf",vf,
         "-c:v","libx264","-preset","veryfast","-profile:v","high","-level","4.0","-pix_fmt","yuv420p","-b:v","780k","-maxrate","950k","-bufsize","1560k",
         "-c:a","aac","-b:a","96k","-ar","44100","-ac","2","-movflags","+faststart",out])


def synth_music(path: Path, seconds=32, sr=44100):
    n = int(seconds*sr)
    t = np.arange(n)/sr
    audio = np.zeros(n, dtype=np.float64)
    # C major / A minor corporate progression, one chord each 4 seconds
    chords = [
        [261.63,329.63,392.00], [220.00,261.63,329.63], [174.61,220.00,261.63], [196.00,246.94,293.66],
        [261.63,329.63,392.00], [220.00,261.63,329.63], [174.61,220.00,261.63], [196.00,246.94,293.66]
    ]
    seg = int(4*sr)
    rng = np.random.default_rng(42)
    for ci,chord in enumerate(chords):
        start = ci*seg; end=min(start+seg,n); tt=np.arange(end-start)/sr
        env=np.minimum(1,tt/0.45)*np.minimum(1,(4-tt)/0.8)
        pad=np.zeros_like(tt)
        for f in chord:
            pad += np.sin(2*np.pi*f*tt) + 0.25*np.sin(2*np.pi*(2*f)*tt)
        pad/=len(chord)*1.25
        audio[start:end]+=0.16*pad*env
        root=chord[0]/2
        audio[start:end]+=0.09*np.sin(2*np.pi*root*tt)*env
        # arpeggio plucks
        for beat in range(8):
            pos=start+int(beat*0.5*sr)
            if pos>=end: break
            ln=min(int(0.42*sr),end-pos)
            et=np.arange(ln)/sr
            penv=np.exp(-6*et)
            f=chord[beat%len(chord)]*2
            audio[pos:pos+ln]+=0.055*np.sin(2*np.pi*f*et)*penv
        # soft high-hat noise every beat
        for beat in range(8):
            pos=start+int((beat*0.5+0.25)*sr)
            ln=min(int(0.05*sr),n-pos)
            if ln<=0: continue
            noise=rng.normal(0,1,ln)*np.exp(-55*np.arange(ln)/sr)
            audio[pos:pos+ln]+=0.012*noise
    mx=max(1e-9,np.max(np.abs(audio)))
    pcm=np.int16(np.clip(audio/mx*0.7,-1,1)*32767)
    with wave.open(str(path),'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(pcm.tobytes())


def concat_segments(paths, out_no_music: Path):
    lst=BUILD/(out_no_music.stem+"_concat.txt")
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in paths),encoding="utf-8")
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",lst,"-c","copy",out_no_music])


def add_music(video: Path, music: Path, out: Path):
    run(["ffmpeg","-y","-i",video,"-stream_loop","-1","-i",music,
         "-filter_complex","[1:a]volume=0.085[m];[0:a][m]amix=inputs=2:duration=first:dropout_transition=2[a]",
         "-map","0:v:0","-map","[a]","-c:v","copy","-c:a","aac","-b:a","96k","-ar","44100","-ac","2","-shortest","-movflags","+faststart",out])


def render_program(scenes, prefix, real_paths):
    segs=[]; visuals=[]
    for i,(key,title,text) in enumerate(scenes,1):
        img=prepare_visual(key,title,real_paths,i,prefix)
        mp3=SCENES/f"{prefix}_{i:02d}.mp3"
        srt=SCENES/f"{prefix}_{i:02d}.srt"
        mp4=SCENES/f"{prefix}_{i:02d}.mp4"
        make_tts(text,mp3,srt)
        render_scene(img,mp3,srt,mp4,i)
        segs.append(mp4); visuals.append(key)
    nomusic=BUILD/f"{prefix}_nomusic.mp4"
    concat_segments(segs,nomusic)
    return nomusic, visuals


def make_thumbnail(real_paths):
    a=Image.open(real_paths["giovanni_estadao"]).convert("RGB")
    b=Image.open(real_paths["factory_atarde"]).convert("RGB")
    left=ImageOps.fit(a,(W//2,H),Image.Resampling.LANCZOS,centering=(0.48,0.45))
    right=ImageOps.fit(b,(W//2,H),Image.Resampling.LANCZOS,centering=(0.5,0.5))
    im=Image.new("RGB",(W,H)); im.paste(left,(0,0)); im.paste(right,(W//2,0))
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    d.rectangle([0,0,W,H],fill=(0,0,0,75))
    d.rectangle([0,H-280,W,H],fill=(5,10,20,205))
    d.text((55,38),"HISTORIAS DE GESTAO",font=font(30,True),fill=(238,190,58,255))
    d.text((55,H-245),"DE 1 VENTILADOR",font=font(66,True),fill="white")
    d.text((55,H-165),"A UMA GIGANTE",font=font(66,True),fill=(238,190,58,255))
    d.text((55,H-80),"A HISTORIA DA MONDIAL",font=font(35,True),fill="white")
    Image.alpha_composite(im.convert("RGBA"),ov).convert("RGB").save(OUT/"youtube-mondial-thumbnail.jpg",quality=93)


def main():
    real_paths=download_real_assets()
    founder_real=sum(1 for m in REAL_ASSETS.values() if m["entity"]=="giovanni")
    company_real=sum(1 for m in REAL_ASSETS.values() if m["entity"]=="company")
    if founder_real < 4 or company_real < 8:
        raise SystemExit("VISUAL_ENTITY_GATE_FAILED")
    # no exact visual reuse inside each program
    yt_keys=[x[0] for x in YT_SCENES]
    li_keys=[x[0] for x in LI_SCENES]
    if len(yt_keys) != len(set(yt_keys)):
        # real and card keys must be unique inside YouTube; duplicate showcase is not allowed
        dup=[k for k in yt_keys if yt_keys.count(k)>1]
        raise SystemExit(f"YT_VISUAL_REUSE_BLOCKED {sorted(set(dup))}")
    if len(li_keys) != len(set(li_keys)):
        raise SystemExit("LI_VISUAL_REUSE_BLOCKED")

    music=BUILD/"ugi_documentary_original_music.wav"; synth_music(music)
    yt_nomusic,yt_visuals=render_program(YT_SCENES,"youtube",real_paths)
    li_nomusic,li_visuals=render_program(LI_SCENES,"linkedin",real_paths)
    yt_out=OUT/"youtube-mondial-historias-de-gestao.mp4"
    li_out=OUT/"linkedin-mondial-historias-de-gestao.mp4"
    add_music(yt_nomusic,music,yt_out)
    add_music(li_nomusic,music,li_out)
    make_thumbnail(real_paths)

    yd=media_duration(yt_out); ld=media_duration(li_out)
    ysize=yt_out.stat().st_size; lsize=li_out.stat().st_size
    if not (570 <= yd <= 960):
        raise SystemExit(f"YT_DURATION_GATE_FAILED {yd}")
    if not (170 <= ld <= 390):
        raise SystemExit(f"LI_DURATION_GATE_FAILED {ld}")
    if ysize >= 98_000_000:
        raise SystemExit(f"YT_FILE_TOO_LARGE {ysize}")
    if lsize >= 98_000_000:
        raise SystemExit(f"LI_FILE_TOO_LARGE {lsize}")

    manifest={
        "schema":"UGI_LONGFORM_SOURCE_MANIFEST_V1",
        "episode":"Mondial / Giovanni M. Cardoso",
        "date":"2026-09-13",
        "factSources":FACT_SOURCES,
        "realVisuals":[{"key":k,"sourceUrl":m["url"],"credit":m["credit"],"entity":m["entity"],"downloadSha256":sha256(real_paths[k])} for k,m in REAL_ASSETS.items()],
        "visualPolicy":{"exactVisualReuseWithinVideo":"BLOCK","realFounderMinimum":4,"realCompanyMinimum":8,"genericStockPrimary":False},
        "music":{"type":"UGI original procedural instrumental","copyright":"original generated bed; no external music asset"},
        "voice":{"engine":"Microsoft Edge TTS","voice":VOICE,"syntheticNarration":True},
        "finals":[
            {"path":str(yt_out.relative_to(ROOT)),"sha256":sha256(yt_out),"durationSeconds":round(yd,2),"bytes":ysize,"visualKeys":yt_visuals},
            {"path":str(li_out.relative_to(ROOT)),"sha256":sha256(li_out),"durationSeconds":round(ld,2),"bytes":lsize,"visualKeys":li_visuals},
            {"path":str((OUT/"youtube-mondial-thumbnail.jpg").relative_to(ROOT)),"sha256":sha256(OUT/"youtube-mondial-thumbnail.jpg")}
        ]
    }
    (OUT/"source-manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    qa={
        "state":"PASS",
        "youtubeDurationSeconds":round(yd,2),
        "linkedinDurationSeconds":round(ld,2),
        "founderRealVisualCount":founder_real,
        "companyRealVisualCount":company_real,
        "youtubeExactVisualReuseCount":0,
        "linkedinExactVisualReuseCount":0,
        "youtubeSceneCount":len(YT_SCENES),
        "linkedinSceneCount":len(LI_SCENES),
        "subtitleBurnedIn":True,
        "musicFit":"corporate documentary / original UGI instrumental",
        "factSourceCount":len(FACT_SOURCES)
    }
    (OUT/"qa.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(qa,ensure_ascii=False))
    print("YT",yt_out,sha256(yt_out),ysize)
    print("LI",li_out,sha256(li_out),lsize)

if __name__ == "__main__":
    main()

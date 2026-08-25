from __future__ import annotations
import hashlib, json, os, subprocess
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

BASE=os.environ['UGI_BASE_URL'].rstrip('/')
KEY=os.environ['UGI_LOLA_COMMAND_KEY']
OUT=Path('generated/commerce/premium-v6'); OUT.mkdir(parents=True,exist_ok=True)
RECEIPT=Path('control-plane/commerce-receipts/ugi-premium-v6-store-publish.json')
W,H=A4
NAVY=HexColor('#071E2E'); GOLD=HexColor('#E8A51A'); CREAM=HexColor('#F6F1E7'); WHITE=HexColor('#FFFFFF'); INK=HexColor('#16222B'); MUTED=HexColor('#6F7B83'); BLUE=HexColor('#DDEAF4'); GREEN=HexColor('#DDEFE4'); YELLOW=HexColor('#F6EBCB'); RED=HexColor('#F3DDDA'); TEAL=HexColor('#DCEFEF'); LIGHT=HexColor('#F5F7F8')
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'; bold='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
pdfmetrics.registerFont(TTFont('UGI',font)); pdfmetrics.registerFont(TTFont('UGI-Bold',bold))

DOCS=[
 {'materialId':'UGI-MAT-GOV-IA-20260825','productId':'UGI-PROD-GOV-IA-20260825','slug':'governanca-ia','title':'Kit de Governança de IA para Gestores','cover1':'GOVERNANÇA','cover2':'DE IA','subtitle':'Controle sem travar a velocidade. Dê autonomia com responsabilidade, evidência e revisão humana.','result':'Mapa de risco + nível de autonomia + responsável humano + regra mínima + checklist de dados + ritual semanal pronto.','price':14.90,'theme':'governança de IA e responsabilidade do gestor','problem':'equipes usam IA sem critérios claros de risco, revisão humana, dados sensíveis ou responsabilidade final','solution':'kit premium para gestores definirem limites, revisão humana, accountability e implantação segura de IA','code':'UGI-KIT-GOV-IA-001','pages':[
  ('Como usar este kit','Uma primeira vitória real',['Escolha 1 uso real de IA.','Classifique o risco por impacto, reversibilidade e dados.','Defina autonomia.','Nomeie o responsável humano.','Registre a regra mínima.'],'PAPEL: atue como Chief of Staff de governança de IA. CONTEXTO: processo [processo], objetivo [objetivo], ferramenta [ferramenta]. TAREFA: liste decisões, dados usados, riscos, responsável humano e evidências necessárias. SAÍDA: tabela única para revisão em 10 minutos.'),
  ('Situação real','IA em todo lugar, responsabilidade em lugar nenhum',['Velocidade: a equipe adota rápido.','Opacidade: ninguém sabe onde revisar.','Risco: erro vira decisão real.','Pergunta-chave: quem responde se a recomendação estiver errada?'],'PAPEL: atue como auditor operacional. Identifique autonomia sem regra, dado sem proteção, decisão sem dono e saída sem revisão. SAÍDA: 5 riscos priorizados + evidência + ação em 48h.'),
  ('Modelo UGI','Governança em quatro camadas',['Propósito: para que a IA pode ser usada?','Dados: o que ela pode acessar?','Decisão: o que exige revisão humana?','Evidência: como provar o que aconteceu?'],'Escreva uma regra de 1 página com propósito autorizado, dados permitidos, decisões que exigem revisão e evidências que precisam ser registradas.'),
  ('Matriz UGI','Risco x autonomia',['Baixo risco + reversível: automatizar.','Médio risco: automatizar com log e revisão.','Alto risco: apoio apenas.','Alto impacto + baixa reversibilidade: decisão humana obrigatória.'],'Classifique impacto 1-5, reversibilidade 1-5, sensibilidade 1-5 e exposição 1-5. SAÍDA: zona da matriz + autonomia + responsável + evidência mínima.'),
  ('Escada de revisão','Nem toda saída precisa do mesmo controle',['N0 AUTO: baixo impacto e reversível.','N1 AMOSTRA: revisar parte das saídas.','N2 HUMANO: toda saída aprovada.','N3 ESPECIALISTA: tema regulado ou crítico.','N4 PROIBIDO: uso incompatível com o risco.'],'Escolha N0-N4 usando impacto, reversibilidade, sensibilidade e exposição. SAÍDA: nível + quem revisa + frequência + evidência + gatilho de escalonamento.'),
  ('Dados','Semáforo de sensibilidade',['VERDE: dados públicos ou internos sem impacto relevante.','AMARELO: dados internos, pessoais básicos ou estratégicos limitados.','VERMELHO: credenciais, saúde, financeiro, jurídico ou segredo comercial.','Regra: quanto mais sensível, menor a autonomia e maior a evidência.'],'Atue como privacy reviewer. Classifique cada dado em verde, amarelo ou vermelho; indique minimização, anonimização ou bloqueio. SAÍDA: tabela + risco residual + decisão recomendada.'),
  ('Responsabilidade','Quem decide, quem revisa, quem responde',['IA: recomenda, resume e sinaliza.','Gestor: decide e prioriza.','Especialista: valida quando o risco exigir.','Toda decisão relevante precisa de dono explícito.'],'Monte a matriz de responsabilidade: quem pede análise, quem revisa, quem decide, quem pode bloquear e quem responde por incidente.'),
  ('Guardrails','Prompts que reduzem respostas perigosas',['Separar fatos, inferências e recomendações.','Declarar dados faltantes.','Construir contra-argumento.','Escalar decisões que exigem revisão humana.'],'Antes de responder: separe fatos de inferências; declare dados faltantes; cite incertezas; mostre alternativa; identifique revisão humana; não invente fonte, número ou política.'),
  ('Qualidade','Auditoria de confiança em 5 perguntas',['Qual afirmação depende de fonte externa?','Que número precisa ser verificado?','Que parte é inferência?','O que mudaria a recomendação?','Qual erro seria mais caro?'],'Atue como revisor cético. Procure alucinação, falsa precisão, omissão de contexto, conflito de interesse e risco de decisão. SAÍDA: achado + severidade + como verificar + versão corrigida.'),
  ('Ferramentas','Checklist rápido de fornecedor',['Dados: retenção, treinamento, localização.','Acesso: SSO, perfis, logs, revogação.','Contrato: responsabilidade, SLA, suporte.','Modelo: limitações, atualização, explicabilidade.','Saída: exportação, deleção, evidência.'],'Crie uma due diligence do fornecedor [nome] para o caso de uso [uso]. SAÍDA: checklist priorizado + red flags + evidências mínimas.'),
  ('Ritual semanal','15 minutos de governança',['0-3 min: usos novos.','3-6: incidentes.','6-9: métricas.','9-12: regras.','12-15: decisões.'],'Atue como secretário da governança. ENTRADAS: novos usos, incidentes, métricas e dúvidas. SAÍDA: 3 decisões, 3 responsáveis, 3 prazos e 1 regra a atualizar.'),
  ('Prompt UGI mestre','Copiloto de governança',['Classifique risco e autonomia.','Identifique dados sensíveis.','Defina revisão humana.','Nomeie responsável.','Proponha evidências e gatilhos.'],'PAPEL: assessor executivo de governança de IA. CONTEXTO: processo [processo], ferramenta [ferramenta], objetivo [objetivo], dados [dados], impacto [impacto]. SAÍDA: resumo, matriz de risco, autonomia N0-N4, controles, decisão e próximos passos.'),
  ('Incidente','O que fazer quando a IA erra',['Conter o uso afetado.','Preservar logs, prompt, entrada e saída.','Avaliar impacto real.','Corrigir regra, acesso ou processo.','Transformar incidente em controle novo.'],'CONTEXTO: incidente [descrição]. Separe fato, hipótese e impacto; indique contenção, evidências, responsáveis, comunicação e controle preventivo. SAÍDA: plano de 24h + plano de 7 dias.'),
  ('Roadmap','30 dias para sair do improviso',['Semana 1: mapear usos, riscos e responsáveis.','Semana 2: controlar dados, revisão e logs.','Semana 3: treinar gestores e usuários-chave.','Semana 4: medir erros, ganhos e exceções.'],'Atue como PMO de governança. Adapte o roadmap de 30 dias. SAÍDA: entregável semanal + responsável + evidência + dependência + risco de atraso.'),
  ('Dashboard','30 dias de governança',['Usos ativos.','Usos com dono.','Usos com log.','Incidentes.','Cobertura de revisão, dados classificados e treino de gestores.'],'ENTRADAS: usos, incidentes, erros, revisões, ganhos de tempo e exceções. SAÍDA: 3 controles que funcionam, 3 lacunas e 3 regras que podem ser simplificadas.'),
  ('Implementação','7 dias para virar regra operacional',['Dia 1: inventário.','Dia 2: risco.','Dia 3: dados.','Dia 4: revisão.','Dia 5: responsável.','Dia 6: teste.','Dia 7: ritual.'],'Adapte os 7 dias para [função], equipe [tamanho], uso [uso], risco [risco]. RESTRIÇÃO: cada dia no máximo 30 min. SAÍDA: ação + resultado + responsável + evidência.'),
  ('Referências e continuidade','Use, prove valor, evolua',['NIST AI RMF — governança e gestão de riscos.','ISO/IEC 42001 — sistema de gestão para IA.','OECD AI Principles — transparência, robustez e accountability.','Microsoft Responsible AI Standard.','PMI — governança e responsabilidade em decisões.'],'REGRA FINAL UGI: se a IA pode influenciar uma decisão real, a responsabilidade humana precisa estar explícita.') ]},
 {'materialId':'UGI-MAT-JULGAMENTO-IA-20260826','productId':'UGI-PROD-JULGAMENTO-IA-20260826','slug':'decisao-humana-ia','title':'Framework de Decisão Humana na Era da IA','cover1':'DECISÃO','cover2':'HUMANA + IA','subtitle':'Use a IA para pensar melhor sem terceirizar julgamento, trade-offs e responsabilidade.','result':'Mapa de delegação + Score de Julgamento + decision memo + contraponto + ritual de revisão + plano de 7 dias.','price':14.90,'theme':'julgamento humano, accountability e liderança com IA','problem':'gestores delegam à IA análise e decisão sem distinguir onde automação ajuda e onde julgamento humano continua indispensável','solution':'framework premium para decidir o que delegar à IA, o que manter humano e como revisar decisões apoiadas por automação','code':'UGI-KIT-DECISAO-HUMANA-001','pages':[
  ('Como usar este kit','Decida melhor, não apenas mais rápido',['Escolha uma decisão real.','Separe análise de decisão.','Meça impacto e reversibilidade.','Teste a recomendação.','Registre a razão da escolha.'],'Atue como assessor executivo. Organize a decisão em fatos, hipóteses, dados faltantes, opções, consequências e perguntas críticas sem escolher ainda.'),
  ('Situação real','A IA recomenda. Quem decide?',['A IA compara mais opções em menos tempo.','O líder assume trade-offs, contexto e consequências.','Risco: terceirizar julgamento para um sistema que não vive as consequências.'],'Identifique quais partes podem ser apoiadas por IA e quais exigem julgamento humano. SAÍDA: fatos, incertezas, trade-offs, stakeholders e ponto exato de decisão humana.'),
  ('Mapa UGI','O que delegar e o que manter humano',['Baixo impacto + reversível: automatize mais.','Impacto médio: IA + revisão.','Alto impacto: humano decide.','Baixa reversibilidade: escalar.'],'Avalie impacto, reversibilidade, contexto humano, risco reputacional e dados. SAÍDA: o que delegar, revisar, decidir pessoalmente e nunca automatizar.'),
  ('Método UGI','Score de julgamento',['Impacto — peso 3.','Baixa reversibilidade — peso 3.','Contexto humano — peso 2.','Incerteza — peso 2.','Accountability — peso 2.'],'Dê notas 1-5 para os cinco critérios e mostre o cálculo. Quanto maior o score, maior a exigência de decisão humana.'),
  ('Julgamento','Checklist antes de dizer sim',['Entendo as premissas?','Consigo explicar sem citar apenas a IA?','Há contexto humano invisível ao modelo?','Que evidência mudaria minha decisão?','Quem assume a consequência?'],'Antes de recomendar, responda às 5 perguntas. Se qualquer uma não puder ser respondida, interrompa a recomendação final e liste o que falta.'),
  ('Escalonamento','Quando a decisão sobe de nível',['N1 rotina: gestor local.','N2 gestor: revisão explícita.','N3 diretor: trade-off entre áreas ou orçamento.','N4 especialista: jurídico, compliance, finanças, pessoas.','N5 executivo: alto impacto ou baixa reversibilidade.'],'Escolha N1-N5 e explique por quê. SAÍDA: nível + quem decide + quem consultar + prazo + condição para descer de nível.'),
  ('Decision memo','Uma página para decisões difíceis',['Decisão: o que precisa ser decidido?','Fatos: o que sabemos?','Hipóteses: o que assumimos?','Opções: alternativas.','Trade-off: o que ganhamos e perdemos?','Dono: quem decide e responde?'],'Gere um decision memo de 1 página: decisão, fatos, hipóteses, opções, trade-offs, recomendação, risco, dado faltante, dono e próxima revisão.'),
  ('Contraponto','Faça a IA discordar de você',['Hipótese A: minha decisão atual.','Hipótese B: melhor argumento contra ela.','Teste premissas frágeis.','Procure cenários de falha.'],'Minha decisão atual é [decisão]. Construa o melhor argumento contra ela. Mostre 3 premissas frágeis, 2 cenários de falha, 1 dado decisivo e uma alternativa plausível.'),
  ('Accountability','Quem responde pelo resultado',['IA: recomenda.','Analista: valida dados e premissas.','Gestor: escolhe e decide.','Executivo responsável: responde por alto impacto.'],'Identifique quem recomenda, decide, executa, pode vetar e responde pelo resultado. SAÍDA: matriz simples + lacunas de autoridade.'),
  ('Quando discordar','A recomendação parece boa, mas você não compra a ideia',['Pause: não aceite nem rejeite por impulso.','Localize onde discorda.','Teste evidência e cenário alternativo.','Decida e registre a razão humana.'],'Decomponha a divergência em dados, premissas, valores, risco e contexto. SAÍDA: verificável + julgamento + teste mínimo para reduzir incerteza.'),
  ('Ritual semanal','Revisão de decisões em 15 minutos',['0-3: decisões.','3-6: premissas.','6-9: resultados.','9-12: erros.','12-15: ajustes.'],'Diferencie erro de execução, erro de premissa, azar e decisão ruim. SAÍDA: 3 aprendizados + 3 regras para a próxima semana.'),
  ('Prompt UGI mestre','Conselheiro de decisão',['Separe fatos, hipóteses e valores.','Identifique dados faltantes.','Avalie impacto e reversibilidade.','Construa contra-argumento.','Indique trade-offs e escalonamento.'],'Atue como assessor executivo de decisão. SAÍDA: memo + score de julgamento + recomendação + contra-argumento + decisão que continua sendo humana.'),
  ('Incerteza','Decidir quando você nunca terá todos os dados',['70%+: decida se reversível.','40-70%: teste antes de escalar.','<40%: reduza exposição e busque informação crítica.'],'Estime o que sabemos, o que não sabemos e o custo de esperar. SAÍDA: decidir agora / testar / esperar + experimento mínimo + gatilho de revisão + limite de perda.'),
  ('Reuniões','Use IA antes; julgamento humano durante',['Antes: IA resume, compara e levanta riscos.','Durante: time traz contexto, trade-offs e discordância.','Depois: dono registra decisão, razão e prazo de revisão.'],'Prepare um pre-read de 1 página com fatos, hipóteses, opções, riscos, dado faltante e 5 perguntas difíceis. NÃO tome a decisão.'),
  ('Dashboard','30 dias de qualidade decisória',['Decisões registradas.','Decisões revistas.','Decisões revertidas.','Decisões sem dono.','Cobertura de memo, premissa, dono e revisão.'],'Identifique onde decidimos cedo demais, tarde demais ou sem dono. SAÍDA: 3 padrões + 3 mudanças no processo + 1 decisão a revisitar.'),
  ('Implementação','7 dias para melhorar a qualidade das decisões',['Dia 1: escolha.','Dia 2: fatos.','Dia 3: hipóteses.','Dia 4: trade-offs.','Dia 5: dono.','Dia 6: revisão.','Dia 7: ritual.'],'Adapte os 7 dias para [função], [tipo de decisão], equipe [tamanho] e problema [problema]. Cada dia no máximo 30 minutos.'),
  ('Referências e continuidade','Use, revise, aprenda',['Daniel Kahneman — Thinking, Fast and Slow.','Annie Duke — Thinking in Bets.','Gary Klein — Recognition-Primed Decision.','NIST AI RMF.','PMI — trade-offs, governança e ownership.'],'REGRA FINAL UGI: a IA pode ampliar a análise. O líder continua responsável pelo trade-off e pela consequência.') ]}
]

def pstyle(size=9,leading=12,color=INK,align=0,bold=False):
 return ParagraphStyle('x',fontName='UGI-Bold' if bold else 'UGI',fontSize=size,leading=leading,textColor=color,alignment=align)
def para(c,text,x,y,w,style):
 p=Paragraph(text,style); _,h=p.wrap(w,H); p.drawOn(c,x,y-h); return h

def header(c,kicker,title,page):
 c.setFillColor(NAVY); c.rect(0,H-31*mm,W,31*mm,0,1); c.setFillColor(GOLD); c.setFont('UGI-Bold',8); c.drawString(14*mm,H-12.7*mm,kicker.upper());
 c.setFillColor(WHITE); s=20
 while pdfmetrics.stringWidth(title.upper(),'UGI-Bold',s)>W-58*mm and s>12:s-=.5
 c.setFont('UGI-Bold',s); c.drawString(14*mm,H-22*mm,title.upper()); c.setFillColor(GOLD); c.roundRect(W-23*mm,H-18*mm,9*mm,9*mm,2*mm,0,1); c.setFillColor(NAVY); c.setFont('UGI-Bold',8); c.drawCentredString(W-18.5*mm,H-14.8*mm,str(page))
def footer(c,page,code):
 c.setStrokeColor(HexColor('#D8DEE2')); c.line(14*mm,14*mm,W-14*mm,14*mm); c.setFillColor(MUTED); c.setFont('UGI',6.2); c.drawString(14*mm,9*mm,'UGI | UMA GESTÃO INTELIGENTE'); c.drawRightString(W-14*mm,9*mm,f'PREMIUM V6 | {page}/18 | {code}')
def card(c,x,y,w,h,fill=WHITE):
 c.setFillColor(fill); c.setStrokeColor(HexColor('#D8DEE2')); c.roundRect(x,y,w,h,4*mm,1,1)
def icon(c,cx,cy,kind):
 c.setFillColor(CREAM); c.circle(cx,cy,6*mm,0,1); c.setStrokeColor(NAVY); c.setLineWidth(1.3)
 if kind%3==0: c.circle(cx,cy,3*mm,1,0); c.line(cx+2*mm,cy+2*mm,cx+5*mm,cy+5*mm)
 elif kind%3==1: c.rect(cx-2.5*mm,cy-3*mm,5*mm,6*mm,1,0); c.line(cx-1.3*mm,cy,cx+1.3*mm,cy)
 else: c.roundRect(cx-3*mm,cy-2.5*mm,6*mm,5*mm,1*mm,1,0); c.arc(cx-2*mm,cy,cx+2*mm,cy+5*mm,0,180)
def prompt(c,text):
 card(c,18*mm,27*mm,165*mm,47*mm,CREAM); c.setFillColor(NAVY); c.setFont('UGI-Bold',8); c.drawString(24*mm,63*mm,'PROMPT UGI — APLICAÇÃO IMEDIATA'); icon(c,170*mm,62*mm,1); para(c,text,24*mm,58*mm,138*mm,pstyle(7.7,10.5))

def build(doc,path):
 c=canvas.Canvas(str(path),pagesize=A4)
 c.setFillColor(NAVY); c.rect(0,0,W,H,0,1); c.setFillColor(GOLD); c.setFont('UGI-Bold',11); c.drawString(14*mm,H-24*mm,'KIT UGI'); c.setFillColor(WHITE); c.setFont('UGI-Bold',26); c.drawString(14*mm,H-42*mm,doc['cover1']); c.setFillColor(GOLD); c.drawString(14*mm,H-56*mm,doc['cover2']); para(c,doc['subtitle'],14*mm,H-66*mm,105*mm,pstyle(11,16,HexColor('#E8EEF1'))); card(c,14*mm,34*mm,W-28*mm,35*mm,CREAM); c.setFillColor(NAVY); c.setFont('UGI-Bold',9); c.drawString(20*mm,60*mm,'RESULTADO EM 30 MINUTOS'); para(c,doc['result'],20*mm,55*mm,W-40*mm,pstyle(9.2,13)); c.setFillColor(WHITE); c.setFont('UGI-Bold',7.2); c.drawString(14*mm,14*mm,'UGI | UMA GESTÃO INTELIGENTE'); c.setFillColor(GOLD); c.drawRightString(W-14*mm,14*mm,doc['code']); c.showPage()
 fills=[BLUE,GREEN,YELLOW,CREAM,TEAL,LIGHT,RED]
 for i,(k,t,bul,pmt) in enumerate(doc['pages'],start=2):
  header(c,k,t,i); y=195*mm
  for j,b in enumerate(bul[:6]):
   h=23*mm if len(b)<80 else 27*mm; card(c,18*mm,y-h,165*mm,h,fills[(j+i)%len(fills)]); icon(c,29*mm,y-h/2,j+i); c.setFillColor(NAVY); c.setFont('UGI-Bold',8); c.drawString(41*mm,y-8*mm,f'{j+1:02d}'); para(c,b,52*mm,y-6*mm,120*mm,pstyle(8.4,11,bold=j==0)); y-=h+5*mm
  prompt(c,pmt); footer(c,i,doc['code']); c.showPage()
 c.save()

def curl_json(method,url,payload=None,binary=None):
 args=['curl','--fail-with-body','--silent','--show-error','--connect-timeout','15','--max-time','120','-X',method,url,'-H',f'x-lola-command-key: {KEY}']
 if payload is not None:
  p=OUT/'payload.json'; p.write_text(json.dumps(payload,ensure_ascii=False),encoding='utf-8'); args += ['-H','Content-Type: application/json','--data-binary',f'@{p}']
 if binary: args += ['-H','Content-Type: application/pdf','--data-binary',f'@{binary}']
 return json.loads(subprocess.check_output(args,text=True))

results=[]
for d in DOCS:
 pdf=OUT/f"{d['slug']}-premium-v6.pdf"; build(d,pdf); checksum=hashlib.sha256(pdf.read_bytes()).hexdigest()
 mr=curl_json('POST',BASE+'/api/materials',{'materialId':d['materialId'],'title':d['title'],'theme':d['theme'],'problem':d['problem'],'solution':d['solution'],'version':'PREMIUM_V6','qualityStatus':'PASS','deliveryEnabled':True,'assetReady':False,'mimeType':'application/pdf','checksum':checksum})
 ar=curl_json('POST',BASE+f"/api/materials/{d['materialId']}/asset",binary=str(pdf))
 pr=curl_json('POST',BASE+'/api/products',{'productId':d['productId'],'materialId':d['materialId'],'title':d['title'],'price':d['price'],'currency':'BRL','active':True,'description':d['solution']})
 results.append({'slug':d['slug'],'materialId':d['materialId'],'productId':d['productId'],'title':d['title'],'price':d['price'],'pdf':str(pdf),'bytes':pdf.stat().st_size,'sha256':checksum,'materialCreated':mr.get('ok') is True,'assetUploaded':ar.get('ok') is True,'productCreated':pr.get('ok') is True})
receipt={'ok':all(r['materialCreated'] and r['assetUploaded'] and r['productCreated'] for r in results),'standard':'UGI_PREMIUM_V6','results':results}
RECEIPT.parent.mkdir(parents=True,exist_ok=True); RECEIPT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(receipt,ensure_ascii=False,indent=2))
if not receipt['ok']: raise SystemExit('PREMIUM_V6_PUBLISH_FAILED')

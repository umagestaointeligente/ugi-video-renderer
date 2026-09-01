#!/usr/bin/env python3
from __future__ import annotations
import json, os, shutil, subprocess, time
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]
ASSET=ROOT/'control-plane/platform-20260901/assets'
WORK=ROOT/'output'
PEX=(os.getenv('PEXELS_API_KEY') or '').strip(); PIX=(os.getenv('PIXABAY_API_KEY') or '').strip()
MUSIC={
 'meta':'https://assets.mixkit.co/music/479/479.mp3',
 'nvidia':'https://assets.mixkit.co/music/1167/1167.mp3',
 'apple':'https://assets.mixkit.co/music/33/33.mp3',
 'nepal':'https://assets.mixkit.co/music/634/634.mp3',
}

def maps(text): return {'instagram':text,'tiktok':text,'youtube':text}
def s(role,visual,q,overlay,support,narr): return {'role':role,'visual_intent':visual,'pexels_query':q,'overlay':maps(overlay),'support':maps(support),'narration':maps(narr)}

TOPICS=[
 {
  'id':'UGI-20260901-TT-01-META-AI-NATIVE','platform':'tiktok','filename':'tiktok-01-meta-ai-native.mp4','title':'A Meta tentou virar AI-native. O plano travou.','music':'meta',
  'scenes':[
   s('hook','modern tech company office team surprised','technology office workers','A IA ia enxugar times.','E o plano travou.','A Meta tentou redesenhar equipes inteiras ao redor de inteligência artificial. E o plano travou.'),
   s('pain','employee team meeting uncertain change','corporate team meeting','A promessa era simples.','Times menores + IA.','A ideia era reduzir camadas, formar equipes menores e usar IA para sustentar mais trabalho com menos gente.'),
   s('consequence','stressed workers looking at laptop office','office employees laptop stress','Na prática, vieram atritos.','Confiança e execução caíram.','Relatos apontaram resistência, dúvidas de produtividade, segurança e uma comunicação ruim sobre cortes.'),
   s('turn','leader explaining strategy to team screen','manager presentation team','O problema não era só a IA.','Era o desenho da mudança.','Tecnologia pode acelerar trabalho, mas não substitui contexto, processo, confiança e clareza sobre quem decide o quê.'),
   s('result','collaborative team working with AI screens','team technology collaboration','Lição de gestão:','Redesenhe o trabalho, não só o quadro.','A transformação funciona quando a empresa redesenha fluxos e responsabilidades, em vez de apenas cortar pessoas e adicionar ferramentas.'),
   s('cta','business leader modern office closing','business leadership office','IA sem gestão vira ruído.','Siga a UGI.','Se a sua empresa quer usar IA de verdade, comece pelo trabalho que precisa mudar. Siga a UGI para mais gestão aplicada.'),
  ]
 },
 {
  'id':'UGI-20260901-TT-02-NVIDIA-MEDIATEK','platform':'tiktok','filename':'tiktok-02-nvidia-mediatek.mp4','title':'Por que a Nvidia colocou US$ 3,5 bi na MediaTek?','music':'nvidia',
  'scenes':[
   s('hook','semiconductor chips futuristic data center','AI chips data center','US$ 3,5 bilhões.','Em uma empresa que ajuda clientes a criar chips próprios.','A Nvidia acabou de investir três bilhões e meio de dólares na MediaTek. E o movimento parece contraditório.'),
   s('pain','engineers designing semiconductor chips','semiconductor engineers','Big Tech quer depender menos.','Chips próprios estão crescendo.','Amazon, Google, Microsoft, OpenAI e outras empresas querem construir mais silício próprio e reduzir dependência de GPUs tradicionais.'),
   s('consequence','server racks AI infrastructure','data center server racks','Isso ameaça a Nvidia?','Sim — se ela ficar só no chip.','Se a disputa fosse apenas por uma peça, o crescimento dos chips customizados poderia tirar espaço da Nvidia.'),
   s('turn','connected technology ecosystem animation real servers','technology ecosystem servers','Então ela muda o jogo.','Integra quem poderia competir.','Ao aproximar a MediaTek do seu ecossistema e do NVLink Fusion, a Nvidia tenta continuar no centro da infraestrutura mesmo quando o chip muda.'),
   s('result','business partnership handshake technology office','technology partnership handshake','Lição estratégica:','Ecossistema > controle total.','Em alguns mercados, ser a plataforma que todos precisam usar é mais valioso do que tentar fabricar tudo sozinho.'),
   s('cta','executive technology strategy office','business strategy technology','Estratégia também é escolher onde ser indispensável.','Siga a UGI.','Siga a UGI para mais histórias de negócios transformadas em decisões práticas.'),
  ]
 },
 {
  'id':'UGI-20260901-YT-01-APPLE-SUCCESSION','platform':'youtube','filename':'youtube-01-apple-succession.mp4','title':'Tim Cook deixa o comando da Apple: o que muda agora?','music':'apple',
  'scenes':[
   s('hook','Apple style technology campus executive walking','technology campus executive','15 anos depois, a Apple troca de CEO.','Tim Cook passa o bastão.','Em primeiro de setembro, a Apple muda de CEO depois de quinze anos sob Tim Cook.'),
   s('pain','executive succession boardroom meeting','executive board meeting','Trocar o CEO de uma gigante é risco.','Especialmente no auge.','Sucessões mal preparadas podem abalar estratégia, cultura e confiança. Por isso o detalhe mais importante dessa história veio meses antes.'),
   s('consequence','company leadership transition handshake office','executive transition handshake','A mudança foi anunciada em abril.','Planejamento antes da cadeira vazia.','A Apple anunciou a transição em abril e preparou uma passagem gradual, em vez de esperar a saída para procurar um nome.'),
   s('turn','experienced engineer leader technology team','senior technology leader team','John Ternus vem de dentro.','25 anos de empresa.','John Ternus assume depois de cerca de vinte e cinco anos na Apple, carregando conhecimento de produto, cultura e operação.'),
   s('result','executive chairman boardroom leadership','boardroom leadership','Cook continua como Executive Chairman.','Continuidade sem impedir a troca.','Tim Cook não some: ele vira Executive Chairman. A estrutura preserva contexto enquanto o novo CEO assume a liderança operacional.'),
   s('cta','business succession planning team','leadership succession planning','A pergunta para qualquer gestor:','Sua empresa funciona sem você?','O melhor legado de liderança não é dependência. É um sistema capaz de continuar. Siga a UGI para mais gestão aplicada.'),
  ]
 },
 {
  'id':'UGI-20260901-YT-02-NEPAL-14MIN','platform':'youtube','filename':'youtube-02-nepal-14min.mp4','title':'14 minutos salvaram mais de 900 alunos no Nepal','music':'nepal',
  'scenes':[
   s('hook','school emergency evacuation heavy rain','school evacuation emergency','14 minutos.','Mais de 900 alunos evacuados.','No Nepal, uma escola recebeu um alerta de enchente e teve apenas quatorze minutos para agir.'),
   s('pain','river flood warning emergency landscape','flood warning river','A água vinha rápido.','A escola estava em área vulnerável.','O prédio ficava entre um rio e um canal de hidrelétrica. Esperar confirmação perfeita poderia custar vidas.'),
   s('consequence','school principal emergency bell students','school principal emergency','O diretor parou as aulas.','Sino, ônibus, rota de fuga.','O diretor interrompeu as aulas, acionou o sino, desviou ônibus que chegavam e começou a evacuação imediatamente.'),
   s('turn','students moving to higher ground emergency','students evacuation safe ground','O último ônibus passou.','Depois, a ponte cedeu.','Pouco depois da saída do último ônibus, a ponte antiga foi levada pela água. A decisão rápida mudou o resultado.'),
   s('result','crisis operations center weather maps','emergency operations data','Onde entra IA?','Previsão só vale com protocolo.','IA pode combinar clima, sensores, rotas, estoque e capacidade. Mas alerta sem autoridade para agir continua sendo só informação.'),
   s('cta','business crisis management team monitors','crisis management team','Gestão de crise começa antes da crise.','Siga a UGI.','Mapeie sinais, responsáveis e decisões antes do caos. Siga a UGI para transformar tecnologia em gestão prática.'),
  ]
 }
]

def get(url,**kw):
 for n in range(3):
  try:
   r=requests.get(url,timeout=(10,120),**kw); r.raise_for_status(); return r
  except Exception:
   if n==2: raise
   time.sleep(2*(n+1))

def download(url,path):
 r=get(url,stream=True); path.parent.mkdir(parents=True,exist_ok=True)
 with open(path,'wb') as f:
  for c in r.iter_content(1024*1024):
   if c:f.write(c)
 if path.stat().st_size<50000: raise RuntimeError(f'download too small {url}')

def acquire(scenes):
 media=WORK/'media'; shutil.rmtree(media,ignore_errors=True); media.mkdir(parents=True,exist_ok=True); used=set()
 for i,sc in enumerate(scenes,1):
  chosen=None
  queries=[sc['pexels_query'],sc['visual_intent']]
  if PEX:
   for q in queries:
    data=get('https://api.pexels.com/v1/videos/search',headers={'Authorization':PEX},params={'query':q,'orientation':'portrait','per_page':15}).json()
    for v in data.get('videos',[]):
     key=f"pexels:{v.get('id')}"
     if key in used: continue
     fs=[x for x in v.get('video_files',[]) if x.get('file_type')=='video/mp4' and x.get('link')]
     if fs:
      fs.sort(key=lambda x:(int(x.get('height') or 0)>int(x.get('width') or 0),int(x.get('height') or 0)),reverse=True)
      chosen=(key,fs[0]['link']); break
    if chosen: break
  if not chosen and PIX:
   for q in queries:
    data=get('https://pixabay.com/api/videos/',params={'key':PIX,'q':q,'video_type':'film','safesearch':'true','per_page':20}).json()
    for v in data.get('hits',[]):
     key=f"pixabay:{v.get('id')}"
     if key in used: continue
     x=(v.get('videos') or {}).get('large') or (v.get('videos') or {}).get('medium') or {}
     if x.get('url'): chosen=(key,x['url']); break
    if chosen: break
  if not chosen: raise RuntimeError(f'no media scene {i}')
  target=media/f'scene-{i}.mp4'; download(chosen[1],target); used.add(chosen[0])

def run_topic(topic):
 shutil.rmtree(WORK,ignore_errors=True); WORK.mkdir(parents=True,exist_ok=True)
 acquire(topic['scenes'])
 music=WORK/f"music-{topic['music']}.mp3"; download(MUSIC[topic['music']],music)
 payload={'scenes':topic['scenes'],'cta':'Siga a UGI para mais gestão aplicada.'}
 env=os.environ.copy(); env.update({
   'VIDEO_TITLE':topic['title'],'VIDEO_RENDER_ID':'r-20260901-'+topic['id'].lower(),
   'VIDEO_CONTENT_ID':topic['id'],'VIDEO_EXPERIMENT_ID':'UGI-20260901-EDITORIAL-V2','VIDEO_VARIANT':'A',
   'VIDEO_COMMERCIAL_INTENT':'atracao_com_potencial_de_conversao','VIDEO_SCENES_JSON':json.dumps(payload,ensure_ascii=False),
   'VIDEO_MUSIC_FILE':str(music),'VIDEO_MUSIC_ENABLED':'true','VIDEO_MUSIC_FALLBACK_MODE':'none',
   'VIDEO_BRAND_TEXT':'UGI - UMA GESTÃO INTELIGENTE','VIDEO_SMOKE_TEST':'false'
 })
 subprocess.run(['python3','render-reel.py'],cwd=ROOT,env=env,check=True)
 source=WORK/({'tiktok':'tiktok-reel.mp4','youtube':'youtube-short.mp4'}[topic['platform']])
 if not source.exists() or source.stat().st_size<100000: raise RuntimeError(f'missing render {source}')
 ASSET.mkdir(parents=True,exist_ok=True); shutil.copy2(source,ASSET/topic['filename'])

def main():
 ASSET.mkdir(parents=True,exist_ok=True)
 for t in TOPICS: run_topic(t)
 manifest={'date':'2026-09-01','timezone':'America/Sao_Paulo','topics':[{k:v for k,v in t.items() if k!='scenes'} for t in TOPICS],
 'hardGates':{'antiRepeatDays':15,'platformSpecific':True,'malePtBrVoice':'pm_alex','musicUnique':True},
 'sources':{
  'meta':'https://www.reuters.com/technology/artificial-intelligence/how-metas-ai-workforce-transformation-plans-went-kaput-2026-08-26/',
  'nvidia':'https://www.reuters.com/world/asia-pacific/nvidia-invests-35-billion-mediatek-convertible-bonds-2026-08-31/',
  'apple':'https://www.apple.com/newsroom/2026/04/tim-cook-to-become-apple-executive-chairman-john-ternus-to-become-apple-ceo/',
  'nepal':'https://www.reuters.com/business/environment/last-minute-flood-warning-saved-over-900-nepal-students-school-head-says-2026-08-31/'}}
 (ASSET/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'ok':True,'renders':len(TOPICS)},ensure_ascii=False))

if __name__=='__main__': main()

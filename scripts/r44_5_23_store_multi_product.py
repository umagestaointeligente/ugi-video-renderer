from __future__ import annotations
import json, os, re, time
from pathlib import Path
import requests
import scripts.r44_5_18_repair_v2 as base

STATUS=Path('cloudflare/status/r44-5-23-store-multi-product.txt')
WORKER='lola-operacional-ugi'
ORIGIN='https://lola-operacional-ugi.umagestaointeligente.workers.dev'
NEW='lola-v8-r44-5-23-store-multi-product-premium-v6-2026-08-25'

PRODUCTS=[
 {'productId':'UGI-MATERIAL-PRIORIDADES-001','materialId':'UGI-KIT-PRIORIZACAO-001','slug':'priorizacao','coverKicker':'KIT PRÁTICO','coverTitle':'Priorização<br>Inteligente','coverFoot':'Decida melhor. Proteja o foco.','search':'priorização prioridades foco produtividade liderança gestão','bullets':['Filtro rápido para novas demandas','Critérios para reduzir urgência artificial','Aplicação prática no dia a dia do gestor']},
 {'productId':'UGI-PROD-GOV-IA-20260825','materialId':'UGI-MAT-GOV-IA-20260825','slug':'governanca-ia','coverKicker':'PREMIUM V6','coverTitle':'Governança<br>de IA','coverFoot':'Autonomia com responsabilidade.','search':'governança ia inteligência artificial responsabilidade risco liderança gestão','bullets':['Matriz risco × autonomia','Semáforo de dados sensíveis','Guardrails, prompts e ritual semanal']},
 {'productId':'UGI-PROD-JULGAMENTO-IA-20260826','materialId':'UGI-MAT-JULGAMENTO-IA-20260826','slug':'decisao-humana-ia','coverKicker':'PREMIUM V6','coverTitle':'Decisão<br>Humana + IA','coverFoot':'Pense melhor. Decida com clareza.','search':'decisão julgamento humano ia accountability liderança gestão','bullets':['Score UGI de Julgamento','Decision memo e contraponto','Accountability e revisão em 7 dias']},
]

def write(lines):
 STATUS.parent.mkdir(parents=True,exist_ok=True); STATUS.write_text('\n'.join(lines)+'\n',encoding='utf-8')
def headers(tok): return {'Authorization':f'Bearer {tok}'}
def fetch_live(api,h):
 r=requests.get(api+'/content/v2',headers=h,timeout=45); r.raise_for_status(); return base.extract_source(r)
def current_bindings(api,h):
 r=requests.get(api+'/deployments',headers=h,timeout=30); r.raise_for_status(); data=r.json(); rows=data.get('result') or []
 if not rows: raise RuntimeError('no current deployment')
 versions=rows[0].get('versions') or []; vid=(versions[0] if versions else {}).get('version_id')
 if not vid: raise RuntimeError('current version id missing')
 vr=requests.get(api+f'/versions/{vid}',headers=h,timeout=30); vr.raise_for_status(); return base.restored_bindings(vr.json()),vid

def top_block(src,start):
 a=src.find(start)
 if a<0: raise RuntimeError('route anchor missing: '+start)
 b=src.find('\n      if (',a+len(start))
 if b<0: raise RuntimeError('next route anchor missing')
 return a,b,src[a:b]

def clean_previous(src):
 return re.sub(r'\n\s*// BEGIN_R44_5_23_STORE_MULTI.*?// END_R44_5_23_STORE_MULTI\s*\n','\n',src,flags=re.S)

def clone_routes(src):
 dstart='      if (request.method === "GET" && path === "/priorizacao") {'
 a,b,detail=top_block(src,dstart)
 buy_candidates=[
  '      if ((request.method === "POST" || request.method === "GET") && path === "/comprar/priorizacao") {',
  '      if (request.method === "POST" && path === "/comprar/priorizacao") {',
  '      if (request.method === "GET" && path === "/comprar/priorizacao") {'
 ]
 bs=None
 for x in buy_candidates:
  if x in src: bs=x; break
 if not bs: raise RuntimeError('priorizacao checkout route not found')
 _,_,buy=top_block(src,bs)
 maps=[
  ('governanca-ia','UGI-PROD-GOV-IA-20260825','UGI-MAT-GOV-IA-20260825','Kit de Governança de IA para Gestores','Governança de IA','governança de IA'),
  ('decisao-humana-ia','UGI-PROD-JULGAMENTO-IA-20260826','UGI-MAT-JULGAMENTO-IA-20260826','Framework de Decisão Humana na Era da IA','Decisão Humana + IA','decisão humana com IA')]
 chunks=[]
 for slug,pid,mid,title,short,topic in maps:
  d=detail.replace('/priorizacao','/'+slug).replace('UGI-MATERIAL-PRIORIDADES-001',pid).replace('UGI-KIT-PRIORIZACAO-001',mid)
  d=d.replace('Kit UGI — Priorização Inteligente',title).replace('Priorização Inteligente',short).replace('Priorização',short).replace('priorização',topic).replace('prioridades',topic)
  q=buy.replace('/comprar/priorizacao','/comprar/'+slug).replace('/priorizacao','/'+slug).replace('UGI-MATERIAL-PRIORIDADES-001',pid).replace('UGI-KIT-PRIORIZACAO-001',mid)
  q=q.replace('Kit UGI — Priorização Inteligente',title).replace('Priorização Inteligente',short).replace('Priorização',short).replace('priorização',topic).replace('prioridades',topic)
  chunks += [d,q]
 marker='\n      // BEGIN_R44_5_23_STORE_MULTI\n'+'\n'.join(chunks)+'\n      // END_R44_5_23_STORE_MULTI\n'
 return src[:a]+marker+src[a:]

def store_route():
 cfg=json.dumps(PRODUCTS,ensure_ascii=False,separators=(',',':'))
 return r'''      if (request.method === "GET" && path === "/materiais") {
        const cfg=__CFG__;
        const cards=[];
        for (const c of cfg) {
          const product=await getJsonR2(env, `${PRODUCT_PREFIX}${c.productId}.json`);
          const material=await getJsonR2(env, `${MATERIAL_PREFIX}${c.materialId}.json`);
          const ok=product&&material&&product.status!=="inactive"&&product.active!==false&&material.assetReady===true&&material.qualityStatus==="PASS"&&material.deliveryEnabled===true;
          if (!ok) continue;
          const title=escapeCommerceHtml(product.title||material.title||c.coverTitle.replace(/<br>/g," "));
          const desc=escapeCommerceHtml(product.description||material.description||"Material prático UGI para aplicação imediata.");
          const price=Number(product.price||14.90);
          const bullets=(c.bullets||[]).map(x=>`<li>${escapeCommerceHtml(x)}</li>`).join("");
          cards.push(`<article class="product-card" data-search="${escapeCommerceHtml(c.search)}"><div class="cover variant-${cards.length%3}"><div class="cover-brand">UGI</div><div class="cover-kicker">${escapeCommerceHtml(c.coverKicker)}</div><div class="cover-title">${c.coverTitle}</div><div class="cover-mark">✦</div><div class="cover-foot">${escapeCommerceHtml(c.coverFoot)}</div></div><div class="product-body"><div class="badges"><span>⚡ Uso imediato</span><span>✓ Premium V6</span></div><h2>${title}</h2><p class="desc">${desc}</p><ul>${bullets}</ul><div class="buy-row"><div><small>Material digital</small><div class="price">R$ ${price.toFixed(2).replace(".",",")}</div></div><a class="buy" href="${url.origin}/${encodeURIComponent(c.slug)}">Ver material</a></div></div></article>`);
        }
        const page=`<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#071b2d"><title>UGI Store · Materiais de Gestão</title><style>
        *{box-sizing:border-box}body{margin:0;background:#f4f6f8;color:#172232;font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif}.top{background:#071b2d;color:#fff}.nav{max-width:1180px;margin:auto;padding:16px 18px;display:flex;align-items:center;justify-content:space-between;gap:18px}.brand{font-weight:950;font-size:20px}.brand b{color:#f6b73c}.nav-note{font-size:13px;color:#d6dee7}.hero{max-width:1180px;margin:auto;padding:38px 18px 44px;display:grid;grid-template-columns:1.25fr .75fr;gap:28px;align-items:center}.eyebrow{color:#f6b73c;font-weight:900;font-size:13px;letter-spacing:.08em}.hero h1{font-size:clamp(36px,6vw,64px);line-height:.98;margin:10px 0 16px;letter-spacing:-.045em}.hero p{font-size:18px;line-height:1.55;color:#d8e1e9;max-width:720px}.hero-box{background:#0e2942;border:1px solid #27425a;border-radius:24px;padding:22px}.hero-box strong{display:block;font-size:20px;margin-bottom:10px}.hero-box div{color:#c9d4de;line-height:1.5}.trust{background:#fff;border-bottom:1px solid #e4e8ec}.trust-inner{max-width:1180px;margin:auto;padding:13px 18px;display:flex;gap:24px;justify-content:center;flex-wrap:wrap;font-size:13px;font-weight:750;color:#394959}.main{max-width:1180px;margin:auto;padding:30px 18px 72px}.search{display:flex;gap:10px;background:#fff;border:1px solid #dfe4e8;border-radius:16px;padding:10px 12px;box-shadow:0 8px 26px rgba(17,33,49,.06)}.search input{border:0;outline:0;width:100%;font-size:16px;background:transparent}.chips{display:flex;gap:9px;overflow:auto;padding:16px 0 8px}.chip{white-space:nowrap;border:1px solid #dce2e7;background:#fff;border-radius:999px;padding:9px 13px;font-size:13px;font-weight:800}.section-head{display:flex;align-items:end;justify-content:space-between;margin:24px 0 14px;gap:14px}.section-head h2{margin:0;font-size:27px}.section-head p{margin:0;color:#6b7785;font-size:14px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:22px}.product-card{background:#fff;border:1px solid #e1e6eb;border-radius:24px;overflow:hidden;box-shadow:0 12px 30px rgba(15,35,55,.09);display:grid;grid-template-columns:184px 1fr;min-height:350px}.cover{position:relative;color:#fff;padding:23px;display:flex;flex-direction:column;min-height:350px;overflow:hidden;background:linear-gradient(145deg,#071b2d 0%,#0d3557 64%,#154f7c 100%)}.cover:before{content:"";position:absolute;width:180px;height:180px;border:1px solid rgba(246,183,60,.22);border-radius:50%;right:-95px;top:35px}.cover:after{content:"";position:absolute;width:95px;height:95px;border:1px solid rgba(255,255,255,.13);border-radius:50%;right:-35px;top:78px}.variant-1{background:linear-gradient(145deg,#071b2d 0%,#123d45 60%,#1d6664 100%)}.variant-2{background:linear-gradient(145deg,#071b2d 0%,#26344f 60%,#51436e 100%)}.cover-brand{color:#f6b73c;font-size:29px;font-weight:950}.cover-kicker{font-size:11px;font-weight:900;letter-spacing:.14em;margin-top:30px;color:#cfe0ee}.cover-title{font-size:28px;line-height:1.02;font-weight:950;margin-top:8px;letter-spacing:-.035em;position:relative;z-index:2}.cover-mark{margin-top:18px;color:#f6b73c;font-size:26px}.cover-foot{margin-top:auto;font-size:12px;line-height:1.4;color:#d7e4ed;position:relative;z-index:2}.product-body{padding:22px;display:flex;flex-direction:column}.badges{display:flex;gap:7px;flex-wrap:wrap}.badges span{font-size:11px;font-weight:850;background:#fff3d7;color:#795000;padding:6px 8px;border-radius:999px}.product-body h2{font-size:22px;line-height:1.12;margin:13px 0 8px}.desc{color:#596776;line-height:1.48;margin:0}.product-body ul{padding-left:19px;color:#43515f;font-size:13px;line-height:1.55}.buy-row{display:flex;align-items:end;justify-content:space-between;gap:14px;margin-top:auto}.buy-row small{color:#7b8794}.price{font-size:27px;font-weight:950;color:#0b2134}.buy{display:inline-block;text-decoration:none;background:#f6b73c;color:#071b2d;font-weight:950;padding:13px 17px;border-radius:13px;box-shadow:0 4px 0 #c58a18}.buy:active{transform:translateY(2px);box-shadow:0 2px 0 #c58a18}.benefits{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:30px}.benefit{background:#fff;border:1px solid #e1e6eb;border-radius:18px;padding:18px}.benefit b{display:block;margin-bottom:6px}.benefit p{margin:0;color:#687582;font-size:13px;line-height:1.45}.empty{background:#fff;padding:28px;border-radius:18px}.footer{background:#071b2d;color:#c9d4de;padding:28px 18px;text-align:center;font-size:13px}.footer b{color:#fff}@media(max-width:760px){.hero{grid-template-columns:1fr}.hero-box{display:none}.product-card{grid-template-columns:1fr}.cover{min-height:250px}.benefits{grid-template-columns:1fr}.section-head{align-items:flex-start;flex-direction:column}.nav-note{display:none}}
        </style></head><body><header class="top"><div class="nav"><div class="brand"><b>UGI</b> · UMA GESTÃO INTELIGENTE</div><div class="nav-note">Soluções práticas · entrega digital</div></div><section class="hero"><div><div class="eyebrow">UGI STORE</div><h1>Ferramentas que transformam gestão em ação.</h1><p>Materiais premium, acessíveis e feitos para resolver problemas reais de liderança, decisão, produtividade e IA.</p></div><div class="hero-box"><strong>🎯 Muito valor. Pouca enrolação.</strong><div>Escolha uma dor real, compre em poucos passos e saia com método, prompts, matrizes e ferramentas para aplicar imediatamente.</div></div></section></header><div class="trust"><div class="trust-inner"><span>🔒 Compra segura</span><span>⚡ Acesso digital</span><span>💡 Aplicação prática</span><span>📘 Premium V6</span></div></div><main class="main"><label class="search">🔎 <input id="q" placeholder="Qual problema você quer resolver?" autocomplete="off"></label><div class="chips"><span class="chip">Todos</span><span class="chip">Prioridades</span><span class="chip">Liderança</span><span class="chip">IA na Gestão</span><span class="chip">Produtividade</span><span class="chip">Decisão</span></div><div class="section-head"><div><h2>🔥 Materiais em destaque</h2><p>Produtos já prontos para aplicar.</p></div><p>Preço simples. Sem assinatura.</p></div><section class="grid" id="products">${cards.length?cards.join(""):`<div class="empty">Nenhum material está disponível neste momento.</div>`}</section><section class="benefits"><div class="benefit"><b>📘 Conteúdo premium</b><p>Método, exemplos, prompts, matrizes e aplicação prática — não apenas texto corrido.</p></div><div class="benefit"><b>⚙️ Feito para usar</b><p>Materiais pensados para virar decisão, conversa, processo e resultado.</p></div><div class="benefit"><b>✨ Biblioteca crescente</b><p>Novos produtos entram conforme tendências e necessidades reais da comunidade UGI.</p></div></section></main><footer class="footer"><b>UGI · Uma Gestão Inteligente</b><br>Gestão melhor começa com uma decisão prática.</footer><script>const q=document.getElementById('q');q&&q.addEventListener('input',()=>{const v=q.value.toLowerCase().trim();document.querySelectorAll('.product-card').forEach(c=>{c.style.display=!v||c.dataset.search.includes(v)?'grid':'none'})});</script></body></html>`;
        return new Response(page,{status:200,headers:{"Content-Type":"text/html; charset=utf-8","Cache-Control":"no-store"}});
      }
'''.replace('__CFG__',cfg)

def patch(src):
 t=clean_previous(base.strip_temp_routes(src))
 t=re.sub(r'(?:const|var) VERSION = "[^"]+";',f'var VERSION = "{NEW}";',t,count=1)
 s='      if (request.method === "GET" && path === "/materiais") {'
 a,b,_=top_block(t,s); t=t[:a]+store_route()+t[b:]
 t=clone_routes(t)
 return t

def validate():
 r=requests.get(ORIGIN+'/materiais',timeout=25); body=r.text
 checks={'http_200':r.status_code==200,'store':'UGI STORE' in body,'gov':'Governança' in body,'decision':'Decisão' in body,'premium':'Premium V6' in body or 'PREMIUM V6' in body,'price':'14,90' in body}
 if not all(checks.values()): raise RuntimeError('store validation failed '+json.dumps(checks,ensure_ascii=False))
 for slug in ['priorizacao','governanca-ia','decisao-humana-ia']:
  p=requests.get(ORIGIN+'/'+slug,timeout=20)
  if p.status_code!=200 or 'Comprar agora' not in p.text: raise RuntimeError('product page failed '+slug+' '+str(p.status_code))
  c=requests.get(ORIGIN+'/comprar/'+slug+'?source=store_v3_smoke',timeout=30,allow_redirects=False,headers={'User-Agent':'UGI-StoreV3-Smoke/1.0'})
  loc=c.headers.get('location','')
  if c.status_code not in (301,302,303,307,308) or 'asaas.com/checkoutSession/show' not in loc: raise RuntimeError('checkout failed '+slug+' http='+str(c.status_code)+' loc='+loc[:200])
 return checks

def main():
 lines=['R44.5.23_STAGE=STORE_MULTI_PRODUCT_PREMIUM_V6','OK=false','STATE=STARTED']; write(lines)
 tok=os.environ['CF_API_TOKEN']; acct=os.environ['CF_ACCOUNT_ID']; h=headers(tok); api=f'https://api.cloudflare.com/client/v4/accounts/{acct}/workers/scripts/{WORKER}'
 live=fetch_live(api,h); bindings,base_vid=current_bindings(api,h); final=patch(live)
 lines += [f'BASE_VERSION_ID={base_vid}',f'BASE_SOURCE_BYTES={len(live.encode())}',f'PATCHED_SOURCE_BYTES={len(final.encode())}',f'BINDINGS_PRESERVED={len(bindings)}']
 v=base.create_version(api,h,final,bindings,'UGI R44.5.23 Store multi-product Premium V6'); d=base.deploy(api,h,v,'UGI R44.5.23 Store multi-product Premium V6')
 last={}
 for _ in range(25):
  try:
   rr=requests.get(ORIGIN+'/api/health',timeout=12)
   if rr.status_code==200:
    last=rr.json()
    if last.get('ok') is True and last.get('version')==NEW: break
  except Exception: pass
  time.sleep(3)
 else: raise RuntimeError('health timeout '+json.dumps(last,ensure_ascii=False)[:800])
 checks=validate(); lines += ['FINAL_VERSION_ID='+v,'FINAL_DEPLOYMENT_ID='+d,'WORKER_HEALTH_PASS=true','STORE_MULTI_PRODUCT_PASS=true','PRODUCT_COUNT_EXPECTED=3','GOVERNANCE_PRODUCT_PAGE_PASS=true','DECISION_PRODUCT_PAGE_PASS=true','CHECKOUT_3_OF_3_PASS=true','PAYMENT_PERFORMED=false','OK=true']; write(lines)
if __name__=='__main__':
 try: main()
 except BaseException as e:
  try: lines=STATUS.read_text(encoding='utf-8').splitlines() if STATUS.exists() else []
  except Exception: lines=[]
  lines += ['ERROR_TYPE='+type(e).__name__,'ERROR='+str(e).replace('\n',' ')[:2000],'OK=false']; write(lines); raise

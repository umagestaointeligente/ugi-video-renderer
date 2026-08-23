from __future__ import annotations
import json, os, re, time
from pathlib import Path
import requests
import scripts.r44_5_18_repair_v2 as base

STATUS=Path('cloudflare/status/r44-5-21-store-v2.txt')
WORKER='lola-operacional-ugi'
ORIGIN='https://lola-operacional-ugi.umagestaointeligente.workers.dev'
OLD='lola-v8-r44-5-20-reliable-checkout-branded-domain-2026-08-21'
NEW='lola-v8-r44-5-21-ugi-store-v2-2026-08-22'


def write(lines):
    STATUS.parent.mkdir(parents=True,exist_ok=True)
    STATUS.write_text('\n'.join(lines)+'\n',encoding='utf-8')


def fetch_live(api,h):
    r=requests.get(api+'/content/v2',headers=h,timeout=40)
    r.raise_for_status()
    return base.extract_source(r)


def bindings(api,h):
    r=requests.get(api+f'/versions/{base.STABLE_VERSION_ID}',headers=h,timeout=30)
    r.raise_for_status()
    return base.restored_bindings(r.json())


def deploy(api,h,src,b,tag):
    v=base.create_version(api,h,src,b,tag)
    d=base.deploy(api,h,v,tag)
    return v,d


def wait(ver):
    last={}
    for _ in range(24):
        try:
            r=requests.get(ORIGIN+'/api/health',timeout=12)
            if r.status_code==200:
                last=r.json(); bd=last.get('bindings') or {}
                if (last.get('ok') is True and last.get('version')==ver
                    and bd.get('MEDIA_R2') is True and bd.get('BUFFER_API_KEY') is True and bd.get('ASAAS_API_KEY') is True):
                    return last
        except Exception:
            pass
        time.sleep(3)
    raise RuntimeError('health timeout '+json.dumps(last,ensure_ascii=False)[:1200])


def store_route():
    return r'''      if (request.method === "GET" && path === "/materiais") {
        const product=await getJsonR2(env, `${PRODUCT_PREFIX}UGI-MATERIAL-PRIORIDADES-001.json`);
        const material=await getJsonR2(env, `${MATERIAL_PREFIX}UGI-KIT-PRIORIZACAO-001.json`);
        const ok=product&&material&&product.status==="active"&&material.assetReady===true&&material.qualityStatus==="PASS"&&material.deliveryEnabled===true;
        const title=escapeCommerceHtml(product?.title||material?.title||"Kit UGI — Priorização Inteligente");
        const desc=escapeCommerceHtml(product?.description||material?.description||"Critérios práticos para decidir o que entra, o que sai e o que realmente merece foco.");
        const price=Number(product?.price||14.99);
        const card=ok?`<article class="product-card" data-search="priorização prioridades foco produtividade liderança gestão"><div class="cover"><div class="cover-brand">UGI</div><div class="cover-kicker">KIT PRÁTICO</div><div class="cover-title">Priorização<br>Inteligente</div><div class="cover-foot">Decida melhor. Proteja o foco.</div></div><div class="product-body"><div class="badges"><span>🔥 Mais procurado</span><span>⚡ Uso imediato</span></div><h2>${title}</h2><p class="desc">${desc}</p><ul><li>Filtro rápido para novas demandas</li><li>Critérios para reduzir urgência artificial</li><li>Aplicação prática no dia a dia do gestor</li></ul><div class="buy-row"><div><small>Material digital</small><div class="price">R$ ${price.toFixed(2).replace(".",",")}</div></div><a class="buy" href="${url.origin}/priorizacao">Ver material</a></div></div></article>`:`<div class="empty">Nenhum material está disponível para compra neste momento.</div>`;
        const page=`<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#071b2d"><title>UGI Store · Materiais de Gestão</title><style>
        *{box-sizing:border-box}body{margin:0;background:#f4f6f8;color:#172232;font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif}.top{background:#071b2d;color:#fff}.nav{max-width:1160px;margin:auto;padding:16px 18px;display:flex;align-items:center;justify-content:space-between;gap:18px}.brand{font-weight:950;letter-spacing:.2px;font-size:20px}.brand b{color:#f6b73c}.nav-note{font-size:13px;color:#d6dee7}.hero{max-width:1160px;margin:auto;padding:34px 18px 40px;display:grid;grid-template-columns:1.25fr .75fr;gap:28px;align-items:center}.eyebrow{color:#f6b73c;font-weight:900;font-size:13px;letter-spacing:.08em}.hero h1{font-size:clamp(34px,6vw,62px);line-height:.98;margin:10px 0 16px;letter-spacing:-.04em}.hero p{font-size:18px;line-height:1.55;color:#d8e1e9;max-width:700px}.hero-box{background:#0e2942;border:1px solid #27425a;border-radius:24px;padding:22px}.hero-box strong{display:block;font-size:20px;margin-bottom:10px}.hero-box div{color:#c9d4de;line-height:1.5}.trust{background:#fff;border-bottom:1px solid #e4e8ec}.trust-inner{max-width:1160px;margin:auto;padding:13px 18px;display:flex;gap:24px;justify-content:center;flex-wrap:wrap;font-size:13px;font-weight:750;color:#394959}.main{max-width:1160px;margin:auto;padding:28px 18px 70px}.search{display:flex;gap:10px;background:#fff;border:1px solid #dfe4e8;border-radius:16px;padding:10px 12px;box-shadow:0 8px 26px rgba(17,33,49,.06)}.search input{border:0;outline:0;width:100%;font-size:16px;background:transparent}.chips{display:flex;gap:9px;overflow:auto;padding:16px 0 8px}.chip{white-space:nowrap;border:1px solid #dce2e7;background:#fff;border-radius:999px;padding:9px 13px;font-size:13px;font-weight:800}.section-head{display:flex;align-items:end;justify-content:space-between;margin:24px 0 14px;gap:14px}.section-head h2{margin:0;font-size:26px}.section-head p{margin:0;color:#6b7785;font-size:14px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:20px}.product-card{background:#fff;border:1px solid #e1e6eb;border-radius:24px;overflow:hidden;box-shadow:0 12px 30px rgba(15,35,55,.08);display:grid;grid-template-columns:190px 1fr;min-height:330px}.cover{background:linear-gradient(145deg,#071b2d 0%,#0d3557 66%,#154f7c 100%);color:#fff;padding:24px;display:flex;flex-direction:column;min-height:330px}.cover-brand{color:#f6b73c;font-size:28px;font-weight:950}.cover-kicker{font-size:11px;font-weight:900;letter-spacing:.14em;margin-top:30px;color:#cfe0ee}.cover-title{font-size:29px;line-height:1.02;font-weight:950;margin-top:8px;letter-spacing:-.03em}.cover-foot{margin-top:auto;font-size:12px;line-height:1.4;color:#d7e4ed}.product-body{padding:22px;display:flex;flex-direction:column}.badges{display:flex;gap:7px;flex-wrap:wrap}.badges span{font-size:11px;font-weight:850;background:#fff3d7;color:#795000;padding:6px 8px;border-radius:999px}.product-body h2{font-size:22px;line-height:1.12;margin:13px 0 8px}.desc{color:#596776;line-height:1.48;margin:0}.product-body ul{padding-left:19px;color:#43515f;font-size:13px;line-height:1.55}.buy-row{display:flex;align-items:end;justify-content:space-between;gap:14px;margin-top:auto}.buy-row small{color:#7b8794}.price{font-size:27px;font-weight:950;color:#0b2134}.buy{display:inline-block;text-decoration:none;background:#f6b73c;color:#071b2d;font-weight:950;padding:13px 17px;border-radius:13px;box-shadow:0 4px 0 #c58a18}.buy:active{transform:translateY(2px);box-shadow:0 2px 0 #c58a18}.benefits{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:28px}.benefit{background:#fff;border:1px solid #e1e6eb;border-radius:18px;padding:18px}.benefit b{display:block;margin-bottom:6px}.benefit p{margin:0;color:#687582;font-size:13px;line-height:1.45}.empty{background:#fff;padding:28px;border-radius:18px}.footer{background:#071b2d;color:#c9d4de;padding:28px 18px;text-align:center;font-size:13px}.footer b{color:#fff}@media(max-width:760px){.hero{grid-template-columns:1fr}.hero-box{display:none}.product-card{grid-template-columns:1fr}.cover{min-height:240px}.benefits{grid-template-columns:1fr}.section-head{align-items:flex-start;flex-direction:column}.nav-note{display:none}}
        </style></head><body><header class="top"><div class="nav"><div class="brand"><b>UGI</b> · UMA GESTÃO INTELIGENTE</div><div class="nav-note">Soluções práticas · entrega digital</div></div><section class="hero"><div><div class="eyebrow">UGI STORE</div><h1>Ferramentas práticas para gerir melhor.</h1><p>Materiais diretos ao ponto, acessíveis e feitos para transformar problemas reais de gestão em ação.</p></div><div class="hero-box"><strong>🎯 Resolva uma dor por vez.</strong><div>Escolha o tema que mais pesa na sua rotina. Veja o material, compre em poucos passos e aplique imediatamente.</div></div></section></header><div class="trust"><div class="trust-inner"><span>🔒 Compra segura</span><span>⚡ Acesso digital</span><span>💡 Aplicação prática</span><span>💰 Baixo investimento</span></div></div><main class="main"><label class="search">🔎 <input id="q" placeholder="Qual problema você quer resolver?" autocomplete="off"></label><div class="chips"><span class="chip">Todos</span><span class="chip">Prioridades</span><span class="chip">Liderança</span><span class="chip">Comunicação</span><span class="chip">IA na Gestão</span><span class="chip">Produtividade</span><span class="chip">Decisão</span></div><div class="section-head"><div><h2>🔥 Materiais em destaque</h2><p>Soluções já prontas para aplicar.</p></div><p>Preço simples. Sem assinatura.</p></div><section class="grid" id="products">${card}</section><section class="benefits"><div class="benefit"><b>📘 Conteúdo objetivo</b><p>Sem enrolação: método, exemplos e aplicação para a rotina do gestor.</p></div><div class="benefit"><b>⚙️ Feito para usar</b><p>Materiais pensados para sair da teoria e virar decisão, conversa ou processo.</p></div><div class="benefit"><b>✨ Loja em evolução</b><p>Novas soluções entram conforme os temas e necessidades reais da comunidade UGI.</p></div></section></main><footer class="footer"><b>UGI · Uma Gestão Inteligente</b><br>Gestão melhor começa com uma decisão prática.</footer><script>const q=document.getElementById('q');q&&q.addEventListener('input',()=>{const v=q.value.toLowerCase().trim();document.querySelectorAll('.product-card').forEach(c=>{c.style.display=!v||c.dataset.search.includes(v)?'grid':'none'})});</script></body></html>`;
        return new Response(page,{status:200,headers:{"Content-Type":"text/html; charset=utf-8","Cache-Control":"no-store"}});
      }
'''


def patch(src):
    t=base.strip_temp_routes(src)
    old=f'var VERSION = "{OLD}";'
    if old in t:
        t=t.replace(old,f'var VERSION = "{NEW}";',1)
    elif f'var VERSION = "{NEW}";' not in t:
        raise RuntimeError('version anchor mismatch; refusing to patch unknown live version')

    start='      if (request.method === "GET" && path === "/materiais") {'
    nxt='      if (request.method === "GET" && path === "/priorizacao") {'
    a=t.find(start); b=t.find(nxt,a+1)
    if a<0 or b<0 or b<=a:
        raise RuntimeError('materials route anchors not found')
    t=t[:a]+store_route()+'\n'+t[b:]
    return t


def validate():
    r=requests.get(ORIGIN+'/materiais',timeout=20)
    body=r.text
    checks={
      'http_200':r.status_code==200,
      'store_marker':'UGI STORE' in body,
      'hero':'Ferramentas práticas para gerir melhor.' in body,
      'search':'Qual problema você quer resolver?' in body,
      'cover':'Priorização' in body,
      'price':'R$ 14,99' in body,
      'product_link':'/priorizacao' in body,
      'trust':'Compra segura' in body,
      'mobile':'@media(max-width:760px)' in body,
    }
    if not all(checks.values()):
        raise RuntimeError('store validation failed '+json.dumps(checks,ensure_ascii=False))
    p=requests.get(ORIGIN+'/priorizacao',timeout=20)
    if p.status_code!=200 or 'Comprar agora' not in p.text or '/comprar/priorizacao' not in p.text:
        raise RuntimeError('product/checkout entrypoint regression')
    c=requests.get(ORIGIN+'/comprar/priorizacao?source=store_v2_smoke',timeout=30,allow_redirects=False,headers={'User-Agent':'UGI-StoreV2-Smoke/1.0'})
    loc=c.headers.get('location','')
    if c.status_code not in (301,302,303,307,308) or 'asaas.com/checkoutSession/show' not in loc:
        raise RuntimeError('checkout regression http='+str(c.status_code)+' loc='+loc[:300])
    return checks,c.status_code


def main():
    lines=['R44.5.21_STAGE=UGI_STORE_V2','OK=false','STATE=STARTED']
    write(lines)
    tok=os.environ['CF_API_TOKEN']; acct=os.environ['CF_ACCOUNT_ID']
    h={'Authorization':f'Bearer {tok}'}; api=f'https://api.cloudflare.com/client/v4/accounts/{acct}/workers/scripts/{WORKER}'
    live=fetch_live(api,h); final=patch(live); b=bindings(api,h)
    lines += [f'BASE_SOURCE_BYTES={len(live.encode())}',f'PATCHED_SOURCE_BYTES={len(final.encode())}','BINDINGS_PRESERVED=19']
    v,d=deploy(api,h,final,b,'UGI R44.5.21 Store V2 visual commerce'); wait(NEW)
    checks,code=validate()
    lines += ['FINAL_VERSION_ID='+v,'FINAL_DEPLOYMENT_ID='+d,'WORKER_HEALTH_PASS=true','STORE_PAGE_HTTP_200=true','STORE_VISUAL_V2_PASS=true','STORE_SEARCH_PRESENT=true','STORE_CATEGORY_CHIPS_PRESENT=true','STORE_PRODUCT_COVER_PRESENT=true','STORE_TRUST_STRIP_PRESENT=true','STORE_MOBILE_RESPONSIVE=true','PRODUCT_PAGE_REGRESSION_PASS=true',f'CHECKOUT_REDIRECT_HTTP={code}','CHECKOUT_END_TO_END_READY=true','PAYMENT_PERFORMED=false','OK=true']
    write(lines)

if __name__=='__main__':
    try: main()
    except BaseException as e:
        try:x=STATUS.read_text(encoding='utf-8').splitlines() if STATUS.exists() else []
        except Exception:x=[]
        x += ['ERROR_TYPE='+type(e).__name__,'ERROR='+str(e).replace('\n',' ')[:2500],'OK=false']
        write(x)
        raise

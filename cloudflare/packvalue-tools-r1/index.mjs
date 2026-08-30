const VERSION = "packvalue-tools-r1-2026-08-30";
const HOST = "lsi-packvalue-tools-r1.umagestaointeligente.workers.dev";
const ORIGIN = `https://${HOST}`;
const INDEXNOW_KEY = "20c4b7acde517f7ccdb4bfbf55baf9d6b9e5674b73ee29cec14368d431dc0673";

const TOOLS = {
  "/preco-por-kg": {
    title: "Calculadora de preço por kg",
    description: "Compare embalagens de pesos diferentes pelo custo real por quilo, incluindo frete e desconto.",
    mode: "pack",
    dimension: "mass",
    defaultUnit: "g",
    example: "Ex.: 3 pacotes de 200 g por R$ 17,90 versus 1 kg por R$ 27,90."
  },
  "/preco-por-litro": {
    title: "Calculadora de preço por litro",
    description: "Descubra qual garrafa, lata ou multipack custa menos por litro.",
    mode: "pack",
    dimension: "volume",
    defaultUnit: "ml",
    example: "Ex.: 6 × 330 ml por R$ 19,90 versus 2 L por R$ 8,99."
  },
  "/preco-por-unidade": {
    title: "Calculadora de preço por unidade",
    description: "Compare caixas, kits e multipacks pelo preço efetivo de cada unidade.",
    mode: "pack",
    dimension: "count",
    defaultUnit: "un",
    example: "Ex.: caixa com 12 unidades por R$ 34,90 versus 8 unidades por R$ 25,90."
  },
  "/comparar-pacotes": {
    title: "Comparador de pacotes e embalagens",
    description: "Compare dois packs lado a lado e veja qual entrega mais quantidade por real gasto.",
    mode: "pack",
    dimension: "any",
    defaultUnit: "g",
    example: "Informe quantidade, tamanho de cada item, unidade, preço, frete e desconto."
  },
  "/desconto-real": {
    title: "Calculadora de desconto real",
    description: "Calcule a redução percentual real entre preço anterior e preço atual.",
    mode: "discount",
    example: "Ex.: de R$ 129,90 por R$ 89,90."
  },
  "/leve-mais-pague-menos": {
    title: "Leve mais, pague menos: vale a pena?",
    description: "Transforme promoções do tipo leve 3 pague 2 em preço efetivo por unidade e desconto real.",
    mode: "promo",
    example: "Ex.: leve 3, pague 2, preço unitário R$ 9,90."
  },
  "/rendimento-diluicao": {
    title: "Calculadora de rendimento e diluição",
    description: "Calcule quanto um concentrado rende após diluição e o custo efetivo por litro pronto.",
    mode: "dilution",
    example: "Ex.: 500 ml de concentrado, proporção 1:9, preço R$ 12,90."
  },
  "/custo-com-frete": {
    title: "Preço real com frete e desconto",
    description: "Veja o custo final de uma compra após desconto, cupom, frete e quantidade.",
    mode: "landed",
    example: "Ex.: produto R$ 49,90, desconto 10%, frete R$ 12 e 3 unidades."
  }
};

function esc(v) {
  return String(v ?? "").replace(/[&<>\"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));
}

function json(data, status = 200, headers = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {"content-type":"application/json; charset=utf-8","cache-control":"no-store", ...headers}
  });
}

function layout(tool, path) {
  const canonical = `${ORIGIN}${path}`;
  const cards = Object.entries(TOOLS).map(([p, t]) => `<a class="tool-link" href="${p}"><strong>${esc(t.title)}</strong><span>${esc(t.description)}</span></a>`).join("");
  const app = appHtml(tool);
  const ld = JSON.stringify({
    "@context":"https://schema.org",
    "@type":"WebApplication",
    name: tool.title,
    description: tool.description,
    url: canonical,
    applicationCategory:"FinanceApplication",
    operatingSystem:"Any",
    offers:{"@type":"Offer",price:"0",priceCurrency:"BRL"}
  }).replace(/</g, "\\u003c");
  return `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(tool.title)} | PackValue Tools</title><meta name="description" content="${esc(tool.description)}"><link rel="canonical" href="${canonical}"><meta name="robots" content="index,follow,max-snippet:-1"><script type="application/ld+json">${ld}</script><style>${CSS}</style></head><body><header><a href="/" class="brand">PackValue Tools</a><span>calculadoras gratuitas de preço e rendimento</span></header><main><article><p class="eyebrow">Calculadora gratuita</p><h1>${esc(tool.title)}</h1><p class="lead">${esc(tool.description)}</p><p class="example">${esc(tool.example)}</p>${app}<section class="content"><h2>Como usar</h2><p>Informe os valores da oferta exatamente como aparecem na loja. O cálculo é feito no seu navegador e nenhum dado digitado é enviado para cadastro ou perfil.</p><h2>Por que comparar o preço normalizado?</h2><p>Embalagens maiores nem sempre são mais baratas. Frete, desconto, quantidade e rendimento podem inverter a comparação. Normalizar para kg, litro ou unidade permite comparar ofertas em uma base comum.</p><h2>Limites</h2><p>Use o resultado como apoio de compra. Verifique validade, qualidade, composição, impostos, condições do cupom e outras diferenças que possam alterar o valor real do produto.</p></section></article><aside><h2>Outras calculadoras</h2>${cards}</aside></main><footer><a href="/sobre">Sobre</a> · <a href="/privacidade">Privacidade</a> · <a href="/llms.txt">llms.txt</a></footer><script>${JS}</script></body></html>`;
}

function home() {
  const cards = Object.entries(TOOLS).map(([p,t]) => `<a class="tool-link big" href="${p}"><strong>${esc(t.title)}</strong><span>${esc(t.description)}</span></a>`).join("");
  return `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PackValue Tools — compare preços, packs e rendimento</title><meta name="description" content="Calculadoras gratuitas para comparar preço por kg, litro, unidade, descontos, frete e rendimento."><link rel="canonical" href="${ORIGIN}/"><meta name="robots" content="index,follow"><style>${CSS}</style></head><body><header><a href="/" class="brand">PackValue Tools</a><span>decisões de compra com matemática simples</span></header><main class="home"><article><p class="eyebrow">Grátis · sem cadastro</p><h1>Compare o valor real antes de comprar.</h1><p class="lead">Multipacks, tamanhos diferentes, descontos e frete tornam preços difíceis de comparar. Escolha uma calculadora e normalize a oferta em segundos.</p><div class="grid">${cards}</div><section class="content"><h2>O que é PackValue?</h2><p>PackValue é uma suíte independente de calculadoras determinísticas para pessoas e agentes de software. O objetivo é transformar embalagens e promoções em métricas comparáveis, sem depender de inteligência artificial para a conta.</p></section></article></main><footer><a href="/sobre">Sobre</a> · <a href="/privacidade">Privacidade</a></footer></body></html>`;
}

function appHtml(tool) {
  if (tool.mode === "discount") return `<div class="calc" data-mode="discount"><label>Preço anterior (R$)<input id="old" inputmode="decimal" value="129,90"></label><label>Preço atual (R$)<input id="now" inputmode="decimal" value="89,90"></label><button>Calcular desconto</button><output></output></div>`;
  if (tool.mode === "promo") return `<div class="calc" data-mode="promo"><label>Leve<input id="take" type="number" min="1" value="3"></label><label>Pague<input id="pay" type="number" min="0" value="2"></label><label>Preço de cada unidade (R$)<input id="unitPrice" inputmode="decimal" value="9,90"></label><button>Calcular promoção</button><output></output></div>`;
  if (tool.mode === "dilution") return `<div class="calc" data-mode="dilution"><label>Volume do concentrado (ml)<input id="conc" inputmode="decimal" value="500"></label><label>Partes de água para 1 parte de concentrado<input id="water" inputmode="decimal" value="9"></label><label>Preço do concentrado (R$)<input id="concPrice" inputmode="decimal" value="12,90"></label><button>Calcular rendimento</button><output></output></div>`;
  if (tool.mode === "landed") return `<div class="calc" data-mode="landed"><label>Preço unitário (R$)<input id="basePrice" inputmode="decimal" value="49,90"></label><label>Quantidade<input id="baseQty" type="number" min="1" value="3"></label><label>Desconto (%)<input id="baseDisc" inputmode="decimal" value="10"></label><label>Frete total (R$)<input id="baseShip" inputmode="decimal" value="12"></label><button>Calcular custo final</button><output></output></div>`;
  return `<div class="calc" data-mode="pack" data-dimension="${esc(tool.dimension || "any")}"><div class="offers"><fieldset><legend>Oferta A</legend>${offerFields("a", tool.defaultUnit || "g", "17,90")}</fieldset><fieldset><legend>Oferta B</legend>${offerFields("b", tool.defaultUnit || "g", "27,90", tool.dimension === "count" ? "1" : "1000")}</fieldset></div><button>Comparar ofertas</button><output></output></div>`;
}
function offerFields(prefix, unit, price, size="200") {
  return `<label>Nº de itens<input id="${prefix}qty" type="number" min="1" value="${prefix==='a'?'3':'1'}"></label><label>Tamanho de cada item<input id="${prefix}size" inputmode="decimal" value="${size}"></label><label>Unidade<select id="${prefix}unit"><option ${unit==='g'?'selected':''}>g</option><option ${unit==='kg'?'selected':''}>kg</option><option ${unit==='ml'?'selected':''}>ml</option><option ${unit==='l'?'selected':''}>L</option><option ${unit==='un'?'selected':''}>un</option></select></label><label>Preço total (R$)<input id="${prefix}price" inputmode="decimal" value="${price}"></label><label>Frete (R$)<input id="${prefix}ship" inputmode="decimal" value="0"></label><label>Desconto (%)<input id="${prefix}disc" inputmode="decimal" value="0"></label>`;
}

const CSS = `:root{font-family:Inter,system-ui,sans-serif;color:#172033;background:#f5f7fb}*{box-sizing:border-box}body{margin:0}header,footer{max-width:1120px;margin:auto;padding:20px 24px;display:flex;gap:16px;align-items:center;justify-content:space-between}.brand{font-weight:800;color:#172033;text-decoration:none;font-size:20px}header span{color:#62708a;font-size:14px}main{max-width:1120px;margin:24px auto 72px;padding:0 24px;display:grid;grid-template-columns:minmax(0,2fr) minmax(250px,1fr);gap:36px}.home{display:block;max-width:1000px}.eyebrow{text-transform:uppercase;letter-spacing:.12em;color:#5268e3;font-size:12px;font-weight:800}h1{font-size:clamp(34px,5vw,60px);line-height:1.02;margin:8px 0 18px}h2{margin-top:34px}.lead{font-size:20px;line-height:1.55;color:#536078;max-width:760px}.example{background:#eef1ff;border-radius:12px;padding:12px 14px;color:#45516c}.calc{background:white;border:1px solid #dde3ee;border-radius:18px;padding:20px;box-shadow:0 10px 30px rgba(28,40,80,.06);margin:24px 0}.offers{display:grid;grid-template-columns:1fr 1fr;gap:16px}fieldset{border:1px solid #e0e5ef;border-radius:12px;padding:14px}legend{font-weight:800}label{display:block;font-size:13px;font-weight:700;margin:10px 0;color:#46536a}input,select{width:100%;padding:11px;margin-top:5px;border:1px solid #cfd7e5;border-radius:9px;background:white;font-size:16px}button{border:0;background:#3048d8;color:white;font-weight:800;border-radius:10px;padding:13px 18px;font-size:16px;cursor:pointer;margin-top:12px}output{display:block;margin-top:16px;padding:15px;border-radius:12px;background:#f0f7f3;font-weight:700;line-height:1.5;min-height:48px}.tool-link{display:block;padding:13px;border:1px solid #dfe5ee;background:white;border-radius:12px;text-decoration:none;color:#1f2940;margin:9px 0}.tool-link span{display:block;font-size:13px;color:#65718a;margin-top:4px;line-height:1.35}.tool-link.big{padding:18px}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin:30px 0}.content{line-height:1.7;color:#44516b}footer{border-top:1px solid #e0e5ec;color:#65718a;font-size:13px}footer a{color:inherit}@media(max-width:760px){main{grid-template-columns:1fr}.offers,.grid{grid-template-columns:1fr}header{align-items:flex-start;flex-direction:column}aside{border-top:1px solid #ddd;padding-top:20px}}`;

const JS = `(()=>{const n=v=>{v=String(v??'').trim().replace(/\\./g,'').replace(',','.');const x=Number(v);return Number.isFinite(x)?x:NaN},money=x=>new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'}).format(x),fmt=x=>new Intl.NumberFormat('pt-BR',{maximumFractionDigits:3}).format(x);const root=document.querySelector('.calc');if(!root)return;root.querySelector('button').addEventListener('click',()=>{const out=root.querySelector('output'),mode=root.dataset.mode;try{if(mode==='discount'){const a=n(old.value),b=n(now.value);if(!(a>0&&b>=0))throw 0;out.textContent='Desconto real: '+fmt((a-b)/a*100)+'%. Economia: '+money(a-b)+'.';return}if(mode==='promo'){const a=n(take.value),b=n(pay.value),p=n(unitPrice.value);if(!(a>0&&b>=0&&b<=a&&p>=0))throw 0;const total=b*p;out.textContent='Total pago: '+money(total)+'. Preço efetivo por unidade: '+money(total/a)+'. Desconto equivalente: '+fmt((a-b)/a*100)+'%.';return}if(mode==='dilution'){const c=n(conc.value),w=n(water.value),p=n(concPrice.value);if(!(c>0&&w>=0&&p>=0))throw 0;const liters=c*(1+w)/1000;out.textContent='Rendimento pronto: '+fmt(liters)+' L. Custo efetivo: '+money(p/liters)+' por litro.';return}if(mode==='landed'){const p=n(basePrice.value),q=n(baseQty.value),d=n(baseDisc.value),s=n(baseShip.value);if(!(p>=0&&q>0&&d>=0&&d<=100&&s>=0))throw 0;const total=p*q*(1-d/100)+s;out.textContent='Custo final: '+money(total)+'. Custo efetivo por unidade: '+money(total/q)+'.';return}if(mode==='pack'){const calc=x=>{const q=n(document.querySelector('#'+x+'qty').value),size=n(document.querySelector('#'+x+'size').value),unit=document.querySelector('#'+x+'unit').value.toLowerCase(),price=n(document.querySelector('#'+x+'price').value),ship=n(document.querySelector('#'+x+'ship').value),disc=n(document.querySelector('#'+x+'disc').value);if(!(q>0&&size>0&&price>=0&&ship>=0&&disc>=0&&disc<=100))throw 0;let dim,base;if(unit==='g'){dim='mass';base=q*size/1000}else if(unit==='kg'){dim='mass';base=q*size}else if(unit==='ml'){dim='volume';base=q*size/1000}else if(unit==='l'){dim='volume';base=q*size}else{dim='count';base=q*size}const final=price*(1-disc/100)+ship;return{dim,base,final,per:final/base}};const a=calc('a'),b=calc('b');if(a.dim!==b.dim){out.textContent='Não é possível comparar: as ofertas usam dimensões diferentes.';return}const unit=a.dim==='mass'?'kg':a.dim==='volume'?'L':'unidade';const winner=a.per<b.per?'A':b.per<a.per?'B':'empate';const saving=a.per===b.per?0:Math.abs(a.per-b.per)/Math.max(a.per,b.per)*100;out.textContent='Oferta A: '+money(a.per)+'/'+unit+'. Oferta B: '+money(b.per)+'/'+unit+'. Melhor valor: '+winner+(winner==='empate'?'.':' ('+fmt(saving)+'% menor por '+unit+').');return}}catch(e){out.textContent='Revise os valores informados. Use números positivos e unidades compatíveis.'}})})();`;

function simplePage(title, body, path) {
  return `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(title)} | PackValue Tools</title><link rel="canonical" href="${ORIGIN}${path}"><style>${CSS}</style></head><body><header><a class="brand" href="/">PackValue Tools</a></header><main class="home"><article><h1>${esc(title)}</h1><div class="content">${body}</div></article></main><footer><a href="/">Início</a></footer></body></html>`;
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/$/, "") || "/";
    if (request.method !== "GET" && request.method !== "HEAD") return json({ok:false,error:"method_not_allowed"},405,{allow:"GET, HEAD"});
    if (path === "/health") return json({ok:true,service:"packvalue-tools",version:VERSION,greenfield:true,ugi_content:false,payment:false,pii_collection:false});
    if (path === "/robots.txt") return new Response(`User-agent: *\nAllow: /\nSitemap: ${ORIGIN}/sitemap.xml\n`,{headers:{"content-type":"text/plain; charset=utf-8","cache-control":"public,max-age=3600"}});
    if (path === "/sitemap.xml") { const paths=["/",...Object.keys(TOOLS),"/sobre","/privacidade"]; const xml=`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${paths.map(p=>`<url><loc>${ORIGIN}${p}</loc><changefreq>weekly</changefreq></url>`).join("")}</urlset>`; return new Response(xml,{headers:{"content-type":"application/xml; charset=utf-8","cache-control":"public,max-age=3600"}}); }
    if (path === `/${INDEXNOW_KEY}.txt`) return new Response(INDEXNOW_KEY,{headers:{"content-type":"text/plain; charset=utf-8","cache-control":"public,max-age=86400"}});
    if (path === "/llms.txt") return new Response(`# PackValue Tools\n\nFree deterministic calculators for pack, unit-price, discount and dilution comparisons.\n\n${Object.entries(TOOLS).map(([p,t])=>`- ${ORIGIN}${p}: ${t.description}`).join("\n")}\n`,{headers:{"content-type":"text/plain; charset=utf-8"}});
    if (path === "/") return new Response(home(),{headers:{"content-type":"text/html; charset=utf-8","cache-control":"public,max-age=600"}});
    if (TOOLS[path]) return new Response(layout(TOOLS[path],path),{headers:{"content-type":"text/html; charset=utf-8","cache-control":"public,max-age=600"}});
    if (path === "/sobre") return new Response(simplePage("Sobre",`<p>PackValue Tools é um projeto independente para comparação matemática de preços, packs, descontos e rendimento. As contas são determinísticas e gratuitas.</p><p>O serviço não representa loja, fabricante ou instituição financeira.</p>`,path),{headers:{"content-type":"text/html; charset=utf-8"}});
    if (path === "/privacidade") return new Response(simplePage("Privacidade",`<p>As calculadoras desta versão executam no navegador e não pedem nome, e-mail, CPF, telefone ou dados de pagamento.</p><p>Logs técnicos de infraestrutura podem registrar dados operacionais básicos de requisição conforme a plataforma de hospedagem.</p>`,path),{headers:{"content-type":"text/html; charset=utf-8"}});
    return new Response("Not found",{status:404,headers:{"content-type":"text/plain; charset=utf-8"}});
  }
};

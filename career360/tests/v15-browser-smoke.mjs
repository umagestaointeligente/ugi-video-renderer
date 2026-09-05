import { chromium } from 'playwright';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

const root = process.env.REPO_ROOT || process.cwd();
const port = 41731;
const base = `http://127.0.0.1:${port}`;

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const mockC = `
window.C={
  $:(id)=>document.getElementById(id),
  esc:(v)=>String(v??'').replace(/[&<>\"]/g,(c)=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c])),
  sb:{
    functions:{invoke:async()=>({data:{capabilities:{photo_studio_external_ai:false,mail_delivery:false}}})},
    auth:{
      onAuthStateChange:()=>{},
      getSession:async()=>({data:{session:null}})
    }
  }
};`;

const responsiveHarness = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>
body{margin:0;font-family:Arial,sans-serif}.w{margin:auto}.tabs{display:flex}.showcase-grid,.showcase-highlights,.photo-compare,.photo-style-grid,.photo-studio-actions,.proactive-grid,.radar-mini,.my-actions,.showcase-actions{display:grid}.showcase-cover{height:150px}.showcase-avatar,.my-avatar{overflow:hidden}.showcase-avatar img,.my-avatar img{width:100%;height:100%}.photo-studio-modal{display:flex}.photo-studio-panel{overflow:auto}.photo-frame img{width:100%}
</style><script>${mockC}</script></head><body><div class="w"><section id="app"><div id="main"><div class="top"><div class="brand">LSI Career 360</div><span id="role">Candidato</span></div><div class="tabs"><button class="btn on" data-v="home">Início</button><button id="showcaseTab" class="btn">Perfil</button><button class="btn" data-v="opps">Oportunidades</button><button class="btn" data-v="agent">Meu Agente<span class="agent-badge">1</span></button><details id="moreNav" class="more-nav"><summary>Mais</summary><div class="more-pop">Menu</div></details><button class="btn" data-v="career">Carreira</button><button class="btn" data-v="support">Suporte</button><button id="masterTab" class="btn">Master</button></div><div class="showcase-shell"><div class="showcase-cover"></div><div class="showcase-body"><div class="showcase-identity"><div class="showcase-avatar"><img alt="avatar" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='500'%3E%3Crect width='100%25' height='100%25' fill='%23ddd'/%3E%3C/svg%3E"></div><div><div class="showcase-name"><h1>Nome profissional com texto comprido para testar quebra</h1></div><div class="showcase-headline">Headline profissional</div></div><div class="showcase-privacy">Só você vê por enquanto</div></div><div class="showcase-actions"><button class="btn">Copiar</button><button class="btn">Baixar currículo</button></div><div class="showcase-grid"><div class="showcase-card"><p>Conteúdo principal</p><div class="showcase-highlights"><div>Um</div><div>Dois</div></div></div><div class="showcase-side-stack"><div class="showcase-card">Lateral</div><div class="showcase-leadership">Liderança</div></div></div></div></div><div class="photo-studio-modal"><div class="photo-studio-panel"><button class="photo-studio-close">×</button><div class="photo-provider">Aguardando estado</div><div class="photo-compare"><div class="photo-frame"><img alt="original" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='500'%3E%3Crect width='100%25' height='100%25' fill='%23ccc'/%3E%3C/svg%3E"></div><div class="photo-frame"><img alt="professional" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='500'%3E%3Crect width='100%25' height='100%25' fill='%23bbb'/%3E%3C/svg%3E"></div></div><div class="photo-studio-actions"><button class="btn">Usar versão</button><button class="btn">Gerar outra</button></div></div></div><div class="proactive-grid"><div>A</div><div>B</div><div>C</div><div>D</div></div><div class="radar-mini"><div><strong>1</strong></div><div><strong>2</strong></div><div><strong>3</strong></div></div><button class="eye">👁</button><button class="photo-studio-btn">✨ Melhorar</button></div></section></div><script type="module" src="/career360/frontend/app-l.js"></script></body></html>`;

const photoHarness = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>body{margin:0;font-family:Arial,sans-serif}.tabs{display:flex}.photo-controls{min-height:1px}.my-avatar{width:96px;height:96px}.my-avatar img{width:100%;height:100%;object-fit:cover}</style><script>
const originalSvg="data:image/svg+xml;charset=utf-8,"+encodeURIComponent("<svg xmlns='http://www.w3.org/2000/svg' width='400' height='500'><rect width='400' height='500' fill='#d8dde5'/><circle cx='200' cy='185' r='85' fill='#c2a18a'/><rect x='105' y='280' width='190' height='180' rx='50' fill='#596579'/></svg>");
let generated=null;window.__uploads=0;window.__segClosed=false;
function state(){return {original:{id:'orig',url:originalSvg},selected:{id:'orig',url:originalSvg},variants:generated?[generated]:[],style_plan:{style_key:'professional',title:'Profissional natural',career_basis:'Gerente / Head',background:'neutro claro',presentation:'clássica'},capabilities:{ai_generation:false},matching_usage:false}}
${mockC.replace('getSession:async()=>({data:{session:null}})','getSession:async()=>({data:{session:{access_token:\'test-token\'}}})')}
window.SelfieSegmentation=class{setOptions(){} onResults(fn){this.fn=fn} send(){return Promise.reject(new Error('SEGMENTATION_RUNTIME_FAIL'))} close(){window.__segClosed=true}};
window.fetch=async(url,opts={})=>{if(!String(url).includes('career-photo-studio'))throw new Error('unexpected fetch '+url);const method=opts.method||'GET';if(method==='GET')return new Response(JSON.stringify(state()),{status:200,headers:{'content-type':'application/json'}});if(opts.body instanceof FormData){window.__uploads++;generated={id:'v1',provider:'local-studio-v1',style_key:'professional',status:'generated',url:originalSvg};return new Response(JSON.stringify({status:'VARIANT_READY',variant:generated}),{status:201,headers:{'content-type':'application/json'}})}const body=JSON.parse(opts.body||'{}');if(body.action==='set_style')return new Response(JSON.stringify({status:'STYLE_UPDATED'}),{status:200,headers:{'content-type':'application/json'}});if(body.action==='accept')return new Response(JSON.stringify({status:'VARIANT_ACCEPTED'}),{status:200,headers:{'content-type':'application/json'}});if(body.action==='keep_original')return new Response(JSON.stringify({status:'ORIGINAL_SELECTED'}),{status:200,headers:{'content-type':'application/json'}});return new Response(JSON.stringify({status:'OK'}),{status:200,headers:{'content-type':'application/json'}})};
</script></head><body><section id="app"><div id="professionalV8"><div class="photo-controls"></div></div><div class="my-avatar"><img alt="avatar" src="${'${originalSvg}'}"></div></section><script>document.querySelector('.my-avatar img').src=originalSvg;</script><script type="module" src="/career360/frontend/app-k.js"></script><script type="module" src="/career360/frontend/app-l.js"></script></body></html>`;

const server = http.createServer(async (req, res) => {
  try {
    if (req.url === '/v15.html') {
      res.writeHead(200, {'content-type':'text/html; charset=utf-8'}); res.end(responsiveHarness); return;
    }
    if (req.url === '/photo.html') {
      res.writeHead(200, {'content-type':'text/html; charset=utf-8'}); res.end(photoHarness); return;
    }
    const rel = decodeURIComponent((req.url || '/').replace(/^\//,''));
    const file = path.join(root, rel);
    if (!file.startsWith(root)) throw new Error('invalid path');
    const data = await fs.readFile(file);
    const type = file.endsWith('.js') ? 'text/javascript; charset=utf-8' : file.endsWith('.css') ? 'text/css; charset=utf-8' : 'application/octet-stream';
    res.writeHead(200, {'content-type':type}); res.end(data);
  } catch {
    res.writeHead(404); res.end('not found');
  }
});
await new Promise(resolve=>server.listen(port,'127.0.0.1',resolve));

const browser = await chromium.launch({headless:true});
try {
  const page = await browser.newPage();
  const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});

  for (const width of [360,412,768,1180]) {
    await page.setViewportSize({width,height:900});
    await page.goto(`${base}/v15.html`,{waitUntil:'networkidle'});
    await page.evaluate(()=>{window.__mutationCount=0;new MutationObserver(m=>window.__mutationCount+=m.length).observe(document.getElementById('app'),{childList:true,subtree:true});document.getElementById('app').appendChild(document.createElement('i'))});
    await page.waitForTimeout(850);
    const r=await page.evaluate(()=>{
      const cols=(sel)=>getComputedStyle(document.querySelector(sel)).gridTemplateColumns.trim().split(/\s+/).filter(Boolean).length;
      const rect=(sel)=>document.querySelector(sel).getBoundingClientRect();
      const h=(sel)=>rect(sel).height,w=(sel)=>rect(sel).width;
      return {vw:innerWidth,scrollWidth:document.documentElement.scrollWidth,navPosition:getComputedStyle(document.querySelector('.tabs')).position,showcaseCols:cols('.showcase-grid'),highlightCols:cols('.showcase-highlights'),photoCols:cols('.photo-compare'),photoActionCols:cols('.photo-studio-actions'),closeH:h('.photo-studio-close'),closeW:w('.photo-studio-close'),eyeH:h('.eye'),eyeW:w('.eye'),improveH:h('.photo-studio-btn'),photoPanelH:h('.photo-studio-panel'),datasetPhoto:document.documentElement.dataset.photoAi,homeText:document.querySelector('[data-v="home"]').textContent,profileText:document.getElementById('showcaseTab').textContent,mutationCount:window.__mutationCount};
    });
    assert(r.scrollWidth<=width+1,`horizontal overflow at ${width}: ${r.scrollWidth}`);
    assert(r.closeH>=44&&r.closeW>=44,`photo close touch target <44 at ${width}: ${r.closeW}x${r.closeH}`);
    assert(r.eyeH>=44&&r.eyeW>=44,`eye touch target <44 at ${width}: ${r.eyeW}x${r.eyeH}`);
    assert(r.improveH>=44,`improve touch target <44 at ${width}: ${r.improveH}`);
    assert(r.datasetPhoto==='unknown',`capability should stay unknown without ui-state at ${width}: ${r.datasetPhoto}`);
    assert(r.homeText.includes('Minha Página')&&r.profileText.includes('Meu Perfil'),`canonical nav labels missing at ${width}`);
    assert(r.mutationCount<25,`mutation observer did not settle at ${width}: ${r.mutationCount}`);
    if(width<=768){assert(r.navPosition==='fixed',`mobile nav not fixed at ${width}`);assert(r.showcaseCols===1,`showcase not single column at ${width}`);assert(r.highlightCols===1,`highlights not single column at ${width}`);assert(r.photoCols===1,`photo compare not single column at ${width}`);assert(r.photoPanelH<=900*.94,`photo panel exceeds mobile viewport at ${width}`)}
    if(width<=430)assert(r.photoActionCols===1,`photo actions not single column at ${width}`);
    if(width===1180){assert(r.showcaseCols===2,`desktop showcase should be two columns`);assert(r.photoCols===2,`desktop photo compare should be two columns`)}
    console.log(`RESPONSIVE_${width}=PASS mutations=${r.mutationCount}`);
  }
  assert(errors.length===0,`responsive harness browser errors: ${errors.join(' | ')}`);
  await page.close();

  const photo=await browser.newPage({viewport:{width:360,height:900}});
  const photoErrors=[];photo.on('pageerror',e=>photoErrors.push(String(e)));photo.on('console',m=>{if(m.type()==='error')photoErrors.push(m.text())});
  await photo.goto(`${base}/photo.html`,{waitUntil:'networkidle'});
  await photo.locator('.photo-studio-btn').first().click();
  await photo.locator('#photoCreate').click();
  await photo.waitForFunction(()=>window.__uploads===1,{timeout:15000});
  await photo.waitForFunction(()=>document.getElementById('photoStudioMsg')?.textContent.includes('Versão pronta'),{timeout:15000});
  const p=await photo.evaluate(()=>({uploads:window.__uploads,segClosed:window.__segClosed,msg:document.getElementById('photoStudioMsg').textContent,compareCols:getComputedStyle(document.querySelector('.photo-compare')).gridTemplateColumns.trim().split(/\s+/).filter(Boolean).length,scrollWidth:document.documentElement.scrollWidth}));
  assert(p.uploads===1,'Photo Studio fallback did not upload exactly one local variant');
  assert(p.segClosed===true,'Photo Studio did not close failed segmenter');
  assert(p.msg.includes('Versão pronta'),'Photo Studio fallback did not complete successfully');
  assert(p.compareCols===1,'Photo Studio compare is not single-column at 360px');
  assert(p.scrollWidth<=361,`Photo Studio horizontal overflow: ${p.scrollWidth}`);
  assert(photoErrors.length===0,`Photo Studio browser errors: ${photoErrors.join(' | ')}`);
  console.log('PHOTO_STUDIO_SEGMENTATION_RUNTIME_FALLBACK=PASS');
  await photo.close();
} finally {
  await browser.close();
  await new Promise(resolve=>server.close(resolve));
}

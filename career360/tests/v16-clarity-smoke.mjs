import { chromium } from 'playwright';
import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

const root = process.env.REPO_ROOT || process.cwd();
const port = 41732;
const base = `http://127.0.0.1:${port}`;

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const harness = `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><style>
*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif}.w{max-width:1180px;margin:auto;padding:10px}.card{padding:18px;border:1px solid #eee;border-radius:18px}.stack{display:grid;gap:12px}.tabs{display:flex;gap:6px}.btn,.tinybtn,input{min-height:44px}.muted{color:#667085}.row{display:flex;gap:8px}.row input{flex:1}.chat{min-height:160px}.proactive-head{display:flex;justify-content:space-between}.proactive-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}.proactive-metric{padding:10px}.proactive-alert{padding:10px}.v{display:none}.v.on{display:block}
</style><script>
window.C={$:(id)=>document.getElementById(id)};
window.__asked=[];
</script></head><body><div class="w"><section id="app"><div id="main"><div class="tabs"><button class="btn" data-v="home">Minha Página</button><button class="btn" data-v="agent">Meu Agente</button></div>
<div id="home" class="v on stack"><div class="card hero"><h2>Olá</h2><p class="muted">Conte uma vez. Confirme o que importa. O agente organiza o resto.</p></div><div class="card profilebox"><div class="profilehead"><div><h3>Seu perfil</h3><p class="muted">O que o Career 360 já conhece e você confirmou.</p></div></div></div><div class="card radarbox"><div class="radarhead"><div><h3>Seu radar</h3><p class="muted">O agente pesquisa, filtra e explica. Você não precisa cadastrar vagas manualmente.</p></div></div></div>
<div id="proactiveCard" class="card proactive-card"><div class="proactive-head"><div><h3>Atualizações do seu agente</h3><div class="proactive-sub">Resumo automático a cada 12h · última atualização 05/09 22:00 · próxima prevista 06/09 10:00</div></div><div class="proactive-pulse">Agente trabalhando</div></div><div class="proactive-summary"><strong>Desde a última atualização</strong><div class="proactive-grid"><div class="proactive-metric"><span>Analisadas</span><b>18</b></div><div class="proactive-metric"><span>Qualificadas</span><b>4</b></div><div class="proactive-metric"><span>Candidaturas</span><b>1</b></div><div class="proactive-metric"><span>Respostas</span><b>2</b></div></div><div class="proactive-actions"><button id="proactiveNow" class="btn sec">Atualizar agora</button></div></div><div class="proactive-alert"><div class="proactive-alert-title">Confirmação necessária</div><div class="proactive-alert-body">Uma oportunidade precisa da sua confirmação antes de qualquer próximo passo.</div><button class="tinybtn proactive-read">Marcar como lido</button></div></div></div>
<div id="opps" class="v"><div class="card radarbox"><div class="radarhead"><div><h2>Oportunidades</h2><p class="muted">Aqui entram somente oportunidades que o agente encontrou e avaliou para você.</p></div></div><div class="notice-sec"><strong>Você não precisa preencher empresa, cargo, salário ou competências da vaga.</strong><br>Essa coleta é trabalho do agente. O radar automático pesquisa fontes públicas estruturadas.</div></div></div>
<div id="agent" class="v card"><h2>Meu Agente</h2><div id="chat" class="chat"><div class="bubble ai">Posso verificar oportunidades, currículo, privacidade e pendências.</div></div><div class="row" style="margin-top:10px"><input id="question" placeholder="Ex.: quais são minhas melhores oportunidades?"><button id="ask" class="btn">Enviar</button></div></div>
</div></section></div><script>
document.getElementById('ask').onclick=()=>{window.__asked.push(document.getElementById('question').value);document.getElementById('question').value='';};
</script><script type="module" src="/career360/frontend/app-m.js"></script></body></html>`;

const server = http.createServer(async (req, res) => {
  try {
    if (req.url === '/v16.html') {
      res.writeHead(200, {'content-type':'text/html; charset=utf-8'});
      res.end(harness);
      return;
    }
    const rel = decodeURIComponent((req.url || '/').replace(/^\//,''));
    const file = path.join(root, rel);
    if (!file.startsWith(root)) throw new Error('invalid path');
    const data = await fs.readFile(file);
    res.writeHead(200, {'content-type': file.endsWith('.js') ? 'text/javascript; charset=utf-8' : 'application/octet-stream'});
    res.end(data);
  } catch {
    res.writeHead(404); res.end('not found');
  }
});
await new Promise(resolve=>server.listen(port,'127.0.0.1',resolve));

const browser = await chromium.launch({headless:true});
try {
  for (const width of [360,412,768,1180]) {
    const page = await browser.newPage({viewport:{width,height:900}});
    const errors=[];
    page.on('pageerror',e=>errors.push(String(e)));
    page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
    await page.goto(`${base}/v16.html`,{waitUntil:'networkidle'});
    await page.waitForTimeout(350);

    const result = await page.evaluate(() => ({
      dataset: document.documentElement.dataset.careerUiClarity,
      scrollWidth: document.documentElement.scrollWidth,
      hero: document.querySelector('#home .hero .muted')?.textContent,
      profile: document.querySelector('#home .profilebox .muted')?.textContent,
      radar: document.querySelector('#home .radarbox .muted')?.textContent,
      opps: document.querySelector('#opps .radarhead .muted')?.textContent,
      notice: document.querySelector('#opps .notice-sec')?.textContent.replace(/\s+/g,' ').trim(),
      agentShells: document.querySelectorAll('#agent .agent-shell').length,
      quicks: document.querySelectorAll('#agent .agent-quick button').length,
      firstBubble: document.querySelector('#chat .bubble.ai')?.textContent,
      placeholder: document.getElementById('question')?.placeholder,
      pulse: document.querySelector('.proactive-pulse')?.textContent,
      proactiveTitle: document.querySelector('.proactive-head h3')?.textContent,
      proactiveSubDisplay: getComputedStyle(document.querySelector('.proactive-sub')).display,
      readText: document.querySelector('.proactive-read')?.textContent,
      askHeight: document.getElementById('ask').getBoundingClientRect().height,
      quickHeight: document.querySelector('.agent-quick button').getBoundingClientRect().height
    }));

    assert(result.dataset==='v16',`V16 dataset missing at ${width}`);
    assert(result.scrollWidth<=width+1,`horizontal overflow at ${width}: ${result.scrollWidth}`);
    assert(result.hero==='Você confirma. O agente cuida do resto.',`hero copy not compact at ${width}`);
    assert(result.profile==='Dados confirmados por você.',`profile copy not compact at ${width}`);
    assert(result.radar==='Seu agente pesquisa e filtra.',`radar copy not compact at ${width}`);
    assert(result.opps==='Só o que passou pelos seus filtros.',`opportunities copy not compact at ${width}`);
    assert(result.notice.includes('Radar automático')&&result.notice.includes('Você revisa.'),`opportunity notice not compact at ${width}`);
    assert(result.agentShells===1,`agent shell count ${result.agentShells} at ${width}`);
    assert(result.quicks===3,`quick actions count ${result.quicks} at ${width}`);
    assert(result.firstBubble==='O que você quer ver agora?',`agent first bubble too verbose at ${width}`);
    assert(result.placeholder==='Pergunte sobre sua carreira',`agent placeholder not compact at ${width}`);
    assert(result.pulse==='Trabalhando',`agent pulse not compact at ${width}`);
    assert(result.proactiveTitle==='Seu agente',`proactive title not compact at ${width}`);
    assert(result.proactiveSubDisplay==='none',`operational cadence still visible at ${width}`);
    assert(result.readText==='Ok',`notification action not compact at ${width}`);
    assert(result.askHeight>=44,`send button touch target <44 at ${width}`);
    assert(result.quickHeight>=38,`quick action height <38 at ${width}`);
    assert(errors.length===0,`browser errors at ${width}: ${errors.join(' | ')}`);

    await page.locator('.agent-quick button').first().click();
    await page.waitForTimeout(50);
    const asked = await page.evaluate(()=>window.__asked.slice());
    assert(asked.length===1&&asked[0]==='Quais são minhas melhores oportunidades agora?',`quick action did not delegate to canonical ask handler at ${width}`);

    await page.evaluate(()=>{
      window.__mutations=0;
      new MutationObserver(m=>window.__mutations+=m.length).observe(document.getElementById('app'),{childList:true,subtree:true});
      const card=document.getElementById('proactiveCard');
      card.querySelector('.proactive-head h3').textContent='Atualizações do seu agente';
      card.querySelector('.proactive-pulse').textContent='Agente trabalhando';
      card.querySelector('.proactive-summary > strong').textContent='Desde a última atualização';
      card.appendChild(document.createElement('i'));
    });
    await page.waitForTimeout(500);
    const settled = await page.evaluate(()=>({
      shells:document.querySelectorAll('#agent .agent-shell').length,
      quicks:document.querySelectorAll('#agent .agent-quick button').length,
      title:document.querySelector('.proactive-head h3').textContent,
      pulse:document.querySelector('.proactive-pulse').textContent,
      mutations:window.__mutations
    }));
    assert(settled.shells===1&&settled.quicks===3,`V16 duplicated UI after mutation at ${width}`);
    assert(settled.title==='Seu agente'&&settled.pulse==='Trabalhando',`V16 did not recompact dynamic proactive render at ${width}`);
    assert(settled.mutations<35,`V16 mutation observer did not settle at ${width}: ${settled.mutations}`);
    console.log(`CLARITY_${width}=PASS mutations=${settled.mutations}`);
    await page.close();
  }
  console.log('V16_AGENT_QUICK_ACTIONS=PASS');
  console.log('V16_DYNAMIC_PROACTIVE_RECOMPACT=PASS');
} finally {
  await browser.close();
  await new Promise(resolve=>server.close(resolve));
}

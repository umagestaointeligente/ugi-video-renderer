from pathlib import Path

APP=Path('career360/frontend/app-m.js')
TEST=Path('career360/tests/v16-clarity-smoke.mjs')

s=APP.read_text()
old="function compactStaticCopy() {\n  setText(document.querySelector('#home .hero .muted'), 'Você confirma. O agente cuida do resto.');"
new="function compactStaticCopy() {\n  setText(document.querySelector('#auth > p.muted'), 'Você confirma o que importa. O Career 360 organiza sua busca.');\n  setText(document.querySelector('#home .hero .muted'), 'Você confirma. O agente cuida do resto.');"
if old not in s:
    raise SystemExit('app-m auth anchor missing')
s=s.replace(old,new,1)
APP.write_text(s)

t=TEST.read_text()
old_body='<style>\n*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif}.w{max-width:1180px;margin:auto;padding:10px}.card{padding:18px;border:1px solid #eee;border-radius:18px}.stack{display:grid;gap:12px}.tabs{display:flex;gap:6px}.btn,.tinybtn,input{min-height:44px}.muted{color:#667085}.row{display:flex;gap:8px}.row input{flex:1}.chat{min-height:160px}.proactive-head{display:flex;justify-content:space-between}.proactive-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}.proactive-metric,.proactive-alert{padding:10px}.v{display:block}\n</style><script>window.C={$:(id)=>document.getElementById(id)};window.__asked=[];</script></head><body><div class="w"><section id="app">'
new_body='<style>\n*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif}.w{max-width:1180px;margin:auto;padding:10px}.card{padding:18px;border:1px solid #eee;border-radius:18px}.stack{display:grid;gap:12px}.tabs{display:flex;gap:6px}.btn,.tinybtn,input{min-height:44px}.muted{color:#667085}.row{display:flex;gap:8px}.row input{flex:1}.chat{min-height:160px}.proactive-head{display:flex;justify-content:space-between}.proactive-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}.proactive-metric,.proactive-alert{padding:10px}.v{display:block}\n</style><script>window.C={$:(id)=>document.getElementById(id)};window.__asked=[];</script></head><body><div class="w"><section id="auth" class="card auth"><p class="muted">Enquanto você trabalha na sua carreira, seu agente trabalha na próxima oportunidade.</p></section><section id="app">'
if old_body not in t:
    raise SystemExit('test harness body anchor missing')
t=t.replace(old_body,new_body,1)
old_eval="const r=await page.evaluate(()=>({dataset:document.documentElement.dataset.careerUiClarity,scrollWidth:document.documentElement.scrollWidth,hero:"
new_eval="const r=await page.evaluate(()=>({dataset:document.documentElement.dataset.careerUiClarity,scrollWidth:document.documentElement.scrollWidth,authCopy:document.querySelector('#auth > p.muted').textContent,hero:"
if old_eval not in t:
    raise SystemExit('test evaluate anchor missing')
t=t.replace(old_eval,new_eval,1)
old_assert="assert(r.dataset==='v16',`dataset missing ${width}`);assert(r.scrollWidth<=width+1,`overflow ${width}: ${r.scrollWidth}`);assert(r.hero==='Você confirma. O agente cuida do resto.',`hero ${width}`);"
new_assert="assert(r.dataset==='v16',`dataset missing ${width}`);assert(r.scrollWidth<=width+1,`overflow ${width}: ${r.scrollWidth}`);assert(r.authCopy==='Você confirma o que importa. O Career 360 organiza sua busca.',`auth truth ${width}`);assert(r.hero==='Você confirma. O agente cuida do resto.',`hero ${width}`);"
if old_assert not in t:
    raise SystemExit('test assertion anchor missing')
t=t.replace(old_assert,new_assert,1)
old_tail="console.log('V16_AGENT_QUICK_ACTIONS=PASS');console.log('V16_DYNAMIC_PROACTIVE_RECOMPACT=PASS');console.log('V16_TRUTHFUL_RUNTIME_DERIVATION=PASS');"
new_tail="console.log('V16_AGENT_QUICK_ACTIONS=PASS');console.log('V16_DYNAMIC_PROACTIVE_RECOMPACT=PASS');console.log('V16_TRUTHFUL_RUNTIME_DERIVATION=PASS');console.log('V16_AUTH_TRUTHFUL_COPY=PASS');"
if old_tail not in t:
    raise SystemExit('test console anchor missing')
t=t.replace(old_tail,new_tail,1)
TEST.write_text(t)
print('V16_AUTH_TRUTH_PATCH=PASS')

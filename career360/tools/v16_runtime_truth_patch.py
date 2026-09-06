from pathlib import Path
import re
import sys

APP = Path('career360/frontend/app-m.js')
TEST = Path('career360/tests/v16-clarity-smoke.mjs')
INDEX = Path('career360/frontend/index.html')


def once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 anchor, found {count}')
    return text.replace(old, new, 1)


def patch():
    s = APP.read_text()
    old_fn = """function compactRuntimePulse(pulse) {
  if (!pulse) return;
  const raw = (pulse.textContent || '').trim();
  if (!raw) return;
  const low = raw.toLowerCase();
  let next = raw;
  if (low.includes('atualiz') || low.includes('carreg')) next = 'Atualizando';
  else if (low.includes('paus')) next = 'Pausado';
  else if (low.includes('erro') || low.includes('falh') || low.includes('aten')) next = 'Atenção';
  else if (low.includes('trabalh') || low.includes('ativo') || low.includes('rodando')) next = 'Ativo';
  else if (raw.length > 18) next = 'Status';
  setText(pulse, next);
}
"""
    new_fn = """function setTruthfulProactivePulse(pulse, summary, now) {
  if (!pulse) return;
  const summaryText = (summary?.textContent || '').toLowerCase();
  const hasDigest = !!summary && !summaryText.includes('primeiro');
  const next = now?.disabled ? 'Atualizando' : (hasDigest ? 'Atualizado' : 'Aguardando');
  setText(pulse, next);
}
"""
    s = once(s, old_fn, new_fn, 'runtime pulse function')

    old_block = """  const pulse = card.querySelector('.proactive-pulse');
  compactRuntimePulse(pulse);
  const summary = card.querySelector('.proactive-summary > strong');
  if (summary) {
    const next = summary.textContent.includes('primeiro') ? 'Primeiro resumo' : 'Resumo';
    setText(summary, next);
  }
  const now = $('proactiveNow');
  setText(now, now?.disabled ? 'Atualizando…' : 'Atualizar');
"""
    new_block = """  const pulse = card.querySelector('.proactive-pulse');
  const summary = card.querySelector('.proactive-summary > strong');
  const now = $('proactiveNow');
  setTruthfulProactivePulse(pulse, summary, now);
  if (summary) {
    const next = summary.textContent.toLowerCase().includes('primeiro') ? 'Primeiro resumo' : 'Resumo';
    setText(summary, next);
  }
  setText(now, now?.disabled ? 'Atualizando…' : 'Atualizar');
"""
    s = once(s, old_block, new_block, 'compact proactive block')
    APP.write_text(s)

    q = TEST.read_text()
    q = once(q, "assert(r.pulse==='Ativo'&&r.title==='Seu agente'", "assert(r.pulse==='Atualizado'&&r.title==='Seu agente'", 'initial truthful expectation')
    q = once(q, "c.querySelector('.proactive-pulse').textContent='Atualizando oportunidades';c.appendChild(document.createElement('i'))", "document.getElementById('proactiveNow').disabled=true;c.querySelector('.proactive-pulse').textContent='Agente trabalhando';c.appendChild(document.createElement('i'))", 'dynamic updating state')
    old_dynamic = """const s=await page.evaluate(()=>({shells:document.querySelectorAll('#agent .agent-shell').length,quicks:document.querySelectorAll('#agent .agent-quick button').length,title:document.querySelector('.proactive-head h3').textContent,pulse:document.querySelector('.proactive-pulse').textContent,mutations:window.__mutations}));assert(s.shells===1&&s.quicks===3,`duplicates ${width}`);assert(s.title==='Seu agente'&&s.pulse==='Atualizando',`dynamic recompact ${width}`);assert(s.mutations<35,`observer churn ${width}: ${s.mutations}`);console.log(`CLARITY_${width}=PASS mutations=${s.mutations}`);await page.close();
"""
    new_dynamic = """const s=await page.evaluate(()=>({shells:document.querySelectorAll('#agent .agent-shell').length,quicks:document.querySelectorAll('#agent .agent-quick button').length,title:document.querySelector('.proactive-head h3').textContent,pulse:document.querySelector('.proactive-pulse').textContent,mutations:window.__mutations}));assert(s.shells===1&&s.quicks===3,`duplicates ${width}`);assert(s.title==='Seu agente'&&s.pulse==='Atualizando',`dynamic recompact ${width}`);assert(s.mutations<35,`observer churn ${width}: ${s.mutations}`);
  await page.evaluate(()=>{document.getElementById('proactiveNow').disabled=false;document.querySelector('.proactive-summary > strong').textContent='Primeiro resumo';document.getElementById('proactiveCard').appendChild(document.createElement('i'))});await page.waitForTimeout(300);const waiting=await page.evaluate(()=>document.querySelector('.proactive-pulse').textContent);assert(waiting==='Aguardando',`waiting state ${width}: ${waiting}`);console.log(`CLARITY_${width}=PASS mutations=${s.mutations}`);await page.close();
"""
    q = once(q, old_dynamic, new_dynamic, 'waiting state test')
    q = once(q, "console.log('V16_AGENT_QUICK_ACTIONS=PASS');console.log('V16_DYNAMIC_PROACTIVE_RECOMPACT=PASS');", "console.log('V16_AGENT_QUICK_ACTIONS=PASS');console.log('V16_DYNAMIC_PROACTIVE_RECOMPACT=PASS');console.log('V16_TRUTHFUL_RUNTIME_DERIVATION=PASS');", 'truthful final evidence')
    TEST.write_text(q)
    print('V16_RUNTIME_TRUTH_SOURCE=PASS')


def repin(sha):
    s = INDEX.read_text()
    pat = r'@([0-9a-f]{40})/career360/frontend/app-m\.js'
    hits = re.findall(pat, s)
    if len(hits) != 1:
        raise SystemExit(f'expected one app-m pin, got {len(hits)}')
    INDEX.write_text(re.sub(pat, f'@{sha}/career360/frontend/app-m.js', s, count=1))
    print('V16_RUNTIME_TRUTH_REPIN=PASS')


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'patch':
        patch()
    elif len(sys.argv) == 3 and sys.argv[1] == 'repin':
        repin(sys.argv[2])
    else:
        raise SystemExit('usage: patch | repin <sha>')

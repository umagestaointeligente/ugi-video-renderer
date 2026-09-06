from pathlib import Path
import sys

APP = Path('career360/frontend/app-m.js')
TEST = Path('career360/tests/v16-clarity-smoke.mjs')
INDEX = Path('career360/frontend/index.html')
SMOKE = Path('.github/workflows/career360-v16-clarity-smoke.yml')


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 anchor, found {count}')
    return text.replace(old, new, 1)


def patch_ui():
    s = APP.read_text()

    s = replace_once(
        s,
        ".btn{border-radius:13px;transition:transform .15s ease,box-shadow .15s ease,background .15s ease}.btn:not(.sec){box-shadow:0 5px 14px rgba(101,71,245,.18)}.btn:active{transform:translateY(1px)}\n",
        ".btn{border-radius:13px;transition:transform .15s ease,box-shadow .15s ease,background .15s ease}.btn:not(.sec){box-shadow:0 5px 14px rgba(101,71,245,.18)}.btn:active{transform:translateY(1px)}\n.btn:focus-visible,.tinybtn:focus-visible,.agent-quick button:focus-visible,input:focus-visible,textarea:focus-visible,select:focus-visible{outline:3px solid rgba(101,71,245,.24);outline-offset:2px}\n",
        'focus styles')

    s = replace_once(
        s,
        ".notice-sec{border:1px solid var(--v16-line)!important;background:var(--v16-soft)!important;border-radius:14px!important;padding:12px 14px!important;color:#4b5563!important;font-size:13px!important;line-height:1.4!important}\n",
        ".notice-sec{border:1px solid var(--v16-line)!important;background:var(--v16-soft)!important;border-radius:14px!important;padding:12px 14px!important;color:#4b5563!important;font-size:13px!important;line-height:1.4!important}\n#onboarding .step>p.muted{margin-top:-2px!important;max-width:620px}#onboarding .helper{font-size:12px!important;line-height:1.35!important}#support{width:min(720px,100%);margin-inline:auto}#support>h2{margin-bottom:12px}#support textarea{min-height:120px}\n",
        'secondary flow styles')

    s = replace_once(
        s,
        "@media(max-width:430px){.proactive-card{padding:14px!important}.proactive-head h3{font-size:17px}.proactive-pulse{font-size:10.5px!important}.proactive-metric b{font-size:20px!important}.agent-mark{width:36px;height:36px}.agent-title{font-size:17px}.agent-body{padding:12px}.agent-topline{padding:13px 12px 11px}.agent-quick{margin-right:-12px;padding-right:12px}}\n",
        "@media(max-width:430px){.proactive-card{padding:14px!important}.proactive-head h3{font-size:17px}.proactive-pulse{font-size:10.5px!important}.proactive-metric b{font-size:20px!important}.agent-mark{width:36px;height:36px}.agent-title{font-size:17px}.agent-body{padding:12px}.agent-topline{padding:13px 12px 11px}.agent-quick{margin-right:-12px;padding-right:12px}}\n@media(prefers-reduced-motion:reduce){*,*::before,*::after{scroll-behavior:auto!important;transition:none!important;animation:none!important}}\n",
        'reduced motion')

    secondary = """function compactSecondaryCopy() {
  const pairs = [
    ['#onboarding .obhead h1', 'Configure seu agente'],
    ['#onboarding .obhead .muted', 'Só o essencial. Você revisa depois.'],
    ['#s1 h2', 'Sobre você'],
    ['#s1 > p.muted', 'Comece pelo básico.'],
    ['#s2 h2', 'O que você procura?'],
    ['#s2 > p.muted', 'Isso guia seu radar.'],
    ['#s3 h2', 'Privacidade'],
    ['#s3 > p.muted', 'Proteja sua busca.'],
    ['#s4 h2', 'Sua experiência'],
    ['#s4 > p.muted', 'Marque o que realmente faz.'],
    ['#s5 h2', 'Currículo'],
    ['#s5 > p.muted', 'Adicione agora ou depois. O agente organiza para você revisar.'],
    ['#s5 .filebox p.muted', 'PDF ou DOCX, até 10 MB.'],
    ['#support > h2', 'Ajuda'],
    ['#oppList > h2', 'Resultados'],
    ['#oppList .emptyradar .muted', 'Quando uma oportunidade passar pelos filtros, ela aparece aqui.']
  ];
  pairs.forEach(([selector, text]) => setText(document.querySelector(selector), text));
  setText(document.querySelector('#s1 .tip span'), 'Você pode revisar depois.');
  setText(document.querySelector('#s5 .tip span'), 'Você pode incluir depois.');
  const employerHelp = document.querySelector('#s3 .helper');
  if (employerHelp) setText(employerHelp, 'Escolha uma sugestão se aparecer.');
  const problem = $('problem');
  if (problem) problem.placeholder = 'Conte o que aconteceu';
  setText($('solve'), 'Resolver');
  setText($('lateCvGo'), 'Ler meu currículo');
  setText($('confirmCv'), 'Confirmar currículo');
  setText(document.querySelector('#career .card:nth-child(2) > p.muted'), 'O agente organiza sua trajetória para você revisar.');
}

function compactRuntimePulse(pulse) {
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

function compactProactive() {
"""
    s = replace_once(s, 'function compactProactive() {\n', secondary, 'secondary copy insertion')
    s = replace_once(s, "  const pulse = card.querySelector('.proactive-pulse');\n  setText(pulse, 'Trabalhando');\n", "  const pulse = card.querySelector('.proactive-pulse');\n  compactRuntimePulse(pulse);\n", 'truthful proactive pulse')
    s = replace_once(s, "  question.placeholder = 'Pergunte sobre sua carreira';\n  ask.setAttribute('aria-label', 'Enviar pergunta');\n", "  question.placeholder = 'Pergunte sobre sua carreira';\n  question.setAttribute('aria-label', 'Pergunte ao seu agente');\n  ask.setAttribute('aria-label', 'Enviar pergunta');\n  ask.title = 'Enviar';\n", 'agent accessibility')
    s = replace_once(s, '        </div>\n        <div class="agent-state">Trabalhando</div>\n      </div>\n', '        </div>\n      </div>\n', 'remove fake agent state')
    s = replace_once(s, '    compactStaticCopy();\n    compactProactive();\n', '    compactStaticCopy();\n    compactSecondaryCopy();\n    compactProactive();\n', 'apply secondary copy')
    APP.write_text(s)

    q = TEST.read_text()
    q = replace_once(q, '<section id="app"><div class="tabs">', '<section id="app"><div id="onboarding"><div class="obhead"><h1>Vamos preparar seu Career 360</h1><p class="muted">Em poucos passos, você nos conta o essencial. Depois o agente organiza o restante.</p></div><div id="s1" class="step"><h2>👋 Comece por aqui</h2><p class="muted">Primeiro, só o básico para seu agente saber quem você é.</p><div class="tip"><span>Não precisa deixar tudo perfeito agora.</span></div></div><div id="s2" class="step"><h2>🎯 O que você quer encontrar?</h2><p class="muted">Isso direciona seu radar de oportunidades.</p></div><div id="s3" class="step"><h2>🔒 Vamos proteger sua busca</h2><p class="muted">Sua privacidade vem antes do matching.</p><div class="helper">Se aparecer uma sugestão, toque nela.</div></div><div id="s4" class="step"><h2>✨ O que faz parte do seu trabalho?</h2><p class="muted">Selecionamos atribuições comuns ao seu cargo.</p></div><div id="s5" class="step"><h2>📄 Currículo — agora ou depois</h2><p class="muted">Você já pode ativar o agente sem currículo.</p><div class="filebox"><p class="muted">PDF textual ou DOCX, até 10 MB.</p></div><div class="tip"><span>Se preferir, ative agora e inclua o currículo depois.</span></div></div></div><div class="tabs">', 'test onboarding harness')
    q = replace_once(q, '<div id="agent" class="v card"><h2>Meu Agente</h2>', '<div id="support" class="v card"><h2>🚨 Resolver agora</h2><textarea id="problem" placeholder="Descreva o problema"></textarea><button id="solve" class="btn">Diagnosticar</button></div><div id="agent" class="v card"><h2>Meu Agente</h2>', 'test support harness')
    q = replace_once(q, "pulse:document.querySelector('.proactive-pulse').textContent,title:document.querySelector('.proactive-head h3').textContent,sub:getComputedStyle(document.querySelector('.proactive-sub')).display,read:document.querySelector('.proactive-read').textContent,askH:", "pulse:document.querySelector('.proactive-pulse').textContent,title:document.querySelector('.proactive-head h3').textContent,sub:getComputedStyle(document.querySelector('.proactive-sub')).display,read:document.querySelector('.proactive-read').textContent,agentState:document.querySelectorAll('.agent-state').length,questionAria:document.getElementById('question').getAttribute('aria-label'),onboardingTitle:document.querySelector('#onboarding .obhead h1').textContent,onboardingSub:document.querySelector('#onboarding .obhead .muted').textContent,supportTitle:document.querySelector('#support h2').textContent,supportPlaceholder:document.getElementById('problem').placeholder,askH:", 'test eval fields')
    q = replace_once(q, "assert(r.pulse==='Trabalhando'&&r.title==='Seu agente'&&r.sub==='none'&&r.read==='Ok',`proactive compact ${width}`);", "assert(r.pulse==='Ativo'&&r.title==='Seu agente'&&r.sub==='none'&&r.read==='Ok',`proactive compact ${width}`);assert(r.agentState===0,`fake agent state ${width}`);assert(r.questionAria==='Pergunte ao seu agente',`agent aria ${width}`);assert(r.onboardingTitle==='Configure seu agente'&&r.onboardingSub==='Só o essencial. Você revisa depois.',`onboarding compact ${width}`);assert(r.supportTitle==='Ajuda'&&r.supportPlaceholder==='Conte o que aconteceu',`support compact ${width}`);", 'test truthful assertions')
    q = replace_once(q, "c.querySelector('.proactive-pulse').textContent='Agente trabalhando';", "c.querySelector('.proactive-pulse').textContent='Atualizando oportunidades';", 'dynamic status input')
    q = replace_once(q, "assert(s.title==='Seu agente'&&s.pulse==='Trabalhando',`dynamic recompact ${width}`);", "assert(s.title==='Seu agente'&&s.pulse==='Atualizando',`dynamic recompact ${width}`);", 'dynamic status assertion')
    TEST.write_text(q)
    print('V16_TRUTHFUL_UX_SOURCE=PASS')


def repin(sha):
    import re
    s = INDEX.read_text()
    pat = r'@([0-9a-f]{40})/career360/frontend/app-m\.js'
    hits = re.findall(pat, s)
    if len(hits) != 1:
        raise SystemExit(f'expected one app-m pin, got {len(hits)}')
    INDEX.write_text(re.sub(pat, f'@{sha}/career360/frontend/app-m.js', s, count=1))

    x = SMOKE.read_text()
    pat2 = r"grep -F '@[0-9a-f]{40}/career360/frontend/app-m\.js' career360/frontend/index\.html >/dev/null"
    hits2 = re.findall(pat2, x)
    if len(hits2) != 1:
        raise SystemExit(f'expected one smoke pin gate, got {len(hits2)}')
    SMOKE.write_text(re.sub(pat2, f"grep -F '@{sha}/career360/frontend/app-m.js' career360/frontend/index.html >/dev/null", x, count=1))
    print('V16_REPIN_SOURCE=PASS')


if __name__ == '__main__':
    if len(sys.argv) == 1 or sys.argv[1] == 'patch':
        patch_ui()
    elif sys.argv[1] == 'repin' and len(sys.argv) == 3:
        repin(sys.argv[2])
    else:
        raise SystemExit('usage: v16_truthful_hardening.py patch | repin <sha>')

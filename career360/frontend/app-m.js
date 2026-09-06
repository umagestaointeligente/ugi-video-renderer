const { $ } = window.C;

const V16 = { applying: false };

function installStyles() {
  if ($('careerV16Clarity')) return;
  const s = document.createElement('style');
  s.id = 'careerV16Clarity';
  s.textContent = `
:root{
  --v16-ink:#1f2430;
  --v16-muted:#6b7280;
  --v16-line:#ececf3;
  --v16-surface:rgba(255,255,255,.94);
  --v16-soft:#f7f6fb;
  --v16-brand:#6547f5;
  --v16-brand-soft:#f1efff;
  --v16-good:#087a55;
  --v16-good-soft:#edfdf5;
}
body{color:var(--v16-ink);background:linear-gradient(180deg,#f9f8ff 0,#ffffff 240px);}
.card{background:var(--v16-surface);border:1px solid var(--v16-line);box-shadow:0 10px 30px rgba(34,30,70,.055);}
.hero{background:linear-gradient(135deg,#ffffff 0,#f6f3ff 100%);border-color:#e7e1ff;}
.hero h2{letter-spacing:-.02em;margin-bottom:5px}.hero .muted{font-size:14px;max-width:520px}
.brand{letter-spacing:-.02em}.brand span{font-weight:750}
.btn{border-radius:13px;transition:transform .15s ease,box-shadow .15s ease,background .15s ease}.btn:not(.sec){box-shadow:0 5px 14px rgba(101,71,245,.18)}.btn:active{transform:translateY(1px)}
.btn:focus-visible,.tinybtn:focus-visible,.agent-quick button:focus-visible,input:focus-visible,textarea:focus-visible,select:focus-visible{outline:3px solid rgba(101,71,245,.24);outline-offset:2px}
.tabs{padding:5px;border:1px solid var(--v16-line);background:rgba(255,255,255,.88);border-radius:17px;box-shadow:0 8px 24px rgba(34,30,70,.04)}
.tabs>.btn,.tabs>.more-nav>summary{border-radius:12px!important}
#home.stack{gap:14px}.profilebox,.radarbox,.proactive-card{overflow:hidden}
.profilehead h3,.radarhead h3,.proactive-head h3{letter-spacing:-.015em}
.profilebox>.profilehead .muted,.radarhead .muted{font-size:12.5px!important}
.notice-sec{border:1px solid var(--v16-line)!important;background:var(--v16-soft)!important;border-radius:14px!important;padding:12px 14px!important;color:#4b5563!important;font-size:13px!important;line-height:1.4!important}
#onboarding .step>p.muted{margin-top:-2px!important;max-width:620px}#onboarding .helper{font-size:12px!important;line-height:1.35!important}#support{width:min(720px,100%);margin-inline:auto}#support>h2{margin-bottom:12px}#support textarea{min-height:120px}

/* Proactive summary: numbers first, operational detail second. */
.proactive-card{padding:18px!important}.proactive-head{align-items:center!important}.proactive-head h3{font-size:18px}.proactive-sub{display:none!important}.proactive-pulse{background:var(--v16-good-soft)!important;color:var(--v16-good)!important;padding:6px 10px!important}.proactive-summary{background:transparent!important;border:0!important;padding:0!important;margin-top:14px!important}.proactive-summary>strong{font-size:12px;color:var(--v16-muted);font-weight:750;margin-bottom:8px!important}.proactive-grid{gap:8px!important;margin-top:0!important}.proactive-metric{background:var(--v16-soft)!important;border:1px solid #efedf8;padding:11px!important}.proactive-metric span{font-size:10.5px!important}.proactive-metric b{font-size:22px!important;letter-spacing:-.03em}.proactive-actions{margin-top:10px!important}.proactive-actions .btn{min-height:44px!important;font-size:13px!important;padding:7px 11px!important}.proactive-alert{position:relative;padding:12px 60px 12px 13px!important}.proactive-alert-body{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}.proactive-read{position:absolute;right:8px;top:8px;min-width:44px!important;min-height:44px!important;height:44px!important;padding:0 8px!important;font-size:12px!important}

/* Agent: dashboard-like, concise and action-led. */
#agent{width:min(820px,100%);margin-inline:auto;padding:0!important;background:transparent!important;border:0!important;box-shadow:none!important;}
#agent>h2{display:none}.agent-shell{background:var(--v16-surface);border:1px solid var(--v16-line);border-radius:24px;box-shadow:0 16px 44px rgba(34,30,70,.07);overflow:hidden}.agent-topline{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:18px 18px 14px;border-bottom:1px solid var(--v16-line)}.agent-id{display:flex;align-items:center;gap:11px;min-width:0}.agent-mark{width:38px;height:38px;border-radius:13px;display:grid;place-items:center;background:var(--v16-brand-soft);color:var(--v16-brand);font-weight:900;font-size:18px}.agent-title{font-size:18px;font-weight:850;letter-spacing:-.02em}.agent-caption{font-size:12px;color:var(--v16-muted);margin-top:1px}.agent-state{display:inline-flex;align-items:center;gap:6px;border-radius:999px;background:var(--v16-good-soft);color:var(--v16-good);font-size:11px;font-weight:800;padding:6px 9px;white-space:nowrap}.agent-state:before{content:'';width:7px;height:7px;border-radius:50%;background:#18b777}.agent-body{padding:16px}.agent-quick{display:flex;gap:7px;overflow-x:auto;padding:0 0 11px;scrollbar-width:none}.agent-quick::-webkit-scrollbar{display:none}.agent-quick button{flex:0 0 auto;min-height:44px!important;border:1px solid #e8e4fb;background:#faf9ff;color:#4f3fb5;border-radius:999px;padding:7px 11px;font-size:12px!important;font-weight:750;box-shadow:none}.agent-quick button:hover{background:var(--v16-brand-soft)}
#agent #chat{display:flex;flex-direction:column;gap:8px;min-height:190px;max-height:440px;overflow:auto;padding:4px 2px 12px;scroll-behavior:smooth;background:transparent!important;border:0!important}.bubble{max-width:min(86%,620px);border-radius:16px!important;padding:10px 12px!important;line-height:1.45!important;font-size:14px!important}.bubble.ai{align-self:flex-start;background:#f7f7fa!important;color:#303544!important}.bubble.me{align-self:flex-end;background:var(--v16-brand)!important;color:white!important}.agent-composer{display:grid!important;grid-template-columns:minmax(0,1fr) auto!important;gap:8px!important;margin-top:0!important;padding-top:12px;border-top:1px solid var(--v16-line)}.agent-composer input{border-radius:14px!important;background:#fbfbfd!important;border:1px solid #e4e5eb!important;min-width:0}.agent-composer .btn{min-width:52px;padding-inline:14px!important}.agent-composer .btn .send-label{display:inline}

@media(max-width:768px){
  .tabs{border-radius:0;box-shadow:0 -10px 30px rgba(20,18,40,.08)}
  #agent{padding:2px 0 8px!important}.agent-shell{border-radius:20px}.agent-topline{padding:15px 14px 12px}.agent-body{padding:14px}.agent-caption{display:none}.agent-state{font-size:10.5px}.agent-quick{margin-right:-14px;padding-right:14px}.bubble{max-width:92%;font-size:13.5px!important}#agent #chat{min-height:180px;max-height:48dvh}.agent-composer{grid-template-columns:minmax(0,1fr) 50px!important}.agent-composer .btn{min-width:50px!important;padding-inline:0!important}.agent-composer .btn .send-label{display:none}
}
@media(max-width:430px){.proactive-card{padding:14px!important}.proactive-head h3{font-size:17px}.proactive-pulse{font-size:10.5px!important}.proactive-metric b{font-size:20px!important}.agent-mark{width:36px;height:36px}.agent-title{font-size:17px}.agent-body{padding:12px}.agent-topline{padding:13px 12px 11px}.agent-quick{margin-right:-12px;padding-right:12px}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{scroll-behavior:auto!important;transition:none!important;animation:none!important}}
`;
  document.head.appendChild(s);
}

function setText(el, text) {
  if (el && el.textContent !== text) el.textContent = text;
}

function compactStaticCopy() {
  setText(document.querySelector('#home .hero .muted'), 'Você confirma. O agente cuida do resto.');
  setText(document.querySelector('#home .profilebox .profilehead .muted'), 'Dados confirmados por você.');
  setText(document.querySelector('#home .radarbox .radarhead .muted'), 'Seu agente pesquisa e filtra.');
  setText(document.querySelector('#opps .radarbox .radarhead .muted'), 'Só o que passou pelos seus filtros.');

  const notice = document.querySelector('#opps .notice-sec');
  if (notice && notice.dataset.v16Compact !== '1') {
    notice.dataset.v16Compact = '1';
    notice.innerHTML = '<strong>Radar automático</strong><span style="display:block;margin-top:2px">O agente encontra e avalia. Você revisa.</span>';
  }
}

function compactSecondaryCopy() {
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
  const card = $('proactiveCard');
  if (!card) return;
  const h = card.querySelector('.proactive-head h3');
  setText(h, 'Seu agente');
  const pulse = card.querySelector('.proactive-pulse');
  compactRuntimePulse(pulse);
  const summary = card.querySelector('.proactive-summary > strong');
  if (summary) {
    const next = summary.textContent.includes('primeiro') ? 'Primeiro resumo' : 'Resumo';
    setText(summary, next);
  }
  const now = $('proactiveNow');
  setText(now, now?.disabled ? 'Atualizando…' : 'Atualizar');
  card.querySelectorAll('.proactive-read').forEach((b) => {
    b.setAttribute('aria-label', 'Marcar como lido');
    setText(b, 'Ok');
  });
}

function ensureAgentShell() {
  const agent = $('agent');
  const chat = $('chat');
  const question = $('question');
  const ask = $('ask');
  if (!agent || !chat || !question || !ask) return;

  setText(chat.querySelector('.bubble.ai'), 'O que você quer ver agora?');
  question.placeholder = 'Pergunte sobre sua carreira';
  question.setAttribute('aria-label', 'Pergunte ao seu agente');
  ask.setAttribute('aria-label', 'Enviar pergunta');
  ask.title = 'Enviar';
  if (!ask.querySelector('.send-label')) ask.innerHTML = '<span aria-hidden="true">↑</span><span class="send-label"> Enviar</span>';

  let shell = agent.querySelector('.agent-shell');
  if (!shell) {
    shell = document.createElement('div');
    shell.className = 'agent-shell';
    shell.innerHTML = `
      <div class="agent-topline">
        <div class="agent-id">
          <div class="agent-mark" aria-hidden="true">✦</div>
          <div><div class="agent-title">Meu Agente</div><div class="agent-caption">O que importa, sem complicação.</div></div>
        </div>
      </div>
      <div class="agent-body"><div class="agent-quick" aria-label="Ações rápidas"></div></div>`;
    agent.insertBefore(shell, chat);
    const body = shell.querySelector('.agent-body');
    body.appendChild(chat);
    const row = question.closest('.row');
    if (row) {
      row.classList.add('agent-composer');
      body.appendChild(row);
    }
  }

  const quick = shell.querySelector('.agent-quick');
  if (quick && !quick.children.length) {
    const actions = [
      ['Melhores vagas', 'Quais são minhas melhores oportunidades agora?'],
      ['Preciso agir?', 'O que precisa da minha confirmação ou ação agora?'],
      ['Próximo passo', 'Qual é meu próximo passo mais importante?']
    ];
    actions.forEach(([label, prompt]) => {
      const b = document.createElement('button');
      b.type = 'button';
      b.textContent = label;
      b.dataset.prompt = prompt;
      b.onclick = () => {
        question.value = prompt;
        ask.click();
      };
      quick.appendChild(b);
    });
  }
}

function apply() {
  if (V16.applying) return;
  V16.applying = true;
  try {
    installStyles();
    compactStaticCopy();
    compactSecondaryCopy();
    compactProactive();
    ensureAgentShell();
    document.documentElement.dataset.careerUiClarity = 'v16';
  } finally {
    V16.applying = false;
  }
}

function watch() {
  const root = $('app') || document.body;
  let t = null;
  new MutationObserver(() => {
    clearTimeout(t);
    t = setTimeout(apply, 120);
  }).observe(root, { childList: true, subtree: true });
}

apply();
watch();

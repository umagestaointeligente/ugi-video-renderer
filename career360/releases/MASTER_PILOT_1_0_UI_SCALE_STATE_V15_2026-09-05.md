# LSI Career 360 — UI Scale + State API V15

Data: 2026-09-05 BRT
Status: BACKEND STATE API LIVE / SCALE DB HARDENING LIVE / FRONTEND V15 BROWSER-VALIDATED NOT YET PROMOTED

## Objetivo

Fechar as lacunas restantes de interface e escala sem reconstruir o Career 360:

`ESTADO ÚNICO -> UI FLUIDA -> MOBILE/WEB CONSISTENTE -> COMPLEXIDADE ESCONDIDA`

## 1. career-ui-state — LIVE

Edge Function autenticada:
`career-ui-state`

JWT obrigatório.

Fornece ao frontend uma única leitura de estado para:
- versão da UI;
- Perfil Profissional;
- foto e variante profissional ativa;
- capacidades do Photo Studio;
- agente proativo/digest;
- notificações;
- Radar;
- engine campeão/rollback;
- capacidades ainda indisponíveis.

Capacidades declaradas no checkpoint:
- Visual Profile: true;
- Proactive Agent: true;
- Smart CV: true;
- Photo Studio local: true;
- Photo Studio IA externa: false;
- Radar refresh manual: true;
- Mail Decision: true;
- Mail Delivery: false.

Princípio:
`A UI NÃO DEVE ADIVINHAR SE UMA CAPACIDADE EXISTE.`

## 2. Escala de banco — LIVE

Migration:
`career_scale_indexes_v15`

Canônico:
`career360/migrations/20260905_scale_indexes_v15.sql`

Correções:
- removidos dois pares de índices únicos exatamente duplicados em `career_opportunities`;
- índices de apoio criados para FKs de applications, mail actions, photo settings, photo variants e role expansion.

Validação posterior no Performance Advisor:
- WARNs de duplicate_index = removidos;
- unindexed_foreign_keys = removidos;
- permanecem apenas INFOs de `unused_index`, esperado em piloto de baixo tráfego.

Não remover índices preventivos apenas porque o piloto ainda não os exerceu.

## 3. Frontend V15 — BROWSER-VALIDATED / NOT YET PROMOTED

Arquivo:
`career360/frontend/app-l.js`

Versão imutável atual a promover:
`4283646143425e4a3156e44100aabb475df88d27`

Bundle canônico:
`career360/frontend/index.html`

Commit do bundle atual:
`ece1582aa2a5253d4dc3ee7fbde7354896b57b01`

Pins atuais:
- `app-k.js` -> `6df7b4e63d7e52ce3c3f02247392b98f0393cbe8`;
- `app-l.js` -> `4283646143425e4a3156e44100aabb475df88d27`.

Objetivo: responsividade fluida em vez de zoom/transform global.

Breakpoints de produto:
- 360 px;
- 412 px;
- 768 px;
- 1180 px.

Comportamentos:
- largura fluida;
- tipografia com `clamp()`;
- cards com padding/radius fluidos;
- imagens sem deformação;
- Meu Perfil reorganiza duas colunas -> uma coluna;
- Photo Studio Antes/Depois reorganiza para uma coluna no celular;
- botões com alvo mínimo de toque de 44 px;
- navegação principal fixa na parte inferior no mobile;
- safe-area para Android/iOS;
- modais/drawers usam `dvh` e safe-area;
- Radar e Proactive cards reduzem densidade sem esconder informação crítica.

Navegação mobile desejada:
`MINHA PÁGINA | MEU PERFIL | OPORTUNIDADES | MEU AGENTE | MAIS`

### Hardening pré-promoção

Foram corrigidos antes de chegar à produção:

1. loop potencial do `MutationObserver` causado por reescrita contínua dos próprios rótulos de navegação;
2. capacidades desconhecidas representadas prematuramente como `local/off` antes de `career-ui-state` responder;
3. touch targets abaixo de 44 px em controles pequenos, incluindo fechamento do Photo Studio e controles equivalentes.

Commits:
- observer/idempotência: `c60a6e98a30db03a4c6d70f99fd133076618297d`;
- capacidades fail-closed/unknown: `f8e891b44fc69e1ee44505e4f89d69ca7104567c`;
- touch targets 44 px: `4283646143425e4a3156e44100aabb475df88d27`.

## 4. Photo Studio

V14 continua sendo o provider de foto profissional em produção:
`local-studio-v1`.

O V15 não finge geração externa.

Estado explícito entregue por `career-ui-state`:
`photo_studio_external_ai=false`.

A UI deve exibir ajuste profissional local quando a geração externa não estiver configurada.

### Hardening mobile do fallback local

Arquivo:
`career360/frontend/app-k.js`

Versão imutável a promover:
`6df7b4e63d7e52ce3c3f02247392b98f0393cbe8`.

Correção:
- MediaPipe continua sendo usado quando funciona;
- se a biblioteca carregar mas falhar durante segmentação/processamento no aparelho, o segmentador é fechado quando possível;
- o fluxo cai para o polish canvas local seguro;
- original continua preservada;
- aceite/reversão continuam exigindo ação explícita;
- nenhuma foto entra no matching/FIT.

## 5. Browser regression — PASS

Teste permanente:
`career360/tests/v15-browser-smoke.mjs`

Workflow:
`.github/workflows/career360-v15-browser-smoke.yml`

GitHub Actions run:
`33988409906`

Resultado:
`PASS`

Provas do run:
- `RESPONSIVE_360=PASS`;
- `RESPONSIVE_412=PASS`;
- `RESPONSIVE_768=PASS`;
- `RESPONSIVE_1180=PASS`;
- `PHOTO_STUDIO_SEGMENTATION_RUNTIME_FALLBACK=PASS`;
- JavaScript syntax gate = PASS;
- canonical pin gate = PASS;
- Chromium/Playwright browser regression = PASS.

O teste verifica:
- ausência de overflow horizontal;
- navegação fixa mobile;
- Meu Perfil 1 coluna mobile / 2 desktop;
- Antes/Depois 1 coluna mobile / 2 desktop;
- alvos de toque >=44 px;
- capacidade permanece `unknown` até resolução de `career-ui-state`;
- rótulos canônicos de navegação;
- MutationObserver estabiliza;
- fallback local do Photo Studio conclui e produz variante mesmo quando a segmentação falha em runtime.

Isso é validação automatizada de navegador, NÃO substitui o gate humano Android autenticado.

## 6. Deploy determinístico — ROTA CRIADA / CREDENCIAL AUSENTE

Produção oficial atual:
`dpl_98eN1wuVyk4wQmnYpG2jjsZ1ZazU`

Ela continua contendo V12/V13/V14 anterior e ainda NÃO contém a V15.

Foi criada uma rota de deploy explicitamente project-scoped:
`.github/workflows/career360-vercel-deploy.yml`

Destino hardcoded não secreto:
- Team: `team_ZJys00FTE2kK9yVtsqH5fHyF`;
- Project: `prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP`.

A rota:
- valida os pins canônicos antes de mutar Vercel;
- cria `.vercel/project.json` em runtime apontando exclusivamente ao projeto oficial;
- suporta preview e production;
- faz smoke HTTP/pins após deploy;
- aborta antes de qualquer mutação se `VERCEL_TOKEN` não existir.

Primeiro preview controlado:
- trigger: `.github/career360-vercel-deploy.trigger`;
- run: `33988095559`;
- resultado: `FAIL_CLOSED_BEFORE_VERCEL_MUTATION`;
- motivo comprovado: `VERCEL_TOKEN repository secret is not configured`.

Portanto:
`VERCEL_DEPLOY_ROUTE=READY_WAITING_CREDENTIAL`
`VERCEL_TOKEN=NOT_CONFIGURED`
`V15_VERCEL_DEPLOYED=NO`

Não usar a ação Vercel genérica sem `projectId` porque a conta possui múltiplos projetos.

## 7. Segurança

Security Advisor atual:
`auth_leaked_password_protection=DISABLED/WARN`.

Projeto Supabase atual:
- status `ACTIVE_HEALTHY`;
- organização no plano `free`.

A documentação atual da Supabase informa que Leaked Password Protection está disponível apenas no plano Pro ou superior.

Decisão canônica durante incubação de custo zero:
`LEAKED_PASSWORD_PROTECTION=KNOWN_PLAN_LIMITATION_NOT_UPGRADED`

Não gerar custo apenas para eliminar esse WARN sem decisão de produto/monetização.

O frontend usa como destino de confirmação de e-mail:
`https://lsi-career-360.vercel.app/?email-confirmado=1`.

A configuração server-side da Site URL / Additional Redirect URLs não é exposta pelas ferramentas atuais deste runtime, então:
`SUPABASE_CLIENT_EMAIL_REDIRECT_TARGET=PROVEN_OFFICIAL_URL`
`SUPABASE_SERVER_REDIRECT_ALLOWLIST=NOT_YET_PROVEN`

Não inferir a allowlist apenas pelo código do cliente.

## 8. Estado de promoção

`UI_V15=BROWSER_VALIDATED_NOT_YET_PROMOTED`
`PHOTO_STUDIO_MOBILE_FALLBACK_HARDENING=BROWSER_VALIDATED_NOT_YET_PROMOTED`

Não declarar V15 visual LIVE até:
1. existir preview Vercel do projeto oficial com os pins atuais;
2. preview passar HTTP/runtime smoke;
3. produção oficial carregar `app-l.js@428364...` e `app-k.js@6df7b4...`;
4. alias oficial permanecer correto;
5. Android autenticado passar o fluxo real;
6. Photo Studio passar gerar/comparar/aceitar/reverter no aparelho real.

`LAST_VERIFIED_CHANGE=V15_BROWSER_REGRESSION_PASS_360_412_768_1180_PHOTO_STUDIO_RUNTIME_FALLBACK_PASS_TOUCH_TARGETS_44PX_DEPLOY_ROUTE_PROJECT_SCOPED_READY_BUT_VERCEL_TOKEN_NOT_CONFIGURED_PRODUCTION_STILL_V14`

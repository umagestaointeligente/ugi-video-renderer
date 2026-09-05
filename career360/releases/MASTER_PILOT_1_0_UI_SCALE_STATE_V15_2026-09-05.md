# LSI Career 360 — UI Scale + State API V15

Data: 2026-09-05 BRT
Status: BACKEND STATE API LIVE / SCALE DB HARDENING LIVE / FRONTEND V15 VERSIONED NOT YET PROMOTED

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

## 3. Frontend V15 — VERSIONED

Arquivo:
`career360/frontend/app-l.js`

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
- botões com alvo mínimo de toque;
- navegação principal fixa na parte inferior no mobile;
- safe-area para Android/iOS;
- modais/drawers usam `dvh` e safe-area;
- Radar e Proactive cards reduzem densidade sem esconder informação crítica.

Navegação mobile desejada:
`MINHA PÁGINA | MEU PERFIL | OPORTUNIDADES | MEU AGENTE | MAIS`

## 4. Photo Studio

V14 continua sendo o provider de foto profissional em produção:
`local-studio-v1`.

O V15 não finge geração externa.

Estado explícito entregue por `career-ui-state`:
`photo_studio_external_ai=false`.

A UI deve exibir ajuste profissional local quando a geração externa não estiver configurada.

## 5. Deploy

Produção oficial atual no momento desta release:
`dpl_98eN1wuVyk4wQmnYpG2jjsZ1ZazU`

Ela já contém:
- V12 Proactive UI;
- V13 Visual Profile;
- V14 Photo Studio.

O novo `app-l.js` V15 está versionado no GitHub, mas ainda não está referenciado pelo HTML oficial.

Portanto:
`UI_V15=VERSIONED_NOT_YET_PROMOTED`.

Não declarar V15 visual LIVE até o bundle oficial carregar `app-l.js` e passar validação no domínio oficial.

## 6. Segurança

Security Advisor anterior ao V15 mantinha apenas:
`auth_leaked_password_protection=DISABLED/WARN`.

O V15 não adiciona escrita direta de cliente em tabelas internas.
`career-ui-state` é read-only e autenticado.

## 7. Próximo gate

1. promover `app-l.js` no bundle estático Vercel;
2. validar 360/412/768/desktop;
3. validar navegação fixa mobile;
4. validar Photo Studio modal e comparação em 360/412;
5. checar runtime errors;
6. somente depois marcar `UI_V15=LIVE`.

`LAST_VERIFIED_CHANGE=CAREER_UI_STATE_LIVE_SCALE_INDEX_HARDENING_LIVE_APP_L_V15_VERSIONED_NOT_YET_PROMOTED`

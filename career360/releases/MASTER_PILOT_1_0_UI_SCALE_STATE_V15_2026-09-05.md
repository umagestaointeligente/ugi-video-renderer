# LSI Career 360 — UI Scale + State API V15

Data: 2026-09-05 BRT
Status: BACKEND STATE API LIVE / SCALE DB HARDENING LIVE / FRONTEND V15 BROWSER-VALIDATED / PROMOTION PIPELINE READY / VERCEL AUTH PENDING

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

Navegação mobile:
`MINHA PÁGINA | MEU PERFIL | OPORTUNIDADES | MEU AGENTE | MAIS`

### Hardening pré-promoção

Foram corrigidos antes de chegar à produção:
1. loop potencial do `MutationObserver`;
2. capacidades desconhecidas inferidas prematuramente antes de `career-ui-state` responder;
3. touch targets abaixo de 44 px em controles pequenos.

Commits:
- observer/idempotência: `c60a6e98a30db03a4c6d70f99fd133076618297d`;
- capacidades fail-closed/unknown: `f8e891b44fc69e1ee44505e4f89d69ca7104567c`;
- touch targets 44 px: `4283646143425e4a3156e44100aabb475df88d27`.

## 4. Photo Studio

Provider atual em produção:
`local-studio-v1`.

O V15 não finge geração externa.

Estado explícito:
`photo_studio_external_ai=false`.

### Hardening mobile do fallback local

Arquivo:
`career360/frontend/app-k.js`

Versão imutável a promover:
`6df7b4e63d7e52ce3c3f02247392b98f0393cbe8`.

Correção:
- MediaPipe continua sendo usado quando funciona;
- falha durante segmentação/processamento cai para canvas local;
- segmentador é fechado quando possível;
- original continua preservada;
- aceite/reversão continuam explícitos;
- foto continua fora do matching/FIT.

## 5. Browser regression — PASS

Teste permanente:
`career360/tests/v15-browser-smoke.mjs`

Workflow:
`.github/workflows/career360-v15-browser-smoke.yml`

GitHub Actions run:
`33988409906`

Resultado:
`PASS`

Provas:
- `RESPONSIVE_360=PASS`;
- `RESPONSIVE_412=PASS`;
- `RESPONSIVE_768=PASS`;
- `RESPONSIVE_1180=PASS`;
- `PHOTO_STUDIO_SEGMENTATION_RUNTIME_FALLBACK=PASS`;
- JavaScript syntax gate = PASS;
- canonical pin gate = PASS;
- Chromium/Playwright regression = PASS.

O teste verifica:
- ausência de overflow horizontal;
- navegação fixa mobile;
- Meu Perfil 1 coluna mobile / 2 desktop;
- Antes/Depois 1 coluna mobile / 2 desktop;
- alvos de toque >=44 px;
- capacidade `unknown` até resolução de `career-ui-state`;
- rótulos canônicos de navegação;
- MutationObserver estabiliza;
- fallback local do Photo Studio conclui mesmo quando a segmentação falha em runtime.

Isso é validação automatizada e NÃO substitui Android autenticado real.

## 6. Deploy determinístico — PIPELINE FINAL READY / AUTH PENDING

Produção oficial atual:
`dpl_98eN1wuVyk4wQmnYpG2jjsZ1ZazU`

Ela continua contendo V12/V13/V14 anterior e ainda NÃO contém V15.

Workflow canônico:
`.github/workflows/career360-vercel-deploy.yml`

Destino hardcoded não secreto:
- Team: `team_ZJys00FTE2kK9yVtsqH5fHyF`;
- Project: `prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP`.

Commit do pipeline endurecido:
`64fe2aa62856632b863a97c4a008e74cdc54b9c6`.

Vercel CLI pinada:
`59.11.7`.

### Estratégia final de promoção

`VERIFY SOURCE -> BIND OFFICIAL PROJECT -> CREATE PREVIEW -> PREVIEW HTTP/PIN SMOKE -> PROMOTE EXACT PREVIEW -> OFFICIAL ALIAS SMOKE`

Quando `target=production`:
- o pipeline não cria um segundo build de produção;
- promove exatamente o Preview que passou no smoke;
- valida o domínio oficial após a promoção;
- aguarda convergência por tentativas controladas;
- falha se o alias oficial não carregar os pins esperados.

Isso elimina a possibilidade de validar um Preview e publicar outro artefato diferente.

### Credential gate

Primeiro preview controlado anterior:
- run `33988095559`;
- resultado `FAIL_CLOSED_BEFORE_VERCEL_MUTATION`;
- motivo: `VERCEL_TOKEN repository secret is not configured`.

### OIDC probe

Foi testada uma rota para eliminar segredo persistente:
- GitHub OIDC token emitido corretamente;
- exchange Vercel retornou `HTTP 400`;
- run `34005662454`;
- nenhuma mutação Vercel ocorreu;
- workflow temporário removido no commit `02f7bedb284ae52aef879fc7edb8b88ce8ccf493`.

A documentação/skill atual da Vercel confirma que OIDC federation não substitui `VERCEL_TOKEN` para `vercel deploy`/CLI em CI.

Portanto:
`VERCEL_DEPLOY_ROUTE=PREVIEW_PROMOTE_PIPELINE_READY_WAITING_AUTH`
`VERCEL_TOKEN=NOT_CONFIGURED`
`V15_VERCEL_DEPLOYED=NO`

Não usar a ação Vercel genérica sem `projectId`, pois a conta possui múltiplos projetos.
Não usar OTP/magic link/e-mail como atalho automatizado de autenticação.

## 7. Segurança

Security Advisor atual:
`auth_leaked_password_protection=DISABLED/WARN`.

Projeto Supabase:
- `ACTIVE_HEALTHY`;
- plano `free`.

Leaked Password Protection exige plano Pro ou superior.

Decisão de incubação zero-cash:
`LEAKED_PASSWORD_PROTECTION=KNOWN_PLAN_LIMITATION_NOT_UPGRADED`.

O frontend usa como destino de confirmação:
`https://lsi-career-360.vercel.app/?email-confirmado=1`.

Estado:
`SUPABASE_CLIENT_EMAIL_REDIRECT_TARGET=PROVEN_OFFICIAL_URL`
`SUPABASE_SERVER_REDIRECT_ALLOWLIST=NOT_YET_PROVEN`

Não inferir allowlist server-side apenas do código cliente.

## 8. Estado de promoção

`UI_V15=BROWSER_VALIDATED_NOT_YET_PROMOTED`
`PHOTO_STUDIO_MOBILE_FALLBACK_HARDENING=BROWSER_VALIDATED_NOT_YET_PROMOTED`

Para marcar LIVE ainda é obrigatório:
1. autenticação válida para o pipeline project-scoped;
2. Preview oficial com pins atuais;
3. smoke Preview PASS;
4. promoção do mesmo artefato;
5. alias oficial carregando `app-l@428364...` e `app-k@6df7b4...`;
6. runtime errors limpos;
7. Android autenticado real;
8. Photo Studio gerar/comparar/aceitar/reverter no aparelho real.

`LAST_VERIFIED_CHANGE=V15_BROWSER_REGRESSION_PASS_PHOTO_STUDIO_FALLBACK_PASS_DEPLOY_PIPELINE_64FE2_PREVIEW_THEN_PROMOTE_EXACT_ARTIFACT_VERCEL_CLI_59_11_7_AUTH_REQUIRED_PRODUCTION_STILL_V14`

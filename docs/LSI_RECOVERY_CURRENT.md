# LSI — RECOVERY CURRENT

Status: CURRENT / AUTORITATIVO PARA HANDOFF
Atualizado: 2026-09-05 BRT
Âncora humana: `Recovery LSI`

Handoff canônico desta transição de chat:
`docs/LSI_CAREER360_HANDOFF_2026-09-05_1609.md`

## 0. Estado global

`CURRENT_FOCUS=LSI_CAREER_360_MASTER_PILOT_1_0`
`CURRENT_STATUS=V14_PRODUCTION_STABLE_WITH_V15_CANONICAL_BUNDLE_HARDENED_NOT_VERCEL_DEPLOYED`
`VERIFIED_REVENUE=R$0,00` para lógica de incubação; reconfirmar antes de decisão monetária.

## 1. Canônico / runtime

Repository: `umagestaointeligente/ugi-video-renderer`
Branch: `main`
Supabase: `nxjdnzdxclszqyqrkwdk`
Frontend oficial: `https://lsi-career-360.vercel.app/`
Vercel project: `prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP`

Produção visual oficial atual:
`dpl_98eN1wuVyk4wQmnYpG2jjsZ1ZazU`

Verificado em runtime em 2026-09-05:
- Supabase = `ACTIVE_HEALTHY`;
- `career-ui-state` V1 ACTIVE;
- `career-photo-studio` V11 ACTIVE;
- `career-profile-photo` V10 ACTIVE;
- Vercel production = `READY`;
- target `production`;
- alias oficial presente;
- HTTP 200;
- HTML oficial carrega `app-i.js`, `app-j.js` e a versão V14 anterior de `app-k.js`;
- HTML oficial ainda NÃO carrega `app-l.js`;
- nenhum runtime error no Vercel no período pós-readback consultado.

## 2. Gates de produto

`AUTH=LIVE`
`CAREER_PRIVACY_P0=PASS_MASTER_PILOT_SCOPE`
`MULTIUSER_ISOLATION=PASS`
`SAFE_FILE_PIPELINE=PASS_MASTER_PILOT_SCOPE`
`PARSER_1_0_3=LIVE`
`PROFESSIONAL_PROFILE_V3=LIVE`
`CONTE_DO_SEU_JEITO=LIVE`
`SMART_CV=LIVE`
`MATCH_ENGINE_V2=CHAMPION`
`MATCH_ENGINE_V1=ROLLBACK`
`REGION_FILTER_V2=LIVE`
`AUTOMATED_OPPORTUNITY_RESEARCH=LIVE_PILOT_SCOPE`
`PROACTIVE_AGENT_CORE_V12=LIVE`
`PROACTIVE_UI_V12=LIVE`
`VISUAL_PROFILE_V13=LIVE`
`PHOTO_STUDIO_V14=LIVE_LOCAL_ZERO_CASH`
`PHOTO_STUDIO_MOBILE_FALLBACK_HARDENING=VERSIONED_NOT_YET_PROMOTED`
`CAREER_UI_STATE_V15=LIVE`
`SCALE_DB_HARDENING_V15=LIVE`
`UI_RESPONSIVE_V15=CANONICAL_BUNDLE_HARDENED_VERCEL_NOT_YET_DEPLOYED`
`MAIL_DECISION=LIVE`
`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`
`PUBLIC_BETA=NOT_OPENED_PRODUCT_DECISION`

## 3. Princípios duros

`O CLIENTE NÃO PREENCHE. O CLIENTE CONFIRMA.`
`O CLIENTE NÃO OPERA A BUSCA. O AGENTE OPERA; O CLIENTE CONFIRMA O QUE IMPORTA.`
`O CAREER NÃO DEPENDE DO USUÁRIO ABRIR O CHAT PARA CONTINUAR TRABALHANDO.`
`COMPLEXIDADE POR TRÁS. IDENTIDADE PROFISSIONAL NA FRENTE.`

- privacidade antes de matching;
- idade/foto/plano nunca elevam FIT;
- salário oculto/estimado nunca vira fato;
- currículo/perfil nunca fabrica informação;
- candidatura não vira `applied` sem evidência;
- e-mail não vira `sent` apenas porque foi aprovado;
- perfil não é público sem consentimento explícito;
- foto profissional não substitui original sem aceite explícito.

## 4. V12 — Proactive Agent LIVE

Backend e UI LIVE:
- Activity Ledger;
- Digest 4h/6h/8h/12h;
- notifications;
- applications foundation;
- mail actions foundation;
- `career-proactive-digest`;
- `career-proactive-status`;
- `career-mail-decision`;
- `career360/frontend/app-i.js`.

Conta piloto: digest 4h.
Cron `career-proactive-digest` = ACTIVE.

## 5. V13 — Meu Perfil Visual LIVE

Frontend:
`career360/frontend/app-j.js`.

Arquitetura:
`MINHA PÁGINA -> MEU PERFIL -> OPORTUNIDADES -> MEU AGENTE -> MAIS`

Meu Perfil interno:
- capa;
- foto;
- headline/localização;
- Sobre;
- Destaques;
- Liderança/Escopo;
- timeline de experiência;
- competências;
- formação;
- idiomas/certificações;
- copiar blocos para LinkedIn;
- baixar currículo;
- selo `Só você vê por enquanto`.

Sem URL pública/exposição automática.

## 6. V14 — Professional Photo Studio LIVE

Backend LIVE, sem alteração neste gate:
- `career_profile_photo_variants`;
- `career_profile_photo_settings`;
- `career-photo-studio` V11;
- `career-profile-photo` V10.

Frontend oficial atualmente LIVE:
`career360/frontend/app-k.js` na versão já promovida no deployment V14 atual.

Fluxo:
`ORIGINAL -> CONTEXTO DE CARREIRA -> ESTILO -> POLIMENTO LOCAL -> ANTES/DEPOIS -> ACEITAR OU MANTER ORIGINAL`

Contexto usa somente cargo atual + cargos-alvo.
Foto não entra no matching/FIT.

Runtime:
`PHOTO_STUDIO_PROVIDER=local-studio-v1`
`AI_GENERATION_EXTERNAL=NOT_CONFIGURED`

Não declarar geração externa LIVE.

### Hardening mobile versionado / ainda não promovido

Durante o gate pré-V15 foi encontrada uma lacuna real no fallback local:
- se a biblioteca MediaPipe não carregasse, já existia fallback canvas;
- se a biblioteca carregasse mas falhasse durante segmentação/processamento no dispositivo, o fluxo podia abortar em vez de cair no fallback.

Correção versionada em:
`career360/frontend/app-k.js`

Commit imutável:
`6df7b4e63d7e52ce3c3f02247392b98f0393cbe8`

A correção:
- mantém MediaPipe quando funciona;
- captura falha de runtime/segmentação;
- fecha o segmentador quando possível;
- cai para o polish canvas local seguro;
- não altera backend, identidade, estilos, aceite, reversão ou uso da foto no FIT.

Esse hardening só se torna produção quando o próximo deployment oficial carregar o novo pin de `app-k.js`.

Gate humano Android ainda pendente:
`MELHORAR -> GERAR -> COMPARAR -> ACEITAR -> VALIDAR MINHA PÁGINA/MEU PERFIL/PDF -> VOLTAR À ORIGINAL -> CONFIRMAR ROLLBACK`.

## 7. V15 — UI State API + Escala

### Backend LIVE

Edge autenticada:
`career-ui-state` V1 / JWT required.

Ela entrega uma única leitura de capacidades/estado para:
- Perfil/CV;
- foto e seleção ativa;
- Photo Studio;
- agente proativo;
- notificações;
- Radar;
- engine champion/rollback;
- capacidades indisponíveis.

Princípio:
`A UI NÃO ADIVINHA CAPACIDADES.`

### Scale DB hardening LIVE

Migration aplicada:
`career_scale_indexes_v15`.

Canônico:
`career360/migrations/20260905_scale_indexes_v15.sql`.

Resultado comprovado no Performance Advisor:
- `duplicate_index` WARNs removidos;
- `unindexed_foreign_keys` removidos;
- permanecem apenas `unused_index` INFOs esperados em piloto de baixo tráfego.

### Frontend V15 HARDENED NO BUNDLE CANÔNICO / NÃO DEPLOYED NA PRODUÇÃO VERCEL

Arquivo:
`career360/frontend/app-l.js`.

A revisão pré-promoção encontrou e corrigiu dois pontos antes de chegarem à produção:

1. `MutationObserver` podia autoacionar novas mutações ao reescrever repetidamente os próprios rótulos de navegação, criando churn de DOM em intervalos curtos e risco de lentidão mobile.
2. Antes da resposta de `career-ui-state`, capacidades desconhecidas eram representadas implicitamente como `local/off`, contrariando `A UI NÃO ADIVINHA CAPACIDADES`.

Hardening final do `app-l.js`:
- escrita de labels idempotente com `dataset.v15Nav`;
- preservação do badge do agente;
- provider só é reescrito quando necessário;
- `ResizeObserver` não regrava a mesma largura;
- capacidades permanecem `unknown` até `career-ui-state` responder.

Commits do hardening:
- observer/idempotência: `c60a6e98a30db03a4c6d70f99fd133076618297d`;
- estado desconhecido fail-closed: `f8e891b44fc69e1ee44505e4f89d69ca7104567c`.

Versão imutável final a promover do `app-l.js`:
`f8e891b44fc69e1ee44505e4f89d69ca7104567c`.

### Bundle canônico final para próximo deployment

Arquivo:
`career360/frontend/index.html`.

Commit final do bundle:
`dbf1913748563d5a3aa51bfa8aa2473fb6ba3fd3`.

Pins finais:
- `app-k.js` -> `6df7b4e63d7e52ce3c3f02247392b98f0393cbe8`;
- `app-l.js` -> `f8e891b44fc69e1ee44505e4f89d69ca7104567c`.

Diff comprovado do repin final:
- 2 adições;
- 2 remoções;
- únicas alterações: os dois pins acima.

Responsividade alvo para 360 / 412 / 768 / 1180 px:
- tipografia/spacing com `clamp`;
- imagens sem deformação;
- Meu Perfil 2 colunas -> 1 coluna;
- Photo Studio Antes/Depois -> 1 coluna no mobile;
- touch targets mínimos;
- navegação inferior fixa no mobile;
- safe-area;
- drawers/modais com `dvh`;
- densidade reduzida sem esconder informação crítica.

IMPORTANTE:
A produção oficial atual AINDA NÃO referencia `app-l.js` e ainda não carrega os pins hardened acima.
Não declarar `UI_V15=LIVE` nem `PHOTO_STUDIO_MOBILE_FALLBACK_HARDENING=LIVE` até existir deployment do projeto Vercel oficial carregando o bundle `dbf191...` e passar validação responsiva + Android.

### Guardrail de deployment descoberto no readback

A conta Vercel atual possui múltiplos projetos.
A ação de deploy disponível neste contexto não aceita `projectId` explícito.
Portanto:
`UNSCOPED_VERCEL_DEPLOY=DO_NOT_USE`.

Não usar deploy genérico sem prova determinística de que o destino é `prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP`.
O histórico V14 mostra preview direto seguido de novo deployment de produção, ambos criados pela conta Vercel e sem Git Integration (`meta={}`).

Release:
`career360/releases/MASTER_PILOT_1_0_UI_SCALE_STATE_V15_2026-09-05.md`.

## 8. Radar / Matching

`CHAMPION=v2.0`
`ROLLBACK=v1.0`
Threshold: 72.
Radar piloto: fontes estruturadas, rotação automática e `Pesquisar agora`.
Zero vaga qualificada é estado válido.

## 9. Currículo / Perfil

Parser: `career360-edge-parser/1.0.3`.
Separa summary/highlights/leadership/experience/education/skills/languages/certifications.
Regra: `EXTRAIR -> MOSTRAR -> USUÁRIO CONFIRMA -> VIRA FATO`.
Perfil/CV V3 usa apenas informação confirmada/aceita.

## 10. Segurança / pré-Beta

Security Advisor:
- sem lint estrutural novo de RLS;
- permanece `auth_leaked_password_protection=DISABLED/WARN`.

Também pendente:
`SUPABASE_GLOBAL_SITE_URL_REDIRECT_ALLOWLIST=NOT_YET_PROVEN`.

Performance Advisor após V15:
- sem duplicate-index WARN;
- sem unindexed-FK;
- somente INFOs de unused indexes.

## 11. Próximos gates

1. criar deployment PREVIEW determinístico do bundle `dbf1913748563d5a3aa51bfa8aa2473fb6ba3fd3` no projeto Vercel oficial `prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP` usando rota explicitamente project-scoped;
2. validar preview em 360/412/768/1180 e runtime errors;
3. promover/criar produção e confirmar alias oficial + HTTP 200 + pins hardened de `app-k.js`/`app-l.js` no HTML;
4. validar Android real;
5. validar Photo Studio gerar/comparar/aceitar/reverter no Android;
6. conectar e-mail OAuth + receipts reais;
7. ligar candidatura real ao funil;
8. follow-up scheduler;
9. reprocessar/confirmar currículo 1.0.3;
10. hidratar catálogo de empregadores;
11. ampliar Radar mantendo precisão;
12. resolver redirect/password warning;
13. Career Learning Engine;
14. Founding Beta 20 somente após decisão explícita.

## 12. DO NOT FAKE / DO NOT REDO

- não reconstruir Career;
- não copiar LinkedIn/trade dress;
- não usar foto/idade/plano no FIT;
- não inventar fatos;
- não fingir vaga/candidatura/e-mail;
- não fingir geração externa de imagem;
- não substituir original silenciosamente;
- não declarar UI V15 LIVE antes do bundle oficial Vercel carregar `app-l.js` e passar validação;
- não declarar o hardening mobile do Photo Studio LIVE antes do bundle oficial carregar o novo `app-k.js`;
- não usar deploy Vercel sem escopo determinístico do projeto oficial;
- não abrir Beta automaticamente.

`LAST_VERIFIED_CHANGE=CANONICAL_BUNDLE_DBF191_PINS_APP_K_6DF7B4E_AND_APP_L_F8E891_V15_OBSERVER_AND_CAPABILITY_HARDENED_PHOTO_STUDIO_RUNTIME_FALLBACK_HARDENED_VERCEL_OFFICIAL_STILL_V14_UI_V15_NOT_LIVE`

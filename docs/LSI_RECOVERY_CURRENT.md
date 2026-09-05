# LSI — RECOVERY CURRENT

Status: CURRENT / AUTORITATIVO PARA HANDOFF
Atualizado: 2026-09-05 BRT
Âncora humana: `Recovery LSI`

## 0. Estado global

`CURRENT_FOCUS=LSI_CAREER_360_MASTER_PILOT_1_0`
`CURRENT_STATUS=V14_PRODUCTION_WITH_V15_BACKEND_SCALE_HARDENING`
`VERIFIED_REVENUE=R$0,00` para lógica de incubação; reconfirmar antes de decisão monetária.

## 1. Canônico / runtime

Repository: `umagestaointeligente/ugi-video-renderer`
Branch: `main`
Supabase: `nxjdnzdxclszqyqrkwdk`
Frontend oficial: `https://lsi-career-360.vercel.app/`
Vercel project: `prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP`

Produção visual oficial atual:
`dpl_98eN1wuVyk4wQmnYpG2jjsZ1ZazU`

Verificado:
- `READY`;
- target `production`;
- alias oficial presente;
- HTTP 200;
- HTML oficial carrega `app-i.js`, `app-j.js` e `app-k.js`;
- nenhum runtime error no Vercel no período consultado.

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
`CAREER_UI_STATE_V15=LIVE`
`SCALE_DB_HARDENING_V15=LIVE`
`UI_RESPONSIVE_V15=VERSIONED_NOT_YET_PROMOTED`
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

Backend:
- `career_profile_photo_variants`;
- `career_profile_photo_settings`;
- `career-photo-studio`;
- `career-profile-photo`.

Frontend:
`career360/frontend/app-k.js`.

Fluxo:
`ORIGINAL -> CONTEXTO DE CARREIRA -> ESTILO -> POLIMENTO LOCAL -> ANTES/DEPOIS -> ACEITAR OU MANTER ORIGINAL`

Contexto usa somente cargo atual + cargos-alvo.
Foto não entra no matching/FIT.

Runtime:
`PHOTO_STUDIO_PROVIDER=local-studio-v1`
`AI_GENERATION_EXTERNAL=NOT_CONFIGURED`

Não declarar geração externa LIVE.

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

### Frontend V15 VERSIONED / NOT YET PROMOTED

Arquivo:
`career360/frontend/app-l.js`.

Responsividade fluida para 360 / 412 / 768 / 1180 px:
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
A produção oficial atual ainda não referencia `app-l.js`.
Não declarar `UI_V15=LIVE` até promoção do bundle estático + validação Android.

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

1. promover `app-l.js` no bundle estático oficial;
2. validar 360/412/768/desktop + Android;
3. validar Photo Studio gerar/comparar/aceitar/reverter no Android;
4. conectar e-mail OAuth + receipts reais;
5. ligar candidatura real ao funil;
6. follow-up scheduler;
7. reprocessar/confirmar currículo 1.0.3;
8. hidratar catálogo de empregadores;
9. ampliar Radar mantendo precisão;
10. resolver redirect/password warning;
11. Career Learning Engine;
12. Founding Beta 20 somente após decisão explícita.

## 12. DO NOT FAKE / DO NOT REDO

- não reconstruir Career;
- não copiar LinkedIn/trade dress;
- não usar foto/idade/plano no FIT;
- não inventar fatos;
- não fingir vaga/candidatura/e-mail;
- não fingir geração externa de imagem;
- não substituir original silenciosamente;
- não declarar UI V15 LIVE antes do bundle oficial carregar `app-l.js`;
- não abrir Beta automaticamente.

`LAST_VERIFIED_CHANGE=V15_UI_STATE_API_LIVE_SCALE_DB_HARDENING_LIVE_APP_L_VERSIONED_NOT_PROMOTED_V14_PRODUCTION_STABLE`

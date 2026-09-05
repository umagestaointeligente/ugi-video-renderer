# LSI — RECOVERY CURRENT

Status: CURRENT / AUTORITATIVO PARA HANDOFF
Atualizado: 2026-09-05 BRT
Âncora humana: `Recovery LSI`

## 0. Estado global

`CURRENT_FOCUS=LSI_CAREER_360_MASTER_PILOT_1_0`
`CURRENT_STATUS=V11_1_PRODUCTION_V12_PROACTIVE_BACKEND_LIVE_V13_VISUAL_PROFILE_VERSIONED_V14_PHOTO_STUDIO_LOCAL_POLISH_BACKEND_LIVE`
`VERIFIED_REVENUE=R$0,00` para lógica de incubação; reconfirmar antes de decisão monetária.

## 1. Canônico / runtime

Repository: `umagestaointeligente/ugi-video-renderer`
Branch: `main`
Supabase: `nxjdnzdxclszqyqrkwdk`
Frontend oficial: `https://lsi-career-360.vercel.app/`
Vercel project: `prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP`

Produção visual comprovada atual:
`UX_V11_1=LIVE`
Deployment: `dpl_EjNc9WzK1uPCZFWhY8ympukcAMGG`

Vercel continua bundle estático/framework null. Não fazer deploy cego; preservar scripts pinados e rollback.

## 2. Produto LIVE

`AUTH=LIVE`
`CAREER_PRIVACY_P0=PASS_MASTER_PILOT_SCOPE`
`MULTIUSER_ISOLATION=PASS`
`SAFE_FILE_PIPELINE=PASS_MASTER_PILOT_SCOPE`
`PROFILE_PHOTO_PRIVATE_BACKEND=LIVE_V5`
`PARSER_1_0_3=LIVE`
`PROFESSIONAL_PROFILE_V3=LIVE`
`CONTE_DO_SEU_JEITO=LIVE`
`SMART_CV=LIVE`
`MATCH_ENGINE_V2=CHAMPION`
`MATCH_ENGINE_V1=ROLLBACK`
`REGION_FILTER_V2=LIVE`
`AUTOMATED_OPPORTUNITY_RESEARCH=LIVE_PILOT_SCOPE`
`PROACTIVE_AGENT_CORE_V12=LIVE`
`PROACTIVE_DIGEST_CRON=LIVE`
`MAIL_DECISION=LIVE`
`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`
`PHOTO_STUDIO_LOCAL_POLISH_BACKEND=LIVE`
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
- foto profissional nunca substitui original sem aceite.

## 4. V12 — Proactive Agent

Backend LIVE:
- Activity Ledger;
- Digest 4h/6h/8h/12h;
- notifications;
- applications foundation;
- mail actions foundation;
- `career-proactive-digest`;
- `career-proactive-status`;
- `career-mail-decision`.

Conta piloto: digest 4h.
Cron `career-proactive-digest` = ACTIVE.

UI: `career360/frontend/app-i.js`
`PROACTIVE_UI_V12=VERSIONED_NOT_YET_PROMOTED`.

## 5. V13 — Meu Perfil Visual

Arquivo: `career360/frontend/app-j.js`.

Arquitetura desejada:
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

`VISUAL_PROFILE_V13=VERSIONED_NOT_YET_PROMOTED`.

## 6. V14 — Professional Photo Studio

### Backend LIVE

Migration canônica:
`career360/migrations/20260905_professional_photo_studio_v1.sql`

Tabela:
`career_professional_photo_jobs`

Campos de seleção no perfil:
- `active_professional_photo_job_id`;
- `photo_style_preference`.

Edges ACTIVE / JWT required:
- `career-photo-studio`;
- `career-professional-photo-plan`;
- `career-professional-photo-decision`;
- `career-profile-photo` V5.

Fluxo zero-cash:
`ORIGINAL -> CONTEXTO DE CARREIRA -> ESTILO -> AJUSTE LOCAL NO NAVEGADOR -> ANTES/DEPOIS -> ACEITAR/MANTER ORIGINAL`.

Contexto permitido:
- cargo atual;
- cargos-alvo.

Estilos:
- executive;
- commercial;
- modern;
- creative;
- professional.

Regras:
- preservar identidade;
- não alterar idade/gênero/raça/corpo/rosto;
- foto nunca entra no matching/FIT;
- original preservada;
- variante aceita passa a ser `photo` de exibição;
- trocar original remove/invalida derivações antigas.

### Local Professional Polish

Frontend versionado:
`career360/frontend/app-k.js`.

Processamento zero-cash no aparelho:
- crop 4:5;
- segmentação pessoa/fundo;
- fundo profissional conforme estilo;
- brilho/contraste/saturação suaves;
- upload privado da variante;
- comparação Original x Profissional;
- aceitar ou voltar para original.

`PHOTO_STUDIO_UI=VERSIONED_NOT_YET_PROMOTED`.

### Generative provider

`GENERATIVE_PHOTO_PROVIDER=NOT_CONFIGURED`.
Não fingir troca generativa de roupa/cenário. A primeira versão funcional é local polish.

## 7. Radar / Matching

`CHAMPION=v2.0`
`ROLLBACK=v1.0`
Threshold: `72`.

Radar piloto:
- 10 fontes estruturadas;
- rotação aproximadamente horária;
- cobertura completa ~4h;
- `Pesquisar agora`.

Zero vaga qualificada é estado válido.

## 8. Currículo / Perfil

Parser: `career360-edge-parser/1.0.3`.
Separa summary/highlights/leadership/experience/education/skills/languages/certifications.
Regra: `EXTRAIR -> MOSTRAR -> USUÁRIO CONFIRMA -> VIRA FATO`.

Perfil/CV V3 usa somente informação confirmada/aceita.
Foto no PDF é opt-in.

## 9. Segurança / pré-Beta

Security Advisor após V14:
- nenhum WARN novo estrutural de RLS;
- permanece apenas `auth_leaked_password_protection=DISABLED/WARN`.

Também pendente:
`SUPABASE_GLOBAL_SITE_URL_REDIRECT_ALLOWLIST=NOT_YET_PROVEN`.

## 10. Próxima promoção visual

Promoção controlada deve manter V11.1 e adicionar:
- `app-i.js` V12;
- `app-j.js` V13;
- `app-k.js` V14.

Gates:
- alias oficial;
- HTTP 200;
- runtime errors;
- login/onboarding;
- foto original;
- Estúdio antes/depois;
- aceite/rollback de foto;
- Meu Perfil;
- card proativo;
- teste Android autenticado.

## 11. Próximos gargalos

1. promoção controlada V12+V13+V14;
2. teste Android;
3. avaliar provider generativo apenas como Próximo Degrau;
4. conectar e-mail OAuth + receipts;
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
- não fingir foto generativa sem provider;
- não substituir original silenciosamente;
- não declarar V12/V13/V14 UI LIVE antes do deployment validado;
- não abrir Beta automaticamente.

## 13. Leitura sob demanda

Manifesto: `docs/projects/LSI_CAREER360.md`
V12: `career360/releases/MASTER_PILOT_1_0_PROACTIVE_AGENT_V12_2026-09-04.md`
V13: `career360/releases/MASTER_PILOT_1_0_VISUAL_PROFILE_V13_2026-09-04.md`
V14: `career360/releases/MASTER_PILOT_1_0_PROFESSIONAL_PHOTO_STUDIO_V14_2026-09-05.md`

`LAST_VERIFIED_CHANGE=PHOTO_STUDIO_V14_LOCAL_POLISH_BACKEND_LIVE_APP_K_VERSIONED_NOT_PROMOTED_GENERATIVE_PROVIDER_NOT_CONFIGURED`

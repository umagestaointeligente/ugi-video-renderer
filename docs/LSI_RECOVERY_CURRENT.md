# LSI — RECOVERY CURRENT

Status: CURRENT / AUTORITATIVO PARA HANDOFF
Atualizado: 2026-09-05 BRT
Âncora humana: `Recovery LSI`

## 0. Estado global

`CURRENT_FOCUS=LSI_CAREER_360_MASTER_PILOT_1_0`
`CURRENT_STATUS=V14_PRODUCTION_WITH_V12_PROACTIVE_V13_VISUAL_PROFILE_V14_PHOTO_STUDIO`
`VERIFIED_REVENUE=R$0,00` para lógica de incubação; reconfirmar antes de decisão monetária.

## 1. Canônico / runtime

Repository: `umagestaointeligente/ugi-video-renderer`
Branch: `main`
Supabase: `nxjdnzdxclszqyqrkwdk`
Frontend oficial: `https://lsi-career-360.vercel.app/`
Vercel project: `prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP`

Produção atual:
`dpl_98eN1wuVyk4wQmnYpG2jjsZ1ZazU`

Verificado:
- `READY`;
- target `production`;
- alias oficial presente;
- HTTP 200 no domínio oficial;
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

Backend:
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
UI `career360/frontend/app-i.js` = LIVE na produção atual.

## 5. V13 — Meu Perfil Visual LIVE

Frontend: `career360/frontend/app-j.js`.

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

Não existe URL pública nem exposição automática.

## 6. V14 — Professional Photo Studio LIVE

Modelo canônico:
- `career_profile_photo_variants`;
- `career_profile_photo_settings`.

Edges ACTIVE / JWT required:
- `career-photo-studio` V11;
- `career-profile-photo` V10.

Frontend:
`career360/frontend/app-k.js` = LIVE.

Fluxo:
`ORIGINAL -> CONTEXTO DE CARREIRA -> ESTILO -> POLIMENTO LOCAL -> ANTES/DEPOIS -> ACEITAR OU MANTER ORIGINAL`

Estilos:
- executive;
- commercial;
- modern;
- creative;
- professional.

Contexto usa somente cargo atual + cargos-alvo.

Local Professional Polish:
- crop 4:5;
- segmentação pessoa/fundo quando disponível;
- fundo profissional por estilo;
- iluminação/contraste/saturação leves;
- fallback canvas;
- JPEG local;
- upload privado;
- comparação Original x Profissional;
- aceite ou rollback para original.

Runtime atual:
`PHOTO_STUDIO_PROVIDER=local-studio-v1`
`AI_GENERATION_EXTERNAL=NOT_CONFIGURED`

Não declarar geração externa/Cloudflare LIVE. `generate_ai` é fail-closed e a UI usa o caminho local zero-cash.

A variante accepted passa a ser devolvida como foto ativa por `career-profile-photo`, portanto Minha Página / Meu Perfil / PDF usam a seleção aprovada. Nova foto original remove/invalida variantes anteriores.

Release:
`career360/releases/MASTER_PILOT_1_0_PROFESSIONAL_PHOTO_STUDIO_V14_2026-09-05.md`

## 7. Radar / Matching

`CHAMPION=v2.0`
`ROLLBACK=v1.0`
Threshold: 72.
Radar piloto: 10 fontes estruturadas, rotação ~horária, cobertura completa ~4h e `Pesquisar agora`.
Zero vaga qualificada é estado válido.

## 8. Currículo / Perfil

Parser: `career360-edge-parser/1.0.3`.
Separa summary/highlights/leadership/experience/education/skills/languages/certifications.
Regra: `EXTRAIR -> MOSTRAR -> USUÁRIO CONFIRMA -> VIRA FATO`.
Perfil/CV V3 usa somente informação confirmada/aceita.
Foto no PDF é opt-in.

## 9. Segurança / pré-Beta

Security Advisor pós-V14:
- nenhum lint estrutural novo de RLS;
- permanece somente `auth_leaked_password_protection=DISABLED/WARN`.

Também pendente:
`SUPABASE_GLOBAL_SITE_URL_REDIRECT_ALLOWLIST=NOT_YET_PROVEN`.

## 10. Próximos gates

1. teste Android autenticado do V14: gerar/comparar/aceitar/reverter foto;
2. confirmar V12/V13 visualmente no Android;
3. conectar e-mail OAuth + receipts reais;
4. ligar candidatura real ao funil;
5. follow-up scheduler;
6. reprocessar/confirmar currículo 1.0.3;
7. hidratar catálogo de empregadores;
8. ampliar Radar mantendo precisão;
9. resolver redirect/password warning;
10. Career Learning Engine;
11. Founding Beta 20 somente após decisão explícita.

## 11. DO NOT FAKE / DO NOT REDO

- não reconstruir Career;
- não copiar LinkedIn/trade dress;
- não usar foto/idade/plano no FIT;
- não inventar fatos;
- não fingir vaga/candidatura/e-mail;
- não fingir geração externa de imagem;
- não substituir original silenciosamente;
- não abrir Beta automaticamente.

`LAST_VERIFIED_CHANGE=V14_OFFICIAL_PRODUCTION_V12_V13_V14_UI_LIVE_PHOTO_STUDIO_LOCAL_ZERO_CASH_BACKEND_STUDIO_V11_PROFILE_PHOTO_V10`

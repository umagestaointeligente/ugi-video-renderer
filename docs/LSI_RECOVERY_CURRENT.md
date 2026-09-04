# LSI — RECOVERY CURRENT

Status: CURRENT / AUTORITATIVO PARA HANDOFF
Atualizado: 2026-09-04 BRT
Âncora humana: `Recovery LSI`
Alias técnico interno: `LSI::RECOVERY::CURRENT`

## 0. Estado global

`LSI_RECOVERY=TRUE`
`CURRENT_FOCUS=LSI_CAREER_360_MASTER_PILOT_1_0`
`CURRENT_STATUS=MASTER_PILOT_ACTIVE_V12_PROACTIVE_BACKEND_WITH_V11_1_UI`
`VERIFIED_REVENUE=R$0,00` para lógica de incubação; reconfirmar antes de decisão monetária.

## 1. Fonte canônica

Repository: `umagestaointeligente/ugi-video-renderer`
Branch: `main`
Backend: Supabase `nxjdnzdxclszqyqrkwdk`, `sa-east-1`
Frontend oficial: `https://lsi-career-360.vercel.app/`
Vercel project: `prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP`
Arquitetura: `VERCEL STATIC FRONTEND -> SUPABASE AUTH/DATA/EDGE BACKEND`

Produção visual comprovada atual: V11.1
Deployment: `dpl_EjNc9WzK1uPCZFWhY8ympukcAMGG`
Rollback visual imediato V11: `dpl_59kEVUkAGkkZZXfRcRP9p4duWoSF`

## 2. Gates atuais

`DEDICATED_PROJECT=PASS`
`AUTH=LIVE`
`MASTER_ROLE=LIVE`
`REAL_AUTH_E2E=PASS`
`CAREER_PRIVACY_P0=PASS_MASTER_PILOT_SCOPE`
`MULTIUSER_ISOLATION=PASS`
`SAFE_FILE_PIPELINE=PASS_MASTER_PILOT_SCOPE`
`MATCH_ENGINE_V2=CHAMPION`
`MATCH_ENGINE_V1=ROLLBACK`
`NO_FABRICATION_GUARD=PASS_MASTER_PILOT_SCOPE`
`FRONTEND_HOSTING=PASS_VERCEL`
`GUIDED_ONBOARDING_V6=LIVE`
`PROFILE_CV_V7_V8=LIVE`
`UX_V11_1=LIVE`
`AUTOMATED_OPPORTUNITY_RESEARCH=LIVE_PILOT_SCOPE`
`PROACTIVE_AGENT_CORE_V12=LIVE`
`PROACTIVE_DIGEST_CRON=LIVE`
`PROACTIVE_UI_V12=VERSIONED_NOT_YET_PROMOTED`
`MAIL_DECISION=LIVE`
`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`
`PUBLIC_BETA=NOT_OPENED_PRODUCT_DECISION`

Security Advisor atual:
- sem lint estrutural novo de RLS;
- permanece `auth_leaked_password_protection = WARN / DISABLED`.
Não declarar `PASS_ZERO_LINTS` enquanto esse WARN existir.

## 3. Princípios de produto

`O CLIENTE NÃO PREENCHE. O CLIENTE CONFIRMA.`
`O CLIENTE NÃO OPERA A BUSCA. O AGENTE OPERA; O CLIENTE CONFIRMA O QUE IMPORTA.`
`O CAREER NÃO DEPENDE DO USUÁRIO ABRIR O CHAT PARA CONTINUAR TRABALHANDO.`

- privacidade antes de matching;
- idade nunca entra no matching;
- foto nunca entra no matching/FIT;
- plano pago nunca altera FIT;
- plano pode alterar cadência de acompanhamento;
- salário oculto/estimado nunca vira fato;
- nenhuma candidatura vira `applied` sem evidência real;
- nenhum e-mail vira `sent` apenas porque foi aprovado;
- currículo/perfil nunca fabrica experiência, cargo, empresa, resultado, competência, formação ou certificação.

## 4. UX atual — V11.1 LIVE

Superfície principal:
- `Minha Página` = perfil profissional limpo;
- `Oportunidades` = Radar;
- `Meu Agente`;
- edição/suporte ficam em superfícies secundárias/`Mais`;
- Painel Mestre somente role master.

Minha Página suporta:
- foto opcional;
- nome/headline/localização;
- resumo compacto;
- competências;
- Destaques profissionais;
- Liderança e escopo;
- Experiência;
- Formação.

Smart CV PDF inclui Destaques/Liderança quando disponíveis e foto opt-in quando autorizada.

Frontend V11.1: `career360/frontend/app-h.js`
Commit carregado pela produção: `2bff879b2b2a99815ed3933009f9a6a19a8a9501`

## 5. Proactive Agent V12 — BACKEND LIVE

Objetivo:
`PESQUISAR -> ANALISAR -> AGIR -> REGISTRAR -> ACOMPANHAR -> DETECTAR MUDANÇA -> AVISAR -> CONTINUAR`

Componentes LIVE:
- `career_activity_ledger`;
- `career_digest_preferences`;
- `career_digest_runs`;
- `career_notifications`;
- `career_applications` foundation;
- `career_mail_actions` foundation;
- Edge `career-proactive-digest`;
- Edge `career-proactive-status`;
- Edge `career-mail-decision`.

Cadências suportadas:
`4h / 6h / 8h / 12h`.

Conta piloto atual:
`plan_key=pilot`
`cadence_hours=4`

Cron:
`career-proactive-digest`
Schedule: `7 * * * *`
Estado: `ACTIVE`

O cron roda a cada hora, mas só gera digest quando `next_digest_at` venceu.

QA real do digest:
- ciclo forçado HTTP 200;
- 1 usuário processado;
- 1 digest criado;
- janela do teste: 1 oportunidade analisada / 0 qualificada;
- segundo ciclo imediatamente após: 0 usuários processados, comprovando cadência sem duplicação.

QA transacional com rollback:
- candidatura `awaiting_user` -> 1 Ledger event + 1 notification;
- mensagem crítica simulada -> 1 Ledger event + 1 critical notification;
- 0 dados QA persistidos.

## 6. UI Proativa V12 — NÃO PROMOVIDA

Arquivo versionado:
`career360/frontend/app-i.js`

Prevê:
- card `Atualizações do seu agente` na Minha Página;
- última/próxima atualização;
- analisadas/qualificadas/candidaturas/respostas;
- alertas críticos/action-required;
- badge no Meu Agente;
- `Atualizar agora`.

`PROACTIVE_UI_V12=VERSIONED_NOT_YET_PROMOTED`

Não declarar LIVE até novo bundle Vercel carregar `app-i.js` no domínio oficial e passar teste autenticado no Android.

## 7. E-mail / autonomia

Reutiliza `career_action_permissions`.

Modos:
- `suggestion`;
- `one_tap`;
- `controlled_autopilot`.

Permissões técnicas:
- inbox monitoring;
- recruiter reply draft/send;
- follow-up draft/send;
- auto-send de acknowledgement simples;
- auto-send de disponibilidade simples;
- auto-send de follow-up.

Regra dura:
`always_confirm_sensitive_email=true`.

Categorias tratadas como sensíveis no gate:
- salary;
- offer;
- documents;
- identity;
- interview_commitment;
- legal.

`career-mail-decision` permite:
- ler/alterar política;
- approve;
- copy;
- dismiss.

Aprovar = registrar autorização.
Aprovar NÃO = enviar.

`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`.
Conectar Gmail/Outlook exige OAuth/consentimento do próprio usuário + receipt real de entrega.

## 8. Currículo — Parser 1.0.3

`PARSER_VERSION=career360-edge-parser/1.0.3`
`career-document-process=ACTIVE / JWT_REQUIRED`

Separa:
- summary;
- highlights;
- leadership;
- experience;
- education;
- skills;
- languages;
- certifications.

Regra:
`EXTRAIR -> MOSTRAR -> USUÁRIO CONFIRMA -> VIRA FATO`

## 9. Perfil Profissional / Currículo Inteligente — V3

Edge: `career-professional-profile=ACTIVE / V3 / JWT_REQUIRED`
Persistência: `career_professional_profile_versions`

Consome apenas dados confirmados/aceitos e produz headline, resumo, skills, highlights, leadership, experience, education, languages e certifications.

Versionamento:
`draft -> accepted -> superseded`

## 10. Conte do Seu Jeito — LIVE

Fluxo:
`FALAR/ESCREVER -> ORGANIZAR -> MOSTRAR -> APROVAR/AJUSTAR/DESCARTAR -> PERFIL/CURRÍCULO`

Somente narrativa `accepted` entra no Perfil Profissional.

## 11. Foto

`career-profile-photo=LIVE / JWT_REQUIRED`
- opcional;
- storage privado;
- não entra no FIT;
- não inferir atributos sensíveis;
- foto em PDF opt-in.

`PROFESSIONAL_PHOTO_STUDIO=NOT_LIVE`
Não mostrar botão até image-to-image + preview + aceite explícito funcionarem ponta a ponta.

## 12. Radar automático — LIVE piloto

`AUTOMATED_OPPORTUNITY_RESEARCH=LIVE_PILOT_SCOPE`
Fontes piloto ativas: 10.
Ciclo: aproximadamente 1h por lote/rotação, cobertura completa ~4h no desenho atual.
Ação manual: `Pesquisar agora`.

Region Filter V2 LIVE.
Última limpeza integral comprovada:
- 126 anteriormente ativas;
- 70 expiradas como ruído regional;
- 56 permaneceram ativas no recorte naquele checkpoint;
- 0 qualificadas naquele checkpoint.

Zero qualificada é estado válido.

Edges:
- `career-opportunity-research`;
- `career-opportunity-list`;
- `career-radar-status`.

## 13. Matching V2 — CHAMPION

`CHAMPION=v2.0`
`ROLLBACK=v1.0`

Combina família profissional bilíngue, senioridade, similaridade lexical, competências quando evidenciadas, localização, modelo de trabalho e setor quando aplicável.

Gates anteriores ao score:
- privacidade;
- salário explícito abaixo do piso;
- modelo incompatível;
- localização não permitida quando aplicável.

Threshold de referência: `72`.
QA de promoção: 6/6 casos esperados.

## 14. Empresa / autocomplete

`career-employer-suggest=LIVE`.
`EMPLOYER_CATALOG_HYDRATION=PENDING`.
Não fingir cobertura ampla.

## 15. Auth / redirect / segurança

Supabase Auth + RLS.
Service role nunca no frontend.

Pendências pré-Beta:
`SUPABASE_GLOBAL_SITE_URL_REDIRECT_ALLOWLIST=NOT_YET_PROVEN`
`LEAKED_PASSWORD_PROTECTION=DISABLED/WARN`

## 16. Próximos gargalos reais

1. promover `app-i.js` no bundle oficial Vercel e testar no Android;
2. conectar provedor real de e-mail com OAuth/consentimento por usuário;
3. ingestão de e-mail -> resumo -> classificação -> resposta sugerida;
4. delivery somente depois de policy gate + receipt real;
5. ligar submissão real de candidatura à tabela `career_applications`;
6. follow-up scheduler por candidatura;
7. alertas críticos fora do digest;
8. reprocessar currículo real pelo Parser 1.0.3 e confirmar draft;
9. hidratar catálogo de empregadores;
10. ampliar fontes do Radar sem degradar precisão;
11. provar redirect allowlist;
12. resolver leaked-password protection antes da Beta;
13. Career Learning Engine;
14. Professional Photo Studio somente com endpoint real;
15. Founding Beta 20 somente após decisão explícita.

## 17. DO NOT REDO / DO NOT FAKE

- não reconstruir Career do zero;
- não copiar LinkedIn/trade dress;
- não tornar foto obrigatória;
- não usar foto/idade/plano no FIT;
- não reintroduzir vaga manual ao candidato;
- não transformar inferência em fato;
- não conservar raw por conveniência;
- não fingir oportunidade qualificada;
- não fingir candidatura aplicada;
- não fingir e-mail enviado;
- não marcar `sent` a partir de `approved`;
- não declarar UI V12 LIVE antes do deployment validado;
- não declarar CI PASS sem check real;
- não declarar Security Advisor zero warnings;
- não abrir Beta automaticamente;
- não criar recovery paralelo.

## 18. Leitura sob demanda

Manifesto: `docs/projects/LSI_CAREER360.md`
V11.1: `career360/releases/MASTER_PILOT_1_0_INTELLIGENCE_UX_V11_1_2026-09-04.md`
V12 Proactive: `career360/releases/MASTER_PILOT_1_0_PROACTIVE_AGENT_V12_2026-09-04.md`

## 19. Última alteração verificada

`LAST_VERIFIED_CHANGE=PROACTIVE_AGENT_V12_CORE_LIVE_DIGEST_CRON_ACTIVE_LEDGER_NOTIFICATIONS_APPLICATION_MAIL_FOUNDATION_MAIL_DECISION_LIVE_UI_VERSIONED_NOT_PROMOTED_MAIL_DELIVERY_NOT_LIVE`

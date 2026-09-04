# LSI — RECOVERY CURRENT

Status: CURRENT / AUTORITATIVO PARA HANDOFF
Atualizado: 2026-09-04 BRT
Âncora humana: `Recovery LSI`

## 0. Estado global

`CURRENT_FOCUS=LSI_CAREER_360_MASTER_PILOT_1_0`
`CURRENT_STATUS=V11_1_PRODUCTION_V12_PROACTIVE_BACKEND_LIVE_V13_VISUAL_PROFILE_VERSIONED`
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

Arquitetura Vercel atual continua bundle estático/framework null. Não fazer deploy cego do projeto; promoções visuais devem preservar os scripts já pinados e manter rollback.

## 2. Produto LIVE

`AUTH=LIVE`
`MASTER_ROLE=LIVE`
`REAL_AUTH_E2E=PASS`
`CAREER_PRIVACY_P0=PASS_MASTER_PILOT_SCOPE`
`MULTIUSER_ISOLATION=PASS`
`SAFE_FILE_PIPELINE=PASS_MASTER_PILOT_SCOPE`
`PROFILE_PHOTO_PRIVATE_BACKEND=LIVE`
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
- perfil não é público sem consentimento explícito.

## 4. Proactive Agent V12 — BACKEND LIVE

Componentes:
- `career_activity_ledger`;
- `career_digest_preferences`;
- `career_digest_runs`;
- `career_notifications`;
- `career_applications` foundation;
- `career_mail_actions` foundation;
- `career-proactive-digest`;
- `career-proactive-status`;
- `career-mail-decision`.

Cadências suportadas: `4h / 6h / 8h / 12h`.
Conta piloto: `4h`.
Cron: `career-proactive-digest`, schedule `7 * * * *`, ACTIVE.

QA comprovado:
- primeiro ciclo forçado: 1 usuário / 1 digest;
- segundo ciclo imediato: 0 usuários, sem duplicação;
- `awaiting_user` -> Ledger + action_required;
- mensagem crítica simulada -> Ledger + critical notification;
- testes transacionais não deixaram dados QA.

Política de e-mail:
- suggestion;
- one_tap;
- controlled_autopilot.

`always_confirm_sensitive_email=true` para salary/offer/documents/identity/interview_commitment/legal.

Conta piloto permanece conservadora:
`autonomy_level=one_action`
`email_autonomy_mode=suggestion`
`allow_inbox_monitoring=false`
`allow_recruiter_reply_send=false`
`allow_followup_send=false`

## 5. UI Proativa V12 — PRONTA, NÃO PROMOVIDA

Arquivo:
`career360/frontend/app-i.js`

Prevê:
- `Atualizações do seu agente`;
- última/próxima atualização;
- analisadas/qualificadas/candidaturas/respostas;
- alertas críticos/action-required;
- badge no Meu Agente;
- Atualizar agora.

`PROACTIVE_UI_V12=VERSIONED_NOT_YET_PROMOTED`

## 6. Visual Profile V13 — PRONTO, NÃO PROMOVIDO

Arquivo:
`career360/frontend/app-j.js`
Release:
`career360/releases/MASTER_PILOT_1_0_VISUAL_PROFILE_V13_2026-09-04.md`

Nova arquitetura de experiência:
`MINHA PÁGINA -> MEU PERFIL -> OPORTUNIDADES -> MEU AGENTE -> MAIS`

### Minha Página
Uso diário, enxuto:
- identidade resumida;
- agente trabalhando;
- Radar;
- alertas importantes;
- poucos atalhos.

### Meu Perfil
Superfície visual interna própria da LSI:
- capa;
- foto;
- nome/headline/localização;
- selo `Só você vê por enquanto`;
- Sobre;
- Destaques;
- Liderança/Escopo;
- Experiência em timeline;
- competências em chips;
- direcionamento de carreira;
- formação;
- idiomas/certificações.

Ações:
- `Copiar para LinkedIn` abre painel por blocos: Headline/Sobre/Experiência/Competências;
- `Baixar currículo`;
- `Editar informações`.

Não existe ainda:
- URL pública;
- compartilhamento externo automático;
- indexação;
- exposição a recrutadores.

Futura publicação deve obedecer:
`PRIVATE -> PREVIEW -> SELECT FIELDS -> EXPLICIT CONSENT -> SHARE/REVOKE`

`VISUAL_PROFILE_V13=VERSIONED_NOT_YET_PROMOTED`

## 7. Currículo / Perfil

Parser: `career360-edge-parser/1.0.3`.
Separa summary/highlights/leadership/experience/education/skills/languages/certifications.
Regra: `EXTRAIR -> MOSTRAR -> USUÁRIO CONFIRMA -> VIRA FATO`.

Perfil/CV V3 consome somente informação confirmada/aceita.
Foto no PDF continua opt-in.

## 8. Radar / Matching

`CHAMPION=v2.0`
`ROLLBACK=v1.0`
Threshold de referência: `72`.

Radar piloto:
- 10 fontes estruturadas;
- rotação aproximadamente horária;
- cobertura completa ~4h no desenho atual;
- `Pesquisar agora` disponível.

Region Filter V2 removeu ruído internacional causado por texto institucional.
Zero vaga qualificada é estado válido; não mostrar vaga ruim para preencher tela.

## 9. Segurança / pendências pré-Beta

Security Advisor no último checkpoint:
- sem lint estrutural novo de RLS;
- `auth_leaked_password_protection=DISABLED/WARN` permanece.

Também pendente:
`SUPABASE_GLOBAL_SITE_URL_REDIRECT_ALLOWLIST=NOT_YET_PROVEN`.

Não declarar `PASS_ZERO_LINTS`.

## 10. Próxima promoção visual

Promover V12 + V13 juntas em bundle controlado:
- manter todos os scripts da V11.1;
- adicionar `app-i.js`;
- adicionar `app-j.js`;
- validar alias oficial;
- HTTP 200;
- runtime errors;
- teste autenticado Android;
- manter V11.1 como rollback.

Não usar `deploy current project` cego enquanto a rota de bundle estático não estiver reconstruída com segurança.

## 11. Próximos gargalos

1. promoção controlada V12+V13;
2. teste Android da Minha Página + Meu Perfil;
3. conectar provedor real de e-mail com OAuth por usuário;
4. ingestão e-mail -> resumo -> estágio -> resposta sugerida;
5. delivery apenas com policy gate + receipt;
6. ligar submissão real de candidatura ao funil;
7. follow-up scheduler;
8. reprocessar/confirmar currículo pelo Parser 1.0.3;
9. hidratar catálogo de empregadores;
10. ampliar Radar mantendo precisão;
11. Professional Photo Studio com geração real;
12. resolver redirect/password warning;
13. Career Learning Engine;
14. Founding Beta 20 somente após decisão explícita.

## 12. DO NOT FAKE / DO NOT REDO

- não reconstruir Career;
- não copiar LinkedIn/trade dress;
- não chamar perfil de público enquanto for privado;
- não usar foto/idade/plano no FIT;
- não inventar fatos;
- não fingir vaga/candidatura/e-mail;
- não marcar sent a partir de approved;
- não expor identidade sem consentimento;
- não declarar UI V12/V13 LIVE antes do deployment validado;
- não abrir Beta automaticamente.

## 13. Leitura sob demanda

Manifesto: `docs/projects/LSI_CAREER360.md`
V11.1: `career360/releases/MASTER_PILOT_1_0_INTELLIGENCE_UX_V11_1_2026-09-04.md`
V12: `career360/releases/MASTER_PILOT_1_0_PROACTIVE_AGENT_V12_2026-09-04.md`
V13: `career360/releases/MASTER_PILOT_1_0_VISUAL_PROFILE_V13_2026-09-04.md`

`LAST_VERIFIED_CHANGE=VISUAL_PROFILE_V13_VERSIONED_PROACTIVE_V12_BACKEND_LIVE_V12_V13_UI_NOT_YET_PROMOTED_V11_1_STILL_PRODUCTION`

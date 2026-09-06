# LSI — RECOVERY CURRENT

Status: CURRENT / AUTORITATIVO PARA HANDOFF
Atualizado: 2026-09-06 BRT
Âncora humana: `Recovery LSI`

Handoff canônico desta transição de chat:
`docs/LSI_CAREER360_HANDOFF_2026-09-05_1609.md`

## 0. Estado global

`CURRENT_FOCUS=LSI_CAREER_360_MASTER_PILOT_1_0`
`CURRENT_STATUS=V14_PRODUCTION_STABLE_V15_V16_BROWSER_VALIDATED_BUNDLE_PINNED_WAITING_VERCEL_AUTH`
`VERIFIED_REVENUE=R$0,00` para lógica de incubação; reconfirmar antes de decisão monetária.

REGRA:
`RUNTIME_COMPROVADO_VENCE_DOCUMENTO`.

## 1. Fontes canônicas / runtime

Repository: `umagestaointeligente/ugi-video-renderer`
Branch: `main`
Supabase: `nxjdnzdxclszqyqrkwdk`
Frontend oficial: `https://lsi-career-360.vercel.app/`
Vercel project: `prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP`
Vercel team: `team_ZJys00FTE2kK9yVtsqH5fHyF`

Produção visual oficial atual:
`dpl_98eN1wuVyk4wQmnYpG2jjsZ1ZazU`

Readback oficial mais recente em 2026-09-06 BRT:
- Supabase = `ACTIVE_HEALTHY`;
- `career-ui-state` V1 ACTIVE;
- `career-photo-studio` V11 ACTIVE;
- `career-profile-photo` V10 ACTIVE;
- Vercel production = `READY`;
- target `production`;
- aliases oficiais presentes;
- produção oficial continua no mesmo deployment V14;
- produção ainda carrega a versão V14 anterior `app-k@ac1ea580667724b49ee1e8b0c8e04dfc153565f3`;
- produção ainda NÃO carrega `app-l.js`;
- produção ainda NÃO carrega `app-m.js`;
- `V16_CURRENT_PRODUCTION_READBACK=V14_ONLY_NOT_PROMOTED`;
- nenhum runtime error Vercel no período final consultado.

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
`PHOTO_STUDIO_MOBILE_FALLBACK_HARDENING=BROWSER_VALIDATED_NOT_YET_PROMOTED`
`CAREER_UI_STATE_V15=LIVE`
`SCALE_DB_HARDENING_V15=LIVE`
`UI_RESPONSIVE_V15=BROWSER_VALIDATED_NOT_YET_PROMOTED`
`CLARITY_UI_V16=BROWSER_VALIDATED_BUNDLE_PINNED_NOT_YET_PROMOTED`
`VERCEL_PROJECT_SCOPED_DEPLOY_ROUTE=PREVIEW_PROMOTE_PIPELINE_READY_WAITING_AUTH`
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
- foto profissional não substitui original sem aceite explícito;
- plano pode alterar frequência, nunca FIT;
- zero oportunidade qualificada é estado válido;
- custo zero / near-zero durante incubação.

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

O usuário não deve precisar perguntar o que aconteceu; o Career retorna com analisadas, qualificadas, candidaturas, respostas, entrevistas, pendências e próximos passos conforme capacidades reais.

## 5. V13 — Meu Perfil Visual LIVE

Frontend:
`career360/frontend/app-j.js`.

Arquitetura:
`MINHA PÁGINA -> MEU PERFIL -> OPORTUNIDADES -> MEU AGENTE -> MAIS`

Meu Perfil interno inclui:
- capa;
- foto;
- nome/headline/localização;
- Sobre;
- Destaques;
- Liderança/Escopo;
- timeline de experiência;
- competências;
- formação;
- idiomas/certificações;
- copiar blocos para LinkedIn;
- baixar Currículo Inteligente;
- selo `Só você vê por enquanto`.

Sem URL pública/exposição automática.
Não copiar LinkedIn/trade dress.

## 6. V14 — Professional Photo Studio LIVE + hardening versionado

Backend LIVE:
- `career_profile_photo_variants`;
- `career_profile_photo_settings`;
- `career-photo-studio` V11;
- `career-profile-photo` V10.

Provider LIVE:
`PHOTO_STUDIO_PROVIDER=local-studio-v1`
`AI_GENERATION_EXTERNAL=NOT_CONFIGURED`

Fluxo:
`ORIGINAL -> CONTEXTO DE CARREIRA -> ESTILO -> POLIMENTO LOCAL -> ANTES/DEPOIS -> ACEITAR OU MANTER ORIGINAL`

Contexto usa somente cargo atual + cargos-alvo.
Foto nunca entra no matching/FIT.
Original privada é preservada.

### Hardening mobile do processamento local

Correção versionada:
`career360/frontend/app-k.js`

Versão imutável a promover:
`6df7b4e63d7e52ce3c3f02247392b98f0393cbe8`

Comportamento:
- MediaPipe é usado quando funciona;
- falha em runtime/segmentação é capturada;
- segmentador é fechado quando possível;
- fluxo cai para polish canvas local seguro;
- aceite/reversão/identidade/backend permanecem inalterados.

Validação automatizada:
`PHOTO_STUDIO_SEGMENTATION_RUNTIME_FALLBACK=PASS`.

Esse hardening ainda NÃO é LIVE porque a produção oficial continua pinada à versão V14 anterior de `app-k.js`.

Gate humano Android ainda pendente:
`MELHORAR -> GERAR -> COMPARAR -> ACEITAR -> VALIDAR MINHA PÁGINA/MEU PERFIL/PDF -> VOLTAR À ORIGINAL -> CONFIRMAR ROLLBACK`.

## 7. V15 — UI State API + escala

### Backend LIVE

`career-ui-state` V1 / JWT required.

Fornece estado único para:
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

Migration:
`career_scale_indexes_v15`.

Canônico:
`career360/migrations/20260905_scale_indexes_v15.sql`.

Resultado:
- duplicate-index WARNs removidos;
- unindexed-FK removidos;
- permanecem apenas INFOs de unused indexes esperados no piloto.

### Frontend V15 — browser validated / not promoted

Arquivo:
`career360/frontend/app-l.js`.

Versão imutável atual a promover:
`4283646143425e4a3156e44100aabb475df88d27`.

Hardening feito antes da promoção:
1. MutationObserver idempotente, sem auto-loop/churn de DOM;
2. capacidades permanecem `unknown` até `career-ui-state` responder;
3. ResizeObserver evita escrita redundante;
4. touch targets pequenos elevados para mínimo de 44 px, inclusive fechamento do Photo Studio.

Commits relevantes:
- `c60a6e98a30db03a4c6d70f99fd133076618297d` — observer/idempotência;
- `f8e891b44fc69e1ee44505e4f89d69ca7104567c` — capacidades unknown/fail-closed;
- `4283646143425e4a3156e44100aabb475df88d27` — touch targets.

### Bundle canônico atual

`career360/frontend/index.html`

Commit:
`ece1582aa2a5253d4dc3ee7fbde7354896b57b01`

Pins:
- `app-k.js` -> `6df7b4e63d7e52ce3c3f02247392b98f0393cbe8`;
- `app-l.js` -> `4283646143425e4a3156e44100aabb475df88d27`.

## 8. V15 browser regression — PASS

Teste:
`career360/tests/v15-browser-smoke.mjs`

Workflow:
`.github/workflows/career360-v15-browser-smoke.yml`

Run:
`33988409906`

Resultado geral:
`PASS`.

Provas:
- JavaScript syntax gate PASS;
- canonical pin gate PASS;
- `RESPONSIVE_360=PASS mutations=7`;
- `RESPONSIVE_412=PASS mutations=7`;
- `RESPONSIVE_768=PASS mutations=7`;
- `RESPONSIVE_1180=PASS mutations=7`;
- `PHOTO_STUDIO_SEGMENTATION_RUNTIME_FALLBACK=PASS`.

Cobertura:
- ausência de overflow horizontal;
- navegação inferior fixa mobile;
- Meu Perfil 1 coluna mobile / 2 desktop;
- Photo Studio Antes/Depois 1 coluna mobile / 2 desktop;
- ações do Photo Studio 1 coluna nas menores larguras;
- touch targets >=44 px;
- safe state `unknown` até UI State resolver;
- rótulos canônicos de navegação;
- observer estabiliza sem loop;
- falha simulada de segmentação cai no fallback e produz variante local.

IMPORTANTE:
Browser regression PASS não substitui Android autenticado real.

## 9. Deploy Vercel — pipeline final pronto / autenticação externa ausente

A ação Vercel genérica disponível neste contexto não aceita `projectId` e a conta possui múltiplos projetos.

Guardrail:
`UNSCOPED_VERCEL_DEPLOY=DO_NOT_USE`.

Rota canônica project-scoped:
`.github/workflows/career360-vercel-deploy.yml`

Destino explícito:
- Team `team_ZJys00FTE2kK9yVtsqH5fHyF`;
- Project `prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP`.

### Pipeline endurecido

Commit do workflow:
`921fed05010b71d9a49f1a910f8c0a40ec49dc89`

CLI pinada:
`vercel@59.11.7`.

Estratégia final:
`VERIFY SOURCE -> BIND OFFICIAL PROJECT -> CREATE PREVIEW -> HTTP/PIN SMOKE -> PROMOTE EXACT PREVIEW -> VERIFY OFFICIAL ALIAS`.

Para `target=production`, o workflow NÃO faz um segundo build de produção.
Ele promove o mesmo Preview validado para evitar divergência entre Preview e Production.

O workflow:
- valida `app-k`, `app-l` e `app-m` antes de qualquer mutação;
- faz syntax gate;
- cria `.vercel/project.json` em runtime com IDs oficiais;
- cria Preview no projeto oficial;
- valida HTTP + pins do Preview;
- promove exatamente esse Preview quando target=production;
- valida o domínio oficial em até seis tentativas de convergência;
- aborta antes de mutar a Vercel se a credencial estiver ausente.

Trigger controlado:
`.github/career360-vercel-deploy.trigger`

Primeira tentativa anterior:
- run `33988095559`;
- `FAIL_CLOSED_BEFORE_VERCEL_MUTATION`;
- `VERCEL_TOKEN repository secret is not configured`.

### Tentativa de eliminar segredo persistente via GitHub OIDC

Probe read-only:
- workflow temporário `Career360 Vercel OIDC Probe`;
- run `34005662454`;
- GitHub emitiu OIDC token com sucesso;
- troca na Vercel retornou `HTTP 400` antes de qualquer acesso/mutação do projeto;
- nenhuma mutação Vercel ocorreu;
- workflow temporário removido no commit `02f7bedb284ae52aef879fc7edb8b88ce8ccf493`.

A documentação/skill atual da Vercel confirma:
`VERCEL_OIDC_FEDERATION_DOES_NOT_REPLACE_VERCEL_TOKEN_FOR_CLI_DEPLOYMENTS`.

Estado:
`VERCEL_DEPLOY_ROUTE=PREVIEW_PROMOTE_PIPELINE_READY_WAITING_AUTH`
`VERCEL_TOKEN=NOT_CONFIGURED`
`V15_PREVIEW_DEPLOYED=NO`
`V15_PRODUCTION_DEPLOYED=NO`
`V16_PREVIEW_DEPLOYED=NO`
`V16_PRODUCTION_DEPLOYED=NO`
`DEPLOY_AUTH_BLOCKER=EXTERNAL_AUTHENTICATED_SESSION_OR_SECRET_REQUIRED`

Sessões alternativas verificadas neste gate:
- Remote Desktop Commander = `PROIBIDO` por decisão do usuário; não sugerir esta rota novamente;
- Opera Browser Connector = browser desconectado.

Não criar token fictício, não extrair magic link/2FA de e-mail, não expor token em código/repositório/chat e não usar deploy sem escopo.

## 9A. V16 — Clarity UI / menos texto / decisão primeiro

Estado:
`CLARITY_UI_V16=BROWSER_VALIDATED_BUNDLE_PINNED_NOT_YET_PROMOTED`

Camada incremental:
`career360/frontend/app-m.js`

Pin imutável:
`3cd06d176f81e07c6f4dba1f7fb962f73be4ce34`

Bundle canônico com `app-k -> app-l -> app-m`:
`ac8a46fe5a5d3f28aab15c31c0bafd8e6558f844`

Release canônica:
`career360/releases/MASTER_PILOT_1_0_CLARITY_UI_V16_2026-09-06.md`

Objetivo da V16:
- reduzir texto repetitivo na superfície;
- melhorar hierarquia, respiro, bordas, sombras e densidade;
- transformar Meu Agente em superfície de decisão;
- manter métricas e pendências visíveis;
- esconder detalhe operacional que não precisa competir com a decisão;
- oferecer ações rápidas de consulta sem criar novas mutações.

Validação final sobre bundle canônico:
- run `34009190125`;
- job `101421875198`;
- `V16_CANONICAL_BUNDLE_PIN_GATE=PASS`;
- `V16_TOUCH_TARGET_POLICY=44PX`;
- `V16_TRUTHFUL_STATUS_POLICY=PASS`;
- `CLARITY_360=PASS mutations=6`;
- `CLARITY_412=PASS mutations=6`;
- `CLARITY_768=PASS mutations=6`;
- `CLARITY_1180=PASS mutations=6`;
- `V16_AGENT_QUICK_ACTIONS=PASS`;
- `V16_DYNAMIC_PROACTIVE_RECOMPACT=PASS`;
- `V16_TRUTHFUL_RUNTIME_DERIVATION=PASS`.

Hardening final antes de promoção:
- atalhos do agente >=44 px;
- `Atualizar` >=44 px;
- `Ok` >=44 px;
- padding do alerta ajustado para evitar colisão com a ação;
- badge sintético `Trabalhando` removido do cabeçalho do agente;
- o texto legado `Agente trabalhando` da V12 não é tratado como prova de atividade em tempo real;
- status visível derivado apenas de estado verificável: `Atualizando` quando a atualização está realmente em curso, `Atualizado` quando existe resumo real e `Aguardando` quando ainda não existe resumo;
- onboarding e suporte com copy reduzida, sem remover guardrails de privacidade/confirmacao;
- foco visível para teclado e `prefers-reduced-motion` respeitado.

IMPORTANTE:
Browser PASS + bundle pinado NÃO significa produção LIVE.
A V16 só vira LIVE após promoção comprovada no domínio oficial e gate móvel autenticado.

## 10. Radar / Matching

`CHAMPION=v2.0`
`ROLLBACK=v1.0`
Threshold: 72.
Radar piloto: fontes estruturadas, rotação automática e `Pesquisar agora`.
`AUTOMATED_OPPORTUNITY_RESEARCH=LIVE_PILOT_SCOPE`.
Zero vaga qualificada é estado válido.

A camada V10 (`app-g.js`) exibe Radar ativo e oculta cards antigos da home; a camada V9 (`app-f.js`) substitui o empty state antigo de oportunidades por um estado coerente com a pesquisa ativa. Textos legados ainda existentes no `app-b.js` pinado não são a superfície final após inicialização das camadas posteriores; não repinar a base apenas por esse texto sem necessidade funcional.

## 11. Currículo / Perfil

Parser:
`career360-edge-parser/1.0.3`.

Separa:
summary / highlights / leadership / experience / education / skills / languages / certifications.

Regra:
`EXTRAIR -> MOSTRAR -> USUÁRIO CONFIRMA -> VIRA FATO`.

Perfil/CV V3 usa somente informação confirmada/aceita.

## 12. Segurança / pré-Beta

Security Advisor atual:
`auth_leaked_password_protection=DISABLED/WARN`.

Supabase organization plan:
`free`.

Documentação Supabase atual:
Leaked Password Protection é recurso do plano Pro ou superior.

Decisão durante incubação zero-cash:
`LEAKED_PASSWORD_PROTECTION=KNOWN_PLAN_LIMITATION_NOT_UPGRADED`.

Não gerar assinatura/custo apenas para apagar esse WARN sem decisão explícita de produto/monetização.

Redirect de confirmação usado pelo cliente:
`https://lsi-career-360.vercel.app/?email-confirmado=1`.

Estado:
`SUPABASE_CLIENT_EMAIL_REDIRECT_TARGET=PROVEN_OFFICIAL_URL`
`SUPABASE_SERVER_REDIRECT_ALLOWLIST=NOT_YET_PROVEN`

A configuração hosted de Site URL / Additional Redirect URLs não é exposta pelas ferramentas Supabase disponíveis neste contexto. Não inferir allowlist server-side apenas do frontend.

Performance Advisor após Scale DB V15:
- sem duplicate-index WARN;
- sem unindexed-FK WARN;
- somente INFOs de unused indexes.

## 13. Gate único que falta para promoção V15/V16

Uma destas condições precisa existir sem expor credenciais no chat:

A. `VERCEL_TOKEN` válido cadastrado como repository secret no GitHub; OU
B. Browser Connector autenticado na Vercel com acesso suficiente para configurar/autorizar a rota project-scoped; OU
C. novo OAuth Device Flow em runner efêmero privado, com autorização humana explícita e identidade Vercel validada antes do deploy.

Guardrail absoluto:
`REMOTE_DESKTOP_COMMANDER=PROHIBITED_BY_USER_FOR_LSI_CAREER360`.
Não sugerir nem reutilizar Remote Desktop como rota de promoção.

Assim que uma condição válida existir, a rota canônica já permite executar sem nova arquitetura:
1. criar Preview project-scoped;
2. HTTP/pin smoke de `app-k`, `app-l` e `app-m`;
3. promover o MESMO Preview;
4. confirmar alias oficial;
5. checar runtime errors;
6. Android autenticado;
7. Photo Studio gerar/comparar/aceitar/reverter;
8. marcar V15/V16 e o hardening móvel como LIVE somente após prova.

## 14. Próximos gates depois da V15 LIVE

1. OAuth de e-mail + receipts reais;
2. candidaturas reais integradas a `career_applications`;
3. follow-up scheduler;
4. reprocessamento/validação humana Parser 1.0.3;
5. catálogo de empregadores e expansão do Radar mantendo precisão;
6. redirect auth hosted revalidado;
7. Career Learning Engine;
8. Founding Beta 20 somente após decisão explícita.

## 15. DO NOT FAKE / DO NOT REDO

- não reconstruir Career;
- não copiar LinkedIn/trade dress;
- não usar foto/idade/plano no FIT;
- não inventar fatos ou salários;
- não mostrar vaga ruim para preencher tela;
- não fingir vaga/candidatura/e-mail;
- não fingir geração externa de imagem;
- não substituir original silenciosamente;
- não declarar UI V15 LIVE antes da produção oficial carregar os pins validados e passar Android;
- não declarar hardening do Photo Studio LIVE antes do novo `app-k.js` chegar à produção;
- não usar deploy Vercel sem escopo determinístico;
- não colocar token Vercel no código/repositório/chat;
- não usar e-mail/OTP/magic link como atalho de autenticação automatizada;
- não abrir Beta automaticamente.

`LAST_VERIFIED_CHANGE=V16_RUNTIME_TRUTH_BROWSER_PASS_APP_M_3CD06D1_APP_L_428364_APP_K_6DF7B4_BUNDLE_AC8A46F_SMOKE_RUN_34009190125_JOB_101421875198_TRUTH_DERIVATION_PASS_DEPLOY_GATE_921FED0_PRODUCTION_STILL_V14_NOT_PROMOTED_AUTH_REQUIRED_REMOTE_DESKTOP_PROHIBITED`

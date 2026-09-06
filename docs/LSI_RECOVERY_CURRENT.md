# LSI — RECOVERY CURRENT

Status: CURRENT / AUTORITATIVO PARA HANDOFF
Atualizado: 2026-09-06 BRT
Âncora humana: `Recovery LSI`

Handoff canônico desta transição de chat:
`docs/LSI_CAREER360_HANDOFF_2026-09-05_1609.md`

## 0. Estado global

`CURRENT_FOCUS=LSI_CAREER_360_MASTER_PILOT_1_0`
`CURRENT_STATUS=V14_PRODUCTION_STABLE_V15_V16_BROWSER_VALIDATED_BUNDLE_PINNED_WAITING_IN_CHAT_PROJECT_SCOPED_VERCEL_MUTATION`
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
`PROACTIVE_DIGEST_TRUTH_V2=LIVE`
`VISUAL_PROFILE_V13=LIVE`
`PHOTO_STUDIO_V14=LIVE_LOCAL_ZERO_CASH`
`PHOTO_STUDIO_MOBILE_FALLBACK_HARDENING=BROWSER_VALIDATED_NOT_YET_PROMOTED`
`CAREER_UI_STATE_V15=LIVE`
`SCALE_DB_HARDENING_V15=LIVE`
`UI_RESPONSIVE_V15=BROWSER_VALIDATED_NOT_YET_PROMOTED`
`CLARITY_UI_V16=BROWSER_VALIDATED_BUNDLE_PINNED_NOT_YET_PROMOTED`
`VERCEL_PROJECT_SCOPED_DEPLOY_ROUTE=PREVIEW_PROMOTE_PIPELINE_READY_CHAT_CONNECTOR_MUTATION_UNSCOPED`
`MAIL_DECISION=LIVE`
`DELIVERY_EVIDENCE_GUARDS_V16=LIVE`
`MAIL_SENT_RECEIPT_GUARD_V16=LIVE`
`APPLICATION_APPLIED_RECEIPT_GUARD_V16=LIVE`
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

### V12 truthfulness hardening — digest V2 LIVE

`career-proactive-digest` foi promovida para V2 após readback vivo do código publicado.

Evidência canônica:
- source commit: `96cd4254eb972e8267e0bf3d39e37cf0da86f72c`;
- Supabase Edge Function: `career-proactive-digest` V2 `ACTIVE`;
- deployed `ezbr_sha256`: `aa677838765e62fe683309fee53832a9b36cf0e8d0bd176a773e1eee8300e83f`;
- empty-state factual: `Nenhuma novidade relevante foi registrada nesta janela.`;
- frase antiga `seu agente continua ativo` removida do código publicado por não constituir prova de atividade;
- autenticação preservada: cron exige secret validado por `career_validate_proactive_cron_secret`; ação manual exige `Bearer` validado por `auth.getUser()`.

Estado:
`PROACTIVE_DIGEST_TRUTH_V2=LIVE`

Esse LIVE é exclusivamente do backend de digest. Não altera o gate de promoção da UI V15/V16.

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

## 9. Deploy Vercel — pipeline final pronto / acesso somente pelo ChatGPT

A ação Vercel genérica disponível neste contexto não aceita `projectId` e a conta possui múltiplos projetos.

Guardrail:
`UNSCOPED_VERCEL_DEPLOY=DO_NOT_USE`.
`VERCEL_ACCESS_POLICY=CHATGPT_CONNECTOR_ONLY`.
`EXTERNAL_VERCEL_AUTH=PROHIBITED_BY_USER`.
`VERCEL_DEVICE_FLOW=PROHIBITED`.
`VERCEL_MANUAL_TOKEN_ROUTE=PROHIBITED`.
`PRODUCTOS_VERCEL_AUTH_ROUTE=PROHIBITED`.
`REMOTE_DESKTOP_COMMANDER=PROHIBITED_BY_USER_FOR_LSI_CAREER360`.

Rota canônica project-scoped:
`.github/workflows/career360-vercel-deploy.yml`

Destino explícito:
- Team `team_ZJys00FTE2kK9yVtsqH5fHyF`;
- Project `prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP`.

### Pipeline endurecido

Commit do workflow:
`bb344db78e61646926b0259c44552817149c861a`

CLI pinada:
`vercel@59.11.7`.

Estratégia final:
`VALIDATE SOURCE/TRUTH -> BIND OFFICIAL PROJECT -> CREATE PREVIEW -> HTTP/PIN/TRUTH SMOKE -> PROMOTE EXACT PREVIEW -> VERIFY OFFICIAL ALIAS`.

Para `target=production`, o workflow NÃO faz um segundo build de produção.
Ele promove o mesmo Preview validado para evitar divergência entre Preview e Production.

O workflow:
- oferece `target=validate`, que roda os gates de readiness sem credencial e sem qualquer mutação Vercel;
- valida `app-k`, `app-l` e `app-m` antes de qualquer mutação;
- exige a copy estática verdadeira `Você confirma o que importa. O Career 360 organiza sua busca.` e rejeita a copy legada não comprovada;
- faz syntax gate;
- cria `.vercel/project.json` em runtime com IDs oficiais;
- cria Preview no projeto oficial;
- valida HTTP + pins + copy verdadeira do Preview e rejeita a copy legada;
- promove exatamente esse Preview quando target=production, sem segundo build `--prod`;
- valida o domínio oficial em até seis tentativas de convergência, incluindo pins + copy verdadeira;
- aborta antes de mutar a Vercel se a credencial estiver ausente em `preview`/`production`.

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
`VERCEL_DEPLOY_ROUTE=PROJECT_SCOPED_PIPELINE_READY_BUT_CHAT_CONNECTOR_MUTATION_UNSCOPED`
`V15_PREVIEW_DEPLOYED=NO`
`V15_PRODUCTION_DEPLOYED=NO`
`V16_PREVIEW_DEPLOYED=NO`
`V16_PRODUCTION_DEPLOYED=NO`
`DEPLOY_BLOCKER=IN_CHAT_VERCEL_DEPLOY_ACTION_DOES_NOT_EXPOSE_PROJECT_ID`
`VERCEL_TEAM_PROJECT_COUNT=9`
`VERCEL_PROJECT_GIT_LINK=null`
`VERCEL_GIT_INTEGRATION_FOR_CAREER360=NOT_ACTIVE`

Regra operacional absoluta do usuário:
- Vercel só pode ser acessada/operada pelo conector Vercel dentro deste ChatGPT;
- não usar login externo, OAuth Device Flow, navegador externo, token manual, ProductOS como ponte de autenticação ou Remote Desktop;
- o conector interno já prova leitura do projeto `prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP`, deployments e runtime;
- a ação interna de deploy atualmente exposta é zero-argument e não permite selecionar `projectId`; como a conta tem múltiplos projetos, `deploy_to_vercel` permanece proibido até existir escopo determinístico dentro do Chat.

Não criar token fictício, não extrair magic link/2FA de e-mail, não expor token em código/repositório/chat e não usar deploy sem escopo.

## 9A. V16 — Clarity UI / menos texto / decisão primeiro

Estado:
`CLARITY_UI_V16=BROWSER_VALIDATED_BUNDLE_PINNED_NOT_YET_PROMOTED`

Camada incremental:
`career360/frontend/app-m.js`

Pin imutável:
`719c15ebfe89d212a19473b70ea6e615174601d9`

Bundle canônico com `app-k -> app-l -> app-m`:
`f572b824b49b2cc73d5d8389eae98391bcca63a8`

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
- run `34010764428`;
- job `101426061763`;
- `V16_CANONICAL_BUNDLE_PIN_GATE=PASS`;
- `V16_TOUCH_TARGET_POLICY=44PX`;
- `V16_TRUTHFUL_STATUS_POLICY=PASS`;
- `V16_AUTH_TRUTHFUL_COPY_POLICY=PASS`;
- `V16_STATIC_AUTH_TRUTH_SOURCE=PASS`;
- `V16_LEGACY_AUTH_COPY_ABSENT=PASS`;
- `V16_VERCEL_PROJECT_SCOPE_GATE=PASS`;
- `V16_VERCEL_VALIDATE_ONLY_GATE=PASS`;
- `V16_VERCEL_PREVIEW_TRUTH_SMOKE_POLICY=PASS`;
- `V16_VERCEL_EXACT_PREVIEW_PROMOTION_POLICY=PASS`;
- `CLARITY_360=PASS mutations=6`;
- `CLARITY_412=PASS mutations=6`;
- `CLARITY_768=PASS mutations=6`;
- `CLARITY_1180=PASS mutations=6`;
- `V16_AGENT_QUICK_ACTIONS=PASS`;
- `V16_DYNAMIC_PROACTIVE_RECOMPACT=PASS`;
- `V16_TRUTHFUL_RUNTIME_DERIVATION=PASS`;
- `V16_AUTH_TRUTHFUL_COPY=PASS`.

Hardening final antes de promoção:
- atalhos do agente >=44 px;
- `Atualizar` >=44 px;
- `Ok` >=44 px;
- padding do alerta ajustado para evitar colisão com a ação;
- badge sintético `Trabalhando` removido do cabeçalho do agente;
- o texto legado `Agente trabalhando` da V12 não é tratado como prova de atividade em tempo real;
- status visível derivado apenas de estado verificável: `Atualizando` quando a atualização está realmente em curso, `Atualizado` quando existe resumo real e `Aguardando` quando ainda não existe resumo;
- onboarding e suporte com copy reduzida, sem remover guardrails de privacidade/confirmacao;
- o HTML estático e a camada V16 usam a mesma copy pré-login verdadeira desde o primeiro byte: `Você confirma o que importa. O Career 360 organiza sua busca.`;
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


### Supabase security readiness — read-only audit 2026-09-06

Auditoria viva, sem mutação de banco:
- 43/43 tabelas ordinárias do schema `public` com RLS habilitado e pelo menos uma policy;
- policies de dados do usuário verificadas com `auth.uid() = user_id`; UPDATEs auditados possuem `USING` + `WITH CHECK` quando aplicável;
- funções `SECURITY DEFINER` do schema `public`: `EXECUTE=false` para PUBLIC/anon/authenticated e `EXECUTE=true` para service_role;
- `search_path` explicitamente configurado nas funções privilegiadas auditadas;
- nenhuma view/materialized view encontrada no schema `public`;
- buckets `career-profile-private` e `career-resumes-quarantine` permanecem `public=false`;
- `storage.objects` com RLS habilitado e sem policy direta para cliente, mantendo acesso privilegiado pelas Edge Functions;
- funções sem `verify_jwt` auditadas usam autenticação interna apropriada (secret validado, sessão/master quando aplicável) ou são redirect-only;
- media/foto e documentos auditados vinculam operações privilegiadas ao `user_id` autenticado.

Advisor atual:
- Security: somente `auth_leaked_password_protection=DISABLED/WARN`;
- Performance: somente INFOs de unused indexes esperados no piloto; sem duplicate-index/unindexed-FK WARN.

Estado:
`SUPABASE_SECURITY_READINESS_READ_ONLY_AUDIT=PASS`

Limites conhecidos permanecem:
`LEAKED_PASSWORD_PROTECTION=KNOWN_PLAN_LIMITATION_NOT_UPGRADED`
`SUPABASE_SERVER_REDIRECT_ALLOWLIST=NOT_YET_PROVEN`

### Delivery/application evidence guards V16 — LIVE

Antes da ativação de qualquer conector real de envio/candidatura, as tabelas estavam vazias e foram endurecidas fail-closed. Nenhum dado legado precisou ser corrigido.

Migrações canônicas:
- `career360/migrations/20260906_delivery_receipt_guards_v16.sql` — commit `d21f7cfbca17e2fab2a274ff9f5f154361eb6e7b`;
- `career360/migrations/20260906_delivery_receipt_identity_v16.sql` — commit `900398868256dae12faba0df869bd265eb690a45`.

Banco LIVE:
- `career_mail_actions.status='sent'` exige `direction='outbound'`, `sent_at`, `external_thread_ref_hash` e `delivery_receipt_hash`;
- `delivery_receipt_hash` é identidade separada da thread e deve vir de sucesso retornado pelo provider;
- `(user_id, delivery_receipt_hash)` é único quando o recibo existe;
- `career_applications.status='applied'` exige `applied_at` + `external_application_ref_hash`;
- `(user_id, external_application_ref_hash)` é único quando a referência existe;
- ambos os CHECK constraints foram lidos no catálogo como `convalidated=true`.

A camada atual `career-mail-decision` continua correta: `approve` grava somente `approved` e retorna `delivery_connector_required=true`; aprovação não vira `sent`.

Estados:
`DELIVERY_EVIDENCE_GUARDS_V16=LIVE`
`MAIL_SENT_RECEIPT_GUARD_V16=LIVE`
`APPLICATION_APPLIED_RECEIPT_GUARD_V16=LIVE`
`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`

Esses guards não provam que e-mail foi enviado ou candidatura foi realizada. Eles impedem que esses estados sejam persistidos sem a evidência mínima contratada.

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

A promoção só pode acontecer **dentro deste ChatGPT**, pelo conector Vercel, com escopo determinístico para:
- Team `team_ZJys00FTE2kK9yVtsqH5fHyF`;
- Project `prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP`.

Estado atual do conector:
- leitura project-scoped = `PROVEN`;
- `get_project`, `list_deployments`, `web_fetch_vercel_url` e runtime errors = disponíveis;
- mutação de deploy exposta = `deploy_to_vercel()` sem argumentos;
- seleção explícita de `projectId` para a mutação = `NOT_EXPOSED`;
- portanto `UNSCOPED_VERCEL_DEPLOY=DO_NOT_USE`.

Rotas proibidas por decisão do usuário:
`EXTERNAL_BROWSER_AUTH=PROHIBITED`
`OAUTH_DEVICE_FLOW=PROHIBITED`
`MANUAL_VERCEL_TOKEN=PROHIBITED`
`PRODUCTOS_VERCEL_AUTH_BRIDGE=PROHIBITED`
`REMOTE_DESKTOP_COMMANDER=PROHIBITED`

Quando o conector interno expuser deploy/promoção project-scoped, executar sem nova arquitetura:
1. criar Preview no projeto oficial;
2. validar HTTP + pins de `app-k`, `app-l` e `app-m`;
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

`LAST_VERIFIED_CHANGE=DELIVERY_EVIDENCE_GUARDS_V16_LIVE_MAIL_SENT_REQUIRES_PROVIDER_RECEIPT_HASH_THREAD_AND_SENT_AT_APPLICATION_APPLIED_REQUIRES_EXTERNAL_REF_AND_APPLIED_AT_RECEIPT_REUSE_UNIQUE_PROACTIVE_DIGEST_TRUTH_V2_LIVE_SUPABASE_SECURITY_AUDIT_PASS_V16_FRONTEND_STILL_NOT_PROMOTED_VERCEL_CHAT_CONNECTOR_MUTATION_STILL_UNSCOPED_PRODUCTION_STILL_V14`

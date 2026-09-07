# LSI Career 360 — Runtime Truth Hardening — 2026-09-07

Timezone operacional: America/Sao_Paulo

Regra soberana: `RUNTIME_COMPROVADO_VENCE_DOCUMENTO`.

Este documento registra apenas estados comprovados no runtime. Ele não promove preview a produção, não afirma envio/candidatura sem receipt e não altera consentimentos.

## 1. LSI — rota auxiliar reativada e comprovada

Core existente preservado: GitHub OIDC -> Cloudflare Worker `lsi-zero-cost-broker` -> Workers AI, envelope RSA-OAEP-256 + A256GCM, zero provider pago, até 8 tarefas paralelas.

Primeira tentativa:
- branch `lsi-broker-job-career360-routes-20260906`;
- commit `622a252fd44b7532299d3a267f991335c6736ca4`;
- run `34063569299` / job `101568314902`;
- FAIL-CLOSED antes de modelo: envelope Base64 inválido;
- nenhuma decisão/model output produzido.

Transporte corrigido dentro do GitHub runner com WebCrypto e OIDC efêmero:
- commit `e983ade1a3542a3c5eea592d1a4a75c8a98b8781`;
- run `34063653309` SUCCESS;
- envelope/receipt criptográfico PASS;
- Gemma/GLM retornaram `empty_model_output`, portanto não foram tratados como sucesso.

Fallback comprovado:
- Llama 3.1 8B Fast via papel `cheap_text`;
- commit `010fdce7683adee250948dd12be4c1720917c68a`;
- run `34063813926`;
- 4/4 tarefas PASS;
- elapsed `4245 ms`;
- artifact digest `sha256:b9a930e7238bbfe86c4be77903d1fd58edb71766ae3bee0354cfadd0e2008fab`.

Estado:
`LSI_ROUTE_COUNCIL_LLAMA=LIVE_PROVEN`
`LSI_GEMMA_GLM=DEGRADED_EMPTY_OUTPUT_NOT_CHAMPION`
`LSI_DECISION_AUTHORITY=LOLA_FINAL_GATE`

## 2. Frontend — Cloudflare deixa de ser hipótese e vira rota de entrega comprovada

Objetivo: provar uma saída in-app/autônoma para entrega do V16 sem depender da mutação Vercel não escopada.

Preview isolado:
`https://career360-preview-20260906.umagestaointeligente.workers.dev`

Configuração:
- branch `career360-cloudflare-preview-20260906`;
- Workers Static Assets;
- `workers_dev=true`;
- SPA fallback;
- `career360/frontend/.assetsignore` exclui `vercel.json` e `.vercel/**`.

Deploy inicial comprovado:
- run `34063997693`;
- upload/deploy Cloudflare SUCCESS;
- Worker version `2a1f211a-c8b2-47a3-83cc-d21d43dcc296`;
- gate inicial posterior falhou porque `/vercel.json` devolve `index.html` por SPA fallback, não porque o arquivo foi publicado.

Gate corrigido para conteúdo real, sem blind retry:
- commit `558ee5fb87a0574219701fc873530d446b75eb6f`;
- run `34064086287` SUCCESS;
- HTTP 200;
- pins V16 presentes:
  - app-k `6df7b4e63d7e52ce3c3f02247392b98f0393cbe8`;
  - app-l `4283646143425e4a3156e44100aabb475df88d27`;
  - app-m `719c15ebfe89d212a19473b70ea6e615174601d9`;
- copy canônica presente;
- copy antiga ausente;
- conteúdo real de `vercel.json` não exposto;
- produção oficial Vercel não alterada.

Browser smoke live:
- test `career360/tests/v16-cloudflare-live-smoke.mjs` na branch preview;
- primeiro run `34084739293` falhou somente por expectativa incorreta do texto do CTA de signup (`Criar conta` vs runtime canônico `Criar minha conta`);
- handler real em `app-a.js` confirmou o runtime canônico;
- teste corrigido sem alteração do produto;
- commit `7341dc70720a30b85086d1eb080d692e6ca89968`;
- run `34084862777` / job `101626832212` SUCCESS;
- Chromium real:
  - 360 px PASS;
  - 412 px PASS;
  - 768 px PASS;
  - 1180 px PASS;
- prelogin V16 PASS;
- responsividade PASS;
- `pageerror=0`, console error=0, request failure=0;
- alternância login/signup PASS;
- touch target de auth >= 44 px;
- `OFFICIAL_PRODUCTION_PROMOTION=NONE`.

Estado:
`CLOUDFLARE_V16_STATIC_PREVIEW=LIVE_VALIDATED_NOT_OFFICIAL`
`CLOUDFLARE_V16_BROWSER_PRELOGIN=PASS`
`CLOUDFLARE_FRONTEND_DELIVERY_ALTERNATIVE=PROVEN`
`VERCEL_NO_LONGER_SINGLE_FRONTEND_DELIVERY_PATH=TRUE`
`OFFICIAL_FRONTEND_PRODUCTION=VERCEL_V14_UNCHANGED`

## 3. Auth — confirmação funciona; redirect continua sendo defeito de UX

Readback direto de `auth.users`, sem exposição de e-mail:
- total users: 1;
- confirmed users: 1;
- unconfirmed users: 0;
- users with sign-in: 1.

Conclusão factual:
- o único usuário runtime está confirmado e já realizou login;
- o redirect conhecido para `localhost:3000` não impediu confirmação nem login desse usuário;
- o defeito continua real para a experiência pós-confirmação/new-user onboarding e não deve ser declarado corrigido.

A documentação atual do Supabase confirma rota administrativa oficial por Management API (`GET/PATCH /v1/projects/{ref}/config/auth`) para Site URL/redirect/template. O conector Supabase disponível nesta sessão não expõe essa mutação.

Probe de secrets GitHub para 6 nomes plausíveis de Management API token:
- branch `career360-supabase-auth-probe-20260907`;
- commit `4add35894bbb85c10f17a800d5c346e86ff067dc`;
- run `34084216893` / job `101625064545` SUCCESS;
- candidatos presentes: 0/6;
- nenhum valor de secret foi revelado.

Estado:
`AUTH_EMAIL_CONFIRMATION_EXISTING_RUNTIME_USER=PASS`
`AUTH_REDIRECT_LOCALHOST=UX_BUG_NOT_CURRENT_CONFIRMATION_INTEGRITY_BLOCKER`
`SUPABASE_SERVER_REDIRECT_ALLOWLIST=NOT_YET_PROVEN_OR_MUTABLE_IN_APP`
`SUPABASE_MANAGEMENT_TOKEN_ROUTE=NOT_AVAILABLE`
`AUTH_INSECURE_AUTO_CONFIRM_WORKAROUND=REJECTED`

## 4. Matching / métricas / radar / scheduler — regressão viva

Control plane:
- matching champion `v3.1-rolegraph` ACTIVE;
- rollback `v2.0`;
- `matching_role_graph` production component;
- `role_graph` v1.1 ACTIVE.

Router cross-regression:
- corpus champion: 57 oportunidades;
- `career_score_opportunity(..., false)` versus `career_score_opportunity_v3(..., false)`;
- comparação completa de score, classification, privacy, salary, breakdown e explanation;
- 57/57 exact matches;
- mismatches 0.

Métricas:
- champion `career_matches`: 57;
- `career_master_metrics.matches`: 57;
- alinhamento 57 = 57.

Evidência externa:
- `career_applications`: 0;
- `career_followups`: 0;
- `career_mail_actions`: 0.

Scheduler:
- scanned 0;
- ready_for_orchestration 0;
- waiting_permission 0;
- waiting_connector 0;
- cancelled 0.

Radar runtime:
- job id 3;
- schedule `37 * * * *`;
- active true;
- source_limit 3;
- cycle 60 min;
- matching v3.1-rolegraph;
- rollback v2.0;
- role-search-v2.

Estado:
`MATCH_ROUTER_V31_CROSS_REGRESSION=PASS_57_OF_57`
`MASTER_METRICS_CHAMPION_ALIGNMENT=PASS_57_EQ_57`
`RADAR_RUNTIME_TRUTH=PASS`
`FOLLOWUP_SCHEDULER_EMPTY_STATE=PASS`

## 5. Supabase security — latest recount

Ordinary public tables:
- total 47;
- RLS enabled 47;
- with policy 47;
- missing 0.

SECURITY DEFINER:
- total public SECURITY DEFINER functions: 51;
- PUBLIC execute: 0;
- anon execute: 0;
- authenticated execute: 0;
- fixed search_path missing: 0;
- service_role execute: 50.

Única função sem service_role execute:
`career_record_mail_delivery_receipt(...)` legado V1, ACL somente `postgres`, coerente com `legacy_receipt_v1=RETIRED`.

Security Advisor:
- somente WARN `auth_leaked_password_protection`;
- limitação conhecida de plano; não elevar a PASS_ZERO_LINTS.

Performance Advisor:
- apenas INFO `unused_index`;
- nenhum WARN estrutural.

Estado:
`RLS_PUBLIC_TABLES=PASS_47_OF_47_WITH_POLICY`
`SECURITY_DEFINER_ACL=PASS_51_ZERO_PUBLIC_ANON_AUTH_EXEC`
`SECURITY_ADVISOR=KNOWN_WARN_LEAKED_PASSWORD_PROTECTION_PLAN_LIMITATION`
`PERFORMANCE_ADVISOR=INFO_UNUSED_INDEXES_ONLY`

## 6. Role intelligence — runtime mais novo que o recovery antigo

Control plane atual:
- CBO `live_bulk`;
- ESCO `live_api`;
- O*NET `live_bulk`, version 31.0;
- LSI curated `live_bulk`;
- O*NET permanece `diagnostic_evidence_only` e `auto_promote_to_role_graph=false`.

Edge Function atual:
- `career-role-intelligence` V3 ACTIVE;
- SHA `54b68a6fbaf4d6e7831adcf7a42abd6871f18dab3b18a59cabf5a1e1012194da`;
- diagnostic RPC `career_role_pair_diagnostic_v3`;
- O*NET discovery via `career_onet_search`;
- evidência O*NET não auto-promove o graph.

Buscas de stale literals no `main` retornaram zero para:
- `PASS_ZERO_LINTS`;
- `v3.0-challenger`;
- `champion_engine`;
- `CBO_BULK_PENDING`;
- `bulk_pending`;
- `matching_champion`.

Estado:
`ROLE_INTELLIGENCE_V3_CHAMPION_ALIGNED=LIVE`
`ONET_V31_BULK=LIVE_DIAGNOSTIC_EVIDENCE_ONLY`

## 7. Mail/background — verdade preservada

Gmail conectado ao ChatGPT foi readback com sucesso. Isso prova a conexão do ChatGPT, não um OAuth/background connector nativo do Career.

Busca no repo por credenciais reutilizáveis não encontrou:
- `GMAIL_*`;
- `SMTP_*`;
- `GOOGLE_CLIENT*`.

Consentimentos permanecem inalterados e não autorizam draft/send automático.

Control plane:
- `mail_delivery` champion `none`;
- status `paused`;
- reason `MAIL_DELIVERY_CONNECTOR_NOT_LIVE`;
- blind retry false;
- receipt contract V2 obrigatório.

Estado:
`GMAIL_CHATGPT_CONNECTOR=CONNECTED_READ_PROVEN`
`CAREER_GMAIL_OAUTH=NOT_LIVE`
`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`
`MAIL_DELIVERY_CONTROL=PAUSED`
`MAIL_SEND_SIDE_EFFECTS=ZERO`

## 8. Edge runtime readback relevante

- `career-ui-state` V2 SHA `b80ea34e943f4f64500e931a80dd3407e0c2deeaf842edcbcf4e54eed782d66e`;
- `career-master-status` V4 SHA `68bfdfa931303f4a0f5d0504b4fa7408befb4e7ecf99f4d99c04f53a0d3fa4dd`;
- `career-agent` V3 SHA `0877ba595f53f680a2a926440aa0bfba59919460515501913cb1ae405eb36724`;
- `career-opportunity-research` V5 SHA `c77784d8d50d3b861c8b9c61ede2ee385ef053d1d79da06e1305a84ac2bcbc40`;
- `career-opportunity-refresh-now` V3 SHA `64713e5b6f7720f3535f71ac5e5566ca1095001f3978450e4cc608c0e32187d3`;
- `career-radar-status` V2 SHA `977254bf22c6881c0761fd9cf239955019d83fd5c2f817c2d49f05f0b2d3cef9`;
- `career-proactive-digest` V2 SHA `aa677838765e62fe683309fee53832a9b36cf0e8d0bd176a773e1eee8300e83f`;
- `career-role-intelligence` V3 SHA `54b68a6fbaf4d6e7831adcf7a42abd6871f18dab3b18a59cabf5a1e1012194da`;
- `career-role-search-plan` V3 SHA `ce4e569c4f6add7b4d9f7a341172b23a34f0b2407aa03676942549d17329b3cb`;
- `career-role-search-scope` V2 SHA `2d18c9d764ac6f1319f2f2d3734e68c5c0a745361a73cd1a4ce25591720a9acc`.

## 9. Estado final deste hardening

Controllable runtime hardening:
`BACKEND_CONTROL_PLANE_HARDENING_2026_09_07=PASS`

Alternative frontend delivery:
`CLOUDFLARE_V16_ALTERNATIVE_DELIVERY=PROVEN_BROWSER_VALIDATED_NOT_OFFICIAL`

Não declarar 100% de produto completo enquanto persistirem dependências externas reais:
1. hosted Supabase Auth Site URL / redirect allowlist continua sem rota de mutação in-app;
2. Career mail/background provider connector não está live;
3. application submission provider connector real não está live;
4. produção oficial ainda é Vercel V14;
5. authenticated Android E2E final do V16 ainda depende da escolha/promoção da rota oficial;
6. Public Beta permanece decisão explícita e não foi aberta.

Esses itens não anulam os PASS acima; são gates separados e devem permanecer visíveis.

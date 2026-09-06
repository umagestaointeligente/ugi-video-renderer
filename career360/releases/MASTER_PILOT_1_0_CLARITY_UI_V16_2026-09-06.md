# LSI CAREER 360 — MASTER PILOT 1.0 — CLARITY UI V16

Status: `BROWSER_VALIDATED_BUNDLE_PINNED_NOT_YET_PROMOTED`
Date: 2026-09-06 BRT

## Objective

Reduce cognitive load and make the Career 360 interface more pleasant and easier to operate without changing the canonical product logic.

Principle:

`LESS EXPLANATION ON THE SURFACE. MORE CLARITY IN THE NEXT ACTION.`

V16 is an incremental frontend layer over V15. It does not rebuild the product, replace V15, change matching, change privacy, or change backend contracts.

## Immutable frontend layer

File:
`career360/frontend/app-m.js`

Final immutable hardened pin:
`719c15ebfe89d212a19473b70ea6e615174601d9`

Canonical hardened bundle commit:
`f572b824b49b2cc73d5d8389eae98391bcca63a8`

Load order remains additive:
`... -> app-k -> app-l -> app-m`

Existing V15 pins are preserved:
- `app-k` -> `6df7b4e63d7e52ce3c3f02247392b98f0393cbe8`
- `app-l` -> `4283646143425e4a3156e44100aabb475df88d27`

## UX changes

### My Agent

The agent surface is changed from a text-heavy chat card to a compact decision-oriented surface:
- concise header;
- no synthetic real-time working badge;
- short opening message;
- compact composer;
- three quick read-only questions that delegate to the existing canonical agent handler:
  - `Melhores vagas`;
  - `Preciso agir?`;
  - `Próximo passo`.

No new application, email, or profile mutation capability is introduced by these buttons.

### Home / Radar / Opportunities

Repeated explanations are shortened.

Examples:
- `Você confirma. O agente cuida do resto.`
- `Dados confirmados por você.`
- `Seu agente pesquisa e filtra.`
- `Só o que passou pelos seus filtros.`
- `Radar automático — O agente encontra e avalia. Você revisa.`

### Proactive summary

The proactive card prioritizes outcome over operating detail:
- title becomes `Seu agente`;
- legacy `Agente trabalhando` text is not accepted as proof of current activity; the surface derives `Atualizando`, `Atualizado` or `Aguardando` from verifiable UI/digest state;
- cadence / last / next technical subline is removed from the primary visual surface;
- metrics stay visible;
- `Atualizar agora` becomes `Atualizar`;
- `Marcar como lido` becomes the compact action `Ok`, with accessible label preserved.

## Visual language

V16 introduces:
- softer page background;
- lighter card borders and shadows;
- cleaner radius hierarchy;
- reduced visual density;
- shorter secondary copy;
- improved chat bubble hierarchy;
- mobile horizontal quick-action chips;
- preserved mobile touch targets.

## Truthful status + secondary UX hardening

Before promotion, V16 received an additional truthfulness/accessibility pass:
- removed the fixed `Trabalhando` badge from the My Agent header;
- legacy V12 `Agente trabalhando` is treated as non-evidence; `Atualizando` appears only while update is in progress, `Atualizado` only when a digest exists, and `Aguardando` when no digest exists yet;
- onboarding headings and secondary copy were shortened without removing privacy, salary or confirmation guardrails;
- Support became `Ajuda`, with a shorter problem prompt and action;
- keyboard focus visibility was strengthened;
- `prefers-reduced-motion` is respected;
- agent question input has an explicit accessible label.
- static HTML and V16 runtime use the same truthful pre-login copy from first paint: `Você confirma o que importa. O Career 360 organiza sua busca.`

Policy:
`V16_TRUTHFUL_STATUS_POLICY=PASS`

## Mobile touch hardening

A final hardening pass detected that compact visual overrides could reduce some controls below the established V15 mobile target size.

Corrected before promotion:
- agent quick actions >= 44 px;
- proactive `Atualizar` >= 44 px;
- notification `Ok` >= 44 px;
- alert padding expanded so the larger action does not collide with text.

Permanent policy:
`V16_TOUCH_TARGET_POLICY=44PX`

Hardening source commit / immutable app-m pin:
`719c15ebfe89d212a19473b70ea6e615174601d9`

Hardened canonical bundle:
`f572b824b49b2cc73d5d8389eae98391bcca63a8`

## Browser validation

Permanent test:
`career360/tests/v16-clarity-smoke.mjs`

Permanent workflow:
`.github/workflows/career360-v16-clarity-smoke.yml`

Final hardened canonical-bundle + deploy-readiness validation:
- run `34010764428`
- job `101426061763`
- result `SUCCESS`

Evidence:
- `V16_CANONICAL_BUNDLE_PIN_GATE=PASS`
- `V16_TOUCH_TARGET_POLICY=44PX`
- `V16_TRUTHFUL_STATUS_POLICY=PASS`
- `V16_AUTH_TRUTHFUL_COPY_POLICY=PASS`
- `V16_STATIC_AUTH_TRUTH_SOURCE=PASS`
- `V16_LEGACY_AUTH_COPY_ABSENT=PASS`
- `V16_VERCEL_PROJECT_SCOPE_GATE=PASS`
- `V16_VERCEL_VALIDATE_ONLY_GATE=PASS`
- `V16_VERCEL_PREVIEW_TRUTH_SMOKE_POLICY=PASS`
- `V16_VERCEL_EXACT_PREVIEW_PROMOTION_POLICY=PASS`
- `CLARITY_360=PASS mutations=6`
- `CLARITY_412=PASS mutations=6`
- `CLARITY_768=PASS mutations=6`
- `CLARITY_1180=PASS mutations=6`
- `V16_AGENT_QUICK_ACTIONS=PASS`
- `V16_DYNAMIC_PROACTIVE_RECOMPACT=PASS`
- `V16_TRUTHFUL_RUNTIME_DERIVATION=PASS`
- `V16_AUTH_TRUTHFUL_COPY=PASS`

Earlier evidence retained for audit:
- static/runtime truth run `34010396657`, job `101425087473`, SUCCESS before deploy-readiness smoke was bound to the permanent V16 workflow;
- runtime-auth-copy run `34010192948`, job `101424535949`, SUCCESS before static-HTML hardening;
- previous runtime-truth final run `34009190125`, job `101421875198`, SUCCESS before auth-copy hardening;
- pre-bundle run `34006941241`, job `101415802373`, SUCCESS;
- first canonical-bundle run `34007073507`, job `101416159331`, SUCCESS before final 44px hardening;
- first test attempt `34006874557` failed only because the isolated harness kept the agent view hidden and therefore measured a zero-height send button. It did not mutate production.

## Safety / product boundaries

V16 does NOT:
- alter FIT or matching;
- use age, photo, or plan in matching;
- create a public profile;
- create applications;
- send email;
- claim a delivery that did not happen;
- open Beta;
- change backend schema or Edge Functions.

Quick actions remain read-oriented questions and call the existing canonical agent path.


### Deployment-readiness hardening

Permanent Vercel workflow:
`.github/workflows/career360-vercel-deploy.yml`

Current hardened workflow commit:
`bb344db78e61646926b0259c44552817149c861a`

The permanent V16 smoke now verifies that the deploy workflow is bound to the exact official Team/Project, supports a mutation-free `validate` target, rejects the legacy unverified auth copy, checks the truthful static copy in Preview/official alias, and promotes the exact tested Preview instead of creating a second production build.

This is deployment **readiness evidence only**. It is not evidence that a Preview or Production deployment occurred.

## Backend truthfulness alignment

The proactive backend was audited against the V16 truthfulness policy before UI promotion.

`career-proactive-digest` V2 is LIVE with a factual no-event state:
`Nenhuma novidade relevante foi registrada nesta janela.`

Evidence:
- canonical source commit `96cd4254eb972e8267e0bf3d39e37cf0da86f72c`;
- deployed Edge Function V2 `ACTIVE`;
- deployed SHA `aa677838765e62fe683309fee53832a9b36cf0e8d0bd176a773e1eee8300e83f`;
- legacy claim `seu agente continua ativo` absent from deployed source;
- cron-secret and authenticated-user authorization paths preserved.

`PROACTIVE_DIGEST_TRUTH_V2=LIVE`

This backend LIVE state does not promote the V16 frontend.

## Supabase security readiness read-only audit

Before promotion, the live project was audited without schema/data mutation:
- 43/43 ordinary public tables have RLS enabled and at least one policy;
- audited user-owned policies bind access to `auth.uid() = user_id`;
- public `SECURITY DEFINER` functions are not executable by PUBLIC, anon, or authenticated; service_role retains execution;
- no public views/materialized views were found;
- both Career 360 storage buckets are private and direct storage object access remains RLS-gated;
- audited unauthenticated-at-edge functions enforce internal secrets/session/master checks as appropriate, except the redirect-only app function;
- photo/media/document privileged paths were verified to scope ownership by authenticated user id.

Known limitations remain unchanged:
- leaked-password protection is disabled on the current plan;
- hosted Supabase Auth redirect allowlist is not exposed by the available connector and remains `NOT_YET_PROVEN`.

`SUPABASE_SECURITY_READINESS_READ_ONLY_AUDIT=PASS`

## Delivery and application evidence guards

The database was hardened before real mail/application connectors are enabled. Both target tables were empty at migration time, so no legacy state was rewritten.

Canonical migrations:
- `career360/migrations/20260906_delivery_receipt_guards_v16.sql` (`d21f7cfbca17e2fab2a274ff9f5f154361eb6e7b`);
- `career360/migrations/20260906_delivery_receipt_identity_v16.sql` (`900398868256dae12faba0df869bd265eb690a45`).

Fail-closed invariants now LIVE:
- mail `sent` requires outbound direction, `sent_at`, external thread reference, and separate provider-derived `delivery_receipt_hash`;
- delivery receipt identity cannot be reused for two mail actions by the same user;
- application `applied` requires `applied_at` and external application reference;
- external application receipt identity cannot be reused for two applications by the same user;
- both CHECK constraints are validated in the live catalog.

`career-mail-decision` still records user approval as `approved`, never `sent`, and explicitly reports that a delivery connector is required.

States:
`DELIVERY_EVIDENCE_GUARDS_V16=LIVE`
`MAIL_SENT_RECEIPT_GUARD_V16=LIVE`
`APPLICATION_APPLIED_RECEIPT_GUARD_V16=LIVE`
`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`

These guards are evidence contracts, not delivery receipts by themselves. No send/application is claimed without an external connector receipt.

## Mail provider receipt primitives

The external evidence contract was completed before activating a real product mail connector.

Canonical additions:
- external event receipt guards `9957b2bb2f3650b8062d2fef77f022bfedeb47cd`;
- service-only outbound delivery receipt RPC `9a2df7b0f55af3248b070941b3110c1862c8c43f`;
- service-only inbound/milestone RPCs `257ca4257b534a1792330773e31dc961d28579c4`;
- permanent rollback-safe smoke `01159c2d4dedf7678b3c946d5783b78453a8c25e`;
- provider contract `career360/docs/MAIL_PROVIDER_RECEIPT_CONTRACT_V16.md` (`51d351664d78f9112e435ff163e29ad99ad06c47`).

Live database primitives:
- outbound `sent` remains provider-receipt gated;
- inbound requires provider, received timestamp, thread hash and message hash;
- external application milestones require provider, event hash and observed timestamp;
- all receipt RPCs are service-only; raw provider identifiers are hashed before persistence.

A live transactional smoke returned 9/9 PASS and rolled back all test rows. Post-rollback application/mail row counts remained zero.

The Gmail connector inside ChatGPT is readable and its real sent-message shape exposes message id, thread id and timestamp, which is sufficient for the receipt mapping. This is not Career 360 product OAuth. Outlook Email was available in the plugin directory but not installed during this audit.

States:
`EXTERNAL_EVENT_RECEIPT_GUARDS_V16=LIVE`
`MAIL_RECEIPT_PRIMITIVES_V16=LIVE`
`APPLICATION_MILESTONE_RECEIPT_RPC_V16=LIVE`
`GMAIL_CHATGPT_CONNECTOR_READ=PROVEN`
`GMAIL_PROVIDER_RECEIPT_SHAPE=PROVEN`
`CAREER_GMAIL_OAUTH=NOT_LIVE`
`OUTLOOK_EMAIL_CONNECTOR=AVAILABLE_NOT_INSTALLED`
`CAREER_OUTLOOK_OAUTH=NOT_LIVE`
`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`

No actual email/application event is claimed from this infrastructure-only validation.

## Deployment state

`CLARITY_UI_V16=BROWSER_VALIDATED_BUNDLE_PINNED_NOT_YET_PROMOTED`

Do not mark `LIVE` until the official production frontend is proven to load:
- `app-k@6df7b4e...`
- `app-l@4283646...`
- `app-m@719c15e...`

and the authenticated mobile gate is completed.

`RUNTIME_COMPROVADO_VENCE_DOCUMENTO.`

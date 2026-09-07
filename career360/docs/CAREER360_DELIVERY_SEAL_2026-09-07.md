# LSI Career 360 — Master Pilot Delivery Seal — 2026-09-07

## Delivery decision

`DELIVERY_SCOPE=MASTER_PILOT_CONTROLLABLE_SCOPE`
`DELIVERY_STATE=SEALED`
`OFFICIAL_VERCEL_PRODUCTION=V14_STABLE`
`V16_CANONICAL_PACKAGE=BROWSER_VALIDATED_PINNED_NOT_OFFICIAL`
`PUBLIC_BETA=NOT_OPENED_PRODUCT_DECISION`

This seal means the Career 360 master-pilot architecture, backend contracts, canonical V16 frontend package, safety gates and recovery evidence are delivered for the controllable scope.

It does **not** represent external integrations as LIVE when they are not proven.

Core rule:
`RUNTIME_COMPROVADO_VENCE_DOCUMENTO`.

## Canonical repository

Repository: `umagestaointeligente/ugi-video-renderer`
Branch: `main`
Supabase project: `nxjdnzdxclszqyqrkwdk`
Official frontend: `https://lsi-career-360.vercel.app/`
Cloudflare validated preview: `https://career360-preview-20260906.umagestaointeligente.workers.dev`

## Canonical V16 application-confirmation bundle

Application confirmation UI source:
`career360/frontend/app-i.js`

Immutable source commit/pin:
`90a795bf1a371be66fd8f907c8a76501f8a5421c`

Canonical `main` bundle pin commit:
`82b49720bcf2e19e75cb44d19f64118c594e1508`

Other immutable V16 pins remain:
- `app-k.js` -> `6df7b4e63d7e52ce3c3f02247392b98f0393cbe8`
- `app-l.js` -> `4283646143425e4a3156e44100aabb475df88d27`
- `app-m.js` -> `719c15ebfe89d212a19473b70ea6e615174601d9`

Truthful pre-login copy:
`Você confirma o que importa. O Career 360 organiza sua busca.`

Application UI truth rule:
- confirmation does not mean sent;
- when global submit permission is false, UI says nothing was sent;
- `applied` remains receipt-gated.

## Final clean-tree Cloudflare evidence

Validation branch:
`career360-cloudflare-preview-20260906`

Clean branch head used by the final validation pair:
`c5ba5a76d8ccc675e30331d1b78bac6104c55313`

### Static preview deploy

Run: `34157515928`
Job: `101852301277`
Conclusion: `SUCCESS`

Passed stages:
- fail-closed credential and source gates;
- isolated Workers Static Assets deploy;
- live HTTP V16 pin and truth gate.

### Browser smoke

Run: `34157515919`
Job: `101852301179`
Conclusion: `SUCCESS`

Exact assertions from the final clean-tree log:
- `CLOUDFLARE_BROWSER_360=PASS`
- `CLOUDFLARE_BROWSER_412=PASS`
- `CLOUDFLARE_BROWSER_768=PASS`
- `CLOUDFLARE_BROWSER_1180=PASS`
- `CLOUDFLARE_APPLICATION_CONFIRMATION_UI=PASS`
- `CLOUDFLARE_APPLICATION_CONFIRMATION_TRUTHFUL_NO_FALSE_SEND=PASS`
- `CLOUDFLARE_V16_BROWSER_PRELOGIN=PASS`
- `CLOUDFLARE_V16_RESPONSIVE=PASS`
- `CLOUDFLARE_V16_RUNTIME_ERRORS=ZERO`
- `CLOUDFLARE_V16_PRODUCTION_MUTATION=NONE`

The application confirmation smoke validates the UI sequence `Confirmar candidatura -> truthful no-send state -> Revogar confirmação` against a synthetic backend contract. It is not a claim of a real ATS submission.

## Supabase runtime readback

### Confirmable application status API

`career-proactive-status`
- version: V2
- status: ACTIVE
- verify_jwt: true
- SHA-256: `49908165f6eb2fa44afa7bcb4515830e0eaade03339f05aff8f2f033924865dd`

It exposes only user-scoped confirmable application state and current permission truth, including `confirmable_applications`, `application_permissions` and `dispatch_eligible`.

### Per-application confirmation mediator

`career-application-confirm`
- version: V2
- status: ACTIVE
- verify_jwt: true
- SHA-256: `85ce6535ae020696c741d3960979b22ab9e3756a683a17c754a487b089792f44`

It confirms/revokes only after validating the authenticated user and calls the atomic service-only confirmation RPC. It has no provider side effect.

### Submission dispatch contract

`APPLICATION_SUBMISSION_DISPATCH_V2=LIVE_SERVICE_ONLY_CLAIM_BOUND`
`APPLICATION_SUBMISSION_RECEIPT_V2=LIVE_SERVICE_ONLY_CLAIM_BOUND`
`APPLICATION_SUBMISSION_RECEIPT_V1=RETIRED_SERVICE_EXEC_REVOKED`
`BLIND_RETRY_ALLOWED=false`

Previous permanent transactional smokes proved:
- permission OFF -> zero claims;
- permission ON + explicit per-application confirmation -> one claim;
- correct receipt -> `applied`;
- receipt replay -> idempotent;
- wrong claim token -> rejected;
- transaction rollback restores pilot state.

Latest preserved pilot state before this UI-only delivery work:
- applications = 0
- followups = 0
- mail actions = 0
- `allow_application_submit=false`

No application/provider/mail side effects were executed during this delivery seal.

## Security state

Latest post-DDL readback:
- public ordinary tables: `47/47 RLS + policy`;
- public SECURITY DEFINER functions: `55`;
- PUBLIC execute: `0`;
- anon execute: `0`;
- authenticated execute: `0`;
- fixed search_path: `55/55`.

Security Advisor:
- only known `auth_leaked_password_protection` WARN remains, associated with hosted Auth plan/configuration.

Performance Advisor:
- INFO unused indexes only.

## Official Vercel production truth

Vercel project:
`prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP`

Team:
`team_ZJys00FTE2kK9yVtsqH5fHyF`

Latest production deployment returned by the project-scoped read action:
`dpl_98eN1wuVyk4wQmnYpG2jjsZ1ZazU`

State:
- `READY`
- target `production`

A direct in-chat fetch of `https://lsi-career-360.vercel.app/` returned HTTP 200 and still exposed the V14 bundle, including:
- old `app-i@0a2ea38883094ccf9be4c5fde9ea4efa14617b65`;
- old `app-k@ac1ea580667724b49ee1e8b0c8e04dfc153565f3`;
- no V15/V16 app-l/app-m bundle;
- old pre-login slogan.

Therefore:
`V16_OFFICIAL_PRODUCTION_PROMOTION=NONE`

The in-chat Vercel connector was rediscovered on this delivery pass. Its deploy mutation remains:
`deploy_to_vercel()`
with zero project/team arguments.

Because the account has multiple projects, an unscoped mutation is not an acceptable production route.

State:
`VERCEL_PROJECT_SCOPED_MUTATION=NOT_AVAILABLE_IN_CHAT`

No external Vercel auth, manual token, device flow, Make bridge, ProductOS route or Remote Desktop workaround is permitted.

## External integrations intentionally not represented as LIVE

### ATS provider submission

`APPLICATION_PROVIDER_CONNECTOR=NOT_LIVE`

Quickin Make scenario `6090823`:
- inactive;
- explicit `confirm_submit` gate;
- historical result `SUBMIT_UNCONFIRMED`;
- `submitted=false`.

Generic HTTP submit scenario `6075235`:
- retired;
- no provider-specific auth;
- no verified application receipt.

### Background mail

`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`
`CAREER_GMAIL_OAUTH=NOT_LIVE`
`CAREER_OUTLOOK_OAUTH=NOT_LIVE`

Make private and standard spaces were audited and exposed no existing Gmail, SMTP/IMAP, Microsoft mail, Supabase, Supabase Management or PostgreSQL connection that could be safely reused for Career background delivery.

ChatGPT Gmail access is an in-chat action surface and is not equivalent to Career product background OAuth.

### Hosted Auth redirect configuration

`SUPABASE_SERVER_REDIRECT_ALLOWLIST=NOT_YET_PROVEN_OR_MUTABLE_IN_APP`

The known localhost redirect remains a hosted configuration UX issue; it is not represented as repaired.

## Product delivery state

Delivered/sealed now:
- privacy and multi-user isolation foundation;
- safe file/CV/profile flows;
- champion matching V3.1 with V2 rollback;
- role intelligence/search plan;
- automated opportunity research pilot;
- proactive agent/digest;
- visual profile and local professional photo flow;
- application evidence/receipt guards;
- follow-up scheduler without delivery side effects;
- claim-bound application dispatch infrastructure;
- JWT-authenticated per-application confirmation mediator;
- confirmable-application status API;
- V16 confirmation UI with truthful no-send behavior;
- canonical immutable bundle pins;
- Cloudflare static/browser delivery proof;
- canonical recovery and rollback evidence.

Not falsely marked delivered as production integration:
- V16 on official Vercel URL;
- background Gmail/Outlook transport;
- real ATS submission provider connector;
- hosted Supabase Auth redirect admin repair;
- public Beta opening;
- real authenticated Android V16 end-to-end after production promotion.

## Final rule

The Career 360 Master Pilot is delivered for the scope that can be proven and controlled from the current architecture.

External dependencies remain fail-closed until a real, admissible route exists and produces live evidence.

`CONFIRMED != SENT`
`APPROVED != APPLIED`
`PREVIEW_VALIDATED != OFFICIAL_PRODUCTION`

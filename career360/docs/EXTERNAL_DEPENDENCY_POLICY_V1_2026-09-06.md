# Career 360 — External Dependency Policy V1

Date: 2026-09-06 BRT
Status: CANONICAL

## Absolute rule

`IN_APP_AUTONOMOUS_ONLY`

A provider is an admissible Career 360 route only when the complete operational path can be executed from inside ChatGPT/app without requiring Paulo to open an external provider, authenticate externally, provision a token, configure a dashboard, link a repository, approve OAuth on another site, or perform provider-side maintenance.

If a route requires external user intervention, it is not `PENDING`; it is `PROHIBITED_EXTERNAL_USER_DEPENDENCY` for Career 360 and must not be proposed as the next operational step.

## Make

Allowed only if an already-authorized in-app Make connection exists and ChatGPT can create, inspect, activate, run, and debug the required scenario without external user action.

Current evidence:
- private space Gmail connection: none;
- private space Supabase connection: none;
- standard team Gmail connection: none;
- standard team Supabase connection: none;
- creating those connections requires external OAuth.

Current state:
`MAKE_CAREER360_ROUTE=REJECTED_AS_CURRENT_PRODUCTION_ROUTE`

The previously opened Make credential request is obsolete for Career 360 and must not be presented to the user as a required step.

## Vercel

Allowed only when an in-app action is project-scoped and deterministically targets:
- team `team_ZJys00FTE2kK9yVtsqH5fHyF`;
- project `prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP`.

Current in-app deploy action exposes no projectId/teamId parameters and therefore is not admissible for mutation in a multi-project environment.

External Git-link setup, dashboard configuration, VERCEL_TOKEN provisioning, browser/device login, and external Vercel authorization are prohibited routes.

Current state:
`VERCEL_CAREER360_MUTATION_ROUTE=REJECTED_UNTIL_IN_APP_PROJECT_SCOPED_ACTION_EXISTS_AND_IS_PROVEN`

Existing Vercel production remains read-only infrastructure and must not be mutated by an unscoped action.

## Supabase Auth redirect

The redirect bug is proven: a disposable signup requesting the Career 360 official callback was rewritten to `http://localhost:3000`.

Manual Dashboard repair is not an admissible next step because it requires external user intervention.

Repair must use an in-app Supabase/admin capability or another internal route that can deterministically change only the required Auth URL configuration and preserve all other settings.

Current state:
`AUTH_REDIRECT_CONFIG=WRONG_LOCALHOST_PROVEN`
`AUTH_REDIRECT_REPAIR=PAUSED_WAITING_IN_APP_ADMIN_ROUTE`

## Mail

Canonical mailbox for incubation remains:
`umagestaointeligente@gmail.com`

ChatGPT Gmail connector is valid for explicit in-chat read/write actions because it is already connected inside the app.

Background mail transport is not declared live until a fully in-app autonomous route exists.

Current state:
`GMAIL_CHATGPT_CONNECTOR_READ_WRITE=PROVEN_FOR_IN_CHAT_ACTIONS`
`MAIL_BACKGROUND_BRIDGE=NOT_LIVE`
`MAIL_DELIVERY=PAUSED`

Backend dispatch/receipt hardening remains valid and reusable once a compliant transport exists.

## Diagnostic rule

For every external capability:
1. Read `career_engine_control`.
2. Check `route_admissibility_rule`.
3. Reject any route requiring external user intervention.
4. Use only a deterministic in-app action with explicit scope.
5. Require live evidence before changing status to ACTIVE/LIVE.
6. Never convert an unavailable provider route into a manual task for Paulo.

`RUNTIME_COMPROVADO_VENCE_DOCUMENTO`.

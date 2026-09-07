# Career 360 — Application Confirmation V2 — LIVE — 2026-09-07

## State

`APPLICATION_CONFIRMATION_EDGE_V2=ACTIVE_JWT_REQUIRED`
`APPLICATION_CONFIRMATION_ATOMIC_RPC_V2=LIVE_SERVICE_ONLY`
`APPLICATION_CONFIRMATION_PROVIDER_SIDE_EFFECTS=NONE`
`APPLICATION_CONFIRMATION_AUTHENTICATED_E2E=PENDING_REAL_FRONTEND_SESSION`

## Purpose

Complete the principle:

`O CLIENTE NÃO PREENCHE. O CLIENTE CONFIRMA.`

The application submission dispatch already required `submission_confirmed_at`, but there was no client-safe mediator to record or revoke that confirmation without granting direct UPDATE privileges on `career_applications`.

V2 adds the mediator without weakening database ACLs.

## Edge mediator

Function:
`career-application-confirm`

Runtime:
- version `2`
- status `ACTIVE`
- `verify_jwt=true`
- SHA-256 `85ce6535ae020696c741d3960979b22ab9e3756a683a17c754a487b089792f44`

Canonical source:
`career360/edge-functions/career-application-confirm/index.ts`

Source commit for atomic V2:
`6d6f4a7a15ba6af101b8036270b03a1349d6e203`

The Edge Function:
1. accepts only POST/OPTIONS;
2. requires Bearer authentication;
3. validates the session with `auth.getUser()`;
4. never accepts a `user_id` from the client;
5. validates `application_id` and boolean `confirmed`;
6. calls only the service-only atomic RPC using the authenticated user's id;
7. never contacts a provider, Make, ATS, recruiter, or mailbox;
8. cannot mark an application as `applied`.

## Atomic database contract

Migration:
`career360/migrations/20260907_application_confirmation_atomic_v2.sql`

Canonical commit:
`c6a0fa46583003f928156c019a37767a832c25d2`

RPC:
`career_set_application_submission_confirmation(uuid, uuid, boolean)`

ACL:
- service_role EXECUTE = true
- authenticated EXECUTE = false
- anon EXECUTE = false
- PUBLIC EXECUTE = false

The RPC runs confirmation state mutation and audit insertion in one database transaction.

Confirmation is allowed only when:
- application belongs to the authenticated user passed by the trusted Edge mediator;
- status is `draft_ready` or `awaiting_user`;
- application is not already applied;
- no external receipt exists;
- dispatch state is still `idle`;
- no submission attempt has begun.

Confirm:
- status -> `awaiting_user`
- `submission_confirmed_at` -> current timestamp
- audit event -> `application_submission_confirmed`

Revoke:
- status -> `draft_ready`
- `submission_confirmed_at` -> NULL
- audit event -> `application_submission_confirmation_revoked`

Once a dispatch claim/attempt exists, confirmation cannot be changed through this contract.

## Global permission preserved

Per-application confirmation does not change:
`career_action_permissions.allow_application_submit`

Current pilot value remains:
`false`

The function returns both:
- `global_submit_permission`
- `dispatch_eligible`

Therefore a user may have a confirmed intent while dispatch still remains impossible because the global product permission is disabled.

## Permanent smoke

File:
`career360/tests/application-confirmation-atomic-v2-smoke.sql`

Commit:
`92f86f03716c79bc6507997580ec25088b4f2bc5`

Live transactional smoke passed and rolled back.

Proved:
- `draft_ready -> awaiting_user` on confirmation;
- `submission_confirmed_at` is written;
- current global permission false is preserved;
- `dispatch_eligible=false` while global permission is false;
- revoke returns to `draft_ready` and clears timestamp;
- exactly two audit events for confirm + revoke;
- confirmation after a synthetic claim is rejected with `APPLICATION_SUBMISSION_ATTEMPT_ALREADY_STARTED`;
- all synthetic records were rolled back.

## Security readback

After the atomic RPC migration:
- ordinary public tables RLS + policy: `47/47`;
- public SECURITY DEFINER functions: `55`;
- PUBLIC EXECUTE: `0`;
- anon EXECUTE: `0`;
- authenticated EXECUTE: `0`;
- fixed search_path: `55/55`.

Security Advisor still reports only the known leaked-password-protection warning.

## External runtime limitation

An authenticated browser E2E for this new Edge Function was not executed because no real frontend user session token is available to the current server-side tool session.

This is recorded as:
`PENDING_REAL_FRONTEND_SESSION`

This does NOT downgrade the deployed server contract, but the UI path must not be marked browser-E2E validated until a real authenticated frontend session exercises it.

## Make connection audit

Both Make spaces were checked for existing reusable connections.

Private space `2782728`:
- Supabase = none
- Supabase Management = none
- PostgreSQL = none
- Gmail = none
- SMTP/IMAP = none
- Microsoft mail = none

Standard team `2782727`:
- Supabase = none
- Supabase Management = none
- PostgreSQL = none
- Gmail = none
- SMTP/IMAP = none

No OAuth request, new secret, management token, or user intervention was introduced.

## Final boundary

Application intent/confirmation infrastructure is now internally complete through the dispatch boundary.

Actual external submission remains:
`APPLICATION_PROVIDER_CONNECTOR=NOT_LIVE`

No application was submitted during this hardening.

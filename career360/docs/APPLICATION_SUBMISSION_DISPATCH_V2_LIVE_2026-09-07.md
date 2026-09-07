# Career 360 — Application Submission Dispatch V2 — LIVE — 2026-09-07

## Runtime truth

`APPLICATION_SUBMISSION_RECEIPT_V2=LIVE_SERVICE_ONLY`
`APPLICATION_SUBMISSION_DISPATCH_V2=LIVE_NO_PROVIDER_SIDE_EFFECTS`
`APPLICATION_PROVIDER_CONNECTOR=NOT_LIVE`
`ALLOW_APPLICATION_SUBMIT_CURRENT=false`
`BLIND_RETRY_ALLOWED=false`

## Why V2 exists

V1 required an external provider reference before an application could become `applied`, but the receipt RPC was not bound to a specific authorized dispatch attempt.

V2 adds a claim-bound dispatch contract:

`career_claim_application_submission -> provider adapter -> career_record_application_submission_receipt_v2`

A provider receipt can change an application to `applied` only when it is bound to the claim token for that specific application attempt.

## Canonical database changes

Migration:
`career360/migrations/20260907_application_submission_dispatch_v2.sql`

New typed fields on `career_applications`:
- `submission_confirmed_at`
- `submission_dispatch_state`
- `submission_claim_token_hash`
- `submission_claimed_at`
- `submission_claim_expires_at`
- `submission_attempt_count`
- `submission_last_error_safe`
- `submission_route`

Dispatch states:
- `idle`
- `claimed`
- `uncertain`
- `blocked`
- `receipt_confirmed`

Service-only functions:
- `career_claim_application_submission(integer, integer)`
- `career_mark_application_submission_uncertain(uuid, text, text)`
- `career_record_application_submission_receipt_v2(uuid, uuid, text, text, text, timestamptz, timestamptz)`

Legacy V1 receipt:
`career_record_application_submission_receipt(...)`

State:
`RETIRED_SERVICE_EXEC_REVOKED`

The V1 function remains callable only by `postgres` for rollback/forensics and is no longer executable by `service_role`.

## Claim gate

A row can be claimed only when all of these are true:
1. `status='awaiting_user'`;
2. `submission_confirmed_at is not null`;
3. `submission_dispatch_state='idle'`;
4. `submission_attempt_count=0`;
5. `applied_at is null`;
6. no external application receipt already exists;
7. URL is currently a Quickin URL (`https://jobs.quickin.io/%`);
8. `career_action_permissions.allow_application_submit=true`.

The current pilot permission remains `false`, therefore the live production claim count is zero.

## No blind retry

Each application is claimable only while `submission_attempt_count=0`.

An uncertain provider outcome is persisted as `submission_dispatch_state='uncertain'` and is not automatically retried. Manual or future canonical recovery must resolve it first.

## Permanent smoke

File:
`career360/tests/application-submission-dispatch-v2-smoke.sql`

Live transactional execution on 2026-09-07 passed and rolled back.

Proved:
- permission OFF -> zero claims;
- permission ON + explicit confirmation -> exactly one claim;
- correct claim + external receipt -> `applied`;
- replay of the same verified receipt -> idempotent;
- wrong claim token -> `APPLICATION_SUBMISSION_CLAIM_MISMATCH`;
- transaction rollback restored the pilot state.

Post-smoke readback:
- `career_applications=0`
- `career_followups=0`
- `career_mail_actions=0`
- `allow_application_submit=false`

## Security readback after migration

Public ordinary tables:
`47/47 RLS + policy`

Public SECURITY DEFINER functions:
`55`

ACL/readback:
- PUBLIC execute = 0
- anon execute = 0
- authenticated execute = 0
- fixed `search_path` = 55/55

Application submission functions:
- V1 receipt: service role execute = false
- V2 claim: service role execute = true
- V2 uncertain: service role execute = true
- V2 receipt: service role execute = true

Security Advisor:
- only known `auth_leaked_password_protection` WARN remains.

Performance Advisor:
- INFO unused indexes only.

## Make / provider audit

### Quickin
Scenario:
`6090823 — LOLA Recruiter V4 — Quickin Secure Submit`

Runtime:
- status `inactive`;
- Custom JS/Puppeteer connection status `ok`;
- explicit per-application `confirm_submit` input added;
- Puppeteer module is filtered by `confirm_submit=true`;
- no execution was triggered during this hardening.

Historical execution evidence:
- scenario execution succeeded technically;
- final provider state was `SUBMIT_UNCONFIRMED`;
- `submitted=false`;
- therefore it is NOT a valid provider receipt and NOT a real application submission proof.

State:
`QUICKIN_CONNECTOR=INACTIVE_HARD_GATED_NOT_LIVE`

### Generic HTTP submit
Former scenario:
`6075235 — LOLA ATS — Direct HTTP Submit Template`

Audit:
- no authentication;
- no provider-specific contract;
- no executions;
- HTTP status/body alone is not an application receipt.

It was renamed to:
`RETIRED — LOLA ATS — Direct HTTP Submit Template — NO RECEIPT`

State:
`DIRECT_HTTP_SUBMIT=RETIRED`

## Mail transport audit

Make module discovery found no pre-existing connection for:
- Gmail send/draft/search/watch;
- generic SMTP/IMAP send/read/watch;
- Microsoft 365 mail draft/search/watch.

All returned `existing=[]`.

Therefore:
`CAREER_MAIL_DELIVERY=NOT_LIVE`

No OAuth request was created and no external authorization was requested.

## Product rule preserved

`O CLIENTE NÃO PREENCHE. O CLIENTE CONFIRMA.`

The product may prepare a future application, but actual provider dispatch must remain behind:
- global `allow_application_submit` permission;
- per-application confirmation;
- claim lease;
- provider receipt;
- receipt V2 verification.

No provider side effect is LIVE as of this seal.


## Per-application confirmation mediator V2

The dispatch contract is now paired with an authenticated confirmation mediator.

Canonical document:
`career360/docs/APPLICATION_CONFIRMATION_V2_LIVE_2026-09-07.md`

Runtime:
- `career-application-confirm` V2 ACTIVE;
- `verify_jwt=true`;
- SHA-256 `85ce6535ae020696c741d3960979b22ab9e3756a683a17c754a487b089792f44`;
- atomic service-only RPC `career_set_application_submission_confirmation`;
- current global `allow_application_submit=false`;
- provider side effects remain NONE;
- authenticated frontend E2E remains pending a real user session.

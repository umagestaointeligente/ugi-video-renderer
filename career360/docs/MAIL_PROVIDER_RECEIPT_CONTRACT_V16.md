# Career 360 — Mail Provider Receipt Contract V16

Status: CANONICAL / PRE-CONNECTOR CONTRACT
Date: 2026-09-06

## Principle

`APPROVAL_IS_NOT_DELIVERY`
`DRAFT_IS_NOT_SENT`
`DETECTED_IS_NOT_RECEIVED_WITHOUT_PROVIDER_EVIDENCE`
`APPLICATION_PREPARED_IS_NOT_APPLIED`
`EXTERNAL_MILESTONE_IS_NOT_FACT_WITHOUT_PROVIDER_EVIDENCE`

The Career 360 database is fail-closed. Provider integrations may propose or approve actions, but externally asserted states are persisted only after provider-backed receipts are supplied to service-only RPCs.

## Gmail evidence shape proven inside ChatGPT

The connected Gmail connector is readable inside ChatGPT and a real SENT message exposes:
- provider message `id`;
- `thread_id`;
- message timestamp.

This proves the provider has the identifiers required by the database receipt contract.

It does **not** prove that the Career 360 application has its own Gmail OAuth or background connector.

State:
`GMAIL_CHATGPT_CONNECTOR_READ=PROVEN`
`GMAIL_PROVIDER_RECEIPT_SHAPE=PROVEN`
`CAREER_GMAIL_OAUTH=NOT_LIVE`
`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`

## Outlook state

An `Outlook Email` connector exists in the ChatGPT plugin directory but was not installed/connected at the time of this contract.

State:
`OUTLOOK_EMAIL_CONNECTOR=AVAILABLE_NOT_INSTALLED`
`CAREER_OUTLOOK_OAUTH=NOT_LIVE`

## Outbound delivery mapping

Provider-success fields map to the service-only RPC:

`career_record_mail_delivery_receipt(user_id, mail_action_id, provider, message_ref, thread_ref, sent_at)`

Mapping:
- provider name -> normalized `mail_provider`;
- provider message id -> transient `message_ref` -> SHA-256 -> `delivery_receipt_hash`;
- provider thread id -> transient `thread_ref` -> SHA-256 -> `external_thread_ref_hash`;
- provider timestamp -> `sent_at`.

Raw provider IDs are not persisted by the RPC.

The RPC is:
- `SECURITY DEFINER`;
- fixed `search_path=public,extensions`;
- executable by `service_role` only;
- idempotent for the same provider receipt;
- allowed to transition only `approved -> sent`;
- fail-closed for missing/incomplete receipts.

## Inbound mapping

Provider inbound evidence maps to:

`career_record_inbound_mail_event(...)`

Required external facts:
- provider;
- provider message id;
- provider thread id;
- received timestamp.

Both external identifiers are hashed server-side. Duplicate provider message IDs for the same user resolve idempotently.

Direct `direction='inbound'` persistence is also constrained at table level and requires:
- `received_at`;
- `mail_provider`;
- `external_thread_ref_hash`;
- `external_message_ref_hash`.

## Application external milestones

Externally asserted states are recorded through:

`career_record_application_milestone(user_id, application_id, status, provider, event_ref, observed_at)`

Protected states:
- `recruiter_reply`;
- `interview_pending`;
- `interview_confirmed`;
- `finalist`;
- `offer`;
- `hired`;
- `rejected`;
- `closed`.

For those states the table requires:
- normalized external provider;
- SHA-256 external event reference;
- external observation timestamp.

`applied` remains separately protected by `applied_at + external_application_ref_hash`.

## Permanent smoke

`career360/tests/v16-receipt-contract-smoke.sql`

The smoke runs in a transaction and rolls back all test data. Live validation on 2026-09-06 returned 9/9 PASS:
- outbound first receipt;
- outbound idempotent replay;
- inbound first receipt;
- inbound idempotent replay;
- application milestone first receipt;
- application milestone idempotent replay;
- inbound without provider identifiers rejected;
- sent without delivery receipt rejected;
- external milestone without receipt rejected.

Post-rollback live counts remained:
`career_applications=0`
`career_mail_actions=0`

## Canonical migrations

- `career360/migrations/20260906_delivery_receipt_guards_v16.sql`
- `career360/migrations/20260906_delivery_receipt_identity_v16.sql`
- `career360/migrations/20260906_external_event_receipt_guards_v16.sql`
- `career360/migrations/20260906_mail_delivery_receipt_rpc_v16.sql`
- `career360/migrations/20260906_external_event_receipt_rpcs_v16.sql`

## Current state

`DELIVERY_EVIDENCE_GUARDS_V16=LIVE`
`EXTERNAL_EVENT_RECEIPT_GUARDS_V16=LIVE`
`MAIL_RECEIPT_PRIMITIVES_V16=LIVE`
`APPLICATION_MILESTONE_RECEIPT_RPC_V16=LIVE`
`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`

These LIVE states describe database evidence contracts and service-only primitives, not a live Gmail/Outlook product integration and not proof that any new email or application was sent.
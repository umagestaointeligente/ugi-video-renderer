# UGI — Buffer Exactly-Once Publication Guard

Date: 2026-08-24
Status: ACTIVE / RUNTIME VERIFIED
Scope: UGI only
Repository: `umagestaointeligente/ugi-video-renderer`
Worker: `lola-operacional-ugi`

## Incident
A scheduled Instagram slot produced multiple visually duplicate publications although content-generation anti-duplication had passed. The incident showed that creative anti-duplication is not sufficient to guarantee exactly-once delivery at the publication boundary.

The publication plane therefore requires independent idempotency at the Worker/Buffer boundary.

## Provider lock
- Publication and scheduling provider: **BUFFER ONLY**.
- Metricool: **ANALYTICS ONLY**.
- `METRICOOL_PUBLICATION_ALLOWED=false`.
- No fallback to Metricool is allowed when Buffer is degraded.

## Runtime guard
Worker version verified after deployment:
`lola-v8-r44-5-22-publication-idempotency-2026-08-24`

Health readback requires all of the following:
- `publicationExactlyOnceGuard=true`
- `publicationAssetLockR2=true`
- `publicationSlotLockR2=true`
- `publicationRetryCreateBlockedOnUncertain=true`
- `MEDIA_R2=true`
- `BUFFER_API_KEY=true`

### Asset lock
A durable R2 lock is created before any Buffer mutation for the logical content identity + platform. A repeated attempt to publish the same content on the same platform must fail closed before calling Buffer.

### Slot lock
A second durable R2 lock is created before any Buffer mutation for platform + publication mode + exact scheduled time. This prevents different drafts/processes from occupying the same UGI platform/time slot.

### Uncertain-result rule
If Buffer creation times out or returns an uncertain error, the lock is **not released automatically**. State becomes `uncertain`; subsequent automation must reconcile/read back instead of issuing another create request. This prevents a lost response from becoming a duplicate post.

### Existing publications
`POST /api/publication-lock-backfill` creates lock records only for an already-existing active Buffer publication. It does not create a social post.

`GET /api/publication-lock-status` provides independent lock readback without publication mutation.

## Maintenance workflow isolation
`.github/workflows/ugi-buffer-live-readback.yml` is a mutating scheduling workflow and must be explicit-dispatch only. Pull requests, source pushes, watchdogs, diagnostics and maintenance activity must never trigger Buffer scheduling.

Read-only maintenance/observability is handled separately.

## Evidence
Verified recovery run:
- GitHub Actions run: `32729227645`
- Result: success
- Artifact: `ugi-idempotency-recovery-32729227645`
- Artifact readback: `ready=true`
- `public_publish_triggered=false`
- `payment_triggered=false`

Existing lock backfill evidence:
- Fast backfill run: `32729571568`
- Result: success
- `buffer_create_called=false`
- `all_active_scheduled_locked=true`

Remaining scheduled second-peak slots protected by explicit Buffer-ID readback:
- Instagram 24/08 19:00 BRT — Buffer post `6a8b91a17b646aa28b02239c`
- YouTube 24/08 20:30 BRT — Buffer post `6a8b91b753c54dc08763b279`
- Protection run: `32729686335`
- Result: success
- Both asset and slot lock states: `backfilled_confirmed`
- No Buffer create was called by the protection run.

## Operational rule
`GENERATED != SCHEDULED != PUBLISHED != VERIFIED`.

A retry is not permission to create again. Before any publication create, exactly-once locks must be acquired. After any uncertain response, only reconciliation/readback is allowed until the state is resolved.

Do not store secrets in this document.

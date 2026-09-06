# Career 360 — O*NET 31.0 Runtime Integration

Status: `LIVE_BULK_EVIDENCE_ONLY`
Date: 2026-09-06 BRT

## Runtime truth

`ONET_31_LOOKUP_LAYER=LIVE`
`ONET_31_BULK_SYNC=LIVE`
`ONET_SOURCE_STATUS=live_bulk`
`ONET_SOURCE_VERSION=31.0`
`ONET_ROLE_GRAPH_AUTO_PROMOTION=DISABLED`
`ONET_MATCHING_MUTATION=NONE`
`ONET_MATCHING_REGRESSION=57_OF_57_CLASS_AND_SCORE_STABLE`
`ONET_RUNTIME_SMOKE=PASS`
`SUPABASE_PUBLIC_TABLE_RLS=47_OF_47`

O*NET is an external taxonomy evidence layer. It does not automatically create curated Role Graph concepts or aliases and does not directly alter FIT/matching.

## Source and normalized counts

Pinned official bulk endpoints:
- `https://www.onetcenter.org/dl_files/database/db_31_0_json/occupation_data.json`
- `https://www.onetcenter.org/dl_files/database/db_31_0_json/job_titles.json`

Live validated counts:
- raw occupations: 1,016
- persisted occupations: 1,016
- raw job-title rows: 54,269
- persisted unique normalized job titles: 54,229
- source duplicates after `(onetsoc_code, normalized_job_title)` normalization: 40

The first raw title load failed closed on normalization duplicates. No partial load was accepted. The normalized load deduplicates deterministically.

## Database objects

Tables:
- `public.career_onet_occupations`
- `public.career_onet_job_titles`
- `public.career_onet_sync_state`

All three have RLS enabled. Client roles are explicitly denied. Direct table access is reserved for `service_role`/database administration.

Service-only RPCs:
- `career_onet_search(text,integer)`
- `career_onet_begin_sync(text)`
- `career_onet_finalize_sync()`

ACL readback for all three RPCs:
- anon: false
- authenticated: false
- PUBLIC: false
- service_role: true

## Reproducible sync

Canonical migration:
`career360/migrations/20260906_onet31_reproducible_sync_v1.sql`

Design:
1. `career_onet_begin_sync('31.0')` submits the two pinned official JSON downloads through `pg_net`.
2. `career_onet_sync_state` records the exact request IDs and enters `requested`.
3. `career_onet_finalize_sync()` returns `RESPONSES_NOT_READY` without mutation while either response is unavailable.
4. Both payloads must return HTTP 200 and pass minimum-row and referential-integrity checks.
5. Replacement of normalized O*NET tables occurs inside an exception subtransaction.
6. Persisted row counts must reconcile with source rows / deterministic normalization.
7. Only after all gates pass is `career_role_taxonomy_sources.onet` changed to `live_bulk`.
8. A second finalizer call after success is an idempotent no-op.

Live end-to-end sync proof:
- occupation request id: `230`, HTTP 200
- job-title request id: `231`, HTTP 200
- first finalize: `RESPONSES_NOT_READY`, processed=false
- final result: `succeeded`
- raw occupations: 1,016
- persisted occupations: 1,016
- raw job-title rows: 54,269
- persisted titles: 54,229
- normalized duplicate rows: 40
- `error_safe=null`

Cron:
- job `6` — `career-onet-monthly-refresh` — `17 3 10 * *` — active
- job `7` — `career-onet-sync-finalizer` — `*/10 * * * *` — active

The monthly job refreshes the pinned production version `31.0`; version promotion remains an explicit code/config decision rather than silently ingesting an unknown future taxonomy version.

## Lookup semantics

Permanent smoke:
`career360/tests/onet31-runtime-smoke.sql`

Live result:
`ONET31_RUNTIME_SMOKE=PASS`

Example readback for `category manager`:
- exact `Category Manager` under O*NET-SOC `11-2021.00` / `Marketing Managers`, score 1.000
- related `Category Purchasing Manager` under `11-3061.00` / `Purchasing Managers`

The ambiguity of terms such as `Commercial Manager` is intentionally preserved as evidence rather than silently converted to canonical Career 360 aliases.

## Role Intelligence integration

Canonical source:
`career360/edge-functions/career-role-intelligence/index.ts`

Supabase runtime:
- function: `career-role-intelligence`
- version: `3`
- status: `ACTIVE`
- `verify_jwt=true`
- deployed SHA256: `54b68a6fbaf4d6e7831adcf7a42abd6871f18dab3b18a59cabf5a1e1012194da`

New action:
`discover_onet`

It:
- requires authenticated user context at the Edge boundary;
- calls the service-only O*NET lookup RPC;
- returns evidence-only candidates;
- may persist candidates as `source_system=onet`, `status=suggested`;
- explicitly records `auto_promote_to_role_graph=false`.

The deployed source was read back from Supabase and the underlying live RPC was exercised. An independent authenticated HTTP call to `discover_onet` was not executed because no reusable product-user JWT is exposed by the current administration connector; this is not treated as missing proof for the database lookup/sync itself.

## Matching non-regression

After the full O*NET sync, all 57 champion corpus cases were re-scored non-persistently through both the canonical router and direct V3 scorer.

Result:
- router vs direct V3 classification equal: 57/57
- router vs direct V3 classification mismatch: 0
- router vs direct V3 score equal: 57/57
- router vs direct V3 score mismatch: 0
- router vs stored champion classification equal: 57/57

Therefore O*NET did not alter champion scoring/classification.

## Security and capacity

Latest Security Advisor after final schema hardening:
- no O*NET RLS/function warning;
- only existing `auth_leaked_password_protection` WARN remains.

Latest Performance Advisor:
- INFO-only unused indexes, expected in the pilot/early O*NET usage stage;
- no structural performance WARN introduced by O*NET.

Current whole database measurement after the reproducible refresh and retained `pg_net` response records: about 82 MB. This number includes transient/network response storage and is not the size of the normalized O*NET tables alone.

## Canonical rule

`O*NET = DISCOVERY / TAXONOMY EVIDENCE, NOT AUTOMATIC FIT TRUTH.`

`RUNTIME_COMPROVADO_VENCE_DOCUMENTO.`

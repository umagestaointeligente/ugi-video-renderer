# LSI Career 360 — Matching V3.1 Runtime Reconciliation

Date: 2026-09-06
Status: RUNTIME RECONCILED / V3.1 CHAMPION PROVEN

## Why this reconciliation exists

The canonical Recovery and the older Role Graph release still described `v2.0` as matching champion and V3 as challenger. Live Supabase runtime contradicted that documentation.

Per the project rule `RUNTIME_COMPROVADO_VENCE_DOCUMENTO`, the runtime and migration history were audited before any rollback or new feature work.

## Proven promotion

Live `supabase_migrations.schema_migrations` contains:

`20260905183743 — career_matching_v31_promote_and_router`

That migration explicitly:
- routes `career_score_opportunity(...)` through `career_engine_control`;
- routes `v3.1-rolegraph` to `career_score_opportunity_v3(...)`;
- retains `v2.0` as the safe fallback/rollback;
- sets `career_engine_control.component='matching'` to:
  - champion `v3.1-rolegraph`;
  - rollback `v2.0`;
  - status `active`;
- records promotion evidence:
  - synthetic positive cases: 7;
  - synthetic negative hard-gate cases: 4;
  - live corpus size: 57;
  - pre-promotion live classification changes: 0;
  - qualification threshold: 72;
  - role-fit floor: 0.55.

The proven live migration has been mirrored into the canonical repository at:
`career360/migrations/20260905183743_career_matching_v31_promote_and_router.sql`

Mirror commit:
`adb9f240b06c2d2ea1093eaf6a145f8836eac911`

## Current control plane

Live `career_engine_control`:

`matching = v3.1-rolegraph / rollback v2.0 / active`

`matching_role_graph = v3.1-rolegraph / rollback v2.0 / active`

`matching_rolegraph_challenger = v2.1-rolegraph-challenger / paused`

`role_graph = v1.1 / active`

## Runtime corpus revalidation

Current paired V2/V3.1 corpus:
- paired opportunities: 57;
- same classification: 57;
- changed classification: 0;
- score increased: 3;
- score decreased: 11;
- score unchanged: 43;
- average V3.1 minus V2 score delta: -0.69;
- max delta: +6.43;
- min delta: -7.50.

Interpretation: V3.1 remains classification-stable on the current corpus and slightly more conservative on average. This does not prove future perfection; it proves no current classification regression in the validated corpus.

A live non-persisting router check also proved:
`career_score_opportunity(...) == career_score_opportunity_v3(...)`
for the sampled active V3.1 case, including score/classification/salary state.

## Stale consumer hardening

### career-agent V3

Problem found:
The previous live agent queried `career_matches` across every engine. The pilot database currently contains 367 accumulated match rows across historical engines while the champion owns 57 rows. Cross-engine counting could inflate user-facing totals.

Fix:
- read champion + rollback from `career_engine_control`;
- query matches with `.eq('engine_version', engine)`;
- count only active opportunities from the champion;
- expose `matching_engine` in the response/audit metadata.

Canonical source commit:
`b12ca88fcb38f5dcf7b3d8ef7e9cb01591f79a48`

Live Edge Function:
`career-agent` V3 ACTIVE

Deployed SHA:
`0877ba595f53f680a2a926440aa0bfba59919460515501913cb1ae405eb36724`

### career-opportunity-research V5

Problem found:
The previous live V4 still described `v3.0-challenger` and, when V3.1 was already champion, could score V3 twice: once via the canonical router and once via `career_score_opportunity_v3` as a supposed challenger.

Fix:
- read champion + rollback from `career_engine_control`;
- maintain `role-search-v2` for agent-ready users;
- score each changed opportunity exactly once through `career_score_opportunity(...)`;
- remove challenger telemetry;
- report `champion_match_operations` and the live engine/rollback.

Canonical source commit:
`d2a2665c8823f1bbc10e4ad4d4cd94c8b2ea96a9`

Live Edge Function:
`career-opportunity-research` V5 ACTIVE

Deployed SHA:
`c77784d8d50d3b861c8b9c61ede2ee385ef053d1d79da06e1305a84ac2bcbc40`

## Canonical state

`MATCH_ENGINE_V31_ROLEGRAPH=CHAMPION`
`MATCH_ENGINE_V2=ROLLBACK`
`MATCHING_ROUTER_V31=LIVE`
`CAREER_AGENT_CHAMPION_ISOLATION_V3=LIVE`
`OPPORTUNITY_RESEARCH_CHAMPION_ALIGNMENT_V5=LIVE`
`ROLE_SEARCH_PLAN_V2=LIVE`

No rollback was performed because the promotion was proven, intentional, and revalidated. The stale artifact was documentation/consumer assumptions, not the matching champion itself.

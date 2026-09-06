from pathlib import Path

recovery = Path('docs/LSI_RECOVERY_CURRENT.md')
release = Path('career360/releases/MASTER_PILOT_1_0_CLARITY_UI_V16_2026-09-06.md')

r = recovery.read_text()
r = r.replace('`career-ui-state` V1 ACTIVE;', '`career-ui-state` V2 ACTIVE / CONTROL-PLANE ALIGNED;')
r = r.replace('`career-ui-state` V1 / JWT required.', '`career-ui-state` V2 / JWT required / control-plane aligned.')

states_anchor = '`APPLICATION_MILESTONE_RECEIPT_RPC_V16=LIVE`\n'
states = '''`APPLICATION_MILESTONE_RECEIPT_RPC_V16=LIVE`
`APPLICATION_SUBMISSION_RECEIPT_V1=LIVE`
`APPLICATION_SUBMISSION_SIDE_EFFECTS=NONE`
`CAREER_UI_STATE_V2_CONTROL_PLANE_ALIGNED=LIVE`
`MASTER_METRICS_CHAMPION_ONLY=LIVE`
`RADAR_STATUS_RUNTIME_DERIVED_V2=LIVE`
`ROLE_INTELLIGENCE_V2_CHAMPION_ALIGNED=LIVE`
`ROLE_SEARCH_PLAN_V3_CONTROL_PLANE_ALIGNED=LIVE`
`ROLE_SEARCH_SCOPE_V2_CONTROL_PLANE_ALIGNED=LIVE`
'''
if '`APPLICATION_SUBMISSION_RECEIPT_V1=LIVE`' not in r:
    r = r.replace(states_anchor, states)

section = '''
## 9C. Runtime alignment + application submission receipt — SEALED 2026-09-06

Readback vivo após as correções finais de backend:
- matching router genérico vs `career_score_opportunity_v3`: 57/57 classificações idênticas, zero score distinto no corpus champion;
- `career_master_metrics` passou a contar somente o champion: 57 matches, exatamente igual ao corpus `v3.1-rolegraph`; histórico multi-engine deixou de inflar o painel;
- 44/44 tabelas públicas ordinárias com RLS habilitado;
- todas as funções públicas `SECURITY DEFINER` auditadas: `PUBLIC=false`, `anon=false`, `authenticated=false`, `service_role=true`, com `search_path` fixado;
- jobs 1–5 (`raw cleanup`, `master metrics`, `opportunity research`, `proactive digest`, `followup evaluator`) ativos e com última execução `succeeded` no readback final;
- Security Advisor: somente `auth_leaked_password_protection`, limitação conhecida do plano atual;
- Performance Advisor: somente INFO de índices ainda não usados; zero WARN estrutural novo.

Superfícies LIVE alinhadas ao control plane:
- `career-ui-state` V2 — SHA `b80ea34e943f4f64500e931a80dd3407e0c2deeaf842edcbcf4e54eed782d66e`;
- `career-master-status` V4 — SHA `68bfdfa931303f4a0f5d0504b4fa7408befb4e7ecf99f4d99c04f53a0d3fa4dd`;
- `career-radar-status` V2 — SHA `977254bf22c6881c0761fd9cf239955019d83fd5c2f817c2d49f05f0b2d3cef9`;
- `career-opportunity-refresh-now` V3 — SHA `64713e5b6f7720f3535f71ac5e5566ca1095001f3978450e4cc608c0e32187d3`;
- `career-role-intelligence` V2 — SHA `7687e5bd38cde3d1c992381f0ab7db3a1d78c9576626291208d9bf31c95e21c2`;
- `career-role-search-plan` V3 — SHA `ce4e569c4f6add7b4d9f7a341172b23a34f0b2407aa03676942549d17329b3cb`;
- `career-role-search-scope` V2 — SHA `2d18c9d764ac6f1319f2f2d3734e68c5c0a745361a73cd1a4ce25591720a9acc`.

Taxonomias no runtime:
- CBO = `live_bulk`, 2.694 ocupações + 7.778 sinônimos;
- ESCO = `live_api`;
- LSI curated = `live_bulk`;
- O*NET = `bulk_pending`.

Application Submission Receipt V1 LIVE:
- migration: `career360/migrations/20260906_application_submission_receipt_v16.sql`;
- migration source commit: `b4a7e2c063c63330bdb2fd3f8ab080a426de02ae`;
- permanent smoke: `career360/tests/v16-application-submission-receipt-smoke.sql`;
- smoke source commit: `2b85ed833c340a1d352c742df4be5e6ae2188401`;
- transactional smoke: 7/7 PASS;
- post-rollback: applications=0, followups=0, mail_actions=0;
- external reference raw is never persisted; provider-qualified SHA-256 receipt only;
- receipt conflict is rejected;
- replay is idempotent;
- follow-up requires explicit `due_at`;
- no mail/application submission side effect exists inside the primitive.

Estados:
`APPLICATION_SUBMISSION_RECEIPT_V1=LIVE`
`APPLICATION_SUBMISSION_SIDE_EFFECTS=NONE`
`BACKEND_RUNTIME_ALIGNMENT_2026_09_06=PASS`
`SUPABASE_PUBLIC_TABLE_RLS=44_OF_44`
`MASTER_METRICS_SCOPE=ACTIVE_CHAMPION_ONLY`

Este selo não altera os bloqueios externos: `MAIL_DELIVERY_CONNECTOR=NOT_LIVE`, `CAREER_GMAIL_OAUTH=NOT_LIVE`, `SUPABASE_SERVER_REDIRECT_ALLOWLIST=NOT_YET_PROVEN` e V15/V16 continuam não promovidos na Vercel.
'''
if '## 9C. Runtime alignment + application submission receipt' not in r:
    marker = '\n## 10.'
    if marker in r:
        r = r.replace(marker, '\n' + section + marker, 1)
    else:
        r += '\n' + section
recovery.write_text(r)

v = release.read_text()
v = v.replace('43/43 ordinary public tables have RLS enabled and at least one policy;', '44/44 ordinary public tables have RLS enabled; the final catalog readback showed zero ordinary public tables with RLS disabled;')
release_section = '''
## Final backend runtime alignment seal — 2026-09-06

V16 frontend remains not promoted, but the live backend/readiness surfaces were reconciled so historical engine/status assumptions no longer leak into the product.

Final runtime evidence:
- generic matching router vs V3.1 implementation: 57/57 same classification and zero distinct score mismatch;
- master metrics = 57 champion matches, exactly matching `v3.1-rolegraph` rather than the previous 367 multi-engine historical rows;
- public ordinary tables: 44/44 RLS enabled;
- all audited public SECURITY DEFINER functions service-role-only with fixed search path;
- all five Career cron jobs active and latest run `succeeded` at final readback;
- security advisor baseline: only leaked-password protection WARN;
- performance advisor baseline: INFO-only unused indexes.

Runtime-aligned Edge Functions:
- `career-ui-state` V2 (`b80ea34e943f...`);
- `career-master-status` V4 (`68bfdfa93130...`);
- `career-radar-status` V2 (`977254bf22c6...`);
- `career-opportunity-refresh-now` V3 (`64713e5b6f77...`);
- `career-role-intelligence` V2 (`7687e5bd38cd...`);
- `career-role-search-plan` V3 (`ce4e569c4f6a...`);
- `career-role-search-scope` V2 (`2d18c9d764ac...`).

Taxonomy runtime truth: CBO `live_bulk` (2,694 occupations / 7,778 synonyms), ESCO `live_api`, LSI curated `live_bulk`, O*NET `bulk_pending`.

### Application Submission Receipt V1

A service-only receipt primitive now closes the internal evidence chain from a prepared application to a factual `applied` state.

Evidence:
- migration commit `b4a7e2c063c63330bdb2fd3f8ab080a426de02ae`;
- permanent smoke commit `2b85ed833c340a1d352c742df4be5e6ae2188401`;
- live transactional smoke 7/7 PASS;
- independent post-rollback counts: applications=0, followups=0, mail_actions=0;
- raw external application reference is hashed and never persisted;
- conflicting receipt fails closed;
- replay is idempotent;
- optional follow-up requires an explicit due time;
- the primitive never submits a real application and never sends mail.

`APPLICATION_SUBMISSION_RECEIPT_V1=LIVE`
`APPLICATION_SUBMISSION_SIDE_EFFECTS=NONE`
`BACKEND_RUNTIME_ALIGNMENT_2026_09_06=PASS`

This does not change the frontend deployment state or prove any external connector action.
'''
if '## Final backend runtime alignment seal' not in v:
    v += '\n' + release_section
release.write_text(v)

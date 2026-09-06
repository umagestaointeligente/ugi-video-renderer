from pathlib import Path

ROOT = Path('.')
RECOVERY = ROOT / 'docs/LSI_RECOVERY_CURRENT.md'
RELEASE = ROOT / 'career360/releases/MASTER_PILOT_1_0_CLARITY_UI_V16_2026-09-06.md'
START = '<!-- ONET31_RUNTIME_SEAL_START -->'
END = '<!-- ONET31_RUNTIME_SEAL_END -->'

block = f'''{START}

## O*NET 31.0 — runtime bulk evidence LIVE

Runtime validation completed on 2026-09-06 BRT.

`ONET_31_LOOKUP_LAYER=LIVE`
`ONET_31_BULK_SYNC=LIVE`
`ONET_SOURCE_STATUS=live_bulk`
`ONET_SOURCE_VERSION=31.0`
`ONET_ROLE_GRAPH_AUTO_PROMOTION=DISABLED`
`ONET_MATCHING_MUTATION=NONE`
`ONET_MATCHING_REGRESSION=57_OF_57_CLASS_AND_SCORE_STABLE`
`ONET_RUNTIME_SMOKE=PASS`
`CAREER_ROLE_INTELLIGENCE_V3=ACTIVE_DEPLOYED_READBACK_PROVEN`
`SUPABASE_PUBLIC_TABLE_RLS=47_OF_47`

Live normalized corpus:
- 1,016 O*NET occupations;
- 54,269 raw job-title rows;
- 54,229 persisted unique normalized job titles;
- 40 deterministic normalization duplicates recorded.

Reproducible sync:
- `career_onet_begin_sync('31.0')` + `career_onet_finalize_sync()`;
- pg_net request ids `230` / `231` returned HTTP 200;
- first finalizer correctly returned `RESPONSES_NOT_READY` without mutation;
- successful finalizer reconciled all source/persisted counts and set `live_bulk` only after validation;
- second finalizer was an idempotent no-op;
- cron job `6` `career-onet-monthly-refresh` active at `17 3 10 * *`;
- cron job `7` `career-onet-sync-finalizer` active at `*/10 * * * *`.

Security:
- O*NET tables and sync-state are RLS-protected with explicit client denial;
- `career_onet_search`, `career_onet_begin_sync`, and `career_onet_finalize_sync` execute only for `service_role`;
- Security Advisor has no O*NET warning; only the known leaked-password-protection plan limitation remains;
- Performance Advisor remains INFO-only for unused indexes.

Role Intelligence:
- `career-role-intelligence` V3 ACTIVE;
- `verify_jwt=true`;
- deployed SHA256 `54b68a6fbaf4d6e7831adcf7a42abd6871f18dab3b18a59cabf5a1e1012194da`;
- `discover_onet` returns/persists evidence-only suggestions and records `auto_promote_to_role_graph=false`.

Canonical evidence:
`career360/docs/ONET_31_RUNTIME_INTEGRATION_2026-09-06.md`.

Important boundary:
O*NET is taxonomy/discovery evidence only. It does not automatically alter Role Graph aliases, FIT, or matching classification.

External product gates remain separate from this backend LIVE state:
- official Vercel production remains V14; V16 is not promoted;
- Career Gmail/Outlook product OAuth and mail delivery connector are not live;
- hosted Supabase Auth redirect allowlist is not exposed by the current administration connector and remains unproven.

`RUNTIME_COMPROVADO_VENCE_DOCUMENTO.`

{END}'''

def upsert_block(path: Path):
    text = path.read_text(encoding='utf-8')
    if START in text and END in text:
        pre = text.split(START, 1)[0].rstrip()
        post = text.split(END, 1)[1].lstrip('\n')
        text = pre + '\n\n' + block + '\n\n' + post
    else:
        text = text.rstrip() + '\n\n' + block + '\n'
    path.write_text(text, encoding='utf-8')

for p in (RECOVERY, RELEASE):
    upsert_block(p)

print('ONET31_RUNTIME_SEAL_FILES_UPDATED=PASS')

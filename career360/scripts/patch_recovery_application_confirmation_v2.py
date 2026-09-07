from pathlib import Path

recovery = Path('docs/LSI_RECOVERY_CURRENT.md')
s = recovery.read_text(encoding='utf-8')
s = s.replace('`SECURITY_DEFINER_ACL=PASS_54_ZERO_PUBLIC_ANON_AUTH_EXEC`', '`SECURITY_DEFINER_ACL=PASS_55_ZERO_PUBLIC_ANON_AUTH_EXEC`')
s = s.replace('- SECURITY DEFINER = 54, execute PUBLIC/anon/authenticated = 0, fixed search_path = 54/54;', '- SECURITY DEFINER = 55, execute PUBLIC/anon/authenticated = 0, fixed search_path = 55/55;')
anchor = '`APPLICATION_SUBMISSION_DISPATCH_V2=LIVE_SERVICE_ONLY_CLAIM_BOUND`\n'
extra = (
    '`APPLICATION_CONFIRMATION_EDGE_V2=ACTIVE_JWT_REQUIRED`\n'
    '`APPLICATION_CONFIRMATION_ATOMIC_RPC_V2=LIVE_SERVICE_ONLY`\n'
    '`APPLICATION_CONFIRMATION_AUTHENTICATED_E2E=PENDING_REAL_FRONTEND_SESSION`\n'
)
if extra not in s:
    s = s.replace(anchor, anchor + extra)
doc_anchor = '`career360/docs/APPLICATION_SUBMISSION_DISPATCH_V2_LIVE_2026-09-07.md`\n'
new_doc = '`career360/docs/APPLICATION_CONFIRMATION_V2_LIVE_2026-09-07.md`\n'
if new_doc not in s:
    s = s.replace(doc_anchor, doc_anchor + new_doc)
proof_anchor = '- Make Gmail/SMTP-IMAP/Microsoft mail connections = none (`existing=[]`); no OAuth request created.\n'
proof_extra = (
    '- `career-application-confirm` V2 ACTIVE, verify_jwt=true, SHA `85ce6535ae020696c741d3960979b22ab9e3756a683a17c754a487b089792f44`;\n'
    '- atomic confirmation RPC smoke = PASS: confirm/revoke/audit/permission-false preservation/post-claim rejection, transactional rollback;\n'
    '- Make private + standard spaces: Supabase/Supabase Management/PostgreSQL connections = none; mail connections = none;\n'
    '- authenticated browser E2E for application confirmation = pending a real frontend session; no provider side effect.\n'
)
if proof_extra not in s:
    s = s.replace(proof_anchor, proof_anchor + proof_extra)
recovery.write_text(s, encoding='utf-8')

appdoc = Path('career360/docs/APPLICATION_SUBMISSION_DISPATCH_V2_LIVE_2026-09-07.md')
d = appdoc.read_text(encoding='utf-8')
d = d.replace('Public SECURITY DEFINER functions:\n`54`', 'Public SECURITY DEFINER functions:\n`55`')
d = d.replace('- fixed `search_path` = 54/54', '- fixed `search_path` = 55/55')
append = '''\n\n## Per-application confirmation mediator V2\n\nThe dispatch contract is now paired with an authenticated confirmation mediator.\n\nCanonical document:\n`career360/docs/APPLICATION_CONFIRMATION_V2_LIVE_2026-09-07.md`\n\nRuntime:\n- `career-application-confirm` V2 ACTIVE;\n- `verify_jwt=true`;\n- SHA-256 `85ce6535ae020696c741d3960979b22ab9e3756a683a17c754a487b089792f44`;\n- atomic service-only RPC `career_set_application_submission_confirmation`;\n- current global `allow_application_submit=false`;\n- provider side effects remain NONE;\n- authenticated frontend E2E remains pending a real user session.\n'''
if '## Per-application confirmation mediator V2' not in d:
    d += append
appdoc.write_text(d, encoding='utf-8')

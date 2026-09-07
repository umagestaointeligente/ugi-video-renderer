from pathlib import Path

p = Path('docs/LSI_RECOVERY_CURRENT.md')
s = p.read_text(encoding='utf-8')

s = s.replace('`APPLICATION_SUBMISSION_RECEIPT_V1=LIVE`', '`APPLICATION_SUBMISSION_RECEIPT_V2=LIVE_SERVICE_ONLY_CLAIM_BOUND`')
s = s.replace('`SECURITY_DEFINER_ACL=PASS_51_ZERO_PUBLIC_ANON_AUTH_EXEC`', '`SECURITY_DEFINER_ACL=PASS_54_ZERO_PUBLIC_ANON_AUTH_EXEC`')
s = s.replace('- SECURITY DEFINER = 51, execute PUBLIC/anon/authenticated = 0, fixed search_path = 51/51;', '- SECURITY DEFINER = 54, execute PUBLIC/anon/authenticated = 0, fixed search_path = 54/54;')

anchor = '`APPLICATION_SUBMISSION_SIDE_EFFECTS=NONE`\n'
extra = (
    '`APPLICATION_SUBMISSION_DISPATCH_V2=LIVE_SERVICE_ONLY_CLAIM_BOUND`\n'
    '`APPLICATION_SUBMISSION_RECEIPT_V1=RETIRED_SERVICE_EXEC_REVOKED`\n'
    '`APPLICATION_PROVIDER_CONNECTOR=NOT_LIVE`\n'
    '`QUICKIN_CONNECTOR=INACTIVE_HARD_GATED_SUBMIT_UNCONFIRMED`\n'
    '`DIRECT_HTTP_SUBMIT=RETIRED_NO_AUTH_NO_RECEIPT`\n'
    '`MAKE_MAIL_EXISTING_CONNECTIONS=NONE`\n'
)
if extra not in s:
    s = s.replace(anchor, anchor + extra)

runtime_doc = '`career360/docs/RUNTIME_TRUTH_HARDENING_2026-09-07.md`\n'
app_doc = '`career360/docs/APPLICATION_SUBMISSION_DISPATCH_V2_LIVE_2026-09-07.md`\n'
if app_doc not in s:
    s = s.replace(runtime_doc, runtime_doc + app_doc)

proof_anchor = '- applications/followups/mail_actions = 0/0/0; mail delivery continua PAUSED.\n'
proof_extra = (
    '- application dispatch V2 transactional smoke = PASS: permission OFF -> 0 claim; permission ON + confirmation -> single claim; correct receipt -> applied; wrong claim -> rejected; rollback restored 0/0/0;\n'
    '- application submission receipt V1 service execute revoked; V2 claim/uncertain/receipt service-only;\n'
    '- Quickin Make scenario `6090823` = INACTIVE + explicit `confirm_submit` gate; historical provider result `SUBMIT_UNCONFIRMED`, `submitted=false`;\n'
    '- generic HTTP submit scenario `6075235` = RETIRED / no auth / no receipt / no executions;\n'
    '- Make Gmail/SMTP-IMAP/Microsoft mail connections = none (`existing=[]`); no OAuth request created.\n'
)
if proof_extra not in s:
    s = s.replace(proof_anchor, proof_anchor + proof_extra)

p.write_text(s, encoding='utf-8')

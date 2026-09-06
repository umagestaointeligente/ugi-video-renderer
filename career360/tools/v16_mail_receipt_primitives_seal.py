from pathlib import Path
import re

REC=Path('docs/LSI_RECOVERY_CURRENT.md')
REL=Path('career360/releases/MASTER_PILOT_1_0_CLARITY_UI_V16_2026-09-06.md')

s=REC.read_text()

anchor='`DELIVERY_EVIDENCE_GUARDS_V16=LIVE`\n`MAIL_SENT_RECEIPT_GUARD_V16=LIVE`\n`APPLICATION_APPLIED_RECEIPT_GUARD_V16=LIVE`\n`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`\n'
insert='`DELIVERY_EVIDENCE_GUARDS_V16=LIVE`\n`MAIL_SENT_RECEIPT_GUARD_V16=LIVE`\n`APPLICATION_APPLIED_RECEIPT_GUARD_V16=LIVE`\n`EXTERNAL_EVENT_RECEIPT_GUARDS_V16=LIVE`\n`MAIL_RECEIPT_PRIMITIVES_V16=LIVE`\n`APPLICATION_MILESTONE_RECEIPT_RPC_V16=LIVE`\n`GMAIL_CHATGPT_CONNECTOR_READ=PROVEN`\n`GMAIL_PROVIDER_RECEIPT_SHAPE=PROVEN`\n`CAREER_GMAIL_OAUTH=NOT_LIVE`\n`OUTLOOK_EMAIL_CONNECTOR=AVAILABLE_NOT_INSTALLED`\n`CAREER_OUTLOOK_OAUTH=NOT_LIVE`\n`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`\n'
if '`MAIL_RECEIPT_PRIMITIVES_V16=LIVE`' not in s:
    if anchor not in s: raise SystemExit('mail global state anchor missing')
    s=s.replace(anchor,insert,1)

section='''\n### Mail provider receipt primitives V16 — LIVE infrastructure, connector NOT LIVE\n\nA camada de evidência externa foi completada antes da ativação de Gmail/Outlook no produto.\n\nMigrações canônicas novas:\n- `career360/migrations/20260906_external_event_receipt_guards_v16.sql` — commit `9957b2bb2f3650b8062d2fef77f022bfedeb47cd`;\n- `career360/migrations/20260906_mail_delivery_receipt_rpc_v16.sql` — commit `9a2df7b0f55af3248b070941b3110c1862c8c43f`;\n- `career360/migrations/20260906_external_event_receipt_rpcs_v16.sql` — commit `257ca4257b534a1792330773e31dc961d28579c4`;\n- smoke permanente `career360/tests/v16-receipt-contract-smoke.sql` — commit `01159c2d4dedf7678b3c946d5783b78453a8c25e`;\n- contrato `career360/docs/MAIL_PROVIDER_RECEIPT_CONTRACT_V16.md` — commit `51d351664d78f9112e435ff163e29ad99ad06c47`.\n\nBanco LIVE:\n- inbound exige `mail_provider + received_at + external_thread_ref_hash + external_message_ref_hash`;\n- milestones externos (`recruiter_reply`, `interview_pending`, `interview_confirmed`, `finalist`, `offer`, `hired`, `rejected`, `closed`) exigem provider + hash de evento + horário observado;\n- `career_record_mail_delivery_receipt(...)` é service-only, `SECURITY DEFINER`, `search_path=public,extensions`, idempotente e só permite `approved -> sent`;\n- `career_record_inbound_mail_event(...)` é service-only e idempotente;\n- `career_record_application_milestone(...)` é service-only e idempotente;\n- IDs externos brutos entram apenas transitoriamente e os RPCs persistem SHA-256.\n\nTeste vivo transacional com rollback:\n- 9/9 PASS;\n- delivery first + idempotent PASS;\n- inbound first + idempotent PASS;\n- milestone first + idempotent PASS;\n- inbound sem IDs externos = CHECK_REJECTED;\n- sent sem receipt = CHECK_REJECTED;\n- milestone sem ref = CHECK_REJECTED;\n- pós-rollback: `career_applications=0`, `career_mail_actions=0`.\n\nGmail dentro do ChatGPT:\n- conector legível = PROVEN;\n- mensagem real em SENT expõe `id`, `thread_id` e timestamp, suficientes para o contrato de receipt;\n- isso NÃO equivale a OAuth/background connector do Career 360.\n\nOutlook:\n- conector `Outlook Email` existe no diretório e estava `AVAILABLE_NOT_INSTALLED` na auditoria;\n- não declarar OAuth Outlook do produto.\n\nEstados:\n`EXTERNAL_EVENT_RECEIPT_GUARDS_V16=LIVE`\n`MAIL_RECEIPT_PRIMITIVES_V16=LIVE`\n`APPLICATION_MILESTONE_RECEIPT_RPC_V16=LIVE`\n`GMAIL_CHATGPT_CONNECTOR_READ=PROVEN`\n`GMAIL_PROVIDER_RECEIPT_SHAPE=PROVEN`\n`CAREER_GMAIL_OAUTH=NOT_LIVE`\n`OUTLOOK_EMAIL_CONNECTOR=AVAILABLE_NOT_INSTALLED`\n`CAREER_OUTLOOK_OAUTH=NOT_LIVE`\n`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`\n\nOs estados LIVE acima são infraestrutura de evidência. Nenhum novo envio, inbound, candidatura ou milestone real foi criado durante o smoke.\n'''
marker='\nRedirect de confirmação usado pelo cliente:\n'
if '### Mail provider receipt primitives V16 — LIVE infrastructure, connector NOT LIVE' not in s:
    if marker not in s: raise SystemExit('redirect marker missing')
    s=s.replace(marker,section+marker,1)

pat=r'`LAST_VERIFIED_CHANGE=[^`]+`'
if len(re.findall(pat,s))!=1: raise SystemExit('last verified cardinality')
last='`LAST_VERIFIED_CHANGE=MAIL_RECEIPT_PRIMITIVES_V16_LIVE_EXTERNAL_EVENT_GUARDS_LIVE_TRANSACTIONAL_SMOKE_9_OF_9_PASS_ROLLBACK_ZERO_ROWS_GMAIL_CHATGPT_READ_AND_RECEIPT_SHAPE_PROVEN_BUT_CAREER_GMAIL_OAUTH_NOT_LIVE_OUTLOOK_AVAILABLE_NOT_INSTALLED_MAIL_DELIVERY_CONNECTOR_NOT_LIVE_V16_FRONTEND_STILL_NOT_PROMOTED_VERCEL_CHAT_CONNECTOR_MUTATION_STILL_UNSCOPED_PRODUCTION_STILL_V14`'
s=re.sub(pat,last,s,count=1)
REC.write_text(s)

r=REL.read_text()
relsec='''\n## Mail provider receipt primitives\n\nThe external evidence contract was completed before activating a real product mail connector.\n\nCanonical additions:\n- external event receipt guards `9957b2bb2f3650b8062d2fef77f022bfedeb47cd`;\n- service-only outbound delivery receipt RPC `9a2df7b0f55af3248b070941b3110c1862c8c43f`;\n- service-only inbound/milestone RPCs `257ca4257b534a1792330773e31dc961d28579c4`;\n- permanent rollback-safe smoke `01159c2d4dedf7678b3c946d5783b78453a8c25e`;\n- provider contract `career360/docs/MAIL_PROVIDER_RECEIPT_CONTRACT_V16.md` (`51d351664d78f9112e435ff163e29ad99ad06c47`).\n\nLive database primitives:\n- outbound `sent` remains provider-receipt gated;\n- inbound requires provider, received timestamp, thread hash and message hash;\n- external application milestones require provider, event hash and observed timestamp;\n- all receipt RPCs are service-only; raw provider identifiers are hashed before persistence.\n\nA live transactional smoke returned 9/9 PASS and rolled back all test rows. Post-rollback application/mail row counts remained zero.\n\nThe Gmail connector inside ChatGPT is readable and its real sent-message shape exposes message id, thread id and timestamp, which is sufficient for the receipt mapping. This is not Career 360 product OAuth. Outlook Email was available in the plugin directory but not installed during this audit.\n\nStates:\n`EXTERNAL_EVENT_RECEIPT_GUARDS_V16=LIVE`\n`MAIL_RECEIPT_PRIMITIVES_V16=LIVE`\n`APPLICATION_MILESTONE_RECEIPT_RPC_V16=LIVE`\n`GMAIL_CHATGPT_CONNECTOR_READ=PROVEN`\n`GMAIL_PROVIDER_RECEIPT_SHAPE=PROVEN`\n`CAREER_GMAIL_OAUTH=NOT_LIVE`\n`OUTLOOK_EMAIL_CONNECTOR=AVAILABLE_NOT_INSTALLED`\n`CAREER_OUTLOOK_OAUTH=NOT_LIVE`\n`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`\n\nNo actual email/application event is claimed from this infrastructure-only validation.\n'''
marker='\n## Deployment state\n'
if '## Mail provider receipt primitives' not in r:
    if marker not in r: raise SystemExit('release deployment marker missing')
    r=r.replace(marker,relsec+marker,1)
REL.write_text(r)
print('V16_MAIL_RECEIPT_PRIMITIVES_DOCS_SEAL=PASS')

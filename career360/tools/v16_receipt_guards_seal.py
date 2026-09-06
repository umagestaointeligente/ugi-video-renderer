from pathlib import Path
import re

REC=Path('docs/LSI_RECOVERY_CURRENT.md')
REL=Path('career360/releases/MASTER_PILOT_1_0_CLARITY_UI_V16_2026-09-06.md')

s=REC.read_text()

anchor='`MAIL_DECISION=LIVE`\n`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`\n'
insert='`MAIL_DECISION=LIVE`\n`DELIVERY_EVIDENCE_GUARDS_V16=LIVE`\n`MAIL_SENT_RECEIPT_GUARD_V16=LIVE`\n`APPLICATION_APPLIED_RECEIPT_GUARD_V16=LIVE`\n`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`\n'
if '`DELIVERY_EVIDENCE_GUARDS_V16=LIVE`' not in s:
    if anchor not in s: raise SystemExit('mail state anchor missing')
    s=s.replace(anchor,insert,1)

section='''\n### Delivery/application evidence guards V16 — LIVE\n\nAntes da ativação de qualquer conector real de envio/candidatura, as tabelas estavam vazias e foram endurecidas fail-closed. Nenhum dado legado precisou ser corrigido.\n\nMigrações canônicas:\n- `career360/migrations/20260906_delivery_receipt_guards_v16.sql` — commit `d21f7cfbca17e2fab2a274ff9f5f154361eb6e7b`;\n- `career360/migrations/20260906_delivery_receipt_identity_v16.sql` — commit `900398868256dae12faba0df869bd265eb690a45`.\n\nBanco LIVE:\n- `career_mail_actions.status='sent'` exige `direction='outbound'`, `sent_at`, `external_thread_ref_hash` e `delivery_receipt_hash`;\n- `delivery_receipt_hash` é identidade separada da thread e deve vir de sucesso retornado pelo provider;\n- `(user_id, delivery_receipt_hash)` é único quando o recibo existe;\n- `career_applications.status='applied'` exige `applied_at` + `external_application_ref_hash`;\n- `(user_id, external_application_ref_hash)` é único quando a referência existe;\n- ambos os CHECK constraints foram lidos no catálogo como `convalidated=true`.\n\nA camada atual `career-mail-decision` continua correta: `approve` grava somente `approved` e retorna `delivery_connector_required=true`; aprovação não vira `sent`.\n\nEstados:\n`DELIVERY_EVIDENCE_GUARDS_V16=LIVE`\n`MAIL_SENT_RECEIPT_GUARD_V16=LIVE`\n`APPLICATION_APPLIED_RECEIPT_GUARD_V16=LIVE`\n`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`\n\nEsses guards não provam que e-mail foi enviado ou candidatura foi realizada. Eles impedem que esses estados sejam persistidos sem a evidência mínima contratada.\n'''
marker='\nRedirect de confirmação usado pelo cliente:\n'
if '### Delivery/application evidence guards V16 — LIVE' not in s:
    if marker not in s: raise SystemExit('redirect marker missing')
    s=s.replace(marker,section+marker,1)

pat=r'`LAST_VERIFIED_CHANGE=[^`]+`'
if len(re.findall(pat,s))!=1: raise SystemExit('last verified cardinality')
last='`LAST_VERIFIED_CHANGE=DELIVERY_EVIDENCE_GUARDS_V16_LIVE_MAIL_SENT_REQUIRES_PROVIDER_RECEIPT_HASH_THREAD_AND_SENT_AT_APPLICATION_APPLIED_REQUIRES_EXTERNAL_REF_AND_APPLIED_AT_RECEIPT_REUSE_UNIQUE_PROACTIVE_DIGEST_TRUTH_V2_LIVE_SUPABASE_SECURITY_AUDIT_PASS_V16_FRONTEND_STILL_NOT_PROMOTED_VERCEL_CHAT_CONNECTOR_MUTATION_STILL_UNSCOPED_PRODUCTION_STILL_V14`'
s=re.sub(pat,last,s,count=1)
REC.write_text(s)

r=REL.read_text()
relsec='''\n## Delivery and application evidence guards\n\nThe database was hardened before real mail/application connectors are enabled. Both target tables were empty at migration time, so no legacy state was rewritten.\n\nCanonical migrations:\n- `career360/migrations/20260906_delivery_receipt_guards_v16.sql` (`d21f7cfbca17e2fab2a274ff9f5f154361eb6e7b`);\n- `career360/migrations/20260906_delivery_receipt_identity_v16.sql` (`900398868256dae12faba0df869bd265eb690a45`).\n\nFail-closed invariants now LIVE:\n- mail `sent` requires outbound direction, `sent_at`, external thread reference, and separate provider-derived `delivery_receipt_hash`;\n- delivery receipt identity cannot be reused for two mail actions by the same user;\n- application `applied` requires `applied_at` and external application reference;\n- external application receipt identity cannot be reused for two applications by the same user;\n- both CHECK constraints are validated in the live catalog.\n\n`career-mail-decision` still records user approval as `approved`, never `sent`, and explicitly reports that a delivery connector is required.\n\nStates:\n`DELIVERY_EVIDENCE_GUARDS_V16=LIVE`\n`MAIL_SENT_RECEIPT_GUARD_V16=LIVE`\n`APPLICATION_APPLIED_RECEIPT_GUARD_V16=LIVE`\n`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`\n\nThese guards are evidence contracts, not delivery receipts by themselves. No send/application is claimed without an external connector receipt.\n'''
marker='\n## Deployment state\n'
if '## Delivery and application evidence guards' not in r:
    if marker not in r: raise SystemExit('release deployment marker missing')
    r=r.replace(marker,relsec+marker,1)
REL.write_text(r)
print('V16_RECEIPT_GUARDS_DOCS_SEAL=PASS')

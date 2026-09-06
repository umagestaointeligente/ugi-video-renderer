from pathlib import Path
import re

p=Path('docs/LSI_RECOVERY_CURRENT.md')
s=p.read_text()

anchor='`APPLICATION_MILESTONE_RECEIPT_RPC_V16=LIVE`'
if anchor not in s:
    raise SystemExit('receipt primitive gate anchor missing')
if '`FOLLOWUP_SCHEDULER_V1=LIVE`' not in s:
    s=s.replace(anchor, anchor+'\n`FOLLOWUP_SCHEDULER_V1=LIVE`\n`FOLLOWUP_DELIVERY_SIDE_EFFECTS=NONE`\n`MAIL_DELIVERY_CONTROL=PAUSED`',1)

section='''### Follow-up Scheduler V1 — LIVE\n\nScheduler fail-closed para prazos explícitos de follow-up. Não cria candidatura, não escolhe prazo automaticamente, não cria e-mail e não envia mensagem.\n\nRuntime comprovado:\n- `career_followups` com RLS e SELECT-only da própria linha para authenticated; writes service-only;\n- `career_schedule_followup` e `career_process_due_followups` = SECURITY DEFINER / service_role only;\n- `followup_scheduler = v1.0 / active`;\n- `mail_delivery = none / paused`;\n- cron `career-followup-evaluator`, job 5, schedule `23,53 * * * *`, executor `postgres`;\n- candidatura precisa estar `applied` com receipt externo antes de poder receber follow-up;\n- `allow_followup_draft=false` bloqueia em `due_waiting_permission`;\n- conector de mail não LIVE bloqueia em `due_waiting_connector`;\n- mesmo `due_ready_for_orchestration` não cria `career_mail_actions` nem envia e-mail.\n\nQA transacional:\n- schedule inicial PASS;\n- idempotência PASS;\n- permission gate PASS;\n- connector gate PASS;\n- ready gate PASS;\n- progresso externo cancela follow-up PASS;\n- candidatura não applied rejeitada PASS;\n- mail side effect = 0;\n- rollback confirmado com `career_applications=0`, `career_followups=0`, `career_mail_actions=0`.\n\nSmoke permanente:\n`career360/tests/followup-scheduler-v1-smoke.sql`\ncommit `458191d7e36571f9a2f1eebb0506fea36bab1d72`.\n\nMigration base:\n`career360/migrations/20260906_followup_scheduler_v1.sql`\ncommit `5c26f83527e372b21ce77950fbdb196ce90fa196`.\n\nAdvisor hardening:\n`career360/migrations/20260906_followup_scheduler_v1_advisor_hardening.sql`\ncommit `295c21f86b7b89cfb2694465e848030c3634d5be`.\n\nAdvisor pós-hardening:\n- Security: somente leaked-password protection WARN conhecido;\n- Performance: somente INFO unused_index; sem WARN estrutural novo.\n\nDocumento canônico:\n`career360/docs/FOLLOWUP_SCHEDULER_V1_LIVE_2026-09-06.md`\ncommit `2bc76e9f035852446672e86f67d099983889d457`.\n\nEstados:\n`FOLLOWUP_SCHEDULER_V1=LIVE`\n`FOLLOWUP_DELIVERY_SIDE_EFFECTS=NONE`\n`MAIL_DELIVERY_CONTROL=PAUSED`\n`MAIL_DELIVERY_CONNECTOR=NOT_LIVE`\n\n'''
if '### Follow-up Scheduler V1 — LIVE' not in s:
    pat=r'\n(`LAST_VERIFIED_CHANGE=[^`]+`)'
    if not re.search(pat,s):
        raise SystemExit('LAST_VERIFIED_CHANGE marker missing')
    s=re.sub(pat,'\n'+section+r'\1',s,count=1)

s=re.sub(r'(?im)^(\s*\d+\.\s+follow-up scheduler[^\n]*)$', lambda m: m.group(1) + ' — COMPLETED V1 LIVE' if 'COMPLETED V1 LIVE' not in m.group(1) else m.group(1), s)

pat=r'`LAST_VERIFIED_CHANGE=[^`]+`'
if len(re.findall(pat,s))!=1:
    raise SystemExit('LAST_VERIFIED_CHANGE cardinality')
s=re.sub(pat,'`LAST_VERIFIED_CHANGE=FOLLOWUP_SCHEDULER_V1_LIVE_FAIL_CLOSED_CRON_ACTIVE_SMOKE_PERMANENT_ROLLBACK_ZERO_DATA_ADVISORS_BASELINE_MATCHING_V31_CHAMPION_AGENT_V3_RESEARCH_V5_MAIL_RECEIPT_PRIMITIVES_LIVE_MAIL_DELIVERY_CONNECTOR_NOT_LIVE_V16_FRONTEND_NOT_PROMOTED_VERCEL_CHAT_MUTATION_UNSCOPED_PRODUCTION_V14`',s,count=1)

p.write_text(s)
print('FOLLOWUP_SCHEDULER_V1_RECOVERY_SEAL=PASS')

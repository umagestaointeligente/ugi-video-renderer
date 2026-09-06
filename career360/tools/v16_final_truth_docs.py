from pathlib import Path
import re

REC=Path('docs/LSI_RECOVERY_CURRENT.md')
REL=Path('career360/releases/MASTER_PILOT_1_0_CLARITY_UI_V16_2026-09-06.md')

OLD_APP='3cd06d176f81e07c6f4dba1f7fb962f73be4ce34'
NEW_APP='719c15ebfe89d212a19473b70ea6e615174601d9'
OLD_BUNDLE='ac8a46fe5a5d3f28aab15c31c0bafd8e6558f844'
NEW_BUNDLE='4fae7cd5b57fdf68681ac0875f006f8e158f821e'
OLD_RUN='34009190125'
NEW_RUN='34010192948'
OLD_JOB='101421875198'
NEW_JOB='101424535949'
OLD_DEPLOY='921fed05010b71d9a49f1a910f8c0a40ec49dc89'
NEW_DEPLOY='7aba73e550410ed111dde30007a0033935c7b0e4'

# Recovery
s=REC.read_text()
if OLD_DEPLOY not in s: raise SystemExit('Recovery old deploy workflow commit missing')
s=s.replace(OLD_DEPLOY,NEW_DEPLOY,1)
start=s.index('## 9A. V16 — Clarity UI / menos texto / decisão primeiro')
end=s.index('## 10. Radar / Matching',start)
sec=s[start:end]
for old,new,label in [(OLD_APP,NEW_APP,'app-m'),(OLD_BUNDLE,NEW_BUNDLE,'bundle'),(OLD_RUN,NEW_RUN,'run'),(OLD_JOB,NEW_JOB,'job')]:
    if old not in sec: raise SystemExit(f'Recovery V16 {label} missing')
    sec=sec.replace(old,new,1)
if '- `V16_AUTH_TRUTHFUL_COPY_POLICY=PASS`;\n' not in sec:
    anchor='- `V16_TRUTHFUL_STATUS_POLICY=PASS`;\n'
    if anchor not in sec: raise SystemExit('Recovery truth policy anchor missing')
    sec=sec.replace(anchor,anchor+'- `V16_AUTH_TRUTHFUL_COPY_POLICY=PASS`;\n',1)
if '- `V16_AUTH_TRUTHFUL_COPY=PASS`.\n' not in sec:
    anchor='- `V16_TRUTHFUL_RUNTIME_DERIVATION=PASS`.\n'
    if anchor not in sec: raise SystemExit('Recovery runtime evidence anchor missing')
    sec=sec.replace(anchor,'- `V16_TRUTHFUL_RUNTIME_DERIVATION=PASS`;\n- `V16_AUTH_TRUTHFUL_COPY=PASS`.\n',1)
if 'Você confirma o que importa. O Career 360 organiza sua busca.' not in sec:
    anchor='- foco visível para teclado e `prefers-reduced-motion` respeitado.\n'
    if anchor not in sec: raise SystemExit('Recovery hardening anchor missing')
    sec=sec.replace(anchor,'- copy pré-login não afirma atividade sem runtime: `Você confirma o que importa. O Career 360 organiza sua busca.`;\n'+anchor,1)
s=s[:start]+sec+s[end:]

# Record internal connector audit without changing product state.
if '`VERCEL_TEAM_PROJECT_COUNT=9`' not in s:
    anchor='`DEPLOY_BLOCKER=IN_CHAT_VERCEL_DEPLOY_ACTION_DOES_NOT_EXPOSE_PROJECT_ID`\n'
    if anchor not in s: raise SystemExit('Recovery deploy blocker anchor missing')
    s=s.replace(anchor,anchor+'`VERCEL_TEAM_PROJECT_COUNT=9`\n`VERCEL_PROJECT_GIT_LINK=null`\n`VERCEL_GIT_INTEGRATION_FOR_CAREER360=NOT_ACTIVE`\n',1)

last='`LAST_VERIFIED_CHANGE=V16_AUTH_RUNTIME_TRUTH_BROWSER_PASS_APP_M_719C15E_APP_L_428364_APP_K_6DF7B4_BUNDLE_4FAE7CD_SMOKE_RUN_34010192948_JOB_101424535949_AUTH_COPY_PASS_VERCEL_CHATGPT_ONLY_INTERNAL_DEPLOY_UNSCOPED_PRODUCTION_STILL_V14_NOT_PROMOTED`'
pat=r'`LAST_VERIFIED_CHANGE=[^`]+`'
if len(re.findall(pat,s))!=1: raise SystemExit('Recovery LAST_VERIFIED_CHANGE cardinality invalid')
s=re.sub(pat,last,s,count=1)
REC.write_text(s)

# Release
r=REL.read_text()
# Current source/bundle fields occur twice each; replace all current references.
if r.count(OLD_APP) < 2: raise SystemExit('Release app-m occurrences missing')
r=r.replace(OLD_APP,NEW_APP)
if r.count(OLD_BUNDLE) < 2: raise SystemExit('Release bundle occurrences missing')
r=r.replace(OLD_BUNDLE,NEW_BUNDLE)
# Update final validation only, retaining old run in audit by adding it below.
old_validation=f'''Final hardened canonical-bundle validation:\n- run `{OLD_RUN}`\n- job `{OLD_JOB}`\n- result `SUCCESS`'''
new_validation=f'''Final hardened canonical-bundle validation:\n- run `{NEW_RUN}`\n- job `{NEW_JOB}`\n- result `SUCCESS`'''
if old_validation not in r: raise SystemExit('Release final validation block missing')
r=r.replace(old_validation,new_validation,1)
if '- `V16_AUTH_TRUTHFUL_COPY_POLICY=PASS`\n' not in r:
    anchor='- `V16_TRUTHFUL_STATUS_POLICY=PASS`\n'
    if anchor not in r: raise SystemExit('Release policy evidence anchor missing')
    r=r.replace(anchor,anchor+'- `V16_AUTH_TRUTHFUL_COPY_POLICY=PASS`\n',1)
if '- `V16_AUTH_TRUTHFUL_COPY=PASS`\n' not in r:
    anchor='- `V16_TRUTHFUL_RUNTIME_DERIVATION=PASS`\n'
    if anchor not in r: raise SystemExit('Release runtime evidence anchor missing')
    r=r.replace(anchor,anchor+'- `V16_AUTH_TRUTHFUL_COPY=PASS`\n',1)
if 'Você confirma o que importa. O Career 360 organiza sua busca.' not in r:
    anchor='- agent question input has an explicit accessible label.\n'
    if anchor not in r: raise SystemExit('Release hardening anchor missing')
    r=r.replace(anchor,anchor+'- pre-login copy avoids claiming live agent activity without runtime evidence: `Você confirma o que importa. O Career 360 organiza sua busca.`\n',1)
# Add superseded final run to audit.
audit_anchor='Earlier evidence retained for audit:\n'
if f'- previous runtime-truth final run `{OLD_RUN}`, job `{OLD_JOB}`, SUCCESS before auth-copy hardening;\n' not in r:
    if audit_anchor not in r: raise SystemExit('Release audit anchor missing')
    r=r.replace(audit_anchor,audit_anchor+f'- previous runtime-truth final run `{OLD_RUN}`, job `{OLD_JOB}`, SUCCESS before auth-copy hardening;\n',1)
r=r.replace('- `app-m@3cd06d1...`','- `app-m@719c15e...`')
REL.write_text(r)
print('V16_FINAL_TRUTH_DOCS=PASS')

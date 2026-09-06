from pathlib import Path
import re

REC=Path('docs/LSI_RECOVERY_CURRENT.md')
REL=Path('career360/releases/MASTER_PILOT_1_0_CLARITY_UI_V16_2026-09-06.md')
OLD_BUNDLE='4fae7cd5b57fdf68681ac0875f006f8e158f821e'
NEW_BUNDLE='f572b824b49b2cc73d5d8389eae98391bcca63a8'
OLD_RUN='34010192948'
NEW_RUN='34010396657'
OLD_JOB='101424535949'
NEW_JOB='101425087473'

s=REC.read_text()
start=s.index('## 9A. V16 — Clarity UI / menos texto / decisão primeiro')
end=s.index('## 10. Radar / Matching',start)
sec=s[start:end]
for old,new,label in [(OLD_BUNDLE,NEW_BUNDLE,'bundle'),(OLD_RUN,NEW_RUN,'run'),(OLD_JOB,NEW_JOB,'job')]:
    if old not in sec: raise SystemExit(f'Recovery {label} missing')
    sec=sec.replace(old,new,1)
if '- `V16_STATIC_AUTH_TRUTH_SOURCE=PASS`;\n' not in sec:
    anchor='- `V16_AUTH_TRUTHFUL_COPY_POLICY=PASS`;\n'
    if anchor not in sec: raise SystemExit('Recovery static truth anchor missing')
    sec=sec.replace(anchor,anchor+'- `V16_STATIC_AUTH_TRUTH_SOURCE=PASS`;\n',1)
old_bullet='- copy pré-login não afirma atividade sem runtime: `Você confirma o que importa. O Career 360 organiza sua busca.`;'
new_bullet='- o HTML estático e a camada V16 usam a mesma copy pré-login verdadeira desde o primeiro byte: `Você confirma o que importa. O Career 360 organiza sua busca.`;'
if old_bullet in sec: sec=sec.replace(old_bullet,new_bullet,1)
elif new_bullet not in sec: raise SystemExit('Recovery auth copy bullet missing')
s=s[:start]+sec+s[end:]
pat=r'`LAST_VERIFIED_CHANGE=[^`]+`'
if len(re.findall(pat,s))!=1: raise SystemExit('Recovery last-change cardinality')
s=re.sub(pat,'`LAST_VERIFIED_CHANGE=V16_STATIC_AND_RUNTIME_TRUTH_BROWSER_PASS_APP_M_719C15E_APP_L_428364_APP_K_6DF7B4_BUNDLE_F572B82_SMOKE_RUN_34010396657_JOB_101425087473_STATIC_AUTH_SOURCE_PASS_VERCEL_CHATGPT_ONLY_INTERNAL_DEPLOY_UNSCOPED_PRODUCTION_STILL_V14_NOT_PROMOTED`',s,count=1)
REC.write_text(s)

r=REL.read_text()
if r.count(OLD_BUNDLE)<2: raise SystemExit('Release old bundle occurrences missing')
r=r.replace(OLD_BUNDLE,NEW_BUNDLE)
old_validation=f'''Final hardened canonical-bundle validation:\n- run `{OLD_RUN}`\n- job `{OLD_JOB}`\n- result `SUCCESS`'''
new_validation=f'''Final hardened canonical-bundle validation:\n- run `{NEW_RUN}`\n- job `{NEW_JOB}`\n- result `SUCCESS`'''
if old_validation not in r: raise SystemExit('Release current validation missing')
r=r.replace(old_validation,new_validation,1)
if '- `V16_STATIC_AUTH_TRUTH_SOURCE=PASS`\n' not in r:
    anchor='- `V16_AUTH_TRUTHFUL_COPY_POLICY=PASS`\n'
    if anchor not in r: raise SystemExit('Release static policy anchor missing')
    r=r.replace(anchor,anchor+'- `V16_STATIC_AUTH_TRUTH_SOURCE=PASS`\n',1)
old_bullet='- pre-login copy avoids claiming live agent activity without runtime evidence: `Você confirma o que importa. O Career 360 organiza sua busca.`'
new_bullet='- static HTML and V16 runtime use the same truthful pre-login copy from first paint: `Você confirma o que importa. O Career 360 organiza sua busca.`'
if old_bullet in r: r=r.replace(old_bullet,new_bullet,1)
elif new_bullet not in r: raise SystemExit('Release auth copy bullet missing')
audit='Earlier evidence retained for audit:\n'
entry=f'- runtime-auth-copy run `{OLD_RUN}`, job `{OLD_JOB}`, SUCCESS before static-HTML hardening;\n'
if entry not in r:
    if audit not in r: raise SystemExit('Release audit anchor missing')
    r=r.replace(audit,audit+entry,1)
REL.write_text(r)
print('V16_STATIC_TRUTH_DOCS_SEAL=PASS')

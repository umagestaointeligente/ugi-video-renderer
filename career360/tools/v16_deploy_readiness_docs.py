from pathlib import Path
import re

REC=Path('docs/LSI_RECOVERY_CURRENT.md')
REL=Path('career360/releases/MASTER_PILOT_1_0_CLARITY_UI_V16_2026-09-06.md')

OLD_DEPLOY='7aba73e550410ed111dde30007a0033935c7b0e4'
NEW_DEPLOY='bb344db78e61646926b0259c44552817149c861a'
OLD_RUN='34010396657'
NEW_RUN='34010764428'
OLD_JOB='101425087473'
NEW_JOB='101426061763'

s=REC.read_text()
s=s.replace('`CURRENT_STATUS=V14_PRODUCTION_STABLE_V15_V16_BROWSER_VALIDATED_BUNDLE_PINNED_WAITING_VERCEL_AUTH`',
            '`CURRENT_STATUS=V14_PRODUCTION_STABLE_V15_V16_BROWSER_VALIDATED_BUNDLE_PINNED_WAITING_IN_CHAT_PROJECT_SCOPED_VERCEL_MUTATION`',1)
s=s.replace('`VERCEL_PROJECT_SCOPED_DEPLOY_ROUTE=PREVIEW_PROMOTE_PIPELINE_READY_WAITING_AUTH`',
            '`VERCEL_PROJECT_SCOPED_DEPLOY_ROUTE=PREVIEW_PROMOTE_PIPELINE_READY_CHAT_CONNECTOR_MUTATION_UNSCOPED`',1)
if OLD_DEPLOY not in s:
    raise SystemExit('old deploy workflow commit missing in Recovery')
s=s.replace(OLD_DEPLOY,NEW_DEPLOY,1)

old_strategy='`VERIFY SOURCE -> BIND OFFICIAL PROJECT -> CREATE PREVIEW -> HTTP/PIN SMOKE -> PROMOTE EXACT PREVIEW -> VERIFY OFFICIAL ALIAS`.'
new_strategy='`VALIDATE SOURCE/TRUTH -> BIND OFFICIAL PROJECT -> CREATE PREVIEW -> HTTP/PIN/TRUTH SMOKE -> PROMOTE EXACT PREVIEW -> VERIFY OFFICIAL ALIAS`.'
if old_strategy not in s:
    raise SystemExit('strategy anchor missing')
s=s.replace(old_strategy,new_strategy,1)

old_workflow='''O workflow:\n- valida `app-k`, `app-l` e `app-m` antes de qualquer mutação;\n- faz syntax gate;\n- cria `.vercel/project.json` em runtime com IDs oficiais;\n- cria Preview no projeto oficial;\n- valida HTTP + pins do Preview;\n- promove exatamente esse Preview quando target=production;\n- valida o domínio oficial em até seis tentativas de convergência;\n- aborta antes de mutar a Vercel se a credencial estiver ausente.'''
new_workflow='''O workflow:\n- oferece `target=validate`, que roda os gates de readiness sem credencial e sem qualquer mutação Vercel;\n- valida `app-k`, `app-l` e `app-m` antes de qualquer mutação;\n- exige a copy estática verdadeira `Você confirma o que importa. O Career 360 organiza sua busca.` e rejeita a copy legada não comprovada;\n- faz syntax gate;\n- cria `.vercel/project.json` em runtime com IDs oficiais;\n- cria Preview no projeto oficial;\n- valida HTTP + pins + copy verdadeira do Preview e rejeita a copy legada;\n- promove exatamente esse Preview quando target=production, sem segundo build `--prod`;\n- valida o domínio oficial em até seis tentativas de convergência, incluindo pins + copy verdadeira;\n- aborta antes de mutar a Vercel se a credencial estiver ausente em `preview`/`production`.'''
if old_workflow not in s:
    raise SystemExit('workflow description anchor missing')
s=s.replace(old_workflow,new_workflow,1)

# Latest V16 validation evidence.
s=s.replace(f'- run `{OLD_RUN}`;\n- job `{OLD_JOB}`;',f'- run `{NEW_RUN}`;\n- job `{NEW_JOB}`;',1)
anchor='- `V16_STATIC_AUTH_TRUTH_SOURCE=PASS`;\n'
extra='''- `V16_LEGACY_AUTH_COPY_ABSENT=PASS`;\n- `V16_VERCEL_PROJECT_SCOPE_GATE=PASS`;\n- `V16_VERCEL_VALIDATE_ONLY_GATE=PASS`;\n- `V16_VERCEL_PREVIEW_TRUTH_SMOKE_POLICY=PASS`;\n- `V16_VERCEL_EXACT_PREVIEW_PROMOTION_POLICY=PASS`;\n'''
if extra not in s:
    if anchor not in s: raise SystemExit('Recovery evidence anchor missing')
    s=s.replace(anchor,anchor+extra,1)

last='`LAST_VERIFIED_CHANGE=V16_STATIC_RUNTIME_AND_DEPLOY_READINESS_PASS_APP_M_719C15E_APP_L_428364_APP_K_6DF7B4_BUNDLE_F572B82_SMOKE_RUN_34010764428_JOB_101426061763_VERCEL_WORKFLOW_BB344DB_PROJECT_SCOPE_VALIDATE_ONLY_PREVIEW_TRUTH_EXACT_PROMOTION_PASS_CHATGPT_CONNECTOR_MUTATION_STILL_UNSCOPED_PRODUCTION_STILL_V14_NOT_PROMOTED`'
pat=r'`LAST_VERIFIED_CHANGE=[^`]+`'
if len(re.findall(pat,s))!=1:
    raise SystemExit('Recovery LAST_VERIFIED_CHANGE cardinality invalid')
s=re.sub(pat,last,s,count=1)
REC.write_text(s)

r=REL.read_text()
old_validation=f'''Final hardened canonical-bundle validation:\n- run `{OLD_RUN}`\n- job `{OLD_JOB}`\n- result `SUCCESS`'''
new_validation=f'''Final hardened canonical-bundle + deploy-readiness validation:\n- run `{NEW_RUN}`\n- job `{NEW_JOB}`\n- result `SUCCESS`'''
if old_validation not in r:
    raise SystemExit('Release validation block missing')
r=r.replace(old_validation,new_validation,1)

anchor='- `V16_STATIC_AUTH_TRUTH_SOURCE=PASS`\n'
extra='''- `V16_LEGACY_AUTH_COPY_ABSENT=PASS`\n- `V16_VERCEL_PROJECT_SCOPE_GATE=PASS`\n- `V16_VERCEL_VALIDATE_ONLY_GATE=PASS`\n- `V16_VERCEL_PREVIEW_TRUTH_SMOKE_POLICY=PASS`\n- `V16_VERCEL_EXACT_PREVIEW_PROMOTION_POLICY=PASS`\n'''
if extra not in r:
    if anchor not in r: raise SystemExit('Release evidence anchor missing')
    r=r.replace(anchor,anchor+extra,1)

audit='Earlier evidence retained for audit:\n'
entry=f'- static/runtime truth run `{OLD_RUN}`, job `{OLD_JOB}`, SUCCESS before deploy-readiness smoke was bound to the permanent V16 workflow;\n'
if entry not in r:
    if audit not in r: raise SystemExit('Release audit anchor missing')
    r=r.replace(audit,audit+entry,1)

insert='''\n### Deployment-readiness hardening\n\nPermanent Vercel workflow:\n`.github/workflows/career360-vercel-deploy.yml`\n\nCurrent hardened workflow commit:\n`bb344db78e61646926b0259c44552817149c861a`\n\nThe permanent V16 smoke now verifies that the deploy workflow is bound to the exact official Team/Project, supports a mutation-free `validate` target, rejects the legacy unverified auth copy, checks the truthful static copy in Preview/official alias, and promotes the exact tested Preview instead of creating a second production build.\n\nThis is deployment **readiness evidence only**. It is not evidence that a Preview or Production deployment occurred.\n'''
marker='## Deployment state\n'
if insert.strip() not in r:
    if marker not in r: raise SystemExit('Release deployment marker missing')
    r=r.replace(marker,insert+'\n'+marker,1)
REL.write_text(r)
print('V16_DEPLOY_READINESS_DOCS=PASS')

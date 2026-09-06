from pathlib import Path
import re

REC=Path('docs/LSI_RECOVERY_CURRENT.md')
REL=Path('career360/releases/MASTER_PILOT_1_0_CLARITY_UI_V16_2026-09-06.md')

OLD_APP='541f962629ed5c3479972f9192401ce2fdf7c077'
NEW_APP='3cd06d176f81e07c6f4dba1f7fb962f73be4ce34'
OLD_BUNDLE='fc1d20bd73bb48ca77e9e1d522baf6196933b961'
NEW_BUNDLE='ac8a46fe5a5d3f28aab15c31c0bafd8e6558f844'
OLD_RUN='34008976104'
NEW_RUN='34009190125'
OLD_JOB='101421295169'
NEW_JOB='101421875198'
OLD_DEPLOY='85afb95087a706dc8bca5d99555740b4bc5ed0da'
NEW_DEPLOY='921fed05010b71d9a49f1a910f8c0a40ec49dc89'


def req(s,old,new,label):
    if old not in s:
        raise SystemExit(f'missing {label}: {old}')
    return s.replace(old,new)

s=REC.read_text()
s=req(s,OLD_APP,NEW_APP,'Recovery app-m')
s=req(s,OLD_BUNDLE,NEW_BUNDLE,'Recovery bundle')
s=req(s,OLD_RUN,NEW_RUN,'Recovery run')
s=req(s,OLD_JOB,NEW_JOB,'Recovery job')
if OLD_DEPLOY in s:
    s=s.replace(OLD_DEPLOY,NEW_DEPLOY)
elif NEW_DEPLOY not in s:
    raise SystemExit('Recovery deploy workflow id missing')

start=s.index('## 9A. V16 — Clarity UI / menos texto / decisão primeiro')
end=s.index('## 10. Radar / Matching',start)
sec=s[start:end]
sec=sec.replace('mutations=5','mutations=6')
if '- `V16_TRUTHFUL_RUNTIME_DERIVATION=PASS`;\n' not in sec:
    anchor='- `V16_DYNAMIC_PROACTIVE_RECOMPACT=PASS`.\n'
    if anchor not in sec:
        raise SystemExit('Recovery V16 evidence anchor missing')
    sec=sec.replace(anchor,'- `V16_DYNAMIC_PROACTIVE_RECOMPACT=PASS`;\n- `V16_TRUTHFUL_RUNTIME_DERIVATION=PASS`.\n',1)
old_status='- status proativo compactado somente a partir do texto de runtime (`Ativo`, `Atualizando`, `Pausado`, `Atenção` ou `Status`);'
new_status='- o texto legado `Agente trabalhando` da V12 não é tratado como prova de atividade em tempo real;\n- status visível derivado apenas de estado verificável: `Atualizando` quando a atualização está realmente em curso, `Atualizado` quando existe resumo real e `Aguardando` quando ainda não existe resumo;'
if old_status in sec:
    sec=sec.replace(old_status,new_status,1)
elif 'status visível derivado apenas de estado verificável' not in sec:
    raise SystemExit('Recovery truthful status description missing')
s=s[:start]+sec+s[end:]

new_last='`LAST_VERIFIED_CHANGE=V16_RUNTIME_TRUTH_BROWSER_PASS_APP_M_3CD06D1_APP_L_428364_APP_K_6DF7B4_BUNDLE_AC8A46F_SMOKE_RUN_34009190125_JOB_101421875198_TRUTH_DERIVATION_PASS_DEPLOY_GATE_921FED0_PRODUCTION_STILL_V14_NOT_PROMOTED_AUTH_REQUIRED_REMOTE_DESKTOP_PROHIBITED`'
last_pattern=r'`LAST_VERIFIED_CHANGE=[^`]+`'
if len(re.findall(last_pattern,s))!=1:
    raise SystemExit('Recovery LAST_VERIFIED_CHANGE cardinality invalid')
s=re.sub(last_pattern,new_last,s,count=1)
REC.write_text(s)

r=REL.read_text()
r=req(r,OLD_APP,NEW_APP,'Release app-m')
r=req(r,OLD_BUNDLE,NEW_BUNDLE,'Release bundle')
r=req(r,OLD_RUN,NEW_RUN,'Release run')
r=req(r,OLD_JOB,NEW_JOB,'Release job')
r=r.replace('mutations=5','mutations=6')
r=r.replace('- status is compacted from runtime-originated text; no fixed `Trabalhando` claim is injected;', '- legacy `Agente trabalhando` text is not accepted as proof of current activity; the surface derives `Atualizando`, `Atualizado` or `Aguardando` from verifiable UI/digest state;')
r=r.replace('- proactive status now compacts only runtime-originated state into `Ativo`, `Atualizando`, `Pausado`, `Atenção` or neutral `Status`;', '- legacy V12 `Agente trabalhando` is treated as non-evidence; `Atualizando` appears only while update is in progress, `Atualizado` only when a digest exists, and `Aguardando` when no digest exists yet;')
if '- `V16_TRUTHFUL_RUNTIME_DERIVATION=PASS`\n' not in r:
    anchor='- `V16_DYNAMIC_PROACTIVE_RECOMPACT=PASS`\n'
    if anchor not in r:
        raise SystemExit('Release evidence anchor missing')
    r=r.replace(anchor,anchor+'- `V16_TRUTHFUL_RUNTIME_DERIVATION=PASS`\n',1)
r=r.replace('- `app-m@541f962...`','- `app-m@3cd06d1...`')
REL.write_text(r)
print('V16_FINAL_DOCS_SEAL=PASS')

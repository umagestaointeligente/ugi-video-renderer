from pathlib import Path

p=Path('docs/LSI_RECOVERY_CURRENT.md')
s=p.read_text(encoding='utf-8')
old='`CURRENT_STATUS=V14_OFFICIAL_PRODUCTION_STABLE_V16_CLOUDFLARE_BROWSER_VALIDATED_ALTERNATIVE_DELIVERY_PROVEN_NOT_PROMOTED`'
new='`CURRENT_STATUS=V14_OFFICIAL_PRODUCTION_STABLE_V16_TESTER_ENTRYPOINT_LIVE_BROWSER_VALIDATED_PUBLIC_BETA_CLOSED`'
if old not in s and new not in s:
    raise SystemExit('CURRENT_STATUS anchor missing')
s=s.replace(old,new,1)
anchor='Frontend oficial: `https://lsi-career-360.vercel.app/`\n'
insert='Frontend oficial legado: `https://lsi-career-360.vercel.app/`\nTester entrypoint V16: `https://lsi-career-360.umagestaointeligente.workers.dev/`\n'
if insert not in s:
    if anchor not in s: raise SystemExit('frontend anchor missing')
    s=s.replace(anchor,insert,1)
gate='`MASTER_PILOT_DELIVERY=SEALED_CONTROLLABLE_SCOPE`\n'
extra='`MASTER_PILOT_DELIVERY=SEALED_CONTROLLABLE_SCOPE`\n`TESTER_ENTRYPOINT_V16=LIVE_BROWSER_VALIDATED`\n`TESTER_ENTRYPOINT_URL=https://lsi-career-360.umagestaointeligente.workers.dev/`\n`TESTER_VISUAL_RESPONSIVE=PASS_360_412_768_1180`\n`TESTER_RUNTIME_ERRORS=ZERO`\n`TESTER_APPLICATION_CONFIRMATION_UI=PASS_TRUTHFUL_NO_FALSE_SEND`\n`TESTER_PHASE=CONTROLLED_READY_PUBLIC_BETA_CLOSED`\n'
if '`TESTER_ENTRYPOINT_V16=LIVE_BROWSER_VALIDATED`' not in s:
    if gate not in s: raise SystemExit('gate anchor missing')
    s=s.replace(gate,extra,1)
doc='`career360/docs/CAREER360_DELIVERY_SEAL_2026-09-07.md`\n'
if '`career360/docs/CAREER360_TESTER_ENTRYPOINT_2026-09-07.md`' not in s:
    if doc not in s: raise SystemExit('doc anchor missing')
    s=s.replace(doc,doc+'`career360/docs/CAREER360_TESTER_ENTRYPOINT_2026-09-07.md`\n',1)
evidence='- final clean-tree Cloudflare browser smoke: run `34157515919`, job `101852301179`, 360/412/768/1180 PASS, application confirmation UI PASS, truthful no-false-send PASS, runtime errors zero, production mutation NONE;\n'
new_evidence=evidence+'- stable tester Workers deploy: run `34161107108`, job `101862969136`, SUCCESS; Worker `lsi-career-360`; version `6d7f4d9a-c523-423b-9b0b-7f1cc38b3d0a`; URL `https://lsi-career-360.umagestaointeligente.workers.dev/`;\n- stable tester browser smoke: run `34161107086`, job `101862969173`, SUCCESS; 360/412/768/1180 PASS; application confirmation UI PASS; truthful no-false-send PASS; runtime errors zero; Vercel production mutation NONE;\n- tester signup caveat: confirmation redirect source still points to legacy Vercel because hosted Supabase redirect allowlist/Site URL is not currently readable or mutable through the available connector; after confirmation, controlled testers must return to the tester entrypoint;\n'
if 'stable tester Workers deploy: run `34161107108`' not in s:
    if evidence not in s: raise SystemExit('evidence anchor missing')
    s=s.replace(evidence,new_evidence,1)
p.write_text(s,encoding='utf-8')

from pathlib import Path

p = Path('docs/LSI_RECOVERY_CURRENT.md')
s = p.read_text(encoding='utf-8')

s = s.replace('Readback oficial mais recente em 2026-09-06 BRT:', 'Readback oficial mais recente em 2026-09-07 BRT:')

anchor = '`PROACTIVE_DIGEST_TRUTH_V2=LIVE`\n'
extra = '`CAREER_PROACTIVE_STATUS_V2_CONFIRMABLE_APPLICATIONS=LIVE`\n'
if extra not in s:
    s = s.replace(anchor, anchor + extra)

anchor2 = '`APPLICATION_CONFIRMATION_AUTHENTICATED_E2E=PENDING_REAL_FRONTEND_SESSION`\n'
extra2 = (
    '`APPLICATION_CONFIRMATION_UI_V16=BROWSER_VALIDATED_CANONICAL_BUNDLE_PINNED_NOT_OFFICIAL`\n'
    '`APPLICATION_CONFIRMATION_UI_TRUTH_NO_FALSE_SEND=PASS`\n'
    '`MASTER_PILOT_DELIVERY=SEALED_CONTROLLABLE_SCOPE`\n'
)
if extra2 not in s:
    s = s.replace(anchor2, anchor2 + extra2)

anchor3 = '`CLOUDFLARE_V16_BROWSER_PRELOGIN=PASS`\n'
extra3 = '`CLOUDFLARE_V16_APPLICATION_CONFIRMATION_UI=PASS`\n'
if extra3 not in s:
    s = s.replace(anchor3, anchor3 + extra3)

anchor4 = '`career360/docs/APPLICATION_CONFIRMATION_V2_LIVE_2026-09-07.md`\n'
extra4 = '`career360/docs/CAREER360_DELIVERY_SEAL_2026-09-07.md`\n'
if extra4 not in s:
    s = s.replace(anchor4, anchor4 + extra4)

old = '- Cloudflare browser smoke: run `34084862777`, job `101626832212`, 360/412/768/1180 PASS, runtime errors zero;\n'
new = (
    old +
    '- final clean-tree Cloudflare static preview: run `34157515928`, job `101852301277`, SUCCESS;\n'
    '- final clean-tree Cloudflare browser smoke: run `34157515919`, job `101852301179`, 360/412/768/1180 PASS, application confirmation UI PASS, truthful no-false-send PASS, runtime errors zero, production mutation NONE;\n'
    '- `career-proactive-status` V2 ACTIVE, verify_jwt=true, SHA `49908165f6eb2fa44afa7bcb4515830e0eaade03339f05aff8f2f033924865dd`;\n'
    '- canonical `app-i.js` immutable pin `90a795bf1a371be66fd8f907c8a76501f8a5421c`; canonical bundle pin commit `82b49720bcf2e19e75cb44d19f64118c594e1508`;\n'
)
if 'final clean-tree Cloudflare browser smoke: run `34157515919`' not in s:
    s = s.replace(old, new)

old2 = '- official production promotion: NONE; Vercel V14 continua oficial;\n'
new2 = (
    '- official production promotion: NONE; Vercel V14 continua oficial; live readback on 2026-09-07 returned HTTP 200 with old app-i/app-k pins and old pre-login copy;\n'
    '- Vercel in-chat deploy mutation remains zero-argument `deploy_to_vercel()`; project-scoped production mutation is still unavailable and was not invoked;\n'
)
s = s.replace(old2, new2)

old3 = '- authenticated browser E2E for application confirmation = pending a real frontend session; no provider side effect.\n'
new3 = (
    '- authenticated browser E2E for application confirmation = pending a real frontend session on the official promoted bundle; no provider side effect.\n'
    '- browser-level V16 application confirmation UI contract = PASS in Cloudflare preview with synthetic authenticated backend contract; this is not a real ATS submission.\n'
    '- delivery seal = `career360/docs/CAREER360_DELIVERY_SEAL_2026-09-07.md`; controllable master-pilot scope SEALED; public Beta remains closed.\n'
)
s = s.replace(old3, new3)

p.write_text(s, encoding='utf-8')

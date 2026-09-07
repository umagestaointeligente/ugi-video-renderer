# LSI Career 360 — Tester Entrypoint — 2026-09-07

`STATE=LIVE_BROWSER_VALIDATED_TESTER_ENTRYPOINT`
`PUBLIC_BETA=NOT_OPENED`
`TESTER_ENTRYPOINT=https://lsi-career-360.umagestaointeligente.workers.dev/`

## Purpose

This URL is the stable entrypoint for the controlled tester phase of LSI Career 360. It serves the validated V16 bundle without mutating the legacy V14 Vercel production deployment.

Core rule: `RUNTIME_COMPROVADO_VENCE_DOCUMENTO`.

## Deployment evidence

Cloudflare Workers application name: `lsi-career-360`
Workers account subdomain: `umagestaointeligente`
Cloudflare custom zones discovered on the account: none (`zones=[]`).

Deployment source branch: `career360-cloudflare-preview-20260906`
Deployment source commit: `fa97aff45bf674860c00290c34030b8f9a5b2864`

Static deploy:
- run `34161107108`
- job `101862969136`
- conclusion `SUCCESS`
- Wrangler reported `Uploaded lsi-career-360`
- trigger URL `https://lsi-career-360.umagestaointeligente.workers.dev`
- Cloudflare version id `6d7f4d9a-c523-423b-9b0b-7f1cc38b3d0a`
- live HTTP V16 application-confirmation gate `PASS`

Browser smoke:
- run `34161107086`
- job `101862969173`
- conclusion `SUCCESS`
- `CLOUDFLARE_BROWSER_360=PASS`
- `CLOUDFLARE_BROWSER_412=PASS`
- `CLOUDFLARE_BROWSER_768=PASS`
- `CLOUDFLARE_BROWSER_1180=PASS`
- `CLOUDFLARE_APPLICATION_CONFIRMATION_UI=PASS`
- `CLOUDFLARE_APPLICATION_CONFIRMATION_TRUTHFUL_NO_FALSE_SEND=PASS`
- `CLOUDFLARE_V16_BROWSER_PRELOGIN=PASS`
- `CLOUDFLARE_V16_RESPONSIVE=PASS`
- `CLOUDFLARE_V16_RUNTIME_ERRORS=ZERO`
- `CLOUDFLARE_V16_PRODUCTION_MUTATION=NONE`

## Immutable V16 UI evidence

- `app-i.js` -> `90a795bf1a371be66fd8f907c8a76501f8a5421c`
- `app-k.js` -> `6df7b4e63d7e52ce3c3f02247392b98f0393cbe8`
- `app-l.js` -> `4283646143425e4a3156e44100aabb475df88d27`
- `app-m.js` -> `719c15ebfe89d212a19473b70ea6e615174601d9`

Truthful pre-login copy:
`Você confirma o que importa. O Career 360 organiza sua busca.`

## Tester safety state

This environment is suitable for controlled product testers, not public Beta.

Still fail-closed:
- `APPLICATION_PROVIDER_CONNECTOR=NOT_LIVE`
- `MAIL_DELIVERY_CONNECTOR=NOT_LIVE`
- `PUBLIC_BETA=NOT_OPENED_PRODUCT_DECISION`
- application confirmation does not mean application sent;
- no `applied` state without provider receipt;
- no mail `sent` state without delivery receipt.

## Known onboarding caveat

The frontend signup source still requests email confirmation redirect to the legacy Vercel URL. The hosted Supabase redirect allowlist / Site URL cannot be read or mutated through the currently available Supabase connector, so this setting is not represented as repaired.

For controlled testers, after confirming the email, the canonical tester entrypoint remains:
`https://lsi-career-360.umagestaointeligente.workers.dev/`

Do not claim this redirect caveat is fixed until hosted Auth configuration is proven live.

## Final tester-phase truth

`TESTER_ENTRYPOINT=LIVE`
`TESTER_VISUAL_V16=PASS`
`TESTER_RESPONSIVE=PASS_360_412_768_1180`
`TESTER_RUNTIME_ERRORS=ZERO`
`TESTER_APPLICATION_CONFIRMATION_UI=PASS_NO_FALSE_SEND`
`V14_VERCEL_LEGACY_PRODUCTION=UNCHANGED`
`PUBLIC_BETA=CLOSED`

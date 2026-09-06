# LSI CAREER 360 — MASTER PILOT 1.0 — CLARITY UI V16

Status: `BROWSER_VALIDATED_BUNDLE_PINNED_NOT_YET_PROMOTED`
Date: 2026-09-06 BRT

## Objective

Reduce cognitive load and make the Career 360 interface more pleasant and easier to operate without changing the canonical product logic.

Principle:

`LESS EXPLANATION ON THE SURFACE. MORE CLARITY IN THE NEXT ACTION.`

V16 is an incremental frontend layer over V15. It does not rebuild the product, replace V15, change matching, change privacy, or change backend contracts.

## Immutable frontend layer

File:
`career360/frontend/app-m.js`

Final immutable hardened pin:
`d3279ea45b3d3bb9f1686249199d2a46d34eaa2b`

Canonical hardened bundle commit:
`239357f0623683bae362a1dd3f122891cdd2d157`

Load order remains additive:
`... -> app-k -> app-l -> app-m`

Existing V15 pins are preserved:
- `app-k` -> `6df7b4e63d7e52ce3c3f02247392b98f0393cbe8`
- `app-l` -> `4283646143425e4a3156e44100aabb475df88d27`

## UX changes

### My Agent

The agent surface is changed from a text-heavy chat card to a compact decision-oriented surface:
- concise header;
- working-state indicator;
- short opening message;
- compact composer;
- three quick read-only questions that delegate to the existing canonical agent handler:
  - `Melhores vagas`;
  - `Preciso agir?`;
  - `Próximo passo`.

No new application, email, or profile mutation capability is introduced by these buttons.

### Home / Radar / Opportunities

Repeated explanations are shortened.

Examples:
- `Você confirma. O agente cuida do resto.`
- `Dados confirmados por você.`
- `Seu agente pesquisa e filtra.`
- `Só o que passou pelos seus filtros.`
- `Radar automático — O agente encontra e avalia. Você revisa.`

### Proactive summary

The proactive card prioritizes outcome over operating detail:
- title becomes `Seu agente`;
- active state becomes `Trabalhando`;
- cadence / last / next technical subline is removed from the primary visual surface;
- metrics stay visible;
- `Atualizar agora` becomes `Atualizar`;
- `Marcar como lido` becomes the compact action `Ok`, with accessible label preserved.

## Visual language

V16 introduces:
- softer page background;
- lighter card borders and shadows;
- cleaner radius hierarchy;
- reduced visual density;
- shorter secondary copy;
- improved chat bubble hierarchy;
- mobile horizontal quick-action chips;
- preserved mobile touch targets.

## Mobile touch hardening

A final hardening pass detected that compact visual overrides could reduce some controls below the established V15 mobile target size.

Corrected before promotion:
- agent quick actions >= 44 px;
- proactive `Atualizar` >= 44 px;
- notification `Ok` >= 44 px;
- alert padding expanded so the larger action does not collide with text.

Permanent policy:
`V16_TOUCH_TARGET_POLICY=44PX`

Hardening source commit / immutable app-m pin:
`d3279ea45b3d3bb9f1686249199d2a46d34eaa2b`

Hardened canonical bundle:
`239357f0623683bae362a1dd3f122891cdd2d157`

## Browser validation

Permanent test:
`career360/tests/v16-clarity-smoke.mjs`

Permanent workflow:
`.github/workflows/career360-v16-clarity-smoke.yml`

Final hardened canonical-bundle validation:
- run `34007281162`
- job `101416713004`
- result `SUCCESS`

Evidence:
- `V16_CANONICAL_BUNDLE_PIN_GATE=PASS`
- `V16_TOUCH_TARGET_POLICY=44PX`
- `CLARITY_360=PASS mutations=5`
- `CLARITY_412=PASS mutations=5`
- `CLARITY_768=PASS mutations=5`
- `CLARITY_1180=PASS mutations=5`
- `V16_AGENT_QUICK_ACTIONS=PASS`
- `V16_DYNAMIC_PROACTIVE_RECOMPACT=PASS`

Earlier evidence retained for audit:
- pre-bundle run `34006941241`, job `101415802373`, SUCCESS;
- first canonical-bundle run `34007073507`, job `101416159331`, SUCCESS before final 44px hardening;
- first test attempt `34006874557` failed only because the isolated harness kept the agent view hidden and therefore measured a zero-height send button. It did not mutate production.

## Safety / product boundaries

V16 does NOT:
- alter FIT or matching;
- use age, photo, or plan in matching;
- create a public profile;
- create applications;
- send email;
- claim a delivery that did not happen;
- open Beta;
- change backend schema or Edge Functions.

Quick actions remain read-oriented questions and call the existing canonical agent path.

## Deployment state

`CLARITY_UI_V16=BROWSER_VALIDATED_BUNDLE_PINNED_NOT_YET_PROMOTED`

Do not mark `LIVE` until the official production frontend is proven to load:
- `app-k@6df7b4e...`
- `app-l@4283646...`
- `app-m@d3279ea...`

and the authenticated mobile gate is completed.

`RUNTIME_COMPROVADO_VENCE_DOCUMENTO.`

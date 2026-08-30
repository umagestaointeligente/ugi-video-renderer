# UGI MASTER CONTROL PLANE V1

Status: CANONICAL
Project: UGI — Uma Gestão Inteligente
Effective: 2026-08-30

## 1. Purpose

This document is the canonical recovery and execution contract for UGI. A new ChatGPT conversation must not rely on prior chat memory or on Lola 5.3 to execute the operation. The durable source of truth is the repository + deployed Worker + Buffer readbacks + delivery receipts.

## 2. Authority chain

Human direction / ChatGPT orchestration
→ UGI Control Plane repository manifests
→ UGI Worker
→ format renderer
→ QA gates
→ novelty / anti-repeat hard gate
→ Buffer
→ Buffer readback
→ post-delivery verifier
→ durable receipt / alert

Lola 5.3 is optional. It is not an infrastructure dependency.

## 3. Current platform routes

### Instagram
- Reel: R43.8.6 video pipeline
- Carousel: R45 multiformat
- Visual single image: R45 multiformat
- Story image: R45 multiformat
- Story video/music: R45.3 scheduled media path is production-proven; embedded audio is not the same as native Instagram library music

### TikTok
- Video: R43.8.6 multi-platform video pipeline → Buffer
- Photo mode: not production-proven yet; fail closed until adapter + smoke proof exist

### YouTube
- Short: R43.8.6 multi-platform video pipeline → Buffer
- Long form: not production-proven yet; fail closed until long-form renderer/publisher smoke proof exists

## 4. State vocabulary — mandatory

Never use `published` as a synonym for `scheduled`.

- PLANNED: editorial intent exists only.
- RENDER_IN_PROGRESS: renderer accepted job and has no terminal conclusion.
- ASSET_READY: media exists and passed technical checks.
- QA_PASS: semantic/audiovisual or static QA passed.
- ANTI_REPEAT_PASS: candidate passed the recent-history novelty gate.
- ANTI_REPEAT_BLOCK_EXACT: exact repeated content/media detected.
- ANTI_REPEAT_BLOCK_NEAR: near-duplicate content/media detected.
- BUFFER_SCHEDULED: Buffer returned post id and exact requested slot by readback.
- DELIVERY_PENDING: due time reached but terminal send proof is not available yet, within grace window.
- DELIVERY_CONFIRMED: Buffer terminal readback contains sentAt or terminal sent/published state with no error.
- EXTERNAL_LINK_VERIFIED: public externalLink is returned and can be resolved externally.
- DELIVERY_LATE: due time + grace elapsed without terminal send proof.
- DELIVERY_FAILED: Buffer/platform returned terminal error/cancelled/failed state.

A user-facing statement that a post `was published` requires at least DELIVERY_CONFIRMED. Prefer EXTERNAL_LINK_VERIFIED whenever the platform returns a usable public link.

## 5. Evidence requirements

### To claim SCHEDULED
Require all:
1. Buffer create response success.
2. Buffer post id.
3. correct channel/platform.
4. exact dueAt readback.
5. readback status scheduled.
6. `ANTI_REPEAT_PASS` for video/Reel/Short publication.

### To claim PUBLISHED / DELIVERED
Require all:
1. scheduled proof exists or shareNow mutation succeeded.
2. post-delivery readback performed after due time / shareNow.
3. sentAt OR terminal sent/published status.
4. no Buffer error.
5. capture externalLink when available.

### To claim PUBLICLY VERIFIED
Require DELIVERY_CONFIRMED plus successful resolution of externalLink when available and technically fetchable.

## 6. Delivery SLA and alerting

- Delivery verifier schedule: every 10 minutes.
- Grace window: 12 minutes after dueAt.
- Before grace expires: DELIVERY_PENDING.
- After grace expires without terminal send proof: DELIVERY_LATE.
- DELIVERY_LATE or DELIVERY_FAILED must fail the verifier workflow and create/update a GitHub issue titled `UGI ALERT — publicação atrasada ou falhou` with current evidence.
- Never silently downgrade an alert to success.

Canonical verifier:
- `.github/workflows/ugi-delivery-verifier.yml`
- `scripts/ugi_delivery_verifier.py`
- evidence: `control-plane/delivery-proof/latest.json`

## 7. Publishing hubs

### Video
- `.github/workflows/ugi-publisher-hub.yml`
- `scripts/ugi_publisher_hub.py`
- `scripts/ugi_render_reconciler.py`

### Instagram multiformat
- deployed Worker R45+
- static routes under `/api/r45/*`
- repository policy/manifests under `control-plane/r45/`

## 8. Exactly-once / fail-closed rules

- Never create a second post when an active Buffer post id already exists for the same asset/platform.
- Never replace a scheduled publication merely because readback is temporarily unavailable.
- Never classify `in_progress` as `FAIL`.
- Never publish an asset that has not passed the format-specific gate.
- Never bypass semantic or copy-lock validation.
- Never bypass novelty / anti-repeat validation.
- A new CONTENT_ID does not make repeated content new.
- Re-export, crop, resize, caption, music, subtitle or CTA changes do not make an otherwise repeated video novel.
- Never claim scheduled/published without evidence from the toolchain.

## 9. Recovery bootstrap for any new chat

When the user says `Recovery UGI` or asks a new chat to assume UGI operation:

1. Open this document from `main`.
2. Read `control-plane/policies/UGI_ANTI_REPEAT_V1.md`.
3. Read `control-plane/delivery-proof/latest.json`.
4. Read current Publisher Hub status and current R45 status/receipts.
5. Check Worker health/version.
6. Check recent GitHub workflow runs.
7. Read current queue/manifests and receipts before creating any new post.
8. Reconcile overdue publications first.
9. Continue execution from durable state; do not ask the user to paste Lola 5.3 prompts unless a specific external model is explicitly desired.

## 10. Production smoke standard

A route is considered production-proven only after a real smoke test achieves:

GENERATE/RENDER
→ QA
→ ANTI_REPEAT_PASS when applicable
→ APPROVAL
→ Buffer mutation
→ Buffer readback
→ DELIVERY_CONFIRMED
→ externalLink check when available

A `SCHEDULED` smoke alone is insufficient to declare the route proven for unattended publishing.

## 11. Current strategic editorial direction

UGI 2.0 = HUMAN UTILITY FIRST.

Do not regress to a Reel-only corporate-advertising look. Use format diversity and platform-native language. Editorial strategy can evolve, but publication evidence and fail-closed rules in this document are infrastructure invariants.

## 12. Canonical novelty / anti-repeat gate

Canonical policy: `control-plane/policies/UGI_ANTI_REPEAT_V1.md`.

Default same-platform no-repeat window: **15 calendar days**.

Before any Reel/Short/video is allowed to reach Buffer, recent history must be checked for exact and near duplicates. The comparison must use content/media evidence rather than CONTENT_ID alone. When technically available, retain and compare media SHA-256, source/master asset key, renderId, normalized script hash, normalized hook, scene/footage package and recent topic/entity history.

Hard-block a candidate when a viewer would reasonably perceive it as the same video, including cases where only the caption, soundtrack, crop, subtitles, CTA, date or CONTENT_ID changed.

### Regression incident — 2026-08-30
`UGI-20260830-IG-01-CISCO-AGENTS` (Cisco / 90 mil funcionários / MyAgent) reached Instagram using a video visually identical to a recent UGI video already present in the grid. User identified the duplicate and elected to remove it manually.

Classification: `REJECTED_DUPLICATE`.

This incident proves that Buffer exactly-once and CONTENT_ID uniqueness are not sufficient novelty controls. It is now a permanent anti-repeat regression case: any future pipeline that would reproduce this condition must fail closed before Buffer mutation.

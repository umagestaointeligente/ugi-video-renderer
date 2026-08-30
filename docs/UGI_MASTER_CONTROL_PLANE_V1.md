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
- Story video/music: next R45.x extension; do not claim automatic support before terminal smoke proof

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
- Never claim scheduled/published without evidence from the toolchain.

## 9. Recovery bootstrap for any new chat

When the user says `Recovery UGI` or asks a new chat to assume UGI operation:

1. Open this document from `main`.
2. Read `control-plane/delivery-proof/latest.json`.
3. Read current Publisher Hub status and current R45 status/receipts.
4. Check Worker health/version.
5. Check recent GitHub workflow runs.
6. Read current queue/manifests and receipts before creating any new post.
7. Reconcile overdue publications first.
8. Continue execution from durable state; do not ask the user to paste Lola 5.3 prompts unless a specific external model is explicitly desired.

## 10. Production smoke standard

A route is considered production-proven only after a real smoke test achieves:

GENERATE/RENDER
→ QA
→ APPROVAL
→ Buffer mutation
→ Buffer readback
→ DELIVERY_CONFIRMED
→ externalLink check when available

A `SCHEDULED` smoke alone is insufficient to declare the route proven for unattended publishing.

## 11. Current strategic editorial direction

UGI 2.0 = HUMAN UTILITY FIRST.

Do not regress to a Reel-only corporate-advertising look. Use format diversity and platform-native language. Editorial strategy can evolve, but publication evidence and fail-closed rules in this document are infrastructure invariants.

# UGI ANTI-REPEAT POLICY V1

Status: CANONICAL / HARD GATE
Project: UGI — Uma Gestão Inteligente
Effective: 2026-08-30

## Purpose
Prevent exact or near-duplicate publication of UGI content, especially Reels/Shorts, even when a new CONTENT_ID is used.

A new identifier is never evidence of novelty.

## Default no-repeat window
Minimum window: **15 calendar days** across the same UGI brand/account.

The gate must inspect recently published, scheduled, rendered and rejected content within the window before publication.

## HARD BLOCK conditions
A candidate MUST NOT be published if any item inside the no-repeat window matches one or more of these conditions without an explicit editorial reuse exception:

1. Same final media binary SHA-256.
2. Same source/master video key, R2 key, render output, renderId or equivalent immutable asset reference.
3. Same or materially identical scene sequence / footage package.
4. Same normalized narration/script hash or substantially identical narration.
5. Same first-frame/thumbnail perceptual fingerprint or near-identical visual opening combined with the same thesis.
6. Same topic + hook + core argument + visual treatment such that a viewer would reasonably perceive it as the same post.
7. Re-export, crop, resize, subtitle change, music change, caption change, CTA change or new CONTENT_ID applied to an otherwise repeated video. These changes DO NOT create novelty.

## Topic reuse inside 15 days
A topic may be revisited only when the new asset is materially different in at least three dimensions:
- new editorial thesis or question;
- new hook;
- materially new script;
- materially new footage/scene package;
- new data/case/event;
- different content format with a distinct information payload;
- different practical application/CTA.

If the only changes are wording, soundtrack, crop, subtitles, background, opening card or CTA, classify as DUPLICATE/NEAR_DUPLICATE and block.

## Required pre-publication evidence
Before any UGI Reel/Short/video publication, the Control Plane must produce an anti-repeat result:

- `ANTI_REPEAT_PASS`
- `ANTI_REPEAT_BLOCK_EXACT`
- `ANTI_REPEAT_BLOCK_NEAR`
- `ANTI_REPEAT_REVIEW_REQUIRED`

`ANTI_REPEAT_PASS` is required before Buffer scheduling/shareNow.

Minimum evidence to retain when technically available:
- CONTENT_ID
- media SHA-256
- source/master asset key
- renderId
- normalized script hash
- normalized hook
- topic/entity labels
- recent comparison window
- closest prior CONTENT_ID / publication
- similarity reasons
- decision

Fail closed when recent-history comparison is unavailable or incomplete for video publication.

## Cross-platform rule
Publishing the same master intentionally on a different platform as part of a coordinated same-day multi-platform release is not automatically a duplicate. However:
- it must be an intentional platform adaptation;
- the Control Plane must link the assets as one campaign family;
- it must not be reintroduced to the SAME platform inside 15 days as if it were new.

## Incident test case — 2026-08-30
Incident: Instagram Reel scheduled as `UGI-20260830-IG-01-CISCO-AGENTS` / theme "90 mil funcionários / Cisco MyAgent" was published with a video visually identical to a recent UGI video already present in the Instagram grid.

Classification: `REJECTED_DUPLICATE`.

Operational lesson:
- CONTENT_ID uniqueness and Buffer exactly-once protection were insufficient;
- the failure was editorial/media novelty, not duplicate API submission;
- future gates must compare the content and asset history, not only identifiers/slots.

This incident MUST remain a regression test. A candidate that recreates this condition must fail before Buffer mutation.

## User-facing rule
Never call a repeated video "new content" merely because it has a new date, caption, CONTENT_ID, soundtrack or schedule slot.

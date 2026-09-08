# ORBIT / VSA — Você Sabia Agora? — Canonical Production V1

Status: **CANONICAL_ACTIVE**  
Recovery: `RECOVERY::ORBIT::VSA::CANONICAL_V1`

This is the authoritative production runbook for VSA. It supersedes older VSA audiovisual instructions when they conflict, while preserving historical evidence. It does **not** modify Cena Certa.

## 1. Mandatory activation order
1. Resolve target channel. It must be explicitly VSA / Você Sabia Agora?.
2. Read `canonical/vsa/CURRENT.json`.
3. Read `canonical/vsa/v1/VSA_CANONICAL_PRODUCTION_CONTRACT_V1.json` and `canonical/vsa/v1/VSA_EDITORIAL_GUARDRAILS_V2.json`.
4. Read `canonical/vsa/v1/VSA_TOPIC_LEDGER_60D.json`.
5. Run `python ops/vsa-runtime/runtime.py preflight --channel vsa`.
6. Before approving a topic, assign `content_id`, `semantic_topic_id` and `publish_date_local` and run the semantic topic gate (`runtime.py check-topic ...`).
7. If target is ambiguous, Cena Certa, a repeat is blocked, rights are unknown, or a VSA publishing account cannot be verified, STOP with a gate. Never guess.

## 2. Immutable visual identity
The mask and CTA are fixed reusable assets. Do not generate a fresh mask or CTA for each video.

Mask source of truth: `/VSA/Canonical Assets/VSA_MASK_CANONICAL_V1.png` in ChatGPT Library. SHA-256: `9f6ebae6742b007b1e660cd401b610933d0a06c2c3fee240220abf7215e1a4d9`. Native asset: 864×1536.

CTA source of truth: `/VSA/Canonical Assets/VSA_CTA_VISUAL_CANONICAL_V1.png` in ChatGPT Library. SHA-256: `6c064a533784f2c09b594095646aa538e07f77955ed348656c60e5d2795fa5a8`. Native asset: 864×1536.

Only title, subtitle and closed-caption text vary. The underlying layout, logo, palette, frame, footer and CTA composition stay fixed.

Reference geometry on the 864×1536 asset: video window x=42, y=352, w=780, h=676; CC zone approximately x=34, y=1084, w=796, h=145; footer branding begins around y=1245. Final 1080×1920 output scales these coordinates proportionally.

The mask is applied only **after the clean/base video has passed QA**. The mask serves the content; content must not be mutilated to fit the mask. Do not zoom aggressively. When an aspect-ratio mismatch exists, prefer contain/blur-background treatment so the subject and explanatory labels remain visible.

## 3. Visual grammar
Core rule: **NARRAÇÃO = IMAGEM = AÇÃO VISUAL = SIGNIFICADO**.

If narration says a charge rises, the viewer must see it rise. If cells react, the viewer must see the cells, the disturbance and the reaction. A merely related image is not enough.

Use real footage first for observable phenomena, people, places, animals, weather, machinery, historical events and experiments. Animation is for invisible/internal/abstract mechanisms: electricity, molecules, cells, forces, trajectories, cross-sections, microscopic scales, maps, comparisons and data.

Preferred grammar: real hook → causal explanation → different real evidence → causal explanation → consequence/proof → payoff → CTA. Do not force the formula when the story needs a different flow, but preserve semantic correspondence and visual momentum.

First frame must show the anomaly/action immediately, ideally inside 0–1.5 s. Never open with logo, static title card, avatar, still image or generic intro animation.

## 4. Movement and rhythm
Do not reduce benchmark language to “fast cuts”. The screen stays alive because meaningful events happen inside the shot. An explanatory shot may last 3–5 s or more only when multiple internal events occur: reveal, camera movement, deformation, causal propagation, particles, labels/tracking, state change, scale transition or consequence.

Historical benchmark guidance puts median shot duration roughly in the 2.5–4.7 s family. This is guidance, not a rigid cut timer. Preserve motion continuity and information density; do not create frantic cuts just to hit a number.

Never repeat the same real footage accidentally within one video. A deliberate editorial callback must be explicitly justified; convenience reuse is FAIL.

### 4A. 60-day semantic topic lock
The live ledger is `canonical/vsa/v1/VSA_TOPIC_LEDGER_60D.json`. It contains published topics and already-scheduled topics so a future queue cannot repeat itself before publication.

A topic is blocked when its `semantic_topic_id` represents the same central question or mechanism used inside the previous 60 days. A broad subject overlap alone is not an automatic block: for example, lightning formation and damage inside a tree are related subjects but different central mechanisms; humanoid locomotion and military interest in human-compatible form factor are likewise separate mechanisms.

A blocked semantic topic may pass only as `BREAKING_EXCEPTION` when a materially new event changes the story. The runtime requires `repeat_exception=true`, `repeat_exception_reason`, `new_event_source` and `new_event_date`. Performance or convenience is never enough.

The deterministic gate is enforced by `ops/vsa-runtime/runtime.py`; `validate-job` must fail closed with `BLOCK_TOPIC_REPEAT` when the same semantic topic remains inside the window.

### 4B. People / bio-curiosity
VSA may cover living or deceased people when the curiosity is factual, scientific, historical, technological or human. If the person is the subject, the visual story must show the **actual person** using rights-safe footage/photo/archive; journalists, presenters, actors, stock people or unrelated human B-roll cannot substitute for them.

Animation may explain disease, physiology, technology, mechanism, context or cause while the real person remains visually anchored. For medical/health topics, separate documented fact from inference and never diagnose beyond reliable public evidence. `PERSON_PROFILE` requires `person_visual_reference_gate=PASS` before release.

## 5. Tool routing
Use a hybrid system, not one generator for everything.
- Real footage: rights-safe real sources and source-specific ingest.
- Remotion: canonical timeline/composition layer and reusable components.
- GSAP + SVG/Canvas: easing, reveals, tracking labels and scientific motion graphics.
- Three.js/WebGL: spatial mechanisms, 2.5D/3D, virtual camera and scale changes.
- Blender procedural/PBR: selected high-fidelity 3D mechanisms or golden masters where WebGL is insufficient.
- FFmpeg: trim/transcode/audio/concat/subtitles/final encoding/technical QA. Do not use FFmpeg as the main motion-design engine.
- OpenCV/dense frame sampling: visual QA.
- AI video generation: selective only; never substitute observable real footage merely because generation is easier.
- Paid credits/subscriptions: BLOCK unless Paulo explicitly authorizes them.

Reusable golden components should be parameterized rather than recreated: MAP_ZOOM, GLOBE_TO_LOCATION, OBJECT_EXPLODE, CROSS_SECTION, PARTICLE_FLOW, CAUSE_EFFECT_CHAIN, SCALE_COMPARE, TIMELINE, DATA_COUNTER, CAMERA_FLYTHROUGH, MICROSCOPIC_ZOOM, X_RAY_REVEAL, ROUTE_ANIMATION, LABEL_TRACK and PROGRESSIVE_HIGHLIGHT.

## 6. Format/audio/CC
Master: 1080×1920, 9:16, 30 fps, H.264 High, yuv420p. Typical Shorts length is 60–90 s; up to 120 s is allowed when the story earns it.

Narration: male, young adult, natural PT-BR, neutral, never robotic or advertising-style. Music has no vocals and must fit the subject. Target mix is approximately -16 LUFS with true peak ≤ -1.5 dBTP.

Closed captions: max two lines, synchronized, discreet and legible. CC must remain in the designated caption band and must never cover critical explanatory information.

## 7. Ending
The narrative must first pay off the opening question with the exact phrase: **“Agora você já sabe.”**

Then the fixed CTA card closes with: **“Curta, compartilhe e siga o Você Sabia Agora.”** The fixed CTA lasts approximately 3–4.5 seconds.

## 8. Hard visual fails
FAIL: slideshow; static photo plus zoom pretending to be animation; generic B-roll unrelated to the spoken sentence; decorative animation; gratuitous flashes; black screen; prolonged freeze; repeated footage by convenience; excessive use of one visual family; meaningless movement; flashy transitions without narrative purpose; text replacing a visual explanation; talking avatar; animated-PowerPoint look.

## 9. QA and autocorrection
The user must not be the first QA pass. Production loop:
`BASE RENDER → TECH QA → DENSE VISUAL QA → BENCHMARK COMPARISON → AUTO-CORRECT → MASK → FINAL QA → RELEASE`.

Default dense visual sampling is 4 Hz (one state every 250 ms). Never call this “frame-by-frame” unless actual frames were individually inspected. Classify discoveries as OBSERVED, INFERRED or UNKNOWN.

Check black/freeze/flash/silence/clipping, semantic narration-image correspondence, crop/safe-area, caption collisions, duplicate footage, internal motion, CTA order and final technical spec. If any critical gate fails, make V2/V3 internally and do not send/schedule the failed version.

Anti-regression: KEEP validated strengths; CHANGE only the bottleneck; FORBID reintroducing a rejected defect. If a change removes more validated strengths than it adds, do not render it.

The current “machine learning” behavior is persistent correction history + deterministic QA gates + reusable components. Do not claim a trained ML model unless an actual training pipeline exists.

## 10. Rights and publication
Every real footage asset needs provenance/reuse evidence in a rights manifest before publication. An official source is not automatically permission to reuse. Unknown rights = publication BLOCK.

Current verified primary route: **Upload-Post** profile `voce-sabia-agora` → YouTube `Você Sabia Agora?` / `@vocesabiaagoraoficial`, with live readback required before each write. Post Bridge YouTube account id `88527` is historical/fallback only while its `create_post` route remains HTTP 500; do not blind-retry it. Current Metricool brand is `Cena Certa Ofc`; therefore Metricool is **forbidden for VSA** until a VSA brand is independently verified.

No `SCHEDULED`, `POSTED` or `PUBLISHED` claim is allowed without a real receipt. `SCHEDULED` requires the job in the current scheduler state; `PUBLISHED` requires the platform ID or public URL.

## 11. Isolation from Cena Certa
VSA writes only to VSA paths/assets/output prefixes and VSA social accounts. Never write to `canonical/cena-certa/`, `ops/cena-certa-runtime/`, Cena Certa social account id 88240, or Cena Certa Ofc id 88242. An ambiguous instruction such as “post the video” without resolved project target must fail closed.

Run `python ops/vsa-runtime/test_isolation.py` after canonical changes. Current suite `VSA_ISOLATION_V3` verifies channel/account/path isolation, semantic-ledger blocking, breaking-exception manifest enforcement and the `PERSON_PROFILE` real-person gate. A PASS does not authorize publication by itself.

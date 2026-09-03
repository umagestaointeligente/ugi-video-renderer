# UGI ANTI-REPEAT POLICY V1

Status: CANONICAL / HARD GATE
Project: UGI — Uma Gestão Inteligente
Effective: 2026-08-30
Updated: 2026-09-02 — PER-PLATFORM TOPIC COOLDOWN

## Purpose
Prevent exact/near-duplicate media AND editorial topic fatigue.

A new CONTENT_ID, caption, format, soundtrack or date is never evidence of novelty.

The policy has two independent protections:
1. MEDIA/ASSET DUPLICATION GATE;
2. SAME-PLATFORM TOPIC COOLDOWN GATE.

Both must pass before publisher mutation.

## 1. Media/asset duplicate window
Minimum comparison window: **15 calendar days**.

The asset gate may inspect published, scheduled, rendered and rejected content because an unpublished render can still reveal an accidental media reuse.

### HARD BLOCK — media duplication
A candidate MUST NOT be published when one or more of these conditions match without a valid explicit exception:
1. same final media binary SHA-256;
2. same source/master video key, R2 key, render output, renderId or equivalent immutable asset reference;
3. same or materially identical scene sequence / footage package;
4. same normalized narration/script hash or substantially identical narration;
5. same first-frame/thumbnail perceptual fingerprint or near-identical visual opening combined with the same thesis;
6. same topic + hook + core argument + visual treatment such that a viewer would reasonably perceive it as the same post;
7. re-export, crop, resize, subtitle change, music change, caption change, CTA change or new CONTENT_ID applied to an otherwise repeated asset.

Cosmetic changes DO NOT create novelty.

## 2. Same-platform topic cooldown — CANONICAL
Default editorial cooldown: **15 calendar days PER PLATFORM/NETWORK**.

Platform scope is independent:
- Instagram history blocks Instagram only;
- TikTok history blocks TikTok only;
- YouTube history blocks YouTube only;
- LinkedIn history blocks LinkedIn only when that channel becomes active;
- any future UGI network maintains its own history.

A topic used on TikTok does NOT automatically block a genuinely platform-native Instagram or YouTube version. Cross-platform reuse still requires adaptation, factual QA and platform fit.

### What counts as a same-platform topic occurrence
All public-facing formats on the same network share the same topical cooldown:
- Story;
- Reel;
- static feed post;
- carousel/document;
- TikTok video;
- YouTube Short/video;
- any equivalent future format.

A Story therefore counts. Publishing a Story about a subject and then returning to substantially the same subject a few days later on that same network is a topical repeat even if the second asset is a carousel or Reel.

### Topic identity
The Control Plane must normalize each candidate into, at minimum:
- `platform`;
- `topicKey`;
- `primaryEntities`;
- `eventOrCase`;
- `managementThesis`;
- `format`;
- `publicationDate` / dueAt;
- `CONTENT_ID` when available.

Topic matching must be semantic, not filename-only. Examples:
- `Apple + Tim Cook + John Ternus + CEO succession` is one topic cluster;
- changing the hook from succession to legacy does not automatically make it new;
- `Uber + restructuring + management layers` is one topic cluster;
- a completely different Uber development may be a different event, but inside the cooldown still requires the extraordinary-repeat gate when the same company/event cluster would feel repetitive to the audience.

## 3. Default same-platform topic decision
If the same topic/entity-event cluster appeared on the SAME platform within the prior 15 days and is scheduled/published/delivered or otherwise known to have been presented to that platform audience:

`ANTI_REPEAT_BLOCK_TOPIC_15D`

Default action: discard the candidate and select the next strongest eligible topic from the trend/general radar.

Do not lower the trend standard merely to fill a slot.

If history is ambiguous or incomplete and there is credible evidence the subject may have recently appeared on that same platform:

`ANTI_REPEAT_HISTORY_REVIEW_REQUIRED`

Fail closed until the platform history can be reconciled, or choose another topic with clean history.

## 4. Extraordinary repeat exception
A same-platform topic inside 15 days may be revisited ONLY when a genuinely extraordinary new development makes silence editorially worse than repetition.

Required state:
`EDITORIAL_REPEAT_EXCEPTION_BREAKING`

ALL conditions are required:
1. a material new event occurred AFTER the prior publication;
2. the new event has exceptional public/platform demand, breaking significance or direct material impact;
3. the new information changes what the audience needs to know — it is not another article about the same ongoing story;
4. the new asset has a materially different management thesis/application;
5. the new asset differs in at least three dimensions among hook, script, data/event, visual package, format/information payload, practical application/CTA;
6. prior same-platform CONTENT_ID/topic occurrence is explicitly referenced in the exception record;
7. exception rationale is durable in the Control Plane before render/publication;
8. fact/source/visual/reputation QA still passes.

High raw views alone do not qualify.
A minor update, quote, rumor, analyst reaction, cosmetic angle change or new headline does not qualify.

## 5. Cross-platform rule
The cooldown is per platform.

The same real-world subject MAY appear on another UGI network inside 15 days when:
- that second platform independently has editorial/native fit;
- the content is adapted to that platform rather than mechanically copied;
- the platform's own 15-day history is clean;
- the candidate passes all normal trend, fact, rights and QA gates.

Native-trend cross-post rules remain governed by Trend Gate V2.3; this policy does not create automatic cross-post permission.

## 6. Durable platform-topic history
Canonical registry:
`control-plane/anti-repeat/platform-topic-history.json`

The registry is an index, not the sole source of truth. Before editorial lock, reconcile it against available durable evidence:
- publisher receipts/readback;
- scheduled manifests;
- platform publication receipts;
- editorial manifests/assets;
- content commands and render state when needed for media duplicate comparison.

Every newly scheduled/published UGI item must append/update a platform-topic history record.

Minimum record fields:
- `platform`;
- `topicKey`;
- `primaryEntities`;
- `eventOrCase`;
- `managementThesis`;
- `format`;
- `contentId`;
- `dueAt` or publication timestamp;
- `state`;
- `evidenceRef`;
- `cooldownUntil`;
- `repeatException` when applicable.

## 7. Required trend-engine sequence
Before a trend candidate can become an editorial slot:

`DISCOVER -> FACT CHECK -> NORMALIZE TOPIC -> SAME-PLATFORM 15D HISTORY LOOKUP -> ANTI-REPEAT DECISION -> SCORE/ALLOCATE -> SCRIPT -> QA -> PUBLISHER`

A high trend score never bypasses the cooldown gate.

Stories are included in the history lookup.

## 8. Required anti-repeat result states
The Control Plane may return:
- `ANTI_REPEAT_PASS`;
- `ANTI_REPEAT_BLOCK_EXACT`;
- `ANTI_REPEAT_BLOCK_NEAR`;
- `ANTI_REPEAT_BLOCK_TOPIC_15D`;
- `ANTI_REPEAT_HISTORY_REVIEW_REQUIRED`;
- `EDITORIAL_REPEAT_EXCEPTION_BREAKING`;
- `ANTI_REPEAT_REVIEW_REQUIRED`.

A normal candidate requires `ANTI_REPEAT_PASS` before Buffer scheduling/shareNow.

## 9. Minimum evidence to retain
When technically available:
- CONTENT_ID;
- platform/network;
- topicKey/entity labels;
- prior same-platform occurrence(s);
- dueAt/sentAt/publication state;
- media SHA-256;
- source/master asset key;
- renderId;
- normalized script hash;
- normalized hook;
- closest prior CONTENT_ID/publication;
- similarity reasons;
- decision;
- exception rationale if any.

Fail closed when same-platform topical history is materially incomplete and a credible repeat risk exists.

## 10. Regression cases
### 2026-08-30 — Instagram duplicate media
Instagram Reel `UGI-20260830-IG-01-CISCO-AGENTS` / Cisco MyAgent reached the grid with a video visually identical to a recent UGI video.
Classification: `REJECTED_DUPLICATE`.

### 2026-09-01 -> 2026-09-03 — Apple succession topical collision
Instagram 2026-09-01 contains Story `UGI-20260901-IG-STORY-04-APPLE` and carousel `UGI-20260901-IG-CAROUSEL-APPLE-SUCCESSION` about Tim Cook -> John Ternus / succession.
A proposed Instagram Apple succession carousel for 2026-09-03 is therefore a canonical test case for:
`ANTI_REPEAT_BLOCK_TOPIC_15D`.

The fact that a new article or a slightly different succession angle exists does not make the 2026-09-03 candidate eligible absent an extraordinary new development.

## User-facing rule
Never call repeated content "new" merely because it has a new date, caption, CONTENT_ID, soundtrack, format or schedule slot.
Never claim a topic is safe until same-platform 15-day history has been checked.
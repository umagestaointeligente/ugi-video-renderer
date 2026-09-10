# UGI ANTI-REPEAT POLICY V2

Status: CANONICAL / HARD GATE
Project: UGI — Uma Gestão Inteligente
Effective: 2026-09-09
Supersedes: `control-plane/policies/UGI_ANTI_REPEAT_V1.md` for all new editorial selection and publisher mutations.

## Purpose
Prevent editorial fatigue and accidental duplication across the UGI social ecosystem.

A new network, date, caption, soundtrack, format, CONTENT_ID, crop, CTA or visual treatment is never by itself evidence of novelty.

## 1. Global editorial cooldown
Default topic cooldown: **60 calendar days GLOBAL across Instagram, TikTok and LinkedIn**.

The three active editorial networks share one semantic topic history:
- an Instagram occurrence blocks the same normalized topic on Instagram, TikTok and LinkedIn for 60 days;
- a TikTok occurrence blocks the same normalized topic on TikTok, Instagram and LinkedIn for 60 days;
- a LinkedIn occurrence blocks the same normalized topic on LinkedIn, Instagram and TikTok for 60 days.

YouTube remains outside the active distribution scope while paused, but its preserved history must be consulted when a candidate creates a credible repeat risk.

## 2. All formats count
All public-facing formats participate in the same 60-day history, including Story, Reel, static feed post, carousel/document, TikTok video, LinkedIn post/video/document and equivalent future formats.

A Story counts as a topic occurrence. Changing Story to Reel, Instagram to TikTok, or feed to LinkedIn does not reset the clock.

## 3. Semantic identity
Topic matching is semantic, not filename-only and not keyword-only. Normalize at minimum:
- `topicKey`;
- `primaryEntities`;
- `eventOrCase`;
- `managementThesis`;
- `hook`;
- `platform` and `format`;
- `publicationDate` / `dueAt`;
- `CONTENT_ID` when available.

A candidate is considered a repeat when the same entity-event/topic cluster and substantially the same audience learning would reasonably feel like the same story, even with a different headline or network.

A broad category alone does not create a collision: two distinct companies can both illustrate governance if their event/case and audience learning are materially different. Conversely, changing the company name is not enough when the candidate merely repeats an identical generic thesis with no new substantive case.

## 4. Same-day cross-network duplication
By default, the same normalized topic MUST NOT occupy more than one of Instagram, TikTok or LinkedIn on the same day. Each network receives its own subject, not merely a reformatted version of another network's post.

## 5. 60-day decision
If a candidate matches a known occurrence in any of Instagram, TikTok or LinkedIn within the previous 60 calendar days:

`ANTI_REPEAT_BLOCK_TOPIC_60D`

Default action: discard the candidate and select the next strongest clean topic.

Do not lower editorial quality to fill a slot.

If history is incomplete or ambiguous and there is credible repeat risk:

`ANTI_REPEAT_HISTORY_REVIEW_REQUIRED`

Fail closed or select another topic with clean evidence.

## 6. Extraordinary-news exception
A topic inside the 60-day window may be revisited only when a genuinely extraordinary new development makes silence editorially worse than repetition.

Required state: `EDITORIAL_REPEAT_EXCEPTION_BREAKING`.

ALL conditions are mandatory:
1. a material new event occurred after the prior UGI occurrence;
2. the development has exceptional public/platform demand, breaking significance or direct material impact;
3. the new information changes what the audience needs to know and is not a minor update, reaction, rumor or cosmetic new headline;
4. the management thesis/application is materially different from the prior piece;
5. the new asset differs in at least three dimensions among hook, script, data/event, visual package, format/information payload and practical application/CTA;
6. every relevant prior occurrence is referenced in a durable exception record;
7. the exception rationale is stored in the Control Plane before render/publication;
8. normal fact, rights, visual, caption, audio and reputation QA still pass.

High raw views alone never qualify.

## 7. Media/asset duplication
The media/asset comparison window is also **60 days** for new UGI content. Hard-block same SHA-256, source/master, materially identical footage/scene sequence, substantially identical script/narration, near-identical opening with same thesis, or cosmetic re-export of prior media unless a valid extraordinary exception exists.

## 8. Durable history and reconciliation
Legacy registry: `control-plane/anti-repeat/platform-topic-history.json`.

Canonical global rule: this V2 policy. The legacy registry is an index/input, not the sole source of truth. Before editorial lock, reconcile at least:
- publisher receipts/readbacks;
- scheduled manifests;
- editorial plans/manifests/assets;
- content commands and render state;
- known user-confirmed deletions/duplicates;
- available Library/handoff evidence when the durable registry is incomplete.

Every newly scheduled/published item must update durable topic history with a 60-day cooldown date and source evidence.

## 9. Required flow
`DISCOVER -> FACT CHECK -> NORMALIZE TOPIC -> GLOBAL 60D HISTORY LOOKUP -> CROSS-NETWORK DEDUP -> ANTI-REPEAT DECISION -> SCORE/ALLOCATE -> SCRIPT -> FINAL ASSET QA -> HUMAN APPROVAL -> PUBLISHER -> READBACK -> HISTORY UPDATE`

A trend score never bypasses this gate.

## 10. Allowed result states
- `ANTI_REPEAT_PASS`
- `ANTI_REPEAT_BLOCK_EXACT`
- `ANTI_REPEAT_BLOCK_NEAR`
- `ANTI_REPEAT_BLOCK_TOPIC_60D`
- `ANTI_REPEAT_HISTORY_REVIEW_REQUIRED`
- `EDITORIAL_REPEAT_EXCEPTION_BREAKING`
- `ANTI_REPEAT_REVIEW_REQUIRED`

A normal candidate requires `ANTI_REPEAT_PASS` before any Buffer mutation.

## User-facing rule
Never call content new merely because it changed date, caption, CONTENT_ID, soundtrack, format or network. Never claim a topic is safe until the global 60-day history has been reconciled. If there is credible uncertainty, fail closed or choose another clean topic.

# UGI VISUAL + AUDIO QA V1

Status: CANONICAL / HARD GATE
Project: UGI — Uma Gestão Inteligente
Effective: 2026-08-31
Last quality amendment: 2026-09-02

## Purpose
Prevent recurrence of defects observed in UGI Instagram production, including silent Stories, polluted lower thirds, malformed background text and weak information hierarchy.

## Visual hard blocks
A UGI asset MUST NOT be scheduled or published when any of the following is present:
- pseudo-Latin, pseudo-Italian, gibberish or any unintended language in visible artwork;
- AI-generated ghost text, background typography or corrupted letterforms;
- clipped, overlapping or truncated copy;
- a visually polluted lower third that competes with the primary message;
- multiple competing text layers in the bottom zone;
- important copy positioned inside unsafe mobile UI/footer areas;
- illegible decorative text;
- body copy too dense for comfortable mobile reading;
- factual/news creative missing a practical source attribution when the underlying source can reasonably be shown;
- duplicated feed publication in the same editorial window;
- carousel slide that has not passed individual QA.

### Production default
For informational Stories and carousels, use deterministic controlled typography and backgrounds. Generated imagery may be used only when it contains NO generated text. All visible copy must be overlaid by the UGI renderer, not synthesized inside the background image.

Preferred UGI look:
- clean;
- executive;
- modern;
- elegant;
- high contrast;
- strong hierarchy;
- generous negative space;
- cyan accent on dark navy/neutral background;
- no text texture behind the main copy;
- curiosity-led headline;
- concise context;
- clean lower third;
- discreet trustworthy source line on factual content.

### Lower-third pass criteria
A lower third passes only when:
- it performs one primary function: question, short CTA or source line;
- the final question/CTA has breathing room;
- no ghost typography or oversized decorative words compete behind it;
- source attribution, if present, is small but readable;
- the bottom area is visually quieter than the headline area.

## Music hard blocks
Forbidden:
- 8-bit / chiptune;
- game-like or Mario-like melodic patterns;
- polyphonic-ringtone aesthetic;
- repetitive beep/tone beds;
- metallic or synthetic noise beds;
- synthetic test tones presented as music;
- inaudible soundtrack when music is required;
- abrupt music stop before the end frame;
- silent UGI Story without a documented exception.

Required for Stories:
- every UGI Story must carry approved audio/music unless an explicit documented exception was approved before production;
- real music track with a documented usage license;
- different track per Story inside the same day unless an explicit campaign motif is approved;
- music must match the emotional intent of the subject: executive tension, urgency, transformation, curiosity, momentum or action;
- modern production aesthetic;
- audio embedded in the MP4 when the publishing API cannot attach native Instagram music reliably;
- music audibility validated on ordinary phone-speaker playback;
- CTA/end frame must retain audio; no silent tail.

### Story audio evidence
Before Buffer mutation, require when applicable:
- asset container = MP4;
- audio stream present;
- audio codec recognized;
- audio duration covers the intended Story duration;
- music title/source/license recorded;
- normal-speaker audibility check = PASS;
- narration intelligibility check = PASS when narration exists;
- end-frame audio continuity = PASS.

Any missing mandatory Story-audio evidence = `AUDIO_QA_FAIL`.

## Feed collision gate
- One feed publication owns one editorial slot.
- Minimum default spacing between feed publications: 60 minutes.
- If a feed post already exists for a slot/family, creating another Buffer post for the same slot is blocked unless the prior post is proven cancelled/deleted before publication.
- Recovery must reuse the existing Buffer post id whenever possible; recovery must not create a second feed post merely to retry asset generation.

## QA evidence
Before Buffer mutation, retain when applicable:
- dimensions;
- file size;
- slide count;
- visual copy source = controlled renderer;
- intended language = pt-BR;
- lower-third cleanliness result;
- source attribution result for factual/news creative;
- music title/source/license;
- audio codec/duration validation;
- phone-speaker audibility validation;
- end-frame audio continuity;
- feed collision check;
- anti-repeat result for video.

Any hard-block finding = QA_FAIL and publication must fail closed.

## Regression incidents
1. 2026-08-30 — Story music sounded like an old videogame/polyphonic ringtone. Classification: AUDIO_QA_FAIL.
2. 2026-08-30 — Several Story/carousel backgrounds showed malformed ghost text / non-Portuguese-looking strings. Classification: VISUAL_QA_FAIL.
3. 2026-08-30 — Two carousels reached the Instagram feed roughly ten minutes apart. Classification: FEED_COLLISION_FAIL.
4. 2026-08-30 — A Reel repeated a recent video. Covered separately by `UGI_ANTI_REPEAT_V1.md`.
5. 2026-09-02 — Published UGI Stories were observed without music. Classification: AUDIO_QA_REGRESSION. Permanent guard: Story silence is blocked unless a documented exception exists.
6. 2026-09-02 — Lower-third visual density was judged too polluted despite generally modern art direction. Permanent guard: lower-third cleanliness criteria above.
7. 2026-09-02 — Factual Story copy needs stronger curiosity framing and visible trustworthy sourcing to improve authority. Permanent guard: curiosity-led headline + source-attribution checks.

These incidents remain permanent regression cases.

# UGI VISUAL + AUDIO QA V1

Status: CANONICAL / HARD GATE
Project: UGI — Uma Gestão Inteligente
Effective: 2026-08-31

## Purpose
Prevent recurrence of the defects observed in the Instagram production tests of 2026-08-30.

## Visual hard blocks
A UGI asset MUST NOT be scheduled or published when any of the following is present:
- pseudo-Latin, pseudo-Italian, gibberish or any unintended language in visible artwork;
- AI-generated ghost text, background typography or corrupted letterforms;
- clipped, overlapping or truncated copy;
- a visually polluted lower third that competes with the primary message;
- illegible decorative text;
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
- no text texture behind the main copy.

## Music hard blocks
Forbidden:
- 8-bit / chiptune;
- game-like or Mario-like melodic patterns;
- polyphonic-ringtone aesthetic;
- repetitive beep/tone beds;
- synthetic test tones presented as music;
- inaudible soundtrack when music is required.

Required:
- real music track with a documented usage license;
- different track per Story inside the same day unless an explicit campaign motif is approved;
- music must match the emotional intent of the subject: executive tension, urgency, transformation, curiosity, momentum or action;
- modern production aesthetic;
- audio embedded in the MP4 when the publishing API cannot attach native Instagram music.

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
- music title/source/license;
- audio codec/duration validation;
- feed collision check;
- anti-repeat result for video.

Any hard-block finding = QA_FAIL and publication must fail closed.

## Regression incidents — 2026-08-30
1. Story music sounded like an old videogame/polyphonic ringtone. Classification: AUDIO_QA_FAIL.
2. Several Story/carousel backgrounds showed malformed ghost text / non-Portuguese-looking strings. Classification: VISUAL_QA_FAIL.
3. Two carousels reached the Instagram feed roughly ten minutes apart. Classification: FEED_COLLISION_FAIL.
4. A Reel repeated a recent video. Covered separately by `UGI_ANTI_REPEAT_V1.md`.

These incidents remain permanent regression cases.

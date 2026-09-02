# UGI Editorial — 2026-09-03

Timezone: America/Sao_Paulo
Status: PREPARED_QUALITY_LOCK / TOPICS_PENDING_NATIVE_TREND_READBACK

## Editorial thesis
World event/news -> verified context -> curiosity-led hook -> management implication -> practical takeaway -> UGI bridge.

## 2026-09-03 quality correction lock

This editorial inherits all canonical UGI policies and adds the following mandatory regression corrections from 2026-09-02.

### 1. Story audio = mandatory
- Every UGI Story must publish with approved music/audio unless an explicit documented exception is approved before production.
- Default autonomous asset = MP4 with music embedded when the publishing API cannot reliably attach native Instagram music.
- Silent Story = `AUDIO_QA_FAIL`.
- Validate audio stream, duration, codec, normal phone-speaker audibility and end-frame continuity before publisher mutation.
- No silent tail on CTA/end frame.
- Use different tracks across unrelated Stories in the same day unless an explicit campaign motif is approved.
- Music must fit the story emotionally and progress musically; no chiptune, ringtone, beep, metallic noise or flat single-tone loop.

### 2. Cleaner lower third
- Lower third has one primary function only: final question, short CTA or discreet source line.
- No ghost text, oversized decorative typography or repeated phrases behind body copy.
- Preserve generous breathing space around the final question/CTA.
- Keep important copy outside unsafe mobile bottom UI zones.
- If lower-third density competes with the headline, redesign before QA.

### 3. Better copy: curiosity + authority
For factual/news content:
- lead with curiosity, tension, contradiction, consequence or a strong verified number;
- avoid dead corporate statements;
- keep one main idea per Story;
- body copy must be shorter and easier to read on mobile;
- management implication must be explicit but concise;
- trustworthy source attribution must be visible in the creative whenever practical;
- use only sources actually consulted and verified.

Preferred pattern:
`CURIOSITY HOOK -> VERIFIED FACT -> WHY IT MATTERS -> MANAGEMENT READING -> QUESTION`

Examples of tone:
- `O número chama atenção. O gargalo está em outro lugar.`
- `Parece tecnologia. Na prática, é uma decisão de gestão.`
- `A empresa fez X. O detalhe mais importante está no mecanismo.`
- `O que mudou — e por que isso importa para quem decide?`

### 4. Source presentation
Preferred:
- discreet top or lower source line: `Fonte: Reuters`, `Fonte: Banco Central`, `Fonte: NASA`, etc.;
- if multiple sources materially support the claim: `Fontes: X + Y`;
- source line must remain readable but visually secondary to the headline;
- no invented prestige sourcing.

### 5. Visual standard
Preferred UGI look:
- clean;
- executive;
- modern;
- elegant;
- high contrast;
- contextual real-world imagery when the fact is real;
- strong information hierarchy;
- generous negative space;
- no generated text inside background images;
- all copy overlaid by controlled renderer;
- no slide-deck feel.

## Instagram agenda generation rule for 2026-09-03
Final topics and slots are NOT frozen from the prior day.
Before locking the agenda:
1. run current world/business/technology/management/AI radar;
2. run Instagram-native demand radar;
3. verify facts and sources;
4. score UGI fit, freshness, visual potential and anti-repeat;
5. choose format per topic: Story / Reel / carousel / static;
6. apply this quality lock before render;
7. run factual + visual + audio + brand + duplication QA;
8. only then mutate Buffer;
9. require `bufferPostId + exact dueAt + scheduled-state readback` before calling any slot SCHEDULED.

## Story pre-publish checklist
Every Story must have:
- `HOOK_CURIOSITY_PASS`
- `FACT_SOURCE_PASS`
- `SOURCE_VISIBLE_PASS` when factual/news-based
- `MOBILE_COPY_DENSITY_PASS`
- `LOWER_THIRD_CLEAN_PASS`
- `CONTEXTUAL_VISUAL_PASS`
- `AUDIO_STREAM_PRESENT_PASS`
- `MUSIC_FIT_PASS`
- `PHONE_SPEAKER_AUDIBILITY_PASS`
- `END_FRAME_AUDIO_CONTINUITY_PASS`
- `BRAND_QA_PASS`
- `DUPLICATION_QA_PASS`

Any failure = fail closed before Buffer mutation.

## Feed / carousel rule
- Carousels remain silent by default until continuous native carousel audio is proven end-to-end through the autonomous route.
- Reels must carry approved audio.
- Static posts do not require audio.
- Source attribution and lower-third cleanliness rules still apply to factual static/feed creatives.

## Tomorrow's editorial status
Topics: PENDING_CURRENT_TREND_READBACK
Assets: NOT_RENDERED
QA: NOT_RUN
Buffer: NOT_SCHEDULED
Delivery: NOT_APPLICABLE

No state may be promoted without real evidence.

# UGI Editorial — 2026-09-03

Timezone: America/Sao_Paulo
Status: TREND_DRAFT_V2_15D_COOLDOWN_APPLIED / MORNING_REVALIDATION_REQUIRED / NOT_SCHEDULED

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

Named-subject lock:
- if content is about a named real person, the named subject must appear clearly on the cover/opening frame when rights-cleared/editorially permitted imagery is available;
- no generic AI-generated executive may substitute for a named person;
- use official/press/licensed/editorially permitted imagery and fail closed if rights cannot be cleared.

## NEW CANONICAL GATE — same-platform 15-day topic cooldown
Before scoring/final selection, every candidate must be normalized and checked against:
`control-plane/anti-repeat/platform-topic-history.json`
plus durable publisher/manifests/receipts.

Rules:
- 15 calendar days per platform/network;
- Story, Reel, carousel and static share one Instagram topic history;
- same topic on another platform does not automatically block the candidate;
- a high trend score cannot bypass the cooldown;
- ambiguous historical risk = choose another clean candidate or fail closed;
- extraordinary repeat requires `EDITORIAL_REPEAT_EXCEPTION_BREAKING` under `UGI_ANTI_REPEAT_V1.md`.

### Confirmed collision — Apple / succession / Instagram
Instagram 2026-09-01 manifest contains:
- `UGI-20260901-IG-STORY-04-APPLE`;
- `UGI-20260901-IG-CAROUSEL-APPLE-SUCCESSION`.

Therefore the proposed 2026-09-03 Instagram Apple succession carousel is:
`ANTI_REPEAT_BLOCK_TOPIC_15D`.

Apple/Tim Cook/John Ternus succession is removed from the 2026-09-03 Instagram plan. No extraordinary-repeat exception is justified by the current evidence.

### Ambiguous collision — Uber
The user recalls recent UGI coverage of Uber, but current durable search has not yet resolved the platform. Until platform history is backfilled:
`ANTI_REPEAT_HISTORY_REVIEW_REQUIRED`.

Uber is removed from the 2026-09-03 core agenda and Stories rather than risking an avoidable repeat.

## Trend Gate V2.3 readback — captured 2026-09-02 evening BRT
Canonical allocation remains: per platform, target one `PLATFORM_NATIVE` core item + one `GENERAL/WORLD` core item when both pass score, factual and same-platform-history gates. Native topics are not cross-posted by default.

## INSTAGRAM

### Native signal — candidate retained
Public Instagram trend monitor surfaced `New season`, but direct management fit is weak; it remains rejected as trend chasing.

A stronger platform-relevant subject is Instagram transparency around AI-generated profiles and recommendation eligibility. It has natural UGI fit around AI governance, trust, disclosure and distribution. Do NOT describe it as an exact Instagram-wide trend rank unless a native ranked signal is actually observed.

#### 12:45 — Reel — Instagram AI-profile transparency / distribution governance
Class: `INSTAGRAM_NATIVE_PLATFORM_SIGNAL`
History gate: provisional clean; must rerun morning 15d lookup.
Hook direction:
**O Instagram pode reduzir seu alcance por causa de IA — e o detalhe mais importante não é o algoritmo.**
Management angle: when AI enters production, transparency becomes part of distribution and brand governance.
Visual: real Instagram/platform context + controlled UGI overlays; no fake profile/person presented as a real case.
Audio: mandatory approved Reel music, audibly mixed.
Source direction: Meta/Instagram + reputable technology reporting.

### General/world replacement — EU deforestation rule / coffee supply chains
Reuters reported on 2026-09-02 that the EU deforestation regulation can push compliance beyond coffee actually sold into the EU because maintaining separate compliant/non-compliant supply chains may be more expensive than applying one standard broadly.

This is selected as the replacement for Apple because it is current, highly visual, relevant to Brazil and has a clean management mechanism: **a rule in one market can redesign the operating standard of an entire supply chain.**

#### 19:15 — Carousel — Coffee / EUDR / compliance spillover
Class: `GENERAL_WORLD`
History gate: no repo match found in current search; morning 15d lookup still mandatory.
Headline:
**Uma regra europeia pode mudar até o café que nunca será vendido na Europa.**

Carousel logic — 7 slides:
1. COVER — real coffee/export visual + headline. Minimal copy.
2. FACT — the EU rule requires traceability to prove products do not originate from recently deforested land.
3. TENSION — companies serving multiple markets face the cost/complexity of separating supply chains.
4. MECHANISM — when separation is expensive, one demanding market can become the operating standard for the whole chain.
5. MANAGEMENT — compliance stops being legal back-office work and becomes sourcing, data, supplier and process architecture.
6. PRACTICAL TEST — Can you trace origin? Which supplier data is missing? What process would have to split by destination? What is the cost of two operating standards?
7. UGI — neutral UGI-only close: **Regulação distante pode virar processo local. O gestor precisa enxergar antes.**

Visual lock:
- real coffee farm/export/logistics/contextual imagery;
- Brazil-relevant imagery when factually appropriate;
- no generic AI executive;
- generous negative space;
- no polluted lower third;
- source line discreet and visible;
- no generated text inside imagery.

Sources: Reuters 2026-09-02 + source study/official EU material when verified in morning QA.

### Instagram Stories support layer
All Stories: MP4 + embedded approved music + visible source + clean lower third + one main idea. No Apple succession or Uber tomorrow.

Provisional history-clean subjects:
- 09:00 — Google ad-tech antitrust: **Google não foi dividido. Mas a decisão ainda muda como ele pode competir.** Management angle: structural remedy vs behavioral controls; rules can change operating freedom even without breakup. Source: Reuters 2026-09-02. Same-platform history must be checked; prior Google use on another network does not automatically block Instagram.
- 11:00 — BP board governance: **Quando a empresa troca líderes em sequência, o problema deixa de ser só quem ocupa a cadeira.** Management angle: governance stability, board focus and strategic continuity. Source: Reuters 2026-09-02. Avoid generic succession copy.
- 14:15 — Bonds/oil/cost of capital: **O petróleo sobe longe da sua empresa. O custo pode chegar no seu caixa.** Management angle: rates/capital cost as operating variables. Source: Reuters 2026-09-02.
- 17:15 — RESERVED_FRESH_HISTORY_CLEAN_TOPIC — select from morning native/world radar only after 15d Instagram history lookup.
- 21:00 — RESERVED_FRESH_HISTORY_CLEAN_TOPIC — one practical UGI Story chosen after morning scan; no generic repeat of a recent Story theme merely to fill volume.

Do not create a Story teaser for the 19:15 carousel if that simply repeats the same topic on the same platform. The feed asset must stand on its own.

## TIKTOK

### Native candidate — Anitta / portfolio-distribution signal
TikTok Creative Center remains primary. The public dynamic surface did not expose a reliable Brazil ranked board in this readback, so no exact Creative Center BR rank is claimed.

A Brazil public trend proxy showed a strong concentration of Anitta tracks. Treat this as `EVIDENCED_PROXY`, not an official TikTok rank.

#### 19:45 — TikTok — Anitta / portfolio-distribution
Class: `TIKTOK_NATIVE_EVIDENCED_PROXY`
History gate: provisional clean; morning TikTok 15d lookup mandatory.
Hook:
**Quando várias músicas do mesmo projeto começam a aparecer juntas no radar, o que existe por trás: hit ou arquitetura de portfólio?**
Management angle: portfolio, collaborations, frequency, distribution, cultural adjacency and compounding attention.
Rights: do NOT use copyrighted Anitta music unless a platform-native licensed route is proven.
Source direction: demand proxy + Universal Music/official project information.

### General candidate — Anthropic retail agents
#### 12:15 — TikTok — Anthropic retail agents / AI in commerce
Class: `GENERAL_WORLD`
History gate: provisional clean; morning TikTok 15d lookup mandatory.
Hook:
**A IA está deixando de só responder perguntas — ela já começa a montar o carrinho. O que muda para quem vende?**
Management angle: AI moving from employee assistance into customer journey and commercial decision flow.
Source: Reuters + primary sources cited/verified during QA.

## YOUTUBE SHORTS

### Native candidate — Harry Potter / legacy brand relaunch
Current Brazil YouTube trend evidence on 2026-09-02 showed the new Harry Potter/HBO teaser near the top with additional Harry Potter reaction/trailer entries in the same current list. vidIQ was attempted but returned `NOT_ENOUGH_CREDITS`; no credits were purchased.

#### 16:30 — Short — Harry Potter / relaunching a legacy brand
Class: `YOUTUBE_NATIVE_EVIDENCED_PROXY_HIGH`
History gate: provisional clean; morning YouTube 15d lookup mandatory.
Length: 45–55s.
Hook:
**Harry Potter voltou ao topo da conversa. O desafio da HBO não é só refazer uma história — é mexer numa marca que milhões já consideram sua.**
Management angle: legacy brand equity, familiarity vs novelty, relaunch architecture and creation of a new growth cycle.
Visual: official/press/editorially permitted Harry Potter/HBO context only; no long copyrighted excerpts.
Source direction: current Brazil YouTube demand proxy + official Wizarding World/HBO.

### General replacement — OpenAI / automated shutdown / autonomy limits
Reuters reported on 2026-09-02 that OpenAI told lawmakers it is developing automated shutdown capabilities for AI systems, alongside tighter monitoring and access controls following a safety-test incident involving an autonomous agent.

This replaces Uber while Uber platform history remains ambiguous.

#### 20:30 — Short — OpenAI / stop conditions for autonomous systems
Class: `GENERAL_WORLD`
History gate: no YouTube-specific match found in current repo search; morning 15d lookup mandatory. A prior OpenAI-related TikTok item does not automatically block YouTube under the per-platform rule.
Length: 45–60s.
Hook:
**A OpenAI está construindo uma forma de desligar agentes automaticamente. Para gestão, a pergunta é anterior: quem decide quando uma IA precisa parar?**

Management structure:
1. factual hook — automated shutdown capability under development;
2. context — autonomous tools can take multi-step actions with limited supervision;
3. management mechanism — autonomy without stop conditions turns efficiency into uncontrolled exposure;
4. practical framework — define permission ceiling, monitored actions, escalation trigger, human owner and stop condition BEFORE deployment;
5. payoff — **autonomia boa não é autonomia sem limite; é autonomia com fronteira clara.**

Visual: real OpenAI/AI-agent/security/governance context where rights-cleared; no fabricated incident visualization presented as footage.
Source: Reuters 2026-09-02 + primary OpenAI material if available/verified during factual QA.

## Cross-platform / 15-day dedup decisions
Retained:
- Instagram native: AI-generated profile transparency / distribution governance.
- Instagram general: EU deforestation rule / coffee supply-chain operating standard.
- TikTok native: Anitta portfolio/distribution proxy.
- TikTok general: Anthropic retail agents.
- YouTube native: Harry Potter legacy-brand relaunch.
- YouTube general: OpenAI automated shutdown / autonomy limits.

Blocked/held:
- `Apple succession -> Instagram`: `ANTI_REPEAT_BLOCK_TOPIC_15D` due 2026-09-01 Story + carousel.
- `Uber -> any proposed 2026-09-03 slot`: `ANTI_REPEAT_HISTORY_REVIEW_REQUIRED` until historical platform is resolved.
- Dell/HPE AI infrastructure -> Instagram: recent 2026-09-02 topical collision.
- GTA VI -> YouTube: recent 2026-09-02 topical collision.
- US Open -> Instagram: recent 2026-09-02 topical collision.
- Instagram `New season`: management fit too weak; trend chasing blocked.

## Morning revalidation gate — mandatory before render
At the first production window on 2026-09-03:
1. rerun 24h general radar;
2. rerun TikTok Creative Center/native signals;
3. rerun YouTube native/current Brazil proxy; retry vidIQ only if existing credits are available with zero incremental cost;
4. rerun Instagram native trend/proxy;
5. reconcile `platform-topic-history.json` with receipts/manifests for the prior 15 days;
6. normalize every candidate into platform + topicKey + entities + event/case + management thesis;
7. run SAME-PLATFORM 15D HISTORY LOOKUP INCLUDING STORIES;
8. discard normal repeats and take the next strongest clean candidate;
9. use extraordinary exception only under `EDITORIAL_REPEAT_EXCEPTION_BREAKING` with durable rationale;
10. recompute scores/freshness;
11. check breaking-news displacement;
12. render only after source/fact/visual/music rights QA;
13. Buffer mutation only after assets + QA;
14. SCHEDULED requires provider ID + exact dueAt + scheduled readback.

## Story pre-publish checklist
Every Story must have:
- `HOOK_CURIOSITY_PASS`
- `FACT_SOURCE_PASS`
- `SOURCE_VISIBLE_PASS` when factual/news-based
- `SAME_PLATFORM_TOPIC_15D_PASS`
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
- Recommended Instagram mix remains **Reel + carousel; no static feed post** for 2026-09-03 unless morning evidence materially changes the decision.
- Carousels remain silent by default until continuous native carousel audio is proven end-to-end through the autonomous route.
- Reels must carry approved audio.
- Static posts do not require audio.
- Source attribution and lower-third cleanliness rules apply to all factual creatives.

## Current execution state
Topics: PROPOSED_V2_AFTER_15D_COOLDOWN
Assets: NOT_RENDERED
QA: NOT_RUN
Buffer: NOT_SCHEDULED
Delivery: NOT_APPLICABLE

No state may be promoted without real evidence.

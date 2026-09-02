# UGI Platform Trend Intelligence V1

Status: **CANONICAL PRE-EDITORIAL GATE**  
Effective: **2026-09-02**

## Purpose

UGI editorial must combine two different demand layers before closing the daily agenda:

1. **GENERAL DEMAND** — what is materially relevant in the world, business, economy, technology, leadership and management.
2. **PLATFORM-NATIVE DEMAND** — what users are actively searching, watching or discussing inside TikTok, YouTube and Instagram.

The platform-native layer is not permission to chase any viral topic. A topic is eligible only when demand, factual confidence, visual strength and a natural UGI/management angle coexist.

Core equation:

`GENERAL SIGNAL + PLATFORM SIGNAL + NATURAL UGI FIT + VERIFIED FACTS + ORIGINAL INTERPRETATION = EDITORIAL CANDIDATE`

## Pre-editorial sequence

Before `EDITORIAL_LOCK`, execute:

`GENERAL RADAR -> TIKTOK NATIVE -> YOUTUBE NATIVE -> INSTAGRAM NATIVE/PROXY -> CROSS-CORROBORATION -> DEDUP -> SCORE -> ALLOCATION -> FACT CHECK -> EDITORIAL LOCK`

If a native source is unavailable, record `PLATFORM_SIGNAL_UNAVAILABLE` with evidence and use an evidenced proxy. Never convert proxy data into a fake native ranking.

## 1. General radar

Scan current high-signal events across business, economy, technology, AI, leadership, strategy, governance, operations and relevant general news.

The general radar supplies a platform-neutral pool. It does not determine format by itself.

Prefer current events with:
- recognizable real-world anchor;
- strong factual evidence;
- clear consequence or tension;
- usable contextual visuals;
- practical management implication.

## 2. TikTok native radar

Primary signals:
- TikTok Creative Center Trends;
- native Inspiration/topic signals when available;
- trending hashtags;
- trending videos;
- trending songs/keywords;
- regional popularity and trendline.

Default region: Brazil when the target audience is Brazilian.

The TikTok-native slot should be participation-first: fast hook, real visual, fact/context before management lesson, and an opinionable question or useful action at the end.

## 3. YouTube native radar

Primary source: **YouTube Studio Trends/Research** when available.

Useful signals include:
- Top searches;
- Breakout videos;
- Watched on YouTube;
- Searched on YouTube;
- audience interest;
- Content gaps for Shorts.

This layer is especially valuable because it can show not only what is popular, but what the channel's audience is searching for and where viewers are not finding enough strong Shorts.

Optional connected keyword/trending-video intelligence may enrich the scan only when the UGI zero-incremental-cost rule is preserved. No paid credit/top-up becomes a hard dependency.

## 4. Instagram native radar

Instagram provides native trend surfaces around Reels, including trending audio and, when surfaced to the account/region, trending topics and hashtags.

Unlike TikTok Creative Center and YouTube Studio Trends, Instagram does not provide UGI with a dependable public backend-wide ranked trend feed. Therefore this leg has two confidence states:

- `DIRECT_NATIVE` — trend observed directly in an Instagram native trend surface;
- `EVIDENCED_PROXY` — trend inferred from Reels/Explore observations, audio usage, public engagement velocity and cross-source corroboration.

Never label an evidenced proxy as an exact Instagram-wide ranking.

## 5. Daily editorial allocation

When a platform has two core publication slots, target:

- **Slot A — GENERAL/MARKET:** a strong topic selected from the global/general radar;
- **Slot B — PLATFORM-NATIVE:** a topic selected because that specific platform is showing active demand.

Examples:
- TikTok: global management/news topic + TikTok-native trend.
- YouTube Shorts: global management/news topic + YouTube search/breakout/content-gap topic.
- Instagram feed/Reels: global management/news topic + Instagram-native/proxy trend.

Instagram Stories remain a supporting layer and may branch into market news, practical management, curiosities, navigation to feed pieces and UGI conversion. They do not need to obey the two-core-post split rigidly.

## 6. Platform exclusivity and dedup

Default rule:

**A platform-native trend belongs to that platform first.**

Do not take a TikTok-native topic and automatically copy it to Instagram and YouTube. The same applies in reverse.

Cross-platform reuse is allowed only when:
1. the topic independently qualifies as a native signal on the second platform; or
2. it is a major global event chosen from the GENERAL layer, not merely copied because it trended elsewhere.

Even when the factual anchor is shared, packaging, hook, duration, narrative and CTA must be native to each platform.

## 7. Selection score

Score 0–100:
- platform demand/velocity: 25;
- natural management/UGI fit: 20;
- factual confidence: 15;
- visual strength: 10;
- freshness: 10;
- audience relevance: 10;
- share/save/comment potential: 5;
- novelty vs last 30 days: 5.

Minimum default eligibility: **70/100**.

High raw volume cannot rescue a weak or artificial management connection.

## 8. Algorithm hypothesis — important correction

Platform-native demand can increase the probability that a piece starts with stronger relevance because UGI is entering an existing attention stream. It does **not** guarantee distribution.

After the initial match, the platform still judges signals such as retention, completion, rewatches, satisfaction, shares, comments, saves, profile visits and originality.

Therefore the operating hypothesis is:

`TREND FIT -> BETTER INITIAL DEMAND MATCH -> RETENTION/PROPAGATION TEST -> POSSIBLE SECOND DISTRIBUTION WAVE`

Not:

`TREND -> GUARANTEED REACH`

UGI must add original interpretation, not reproduce the trend.

## 9. Measurement loop

Tag every selected item as one of:
- `GENERAL`;
- `TIKTOK_NATIVE`;
- `YOUTUBE_NATIVE`;
- `INSTAGRAM_NATIVE`.

Compare cohorts on:
- retention in first 1–3 seconds;
- completion;
- rewatch when available;
- profile visits per 100 views;
- follows per 100 views;
- comments per 100 views;
- shares per 100 views;
- saves per 100 views when available;
- total distribution.

The purpose is to learn whether native demand materially improves UGI's funnel:

`VIEW -> RETENTION -> PROFILE -> FOLLOW / COMMENT / SHARE / SAVE -> OTHER UGI CONTENT -> CONVERSION`

## 10. Durable evidence

Every daily pre-editorial scan should persist a snapshot under:

`control-plane/trend-intelligence/YYYY-MM-DD.json`

Required evidence:
- capture timestamp;
- region;
- general signals considered;
- TikTok signals;
- YouTube signals;
- Instagram signals and confidence state;
- source/evidence for each signal;
- score;
- selected topic per slot;
- cross-platform dedup decision;
- fact-verification status.

No daily trend claim becomes durable truth without source and timestamp.

## 11. Safety / non-regression

This intelligence layer changes **selection before production**, not publication truth.

Preserve:
- Buffer/publication rules and delivery receipts;
- already scheduled/proven posts;
- anti-repeat gates;
- factual verification;
- contextual visual requirements;
- platform-specific packaging;
- zero incremental cost unless explicitly authorized;
- no `SCHEDULED` without publisher ID + dueAt + scheduled readback;
- no `PUBLISHED` without terminal delivery evidence.

## Source capability notes

- TikTok Creative Center is an official public/free trend surface with filtering and trend analytics.
- YouTube Studio Trends/Research provides search and audience demand signals, breakout videos and Shorts content gaps; availability can vary by country/language/device and Studio rollout.
- Instagram exposes Reels trend signals such as trending audio/topics/hashtags, but automation must distinguish direct-native evidence from proxy evidence.

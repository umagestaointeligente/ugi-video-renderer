# UGI Growth Engine V2

Status: **PILOT OVERLAY**  
Effective pilot date: **2026-08-27**

## Purpose

Add a retention/distribution learning layer to UGI without replacing stable production components. V2 is additive and reversible.

## Non-regression contract

Preserve unchanged:
- Cloudflare Worker stable runtime;
- `render-video.yml` production renderer;
- UGI Publisher Hub;
- Buffer as exclusive publisher;
- Metricool as analytics-only;
- existing queues, receipts, drafts, R2 assets and content IDs;
- `config/ugi/growth-policy.json` (V1);
- every Buffer post already scheduled/proven.

V2 files MUST NOT delete or overwrite V1 solely to activate a pilot.

## Baseline diagnosis (21–25 Aug 2026)

Observed channel data indicates that distribution tests are happening, but most content does not earn a second distribution wave.

Main findings:
1. First seconds are too abstract/corporate.
2. Visual identity is consistent but overly repetitive across the feed.
3. Content often looks like a consulting presentation adapted to vertical video instead of feed-native storytelling.
4. Commercial CTA appears too frequently for a newborn audience.
5. The same editorial treatment is used across TikTok, Reels and Shorts.
6. Operational success (`published`) is not enough; V2 also asks whether the content earned continued distribution.

## Creative V2 structure

Target initial duration: **10–18 s**.

- 0.0–1.0 s: conflict/question/consequence/visual anomaly.
- 1.0–3.0 s: increase tension; do not resolve everything.
- 3.0–10.0 s: concrete example, mini-story or rule.
- 10.0–15.0 s: payoff/solution.
- last 1–2 s: simple behavior CTA.

No intro, logo animation or institutional setup before the hook.

Target perceptible visual change every **0.7–1.5 s** using cuts, reframing, movement, text, object emphasis or scene changes.

## Creative families

1. Expensive mistake / consequence.
2. What would you do?
3. Looks right, but is wrong.
4. 10–15 second manager test.
5. Corporate mini-story.

## Platform adaptation

- TikTok: rawer, faster, provocative, participation-first.
- Instagram Reels: save/share-first, strong grid frame.
- YouTube Shorts: curiosity + story + payoff, with series potential.

The idea may be shared across platforms; the editorial product does not need to be identical.

## Commercial mix during recovery

Initial mix: **80% value / 20% commercial**. Products stay active; commercial posts are not removed. Organic recovery pilots use behavior CTA instead of purchase CTA unless commerce is essential to the idea.

## Learning states

- `NO_SIGNAL`: sample insufficient.
- `KILL`: sufficient initial test + weak retention + no propagation signal.
- `RETEST`: idea promising, packaging/hook weak.
- `SCALE`: materially beats recent channel median and shows stronger retention/propagation.

Thresholds are provisional and must be calibrated from UGI's own data, not treated as universal algorithm rules.

## Pilot safety

`UGI-GROWTH-V2-PILOT-*` is render-only by default:
- no Buffer mutation;
- no queue insertion;
- no automatic publication;
- no checkout/payment;
- unique content/render IDs;
- V1 remains rollback path.

## Pilot #001

Theme: AI governance / sensitive data.  
Hook: **"ELE ACABOU DE ENVIAR ISSO PARA UMA IA."**  
Support: `SALÁRIOS_2026.xlsx`  
Second beat: **"PODIA?"**  
Rules: sensitive data / human review / accountable owner.  
Payoff: **"IA RÁPIDA SEM REGRA = RISCO MAIS RÁPIDO."**  
CTA: **"Salve antes de liberar IA no time."**

This pilot is designed to be understood without audio and to use PT-BR neutral narration when audio is enabled.

---

# Canonical Editorial Engine — UGI Management Intelligence

Effective: **2026-09-01**  
Benchmark inspiration: premium business/editorial storytelling such as G4, translated into an original UGI system. Benchmark means learning structure and attention mechanics, never copying branding, wording, layout or endorsements.

## Core positioning

UGI should not behave like a page of generic management quotes. Its editorial territory is:

**Interpret what is happening in the world through management, leadership and AI — and transform that interpretation into something a manager can apply.**

Every strong editorial candidate should follow the chain:

`TREND / FACT / PERSON / COMPANY → TENSION → MANAGEMENT READING → PRACTICAL LESSON → UGI NEXT STEP`

## Four permanent editorial motors

### 1. REAL STORY → MANAGEMENT
Use a real CEO, founder, CFO, company, crisis, strategic decision or relevant public event as the entry point.

The person/company provides context and attention; UGI provides the interpretation.

Examples of eligible angles:
- succession;
- crisis response;
- strategic pivot;
- governance failure;
- acquisition or partnership;
- cultural change;
- AI adoption;
- margin/productivity decision;
- reputation or trust crisis.

### 2. EXECUTIVE DILEMMA
Turn management tension into a decision the audience can mentally answer.

Examples:
- centralize or delegate?
- promote from within or hire outside?
- grow or protect margin?
- speed or governance?
- automate or redesign the process first?

Priority signals: comments, saves and shares.

### 3. FACT / NUMBER → CONSEQUENCE
Prefer concrete numbers, time windows or consequences when they are verified and meaningful.

Pattern:
`large factual signal → human/operational consequence → management question`

Example pattern: `14 minutes → 900+ students evacuated → what would your organization do with 14 minutes?`

### 4. UGI TOOL / FRAMEWORK
Once the audience understands the problem, connect it to a real practical next step:
- framework;
- checklist;
- playbook;
- decision matrix;
- leadership material;
- AI/governance material.

Commercial CTA must follow value delivery, not interrupt it.

## Selection score for daily trend radar

For each candidate trend, score 0–5 on:
1. **recognizable real-world anchor** — known person, company, event or verifiable fact;
2. **visual strength** — can the fact be understood visually without generic stock art?;
3. **management tension** — is there a real decision/problem?;
4. **practical takeaway** — can UGI teach something actionable?;
5. **share/save potential** — would a manager send or save this?;
6. **UGI bridge** — is there a natural route to a relevant UGI material or framework?;
7. **freshness** — does timing improve relevance?;
8. **platform fit** — is there a clear best format/channel?

Prefer candidates with strong total score rather than forcing daily repetition of one topic family.

## Visual truth and contextual relevance

Hard rule: **real subject = visually related asset**.

- Real person: use the correct person consistently.
- Real company: use recognizable, relevant company context, logo, product, facility, executive or official setting when legally/editorially appropriate.
- Real event: show the location, aftermath, object, building, operation, map, rescue infrastructure or another directly related visual.
- If minors are involved in a sensitive event, avoid depicting identifiable/distressed children; show the environment, aftermath, adult responders, staff, infrastructure or non-identifiable contextual evidence instead.
- Abstract editorial art is reserved for abstract concepts such as "AI does not create value alone", not for a factual case that has a concrete visual anchor.

Generic corporate executive + dark overlay is not an acceptable substitute for a real case when contextual visuals are available.

## Public-figure continuity and endorsement safety

When a carousel/story centers on a real public figure:
- keep the same person throughout the editorial part;
- different angles/crops are allowed, identity swaps are not;
- do not fabricate quotes;
- distinguish verified quotes from UGI interpretation;
- final commercial CTA must not use the public figure as if endorsing UGI;
- penultimate slide may transition to a neutral/environmental visual;
- final CTA is UGI-only.

## Hook rules

Prefer conflict, contrast, consequence or curiosity over topic labels.

Weak:
- "Como melhorar sua liderança"

Strong:
- "Controle demais não escala."
- "O líder muda. O sistema precisa ficar."
- "14 minutos mudaram o desfecho."
- "Ter IA não significa gerar resultado."

The first screen/frame should create a reason to continue before explaining everything.

## Storytelling structure for carousels

Default 7-slide architecture when using a real person/company/case:
1. **real visual + hook**;
2. **what happened / context**;
3. **why it matters**;
4. **management mechanism / decision**;
5. **practical lesson**;
6. **synthesis / question / transition**, reducing dependence on the public figure image;
7. **UGI-only CTA**, with no implied endorsement.

Do not force all carousels into the same graphic template; preserve narrative logic while varying visual composition.

## Story standard

Stories are not miniature corporate slides. They are attention and navigation levers.

Preferred pattern:
`visual fact → strong number/hook → one management insight → one question/action`

Requirements:
- strong contextual visual;
- one main message per Story;
- high contrast and premium modern design;
- minimal copy;
- human or operational context whenever appropriate;
- music modern and coherent with the topic when audio is used;
- different music across Stories unless there is a deliberate narrative sequence;
- no chiptune/game/ringtone feeling;
- CTA can drive to profile, feed piece or paid material when contextually earned.

## Static post standard

A static post must earn its place with one of:
- a striking verified fact;
- a powerful dilemma;
- a visual quote with verified attribution;
- a memorable management framework.

One dominant message. Avoid "motivational wallpaper" and generic AI imagery.

## Commercial bridge

Commercial sequence:
`interest → understanding → need → practical next step → UGI material`

Never make a public figure, company or tragedy appear to endorse UGI products.

The final UGI CTA should explain the value of the material, not only say "link in bio".

## Content diversification

Daily editorial should rotate across:
- world/business news;
- management curiosities;
- leadership;
- AI + management;
- crisis/governance;
- strategy/business models;
- people/culture;
- practical frameworks;
- UGI materials.

Avoid becoming an "AI-only" page or a "CEO quote" page.

## Non-copy benchmark rule

Benchmark references are used to extract:
- attention mechanics;
- narrative sequencing;
- visual hierarchy;
- authority usage;
- conversion architecture.

UGI must preserve original copy, original design language and independent editorial judgment.

# UGI INSTAGRAM EDITORIAL V2

Status: CANONICAL
Effective: 2026-09-01
Last quality amendment: 2026-09-02
Project: UGI — Uma Gestão Inteligente

## 1. Objective

Transform Instagram into a modern growth and conversion engine, not a static corporate bulletin. Stories, carousels, Reels and static posts must be platform-native, visually premium, useful and connected to current management/business/AI conversations.

## 2. Stories — mandatory role

Default target: at least 5 Stories per active publishing day.

Stories are levers to:
- stop the scroll with a strong hook;
- connect a current fact, curiosity or business event to management and/or AI;
- create curiosity that drives users to the UGI profile/feed;
- lead naturally to UGI materials and the link in bio.

Preferred sequence:
HOOK → FACT/CONTEXT → MANAGEMENT/AI INSIGHT → QUESTION/APPLICATION → CTA.

Stories must not look like static corporate slides. Use modern motion, strong hierarchy, clean backgrounds, premium visual treatment and short copy.

### 2.1 Curiosity + authority copy rule

For Stories based on real news, data, companies, public institutions, research or market events:
- the hook must create curiosity, tension, contradiction or a clear consequence;
- avoid dead corporate phrasing and generic declarative headlines;
- one Story = one main idea;
- the body copy must be concise enough to be comfortably read on mobile;
- the management implication must be explicit but short;
- a trustworthy source must be visible in the creative whenever practical, using a discreet `Fonte:` or `Fontes:` line;
- source attribution must never visually compete with the headline;
- source names must reflect the actual evidence used; never add a prestige source that was not consulted.

Preferred hook patterns:
- `O que mudou — e por que isso importa para quem decide?`
- `O número chama atenção. O gargalo está em outro lugar.`
- `Parece uma notícia de tecnologia. Na prática, é uma decisão de gestão.`
- `A empresa fez X. O detalhe mais importante está no mecanismo.`

## 3. Story music — MANDATORY

UGI Stories must publish with music/audio unless an explicit documented exception is approved before production.

Default production rule:
- Story asset must be delivered as MP4 with the approved music already embedded when the publishing API cannot attach native Instagram music reliably;
- a silent Story is `AUDIO_QA_FAIL`;
- still-image Story concepts must be wrapped into a short MP4 presentation with subtle modern motion and embedded music rather than published as silent static Story assets;
- music must remain audible on a normal phone speaker at ordinary listening volume;
- voice/narration, when present, must remain intelligible above the soundtrack;
- CTA/end frame must not fall into silence;
- record music title/source/license and audio validation in QA evidence.

Track diversity:
- use a different track per Story inside the same day unless an explicit campaign motif is approved;
- do not reuse one generic track indiscriminately across unrelated stories.

Hard-banned music profile:
- 8-bit/chiptune;
- videogame-like beeps;
- polyphonic-ringtone feel;
- childish/game soundtrack;
- monotonous single-tone loops;
- metallic noise beds;
- inaudible soundtrack;
- abrupt audio cut before the Story ends.

Preferred profile:
- modern cinematic business;
- executive tension;
- confident contemporary beat;
- modern tech pulse;
- energetic but premium;
- emotionally compatible with the topic;
- progressive arrangement with perceptible movement rather than a flat loop.

Music must reinforce the message, not compete with it.

## 4. Carousels — modern storytelling standard

Carousels should normally use 5–8 slides and tell a real story, not repeat one sentence across cards.

Preferred structure:
1. COVER — real relevant leader/company/case + strong hook.
2. CONTEXT — what happened / why it matters.
3. TENSION — the management problem or contradiction.
4. METHOD/APPLICATION — what the case teaches.
5. CRITERION — what to measure/change/do differently.
6. TRANSITION/LESSON — convert the case into a general management principle.
7. UGI CTA — UGI only, with link-in-bio/material call to action.

### Public figure / company identity lock

When the carousel is about a named real person or company:
- keep the SAME person/company identity across all slides where the subject is shown;
- different angles/crops are allowed, but identity drift is a blocking failure;
- do not replace the subject with a generic AI-generated executive;
- prefer licensed, official, public-domain or otherwise permitted imagery when a real photograph is required;
- never fabricate a quote; distinguish direct quotation from UGI interpretation.

### Penultimate / final slide endorsement safeguard

- Slide 6 should transition away from endorsement-like imagery. Prefer a neutral business scene, silhouette, back view, company environment or abstract management visual.
- Slide 7 must be 100% UGI. Do NOT show the case leader/person as if endorsing UGI products.
- The final CTA must make clear that the material belongs to UGI, not to the featured person/company.

## 5. Carousel audio rule

Do NOT use a mixed carousel where only the first card carries embedded music. This creates a broken experience: audio stops when the user swipes to static cards.

For fully automated scheduling through the current provider/API route:
- native audio configuration is production-supported for Reels/Trial Reels, not proven end-to-end for feed/carousel posts;
- therefore continuous native music across an auto-published carousel is NOT currently a proven capability;
- default automated UGI carousel = NO MUSIC until a native-carousel-audio route is proven end-to-end.

If continuous carousel music is essential, the native Instagram mobile workflow can attach one song across the entire swipe, but that is a manual/mobile path and must never be presented as autonomous scheduling.

Never claim seamless carousel music unless a real published smoke test proves it.

## 6. Static posts

Single-image posts must be modern, high-contrast and editorially useful. Avoid dense copy, text ghosts, random foreign-language artifacts, fake background lettering and generic AI-office imagery.

A static post should communicate one strong idea with one clear payoff.

## 6.1 Lower-third / footer cleanliness rule

The lower third must function as breathing space, not as a second information wall.

Default:
- one primary lower-third function only: question, short CTA or source line;
- no ghost typography, oversized decorative words or repeated phrases behind the body copy;
- no multiple competing text layers near the bottom edge;
- preserve generous negative space around the final question/CTA;
- keep source attribution small, crisp and readable;
- do not place important text inside unsafe bottom UI zones;
- if the lower third feels denser than the headline area, redesign before QA.

Preferred hierarchy:
1. discreet category/UGI marker;
2. strong curiosity-led headline;
3. short context/management insight;
4. clean final question or CTA;
5. discreet source attribution when applicable.

## 7. Visual anti-patterns — hard fail

Block publication if any of these appear:
- gibberish or pseudo-language text;
- foreign-language filler not intentionally part of the content;
- ghost text / duplicated phrases in the background;
- illegible or cropped copy;
- excessive lower-third clutter;
- dense mobile-unfriendly body copy;
- missing source attribution on a factual/news asset when the source can reasonably be shown;
- AI identity drift in a named-person story;
- generic business-person substitution for a named leader;
- third-party logo accidentally left in UGI CTA artwork;
- visual design that looks like a slide deck rather than social content.

## 8. Instagram format strategy

Current 2026 evidence favors:
- Reels for discovery;
- Carousels for saves, repeat engagement and deeper storytelling;
- Stories for daily relationship, profile traffic and conversion;
- Single-image posts selectively, not as the default growth format.

Do not mechanically publish every format every day. Use the editorial objective to choose the feed mix.

## 9. Scheduling truth — provider-agnostic

A post is not 'scheduled' because an asset exists or a workflow was dispatched.

To claim SCHEDULED through any provider (Buffer, Metricool or future route), require:
1. provider create success;
2. provider post ID/UUID or equivalent durable identifier;
3. correct brand/account;
4. correct network and format;
5. exact requested publication timestamp;
6. auto-publish enabled when unattended publication is intended;
7. provider planner/readback returns the same post and exact slot;
8. no validation/error state.

If any item is missing, classify as PLANNED / ASSET_READY / SCHEDULING_FAILED as appropriate — never as scheduled.

Before telling the user that a future day's agenda is 'OK', perform a live readback of every scheduled item and reconcile the expected count against the provider's planner.

## 10. Delivery truth

Scheduled is not delivered.

After each due time, use platform/provider readback to classify delivery. A missing morning post is an incident, not a reason to silently create a replacement and pretend the original schedule worked.

Recovery may move a missed slot only with explicit user direction or a documented editorial recovery rule.

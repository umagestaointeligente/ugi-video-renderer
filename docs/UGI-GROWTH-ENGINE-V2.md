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

# UGI Growth Engine V2 — Pilot #001 Review

Status: REJECTED FOR PRODUCTION / LEARNING RETAINED

## Findings

Pilot #001 is not the production creative standard.

1. The 15.03 s review prototype was created by time-compressing the 24.03 s TikTok master (~1.60x). For management content this feels rushed and unpleasant. V2 must not use global speech/video acceleration as the main retention tactic.
2. The visual language remained too similar to V1: corporate stock footage, persistent dark lower panel, teal accent and repeated text structure.
3. CTA text clipped because the current renderer uses a fixed 430 px CTA box and a single-line drawtext path without adaptive wrapping/autosizing.
4. The opening fade creates a dark/black first frame before the hook is fully visible. V2 requires the hook on frame 1.

## V2.1 direction

- Natural PT-BR narration, target 0.98x–1.05x.
- Typical management short: 18–28 s; 14–18 s only when narration naturally fits.
- Fast visual rhythm comes from cuts, reframing, kinetic text, screenshots, object emphasis and scene changes — not accelerated speech.
- Remove the persistent lower-third panel as the default visual grammar.
- Diversify visuals: POV/screen interactions, phone, spreadsheet, email, chat, calendar, close-up objects/documents, short reenactments, diagrams and full-frame payoff scenes.
- Hook visible on first frame.
- CTA must auto-size or wrap and respect safe margins.
- Behavioral CTA during recovery should usually stay within 6–8 words.

## Non-regression

No stable production component is removed or overwritten because of this review. Publisher Hub, Buffer, Worker, renderer V1 path, queues, receipts and scheduled posts remain preserved until V2.1 is separately proven.

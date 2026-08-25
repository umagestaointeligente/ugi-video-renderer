# UGI PDF Premium Standard

Status: CANONICAL
Version: PREMIUM_V6
Effective date: 2026-08-24
Project: UGI - Uma Gestao Inteligente

## Canonical reference

The visual/editorial baseline is the approved master file:
`Kit_UGI_Priorizacao_Inteligente_PREMIUM_V4_UPLOAD_CANONICO-1.pdf`.

The master defines the expected value perception, depth, hierarchy and practical usefulness. New files must not clone the master page-by-page, but must preserve the same premium standard.

## Commercial promise

Every paid PDF must create the perception that the customer paid less than the delivered value. The target reaction is: "this was inexpensive for what I received" and should create willingness to purchase a higher-ticket follow-on product.

## Mandatory structure

- Premium cover with clear promise and observable result.
- Approximately 14-20 pages unless the topic clearly requires another length.
- Strong UGI visual identity: navy, gold, white/cream, disciplined spacing.
- Clear page hierarchy with kicker, headline, page badge and footer.
- Practical frameworks, matrices, dashboards, checklists or diagrams whenever they add value.
- Ready-to-copy UGI prompts throughout the material.
- At least one implementation plan or ritual that turns reading into action.
- References/continuity page and explicit next-level product path.
- Content must be original to the topic; do not simply recycle the Priorizacao kit.

## Visual standard

- Use modular cards, rounded prompt boxes, strong section bands and professional icons.
- Use everyday/workplace visual elements or contextual illustrations when they improve comprehension.
- Do not repeat the same image/scene across the PDF.
- Do not use generic template-looking visuals.
- Text must never touch safe margins or be visually cut off.
- No overlapping text, crowded cards, clipped headings, broken glyphs or excessive empty space without intentional visual balance.
- Prompt boxes must use safe internal padding and sufficient line spacing.
- Reference pages must keep references visually separated from final-rule callouts.
- Tables and diagrams must remain readable on a mobile PDF viewer.

## Editorial standard

Every material must contain a proprietary or clearly organized operating method, not only generic tips. The method should normally include:

1. problem diagnosis;
2. decision rule or framework;
3. practical application;
4. example or use case;
5. prompt(s) ready to copy;
6. implementation cadence;
7. measurement/review mechanism.

All claims that depend on external frameworks should be referenced. UGI-authored syntheses must be presented as UGI methods, not falsely attributed to external sources.

## Image policy

- Contextual workplace/daily-management imagery is encouraged where it improves interaction and perceived quality.
- No repeated images within the same PDF.
- Visual assets must match the page topic semantically.
- If a visual cannot be generated with sufficient quality, prefer a premium diagram/card/icon composition rather than a weak stock-like image.

## QA hard gate

A new paid PDF must not be released unless all gates are true:

- UGI_PDF_MASTER_STANDARD_PASS=true
- MASTER_LAYOUT_PASS=true
- EDITORIAL_DEPTH_PASS=true
- VISUAL_COMPONENTS_PASS=true
- PRACTICAL_APPLICATION_PASS=true
- UGI_PROMPTS_PASS=true
- REFERENCES_PASS=true
- SAFE_MARGINS_PASS=true
- TEXT_OVERLAP_PASS=true
- MOBILE_READABILITY_PASS=true
- PDF_RENDER_QA_PASS=true

During the validation week, also require:

- HUMAN_REVIEW_REQUIRED=true
- REVIEW_PDF_AVAILABLE=true
- STORE_PUBLICATION_ALLOWED=false until human approval.

After several consecutive approved materials without relevant corrections, HUMAN_REVIEW_REQUIRED may be disabled while automatic QA remains mandatory.

## Current approved visual evolution

PREMIUM_V6 adds:

- cleaner icon-led reference blocks;
- stronger visual callouts;
- better prompt-box spacing;
- safer text margins;
- mobile-readable infographic cards;
- page-specific spacing rules to avoid overlaps;
- more visual variety while keeping UGI identity.

## Commerce rule

A product record is not evidence of a valid commercial asset. Paid-product readiness requires the final PDF, cover/visual presentation, real asset upload, Store visibility, checkout validation and QA evidence.

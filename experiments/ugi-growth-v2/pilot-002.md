# UGI Growth V2.1 — Pilot 002

Status: **RENDERED FOR REVIEW — NOT PRODUCTION APPROVED**

## Why this pilot exists
Pilot 001 was rejected because the 24s master was globally time-compressed to ~15s, creating an unpleasant rushed perception for management content. It also retained too much of the previous fixed-panel visual grammar and exposed a CTA clipping bug.

Pilot 002 deliberately tests a different editorial product:
- natural PT-BR narration at 1.0x;
- no global speed-up;
- first-frame hook;
- no fixed bottom panel;
- different layout per scene;
- full-frame story progression instead of repeated corporate template;
- CTA with short safe-width button copy;
- subtle motion inside scenes, while narration remains calm;
- render-only: no Buffer, no publication, no checkout.

## Story
Hook: `ELE COLOU A FOLHA DE SALÁRIOS NUMA IA.`
Interaction: `VOCÊ DEMITE, BLOQUEIA A IA OU MUDA A REGRA?`
Twist: `SE NINGUÉM SABE RESPONDER... o problema começou antes dele.`
Rules:
1. Dados sensíveis não entram.
2. Decisão crítica exige revisão humana.
3. Alguém precisa ser dono do resultado.
Payoff: `IA COM REGRA ECONOMIZA TEMPO. SEM REGRA, MULTIPLICA RISCO.`
CTA: `CHECKLIST NO PERFIL` + save prompt.

## Evidence
GitHub Actions render run: `32925503001`
Conclusion: `success`
Artifact: `ugi-growth-v2-1-pilot-002`
Artifact ID: `9591400691`

Output properties:
- 1080x1920
- 30 fps
- H.264 + AAC 48kHz stereo
- duration: ~31.12s
- voice speed: 1.0x
- global speed-up: false
- first-frame hook: true
- fixed bottom panel: false
- publicationTriggered: false
- bufferMutationPerformed: false
- checkoutTriggered: false

## Approval gate
Do not adopt as production standard until human review confirms:
1. narration feels natural;
2. visual language is sufficiently different from V1;
3. hook is readable and credible;
4. CTA is fully visible;
5. pacing is dynamic without feeling rushed;
6. content feels native to short-form feeds while preserving UGI credibility.

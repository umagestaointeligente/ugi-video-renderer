# UGI — EDITORIAL 2026-09-04

Status: `EDITORIAL_V2_LOCKED / 15D_COOLDOWN_APPLIED / BUFFER_READINESS_PENDING / WORKER_CAPACITY_BLOCKED / NOT_SCHEDULED`

## Execution state

- Topics: `EDITORIAL_LOCKED_FOR_PRODUCTION`
- Assets: `NOT_RENDERED`
- QA: `NOT_RUN`
- Buffer: `NOT_SCHEDULED`
- Delivery: `NOT_APPLICABLE`
- Publication mutation: `NOT_TRIGGERED`

No state may be promoted without real evidence.

## Operating rules

1. Apply the canonical 15-day semantic topic cooldown per platform before render and publication.
2. Instagram Story/Reel/static/carousel share the same Instagram topic history.
3. Cross-platform reuse is allowed only when the destination platform history is clean and the content is adapted natively.
4. Credible missing-history risk fails closed unless an extraordinary breaking-development exception is explicitly justified.
5. Revalidate factual/trend-sensitive claims on the morning of 2026-09-04 before final copy lock.
6. Render/asset generation must pass real QA before any publishing mutation.
7. Buffer must pass a read-only readiness probe before any scheduling batch.
8. `BUFFER_SCHEDULED` requires real Buffer post ID + exact dueAt + `scheduled` readback.
9. Do not use Metricool as a publisher for UGI.
10. Do not create paid-cost fallbacks or top up paid credits to bypass zero-cost gates.

## 2026-09-04 agenda — V2

| Time (America/Sao_Paulo) | Platform | Format | Topic | Management angle | Editorial state |
|---|---|---|---|---|---|
| 09:00 | Instagram | Story | Experimento LZ / matéria escura | Um sinal interessante não é uma conclusão: hipótese, evidência e decisão sob incerteza | `PLANNED` |
| 10:30 | Instagram | Story | Tyson — preço recorde não significa margem recorde | Preço × custo × margem × elasticidade | `PLANNED` |
| 12:15 | TikTok | Video | #joblife — trabalho real vs. employer branding | Employer brand é a experiência vivida, não apenas a mensagem da empresa | `PLANNED` |
| 12:45 | Instagram | Reel | Anvisa × Unilever | Qualidade/compliance vira tema de operação quando limita capacidade e execução | `PLANNED` |
| 16:30 | YouTube | Short | State of Play — lançar 30+ novidades sem diluir atenção | Arquitetura de lançamento, portfólio e disputa por atenção | `PLANNED` |
| 18:00 | Instagram | Story | Snowflake — IA aparece no uso/receita | Tecnologia vira estratégia quando aparece em uso, receita ou eficiência | `PLANNED` |
| 19:15 | Instagram | Carousel | Lululemon — quando uma marca premium perde novidade | Inovação, posicionamento premium, competição e limites do desconto | `PLANNED` |
| 19:45 | TikTok | Video | Microdramas / aTwist — vídeo curto vira modelo de negócio | Mudança de hábito pode criar novos modelos econômicos | `PLANNED` |
| 20:30 | YouTube | Short | GSM / VinFast — crescer rápido com modelo pesado em capital | Escala × capital × risco × unit economics; crescer rápido não garante crescimento saudável | `PLANNED` |

## Format mix

- Instagram: 5 posts — 3 Stories + 1 Reel + 1 Carousel.
- TikTok: 2 videos.
- YouTube: 2 Shorts.
- Static feed post: none in this agenda.

## 15-day exclusions / replacements

- Volkswagen: removed from 20:30 YouTube candidate set despite no durable YouTube hit, because a recent 2026-08-31 Instagram Volkswagen transformation Reel exists and the new case remains semantically too close for the desired editorial freshness.
- Payroll / U.S. jobs report: removed from 18:00 Instagram because credible user recollection plus incomplete historical backfill requires fail-closed handling (`HISTORY_REVIEW_REQUIRED`).
- GTA VI: excluded from State of Play framing because of recent YouTube topic collision.
- Uber: remains `HISTORY_REVIEW_REQUIRED` and is not eligible for substitution until history is reconciled.

## Readiness snapshot at editorial lock

### Buffer

`BUFFER_READINESS = UNPROVEN`

The last fully proven Publisher Hub Buffer attempt available in durable evidence returned `BUFFER_CHANNELS_FAIL` and did not trigger publication. No post in this 2026-09-04 agenda is scheduled until a new read-only Buffer readiness proof succeeds.

### Worker / generation capacity

`WORKER_GENERATION_READINESS = BLOCKED`

A live Instagram MultiFormat reconciliation at 2026-09-04T01:48Z returned Cloudflare error 4006: daily free allocation of 10,000 neurons exhausted. Generation failed before Buffer scheduling for affected items. This is a separate blocker from Buffer and must clear before relying on tomorrow's production.

## Release sequence

`MORNING_REVALIDATION -> 15D_TOPIC_GATE -> RENDER -> QA_PASS -> WORKER_CAPACITY_PASS -> BUFFER_READINESS_PASS -> SINGLE_POST_CANARY -> BUFFER_ID_DUEAT_SCHEDULED_READBACK -> REMAINING_BATCH`

If any gate fails, keep the remaining agenda fail-closed and reslot rather than claiming it is scheduled.
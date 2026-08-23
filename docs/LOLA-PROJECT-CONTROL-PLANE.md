# LOLA PROJECT CONTROL PLANE

Status: ACTIVE
Version: 1.2
Effective: 2026-08-23
Purpose: durable source of truth across ChatGPT conversations, projects and operators.

## 1. Architecture principle
GitHub is the canonical, versioned source of truth for project architecture, policies, runbooks and non-secret configuration. Runtime state/telemetry may live in Cloudflare storage. Secrets/tokens MUST NOT be committed; keep them in GitHub/Cloudflare secret stores.

Any new chat/operator must read this document plus the project-specific manifest before making production changes. Never infer that an integration is working: require readback/evidence.

## 2. Project registry
### UGI — Uma Gestão Inteligente
Repository: umagestaointeligente/ugi-video-renderer
Runtime: Cloudflare Worker + GitHub Actions/render pipeline + Buffer publishing + analytics integrations.
Observed repository areas: cloudflare/, control-plane/, magic-engine/, generated/, scripts/, assets/.
Commerce: UGI Store / materiais route. Commercial content must have matching material/product before publication when commercial CTA is enabled.
Analytics: Metricool plus first-party platform analytics/readbacks when available.
Official publisher/scheduler: BUFFER ONLY.
Distribution: Instagram, TikTok, YouTube.

### Other projects
Create docs/projects/<project>.md for every active project. Each manifest must contain owner/purpose, repositories, runtime/services, integrations, routes, data stores, deployment flow, operational gates, current version, known limitations, evidence/readback methods and recovery runbook. Do not store credentials.

## 3. UGI integration role separation — HARD POLICY
This separation is mandatory and must survive new chats, operators and future refactors.

### Buffer — EXCLUSIVE publication plane
Buffer is the ONLY approved system for:
- scheduling posts;
- queueing posts;
- publishing posts;
- retry/recovery of publication delivery;
- publication status/readback when supported;
- post IDs used as publication evidence.

No production social post may be scheduled or published through Metricool.

### Metricool — ANALYTICS ONLY
Metricool is restricted to read-only analytical use for UGI:
- content performance analytics;
- reach, views, watch time, retention, saves, shares, engagement and traffic-source analysis;
- best-time signals as an analytical input only;
- historical performance and learning for the Growth Engine.

Metricool MUST NOT be used to create, update, schedule, reschedule, queue or publish UGI social posts.

If an operator/tool exposes Metricool publishing actions, those actions are considered OUT OF POLICY for UGI and must not be called.

### Fail-closed routing rule
If Buffer is unavailable or publication cannot be proven through Buffer/readback, the slot status is BLOCKED/NOT_PROVEN. Do not silently fall back to Metricool publishing.

A future migration away from Buffer requires an explicit architecture decision record, controlled smoke test, rollback plan and policy update before any production use.

## 4. UGI persistent growth policy
Goal/North Star: build toward >=10,000 organic views per content/platform; this is a target, never a guaranteed outcome.
Distribution ladder: 100 -> 500 -> 1,000 -> 3,000 -> 10,000 views.
Primary optimization order: retention/choose-to-view -> distribution -> engagement/save/share -> qualified store traffic -> conversion/revenue.

Before EVERY content batch, Motor de Arranque must combine:
1. UGI recent telemetry by platform (Metricool analytics + native analytics/readback when available).
2. Current platform-specific trends/search/social signals.
3. Market/management/AI signals relevant to UGI.
4. Creative history/novelty scan to avoid topic, hook, first-line, script, visual concept and CTA repetition.
5. Platform-specific audience/format behavior.
6. Commerce/material inventory and relevance.
7. Time/day signals to select dynamic posting windows; times are not fixed.

Each platform is an independent editorial client. DO NOT automatically replicate topic, hook, script, visual concept or asset across Instagram/TikTok/YouTube. Cross-platform reuse requires an explicit evidence-based reason.

## 5. Platform experiments
### TikTok
Current experimental priority: early retention. Test short 7–12s variants when supported by current telemetry; hook/conflict/result must begin at frame 0; no slow introduction. Favor native/human pacing, rapid visual progression and clear on-screen text. Track views, For You share, average watch time, completion, likes, comments, shares, search/profile sources. A zero-view post must trigger eligibility/processing/status diagnosis before delete/repost.

### Instagram
Do not depend exclusively on Reels. Motor may choose Reel, carousel or static post based on evidence. Test utility/save/share-oriented carousels. Avoid repetitive visual templates. Track reach, non-follower reach, views, watch/retention when applicable, saves, shares, comments and profile/store actions.

### YouTube
Keep video/Shorts as primary publishing format. Optimize first-frame choose-to-view behavior, average view duration/percentage and satisfaction/engagement. Analyze micro-winners and create descendants, never copies. Track shown-in-feed/eligible exposure when available, views, choose-to-view, retention, likes/comments/shares and downstream traffic.

## 6. Experiment loop
Every publication is an experiment:
OBSERVE -> HYPOTHESIZE -> GENERATE -> RIGHTS/SAFETY/QUALITY GATES -> COMMERCE GATE -> BUFFER SCHEDULE/PUBLISH -> READBACK -> MEASURE -> LEARN -> UPDATE WEIGHTS.

Record per experiment: content_id, experiment_id, platform, topic, format, hook, first_line, duration, visual_concept, script summary/hash where available, CTA, material/product, selected time and rationale, trend evidence, telemetry baseline, Buffer post ID/readback, performance checkpoints and learning.

Never declare success from scheduling alone. Distinguish SCHEDULED, PUBLISHED and VERIFIED. Publication is verified only with Buffer/platform readback or equivalent concrete evidence.

## 7. Commerce gate
For commercial/solution-linked content:
TOPIC -> MATCHING MATERIAL -> PRODUCT/COVER -> UGI STORE -> CHECKOUT/DESTINATION VALID -> PLATFORM CTA -> BUFFER PUBLICATION.
Fail closed when the required material/destination is absent. Product naming should closely match the promise/topic of the originating content so the visitor recognizes it. Reusing an existing product is allowed only when semantic fit is genuine.
Descriptions should be easy to scan, using visual blocks/emojis when appropriate to the platform, while preserving native readability. Platform link limitations must be respected; use the profile/store route and clear CTA where clickable post links are unavailable.

## 8. Creative novelty
Maintain a compact, queryable creative-history index. Minimum fields: date, platform, content_id, topic, hook, first_line, script_hash/script_summary, visual_concept, scene_summary, CTA, product_id, performance. Default comparison window: 30 days. Do not fetch full drafts/assets merely to prove novelty. Exact and semantic repetition checks should be independently reportable.

## 9. Evidence and fail-closed rules
No operator/AI may report CONNECTED, READY, SCHEDULED, PUBLISHED, STORE_UPDATED or VALIDATED without concrete evidence from the relevant system. If evidence cannot be obtained, status is UNKNOWN/NOT_PROVEN, not PASS.

Required evidence classes where applicable: source commit/version; deployment result; endpoint/readback; render ID/status; Buffer post ID/status; platform publication readback; store/product readback; analytics snapshot.

## 10. Notifications/observability
Desired publication lifecycle events: STUDY_COMPLETE, CONTENT_READY, MATERIAL_READY, GATES_PASS/FAIL, SCHEDULE_CONFIRMED, T_MINUS_15, PUBLISHING, PUBLISHED, VERIFIED, PERFORMANCE_CHECKPOINT, INCIDENT. Notification delivery is only considered active after a real delivery receipt/readback; documentation alone is not evidence that notifications work.

## 11. Durable project documentation standard
For each project maintain:
- docs/projects/<project>.md — architecture and current operating state.
- config/<project>/policy.json — machine-readable non-secret policy.
- docs/runbooks/<project>-operations.md — deploy/test/recovery procedures.
- docs/decisions/ — dated architecture decision records for important changes.
- generated/evidence/ or runtime storage — machine-generated receipts, where appropriate.

Git history is the audit trail for configuration changes. Runtime/high-volume analytics should not bloat source control; store them in suitable Cloudflare storage and persist compact learned weights/summaries.

## 12. Security
Never commit API keys, tokens, passwords, cookies, private customer data or checkout secrets. Use least-privilege GitHub/Cloudflare secrets. Documentation may record secret NAMES and where they are configured, never secret VALUES.

## 13. Handoff protocol for a new conversation
1. Locate this repository.
2. Read docs/LOLA-PROJECT-CONTROL-PLANE.md.
3. Read the relevant docs/projects/<project>.md and config/<project>/policy.json.
4. Confirm integration role separation: Buffer=publisher; Metricool=analytics-only.
5. Read current deployed/source version and recent evidence before changing anything.
6. Reconcile docs vs runtime; runtime evidence wins for current operational status, Git is canonical for intended configuration.
7. Never claim a bridge/integration is live without testing it.

## 14. UGI Growth Engine runtime integration — 2026-08-23
Persistent policy: `config/ugi/growth-policy.json`.
Current live policy schema observed in `main`: `1.2` (do not downgrade to older smoke expectations such as 1.0).
Policy SHA-256 proven by runtime smoke: `ddb581512329447065bff0b2833c769e6a6abfc1465595cc6b5883582308e095`.

### Isolation correction
Audit found that `magic-engine/config.json` belongs to Orbit Media Labs. Therefore UGI must NOT use Orbit's Magic Engine as its production Growth Engine runtime. UGI policy loading is isolated in `scripts/ugi_growth_runtime.py` and smoke evidence is generated by `scripts/ugi_growth_policy_smoke.py`.

### Runtime smoke evidence
Workflow: `.github/workflows/ugi-growth-policy-smoke.yml`.
Run ID: `32659766889`.
Trigger commit: `67163e01ecd4a62fdc7cf64246eb14a8e721b7ca`.
Receipt commit: `308e8e3e8f3245bb5e625f7cb89f0b665742bf23`.
Receipt readback: `control-plane/receipts/ugi-growth-engine/latest.json`.
Result: `SMOKE_TEST_PASS=true`, `POLICY_LOADED=true`, `RUNTIME_POLICY_ACTIVE=true`, `GROWTH_ENGINE_ACTIVE=true`, `PLATFORM_INDEPENDENCE=true`, `DEFAULT_CROSS_PLATFORM_REPLICATION=false`, `NORTH_STAR_VIEWS=10000`, `NOVELTY_WINDOW_DAYS=30`, `COMMERCE_GATE_REQUIRED=true`, `PUBLICATION_TRIGGERED=false`, `PAYMENT_TRIGGERED=false`, `REGRESSION_CHECK_PASS=true`.

### Remaining hard gate before declaring UGI_GROWTH_ENGINE_READY=true
The smoke proves policy -> isolated UGI loader -> runtime contract -> receipt -> persistent readback. It does NOT yet prove that the isolated UGI loader executes in the production content-generation path before `generateFromCommand` / render dispatch in the currently deployed Cloudflare Worker.

Repository audit shows the Worker command path saves the command and, when `generate_now !== false`, calls `generateFromCommand(...)`; therefore production generation-path integration must be inserted before that call or at an equivalent pre-generation control point. Any Worker mutation is forbidden until the exact currently deployed Worker source/version is recovered from Cloudflare and reconciled with the repository source. Repository source alone is not proof of deployed source.

Until that production-path proof exists:
`UGI_GROWTH_ENGINE_READY=false`
`FAILED_GATE=PRODUCTION_GENERATION_PATH_POLICY_CONSUMPTION`
`ERROR=Exact deployed Cloudflare Worker source/runtime could not be retrieved with the currently connected tools.`
`ERROR_CLASS=EXTERNAL_RUNTIME_SOURCE_UNAVAILABLE`
`NEXT_ACTION=Recover exact deployed Worker source/version from Cloudflare, insert isolated UGI policy pre-generation gate without changing other projects/components, deploy with credential revalidation, run one no-publication/no-payment smoke, persist receipt, and perform independent readback.`

This file intentionally captures durable policy and evidence status, not ephemeral chat memory.

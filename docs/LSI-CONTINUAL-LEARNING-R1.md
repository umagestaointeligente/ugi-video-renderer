# LSI CONTINUAL LEARNING R1

Date: 2026-08-30 BRT
Status: IMPLEMENTED ON ISOLATED LSI REVENUE BRANCH — DEPLOYMENT REQUIRES GREEN CI

## Mission

Make LSI progressively better from verified outcomes instead of repeatedly starting from zero. The learning layer is transversal: revenue routes, research routes, automation routes and future LSI projects can submit typed outcome events while preserving each project's isolation and hard rules.

## Non-negotiable truth contract

1. Learning never converts a claim into a fact.
2. Revenue can only increase `verified_revenue` when `revenue_verified=true` and an authoritative evidence reference exists upstream.
3. Unverified monetary claims are stored separately and cannot promote a route.
4. External content has `instruction_authority=false` and raw external prompts are not stored in the learning ledger.
5. Learning recommendations do not grant new capabilities.
6. `ACCELERATE` means allocate more zero-cost discovery/compute within the existing authorization envelope; it never means spend money, activate a wallet, publish, trade or bypass an approval gate.
7. Stable UGI, Orbit, Recruiter, BFY and other project production flows remain isolated.
8. Default incremental monetary cost remains US$0.

## Persistent memory model

The Durable Object stores:
- aggregate model per route;
- trials, successes, failures and blocked events;
- verified revenue and verified cost separately;
- unverified monetary claims separately;
- EMA quality, risk and outcome signal;
- typed success/failure/block reason counts;
- recommendation score and state;
- compact recent event history;
- permanent learned aggregates even when old raw events are compacted.

The system therefore preserves the teaching even if detailed raw history is compacted for bounded storage.

## Online learning policy

Each event has:
- mission/project/route identity;
- outcome (`SUCCESS`, `FAILURE`, `NEUTRAL`, `BLOCKED`, `REVENUE`);
- evidence class E0-E4;
- verified/unverified revenue;
- cost;
- elapsed time;
- quality and risk scores;
- typed reason code;
- source/evidence reference.

Evidence strength controls learning rate. E4 changes the model more than E0. Verified revenue is economically privileged; unverified revenue contributes zero to verified economics.

The route score combines:
- verified economics;
- historical success rate;
- evidence-weighted recent signal;
- exploration bonus for under-tested routes;
- risk penalty.

This is a deterministic online bandit-style policy, not an opaque claim that a neural model retrains itself. The model continuously updates route allocation decisions from real outcomes.

## Recommendation states

- `ACCELERATE`: verified positive economics + acceptable success/risk.
- `KEEP_AND_OPTIMIZE`: promising route; continue and improve.
- `EXPLORE`: insufficient evidence; gather more low-cost evidence.
- `HOLD`: weak current evidence; reduce allocation.
- `KILL_CANDIDATE`: enough trials with persistently poor results and no verified revenue.
- `BLOCKED`: external approval/security/financial gate prevents execution.

## Autonomous observation loop

R1 self-wakes through a Durable Object alarm and observes only safe public/read-only signals:
- PackValue Tools aggregate request telemetry;
- PackValue Remote MCP health;
- PackValue402 payment-disabled health;
- Revenue Radar candidate state.

The default learning cadence is 10 minutes. These observations are not unique-user counts and are not revenue. They are operational evidence only.

## Machine-learning progression rule

Every generation must be at least as evidence-disciplined as the previous generation. The engine may adapt scores and allocation, but it may not relax:
- revenue evidence requirements;
- zero-cost policy;
- security gates;
- project isolation;
- payment approval requirements;
- anti-spam / anti-deception rules.

A failure becomes a reusable negative lesson through its `reason_code`. A later success can outweigh it statistically, but the failure lesson count is never rewritten to pretend the failure did not happen.

## Revenue strategy implication

LSI should seek high-frequency, low-marginal-cost value production. A route producing a few cents repeatedly can outrank a high-ticket route with no traffic if verified net economics and recurrence are better. However projected cadence is never counted as revenue before settlements occur.

Priority lanes for the current greenfield mission:
1. machine-to-machine paid tools / x402 micropayments;
2. free agent-distribution surfaces that can feed paid deterministic tools;
3. verified code/data bounties with proven payout rails;
4. high-traffic digital utilities and API/MCP services;
5. HTML5 games as medium-term scale;
6. clean greenfield BRL checkout only after isolation/security proof.

## Current financial blocker retained

PackValue402 must remain payment-disabled until Paulo explicitly supplies and approves a Base-compatible public receive address he controls. Never request or store a seed phrase/private key. Never invent an address.

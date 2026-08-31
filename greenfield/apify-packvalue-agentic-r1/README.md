# PackValue Agentic R1

Deterministic unit-price normalization Actor prepared for Apify Pay-Per-Event and agentic payment eligibility.

## What it does

Accepts 1–200 offers and normalizes prices by kg, liter, or unit. It applies percentage discount before shipping, ranks only comparable base units, and returns structured dataset rows.

## Safety and privacy

- No external network access is required by the business logic.
- No buyer PII is required or collected.
- No financial outcome or savings is guaranteed.
- Input is bounded to 200 offers.
- The `batch-completed` PPE event is charged only after deterministic computation succeeds and before results are delivered.

## Agentic payment target

Target configuration: Pay Per Event, platform usage not passed through as a separate charge, limited permissions, Standby disabled. Apify requires developer KYC before an Actor can become eligible for x402/Skyfire agentic payments.

## External activation boundary

Publishing/monetization is intentionally not claimed as complete until an authorized Apify developer account exists, KYC is complete, the Actor is pushed, PPE is enabled, limited permissions are verified, and Store visibility is confirmed. No Apify token or developer credential belongs in this repository.

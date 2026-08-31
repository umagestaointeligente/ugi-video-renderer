# PackValue RapidAPI R1

Provider-ready package for exposing PackValue normalization through RapidAPI without exposing the backend directly.

## Security boundary

The production backend must be configured with `RAPIDAPI_PROXY_SECRET` as a platform secret. `/v1/normalize` rejects calls that do not carry the matching `x-rapidapi-proxy-secret` header. No production secret is stored in this repository.

## Import package

`openapi.json` is OpenAPI 3.0.2 and is intended for RapidAPI Studio import. Replace the placeholder server URL only after the private backend Worker is deployed and its proxy secret is configured.

## Monetization boundary

RapidAPI handles subscription/usage billing. Provider payout configuration is external to this repository. Current RapidAPI documentation states provider payouts require a PayPal account. The package must not be classified as revenue-capable until provider payout setup and a paid/freemium plan are verified.

## Current state

Code/schema QA can be fully automated. Deployment stays blocked until the RapidAPI project exists because the proxy secret is generated/configured at that boundary. Revenue remains zero until an actual paid subscription/usage settles.

# PackValue402 Production Activation Policy R1

## Default state

The production Worker may exist publicly while `PAYMENTS_ENABLED=false` and without `PAY_TO`. In that state it MUST fail closed for `/v1/compare` and MUST NOT create a payment requirement tied to a real recipient.

## Financial activation gate

Real x402 payments may be enabled only after all of the following are true:

1. The latest PackValue402 preprod acceptance is PASS.
2. Production and full dependency audits report zero high/critical vulnerabilities.
3. The selected facilitator advertises x402 v2 `exact` on `eip155:8453`.
4. A concrete Base-compatible EVM receive address controlled by the owner is supplied.
5. The owner explicitly approves that exact address for PackValue402 at USD 0.001 per comparison.
6. The address is not any known placeholder, null, burn, CI test, or previously used fake address.
7. The server receives only a public `PAY_TO` address. No wallet private key, seed phrase, signer, spending permission, or buyer funding credential may be stored in the Worker.
8. Production activation occurs on a separate deploy from preprod and preserves rollback to payment-disabled state.

## Address deny rules

Reject at minimum:
- zero address
- `0x000000000000000000000000000000000000dEaD`
- `0x1111111111111111111111111111111111111111`
- `0x2222222222222222222222222222222222222222`
- any malformed or non-EVM address

## First-live sequence

1. Bind the approved public receive address.
2. Enable payments on the separate production Worker only.
3. Verify `/health` reports ready and server_can_spend=false.
4. Make an unpaid request and require a valid HTTP 402 challenge with the approved payTo, x402Version 2, exact scheme, eip155:8453, amount 1000, and Bazaar metadata.
5. Do not self-fund, self-pay, or spend money to manufacture the first transaction without a separate explicit mandate.
6. Treat the first real buyer settlement as revenue only after verifiable on-chain evidence.
7. Verify Bazaar indexing independently after a valid settlement; never infer indexing merely from declaration.

## Kill switch

If facilitator support changes, dependency audit fails, receipt validation fails, price/address drifts, or an incident is detected, redeploy production immediately with `PAYMENTS_ENABLED=false` and no `PAY_TO`, preserving evidence.

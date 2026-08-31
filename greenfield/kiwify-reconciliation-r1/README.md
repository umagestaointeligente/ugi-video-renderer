# Kiwify Reconciliation R1

A least-privilege adapter for reconciling products, sales and payment events from Kiwify into the LSI Payment Hub.

## Required external secrets

- `KIWIFY_CLIENT_ID`
- `KIWIFY_CLIENT_SECRET`
- `KIWIFY_ACCOUNT_ID`

These belong in a secret store only. Never commit them.

## Minimal permissions

Create the Kiwify API key with only the endpoints needed for product reads, sales reads and webhook management. Do not grant withdrawals, refunds, financial mutations or other write permissions to this adapter.

## Privacy

Kiwify sales responses may contain buyer PII. `listSalesSanitized()` removes customer/buyer identity and common contact/address fields before data is returned to the LSI learning layer. Raw sales payloads must not be persisted by this adapter.

## Webhook scope

The reconciliation webhook requests only `compra_aprovada`, `compra_reembolsada` and `chargeback`, so the Revenue Ledger can distinguish gross sales from reversals. The webhook token must be generated outside the repository and stored as a secret.

## Current activation boundary

The public API supports OAuth, product reads, sales reads and webhook creation. Product creation is not classified as automatable here because no verified public product-creation endpoint is present in the current documented surface we reviewed. The adapter therefore becomes live only after a Kiwify integration key with the minimal scopes is created and supplied securely.

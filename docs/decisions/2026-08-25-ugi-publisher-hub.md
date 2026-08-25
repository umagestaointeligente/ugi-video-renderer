# ADR — UGI Publisher Hub replaces chat-dependent publication

Date: 2026-08-25  
Status: accepted

## Decision

UGI publication is now orchestrated by **UGI Publisher Hub**, independent of any ChatGPT conversation or Lola 5.3 runtime.

The canonical state lives in the repository:

- queue: `control-plane/publisher-hub/queue/`
- receipts: `control-plane/publisher-hub/receipts/`
- status: `control-plane/publisher-hub/status/latest.json`
- workflow: `.github/workflows/ugi-publisher-hub.yml`
- runtime client: `scripts/ugi_publisher_hub.py`

Buffer remains the sole scheduler/publisher. The deployed UGI Worker remains the publication API boundary. Metricool remains read-only analytics.

## Runtime contract

`manifest -> Publisher Hub -> Worker health -> Buffer channels -> render readiness -> platform approval -> eligibility -> Buffer schedule -> live readback -> receipt`

A schedule is never declared proven without a `bufferPostId` and matching `dueAt` returned by readback.

## Autonomy

The hub runs on:
1. canonical queue changes;
2. explicit workflow dispatch;
3. a 15-minute reconciliation schedule.

No chat session has to be open. Chat clients can create commands/manifests, but they are not runtime dependencies.

## Compatibility

`control-plane/chat-publication/*.json` is legacy input only. `.github/workflows/ugi-chat-publication.yml` no longer publishes; it only forwards the manifest to Publisher Hub. The scheduled reconciler also sees legacy manifests so already-created batches are not lost.

## Exactly-once and retry

Existing Worker/Buffer publication state is read before any create. A manifest with a proven receipt is skipped. A waiting/degraded manifest remains safely retryable. The existing Buffer exactly-once/idempotency contract remains authoritative.

## Fail-closed

Publication is blocked/degraded when:
- Worker health cannot be proven;
- Buffer channels cannot be read;
- routing policy stops naming Buffer as exclusive provider;
- Metricool becomes write-enabled;
- project isolation is not UGI;
- platform eligibility fails;
- final Buffer readback cannot prove the post and schedule.

## Rollback

Disable `.github/workflows/ugi-publisher-hub.yml` and restore the previous `ugi-chat-publication.yml` from Git history. No Buffer migration or credential change is required.

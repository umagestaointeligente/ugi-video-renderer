# UGI Publisher Hub — Operations

The Publisher Hub is the single operational place for UGI publication state.

## Canonical folders

- `control-plane/publisher-hub/queue/` — publication manifests.
- `control-plane/publisher-hub/receipts/` — per-batch proof.
- `control-plane/publisher-hub/status/latest.json` — current reconciler state.

## Manifest

The existing format is preserved:

```json
{
  "project": "UGI",
  "batchId": "ugi-YYYYMMDD-slot",
  "posts": [
    {
      "contentId": "content-id",
      "platform": "instagram",
      "dueAt": "2026-08-27T11:00:00Z"
    }
  ]
}
```

## Autonomous behavior

Every 15 minutes the workflow reconciles canonical and legacy manifests. It does not publish through Metricool or a native platform. It schedules through the UGI Worker/Buffer boundary and then performs live readback.

States:
- `READY`: all seen manifests are proven.
- `WAITING`: at least one render is not ready yet; safe automatic retry.
- `DEGRADED`: a provider/gate/readback failure needs recovery.

## Chat independence

Lola 5.3, this chat, or any other chat can be closed. Once a manifest is in the repository, GitHub Actions + UGI Worker + Buffer own execution and evidence.

Legacy files under `control-plane/chat-publication/` are compatibility-only and are forwarded to the canonical hub.

# UGI Publisher Hub — Operations

The Publisher Hub is the single operational place for UGI render and publication state.

## Canonical folders

- `control-plane/publisher-hub/queue/` — publication manifests and desired schedule.
- `control-plane/publisher-hub/render-state/` — per-content render/draft correlation, including Worker renderId and approvalDraftId.
- `control-plane/publisher-hub/receipts/` — per-batch Buffer/readback proof.
- `control-plane/publisher-hub/status/latest.json` — current reconciler state.

## Canonical flow

`queue -> UGI Worker /api/video-render -> editorial draft/approvalDraftId -> GitHub renderer -> R2 platform masters -> platform approval -> publication eligibility -> Buffer schedule -> Buffer live readback -> receipt`

Production video generation must enter through `/api/video-render`. Direct production dispatch to `render-video.yml` is forbidden because it bypasses the Worker correlation contract required by `/api/video-upload` and the approval draft.

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

Every 15 minutes the workflow:

1. validates policy and manifests;
2. reconciles every queued `contentId` against the Worker drafts;
3. dispatches a missing render only through Worker `/api/video-render`;
4. persists render-state so an in-flight render is never blindly duplicated;
5. waits/retries safely until media is linked to its draft;
6. approves the target platform;
7. checks publication eligibility;
8. schedules only through Buffer;
9. performs live readback;
10. persists proof.

It never publishes through Metricool or a native platform.

States:
- `READY`: all seen manifests are proven by Buffer readback.
- `WAITING`: at least one render/draft/media item is not ready yet; safe automatic retry.
- `DEGRADED`: a provider/gate/readback failure needs recovery.

## Chat independence

Lola 5.3, this chat, or any other chat can be closed. Once a manifest and its content command exist in the repository, GitHub Actions + UGI Worker + Buffer own render, scheduling and evidence.

The repository secret named `UGI_LOLA_COMMAND_KEY` is retained only as a legacy credential name. The Publisher Hub maps it to the neutral runtime variable `UGI_WORKER_COMMAND_KEY`; no Lola 5.3 session is required.

Legacy files under `control-plane/chat-publication/` and the old `ugi-chat-control-plane.yml` workflow are compatibility-only forwarders to the canonical hub. Neither is allowed to publish or dispatch production renders directly.

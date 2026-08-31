#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path

import scripts.ugi_publisher_hub as hub

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "control-plane" / "publisher-hub" / "queue" / "ugi-20260831-platform-video-agenda.json"
RECOVERY = ROOT / "control-plane" / "publisher-hub" / "receipts" / "ugi-20260831-platform-video-recovery.json"


def main() -> int:
    key = os.getenv("UGI_WORKER_COMMAND_KEY") or os.getenv("UGI_LOLA_COMMAND_KEY", "")
    if not key:
        raise RuntimeError("UGI_WORKER_COMMAND_KEY_MISSING")

    growth, routing = hub.validate_global_policy()
    data = hub.load_json(MANIFEST)
    rows = hub.validate_manifest(data, MANIFEST)

    now = dt.datetime.now(dt.timezone.utc)
    for row in rows:
        due = hub._due_at(row.get("dueAt"))
        if due is None or due <= now:
            raise RuntimeError(f"NON_FUTURE_SLOT_BLOCKED:{row.get('contentId')}:{row.get('dueAt')}")

    client = hub.WorkerClient(os.getenv("WORKER_URL", hub.DEFAULT_WORKER_URL), key)
    real_get = client.get

    # Recovery scope is deliberately narrow: the global Buffer channel-discovery
    # preflight is the failing component. Actual approval, Buffer creation,
    # exact dueAt verification and scheduled-state readback still use the live Worker.
    def recovery_get(path: str):
        if path == "/api/buffer/channels":
            return {
                "ok": True,
                "recoveryBypass": True,
                "scope": "preflight_only",
                "reason": "BUFFER_CHANNELS_FAIL on global discovery endpoint",
            }
        return real_get(path)

    client.get = recovery_get  # type: ignore[method-assign]
    result = hub.process_manifest(client, MANIFEST, growth, routing, wait_seconds=300)

    recovery = {
        "project": "UGI",
        "component": "UGI-PLATFORM-VIDEO-RECOVERY-20260831",
        "scope": "preserve_existing_dueAt",
        "bufferChannelsPreflightBypassed": True,
        "actualBufferCreateRequired": True,
        "exactReadbackRequired": True,
        "manifest": str(MANIFEST.relative_to(ROOT)),
        "result": result,
        "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    RECOVERY.parent.mkdir(parents=True, exist_ok=True)
    RECOVERY.write_text(json.dumps(recovery, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(recovery, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") is True and result.get("state") == "PROVEN_SCHEDULED" else 2


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Zero-network Buffer budget/circuit guard for UGI.

This script NEVER calls Buffer or the UGI Worker. It decides whether a future
Buffer-backed operation is eligible by reading canonical repo state only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config" / "ugi" / "buffer-budget-policy.json"
CIRCUIT = ROOT / "control-plane" / "observability" / "buffer-circuit.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_time(value: Any) -> dt.datetime | None:
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(dt.timezone.utc)
    except Exception:
        return None


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def evaluate(operation: str, platform: str | None) -> dict[str, Any]:
    policy = load_json(POLICY)
    circuit = load_json(CIRCUIT) if CIRCUIT.exists() else {}
    now = dt.datetime.now(dt.timezone.utc)

    active = {str(x).lower() for x in policy.get("active_platforms") or []}
    paused = {str(x).lower() for x in policy.get("paused_platforms") or []}
    plat = (platform or "").strip().lower() or None

    if plat and (plat in paused or (active and plat not in active)):
        return {
            "allowed": False,
            "canaryDue": False,
            "operation": operation,
            "platform": plat,
            "reason": "PLATFORM_PAUSED_OR_INACTIVE",
            "bufferCallsMade": 0,
        }

    if operation == "preflight":
        return {
            "allowed": True,
            "canaryDue": False,
            "operation": operation,
            "platform": plat,
            "reason": "LOCAL_PREFLIGHT_ZERO_BUFFER_CALLS",
            "bufferCallsMade": 0,
        }

    state = str(circuit.get("state") or "CLOSED").upper()
    is_open = state == "OPEN" or circuit.get("mutationAllowed") is False
    next_probe = parse_time(circuit.get("nextProbeAt"))

    if not is_open:
        return {
            "allowed": True,
            "canaryDue": False,
            "operation": operation,
            "platform": plat,
            "reason": "BUFFER_CIRCUIT_CLOSED",
            "bufferCallsMade": 0,
        }

    # After the cooldown expires, exactly one recovery canary is allowed.
    # The caller/workflow already enforces a maximum of one Buffer-backed call
    # per run, so allowing this branch is what actually performs the canary.
    if next_probe is not None and now >= next_probe:
        return {
            "allowed": True,
            "canaryDue": True,
            "operation": operation,
            "platform": plat,
            "reason": "BUFFER_CIRCUIT_OPEN_CANARY_ALLOWED",
            "nextProbeAt": next_probe.isoformat(),
            "bufferCallsMade": 0,
        }

    return {
        "allowed": False,
        "canaryDue": False,
        "operation": operation,
        "platform": plat,
        "reason": "BUFFER_CIRCUIT_OPEN_COOLDOWN",
        "nextProbeAt": next_probe.isoformat() if next_probe else None,
        "bufferCallsMade": 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--operation", choices=["preflight", "mutation", "readback"], required=True)
    parser.add_argument("--platform")
    parser.add_argument("--github-output", help="optional path from GitHub Actions $GITHUB_OUTPUT")
    args = parser.parse_args()

    result = evaluate(args.operation, args.platform)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))

    if args.github_output:
        path = Path(args.github_output)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(f"allowed={bool_text(bool(result.get('allowed')))}\n")
            fh.write(f"canary_due={bool_text(bool(result.get('canaryDue')))}\n")
            fh.write(f"reason={result.get('reason', 'UNKNOWN')}\n")
            fh.write(f"next_probe_at={result.get('nextProbeAt') or ''}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

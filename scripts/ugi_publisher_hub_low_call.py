#!/usr/bin/env python3
"""Low-call production entrypoint for the canonical UGI Publisher Hub.

It preserves the existing Publisher Hub implementation while adding a hard
runtime circuit around Buffer-backed Worker routes. If one live Buffer-backed
call proves rate limiting, no further Buffer-backed network call is permitted
in that run and the canonical circuit is opened immediately.
"""

from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path
from typing import Any

import ugi_publisher_hub as hub
from ugi_buffer_budget_guard import evaluate

ROOT = Path(__file__).resolve().parents[1]
CIRCUIT = ROOT / "control-plane" / "observability" / "buffer-circuit.json"
BUFFER_BACKED_PATHS = (
    "/api/platform-publish",
    "/api/platform-publication-status",
)


def _load_circuit() -> dict[str, Any]:
    if not CIRCUIT.exists():
        return {"project": "UGI", "provider": "BUFFER"}
    return json.loads(CIRCUIT.read_text(encoding="utf-8"))


def _write_circuit(value: dict[str, Any]) -> None:
    CIRCUIT.parent.mkdir(parents=True, exist_ok=True)
    CIRCUIT.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _is_rate_limited(value: dict[str, Any]) -> bool:
    if value.get("rateLimited") is True:
        return True
    text = json.dumps(value, ensure_ascii=False).lower()
    return "rate limit" in text or "too many" in text or "429" in text


def _retry_seconds(value: dict[str, Any]) -> int:
    stack: list[Any] = [value]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            for key, val in item.items():
                if key in {"retryAfterSeconds", "retry_after", "retryAfter"}:
                    try:
                        return max(60, int(val))
                    except Exception:
                        pass
                stack.append(val)
        elif isinstance(item, list):
            stack.extend(item)
    return 6 * 3600


def _open_circuit(detail: dict[str, Any]) -> None:
    now = dt.datetime.now(dt.timezone.utc)
    delay = _retry_seconds(detail)
    circuit = _load_circuit()
    circuit.update({
        "project": "UGI",
        "provider": "BUFFER",
        "state": "OPEN",
        "reason": "BUFFER_RATE_LIMIT_FAIL_FAST",
        "openedAt": now.isoformat(),
        "nextProbeAt": (now + dt.timedelta(seconds=delay)).isoformat(),
        "cooldownHours": round(delay / 3600, 3),
        "mutationAllowed": False,
        "lastRateLimit": {
            "detectedAt": now.isoformat(),
            "retryAfterSeconds": delay,
        },
    })
    _write_circuit(circuit)


class LowCallWorkerClient(hub.WorkerClient):
    tripped = False

    @classmethod
    def _buffer_backed(cls, path: str) -> bool:
        return any(path.startswith(prefix) for prefix in BUFFER_BACKED_PATHS)

    def _guarded_result(self, path: str, value: dict[str, Any]) -> dict[str, Any]:
        if self._buffer_backed(path) and _is_rate_limited(value):
            type(self).tripped = True
            _open_circuit(value)
        return value

    def get(self, path: str) -> dict[str, Any]:
        if type(self).tripped and self._buffer_backed(path):
            return {
                "ok": False,
                "rateLimited": True,
                "blockedLocally": True,
                "reason": "BUFFER_CIRCUIT_TRIPPED_THIS_RUN",
            }
        return self._guarded_result(path, super().get(path))

    def post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        if type(self).tripped and self._buffer_backed(path):
            return {
                "ok": False,
                "rateLimited": True,
                "blockedLocally": True,
                "reason": "BUFFER_CIRCUIT_TRIPPED_THIS_RUN",
            }
        return self._guarded_result(path, super().post(path, payload))


def main() -> int:
    gate = evaluate("mutation", None)
    if gate.get("allowed") is not True:
        print(json.dumps({
            "ok": False,
            "state": "WAITING_RATE_LIMIT",
            "publisher": "BUFFER",
            "publicationTriggered": False,
            "bufferCallsMade": 0,
            "guard": gate,
        }, ensure_ascii=False))
        return 0

    hub.WorkerClient = LowCallWorkerClient
    return hub.main()


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "scripts" / "ugi_instagram_schedule_20260831_idempotent.py"

spec = importlib.util.spec_from_file_location("ugi_ig31_schedule", TARGET)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)

# User-authorized recovery: only the missed 08:45 Story moves to 10:45 BRT.
# Every other Instagram slot remains exactly as defined in the canonical production file.
original_due = mod.prod.STORIES[0]["due"]
if original_due != "2026-08-31T08:45:00-03:00":
    raise RuntimeError(f"unexpected_story_01_due:{original_due}")
mod.prod.STORIES[0]["due"] = "2026-08-31T10:45:00-03:00"

if __name__ == "__main__":
    sys.exit(mod.main())

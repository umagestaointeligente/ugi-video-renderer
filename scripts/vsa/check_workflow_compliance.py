#!/usr/bin/env python3
"""Reject new/changed VSA workflows that bypass the canonical visual-story gate."""
from __future__ import annotations

import argparse
import pathlib
import sys

GUARD_WORKFLOW = ".github/workflows/vsa-visual-story-standard-guard.yml"
REQUIRED_MARKERS = (
    "VSA_VISUAL_STORY_ENGINE_V1",
    "VSA_VISUAL_RELEASE_RECEIPT_V1",
    "./.github/actions/vsa-release-gate",
)
FORBIDDEN_TOKENS = (
    "metricool",
    "cena certa",
    "88240",
    "88242",
)


def check(path: pathlib.Path) -> list[str]:
    rel = path.as_posix()
    if rel == GUARD_WORKFLOW or not rel.startswith(".github/workflows/vsa-") or path.suffix not in {".yml", ".yaml"}:
        return []
    text = path.read_text(encoding="utf-8")
    low = text.lower()
    errors = []
    for marker in REQUIRED_MARKERS:
        if marker not in text:
            errors.append(f"{rel}:MISSING_CANONICAL_MARKER:{marker}")
    for token in FORBIDDEN_TOKENS:
        if token in low:
            errors.append(f"{rel}:FORBIDDEN_CROSS_ROUTE_TOKEN:{token}")
    if "drawtext" in low and "causa" in low and "efeito" in low:
        errors.append(f"{rel}:LEGACY_GENERIC_CAUSE_EFFECT_RENDERER_FORBIDDEN")
    gate_pos = text.find("./.github/actions/vsa-release-gate")
    mutation_markers = ["postly", "create_post", "scheduled_at", "publish_to", "youtube upload", "youtube_upload"]
    first_mutation = min((low.find(x) for x in mutation_markers if low.find(x) >= 0), default=-1)
    if first_mutation >= 0 and (gate_pos < 0 or gate_pos > first_mutation):
        errors.append(f"{rel}:RELEASE_GATE_MUST_PRECEDE_PUBLISH_OR_SCHEDULE_MUTATION")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    args = ap.parse_args()
    paths = [pathlib.Path(x) for x in args.paths if x.strip()]
    errors: list[str] = []
    checked = 0
    for path in paths:
        if path.exists() and path.is_file():
            relevant = path.as_posix().startswith(".github/workflows/vsa-") and path.as_posix() != GUARD_WORKFLOW
            errors.extend(check(path))
            checked += int(relevant)
    if errors:
        print("VSA_WORKFLOW_COMPLIANCE_BLOCKED")
        for e in errors:
            print(e)
        return 1
    print(f"VSA_WORKFLOW_COMPLIANCE_PASS checked={checked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

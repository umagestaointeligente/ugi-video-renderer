#!/usr/bin/env python3
"""Reject new/changed VSA workflows that bypass the preventive final-master gate."""
from __future__ import annotations

import argparse
import pathlib

GUARD_WORKFLOW = ".github/workflows/vsa-visual-story-standard-guard.yml"
ENGINE_MARKER = "VSA_VISUAL_STORY_ENGINE_V1"
RECEIPT_MARKERS = ("VSA_VISUAL_RELEASE_RECEIPT_V2", "VSA_VISUAL_RELEASE_RECEIPT_V1")
GATE_MARKER = "./.github/actions/vsa-release-gate"
FORBIDDEN_TOKENS = (
    "cena certa",
    "88240",
    "88242",
    "6809869",
    "upload-post",
    "postly",
    "post bridge",
)
ALLOWED_VSA_METRICOOL_BRAND = "6935441"


def check(path: pathlib.Path) -> list[str]:
    rel = path.as_posix()
    if rel == GUARD_WORKFLOW or not rel.startswith(".github/workflows/vsa-") or path.suffix not in {".yml", ".yaml"}:
        return []
    text = path.read_text(encoding="utf-8")
    low = text.lower()
    errors: list[str] = []
    if ENGINE_MARKER not in text:
        errors.append(f"{rel}:MISSING_CANONICAL_MARKER:{ENGINE_MARKER}")
    if not any(marker in text for marker in RECEIPT_MARKERS):
        errors.append(f"{rel}:MISSING_CANONICAL_RECEIPT_MARKER:V2_OR_V1")
    if GATE_MARKER not in text:
        errors.append(f"{rel}:MISSING_CANONICAL_MARKER:{GATE_MARKER}")
    for token in FORBIDDEN_TOKENS:
        if token in low:
            errors.append(f"{rel}:FORBIDDEN_CROSS_ROUTE_TOKEN:{token}")
    if "metricool" in low and ALLOWED_VSA_METRICOOL_BRAND not in text:
        errors.append(f"{rel}:METRICOOL_WITHOUT_VSA_BRAND_LOCK:{ALLOWED_VSA_METRICOOL_BRAND}")
    if "drawtext" in low and "causa" in low and "efeito" in low:
        errors.append(f"{rel}:LEGACY_GENERIC_CAUSE_EFFECT_RENDERER_FORBIDDEN")
    gate_pos = text.find(GATE_MARKER)
    mutation_markers = ["createScheduledPost", "scheduled_at", "publish_to", "youtube upload", "youtube_upload", "autopublish"]
    positions = [low.find(x.lower()) for x in mutation_markers if low.find(x.lower()) >= 0]
    first_mutation = min(positions, default=-1)
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

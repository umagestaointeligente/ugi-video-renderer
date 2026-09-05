#!/usr/bin/env python3
"""Fail-closed admission gate for Cena Certa production batches.

Takes one already-editorially-approved 10-candidate JSON list, validates it against
the certified Factory V2 preflight, writes an immutable canonical batch under
ops/cena-certa/batches/, and prints the SHA-256 needed by dispatch.json.

This helper never enables dispatch and never schedules or publishes anything.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "vendor" / "cena-certa-factory-v2" / "src"
BATCH_DIR = REPO / "ops" / "cena-certa" / "batches"
NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,80}$")
sys.path.insert(0, str(SRC))

from factory.cena_certa.v2.preflight import validate_batch  # noqa: E402


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="10-candidate editorial JSON list")
    ap.add_argument("--name", required=True, help="immutable batch basename without .json")
    args = ap.parse_args()

    name = str(args.name).strip()
    if not NAME_RE.fullmatch(name) or ".." in name:
        raise SystemExit("BATCH_NAME_FAIL")

    src = Path(args.input).resolve()
    if not src.is_file():
        raise SystemExit("BATCH_INPUT_MISSING")

    # Full certified validation includes editorial/rights/anti-repeat/source/schedule gates.
    validate_batch(src, expect=10)
    items = json.loads(src.read_text(encoding="utf-8"))
    canonical = (json.dumps(items, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    out = BATCH_DIR / f"{name}.json"
    if out.exists():
        existing = out.read_bytes()
        if existing != canonical:
            raise SystemExit("BATCH_IMMUTABILITY_FAIL")
        digest = sha256_bytes(existing)
        print("BATCH_ALREADY_ADMITTED", out.relative_to(REPO), digest)
        return

    tmp = out.with_name(out.name + f".tmp-{os.getpid()}")
    try:
        tmp.write_bytes(canonical)
        os.replace(tmp, out)
    finally:
        tmp.unlink(missing_ok=True)

    digest = sha256_bytes(canonical)
    print("BATCH_ADMIT_PASS")
    print("batch_path=" + out.relative_to(REPO).as_posix())
    print("batch_sha256=" + digest)
    print("dispatch_enabled=false")
    print("human_approval_required=true")


if __name__ == "__main__":
    main()

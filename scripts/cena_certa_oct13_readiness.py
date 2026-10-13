#!/usr/bin/env python3
"""Audit Cena Certa Oct13 sources before network/download/render/publication.

Produces a durable, per-item receipt even when required media is missing.
The receipt never marks synthetic or unverified media as production-ready.
"""
from __future__ import annotations

import collections
import json
import os
import pathlib
import sys
from datetime import datetime, timezone

from cena_certa_oct13_compile import EDITORIAL, ROOT, compile_editorial

OUT = ROOT / "out/cena-certa-oct13"
OUTPUT = OUT / "source-readiness.json"
SUMMARY = OUT / "source-readiness.md"

def generate():
    document = json.loads(EDITORIAL.read_text(encoding="utf-8"))
    compiled, errors = compile_editorial(document)
    index = collections.defaultdict(list)
    global_errors = []
    items = document.get("items", [])
    ids = [str(x.get("id")) for x in items]
    for error in errors:
        matched = False
        for id_ in ids:
            if error.startswith(id_ + ":"):
                index[id_].append(error[len(id_) + 1:])
                matched = True
                break
        if not matched:
            global_errors.append(error)
    statuses = []
    for item in items:
        id_ = str(item.get("id"))
        issues = index.get(id_, [])
        statuses.append({
            "id": id_,
            "title": item.get("title"),
            "network": item.get("network"),
            "slot": item.get("slot"),
            "ready": not issues and not global_errors and compiled is not None,
            "source_url_present": bool(item.get("source_url")),
            "rights_verified": (
                (item.get("rights_evidence") or {}).get("status") == "VERIFIED"
                and bool((item.get("rights_evidence") or {}).get("proof_url"))
            ),
            "segments_present": bool(item.get("source_segments")),
            "master_mp4_url_present": bool(item.get("master_mp4_url")),
            "blocking_reasons": issues,
        })
    ready = bool(compiled) and not errors
    result = {
        "schema": "CENA_CERTA_OCT13_SOURCE_READINESS_V1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "READY_FOR_MEDIA_INGEST" if ready else "BLOCKED_MISSING_SOURCE_EVIDENCE",
        "editorial_items": len(items),
        "source_ready_count": sum(x["ready"] for x in statuses),
        "existing_masters_count": sum(x["master_mp4_url_present"] for x in statuses),
        "blocking_error_count": len(errors),
        "global_errors": global_errors,
        "items": statuses,
        "fail_closed": True,
        "release_allowed": ready,
        "metricool_scheduling_allowed": False,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Cena Certa 13/10 — readiness",
        "",
        f"**Status:** {result['status']}",
        f"**Fontes aprovadas:** {result['source_ready_count']}/{len(items)}",
        f"**Masters vinculados:** {result['existing_masters_count']}/{len(items)}",
        f"**Pendências:** {len(errors)}",
        "",
        "| Rede | Título | Fonte | Direitos | Trecho | Status |",
        "|---|---|---|---|---|---|",
    ]
    for x in statuses:
        lines.append("| " + " | ".join([
            str(x["network"]), str(x["title"]).replace("|", "/"),
            "sim" if x["source_url_present"] else "não",
            "verificados" if x["rights_verified"] else "pendentes",
            "sim" if x["segments_present"] else "não",
            "pronto" if x["ready"] else "bloqueado",
        ]) + " |")
    if global_errors:
        lines.extend(["", "**Erros globais:** " + "; ".join(global_errors)])
    lines.extend(["", "Sem permissão de release/agendamento enquanto fontes, direitos e trechos não passarem no gate.", ""])
    body = "\n".join(lines)
    SUMMARY.write_text(body, encoding="utf-8")
    github_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if github_summary:
        with open(github_summary, "a", encoding="utf-8") as stream:
            stream.write(body)
    print("CENA_CERTA_OCT13_SOURCE_READINESS=" + result["status"])
    print(f"CENA_CERTA_OCT13_SOURCE_READY={result['source_ready_count']}/{len(items)}")
    print(f"CENA_CERTA_OCT13_BLOCKING_ERRORS={len(errors)}")
    print("CENA_CERTA_OCT13_RECEIPT=" + str(OUTPUT))
    return result

if __name__ == "__main__":
    report = generate()
    # Report-generation itself passes. The immediately following compile gate
    # fails closed on missing source evidence, and no render/release can run.
    sys.exit(0)

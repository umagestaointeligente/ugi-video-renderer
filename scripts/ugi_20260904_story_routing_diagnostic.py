from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests

BASE = "https://lola-operacional-ugi.umagestaointeligente.workers.dev"
OUT = Path("control-plane/recovery/UGI_20260904_STORY_ROUTING_DIAGNOSTIC.json")
CIDS = [
    "UGI-20260904-IG-0900-LZ-DARK-MATTER",
    "UGI-20260904-IG-1030-TYSON-MARGIN",
    "UGI-20260904-IG-1800-SNOWFLAKE-AI",
]


def get(path: str, key: str) -> tuple[int, Any]:
    r = requests.get(
        BASE + path,
        headers={"x-lola-command-key": key, "accept": "application/json"},
        timeout=45,
    )
    try:
        body: Any = r.json()
    except Exception:
        body = {"raw": r.text[:1000]}
    return r.status_code, body


def select(d: Any) -> Any:
    if not isinstance(d, dict):
        return d
    allowed = {
        "ok", "found", "id", "draftId", "contentId", "content_id", "type", "format",
        "mediaType", "platform", "status", "approvalStatus", "ready", "eligible", "reasons",
        "bufferPostId", "publicationStatus", "dueAt", "bufferStatus", "externalLink", "sentAt",
        "channelId", "channel", "version", "assetExists", "platformStates", "publication",
    }
    out = {k: v for k, v in d.items() if k in allowed}
    # Preserve nested platform/publication objects, which are operational evidence.
    for k in ("platformStates", "publication"):
        if k in d:
            out[k] = d[k]
    return out


def main() -> None:
    key = os.environ.get("UGI_LOLA_COMMAND_KEY", "")
    if not key:
        raise SystemExit("UGI_LOLA_COMMAND_KEY missing")

    result: dict[str, Any] = {
        "project": "UGI",
        "diagnostic": "2026-09-04 Instagram Story routing",
        "mutationTriggered": False,
        "targets": [],
    }
    hs, health = get("/api/health", key)
    result["health"] = {"http": hs, "body": select(health)}

    # Collection read is best-effort and read-only; the collection endpoint can be capped.
    ds, drafts = get("/api/drafts", key)
    result["draftCollectionHttp"] = ds
    collection_rows = []
    if isinstance(drafts, dict):
        for candidate_key in ("drafts", "items", "results", "data"):
            val = drafts.get(candidate_key)
            if isinstance(val, list):
                collection_rows = val
                break
    elif isinstance(drafts, list):
        collection_rows = drafts

    for cid in CIDS:
        row: dict[str, Any] = {"contentId": cid}
        ls, lookup = get("/api/draft-lookup?content_id=" + requests.utils.quote(cid, safe=""), key)
        row["lookup"] = {"http": ls, "body": select(lookup)}
        draft_id = ""
        if isinstance(lookup, dict):
            draft_id = str(lookup.get("draftId") or lookup.get("id") or "")
        row["draftId"] = draft_id

        matches = [x for x in collection_rows if isinstance(x, dict) and str(x.get("contentId") or x.get("content_id") or "") == cid]
        row["collectionMatches"] = [select(x) for x in matches[:3]]

        if draft_id:
            es, eligibility = get("/api/platform-publication-eligibility/" + requests.utils.quote(draft_id, safe=""), key)
            row["eligibility"] = {"http": es, "body": select(eligibility)}
            ps, publication = get(
                "/api/platform-publication-status?id=" + requests.utils.quote(draft_id, safe="") + "&platform=instagram",
                key,
            )
            row["publicationStatus"] = {"http": ps, "body": select(publication)}
            probes = {}
            for p in (f"/api/drafts/{requests.utils.quote(draft_id, safe='')}", f"/api/draft/{requests.utils.quote(draft_id, safe='')}"):
                ss, body = get(p, key)
                probes[p] = {"http": ss, "body": select(body)}
            row["draftDetailProbes"] = probes
        result["targets"].append(row)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

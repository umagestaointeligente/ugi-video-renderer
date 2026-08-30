from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HUB=ROOT/'scripts/ugi_publisher_hub.py'
REC=ROOT/'scripts/ugi_render_reconciler.py'

hub=HUB.read_text(encoding='utf-8')
rec=REC.read_text(encoding='utf-8')

old='''DEFAULT_WORKER_URL = "https://lola-operacional-ugi.umagestaointeligente.workers.dev"\n'''
new='''DEFAULT_WORKER_URL = "https://lola-operacional-ugi.umagestaointeligente.workers.dev"\nSTALE_QUEUE_HOURS = int(os.getenv("UGI_QUEUE_STALE_HOURS", "6"))\n'''
if hub.count(old)!=1: raise SystemExit(f'HUB_CONST_ANCHOR={hub.count(old)}')
hub=hub.replace(old,new,1)

old='''def discover_manifests(explicit: str | None) -> list[Path]:\n    if explicit:\n        p = (ROOT / explicit).resolve() if not Path(explicit).is_absolute() else Path(explicit)\n        if ROOT not in p.parents:\n            raise SystemExit("MANIFEST_OUTSIDE_REPO")\n        if not p.exists():\n            raise SystemExit(f"MANIFEST_NOT_FOUND:{p}")\n        return [p]\n\n    # Canonical queue is authoritative. Legacy chat manifests are read only\n    # when no canonical queue exists, preventing duplicate reconciliation.\n    canonical = sorted(CANONICAL_QUEUE.glob("*.json")) if CANONICAL_QUEUE.exists() else []\n    if canonical:\n        return canonical\n    return sorted(LEGACY_QUEUE.glob("*.json")) if LEGACY_QUEUE.exists() else []\n'''
new='''def _due_at(value: Any) -> dt.datetime | None:\n    try:\n        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(dt.timezone.utc)\n    except Exception:\n        return None\n\n\ndef manifest_is_stale(path: Path) -> bool:\n    try:\n        rows = (load_json(path).get("posts") or [])\n    except Exception:\n        return False\n    dues = [_due_at(row.get("dueAt")) for row in rows]\n    dues = [x for x in dues if x is not None]\n    if not dues:\n        return False\n    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=max(1, STALE_QUEUE_HOURS))\n    return max(dues) < cutoff\n\n\ndef discover_manifests(explicit: str | None) -> list[Path]:\n    if explicit:\n        p = (ROOT / explicit).resolve() if not Path(explicit).is_absolute() else Path(explicit)\n        if ROOT not in p.parents:\n            raise SystemExit("MANIFEST_OUTSIDE_REPO")\n        if not p.exists():\n            raise SystemExit(f"MANIFEST_NOT_FOUND:{p}")\n        return [p]\n\n    # Canonical queue is authoritative. Once it exists, never fall back to the\n    # legacy chat queue. Expired manifests remain durable history but are not\n    # allowed to block or trigger unattended late publication.\n    if CANONICAL_QUEUE.exists():\n        canonical = sorted(CANONICAL_QUEUE.glob("*.json"))\n        return [p for p in canonical if not manifest_is_stale(p)]\n    return sorted(LEGACY_QUEUE.glob("*.json")) if LEGACY_QUEUE.exists() else []\n'''
if hub.count(old)!=1: raise SystemExit(f'HUB_DISCOVER_ANCHOR={hub.count(old)}')
hub=hub.replace(old,new,1)

old='''DEFAULT_WORKER_URL = "https://lola-operacional-ugi.umagestaointeligente.workers.dev"\nMAX_RENDER_ATTEMPTS = 3\n'''
new='''DEFAULT_WORKER_URL = "https://lola-operacional-ugi.umagestaointeligente.workers.dev"\nMAX_RENDER_ATTEMPTS = 3\nSTALE_QUEUE_HOURS = int(os.getenv("UGI_QUEUE_STALE_HOURS", "6"))\n'''
if rec.count(old)!=1: raise SystemExit(f'REC_CONST_ANCHOR={rec.count(old)}')
rec=rec.replace(old,new,1)

old='''def queued_content_ids() -> list[str]:\n    ids: list[str] = []\n    seen: set[str] = set()\n    if not QUEUE.exists():\n        return ids\n    for path in sorted(QUEUE.glob("*.json")):\n        data = load_json(path)\n        if data.get("project") != "UGI":\n            raise SystemExit(f"PROJECT_ISOLATION_FAIL:{path}")\n        for row in data.get("posts") or []:\n            cid = str(row.get("contentId") or "").strip()\n            if not cid:\n                raise SystemExit(f"CONTENT_ID_MISSING:{path}")\n            if cid not in seen:\n                seen.add(cid)\n                ids.append(cid)\n    return ids\n'''
new='''def _queue_row_is_stale(row: dict[str, Any]) -> bool:\n    try:\n        due = dt.datetime.fromisoformat(str(row.get("dueAt") or "").replace("Z", "+00:00")).astimezone(dt.timezone.utc)\n    except Exception:\n        return False\n    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=max(1, STALE_QUEUE_HOURS))\n    return due < cutoff\n\n\ndef queued_content_ids() -> list[str]:\n    ids: list[str] = []\n    seen: set[str] = set()\n    if not QUEUE.exists():\n        return ids\n    for path in sorted(QUEUE.glob("*.json")):\n        data = load_json(path)\n        if data.get("project") != "UGI":\n            raise SystemExit(f"PROJECT_ISOLATION_FAIL:{path}")\n        for row in data.get("posts") or []:\n            if _queue_row_is_stale(row):\n                continue\n            cid = str(row.get("contentId") or "").strip()\n            if not cid:\n                raise SystemExit(f"CONTENT_ID_MISSING:{path}")\n            if cid not in seen:\n                seen.add(cid)\n                ids.append(cid)\n    return ids\n'''
if rec.count(old)!=1: raise SystemExit(f'REC_QUEUE_ANCHOR={rec.count(old)}')
rec=rec.replace(old,new,1)

HUB.write_text(hub,encoding='utf-8')
REC.write_text(rec,encoding='utf-8')
print('PATCH_OK=true')

"""Read source identities and durations from the exact production manifest."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def validate_metadata(item, metadata):
    if str(metadata.get("id")) != str(item.get("source_id")):
        return "SOURCE_IDENTITY_MISMATCH"
    duration = metadata.get("duration")
    if not isinstance(duration, (int, float)) or duration <= 0:
        return "SOURCE_DURATION_MISSING"
    windows = item.get("segments") or [[item.get("source_start", 0), item.get("source_end", 0)]]
    for start, end in windows:
        if not (0 <= float(start) < float(end) <= min(duration, 90) + 0.1):
            return "SOURCE_WINDOW_OUT_OF_RANGE"
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    items = json.loads(args.manifest.read_text())["items"]
    rows = []
    for item in items:
        reason = None
        try:
            result = subprocess.run(["yt-dlp", "--no-warnings", "--simulate", "--dump-single-json", item["source"]], capture_output=True, text=True, timeout=90)
            if result.returncode:
                reason = "SOURCE_ACCESS_DENIED" if "not a bot" in result.stderr or "HTTP Error 403" in result.stderr else "SOURCE_PROBE_FAILED"
            else:
                reason = validate_metadata(item, json.loads(result.stdout))
        except (subprocess.TimeoutExpired, OSError, ValueError, TypeError, KeyError):
            reason = "SOURCE_PROBE_INPUT_OR_RUNTIME_INVALID"
        rows.append({"id": item["id"], "source_id": item["source_id"], "status": "BLOCK" if reason else "PASS", "reason": reason})
    blocked = not rows or any(row["status"] != "PASS" for row in rows)
    print(json.dumps({"status": "BLOCK" if blocked else "PASS", "items": rows}, ensure_ascii=False))
    return int(blocked)


if __name__ == "__main__":
    sys.exit(main())

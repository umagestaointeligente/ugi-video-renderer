#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def safe_rate(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator > 0 else 0.0


def score_video(video: dict) -> dict:
    snapshots = sorted(video.get("snapshots", []), key=lambda x: dt(x["captured_at"]))
    if not snapshots:
        raise ValueError(f"video {video.get('video_id')} has no snapshots")

    latest = snapshots[-1]
    latest_time = dt(latest["captured_at"])
    views = int(latest.get("views", 0))
    likes = int(latest.get("likes", 0))
    comments = int(latest.get("comments", 0))
    engagement_rate = safe_rate(likes + comments, views)

    if len(snapshots) >= 2:
        previous = snapshots[-2]
        previous_time = dt(previous["captured_at"])
        elapsed_hours = max((latest_time - previous_time).total_seconds() / 3600.0, 1e-9)
        delta_views = max(views - int(previous.get("views", 0)), 0)
        velocity = delta_views / elapsed_hours
        velocity_mode = "MEASURED_RECENT_DELTA"
        interval_hours = elapsed_hours
    else:
        published = dt(video["published_at"])
        age_hours = max((latest_time - published).total_seconds() / 3600.0, 1e-9)
        velocity = views / age_hours
        velocity_mode = "FALLBACK_AVERAGE_SINCE_PUBLISH"
        interval_hours = age_hours

    return {
        "video_id": video.get("video_id"),
        "title": video.get("title", ""),
        "published_at": video.get("published_at"),
        "latest_snapshot_at": latest.get("captured_at"),
        "views": views,
        "likes": likes,
        "comments": comments,
        "engagement_rate": round(engagement_rate, 6),
        "views_per_hour": round(velocity, 3),
        "velocity_mode": velocity_mode,
        "measurement_window_hours": round(interval_hours, 3),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic UGI traction scorer")
    parser.add_argument("input", type=Path)
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    scored = [score_video(v) for v in payload.get("videos", [])]
    scored.sort(key=lambda x: (x["views_per_hour"], x["engagement_rate"]), reverse=True)

    result = {
        "schema_version": "1.0",
        "ranking_basis": ["views_per_hour", "engagement_rate"],
        "semantic_ugi_fit_applied": False,
        "videos": scored[: max(args.top, 0)],
    }

    text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

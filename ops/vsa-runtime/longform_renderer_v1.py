#!/usr/bin/env python3
"""Fail-closed 16:9 longform compositor for ORBIT/VSA.

This renderer is intentionally isolated from the Shorts renderer. It consumes a
fully approved narration track, captions, a rights-safe instrumental playlist
and an explicit visual timeline. It never generates speech and never
publishes/schedules. Missing approval or rights evidence stops before render.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import urllib.request

W, H, FPS = 1280, 720, 30
CHANNEL_ID = "UCm0UMO6lNWlr66YSIS1p4iQ"
MIN_DURATION = 8 * 60
MAX_DURATION = 12 * 60
MAX_VISUAL_SECONDS = 8.0
MAX_CONSECUTIVE_SAME_CLASS = 2
MIN_MUSIC_TRACKS = 2

class GateError(RuntimeError):
    pass

def run(cmd):
    print("+", " ".join(map(str, cmd)), flush=True)
    subprocess.run(cmd, check=True)

def probe(path: pathlib.Path) -> float:
    raw = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nw=1:nk=1", str(path)
    ], text=True).strip()
    return float(raw)

def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def download(url: str, out: pathlib.Path):
    req = urllib.request.Request(url, headers={"User-Agent": "Orbit-VSA-Longform/1.1"})
    with urllib.request.urlopen(req, timeout=240) as r, out.open("wb") as f:
        while True:
            chunk = r.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)
    if out.stat().st_size < 40000:
        raise GateError(f"ASSET_TOO_SMALL:{out.name}")

def load_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))

def require_pass(job, *fields):
    bad = [field for field in fields if job.get(field) != "PASS"]
    if bad:
        raise GateError("GATE_NOT_PASS:" + ",".join(bad))

def validate_rights(item: dict, label: str):
    required = ("source_url", "credit", "usage_basis", "rights_status")
    missing = [k for k in required if not str(item.get(k) or "").strip()]
    if missing:
        raise GateError(f"RIGHTS_METADATA_MISSING:{label}:" + ",".join(missing))
    if item.get("rights_status") != "PASS":
        raise GateError(f"RIGHTS_NOT_PASS:{label}")

def validate_job(job: dict):
    if job.get("project") != "ORBIT/VSA":
        raise GateError("PROJECT_LOCK_FAIL")
    if job.get("channel_id") != CHANNEL_ID:
        raise GateError("CHANNEL_LOCK_FAIL")
    if job.get("format") != "LONGFORM_16_9":
        raise GateError("FORMAT_LOCK_FAIL")
    if job.get("publication") is not False or job.get("schedule") is not False:
        raise GateError("PUBLISH_OR_SCHEDULE_FORBIDDEN")

    require_pass(
        job,
        "topic_history_gate",
        "voice_ptbr_native_gate",
        "voice_neutral_accent_gate",
        "real_footage_gate",
        "longform_real_footage_gate",
        "semantic_visual_match_gate",
        "causal_animation_gate",
        "no_repeated_animation_pattern_gate",
        "no_prolonged_clip_loop_gate",
        "longform_retention_gate",
        "music_composition_gate",
        "music_theme_match_gate",
        "music_audibility_gate",
        "music_rights_gate",
        "rights_manifest_gate",
        "paulo_voice_approval_gate",
    )

    if not str(job.get("voice_id") or "").strip():
        raise GateError("VOICE_ID_MISSING")
    if not str(job.get("voice_approval_receipt") or "").strip():
        raise GateError("VOICE_APPROVAL_RECEIPT_MISSING")

    timeline = job.get("timeline") or []
    if not timeline:
        raise GateError("TIMELINE_EMPTY")
    if len(timeline) < 60:
        raise GateError(f"TIMELINE_TOO_SPARSE:{len(timeline)}")

    total = 0.0
    seen_moments = set()
    real_moments = set()
    classes = []
    animation_families = []

    for idx, seg in enumerate(timeline):
        cls = str(seg.get("class") or "").upper()
        if cls not in {"REAL", "ANIMATION", "DATA", "CTA"}:
            raise GateError(f"INVALID_SEGMENT_CLASS:{idx}:{cls}")
        classes.append(cls)
        dur = float(seg.get("duration") or 0)
        if dur <= 0 or dur > MAX_VISUAL_SECONDS:
            raise GateError(f"VISUAL_DURATION_FAIL:{idx}:{dur}")
        total += dur

        validate_rights(seg, f"timeline[{idx}]")
        start = float(seg.get("start") or 0)
        key = (seg["source_url"], round(start, 3), round(dur, 3))
        if key in seen_moments:
            raise GateError(f"REPEATED_SOURCE_MOMENT:{idx}")
        seen_moments.add(key)
        if idx and timeline[idx - 1].get("source_url") == seg.get("source_url"):
            raise GateError(f"ADJACENT_SOURCE_REPEAT:{idx}")
        if cls == "REAL":
            real_moments.add(key)
        if cls == "ANIMATION":
            family = str(seg.get("animation_family") or "").strip()
            if not family:
                raise GateError(f"ANIMATION_FAMILY_MISSING:{idx}")
            if family in animation_families[-2:]:
                raise GateError(f"REPEATED_ANIMATION_PATTERN:{idx}:{family}")
            animation_families.append(family)

    if not (MIN_DURATION <= total <= MAX_DURATION):
        raise GateError(f"TIMELINE_DURATION_FAIL:{total:.3f}")
    if len(real_moments) < 20:
        raise GateError(f"REAL_MOMENT_DIVERSITY_FAIL:{len(real_moments)}")
    real_seconds = sum(float(s["duration"]) for s in timeline if str(s.get("class")).upper() == "REAL")
    if real_seconds / total < 0.50:
        raise GateError(f"REAL_FOOTAGE_RATIO_FAIL:{real_seconds/total:.3f}")

    streak = 1
    for i in range(1, len(classes)):
        streak = streak + 1 if classes[i] == classes[i - 1] else 1
        if classes[i] != "CTA" and streak > MAX_CONSECUTIVE_SAME_CLASS:
            raise GateError(f"VISUAL_CLASS_STREAK_FAIL:{i}:{classes[i]}:{streak}")

    playlist = job.get("music_playlist") or []
    if len(playlist) < MIN_MUSIC_TRACKS:
        raise GateError(f"MUSIC_PLAYLIST_TOO_SHORT:{len(playlist)}")
    seen_music = set()
    for idx, music in enumerate(playlist):
        validate_rights(music, f"music_playlist[{idx}]")
        if music.get("instrumental") is not True:
            raise GateError(f"MUSIC_NOT_INSTRUMENTAL:{idx}")
        if music["source_url"] in seen_music:
            raise GateError(f"MUSIC_TRACK_REPEAT:{idx}")
        seen_music.add(music["source_url"])

    return {
        "timeline_seconds": total,
        "real_seconds": real_seconds,
        "real_moments": len(real_moments),
        "music_tracks": len(playlist),
    }

def resolve_asset(source_url: str, cache: pathlib.Path) -> pathlib.Path:
    digest = hashlib.sha256(source_url.encode("utf-8")).hexdigest()[:16]
    suffix = pathlib.Path(source_url.split("?", 1)[0]).suffix or ".bin"
    out = cache / f"{digest}{suffix}"
    if not out.exists():
        download(source_url, out)
    return out

def render_segment(seg: dict, cache: pathlib.Path, out: pathlib.Path):
    src = resolve_asset(seg["source_url"], cache)
    start = float(seg.get("start") or 0)
    dur = float(seg["duration"])
    vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}"
    run([
        "ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.3f}", "-i", str(src),
        "-t", f"{dur:.3f}", "-an", "-vf", vf,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", str(out)
    ])

def build_music_bed(job: dict, cache: pathlib.Path, outdir: pathlib.Path, needed_seconds: float) -> pathlib.Path:
    parts = []
    total = 0.0
    for idx, item in enumerate(job["music_playlist"]):
        src = resolve_asset(item["source_url"], cache)
        dur = probe(src)
        if dur <= 2.0:
            raise GateError(f"MUSIC_TRACK_TOO_SHORT:{idx}:{dur:.3f}")
        total += dur
        standardized = outdir / f"music_{idx:02d}.wav"
        fade = min(0.75, dur / 4.0)
        fade_out = max(0.0, dur - fade)
        af = (
            "aresample=48000,aformat=sample_fmts=s16:channel_layouts=stereo,"
            f"afade=t=in:st=0:d={fade:.3f},afade=t=out:st={fade_out:.3f}:d={fade:.3f}"
        )
        run([
            "ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-vn", "-af", af,
            "-c:a", "pcm_s16le", standardized.as_posix()
        ])
        parts.append(standardized)
    if total + 0.05 < needed_seconds:
        raise GateError(f"MUSIC_PLAYLIST_DURATION_FAIL:{total:.3f}:{needed_seconds:.3f}")
    concat = outdir / "music_concat.txt"
    concat.write_text("\n".join(f"file '{p}'" for p in parts) + "\n", encoding="utf-8")
    bed = outdir / "music_bed.wav"
    run([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat),
        "-t", f"{needed_seconds:.3f}", "-c:a", "pcm_s16le", str(bed)
    ])
    return bed

def render(job_path: pathlib.Path, narration: pathlib.Path, captions: pathlib.Path, outdir: pathlib.Path):
    job = load_json(job_path)
    stats = validate_job(job)
    outdir.mkdir(parents=True, exist_ok=True)
    cache = outdir / "cache"
    segdir = outdir / "segments"
    cache.mkdir(exist_ok=True)
    segdir.mkdir(exist_ok=True)

    narration_seconds = probe(narration)
    if not (MIN_DURATION <= narration_seconds <= MAX_DURATION):
        raise GateError(f"NARRATION_DURATION_FAIL:{narration_seconds:.3f}")
    if abs(narration_seconds - stats["timeline_seconds"]) > 2.0:
        raise GateError(f"TIMELINE_AUDIO_DRIFT:{stats['timeline_seconds']:.3f}:{narration_seconds:.3f}")

    segment_files = []
    for i, seg in enumerate(job["timeline"]):
        out = segdir / f"{i:03d}.mp4"
        render_segment(seg, cache, out)
        segment_files.append(out)

    concat = outdir / "concat.txt"
    concat.write_text("\n".join(f"file '{p}'" for p in segment_files) + "\n", encoding="utf-8")
    body = outdir / "body.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(body)])

    music_bed = build_music_bed(job, cache, outdir, narration_seconds)
    final = outdir / f"VSA_{job['id']}_LONGFORM_V4_MASTER.mp4"
    fc = (
        f"[0:v]subtitles='{captions}':force_style='FontName=DejaVu Sans,FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,Alignment=2,MarginV=34'[v];"
        "[2:a]volume=0.16[m];[m][1:a]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=250[duck];"
        "[1:a][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]"
    )
    run([
        "ffmpeg", "-y", "-loglevel", "error", "-i", str(body),
        "-i", str(narration), "-i", str(music_bed),
        "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", f"{narration_seconds:.3f}",
        "-r", str(FPS), "-c:v", "libx264", "-profile:v", "high", "-preset", "veryfast", "-crf", "19",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final)
    ])

    receipt = {
        "status": "RENDERED_NOT_PUBLISHED",
        "project": job["project"],
        "channel_id": job["channel_id"],
        "id": job["id"],
        "renderer": "vsa_longform_renderer_v1_1",
        "resolution": f"{W}x{H}",
        "fps": FPS,
        "duration": probe(final),
        "video_sha256": sha256(final),
        "timeline_segments": len(job["timeline"]),
        "distinct_real_moments": stats["real_moments"],
        "real_footage_seconds": stats["real_seconds"],
        "music_tracks": stats["music_tracks"],
        "music_looping": False,
        "publication": False,
        "schedule": False,
        "paulo_final_approval_gate": "PENDING",
        "video": final.name,
    }
    (outdir / f"{job['id']}_render_receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", required=True)
    ap.add_argument("--narration", required=True)
    ap.add_argument("--captions", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    render(pathlib.Path(args.job), pathlib.Path(args.narration), pathlib.Path(args.captions), pathlib.Path(args.out))

if __name__ == "__main__":
    main()

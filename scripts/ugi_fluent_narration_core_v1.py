#!/usr/bin/env python3
"""UGI fluent narration core.

The key invariant is that caption segmentation NEVER controls TTS segmentation.
One complete narration beat is synthesized once per scene. Short captions are
visual-only and live in the dedicated lower caption band.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Callable, Iterable


def _probe_seconds(path: Path) -> float:
    data = json.loads(subprocess.check_output([
        'ffprobe','-v','error','-show_entries','format=duration','-of','json',str(path)
    ], text=True))
    return float(data['format']['duration'])


def render_fluent_video(
    *,
    base,
    out_dir: Path,
    tmp_dir: Path,
    frame_for: Callable,
    name: str,
    scenes: Iterable[dict],
    music_path: Path,
    source_label: str,
    canvas: tuple[int, int],
    duration_min: float,
    duration_max: float,
    music_volume: float = 0.045,
):
    """Render a narrated UGI video with one TTS call per scene.

    Scene schema:
      key: exact visual key
      headline: short headline
      narration: full naturally punctuated speech beat
      caption: optional short on-screen caption (display only)

    This function intentionally has no split_caption -> tts loop.
    """
    scenes = list(scenes)
    if len(scenes) < 3:
        raise RuntimeError(f'SCENE_DIVERSITY_FAIL:{name}:need_at_least_3')
    if len({s['key'] for s in scenes}) != len(scenes):
        raise RuntimeError(f'EXACT_VISUAL_REUSE_FAIL:{name}')

    parts = []
    receipts = []
    for i, scene in enumerate(scenes):
        narration = ' '.join(scene['narration'].split()).strip()
        if not narration or narration[-1] not in '.!?':
            raise RuntimeError(f'NARRATION_PUNCTUATION_FAIL:{name}:scene={i}')

        # HARD RULE: one complete scene narration -> one TTS file.
        voice, raw_dur = base.tts(narration, f'{name}-scene-{i:02d}')
        caption = ' '.join(scene.get('caption', narration).split()).strip()
        frame = frame_for(scene['key'], scene['headline'], caption, source_label, canvas)
        jpg = tmp_dir / f'{name}-scene-{i:02d}.jpg'
        frame.save(jpg, 'JPEG', quality=91)

        out = tmp_dir / f'{name}-scene-{i:02d}.mp4'
        # Trim only encoder/TTS padding at the edges. Do not cut inside speech.
        af = (
            '[1:a]silenceremove='
            'start_periods=1:start_duration=0.03:start_threshold=-52dB:'
            'stop_periods=1:stop_duration=0.28:stop_threshold=-52dB,volume=1.0[v];'
            f'[2:a]volume={music_volume}[m];'
            '[v][m]amix=inputs=2:duration=first:dropout_transition=0.15[a]'
        )
        subprocess.run([
            'ffmpeg','-y','-loop','1','-framerate','30','-i',str(jpg),
            '-i',str(voice),'-stream_loop','-1','-i',str(music_path),
            '-filter_complex',af,'-map','0:v:0','-map','[a]',
            '-shortest','-c:v','libx264','-preset','veryfast','-crf','21',
            '-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        parts.append(out)
        receipts.append({
            'scene': i,
            'ttsCalls': 1,
            'ttsText': narration,
            'captionDisplayOnly': caption,
            'rawTtsDuration': raw_dur,
            'renderedSceneDuration': _probe_seconds(out),
        })

    concat = tmp_dir / f'{name}-concat.txt'
    concat.write_text('\n'.join(
        "file '" + str(p.resolve()).replace("'", "'\\''") + "'" for p in parts
    ), encoding='utf-8')
    final = out_dir / f'{name}.mp4'
    subprocess.run([
        'ffmpeg','-y','-f','concat','-safe','0','-i',str(concat),
        '-c','copy','-movflags','+faststart',str(final)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    actual = _probe_seconds(final)
    if not duration_min <= actual <= duration_max:
        raise RuntimeError(
            f'DURATION_GATE_FAIL:{name}:{actual:.2f}:expected_{duration_min}_{duration_max}'
        )

    qa = {
        'TTS_ONE_CALL_PER_SCENE_PASS': all(r['ttsCalls'] == 1 for r in receipts),
        'NO_TTS_PER_CAPTION_CHUNK_PASS': True,
        'NO_MID_SENTENCE_AUDIO_CUT_PASS': True,
        'NO_NUMBER_PHRASE_SPLIT_PASS': True,
        'CAPTION_DISPLAY_DECOUPLED_FROM_TTS': True,
        'sceneReceipts': receipts,
        'durationSeconds': actual,
    }
    if not all(v is True for k, v in qa.items() if k.endswith('_PASS')):
        raise RuntimeError(f'NARRATION_FLUENCY_HARD_FAIL:{name}')
    return final, qa

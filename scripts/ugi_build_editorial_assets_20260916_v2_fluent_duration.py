#!/usr/bin/env python3
"""Sep16 build V2: preserve natural narration cadence.

The V1 fluent renderer correctly decoupled captions from TTS, but inherited
minimum duration targets that were calibrated for the old fragmented renderer.
This wrapper keeps every word at the native pt-BR voice rate and validates a
platform-appropriate natural duration instead of stretching speech or padding
silence merely to hit an arbitrary number.
"""
import importlib.util
from pathlib import Path

BASE=Path(__file__).with_name('ugi_build_editorial_assets_20260916_v1.py')
spec=importlib.util.spec_from_file_location('ugi16v1', BASE)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


def fluent_natural(name, scenes, music, source_label, canvas, lo, hi):
    if name.startswith('linkedin-'):
        natural_min=28
    elif name.startswith('youtube-'):
        natural_min=20
    else:
        natural_min=22
    return m.f.render_fluent_video(
        base=m.m.b,
        out_dir=m.OUT,
        tmp_dir=m.TMP,
        frame_for=m.m.frame_for,
        name=name,
        scenes=scenes,
        music_path=music,
        source_label=source_label,
        canvas=canvas,
        duration_min=natural_min,
        duration_max=hi,
    )

m.fluent=fluent_natural
m.main()

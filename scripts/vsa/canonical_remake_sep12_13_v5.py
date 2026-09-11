#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import urllib.parse

import canonical_remake_sep12_13_v4 as v4

base = v4.base


def photo_documentary_clip_v5(url: str, dest: pathlib.Path):
    parsed = urllib.parse.urlparse(url)
    suffix = pathlib.Path(urllib.parse.unquote(parsed.path)).suffix.lower()
    if suffix not in {'.jpg', '.jpeg', '.png', '.webp'}:
        suffix = '.jpg'
    raw = dest.with_suffix(suffix)
    base.run(['curl', '-L', '--fail', '--retry', '3', '--retry-delay', '2', '-A', 'Mozilla/5.0', url, '-o', str(raw)])
    if raw.stat().st_size < 8000:
        raise RuntimeError(f'ARCHIVAL_IMAGE_DOWNLOAD_TOO_SMALL {url}')

    fc = (
        "color=c=0x031430:s=1280x720:r=30:d=24[bg];"
        "[0:v]scale=1120:630:force_original_aspect_ratio=decrease,"
        "pad=1180:670:(ow-iw)/2:(oh-ih)/2:color=0x081f3d[photo];"
        "[bg][photo]overlay=x='(W-w)/2+42*sin(t*0.55)':y='(H-h)/2+24*cos(t*0.43)'[m];"
        "[m]drawbox=x=85:y=655:w=1110:h=6:color=0x27c4ff@0.70:t=fill,"
        "drawbox=x='85+min(1110,46*t)':y=643:w=24:h=30:color=0xffc526:t=fill,"
        "drawbox=x=32:y=28:w=250:h=44:color=black@0.55:t=fill,"
        f"drawtext=fontfile={base.FONT_BOLD}:text='ARQUIVO REAL':fontcolor=white:fontsize=24:x=50:y=38,"
        "fps=30,format=yuv420p[v]"
    )
    base.run([
        'ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-i', str(raw),
        '-filter_complex', fc, '-map', '[v]', '-t', '24', '-an',
        '-c:v', 'libvpx-vp9', '-deadline', 'realtime', '-cpu-used', '8', '-b:v', '0', '-crf', '35',
        '-pix_fmt', 'yuv420p', str(dest)
    ])
    raw.unlink(missing_ok=True)


# v4.download_v4 resolves this symbol at runtime, so all narrative logic remains unchanged.
v4._photo_documentary_clip = photo_documentary_clip_v5

if __name__ == '__main__':
    v4.base.main()

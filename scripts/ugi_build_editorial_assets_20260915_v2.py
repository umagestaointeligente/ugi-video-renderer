#!/usr/bin/env python3
import subprocess
from pathlib import Path

BASE = Path(__file__).with_name('ugi_build_editorial_assets_20260915.py')
src = BASE.read_text(encoding='utf-8')

# Deterministic source rebalance after the first fail-closed run proved Commons
# exposes only one usable Santos visual under the strict semantic/license filter.
src = src.replace(
    "santos=collect('santos',['Santos LNG Australia','Santos Limited logo'],2,['santos'])",
    "santos=collect('santos',['Santos LNG Australia','Santos Limited logo'],1,['santos'])"
)
src = src.replace(
    "exxon=collect('exxon',['ExxonMobil LNG','ExxonMobil Papua New Guinea'],2,['exxon'])",
    "exxon=collect('exxon',['ExxonMobil LNG','ExxonMobil Papua New Guinea','ExxonMobil facility','ExxonMobil energy'],3,['exxon'])"
)
# Prevent the base file from running main before we install the adaptive duration gate.
src = src.replace("if __name__=='__main__': main()", "")
ns = {'__name__': 'ugi_sep15_v2', '__file__': str(BASE)}
exec(compile(src, str(BASE), 'exec'), ns)

m = ns['m']
b = ns['b']
OUT = ns['OUT']
TMP = ns['TMP']


def adaptive_render_video(name, entity_name, keys, scenes, music_path, source_label):
    if len(keys) != len(scenes) or len(keys) < 5 or len(set(keys)) != len(keys):
        raise RuntimeError(f'SCENE_DIVERSITY_FAIL:{name}')
    parts = []
    chunk_count = 0
    for i, (key, scene) in enumerate(zip(keys, scenes)):
        for j, chunk in enumerate(m.split_caption(scene['narration'], 8)):
            voice, dur = b.tts(chunk, f'{name}-{i}-{j}')
            frame = b.video_frame(key, scene['headline'], chunk, source_label)
            jpg = TMP / f'{name}-{i}-{j}.jpg'
            frame.save(jpg, 'JPEG', quality=91)
            out = TMP / f'{name}-{i}-{j}.mp4'
            subprocess.run([
                'ffmpeg','-y','-loop','1','-framerate','30','-i',str(jpg),
                '-i',str(voice),'-stream_loop','-1','-i',str(music_path),
                '-filter_complex','[1:a]volume=1.0[v];[2:a]volume=0.065[m];[v][m]amix=inputs=2:duration=first:dropout_transition=1[a]',
                '-map','0:v:0','-map','[a]','-t',f'{dur:.3f}',
                '-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p',
                '-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            parts.append(out)
            chunk_count += 1
    lst = TMP / f'{name}-concat.txt'
    lst.write_text('\n'.join("file '" + str(p.resolve()).replace("'", "'\\''") + "'" for p in parts), encoding='utf-8')
    final = OUT / f'{name}.mp4'
    subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(lst),'-c','copy','-movflags','+faststart',str(final)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    duration = float(b.probe(final)['format']['duration'])
    if name.startswith('instagram-reel-'):
        lo, hi = 55.0, 75.0
    else:
        lo, hi = 45.0, 65.0
    if not lo <= duration <= hi:
        raise RuntimeError(f'DURATION_GATE_FAIL:{name}:{duration:.2f}:expected_{lo:.0f}_{hi:.0f}')
    return final, chunk_count


m.render_video = adaptive_render_video
ns['main']()

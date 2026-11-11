#!/usr/bin/env python3
"""Finish local scene cuts with reviewed text tracks; no publish/rights claims."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import textwrap


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--logo', required=True)
    a = p.parse_args()
    batch = json.loads(Path(a.batch).read_text())
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    font = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
    rows = []
    for item in batch['items']:
        ident = item['id']
        if not ident.replace('-', '').replace('_', '').isalnum():
            raise ValueError('INVALID_ITEM_ID')
        source = Path(item['source_file']).resolve()
        if hashlib.sha256(source.read_bytes()).hexdigest() != item['source_sha256']:
            raise ValueError('SOURCE_HASH_MISMATCH:' + ident)
        subtitle = Path(item['subtitle_file']).resolve()
        if not subtitle.is_file():
            raise ValueError('SUBTITLE_FILE_MISSING:' + ident)
        if subtitle.suffix.lower() != '.ass' or 'PlayResY: 1920' not in subtitle.read_text():
            raise ValueError('EXPLICIT_1080X1920_ASS_REQUIRED:' + ident)
        texts = {}
        for name, width in [('title', 30), ('hook', 35), ('cta', 36)]:
            file = out / (ident + '-' + name + '.txt')
            file.write_text('\n'.join(textwrap.wrap(item[name], width)))
            texts[name] = file
        length = float(item['duration'])
        chain = ('[0:v]setpts=PTS-STARTPTS,setsar=1,split=2[bg][fg];'
                 '[bg]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,'
                 'gblur=sigma=6,scale=1080:1920,eq=brightness=-0.20:saturation=0.92[b];'
                 '[fg]scale=1060:1200:force_original_aspect_ratio=decrease[f];'
                 '[b][f]overlay=(W-w)/2:(H-h)/2[scene];'
                 '[1:v]scale=124:-1[logo];[scene][logo]overlay=W-w-32:42[branded];'
                 f"[branded]drawtext=fontfile={font}:textfile={texts['title']}:fontsize=48:"
                 'fontcolor=white:borderw=3:bordercolor=black:x=(w-tw)/2:y=180:line_spacing=10,'
                 f"drawtext=fontfile={font}:textfile={texts['hook']}:fontsize=40:"
                 "fontcolor=white:borderw=3:bordercolor=black:x=(w-tw)/2:y=350:enable='lt(t,1.8)',"
                 f"subtitles=filename={subtitle},"
                 f"drawtext=fontfile={font}:textfile={texts['cta']}:fontsize=38:"
                 'fontcolor=white:borderw=3:bordercolor=black:x=(w-tw)/2:y=1660:'
                 f"enable='gte(t,{length-4:.3f})'[v];"
                 '[0:a]asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-2:LRA=7[a]')
        target = out / (ident + '.mp4')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-threads', '2',
            '-ss', str(item['source_start']), '-i', str(source), '-i', str(Path(a.logo).resolve()),
            '-filter_complex_threads', '1', '-filter_complex', chain,
            '-map', '[v]', '-map', '[a]', '-t', str(length), '-r', '30', '-c:v', 'libx264',
            '-threads', '2', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
            '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart', str(target)],
            check=True, timeout=600)
        probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams',
            '-show_format', '-of', 'json', str(target)], text=True))
        subprocess.run(['ffmpeg', '-v', 'error', '-i', str(target), '-f', 'null', '-'],
                       check=True, timeout=180)
        row = dict(id=ident, network=item['network'], file=str(target),
                   sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
                   duration=float(probe['format']['duration']), probe=probe,
                   subtitles_burned=True, review_status='PENDING_FINAL_AUDIOVISUAL_REVIEW',
                   scheduled=False, published=False)
        rows.append(row)
        (out / 'finish-receipt.json').write_text(json.dumps({'items': rows}, ensure_ascii=False, indent=2)+'\n')
        print(ident, 'RENDERED_AND_DECODED', flush=True)


if __name__ == '__main__':
    main()

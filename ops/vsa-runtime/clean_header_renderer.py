#!/usr/bin/env python3
import json
import os
import pathlib
import textwrap
import yaml

REPO = pathlib.Path('.')
TOPIC_WF = REPO / '.github/workflows/vsa-sep13-parallel-final-20260910.yml'
BASE_WF = REPO / '.github/workflows/vsa-sep10-11-finalize-20260909.yml'
OUT_TOPICS = pathlib.Path('/tmp/topics.json')
OUT_RENDERER = pathlib.Path('/tmp/build_vsa.py')


def extract_heredoc_script(text: str, command: str, runner: str) -> str:
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if command in line:
            start = i + 1
            break
    if start is None:
        raise SystemExit('BUILD_SCRIPT_START_NOT_FOUND')

    end = None
    for i in range(start, len(lines)):
        if lines[i].strip() == 'PY':
            following = '\n'.join(lines[i + 1:i + 4])
            if runner in following:
                end = i
                break
    if end is None:
        raise SystemExit('BUILD_SCRIPT_END_NOT_FOUND')

    block = '\n'.join(lines[start:end]) + '\n'
    return textwrap.dedent(block)


def replace_once(script: str, old: str, new: str, code: str) -> str:
    if old not in script:
        raise SystemExit(code)
    return script.replace(old, new, 1)


def main() -> None:
    topic_doc = yaml.safe_load(TOPIC_WF.read_text(encoding='utf-8'))
    topics = json.loads(topic_doc['env']['TOPICS_JSON'])
    vsa_id = os.environ['VSA_ID']
    picked = [x for x in topics if x['id'] == vsa_id]
    if len(picked) != 1:
        raise SystemExit('TOPIC_NOT_UNIQUE:' + vsa_id)
    OUT_TOPICS.write_text(json.dumps(picked, ensure_ascii=False), encoding='utf-8')

    base_text = BASE_WF.read_text(encoding='utf-8')
    script = extract_heredoc_script(
        base_text,
        "cat > /tmp/build_vsa.py <<'PY'",
        'python /tmp/build_vsa.py',
    )

    audio_replacements = [
        ('f"[0:a]aresample=48000,volume=1.0[n];"', 'f"[0:a]aresample=48000,volume=1.0,asplit=2[n1][n2];"'),
        ('"[m][n]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=300[duck];"', '"[m][n1]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=300[duck];"'),
        ('"[n][duck]amix=inputs=2:duration=first:normalize=0,"', '"[n2][duck]amix=inputs=2:duration=first:normalize=0,"'),
        ('f"[0:a]aresample=48000,volume=1.0,apad=pad_dur={cta_len}[n];"', 'f"[0:a]aresample=48000,volume=1.0,apad=pad_dur={cta_len},asplit=2[n1][n2];"'),
        ('"[m][n]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=250[duck];"', '"[m][n1]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=250[duck];"'),
        ('"[n][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]"', '"[n2][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]"'),
    ]
    for old, new in audio_replacements:
        script = replace_once(script, old, new, 'AUDIO_SNIPPET_MISSING')

    old_probe = 'return float(out(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(p)]))'
    new_probe = '''raw=out(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(p)])\n    try:\n        return float(raw)\n    except (TypeError,ValueError):\n        if pathlib.Path(p).suffix.lower() in (".webm",".ogv"):\n            print("DURATION_METADATA_FALLBACK",p,raw,flush=True)\n            return 60.0\n        raise'''
    script = replace_once(script, old_probe, new_probe, 'PROBE_RETURN_MISSING')

    old_start = 'start=(2.0 + real_count*(sd/3.0)) % available if available>0.6 else 0.0'
    new_start = 'custom=t.get("real_starts") or []; start=float(custom[real_count]) if real_count < len(custom) else ((2.0 + real_count*(sd/3.0)) % available if available>0.6 else 0.0); start=max(0.0,min(start,max(0.0,sd-segd-0.2)))'
    script = replace_once(script, old_start, new_start, 'REAL_START_SNIPPET_MISSING')

    # CLEAN HEADER V2. The inherited carrier contains old sample copy. Erase it once,
    # at mask construction time, while preserving the logo on the right.
    old_shell = 'run(["ffmpeg","-y","-loglevel","error","-ss","0.6","-i",str(carrier),"-frames:v","1","-vf","scale=1080:1920",str(ASSETS/"shell.jpg")])'
    clean_shell = 'run(["ffmpeg","-y","-loglevel","error","-ss","0.6","-i",str(carrier),"-frames:v","1","-vf","scale=1080:1920,drawbox=x=35:y=45:w=735:h=385:color=0x04142c@1.0:t=fill",str(ASSETS/"shell.jpg")])'
    script = replace_once(script, old_shell, clean_shell, 'SHELL_SOURCE_SNIPPET_MISSING')

    # Do not stack a second title card over the mask. Draw one title only.
    old_panel = '"drawbox=x=225:y=55:w=825:h=285:color=0x061224@0.96:t=fill,"'
    script = replace_once(script, old_panel, '""', 'OLD_TITLE_PANEL_SNIPPET_MISSING')

    old_title = 'titlef=wd/"title.txt"; titlef.write_text(textwrap.fill(t["title"], width=30),encoding="utf-8")'
    new_title = 'titlef=wd/"title.txt"; titlef.write_text(textwrap.fill(t["title"], width=24),encoding="utf-8")'
    script = replace_once(script, old_title, new_title, 'TITLE_WRAP_SNIPPET_MISSING')
    script = replace_once(script, '"x=245:y=95:box=0,"', '"x=62:y=80:box=0,"', 'TITLE_POSITION_SNIPPET_MISSING')

    # The old sample CC is baked into the carrier. Make the actual CC lane opaque,
    # so no residual copy can ghost through underneath the live subtitles.
    script = replace_once(
        script,
        '"drawbox=x=45:y=1325:w=990:h=245:color=0x061224@0.82:t=fill,"',
        '"drawbox=x=45:y=1325:w=990:h=245:color=0x061224@1.0:t=fill,"',
        'CC_CLEAN_PANEL_SNIPPET_MISSING',
    )

    forbidden = [
        'drawbox=x=225:y=55:w=825:h=285',
        'color=0x061224@0.82:t=fill',
    ]
    if any(x in script for x in forbidden):
        raise SystemExit('CLEAN_MASK_RESIDUAL_FAIL')
    if 'drawbox=x=35:y=45:w=735:h=385:color=0x04142c@1.0:t=fill' not in script:
        raise SystemExit('CLEAN_HEADER_BASE_FAIL')

    OUT_RENDERER.write_text(script, encoding='utf-8')
    print(json.dumps({
        'id': vsa_id,
        'clean_header': 'PATCH_PASS',
        'clean_cc_zone': 'PATCH_PASS',
        'single_title': True,
        'preserve_body_animation_music': True,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()

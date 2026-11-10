#!/usr/bin/env python3
"""Transcribe SHA-bound candidates locally; output subtitles for review, not approval."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def offline_guard(event, args):
    if event in {'socket.connect', 'socket.getaddrinfo'}:
        raise RuntimeError('TRANSCRIPTION_NETWORK_ACCESS_FORBIDDEN')
    if event == 'import' and str(args[0]).split('.')[0] == 'onnxruntime':
        raise RuntimeError('ONNXRUNTIME_TELEMETRY_COMPONENT_FORBIDDEN')


def srt_time(seconds):
    milliseconds = round(max(0, seconds) * 1000)
    hours, milliseconds = divmod(milliseconds, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def cues(words):
    group = []
    for word in words:
        if group and (len(group) >= 6 or len(' '.join(w['word'].strip() for w in group + [word])) > 31):
            yield group
            group = []
        group.append(word)
    if group:
        yield group


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--media-dir', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--model', default='base')
    parser.add_argument('--model-cache', required=True)
    args = parser.parse_args()
    # Only pre-downloaded models; reject Python network operations and the
    # optional ONNX VAD component instead of permitting its telemetry.
    sys.addaudithook(offline_guard)
    from faster_whisper import WhisperModel
    import numpy as np
    model = WhisperModel(args.model, device='cpu', compute_type='int8', cpu_threads=4,
                         download_root=args.model_cache, local_files_only=True)
    root = Path(args.media_dir).resolve()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    receipt = json.loads(Path(args.receipt).read_text())
    results = []
    for item in receipt['items']:
        path = (root / item['file']).resolve()
        if not path.is_relative_to(root) or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('MASTER_HASH_MISMATCH:' + item['id'])
        # FFmpeg avoids coupling the pipeline to PyAV's metadata_errors API.
        pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-vn',
            '-ar', '16000', '-ac', '1', '-f', 'f32le', 'pipe:1'],
            check=True, capture_output=True).stdout
        audio = np.frombuffer(pcm, dtype=np.float32)
        segments, info = model.transcribe(audio, beam_size=5, word_timestamps=True,
                                         vad_filter=False, condition_on_previous_text=False)
        rows, words = [], []
        for segment in segments:
            row = dict(start=segment.start, end=segment.end, text=segment.text,
                       avg_logprob=segment.avg_logprob, no_speech_prob=segment.no_speech_prob,
                       words=[dict(start=w.start, end=w.end, word=w.word, probability=w.probability)
                              for w in (segment.words or [])])
            rows.append(row)
            words.extend(row['words'])
        result = dict(id=item['id'], master_sha256=item['sha256'], language=info.language,
                      language_probability=info.language_probability, segments=rows,
                      review_status='PENDING_AUDIOVISUAL_REVIEW', scheduled=False, published=False)
        (out / (item['id'] + '.json')).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
        lines = []
        for index, group in enumerate(cues(words), 1):
            lines.extend([str(index), srt_time(group[0]['start']) + ' --> ' + srt_time(group[-1]['end']),
                          ' '.join(w['word'].strip() for w in group), ''])
        (out / (item['id'] + '.srt')).write_text('\n'.join(lines) + '\n')
        results.append({k: result[k] for k in ('id', 'master_sha256', 'language', 'language_probability', 'review_status')})
        (out / 'batch-transcription.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n')
        print(item['id'], info.language, round(info.language_probability, 3), len(words), flush=True)


if __name__ == '__main__':
    main()

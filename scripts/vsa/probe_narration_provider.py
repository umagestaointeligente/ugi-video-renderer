#!/usr/bin/env python3
"""One bounded, non-publishing probe; output contains no raw provider URLs."""
import argparse
import importlib.util
import importlib.metadata
import json
import pathlib
import os
import sys
import tempfile
import time

ROOT=pathlib.Path(__file__).resolve().parents[2]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    args=parser.parse_args()
    spec=importlib.util.spec_from_file_location('oct13',ROOT/'production/vsa/pilots/oct13_triple/render_oct13_triple.py')
    renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)
    os.environ['PATH']=str(pathlib.Path(sys.executable).parent)+os.pathsep+os.environ.get('PATH','')
    report={'status':'FAIL','provider':'edge-tts','voice':renderer.VOICE,'versions':{}}
    for package in ('edge-tts','aiohttp','multidict','requests','certifi'):
        try:report['versions'][package]=importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:report['versions'][package]='MISSING'
    start=time.monotonic()
    with tempfile.TemporaryDirectory() as td:
        target=pathlib.Path(td)/'probe.mp3'
        try:
            text=renderer.TOPICS['pendulo_newton']['scenes'][0][-1]
            renderer.synthesize_narration(text,'-2%',target)
            report.update(status='PASS',duration_seconds=renderer.duration(target),audio_sha256=renderer.sha(target))
        except Exception as exc:
            code=str(exc).split(' ',1)[0]
            allowed={'TTS_PROVIDER_HTTP_403','TTS_PROVIDER_FAILED','TTS_TLS_CERTIFICATE_FAIL','TTS_TIMEOUT','TTS_AUDIO_MISSING','TTS_AUDIO_INVALID','TTS_AUDIO_DECODE_FAIL','TTS_AUDIO_SILENT_OR_UNMEASURED'}
            report['error_code']=code if code in allowed else 'TTS_PROBE_UNCLASSIFIED_FAILURE'
    report['elapsed_seconds']=round(time.monotonic()-start,3)
    output=pathlib.Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))
    return 0 if report['status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())

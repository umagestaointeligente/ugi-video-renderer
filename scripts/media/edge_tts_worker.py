#!/usr/bin/env python3
"""Bounded Edge synthesis, system+certifi trust, sanitized errors; no paid fallback."""
import argparse
import asyncio
import sys
from pathlib import Path

async def synthesize(text, voice, rate, output, metadata=None):
    import edge_tts
    import edge_tts.communicate as transport
    # edge-tts 7.3.1 supplies a certifi context. Add OS/enterprise roots;
    # certificate and hostname verification remain enabled.
    transport._SSL_CTX.load_default_certs()
    await asyncio.wait_for(edge_tts.Communicate(text, voice, rate=rate, boundary="WordBoundary").save(str(output),str(metadata) if metadata else None), 55)

def main():
    p=argparse.ArgumentParser();p.add_argument('--voice',required=True)
    p.add_argument('--rate',default='+0%');p.add_argument('--text',required=True)
    p.add_argument('--write-media',required=True);p.add_argument('--write-metadata');a=p.parse_args()
    output=Path(a.write_media);output.parent.mkdir(parents=True,exist_ok=True)
    output.unlink(missing_ok=True)
    metadata=Path(a.write_metadata) if a.write_metadata else None
    if metadata:
        metadata.parent.mkdir(parents=True,exist_ok=True)
        metadata.unlink(missing_ok=True)
    try:
        asyncio.run(synthesize(a.text,a.voice,a.rate,output,metadata))
        if not output.is_file() or not output.stat().st_size:raise ValueError('empty')
        return 0
    except Exception as exc:
        output.unlink(missing_ok=True)
        if metadata:metadata.unlink(missing_ok=True)
        name=type(exc).__name__
        code=('TTS_PROVIDER_HTTP_403' if getattr(exc,'status',None)==403 else
              'TTS_TIMEOUT' if isinstance(exc,TimeoutError) else
              'TTS_TLS_CERTIFICATE_FAIL' if 'Certificate' in name else
              'TTS_DEPENDENCY_MISSING' if isinstance(exc,ImportError) else 'TTS_PROVIDER_FAILED')
        print(code,file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())

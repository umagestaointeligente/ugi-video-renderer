from __future__ import annotations
import asyncio, os
from pathlib import Path
import edge_tts
from .common import normalize_text,tokens,media_probe


# Calibrated against the canonical pt-BR-AntonioNeural voice on real Cena Certa
# scripts. Live production on 2026-09-05 showed provider drift at +22%:
# ~136.8 WPM on SCP and ~42.94-43.00s story duration on the other exact4 slots.
# +28% restores headroom inside the canonical 145-165 WPM / 32-42s envelope;
# prepare.py still measures every real speech output and fails closed on drift.
CANONICAL_SPEECH_RATE='+28%'
MAX_PROVIDER_BOUNDARY_OVERLAP_SECONDS=0.12


def _transient_tts_error(exc: Exception) -> bool:
    if isinstance(exc, (asyncio.TimeoutError, TimeoutError, ConnectionError, OSError)):
        return True
    probe=(type(exc).__name__+' '+str(exc)).lower()
    markers=('timeout','timed out','connection','websocket','temporar','429','502','503','504','no audio','voice_empty')
    return any(x in probe for x in markers)


async def _stream_once(c,text,part):
 words=[]; sentences=[]
 comm=edge_tts.Communicate(text,c['voice']['voice_id'],rate=CANONICAL_SPEECH_RATE,volume='+0%')
 with open(part,'wb') as f:
  async for chunk in comm.stream():
   if chunk['type']=='audio': f.write(chunk['data'])
   elif chunk['type']=='WordBoundary': words.append((chunk['text'],chunk['offset']/1e7,chunk['duration']/1e7))
   elif chunk['type']=='SentenceBoundary': sentences.append((chunk['text'],chunk['offset']/1e7,chunk['duration']/1e7))
 return words,sentences


def _clip_provider_boundary_overlap(cues):
 # Edge WordBoundary durations may extend a few milliseconds beyond the next
 # word offset. Keep the real next-word start and trim only the previous visual
 # cue end. Large overlaps still fail closed instead of being hidden.
 for i in range(len(cues)-1):
  overlap=float(cues[i]['end'])-float(cues[i+1]['start'])
  if overlap>0:
   if overlap>MAX_PROVIDER_BOUNDARY_OVERLAP_SECONDS:
    raise RuntimeError(f'WORD_BOUNDARY_OVERLAP_FAIL cue={i+1} overlap={overlap:.3f}')
   cues[i]['end']=float(cues[i+1]['start'])
 return cues


async def tts_with_real_boundaries(c,text,caption_chunks,out):
 out=Path(out); out.parent.mkdir(parents=True,exist_ok=True)
 authored=' '.join(caption_chunks)
 if normalize_text(authored)!=normalize_text(text): raise RuntimeError('CAPTION_LITERAL_MISMATCH_BEFORE_TTS')
 timeout=float(c.get('runtime',{}).get('tts_timeout_seconds',50))
 configured=max(1,int(c.get('runtime',{}).get('tts_attempts',1)))
 attempts=min(configured,2)  # one primary call + at most one classified transient retry
 last=None; words=[]; sentences=[]
 for attempt in range(1,attempts+1):
  part=out.with_name(out.name+f'.part-{os.getpid()}-{attempt}')
  try:
   words,sentences=await asyncio.wait_for(_stream_once(c,text,part),timeout=timeout)
   if not part.exists() or part.stat().st_size<10000: raise RuntimeError('VOICE_EMPTY')
   media_probe(part,'audio'); os.replace(part,out); last=None; break
  except Exception as e:
   last=e; part.unlink(missing_ok=True)
   transient=_transient_tts_error(e)
   if not transient:
    raise RuntimeError(f'TTS_NON_TRANSIENT_FAIL {type(e).__name__}: {e}') from e
   if attempt<attempts:
    print('TTS_TRANSIENT_RETRY',attempt,type(e).__name__)
    await asyncio.sleep(1.0)
 if last is not None: raise RuntimeError(f'TTS_TRANSIENT_RETRY_EXHAUSTED {type(last).__name__}: {last}') from last
 cues=[]
 if words:
  if tokens(' '.join(w[0] for w in words))!=tokens(text): raise RuntimeError('WORD_BOUNDARY_TEXT_MISMATCH')
  pos=0
  for chunk in caption_chunks:
   n=len(tokens(chunk)); seg=words[pos:pos+n]
   if len(seg)!=n: raise RuntimeError('WORD_BOUNDARY_COUNT_FAIL')
   cues.append({'text':chunk,'start':seg[0][1],'end':seg[-1][1]+seg[-1][2]}); pos+=n
 elif len(sentences)==len(caption_chunks):
  for chunk,s in zip(caption_chunks,sentences): cues.append({'text':chunk,'start':s[1],'end':s[1]+s[2]})
 else:
  raise RuntimeError(f'REAL_ALIGNMENT_UNAVAILABLE words={len(words)} sentences={len(sentences)} chunks={len(caption_chunks)}')
 _clip_provider_boundary_overlap(cues)
 for a,b in zip(cues,cues[1:]):
  gap=b['start']-a['end']
  if gap>c['voice']['max_internal_speech_gap_seconds']: raise RuntimeError(f'DEAD_AIR_FAIL {gap:.3f}s')
 return cues

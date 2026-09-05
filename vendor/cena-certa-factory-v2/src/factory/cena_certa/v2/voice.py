from __future__ import annotations
import asyncio, os
from pathlib import Path
import edge_tts
from .common import normalize_text,tokens,media_probe

async def _stream_once(c,text,part):
 words=[]; sentences=[]
 comm=edge_tts.Communicate(text,c['voice']['voice_id'],rate='+3%',volume='+0%')
 with open(part,'wb') as f:
  async for chunk in comm.stream():
   if chunk['type']=='audio': f.write(chunk['data'])
   elif chunk['type']=='WordBoundary': words.append((chunk['text'],chunk['offset']/1e7,chunk['duration']/1e7))
   elif chunk['type']=='SentenceBoundary': sentences.append((chunk['text'],chunk['offset']/1e7,chunk['duration']/1e7))
 return words,sentences

async def tts_with_real_boundaries(c,text,caption_chunks,out):
 out=Path(out); out.parent.mkdir(parents=True,exist_ok=True)
 authored=' '.join(caption_chunks)
 if normalize_text(authored)!=normalize_text(text): raise RuntimeError('CAPTION_LITERAL_MISMATCH_BEFORE_TTS')
 timeout=float(c.get('runtime',{}).get('tts_timeout_seconds',50)); attempts=int(c.get('runtime',{}).get('tts_attempts',3))
 last=None; words=[]; sentences=[]
 for attempt in range(1,attempts+1):
  part=out.with_name(out.name+f'.part-{os.getpid()}-{attempt}')
  try:
   words,sentences=await asyncio.wait_for(_stream_once(c,text,part),timeout=timeout)
   if not part.exists() or part.stat().st_size<10000: raise RuntimeError('VOICE_EMPTY')
   media_probe(part,'audio'); os.replace(part,out); last=None; break
  except Exception as e:
   last=e; part.unlink(missing_ok=True)
   if attempt<attempts: await asyncio.sleep(min(1.5*attempt,3.0))
 if last is not None: raise RuntimeError(f'TTS_RETRY_EXHAUSTED {type(last).__name__}: {last}') from last
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
 for a,b in zip(cues,cues[1:]):
  gap=b['start']-a['end']
  if gap>c['voice']['max_internal_speech_gap_seconds']: raise RuntimeError(f'DEAD_AIR_FAIL {gap:.3f}s')
 return cues

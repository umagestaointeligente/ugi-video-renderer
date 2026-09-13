#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path
import edge_tts

async def voice_and_words(text, audio_path):
    """Generate the canonical pt-BR voice plus timing without weakening TLS."""
    audio_path = Path(audio_path)
    words = []
    comm = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate="+5%", volume="+0%")
    with audio_path.open("wb") as f:
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append({
                    "text": chunk["text"],
                    "start": chunk["offset"] / 10_000_000,
                    "dur": chunk["duration"] / 10_000_000,
                })
            elif chunk["type"] == "SentenceBoundary" and not words:
                sentence_words = chunk["text"].split()
                start = chunk["offset"] / 10_000_000
                duration = chunk["duration"] / 10_000_000
                weights = [max(1, len(re.sub(r"[^0-9A-Za-zÀ-ÿ]", "", w))) for w in sentence_words]
                total_weight = sum(weights) or 1
                cursor = start
                for token, weight in zip(sentence_words, weights):
                    token_dur = duration * weight / total_weight
                    words.append({"text": token, "start": cursor, "dur": token_dur})
                    cursor += token_dur
    if not audio_path.exists() or audio_path.stat().st_size < 10_000:
        raise RuntimeError("TTS_FAILED")
    if not words:
        raise RuntimeError("TTS_TIMING_MISSING")
    return words

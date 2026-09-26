from faster_whisper import WhisperModel
from pathlib import Path

model = WhisperModel("tiny", device="cpu", compute_type="int8")

for stem in ("mister", "deus"):
    src = next(Path("out/src").glob(stem + ".*"))
    segments, _ = model.transcribe(
        str(src),
        language="pt",
        vad_filter=True,
        beam_size=3,
    )
    lines = []
    for seg in segments:
        txt = seg.text.strip()
        if txt:
            lines.append(f"{seg.start:06.2f} --> {seg.end:06.2f} | {txt}")
    Path(f"out/{stem}-transcript.txt").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

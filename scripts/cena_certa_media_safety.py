"""Small deterministic helpers shared by the dated renderers."""
from pathlib import Path
import hashlib


def overlay_textfile(text, directory):
    """Keep user/editorial text out of FFmpeg's filter grammar."""
    payload = str(text).encode("utf-8")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / (hashlib.sha256(payload).hexdigest() + ".txt")
    path.write_bytes(payload)
    # Callers use a fixed relative directory, never a source-provided path.
    return path.as_posix()

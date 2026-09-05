FROM python:3.12.14-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ffmpeg \
      fonts-lato \
      fonts-dejavu-core \
      fontconfig \
      ca-certificates \
      curl \
 && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --no-cache-dir \
      Pillow==12.3.0 \
      numpy==2.5.2

RUN ffmpeg -version | head -1 \
 && ffprobe -version | head -1 \
 && fc-match Lato | head -1 \
 && python - <<'PY'
import PIL, numpy
print('RUNTIME_PILLOW', PIL.__version__)
print('RUNTIME_NUMPY', numpy.__version__)
PY

WORKDIR /work

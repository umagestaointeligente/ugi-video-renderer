import os
import subprocess
import textwrap
from pathlib import Path

TITLE = os.getenv(
    "VIDEO_TITLE",
    "Sua empresa cresceu. A gestão precisa acompanhar."
)

CTA = os.getenv(
    "VIDEO_CTA",
    "Conheça a UGI"
)

DURATION = int(os.getenv("VIDEO_DURATION", "8"))

OUTPUT = "output/ugi-reel.mp4"

Path("output").mkdir(exist_ok=True)
Path("tmp").mkdir(exist_ok=True)

# ---------------------------------------------------------
# TEXTOS
# ---------------------------------------------------------

title_wrapped = "\n".join(
    textwrap.wrap(
        TITLE,
        width=24
    )
)

Path("tmp/title.txt").write_text(
    title_wrapped,
    encoding="utf-8"
)

Path("tmp/support.txt").write_text(
    "Crescer exige uma gestão que evolua junto.",
    encoding="utf-8"
)

Path("tmp/cta.txt").write_text(
    CTA,
    encoding="utf-8"
)

Path("tmp/brand.txt").write_text(
    "UMA GESTÃO INTELIGENTE",
    encoding="utf-8"
)

Path("tmp/handle.txt").write_text(
    "@umagestaointeligente",
    encoding="utf-8"
)

# ---------------------------------------------------------
# FONTES
# ---------------------------------------------------------

font = (
    "/usr/share/fonts/truetype/"
    "dejavu/DejaVuSans.ttf"
)

font_bold = (
    "/usr/share/fonts/truetype/"
    "dejavu/DejaVuSans-Bold.ttf"
)

# ---------------------------------------------------------
# COMPOSIÇÃO VISUAL
# ---------------------------------------------------------

filters = [

    # Fundo
    (
        "drawbox="
        "x=0:y=0:w=iw:h=ih:"
        "color=0x101820:t=fill"
    ),

    # Barra editorial
    (
        "drawbox="
        "x=80:y=180:w=8:h=260:"
        "color=white@0.85:t=fill"
    ),

    # Marca
    (
        f"drawtext="
        f"fontfile={font_bold}:"
        "textfile=tmp/brand.txt:"
        "fontcolor=white@0.75:"
        "fontsize=38:"
        "x=110:"
        "y=190"
    ),

    # Título
    (
        f"drawtext="
        f"fontfile={font_bold}:"
        "textfile=tmp/title.txt:"
        "fontcolor=white:"
        "fontsize=72:"
        "line_spacing=18:"
        "x=110:"
        "y='620-20*min(t,1)':"
        "alpha='if(lt(t,0.7),t/0.7,1)'"
    ),

    # Linha de apoio
    (
        f"drawtext="
        f"fontfile={font}:"
        "textfile=tmp/support.txt:"
        "fontcolor=white@0.75:"
        "fontsize=38:"
        "x=110:"
        "y=1120:"
        "alpha="
        "'if(lt(t,2),0,"
        "if(lt(t,3),t-2,1))'"
    ),

    # Caixa CTA
    (
        "drawbox="
        "x=110:"
        "y=1450:"
        "w=860:"
        "h=150:"
        "color=white@0.10:"
        "t=fill:"
        "enable='gte(t,4.8)'"
    ),

    # CTA
    (
        f"drawtext="
        f"fontfile={font_bold}:"
        "textfile=tmp/cta.txt:"
        "fontcolor=white:"
        "fontsize=52:"
        "x=(w-text_w)/2:"
        "y=1500:"
        "alpha="
        "'if(lt(t,4.8),0,"
        "if(lt(t,5.6),"
        "(t-4.8)/0.8,1))'"
    ),

    # Rodapé
    (
        f"drawtext="
        f"fontfile={font}:"
        "textfile=tmp/handle.txt:"
        "fontcolor=white@0.55:"
        "fontsize=30:"
        "x=(w-text_w)/2:"
        "y=1770"
    )
]

# Aqui está a correção principal:
# transforma todos os filtros em UMA STRING válida.
filter_complex = ",".join(filters)

# ---------------------------------------------------------
# FFMPEG
# ---------------------------------------------------------

cmd = [

    "ffmpeg",
    "-y",

    "-f",
    "lavfi",

    "-i",
    (
        "color="
        "c=0x101820:"
        "s=1080x1920:"
        "r=30:"
        f"d={DURATION}"
    ),

    "-vf",
    filter_complex,

    "-c:v",
    "libx264",

    "-preset",
    "medium",

    "-crf",
    "18",

    "-pix_fmt",
    "yuv420p",

    "-movflags",
    "+faststart",

    "-t",
    str(DURATION),

    OUTPUT
]

# ---------------------------------------------------------
# LOG
# ---------------------------------------------------------

print("=" * 42)
print("UGI FREE VIDEO RENDERER")
print("=" * 42)

print(
    f"Title: {TITLE}"
)

print(
    f"CTA: {CTA}"
)

print(
    f"Duration: {DURATION}s"
)

print(
    f"Output: {OUTPUT}"
)

print("=" * 42)

# ---------------------------------------------------------
# RENDER
# ---------------------------------------------------------

subprocess.run(
    cmd,
    check=True
)

print(
    "RENDER_SUCCESS"
)

print(
    OUTPUT
)

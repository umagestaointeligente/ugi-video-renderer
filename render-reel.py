import os
import subprocess
import textwrap

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

os.makedirs("output", exist_ok=True)

# Escapa caracteres que podem quebrar drawtext
def escape_ffmpeg(text):
    return (
        text.replace("\\", "\\\\")
            .replace(":", "\\:")
            .replace("'", "\\'")
            .replace("%", "\\%")
    )

# Quebra o título para funcionar melhor no formato vertical
title_lines = textwrap.wrap(TITLE, width=25)
title = "\\n".join(title_lines)

title = escape_ffmpeg(title)
cta = escape_ffmpeg(CTA)

# Fonte padrão disponível no Ubuntu/GitHub Actions
font = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

filter_complex = (
    # Fundo com leve movimento/variação
    "drawbox=x=0:y=0:w=iw:h=ih:"
    "color=0x101820:t=fill,"

    # Elemento gráfico superior
    "drawbox=x=80:y=180:w=8:h=260:"
    "color=white@0.85:t=fill,"

    # Marca
    f"drawtext=fontfile={font_bold}:"
    "text='UMA GESTÃO INTELIGENTE':"
    "fontcolor=white@0.75:"
    "fontsize=38:"
    "x=110:y=190:"
    "enable='between(t,0,8)',"

    # Título principal
    f"drawtext=fontfile={font_bold}:"
    f"text='{title}':"
    "fontcolor=white:"
    "fontsize=72:"
    "line_spacing=18:"
    "x=110:"
    "y='620-20*min(t,1)':"
    "alpha='if(lt(t,0.7),t/0.7,1)':",

    # Linha de apoio
    f"drawtext=fontfile={font}:"
    "text='Crescer exige uma gestão que evolua junto.':"
    "fontcolor=white@0.75:"
    "fontsize=38:"
    "x=110:y=1120:"
    "alpha='if(lt(t,2),0,if(lt(t,3),(t-2),1))':",

    # CTA
    "drawbox=x=110:y=1450:w=860:h=150:"
    "color=white@0.10:t=fill:"
    "enable='gte(t,4.8)',"

    f"drawtext=fontfile={font_bold}:"
    f"text='{cta}':"
    "fontcolor=white:"
    "fontsize=52:"
    "x=(w-text_w)/2:"
    "y=1500:"
    "alpha='if(lt(t,4.8),0,if(lt(t,5.6),(t-4.8)/0.8,1))',"

    # Rodapé
    f"drawtext=fontfile={font}:"
    "text='@umagestaointeligente':"
    "fontcolor=white@0.55:"
    "fontsize=30:"
    "x=(w-text_w)/2:y=1770"
)

cmd = [
    "ffmpeg",
    "-y",

    "-f", "lavfi",
    "-i", f"color=c=0x101820:s=1080x1920:r=30:d={DURATION}",

    "-vf", filter_complex,

    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "18",
    "-pix_fmt", "yuv420p",

    "-movflags", "+faststart",

    "-t", str(DURATION),

    OUTPUT
]

print("==========================================")
print("UGI FREE VIDEO RENDERER")
print("==========================================")
print(f"Title: {TITLE}")
print(f"CTA: {CTA}")
print(f"Duration: {DURATION}s")
print(f"Output: {OUTPUT}")
print("==========================================")

subprocess.run(cmd, check=True)

print("RENDER_SUCCESS")
print(OUTPUT)

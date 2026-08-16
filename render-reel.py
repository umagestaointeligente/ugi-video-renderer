#!/usr/bin/env python3
"""
UGI Reel Renderer R37.3 CREATIVE PRODUCTION
=====================
Renderer vertical 9:16 de custo inicial zero, executado com FFmpeg no GitHub Actions.

Objetivos do R37.3:
- preservar a interface do workflow R27 (VIDEO_TITLE, VIDEO_DURATION, VIDEO_RENDER_ID);
- gerar MP4 H.264 1080x1920 / 30 fps com locução neural PT-BR + trilha moderna AAC;
- usar somente conteúdo derivado do título + CTA UGI, evitando inventar mensagens editoriais;
- criar 4 cenas com direção visual, movimento, hierarquia tipográfica, metáforas gráficas e CTA;
- funcionar sem APIs pagas; usar Kokoro PT-BR local + FFmpeg no GitHub Actions.

Saída:
    output/ugi-reel.mp4
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import wave
import textwrap
from pathlib import Path

WIDTH = 1080
HEIGHT = 1920
FPS = 30
OUTPUT = Path("output/ugi-reel.mp4")
WORK = Path("output/r373_work")

TITLE = (os.getenv("VIDEO_TITLE") or "Sua empresa cresceu. A gestão precisa acompanhar.").strip()
CTA = (os.getenv("VIDEO_CTA") or "Conheça a UGI").strip()
RENDER_ID = (os.getenv("VIDEO_RENDER_ID") or "local-r373").strip()
NARRATION_RAW = (
    os.getenv("VIDEO_NARRATION")
    or f"{TITLE} {CTA}."
).strip()


try:
    DURATION = int(os.getenv("VIDEO_DURATION") or "8")
except ValueError:
    DURATION = 8

DURATION = max(4, min(40, DURATION))

FONT_REGULAR_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
]
FONT_BOLD_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
]

BG = "0x0B1118"
PANEL = "0x101820"
WHITE = "0xF4F7F9"
MUTED = "0xAAB6C2"
ACCENT = "0x35D0BA"
ACCENT_2 = "0x66A6FF"
DEEP = "0x07101A"
PANEL_2 = "0x162330"
WARM = "0xD7B56D"


def first_existing(paths: list[str]) -> str:
    for p in paths:
        if Path(p).exists():
            return p
    raise FileNotFoundError("Nenhuma fonte compatível encontrada no runner.")


FONT_REGULAR = first_existing(FONT_REGULAR_CANDIDATES)
FONT_BOLD = first_existing(FONT_BOLD_CANDIDATES)


def run(cmd: list[str]) -> None:
    print(">", " ".join(cmd))
    subprocess.run(cmd, check=True)


def clean_text(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return value or "Uma Gestão Inteligente"


def balanced_chunks(text: str, parts: int = 3) -> list[str]:
    """Divide o título em blocos por palavras, preservando 100% do texto e a ordem."""
    words = clean_text(text).split()
    if len(words) <= parts:
        chunks = words + [""] * (parts - len(words))
        return chunks[:parts]

    total_chars = sum(len(w) for w in words) + max(0, len(words) - 1)
    target = max(1, total_chars / parts)

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for idx, word in enumerate(words):
        word_len = len(word) + (1 if current else 0)
        remaining_words = len(words) - idx
        remaining_parts = parts - len(chunks)

        if (
            current
            and current_len + word_len > target
            and remaining_words >= remaining_parts
            and len(chunks) < parts - 1
        ):
            chunks.append(" ".join(current))
            current = [word]
            current_len = len(word)
        else:
            current.append(word)
            current_len += word_len

    if current:
        chunks.append(" ".join(current))

    while len(chunks) < parts:
        chunks.append("")

    # Reequilíbrio simples caso sobrem blocos por pontuação/distribuição.
    if len(chunks) > parts:
        chunks = chunks[: parts - 1] + [" ".join(chunks[parts - 1 :])]

    return chunks


def wrap_for_reel(text: str, width: int) -> str:
    if not text:
        return ""
    return "\n".join(
        textwrap.wrap(
            text,
            width=width,
            break_long_words=False,
            break_on_hyphens=False,
        )
    )


def scene_durations(total: int) -> list[float]:
    # 3 cenas de narrativa + fechamento. O fechamento recebe levemente mais tempo.
    ratios = [0.24, 0.24, 0.24, 0.28]
    vals = [round(total * r, 3) for r in ratios]
    vals[-1] = round(total - sum(vals[:-1]), 3)
    # duração mínima funcional
    for i, v in enumerate(vals):
        if v < 0.85:
            vals[i] = 0.85
    scale = total / sum(vals)
    vals = [round(v * scale, 3) for v in vals]
    vals[-1] = round(total - sum(vals[:-1]), 3)
    return vals


def write_text(name: str, content: str) -> Path:
    p = WORK / f"{name}.txt"
    p.write_text(content, encoding="utf-8")
    return p


def esc_path(p: Path) -> str:
    # Caminhos relativos controlados, sem caracteres especiais relevantes ao parser.
    return p.as_posix().replace("'", r"\'")


def add_common_layers(filters: list[str], scene_index: int, dur: float) -> None:
    """Base visual R37.3 usando apenas filtros FFmpeg amplamente compatíveis."""
    filters.extend(
        [
            f"drawbox=x=54:y=210:w={WIDTH-108}:h={HEIGHT-420}:color={PANEL}@0.42:t=fill",
            f"drawbox=x=78:y=238:w={WIDTH-156}:h={HEIGHT-476}:color={PANEL_2}@0.18:t=fill",
            f"drawbox=x='-560+t*320':y={275 + scene_index*24}:w=520:h=10:color={ACCENT}@0.78:t=fill",
            f"drawbox=x='{WIDTH+180}-t*235':y={1495 - scene_index*34}:w=430:h=8:color={ACCENT_2}@0.52:t=fill",
            f"drawbox=x='-300+t*150':y={1660 - scene_index*12}:w=260:h=4:color={WHITE}@0.18:t=fill",
            f"drawbox=x=82:y=300:w=2:h=1230:color={WHITE}@0.10:t=fill",
            f"drawbox=x={WIDTH-84}:y=300:w=2:h=1230:color={WHITE}@0.07:t=fill",
            f"drawbox=x=82:y=300:w={WIDTH-164}:h=2:color={WHITE}@0.06:t=fill",
            f"drawbox=x=82:y=1530:w={WIDTH-164}:h=2:color={WHITE}@0.05:t=fill",
            "noise=alls=2:allf=t+u",
            "vignette=PI/5.5",
        ]
    )

    progress_x = 82
    progress_y = 1765
    progress_w = WIDTH - 164
    filters.append(
        f"drawbox=x={progress_x}:y={progress_y}:w={progress_w}:h=4:color={WHITE}@0.10:t=fill"
    )
    filters.append(
        f"drawbox=x={progress_x}:y={progress_y}:w='({progress_w})*min(t/{dur},1)':h=4:color={ACCENT}@0.96:t=fill"
    )


def add_scene_motif(filters: list[str], scene_index: int, dur: float) -> None:
    """Metáforas gráficas abstratas sem criar texto editorial adicional."""
    if scene_index == 1:
        filters.extend(
            [
                f"drawbox=x='110+180*min(t/{dur},1)':y=430:w=230:h=78:color={ACCENT_2}@0.16:t=fill",
                f"drawbox=x='{WIDTH-340}-180*min(t/{dur},1)':y=540:w=230:h=78:color={ACCENT}@0.16:t=fill",
                f"drawbox=x='130+160*min(t/{dur},1)':y=650:w=210:h=70:color={WHITE}@0.08:t=fill",
                f"drawbox=x={WIDTH//2-18}:y=390:w=36:h=390:color={ACCENT}@0.26:t=fill",
            ]
        )
    elif scene_index == 2:
        for i, y in enumerate((430, 535, 640, 745)):
            delay = 0.08 * i
            filters.append(
                f"drawbox=x='115+{i*24}+120*max(0,min((t-{delay})/{max(0.6, dur)},1))':"
                f"y={y}:w={560-i*42}:h=72:color={WHITE}@{0.07 + i*0.015}:t=fill"
            )
        filters.append(
            f"drawbox=x={WIDTH-265}:y=400:w=120:h=470:color={ACCENT_2}@0.18:t=fill"
        )
    elif scene_index == 3:
        filters.extend(
            [
                f"drawbox=x='420-250*min(t/{dur},1)':y=430:w=210:h=72:color={ACCENT}@0.16:t=fill",
                f"drawbox=x='450+250*min(t/{dur},1)':y=540:w=210:h=72:color={ACCENT_2}@0.16:t=fill",
                f"drawbox=x='410-205*min(t/{dur},1)':y=650:w=190:h=68:color={WHITE}@0.09:t=fill",
                f"drawbox=x='470+185*min(t/{dur},1)':y=760:w=190:h=68:color={WHITE}@0.07:t=fill",
            ]
        )
    else:
        filters.extend(
            [
                f"drawbox=x='120+30*sin(t*2.2)':y=470:w={WIDTH-240}:h=5:color={ACCENT}@0.42:t=fill",
                f"drawbox=x='180-24*sin(t*1.8)':y=1380:w={WIDTH-360}:h=5:color={ACCENT_2}@0.26:t=fill",
            ]
        )



def drawtext_filter(
    textfile: Path,
    *,
    fontfile: str,
    fontsize: int,
    fontcolor: str,
    x: str,
    y: str,
    line_spacing: int = 14,
    alpha: str = "1",
    borderw: int = 0,
    bordercolor: str = "black@0.0",
) -> str:
    return (
        "drawtext="
        f"fontfile='{fontfile}':"
        f"textfile='{esc_path(textfile)}':reload=0:"
        f"fontsize={fontsize}:fontcolor={fontcolor}:"
        f"line_spacing={line_spacing}:"
        f"x={x}:y={y}:alpha='{alpha}':"
        f"borderw={borderw}:bordercolor={bordercolor}"
    )


def render_scene(index: int, phrase: str, dur: float, output: Path, closing: bool = False) -> None:
    scene_no = write_text(f"scene_{index}_no", f"0{index} / 04")
    brand = write_text(f"scene_{index}_brand", "UMA GESTÃO INTELIGENTE")
    phrase_file = write_text(
        f"scene_{index}_phrase",
        wrap_for_reel(phrase if phrase else TITLE, 23 if not closing else 28),
    )
    cta_file = write_text(f"scene_{index}_cta", CTA)
    render_file = write_text(f"scene_{index}_render", RENDER_ID)

    filters: list[str] = []
    add_common_layers(filters, index, dur)
    add_scene_motif(filters, index, dur)

    filters.append(
        drawtext_filter(
            scene_no,
            fontfile=FONT_BOLD,
            fontsize=28,
            fontcolor=MUTED,
            x="96",
            y="112",
            alpha="min(t/0.24,1)",
        )
    )
    filters.append(
        drawtext_filter(
            brand,
            fontfile=FONT_BOLD,
            fontsize=27,
            fontcolor=WHITE,
            x="w-text_w-96",
            y="112",
            alpha="min(t/0.24,1)",
        )
    )

    if not closing:
        text_x = "104+34*exp(-4*t)"
        text_y = 895 if index == 1 else (865 if index == 2 else 835)
        text_alpha = "if(lt(t,0.08),0,min((t-0.08)/0.30,1))"

        filters.append(
            drawtext_filter(
                phrase_file,
                fontfile=FONT_BOLD,
                fontsize=70,
                fontcolor=WHITE,
                x=text_x,
                y=str(text_y),
                line_spacing=15,
                alpha=text_alpha,
                borderw=1,
                bordercolor="black@0.20",
            )
        )

        filters.append(
            f"drawbox=x=104:y={text_y-42}:w='190+380*min(t/{dur},1)':h=7:color={ACCENT}@0.88:t=fill"
        )

        accent_word = write_text(f"scene_{index}_accent", "UGI")
        filters.append(
            drawtext_filter(
                accent_word,
                fontfile=FONT_BOLD,
                fontsize=30,
                fontcolor=ACCENT,
                x="104",
                y="1585",
                alpha="if(lt(t,0.42),0,min((t-0.42)/0.26,1))",
            )
        )
    else:
        title_full = write_text("scene_4_title_full", wrap_for_reel(TITLE, 30))
        filters.append(
            drawtext_filter(
                title_full,
                fontfile=FONT_BOLD,
                fontsize=56,
                fontcolor=WHITE,
                x="104",
                y="570",
                line_spacing=14,
                alpha="min(t/0.34,1)",
            )
        )

        filters.append(
            f"drawbox=x=104:y=1125:w={WIDTH-208}:h=168:color={PANEL_2}@0.92:t=fill"
        )
        filters.append(
            f"drawbox=x=104:y=1125:w=12:h=168:color={ACCENT}@0.98:t=fill"
        )
        filters.append(
            drawtext_filter(
                cta_file,
                fontfile=FONT_BOLD,
                fontsize=54,
                fontcolor=WHITE,
                x="148",
                y="1172",
                alpha="if(lt(t,0.18),0,min((t-0.18)/0.30,1))",
            )
        )
        filters.append(
            drawtext_filter(
                render_file,
                fontfile=FONT_REGULAR,
                fontsize=16,
                fontcolor=MUTED,
                x="104",
                y="1644",
                alpha="0.26",
            )
        )

    out_start = max(0.05, dur - 0.14)
    filters.append("fade=t=in:st=0:d=0.10")
    filters.append(f"fade=t=out:st={out_start}:d=0.14")

    vf = ",".join(filters)

    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c={DEEP}:s={WIDTH}x{HEIGHT}:r={FPS}:d={dur}",
            "-vf",
            vf,
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "19",
            "-pix_fmt",
            "yuv420p",
            "-r",
            str(FPS),
            "-movflags",
            "+faststart",
            str(output),
        ]
    )




def synthesize_narration() -> Path:
    """Gera locução PT-BR local com Kokoro, voz feminina pf_dora."""
    try:
        import numpy as np
        import soundfile as sf
        from kokoro import KPipeline
    except Exception as exc:
        raise RuntimeError(
            "Kokoro TTS não está instalado. Use o workflow R36 KOKORO."
        ) from exc

    narration = clean_text(NARRATION_RAW)
    raw_wav = WORK / "narration_raw.wav"

    pipeline = KPipeline(lang_code="p")
    chunks = []
    for result in pipeline(
        narration,
        voice="pf_dora",
        speed=1.02,
        split_pattern=r"\n+",
    ):
        audio = getattr(result, "audio", None)
        if audio is not None:
            chunks.append(np.asarray(audio, dtype=np.float32))

    if not chunks:
        raise RuntimeError("Kokoro não retornou áudio para a locução.")

    audio = np.concatenate(chunks)
    sf.write(str(raw_wav), audio, 24000, subtype="PCM_16")

    narration_wav = WORK / "narration.wav"
    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(raw_wav),
            "-af",
            (
                "highpass=f=80,"
                "lowpass=f=10000,"
                "acompressor=threshold=-20dB:ratio=2:attack=8:release=120:makeup=2,"
                "loudnorm=I=-16:TP=-2:LRA=5"
            ),
            "-ar", "48000",
            "-ac", "2",
            str(narration_wav),
        ]
    )
    return narration_wav



def concat_and_finalize(scene_files: list[Path]) -> None:
    concat_file = WORK / "concat.txt"
    concat_file.write_text(
        "\n".join(f"file '{p.resolve().as_posix()}'" for p in scene_files),
        encoding="utf-8",
    )

    intermediate = WORK / "joined.mp4"
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c",
            "copy",
            str(intermediate),
        ]
    )

    narration_wav = synthesize_narration()

    # Trilha moderna procedural: pad + pulso + acentos de transição.
    # A música é criada localmente e abaixada automaticamente sob a locução.
    pulse = "(0.50+0.50*sin(2*PI*2*t))"
    accent = (
        "exp(-16*abs(t-2.0))"
        "+exp(-16*abs(t-4.0))"
        "+exp(-16*abs(t-6.0))"
    )
    lift = "(0.5+0.5*tanh(3*(t-6.1)))"

    music_expr = (
        "0.030*sin(2*PI*110*t)"
        "+0.022*sin(2*PI*164.81*t)"
        "+0.018*sin(2*PI*220*t)"
        "+0.015*" + pulse + "*sin(2*PI*329.63*t)"
        "+0.011*" + pulse + "*sin(2*PI*440*t)"
        "+0.025*(" + accent + ")*sin(2*PI*659.25*t)"
        "+0.010*" + lift + "*sin(2*PI*523.25*t)"
    )

    music_src = (
        f"aevalsrc='{music_expr}':s=48000:d={DURATION},"
        "aformat=sample_fmts=fltp:channel_layouts=stereo,"
        "highpass=f=70,lowpass=f=7200,"
        "acompressor=threshold=-22dB:ratio=2:attack=12:release=160:makeup=2,"
        "afade=t=in:st=0:d=0.25,"
        f"afade=t=out:st={max(0.1, DURATION-0.55)}:d=0.55"
    )

    # Locução entra levemente após o início; sidechain reduz a música durante a fala.
    mix_filter = (
        # A voz precisa alimentar dois ramos do grafo:
        # 1) sidechain para abaixar a música;
        # 2) mix final audível.
        # O asplit evita o erro "Stream specifier 'voice' matches no streams".
        "[1:a]adelay=280|280,volume=1.12,asplit=2[voice_sc][voice_mix];"
        "[2:a]volume=0.82[music];"
        "[music][voice_sc]sidechaincompress="
        "threshold=0.016:ratio=9:attack=14:release=240:makeup=1[ducked];"
        "[ducked][voice_mix]amix=inputs=2:duration=longest:dropout_transition=0,"
        "loudnorm=I=-14:TP=-1.2:LRA=6[aout]"
    )

    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(intermediate),
            "-i",
            str(narration_wav),
            "-f",
            "lavfi",
            "-i",
            music_src,
            "-filter_complex",
            mix_filter,
            "-map",
            "0:v:0",
            "-map",
            "[aout]",
            "-t",
            str(DURATION),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "160k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            str(OUTPUT),
        ]
    )



def validate_output() -> None:
    if not OUTPUT.exists() or OUTPUT.stat().st_size < 10_000:
        raise RuntimeError("R37.3 não produziu um MP4 válido ou o arquivo ficou pequeno demais.")

    signature = OUTPUT.read_bytes()[:12]
    if len(signature) < 12 or signature[4:8] != b"ftyp":
        raise RuntimeError("Assinatura MP4 ftyp ausente.")

    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
            "-show_entries",
            "format=duration,size",
            "-of",
            "default=noprint_wrappers=1",
            str(OUTPUT),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    print("===== R37.3 VALIDATION =====")
    print(probe.stdout.strip())
    print(f"TITLE={TITLE}")
    print(f"CTA={CTA}")
    print(f"RENDER_ID={RENDER_ID}")
    print(f"OUTPUT={OUTPUT}")
    print("==========================")


def main() -> int:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise RuntimeError("FFmpeg/ffprobe não encontrados.")

    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True, exist_ok=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    chunks = balanced_chunks(TITLE, 3)
    durations = scene_durations(DURATION)

    print("===== UGI REEL RENDERER R37.3 CREATIVE PRODUCTION =====")
    print(f"Title: {TITLE}")
    print(f"Duration: {DURATION}s")
    print(f"Render ID: {RENDER_ID}")
    print(f"Narration: {clean_text(NARRATION_RAW)}")
    print(f"Chunks: {chunks}")
    print(f"Scene durations: {durations}")
    print("=================================")

    scene_files: list[Path] = []
    for idx in range(1, 5):
        scene_path = WORK / f"scene-{idx}.mp4"
        phrase = chunks[idx - 1] if idx <= 3 else TITLE
        render_scene(
            idx,
            phrase,
            durations[idx - 1],
            scene_path,
            closing=(idx == 4),
        )
        scene_files.append(scene_path)

    concat_and_finalize(scene_files)
    validate_output()
    print("RENDER_SUCCESS_R37_3")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"FFMPEG_ERROR: returncode={exc.returncode}", file=sys.stderr)
        raise
    except Exception as exc:
        print(f"R37_3_ERROR: {exc}", file=sys.stderr)
        raise


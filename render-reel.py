#!/usr/bin/env python3
"""
UGI Reel Renderer R32 FINAL VOICE
=====================
Renderer vertical 9:16 de custo inicial zero, executado com FFmpeg no GitHub Actions.

Objetivos do R32:
- preservar a interface do workflow R27 (VIDEO_TITLE, VIDEO_DURATION, VIDEO_RENDER_ID);
- gerar MP4 H.264 1080x1920 / 30 fps com locução neural PT-BR + trilha moderna AAC;
- usar somente conteúdo derivado do título + CTA UGI, evitando inventar mensagens editoriais;
- criar 4 cenas de kinetic typography com composição premium, transições, grão e progresso;
- funcionar sem APIs pagas; o workflow baixa uma voz Piper aberta e executa TTS localmente.

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
WORK = Path("output/r32_work")

TITLE = (os.getenv("VIDEO_TITLE") or "Sua empresa cresceu. A gestão precisa acompanhar.").strip()
CTA = (os.getenv("VIDEO_CTA") or "Conheça a UGI").strip()
RENDER_ID = (os.getenv("VIDEO_RENDER_ID") or "local-r32").strip()
VOICE_MODEL = Path(
    os.getenv("PIPER_VOICE_MODEL")
    or "voices/pt_BR-cadu-medium.onnx"
)
VOICE_CONFIG = Path(
    os.getenv("PIPER_VOICE_CONFIG")
    or "voices/pt_BR-cadu-medium.onnx.json"
)
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
    # Fundo com painel central muito sutil.
    filters.extend(
        [
            f"drawbox=x=70:y=250:w={WIDTH-140}:h={HEIGHT-500}:color={PANEL}@0.36:t=fill",
            # linhas cinéticas que atravessam a composição
            f"drawbox=x='-420+t*240':y={280 + scene_index*28}:w=420:h=8:color={ACCENT}@0.72:t=fill",
            f"drawbox=x='{WIDTH+120}-t*190':y={1510 - scene_index*35}:w=330:h=6:color={ACCENT_2}@0.48:t=fill",
            # régua vertical / grid editorial
            f"drawbox=x=92:y=320:w=3:h=1180:color={WHITE}@0.10:t=fill",
            f"drawbox=x={WIDTH-95}:y=320:w=3:h=1180:color={WHITE}@0.07:t=fill",
            # grão discreto e vinheta
            "noise=alls=3:allf=t+u",
            "vignette=PI/5",
        ]
    )

    # barra de progresso no rodapé
    progress_x = 82
    progress_y = 1765
    progress_w = WIDTH - 164
    filters.append(
        f"drawbox=x={progress_x}:y={progress_y}:w={progress_w}:h=4:color={WHITE}@0.12:t=fill"
    )
    filters.append(
        f"drawbox=x={progress_x}:y={progress_y}:w='({progress_w})*min(t/{dur},1)':h=4:color={ACCENT}@0.90:t=fill"
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
        wrap_for_reel(phrase if phrase else TITLE, 21 if not closing else 27),
    )
    cta_file = write_text(f"scene_{index}_cta", CTA)
    render_file = write_text(f"scene_{index}_render", RENDER_ID)

    filters: list[str] = []
    add_common_layers(filters, index, dur)

    # Cabeçalho editorial.
    filters.append(
        drawtext_filter(
            scene_no,
            fontfile=FONT_BOLD,
            fontsize=31,
            fontcolor=MUTED,
            x="96",
            y="118",
            alpha=f"min(t/0.30,1)",
        )
    )
    filters.append(
        drawtext_filter(
            brand,
            fontfile=FONT_BOLD,
            fontsize=28,
            fontcolor=WHITE,
            x="w-text_w-96",
            y="118",
            alpha=f"min(t/0.30,1)",
        )
    )

    if not closing:
        # Entrada vertical com leve overshoot visual.
        text_y = "760-50*exp(-4*t)"
        text_alpha = f"if(lt(t,0.18),0,min((t-0.18)/0.38,1))"
        filters.append(
            drawtext_filter(
                phrase_file,
                fontfile=FONT_BOLD,
                fontsize=84,
                fontcolor=WHITE,
                x="(w-text_w)/2",
                y=text_y,
                line_spacing=18,
                alpha=text_alpha,
                borderw=1,
                bordercolor="black@0.16",
            )
        )
        # assinatura visual mínima, sem criar nova mensagem editorial
        accent_word = write_text(f"scene_{index}_accent", "UGI")
        filters.append(
            drawtext_filter(
                accent_word,
                fontfile=FONT_BOLD,
                fontsize=34,
                fontcolor=ACCENT,
                x="96",
                y="1585",
                alpha=f"if(lt(t,0.55),0,min((t-0.55)/0.28,1))",
            )
        )
    else:
        # Fechamento: título completo menor + CTA forte.
        title_full = write_text("scene_4_title_full", wrap_for_reel(TITLE, 28))
        filters.append(
            drawtext_filter(
                title_full,
                fontfile=FONT_BOLD,
                fontsize=62,
                fontcolor=WHITE,
                x="(w-text_w)/2",
                y="610",
                line_spacing=15,
                alpha=f"min(t/0.42,1)",
            )
        )

        # CTA em bloco premium
        filters.append(
            f"drawbox=x=150:y=1150:w={WIDTH-300}:h=154:color={ACCENT}@0.92:t=fill"
        )
        filters.append(
            drawtext_filter(
                cta_file,
                fontfile=FONT_BOLD,
                fontsize=54,
                fontcolor=BG,
                x="(w-text_w)/2",
                y="1192",
                alpha=f"if(lt(t,0.28),0,min((t-0.28)/0.32,1))",
            )
        )
        filters.append(
            drawtext_filter(
                render_file,
                fontfile=FONT_REGULAR,
                fontsize=18,
                fontcolor=MUTED,
                x="96",
                y="1642",
                alpha="0.55",
            )
        )

    # Fade integral de cena.
    out_start = max(0.05, dur - 0.22)
    filters.append(f"fade=t=in:st=0:d=0.18")
    filters.append(f"fade=t=out:st={out_start}:d=0.22")

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
            f"color=c={BG}:s={WIDTH}x{HEIGHT}:r={FPS}:d={dur}",
            "-vf",
            vf,
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "20",
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
    """Gera locução neural PT-BR local com Piper."""
    if not VOICE_MODEL.exists():
        raise FileNotFoundError(
            f"Modelo Piper ausente: {VOICE_MODEL}. "
            "O workflow R32 deve baixar a voz antes de executar o renderer."
        )

    try:
        from piper import PiperVoice, SynthesisConfig
    except Exception as exc:
        raise RuntimeError(
            "piper-tts não está instalado no runner. "
            "Use o workflow R32 FINAL."
        ) from exc

    narration = clean_text(NARRATION_RAW)
    raw_wav = WORK / "narration_raw.wav"

    voice = PiperVoice.load(
        str(VOICE_MODEL),
        config_path=str(VOICE_CONFIG) if VOICE_CONFIG.exists() else None,
    )

    # Ritmo ligeiramente mais ágil para caber com naturalidade em Reels de 8 s.
    syn_config = SynthesisConfig(
        volume=1.0,
        length_scale=0.92,
        noise_scale=0.62,
        noise_w_scale=0.76,
        normalize_audio=True,
    )

    with wave.open(str(raw_wav), "wb") as wav_file:
        voice.synthesize_wav(
            narration,
            wav_file,
            syn_config=syn_config,
        )

    # Tratamento de voz: presença, limpeza e volume estável.
    narration_wav = WORK / "narration.wav"
    run(
        [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(raw_wav),
            "-af",
            (
                "highpass=f=85,"
                "lowpass=f=9000,"
                "acompressor=threshold=-20dB:ratio=2.2:attack=8:release=120:makeup=2,"
                "loudnorm=I=-16:TP=-2:LRA=5"
            ),
            "-ar",
            "48000",
            "-ac",
            "2",
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
        "[1:a]adelay=350|350,volume=1.08,asplit=2[voice_sc][voice_mix];"
        "[2:a]volume=0.95[music];"
        "[music][voice_sc]sidechaincompress="
        "threshold=0.018:ratio=8:attack=18:release=280:makeup=1[ducked];"
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
        raise RuntimeError("R32 não produziu um MP4 válido ou o arquivo ficou pequeno demais.")

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
    print("===== R32 VALIDATION =====")
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

    print("===== UGI REEL RENDERER R32 =====")
    print(f"Title: {TITLE}")
    print(f"Duration: {DURATION}s")
    print(f"Render ID: {RENDER_ID}")
    print(f"Narration: {clean_text(NARRATION_RAW)}")
    print(f"Voice model: {VOICE_MODEL}")
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
    print("RENDER_SUCCESS_R32")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"FFMPEG_ERROR: returncode={exc.returncode}", file=sys.stderr)
        raise
    except Exception as exc:
        print(f"R32_ERROR: {exc}", file=sys.stderr)
        raise


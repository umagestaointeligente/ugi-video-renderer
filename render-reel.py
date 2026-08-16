#!/usr/bin/env python3
"""
UGI Reel Renderer R40.2 — HUMAN VISUAL COMMERCIAL ENGINE
===================================================
Evolução direta do R39.

Objetivos do R39:
- preservar VIDEO_TITLE, VIDEO_DURATION, VIDEO_RENDER_ID, VIDEO_CTA;
- respeitar a duração solicitada como duração final real;
- priorizar pessoas, situações empresariais e movimento na área principal;
- aplicar safe zones maiores para textos e separar título, overlay e apoio;
- preservar leitura confortável em Instagram, TikTok e YouTube Shorts;
- produzir narrativa comercial: dor -> tensão -> transformação -> desejo -> CTA;
- manter voz PT-BR Kokoro;
- sincronizar fala, cena e texto por timeline real;
- usar mídia humana real por cena quando disponível;
- aceitar mídia por arquivo local OU URL remota;
- evitar transcrição literal: texto visual curto, grande e orientado a impacto;
- aplicar QA comercial: duração, contraste, presença de mídia humana e CTA;
- preservar GitHub Actions -> FFmpeg -> Worker -> R2 -> Central de Aprovação.

Entradas opcionais:
- VIDEO_STORYBOARD_JSON
- VIDEO_SCENE_MEDIA_JSON
- VIDEO_MEDIA_MODE = pilot | production
- VIDEO_ASSET_DIR

Saídas:
- output/ugi-reel.mp4
- output/storyboard.json
- output/qa.json
"""

from __future__ import annotations

import json
import math
import os
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from urllib.parse import urlparse

WIDTH = 1080
HEIGHT = 1920
FPS = 30

OUTPUT = Path("output/ugi-reel.mp4")
WORK = Path("output/r402_work")
STORYBOARD_OUT = Path("output/storyboard.json")
QA_OUT = Path("output/qa.json")
ASSET_DIR = Path(os.getenv("VIDEO_ASSET_DIR") or "assets")

TITLE = (
    os.getenv("VIDEO_TITLE")
    or "Se tudo precisa passar por você, sua empresa não está crescendo. Está ficando dependente."
).strip()
CTA = (os.getenv("VIDEO_CTA") or "Conheça a UGI").strip()
RENDER_ID = (os.getenv("VIDEO_RENDER_ID") or "local-r402").strip()
MEDIA_MODE = (os.getenv("VIDEO_MEDIA_MODE") or "pilot").strip().lower()

try:
    REQUESTED_DURATION = int(os.getenv("VIDEO_DURATION") or "30")
except ValueError:
    REQUESTED_DURATION = 30

REQUESTED_DURATION = max(20, min(60, REQUESTED_DURATION))

FONT_REGULAR_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
]
FONT_BOLD_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
]

BG = "0x07101A"
PANEL = "0x101820"
PANEL_2 = "0x162330"
WHITE = "0xF4F7F9"
MUTED = "0xB8C4CF"
ACCENT = "0x35D0BA"
ACCENT_2 = "0x66A6FF"
WARM = "0xD7B56D"
RED = "0xE76F73"


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
    return re.sub(r"\s+", " ", str(value or "")).strip()


def esc_path(path: Path) -> str:
    return path.as_posix().replace("'", r"\'")


def write_text(name: str, content: str) -> Path:
    path = WORK / f"{name}.txt"
    path.write_text(content, encoding="utf-8")
    return path


def wrap_text(text: str, width: int = 20) -> str:
    return "\n".join(
        textwrap.wrap(
            clean_text(text),
            width=width,
            break_long_words=False,
            break_on_hyphens=False,
        )
    )


def default_storyboard() -> list[dict]:
    """
    R40: roteiro curto para caber em 30 s sem acelerar artificialmente a voz.
    A imagem humana conta a história; o overlay apenas reforça a ideia.
    """
    return [
        {
            "id": "hook",
            "role": "hook",
            "emotion": "pressure",
            "narration":
                "Se tudo precisa passar por você, sua empresa pode estar crescendo dependente.",
            "overlay": "TUDO DEPENDE DE VOCÊ?",
            "support": "Quando o líder vira passagem obrigatória, o crescimento trava.",
            "visual_prompt":
                "Vertical cinematic realistic video, Brazilian business manager in a modern office, multiple coworkers approaching for approvals, phone notifications, manager visibly overloaded, natural movement, authentic corporate environment, no text, no logos.",
            "min_duration": 4.8,
        },
        {
            "id": "pain",
            "role": "pain",
            "emotion": "friction",
            "narration":
                "A equipe espera. Decisões acumulam. O líder vira gargalo.",
            "overlay": "ESPERA • RETRABALHO • LENTIDÃO",
            "support": "Mais demanda. Menos velocidade.",
            "visual_prompt":
                "Vertical realistic business video, team waiting in a meeting for manager approval, stalled work, laptops and documents, subtle frustration, natural office movement, no text, no logos.",
            "min_duration": 4.3,
        },
        {
            "id": "turn",
            "role": "consequence",
            "emotion": "realization",
            "narration":
                "Controle demais não cria segurança. Cria dependência.",
            "overlay": "CONTROLE ≠ AUTONOMIA",
            "support": "Centralizar tudo custa velocidade.",
            "visual_prompt":
                "Vertical cinematic corporate video, overloaded manager surrounded by pending tasks while capable team members wait, visual metaphor of bottleneck, realistic people, no text, no logos.",
            "min_duration": 4.2,
        },
        {
            "id": "solution",
            "role": "solution",
            "emotion": "relief",
            "narration":
                "Gestão inteligente define critérios, distribui responsabilidades e mantém clareza.",
            "overlay": "AUTONOMIA COM CRITÉRIOS.",
            "support": "Decisões no nível certo. Controle sem centralização.",
            "visual_prompt":
                "Vertical realistic corporate video, confident leader aligning priorities with diverse team at planning board, team members taking ownership, collaboration, positive movement, no text, no logos.",
            "min_duration": 5.0,
        },
        {
            "id": "desire",
            "role": "desire",
            "emotion": "aspiration",
            "narration":
                "A operação ganha velocidade. E você volta a liderar o crescimento.",
            "overlay": "LIDERE. NÃO CENTRALIZE.",
            "support": "Sua equipe avança sem depender de você para tudo.",
            "visual_prompt":
                "Vertical cinematic business video, autonomous team working confidently while manager reviews strategic indicators and coaches team, modern office, energetic but professional, no text, no logos.",
            "min_duration": 4.8,
        },
        {
            "id": "cta",
            "role": "cta",
            "emotion": "confidence",
            "narration":
                "Conheça a UGI. Uma Gestão Inteligente.",
            "overlay": "CONHEÇA A UGI",
            "support": "Transforme gestão em execução.",
            "visual_prompt":
                "Vertical premium corporate closing shot, confident manager and team moving forward together in modern workplace, aspirational realistic lighting, clean composition for brand overlay, no text, no logos.",
            "min_duration": 3.8,
            "cta": CTA,
        },
    ]

def load_storyboard() -> list[dict]:
    raw = os.getenv("VIDEO_STORYBOARD_JSON", "").strip()
    if raw:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"VIDEO_STORYBOARD_JSON inválido: {exc}") from exc
        scenes = parsed.get("scenes") if isinstance(parsed, dict) else parsed
    else:
        scenes = default_storyboard()

    if not isinstance(scenes, list) or len(scenes) < 3:
        raise RuntimeError("Storyboard inválido: mínimo de 3 cenas.")

    out = []
    for idx, scene in enumerate(scenes, start=1):
        if not isinstance(scene, dict):
            raise RuntimeError(f"Cena {idx} inválida.")

        narration = clean_text(scene.get("narration"))
        overlay = clean_text(scene.get("overlay") or scene.get("on_screen_text"))
        if not narration:
            raise RuntimeError(f"Cena {idx} sem narration.")
        if not overlay:
            raise RuntimeError(f"Cena {idx} sem overlay.")

        out.append(
            {
                "index": idx,
                "id": clean_text(scene.get("id")) or f"scene-{idx}",
                "role": clean_text(scene.get("role")) or "content",
                "emotion": clean_text(scene.get("emotion")) or "neutral",
                "narration": narration,
                "overlay": overlay,
                "support": clean_text(scene.get("support")),
                "visual_prompt": clean_text(scene.get("visual_prompt")),
                "min_duration": max(2.6, float(scene.get("min_duration") or 4.0)),
                "cta": clean_text(scene.get("cta")),
            }
        )
    return out


def load_scene_media_config() -> dict[int, dict]:
    """
    Exemplo:
    {
      "1":{"url":"https://.../clip.mp4","type":"video"},
      "2":{"path":"assets/scene-2.jpg","type":"image"}
    }
    """
    raw = os.getenv("VIDEO_SCENE_MEDIA_JSON", "").strip()
    if not raw:
        return {}

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"VIDEO_SCENE_MEDIA_JSON inválido: {exc}") from exc

    result = {}
    for key, value in (parsed or {}).items():
        try:
            idx = int(key)
        except (TypeError, ValueError):
            continue
        if isinstance(value, str):
            value = {"url": value}
        if isinstance(value, dict):
            result[idx] = value
    return result


def ffprobe_duration(path: Path) -> float:
    cp = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(cp.stdout.strip())


def synthesize_scene_voice(scene: dict) -> Path:
    try:
        import numpy as np
        import soundfile as sf
        from kokoro import KPipeline
    except Exception as exc:
        raise RuntimeError("Kokoro TTS não instalado no workflow.") from exc

    raw_path = WORK / f"voice-{scene['index']}-raw.wav"
    out_path = WORK / f"voice-{scene['index']}.wav"

    pipeline = KPipeline(lang_code="p")
    chunks = []
    for result in pipeline(
        scene["narration"],
        voice="pf_dora",
        speed=1.04,
        split_pattern=r"\n+",
    ):
        audio = getattr(result, "audio", None)
        if audio is not None:
            chunks.append(np.asarray(audio, dtype=np.float32))

    if not chunks:
        raise RuntimeError(f"Kokoro sem áudio na cena {scene['index']}.")

    sf.write(
        str(raw_path),
        np.concatenate(chunks),
        24000,
        subtype="PCM_16",
    )

    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(raw_path),
            "-af",
            (
                "highpass=f=80,"
                "lowpass=f=10000,"
                "acompressor=threshold=-20dB:ratio=2:attack=8:release=120:makeup=2,"
                "loudnorm=I=-16:TP=-2:LRA=5"
            ),
            "-ar", "48000",
            "-ac", "2",
            str(out_path),
        ]
    )
    return out_path


def download_media(url: str, index: int) -> Path:
    parsed = urlparse(url)
    suffix = Path(parsed.path).suffix.lower()
    if suffix not in {".mp4", ".mov", ".jpg", ".jpeg", ".png", ".webp"}:
        suffix = ".mp4"

    out = WORK / f"remote-scene-{index}{suffix}"
    run(
        [
            "curl",
            "-L",
            "--fail",
            "--silent",
            "--show-error",
            "--max-time",
            "45",
            "-o",
            str(out),
            url,
        ]
    )
    if not out.exists() or out.stat().st_size < 1000:
        raise RuntimeError(f"Mídia remota inválida na cena {index}.")
    return out


def resolve_scene_media(index: int, config: dict[int, dict]) -> tuple[str, Path | None, str]:
    entry = config.get(index) or {}

    # 1) configuração explícita
    path_value = clean_text(entry.get("path"))
    url_value = clean_text(entry.get("url"))
    declared = clean_text(entry.get("type")).lower()

    path = None
    source = "none"

    if path_value:
        candidate = Path(path_value)
        if candidate.exists():
            path = candidate
            source = "configured_path"
    elif url_value:
        try:
            path = download_media(url_value, index)
            source = "remote_url"
        except Exception as exc:
            print(f"MEDIA_DOWNLOAD_WARNING scene={index}: {exc}")

    # 2) convenção local
    if path is None:
        candidates = [
            ASSET_DIR / f"scene-{index}.mp4",
            ASSET_DIR / f"scene-{index}.mov",
            ASSET_DIR / f"scene-{index}.jpg",
            ASSET_DIR / f"scene-{index}.jpeg",
            ASSET_DIR / f"scene-{index}.png",
            ASSET_DIR / f"scene-{index}.webp",
        ]
        for candidate in candidates:
            if candidate.exists() and candidate.stat().st_size > 0:
                path = candidate
                source = "asset_dir"
                break

    if path is None:
        return "fallback", None, "fallback"

    ext = path.suffix.lower()
    if declared in {"video", "image"}:
        kind = declared
    elif ext in {".mp4", ".mov"}:
        kind = "video"
    else:
        kind = "image"

    return kind, path, source


def fit_scene_durations(scenes: list[dict], voice_durations: list[float]) -> list[float]:
    """
    R40: a soma das cenas fecha exatamente em VIDEO_DURATION.
    O roteiro padrão foi reduzido para caber naturalmente em ~30 s.
    Se uma voz isolada exceder sua janela, ela será ajustada na timeline de áudio.
    """
    mins = [max(2.8, float(scene["min_duration"])) for scene in scenes]
    total_min = sum(mins)

    if total_min > REQUESTED_DURATION:
        scale = REQUESTED_DURATION / total_min
        durations = [max(2.5, m * scale) for m in mins]
    else:
        durations = mins[:]
        extra = REQUESTED_DURATION - sum(durations)
        weights = [
            1.15 if scene["role"] in {"hook", "solution", "desire", "cta"} else 0.9
            for scene in scenes
        ]
        sw = sum(weights)
        durations = [d + extra * weights[i] / sw for i, d in enumerate(durations)]

    # Fecha matematicamente no alvo.
    durations = [round(d, 3) for d in durations]
    durations[-1] = round(REQUESTED_DURATION - sum(durations[:-1]), 3)
    return durations

def drawtext_filter(
    textfile: Path,
    *,
    fontfile: str,
    fontsize: int,
    fontcolor: str,
    x: str,
    y: str,
    alpha: str = "1",
    line_spacing: int = 12,
    borderw: int = 0,
    bordercolor: str = "black@0.0",
) -> str:
    return (
        "drawtext="
        f"fontfile='{fontfile}':"
        f"textfile='{esc_path(textfile)}':reload=0:"
        f"fontsize={fontsize}:fontcolor={fontcolor}:"
        f"x={x}:y={y}:line_spacing={line_spacing}:"
        f"alpha='{alpha}':"
        f"borderw={borderw}:bordercolor={bordercolor}"
    )


def role_accent(scene: dict) -> str:
    if scene["role"] in {"hook", "pain"}:
        return RED
    if scene["role"] in {"solution", "desire", "cta"}:
        return ACCENT
    return ACCENT_2


def add_text_layers(filters: list[str], scene: dict, dur: float) -> None:
    """
    R40.2 — tipografia com safe zones:
    - marca no topo;
    - área visual principal livre;
    - overlay principal no terço inferior;
    - texto de apoio com respiro real;
    - proteção contra aproximação excessiva entre blocos.
    """
    accent = role_accent(scene)

    overlay_file = write_text(
        f"scene-{scene['index']}-overlay",
        wrap_text(scene["overlay"], 18),
    )
    support_file = write_text(
        f"scene-{scene['index']}-support",
        wrap_text(scene["support"], 34),
    )
    brand_file = write_text(
        f"scene-{scene['index']}-brand",
        "UMA GESTÃO INTELIGENTE",
    )

    # Safe zones universais: topo e rodapé de interfaces sociais.
    top_safe = 150
    bottom_safe = 1780

    # O painel textual foi empurrado para baixo e ganhou mais altura.
    panel_y = 1265
    panel_h = 455

    filters.extend(
        [
            f"drawbox=x=0:y=0:w={WIDTH}:h=245:color=black@0.26:t=fill",
            f"drawbox=x=0:y=1180:w={WIDTH}:h=740:color=black@0.46:t=fill",
            f"drawbox=x=66:y={panel_y}:w={WIDTH-132}:h={panel_h}:color={PANEL}@0.64:t=fill",
            f"drawbox=x=66:y={panel_y}:w=10:h={panel_h}:color={accent}@0.98:t=fill",
        ]
    )

    # Marca discretamente no topo; não compete com o conteúdo.
    filters.append(
        drawtext_filter(
            brand_file,
            fontfile=FONT_BOLD,
            fontsize=22,
            fontcolor=WHITE,
            x="w-text_w-78",
            y=str(top_safe),
            alpha="0.90",
        )
    )

    # Overlay principal — mais alto, mas ainda separado do apoio.
    overlay_size = 64
    if len(scene["overlay"]) > 34:
        overlay_size = 56
    if len(scene["overlay"]) > 52:
        overlay_size = 48

    overlay_y = 1335
    filters.append(
        drawtext_filter(
            overlay_file,
            fontfile=FONT_BOLD,
            fontsize=overlay_size,
            fontcolor=WHITE,
            x="102",
            y=str(overlay_y),
            line_spacing=12,
            alpha="if(lt(t,0.10),0,min((t-0.10)/0.24,1))",
            borderw=1,
            bordercolor="black@0.30",
        )
    )

    # Apoio — mais abaixo e menor, criando respiro perceptível.
    if scene["support"]:
        support_y = 1585
        filters.append(
            drawtext_filter(
                support_file,
                fontfile=FONT_REGULAR,
                fontsize=28,
                fontcolor=MUTED,
                x="102",
                y=str(support_y),
                line_spacing=10,
                alpha="if(lt(t,0.42),0,min((t-0.42)/0.28,1))",
            )
        )

    # Progresso fora da área textual e acima da interface inferior.
    progress_y = 1748
    filters.append(
        f"drawbox=x=82:y={progress_y}:w={WIDTH-164}:h=4:color={WHITE}@0.16:t=fill"
    )
    filters.append(
        f"drawbox=x=82:y={progress_y}:w='({WIDTH-164})*min(t/{dur},1)':h=4:color={accent}@0.96:t=fill"
    )


def render_scene_visual(
    scene: dict,
    dur: float,
    media_config: dict[int, dict],
    output: Path,
) -> dict:
    kind, media_path, media_source = resolve_scene_media(scene["index"], media_config)
    filters = []

    if kind == "video":
        input_args = [
            "-stream_loop", "-1",
            "-i", str(media_path),
        ]
        filters.extend(
            [
                f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase",
                f"crop={WIDTH}:{HEIGHT}",
                "setsar=1",
            ]
        )

    elif kind == "image":
        frames = max(1, round(dur * FPS))
        input_args = [
            "-loop", "1",
            "-framerate", str(FPS),
            "-i", str(media_path),
        ]
        filters.extend(
            [
                "scale=1500:-2",
                (
                    "zoompan="
                    "z='min(zoom+0.00075,1.09)':"
                    "x='iw/2-(iw/zoom/2)+14*sin(on/23)':"
                    "y='ih/2-(ih/zoom/2)+10*cos(on/27)':"
                    f"d={frames}:s={WIDTH}x{HEIGHT}:fps={FPS}"
                ),
                "setsar=1",
            ]
        )

    else:
        # Fallback visual mais vivo que o R38, mas ainda marcado como fallback.
        input_args = [
            "-f", "lavfi",
            "-i", f"color=c={BG}:s={WIDTH}x{HEIGHT}:r={FPS}:d={dur}",
        ]
        accent = role_accent(scene)
        filters.extend(
            [
                f"drawbox=x=72:y=290:w={WIDTH-144}:h=790:color={PANEL_2}@0.88:t=fill",
                f"drawbox=x='-600+t*210':y=430:w=560:h=14:color={accent}@0.68:t=fill",
                f"drawbox=x='{WIDTH+180}-t*180':y=760:w=420:h=10:color={ACCENT_2}@0.42:t=fill",
                f"drawbox=x='110+80*sin(t*1.7)':y=900:w=310:h=80:color={WHITE}@0.07:t=fill",
                f"drawbox=x='650-70*sin(t*1.4)':y=560:w=280:h=72:color={accent}@0.10:t=fill",
                "noise=alls=2:allf=t+u",
            ]
        )

    add_text_layers(filters, scene, dur)
    filters.append("vignette=PI/6")
    filters.append("fade=t=in:st=0:d=0.10")
    filters.append(f"fade=t=out:st={max(0.05, dur-0.12)}:d=0.12")

    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            *input_args,
            "-t", f"{dur:.3f}",
            "-vf", ",".join(filters),
            "-an",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "19",
            "-pix_fmt", "yuv420p",
            "-r", str(FPS),
            "-movflags", "+faststart",
            str(output),
        ]
    )

    return {
        "media_kind": kind,
        "media_path": str(media_path) if media_path else None,
        "media_source": media_source,
    }


def create_voice_timeline(
    voice_files: list[Path],
    scene_durations: list[float],
) -> Path:
    """
    Ajusta cada locução à janela da própria cena.
    Só acelera quando necessário e limita cada estágio do atempo a 2x.
    """
    padded = []

    for idx, (voice, duration) in enumerate(zip(voice_files, scene_durations), start=1):
        source_duration = ffprobe_duration(voice)
        out = WORK / f"voice-{idx}-timeline.wav"

        filters = []
        usable = max(0.8, duration - 0.20)

        if source_duration > usable:
            factor = source_duration / usable
            stages = []
            while factor > 2.0:
                stages.append("atempo=2.0")
                factor /= 2.0
            if factor > 1.001:
                stages.append(f"atempo={factor:.5f}")
            filters.extend(stages)

        filters.append(f"apad=whole_dur={duration}")
        af = ",".join(filters)

        run(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(voice),
                "-af", af,
                "-t", f"{duration:.3f}",
                "-ar", "48000",
                "-ac", "2",
                str(out),
            ]
        )
        padded.append(out)

    concat_file = WORK / "voice-concat.txt"
    concat_file.write_text(
        "\n".join(f"file '{p.resolve().as_posix()}'" for p in padded),
        encoding="utf-8",
    )

    output = WORK / "voice-timeline.wav"
    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(output),
        ]
    )
    return output

def concat_visuals(scene_files: list[Path]) -> Path:
    concat_file = WORK / "visual-concat.txt"
    concat_file.write_text(
        "\n".join(f"file '{p.resolve().as_posix()}'" for p in scene_files),
        encoding="utf-8",
    )

    output = WORK / "joined.mp4"
    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(output),
        ]
    )
    return output


def finalize(video: Path, voice: Path, final_duration: float) -> None:
    pulse = "(0.50+0.50*sin(2*PI*1.7*t))"
    music_expr = (
        "0.022*sin(2*PI*110*t)"
        "+0.016*sin(2*PI*164.81*t)"
        "+0.012*sin(2*PI*220*t)"
        "+0.009*" + pulse + "*sin(2*PI*329.63*t)"
        "+0.006*" + pulse + "*sin(2*PI*440*t)"
    )

    music_src = (
        f"aevalsrc='{music_expr}':s=48000:d={final_duration},"
        "aformat=sample_fmts=fltp:channel_layouts=stereo,"
        "highpass=f=70,lowpass=f=7200,"
        "acompressor=threshold=-22dB:ratio=2:attack=12:release=160:makeup=2,"
        "afade=t=in:st=0:d=0.20,"
        f"afade=t=out:st={max(0.1, final_duration-0.75)}:d=0.75"
    )

    mix = (
        "[1:a]volume=1.14,asplit=2[voice_sc][voice_mix];"
        "[2:a]volume=0.66[music];"
        "[music][voice_sc]sidechaincompress="
        "threshold=0.015:ratio=10:attack=12:release=230:makeup=1[ducked];"
        "[ducked][voice_mix]amix=inputs=2:duration=longest:dropout_transition=0,"
        "loudnorm=I=-14:TP=-1.2:LRA=6[aout]"
    )

    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(video),
            "-i", str(voice),
            "-f", "lavfi",
            "-i", music_src,
            "-filter_complex", mix,
            "-map", "0:v:0",
            "-map", "[aout]",
            "-t", f"{final_duration:.3f}",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "160k",
            "-ar", "48000",
            "-ac", "2",
            "-movflags", "+faststart",
            str(OUTPUT),
        ]
    )


def qa_report(scenes: list[dict], final_duration: float) -> dict:
    human_scenes = sum(
        1 for scene in scenes
        if scene.get("media_kind") in {"video", "image"}
    )
    fallback_scenes = len(scenes) - human_scenes

    issues = []

    if abs(final_duration - REQUESTED_DURATION) > 0.12:
        issues.append("final_duration_mismatch")

    if final_duration < 20:
        issues.append("duration_too_short_for_commercial_story")
    if final_duration > 60:
        issues.append("duration_above_initial_shortform_guardrail")

    if not any(scene["role"] == "hook" for scene in scenes):
        issues.append("hook_missing")
    if not any(scene["role"] == "cta" for scene in scenes):
        issues.append("cta_missing")

    if MEDIA_MODE == "production" and human_scenes < max(3, math.ceil(len(scenes) * 0.6)):
        issues.append("insufficient_human_media_for_production")

    commercial_ready = not issues and (
        MEDIA_MODE != "production"
        or human_scenes >= max(3, math.ceil(len(scenes) * 0.6))
    )

    return {
        "version": "R40.2",
        "render_id": RENDER_ID,
        "media_mode": MEDIA_MODE,
        "scene_count": len(scenes),
        "human_media_scenes": human_scenes,
        "fallback_scenes": fallback_scenes,
        "requested_duration": REQUESTED_DURATION,
        "final_duration": round(final_duration, 3),
        "commercial_ready": commercial_ready,
        "issues": issues,
    }


def validate_output() -> None:
    if not OUTPUT.exists() or OUTPUT.stat().st_size < 10_000:
        raise RuntimeError("R40.2 não produziu MP4 válido.")

    signature = OUTPUT.read_bytes()[:12]
    if len(signature) < 12 or signature[4:8] != b"ftyp":
        raise RuntimeError("Assinatura MP4 ftyp ausente.")

    cp = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries",
            "stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
            "-show_entries", "format=duration,size",
            "-of", "default=noprint_wrappers=1",
            str(OUTPUT),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    print("===== R40.2 VALIDATION =====")
    print(cp.stdout.strip())
    print("==========================")


def main() -> int:
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise RuntimeError("FFmpeg/ffprobe não encontrados.")
    if shutil.which("curl") is None:
        raise RuntimeError("curl não encontrado no runner.")

    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True, exist_ok=True)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    scenes = load_storyboard()
    media_config = load_scene_media_config()

    print("===== UGI R40.2 HUMAN VISUAL COMMERCIAL ENGINE =====")
    print(f"Title: {TITLE}")
    print(f"Requested duration: {REQUESTED_DURATION}s")
    print(f"Scenes: {len(scenes)}")
    print(f"Media mode: {MEDIA_MODE}")
    print("==============================================")

    voice_files = []
    voice_durations = []

    for scene in scenes:
        voice = synthesize_scene_voice(scene)
        duration = ffprobe_duration(voice)
        scene["voice_duration"] = round(duration, 3)
        voice_files.append(voice)
        voice_durations.append(duration)

    durations = fit_scene_durations(scenes, voice_durations)
    final_duration = round(sum(durations), 3)

    scene_files = []
    cursor = 0.0

    for scene, duration in zip(scenes, durations):
        scene["start"] = round(cursor, 3)
        scene["duration"] = duration

        output = WORK / f"scene-{scene['index']}.mp4"
        media_info = render_scene_visual(
            scene,
            duration,
            media_config,
            output,
        )
        scene.update(media_info)
        scene_files.append(output)
        cursor += duration

    storyboard_payload = {
        "version": "R40.2",
        "render_id": RENDER_ID,
        "title": TITLE,
        "requested_duration": REQUESTED_DURATION,
        "final_duration": final_duration,
        "scenes": scenes,
    }
    STORYBOARD_OUT.write_text(
        json.dumps(storyboard_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    voice_timeline = create_voice_timeline(voice_files, durations)
    joined = concat_visuals(scene_files)
    finalize(joined, voice_timeline, final_duration)
    validate_output()

    qa = qa_report(scenes, final_duration)
    QA_OUT.write_text(
        json.dumps(qa, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("===== R40.2 QA =====")
    print(json.dumps(qa, ensure_ascii=False, indent=2))
    print("==================")

    if MEDIA_MODE == "production" and not qa["commercial_ready"]:
        raise RuntimeError(
            "R40.2 commercial QA reprovado: " + ", ".join(qa["issues"])
        )

    print("RENDER_SUCCESS_R40_2")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"FFMPEG_ERROR: returncode={exc.returncode}", file=sys.stderr)
        raise
    except Exception as exc:
        print(f"R40_2_ERROR: {exc}", file=sys.stderr)
        raise


#!/usr/bin/env python3
"""
UGI Reel Renderer R39 — CREATIVE COMMERCIAL ENGINE
===================================================
Evolução direta do R38.

Objetivos do R39:
- preservar VIDEO_TITLE, VIDEO_DURATION, VIDEO_RENDER_ID, VIDEO_CTA;
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
WORK = Path("output/r39_work")
STORYBOARD_OUT = Path("output/storyboard.json")
QA_OUT = Path("output/qa.json")
ASSET_DIR = Path(os.getenv("VIDEO_ASSET_DIR") or "assets")

TITLE = (
    os.getenv("VIDEO_TITLE")
    or "Se tudo precisa passar por você, sua empresa não está crescendo. Está ficando dependente."
).strip()
CTA = (os.getenv("VIDEO_CTA") or "Conheça a UGI").strip()
RENDER_ID = (os.getenv("VIDEO_RENDER_ID") or "local-r39").strip()
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
    Storyboard comercial padrão.
    Os overlays são curtos por design: não repetem toda a locução.
    """
    return [
        {
            "id": "hook",
            "role": "hook",
            "emotion": "pressure",
            "narration":
                "Se tudo precisa passar por você, talvez sua empresa não esteja crescendo de verdade. Talvez esteja ficando dependente.",
            "overlay": "TUDO DEPENDE DE VOCÊ?",
            "support": "Isso parece controle. Mas pode ser gargalo.",
            "visual_prompt":
                "Gestor em escritório moderno sendo interrompido por várias pessoas, notificações e solicitações simultâneas, expressão de sobrecarga, equipe aguardando decisões, movimento corporativo realista.",
            "min_duration": 5.0,
        },
        {
            "id": "tension",
            "role": "pain",
            "emotion": "friction",
            "narration":
                "Quando cada decisão para no gestor, a equipe espera, o trabalho desacelera e o retrabalho aumenta.",
            "overlay": "ESPERA • RETRABALHO • LENTIDÃO",
            "support": "O problema não é trabalhar mais. É decidir melhor.",
            "visual_prompt":
                "Equipe em reunião olhando para o líder aguardando aprovação, documentos e notebooks abertos, colaboradores interrompendo o gestor, sensação de fila e dependência.",
            "min_duration": 5.0,
        },
        {
            "id": "consequence",
            "role": "consequence",
            "emotion": "realization",
            "narration":
                "Centralizar pode funcionar no começo. Mas quando a empresa cresce, o que parecia controle vira limite.",
            "overlay": "O CONTROLE VIROU GARGALO.",
            "support": "Crescimento sem autonomia aumenta a dependência.",
            "visual_prompt":
                "Gestor sobrecarregado diante de quadro de tarefas e mensagens enquanto a equipe aguarda, ambiente empresarial movimentado, sensação de gargalo operacional.",
            "min_duration": 5.0,
        },
        {
            "id": "transformation",
            "role": "solution",
            "emotion": "relief",
            "narration":
                "Gestão inteligente distribui responsabilidades, cria critérios claros e permite que decisões aconteçam no nível certo.",
            "overlay": "AUTONOMIA COM CRITÉRIOS.",
            "support": "Menos dependência. Mais velocidade e clareza.",
            "visual_prompt":
                "Líder alinhando prioridades com equipe em quadro de planejamento, colaboradores tomando decisões, ambiente profissional, autonomia, confiança e clareza.",
            "min_duration": 5.4,
        },
        {
            "id": "desire",
            "role": "desire",
            "emotion": "aspiration",
            "narration":
                "Sua empresa pode crescer sem depender de você para tudo. Você deixa de ser o gargalo e volta a liderar o crescimento.",
            "overlay": "LIDERE O CRESCIMENTO.",
            "support": "A operação funciona. Você ganha visão e controle.",
            "visual_prompt":
                "Equipe trabalhando com autonomia enquanto o gestor acompanha indicadores e conversa estrategicamente com o time, clima de confiança e crescimento.",
            "min_duration": 5.2,
        },
        {
            "id": "cta",
            "role": "cta",
            "emotion": "confidence",
            "narration":
                "Conheça a UGI e transforme gestão em execução.",
            "overlay": "CONHEÇA A UGI",
            "support": "Uma Gestão Inteligente.",
            "visual_prompt":
                "Equipe confiante em ambiente corporativo contemporâneo, líder em posição estratégica, composição limpa para encerramento de marca.",
            "min_duration": 3.4,
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
    Não corta locução. A fala governa a duração.
    O alvo solicitado serve como referência editorial, não como guilhotina.
    """
    durations = [
        max(scene["min_duration"], voice + 0.42)
        for scene, voice in zip(scenes, voice_durations)
    ]

    total = sum(durations)

    # Se houver folga até o alvo, distribui principalmente no hook/CTA/desejo.
    if total < REQUESTED_DURATION:
        extra = REQUESTED_DURATION - total
        weights = []
        for scene in scenes:
            role = scene["role"]
            if role in {"hook", "desire", "cta"}:
                weights.append(1.25)
            else:
                weights.append(0.9)

        weight_sum = sum(weights)
        durations = [
            d + extra * weights[i] / weight_sum
            for i, d in enumerate(durations)
        ]

    return [round(d, 3) for d in durations]


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
    accent = role_accent(scene)

    overlay_file = write_text(
        f"scene-{scene['index']}-overlay",
        wrap_text(scene["overlay"], 18),
    )
    support_file = write_text(
        f"scene-{scene['index']}-support",
        wrap_text(scene["support"], 38),
    )
    brand_file = write_text(
        f"scene-{scene['index']}-brand",
        "UMA GESTÃO INTELIGENTE",
    )

    # Top/Bottom readability shields
    filters.extend(
        [
            f"drawbox=x=0:y=0:w={WIDTH}:h=260:color=black@0.30:t=fill",
            f"drawbox=x=0:y=1190:w={WIDTH}:h=730:color=black@0.50:t=fill",
            f"drawbox=x=72:y=1310:w={WIDTH-144}:h=405:color={PANEL}@0.66:t=fill",
            f"drawbox=x=72:y=1310:w=10:h=405:color={accent}@0.98:t=fill",
        ]
    )

    filters.append(
        drawtext_filter(
            brand_file,
            fontfile=FONT_BOLD,
            fontsize=24,
            fontcolor=WHITE,
            x="w-text_w-82",
            y="92",
            alpha="0.94",
        )
    )

    # Overlay principal: grande, curto, sempre legível.
    overlay_size = 66
    if len(scene["overlay"]) > 34:
        overlay_size = 58
    if len(scene["overlay"]) > 52:
        overlay_size = 50

    filters.append(
        drawtext_filter(
            overlay_file,
            fontfile=FONT_BOLD,
            fontsize=overlay_size,
            fontcolor=WHITE,
            x="108",
            y="1370",
            line_spacing=10,
            alpha="if(lt(t,0.10),0,min((t-0.10)/0.24,1))",
            borderw=1,
            bordercolor="black@0.28",
        )
    )

    if scene["support"]:
        filters.append(
            drawtext_filter(
                support_file,
                fontfile=FONT_REGULAR,
                fontsize=31,
                fontcolor=MUTED,
                x="108",
                y="1585",
                line_spacing=9,
                alpha="if(lt(t,0.35),0,min((t-0.35)/0.28,1))",
            )
        )

    # Scene progress
    filters.append(
        f"drawbox=x=84:y=1778:w={WIDTH-168}:h=4:color={WHITE}@0.18:t=fill"
    )
    filters.append(
        f"drawbox=x=84:y=1778:w='({WIDTH-168})*min(t/{dur},1)':h=4:color={accent}@0.96:t=fill"
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
    padded = []

    for idx, (voice, duration) in enumerate(zip(voice_files, scene_durations), start=1):
        out = WORK / f"voice-{idx}-timeline.wav"
        run(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(voice),
                "-af", f"apad=whole_dur={duration}",
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
        "version": "R39",
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
        raise RuntimeError("R39 não produziu MP4 válido.")

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
    print("===== R39 VALIDATION =====")
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

    print("===== UGI R39 CREATIVE COMMERCIAL ENGINE =====")
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
        "version": "R39",
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

    print("===== R39 QA =====")
    print(json.dumps(qa, ensure_ascii=False, indent=2))
    print("==================")

    if MEDIA_MODE == "production" and not qa["commercial_ready"]:
        raise RuntimeError(
            "R39 commercial QA reprovado: " + ", ".join(qa["issues"])
        )

    print("RENDER_SUCCESS_R39")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"FFMPEG_ERROR: returncode={exc.returncode}", file=sys.stderr)
        raise
    except Exception as exc:
        print(f"R39_ERROR: {exc}", file=sys.stderr)
        raise


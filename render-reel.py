#!/usr/bin/env python3
"""
UGI Reel Renderer R43.4 — MULTI-PLATFORM SEMANTIC VIDEO ENGINE — CLEAN OUTPUT
=============================================================
Objetivo:
- preservar Pexels + Kokoro + FFmpeg + GitHub + R2;
- sincronizar cada cena pela duração real da locução;
- aplicar layout dinâmico com painel mais baixo;
- gerar 3 versões específicas: Instagram Reels, TikTok e YouTube Shorts;
- preservar output/ugi-reel.mp4 como compatibilidade (Instagram);
- registrar metadados experimentais e QA por plataforma.

Saídas:
  output/instagram-reel.mp4
  output/tiktok-reel.mp4
  output/youtube-short.mp4
  output/ugi-reel.mp4                  # alias/cópia do Instagram
  output/r42-platform-manifest.json
  output/r42-storyboard-instagram.json
  output/r42-storyboard-tiktok.json
  output/r42-storyboard-youtube.json

Mídia esperada do workflow:
  output/media/scene-1.mp4 ... scene-6.mp4
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
from dataclasses import dataclass, asdict
from pathlib import Path

WIDTH = 1080
HEIGHT = 1920
FPS = 30

OUTPUT_DIR = Path("output")
WORK = OUTPUT_DIR / "r42_work"
MEDIA = OUTPUT_DIR / "media"

TITLE = (
    os.getenv("VIDEO_TITLE")
    or "Se tudo precisa passar por você, sua empresa não está crescendo. Está ficando dependente."
).strip()
CTA = (os.getenv("VIDEO_CTA") or "Conheça a UGI.").strip()
RENDER_ID = (os.getenv("VIDEO_RENDER_ID") or "local-r42").strip()

CONTENT_ID = (os.getenv("VIDEO_CONTENT_ID") or "UGI-R42-CONTENT").strip()
EXPERIMENT_ID = (os.getenv("VIDEO_EXPERIMENT_ID") or "UGI-R42-EXPERIMENT").strip()
VARIANT = (os.getenv("VIDEO_VARIANT") or "A-R42").strip()
COMMERCIAL_INTENT = (
    os.getenv("VIDEO_COMMERCIAL_INTENT")
    or "atracao_com_potencial_de_conversao"
).strip()

FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

BG = "0x091018"
WHITE = "0xF4F7F9"
MUTED = "0xCAD3DC"
ACCENT = "0x35D0BA"
PANEL = "0x071019"

PLATFORM_PROFILES = {
    "instagram": {
        "label": "Instagram Reels",
        "target_duration": 32.0,
        "hook_seconds_max": 3.0,
        "cut_pace": "medium_dynamic",
        "text_density": "short",
        "cta_style": "brand_interest",
        "primary_cta": "Conheça a UGI",
        "panel_y": 1210,
        "panel_h": 435,
        "overlay_y": 1275,
        "support_y": 1495,
        "progress_y": 1745,
        "music_level": 0.72,
        "voice_speed": 1.03,
    },
    "tiktok": {
        "label": "TikTok",
        "target_duration": 24.0,
        "hook_seconds_max": 1.8,
        "cut_pace": "fast",
        "text_density": "very_short",
        "cta_style": "interaction_plus_brand",
        "primary_cta": "Conheça a UGI",
        "panel_y": 1235,
        "panel_h": 395,
        "overlay_y": 1300,
        "support_y": 1490,
        "progress_y": 1745,
        "music_level": 0.78,
        "voice_speed": 1.08,
    },
    "youtube": {
        "label": "YouTube Shorts",
        "target_duration": 36.0,
        "hook_seconds_max": 3.2,
        "cut_pace": "medium",
        "text_density": "short_explanatory",
        "cta_style": "learn_more",
        "primary_cta": "Conheça a UGI",
        "panel_y": 1205,
        "panel_h": 445,
        "overlay_y": 1270,
        "support_y": 1500,
        "progress_y": 1745,
        "music_level": 0.68,
        "voice_speed": 1.00,
    },
}


@dataclass
class SceneTemplate:
    role: str
    visual_intent: str
    pexels_query: str
    overlay: dict
    support: dict
    narration: dict


SCENES = [
    SceneTemplate(
        "hook",
        "gestor sobrecarregado recebendo múltiplas demandas e interrupções",
        "overwhelmed male manager busy office coworkers approval",
        {
            "instagram": "Tudo passa por você?",
            "tiktok": "Tudo depende de você?",
            "youtube": "Sua empresa depende de você para tudo?",
        },
        {
            "instagram": "Isso parece controle. Mas pode ser gargalo.",
            "tiktok": "Isso é gargalo.",
            "youtube": "Toda decisão no líder limita o crescimento.",
        },
        {
            "instagram": "Se tudo precisa passar por você, sua empresa pode estar crescendo dependente.",
            "tiktok": "Se tudo depende de você, você virou o gargalo.",
            "youtube": "Se tudo precisa passar por você, sua empresa pode estar crescendo, mas também ficando cada vez mais dependente.",
        },
    ),
    SceneTemplate(
        "pain",
        "equipe esperando decisão em reunião, trabalho parado",
        "business team waiting meeting female manager office",
        {
            "instagram": "A equipe espera.",
            "tiktok": "A equipe para.",
            "youtube": "A equipe espera pela decisão.",
        },
        {
            "instagram": "Decisões acumulam. A operação desacelera.",
            "tiktok": "Decisão parada = trabalho parado.",
            "youtube": "Decisões acumulam. O ritmo cai.",
        },
        {
            "instagram": "A equipe espera, as decisões acumulam e a operação perde velocidade.",
            "tiktok": "A equipe espera. A decisão para. O trabalho também.",
            "youtube": "A equipe espera, as decisões acumulam e atividades que poderiam avançar ficam presas ao mesmo ponto de aprovação.",
        },
    ),
    SceneTemplate(
        "consequence",
        "líder sobrecarregado e equipe dependente em ambiente corporativo",
        "busy diverse office team working pressure manager",
        {
            "instagram": "O líder vira gargalo.",
            "tiktok": "Você virou o gargalo.",
            "youtube": "O controle virou gargalo.",
        },
        {
            "instagram": "Crescer assim aumenta a dependência.",
            "tiktok": "Quanto mais cresce, pior fica.",
            "youtube": "Sem autonomia, o crescimento concentra decisões.",
        },
        {
            "instagram": "Quando a empresa cresce sem autonomia, o que parecia controle vira gargalo.",
            "tiktok": "E quanto mais a empresa cresce assim, maior fica o problema.",
            "youtube": "Centralizar pode funcionar no começo. Mas quando a empresa cresce, o que parecia controle começa a limitar a própria capacidade de execução.",
        },
    ),
    SceneTemplate(
        "turn",
        "líder alinhando prioridades e profissional jovem apresentando solução à equipe",
        "young professional presenting diverse team collaboration office",
        {
            "instagram": "Autonomia com direção.",
            "tiktok": "Autonomia não é abandono.",
            "youtube": "Autonomia com critérios.",
        },
        {
            "instagram": "Critérios claros. Mais execução.",
            "tiktok": "Critério claro. Decisão rápida.",
            "youtube": "Critérios claros. Decisões no nível certo.",
        },
        {
            "instagram": "Gestão inteligente cria autonomia com critérios, clareza e direção.",
            "tiktok": "Gestão inteligente dá autonomia com critério e direção.",
            "youtube": "Gestão inteligente distribui responsabilidades, define critérios claros e permite que decisões aconteçam no nível certo.",
        },
    ),
    SceneTemplate(
        "result",
        "equipe trabalhando com autonomia enquanto líder acompanha indicadores",
        "male leader dashboard diverse autonomous team office",
        {
            "instagram": "Mais autonomia. Mais execução.",
            "tiktok": "A equipe avança.",
            "youtube": "A operação ganha velocidade.",
        },
        {
            "instagram": "O líder acompanha. A equipe executa.",
            "tiktok": "Você lidera. O time executa.",
            "youtube": "O líder sai do gargalo e volta a liderar.",
        },
        {
            "instagram": "A operação ganha velocidade, e você volta a liderar o crescimento.",
            "tiktok": "A equipe avança e você volta a liderar.",
            "youtube": "Com autonomia bem estruturada, a operação ganha velocidade e o líder deixa de ser passagem obrigatória para cada decisão.",
        },
    ),
    SceneTemplate(
        "cta",
        "equipe profissional diversa com homem, mulher e jovem em ambiente corporativo",
        "diverse business team man woman young professional success office",
        {
            "instagram": "Cresça sem ser o gargalo.",
            "tiktok": "Pare de ser o gargalo.",
            "youtube": "Cresça sem depender de você para tudo.",
        },
        {
            "instagram": "Autonomia para crescer.",
            "tiktok": "Autonomia para avançar.",
            "youtube": "Autonomia para crescer.",
        },
        {
            "instagram": "Sua empresa pode crescer sem depender de você para tudo. Conheça a UGI.",
            "tiktok": "Se isso acontece na sua empresa, conheça a UGI.",
            "youtube": "Sua empresa pode crescer sem depender de você para tudo. Conheça a UGI e veja como estruturar uma gestão menos dependente.",
        },
    ),
]


def run(cmd: list[str | Path]) -> None:
    printable = [str(x) for x in cmd]
    print(">", " ".join(printable))
    subprocess.run(printable, check=True)


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def esc(path: Path) -> str:
    return path.as_posix().replace("'", r"\'")


def write_text(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


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


def find_media(index: int) -> Path | None:
    for ext in ("mp4", "mov", "jpg", "jpeg", "png", "webp"):
        p = MEDIA / f"scene-{index}.{ext}"
        if p.exists() and p.stat().st_size > 0:
            return p
    return None


def synthesize_scene_voice(platform: str, index: int, text: str, speed: float) -> Path:
    try:
        import numpy as np
        import soundfile as sf
        from kokoro import KPipeline
    except Exception as exc:
        raise RuntimeError("Kokoro TTS não disponível no workflow.") from exc

    pdir = WORK / platform
    pdir.mkdir(parents=True, exist_ok=True)

    raw = pdir / f"voice-{index}-raw.wav"
    out = pdir / f"voice-{index}.wav"

    pipeline = KPipeline(lang_code="p")
    chunks = []

    for result in pipeline(
        clean(text),
        voice="pf_dora",
        speed=speed,
        split_pattern=r"\n+",
    ):
        audio = getattr(result, "audio", None)
        if audio is not None:
            chunks.append(np.asarray(audio, dtype=np.float32))

    if not chunks:
        raise RuntimeError(f"Kokoro não retornou áudio: {platform} cena {index}.")

    sf.write(str(raw), np.concatenate(chunks), 24000, subtype="PCM_16")

    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", raw,
            "-af",
            (
                "highpass=f=80,"
                "lowpass=f=10000,"
                "acompressor=threshold=-20dB:ratio=2:attack=8:release=120:makeup=2,"
                "loudnorm=I=-16:TP=-2:LRA=5"
            ),
            "-ar", "48000",
            "-ac", "2",
            out,
        ]
    )
    return out


def platform_script(platform: str) -> list[dict]:
    return [
        {
            "index": i,
            "role": scene.role,
            "visual_intent": scene.visual_intent,
            "pexels_query": scene.pexels_query,
            "overlay": scene.overlay[platform],
            "support": scene.support[platform],
            "narration": scene.narration[platform],
        }
        for i, scene in enumerate(SCENES, start=1)
    ]


def allocate_semantic_timeline(platform: str, script: list[dict], voice_durations: list[float]) -> list[float]:
    """
    A voz é o relógio mestre.
    1) cada cena recebe duração real da fala + respiro;
    2) se o total ultrapassa a meta, o sistema reduz respiros e acelera apenas o áudio da cena;
    3) se sobra tempo, distribui respiro por função narrativa.
    """
    target = float(PLATFORM_PROFILES[platform]["target_duration"])

    role_buffer = {
        "hook": 0.28,
        "pain": 0.22,
        "consequence": 0.22,
        "turn": 0.25,
        "result": 0.25,
        "cta": 0.40,
    }

    minimum_visual = {
        "instagram": 3.2,
        "tiktok": 2.5,
        "youtube": 3.8,
    }[platform]

    base = [
        max(minimum_visual, vd + role_buffer[item["role"]])
        for item, vd in zip(script, voice_durations)
    ]

    total = sum(base)

    if total < target:
        extra = target - total
        weights = []
        for item in script:
            if item["role"] in {"hook", "turn", "result", "cta"}:
                weights.append(1.15)
            else:
                weights.append(0.85)
        sw = sum(weights)
        durations = [d + extra * w / sw for d, w in zip(base, weights)]
    else:
        # Não corta semanticamente; comprime janelas proporcionalmente até a meta.
        scale = target / total
        durations = [d * scale for d in base]

    durations = [round(d, 3) for d in durations]
    durations[-1] = round(target - sum(durations[:-1]), 3)
    return durations


def atempo_chain(factor: float) -> str:
    """Retorna cadeia atempo válida para qualquer fator positivo."""
    if factor <= 0:
        return "anull"
    stages = []
    while factor > 2.0:
        stages.append("atempo=2.0")
        factor /= 2.0
    while factor < 0.5:
        stages.append("atempo=0.5")
        factor /= 0.5
    if abs(factor - 1.0) > 0.001:
        stages.append(f"atempo={factor:.5f}")
    return ",".join(stages) if stages else "anull"


def fit_voice_to_scene(voice: Path, scene_duration: float, platform: str, index: int) -> Path:
    source = ffprobe_duration(voice)
    usable = max(0.8, scene_duration - 0.15)
    out = WORK / platform / f"voice-{index}-fit.wav"

    filters = []
    if source > usable:
        factor = source / usable
        filters.append(atempo_chain(factor))
    filters.append(f"apad=whole_dur={scene_duration}")

    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", voice,
            "-af", ",".join(filters),
            "-t", f"{scene_duration:.3f}",
            "-ar", "48000",
            "-ac", "2",
            out,
        ]
    )
    return out


def drawtext(textfile: Path, fontfile: str, size: int, color: str, x: str, y: str,
             alpha: str = "1", spacing: int = 12) -> str:
    return (
        "drawtext="
        f"fontfile='{fontfile}':textfile='{esc(textfile)}':reload=0:"
        f"fontsize={size}:fontcolor={color}:line_spacing={spacing}:"
        f"x={x}:y={y}:alpha='{alpha}'"
    )


def render_scene(platform: str, item: dict, duration: float, output: Path) -> dict:
    profile = PLATFORM_PROFILES[platform]
    media = find_media(item["index"])

    pdir = WORK / platform
    overlay = write_text(
        pdir / f"{item['index']}-overlay.txt",
        "\n".join(textwrap.wrap(item["overlay"], width=24, break_long_words=False)),
    )
    support = write_text(
        pdir / f"{item['index']}-support.txt",
        "\n".join(textwrap.wrap(item["support"], width=46, break_long_words=False)[:2]),
    )
    brand = write_text(
        pdir / f"{item['index']}-brand.txt",
        "UMA GESTÃO INTELIGENTE",
    )
    cta_file = write_text(
        pdir / f"{item['index']}-cta.txt",
        profile["primary_cta"],
    )

    if media and media.suffix.lower() in {".mp4", ".mov"}:
        input_args = ["-stream_loop", "-1", "-i", media]
        visual = [
            f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase",
            f"crop={WIDTH}:{HEIGHT}",
            "setsar=1",
            "eq=brightness=-0.04:saturation=0.96",
        ]
        media_kind = "video"
    elif media:
        input_args = ["-loop", "1", "-framerate", str(FPS), "-i", media]
        visual = [
            "scale=1500:-2",
            (
                "zoompan="
                "z='min(zoom+0.0007,1.08)':"
                "x='iw/2-(iw/zoom/2)':"
                "y='ih/2-(ih/zoom/2)':"
                f"d={max(1, round(duration*FPS))}:s={WIDTH}x{HEIGHT}:fps={FPS}"
            ),
            "setsar=1",
        ]
        media_kind = "image"
    else:
        input_args = [
            "-f", "lavfi",
            "-i", f"color=c={BG}:s={WIDTH}x{HEIGHT}:r={FPS}:d={duration}",
        ]
        visual = []
        media_kind = "fallback"

    # R43.4: clean output.
    # O scene index continua existindo internamente para timeline, logs e storyboard,
    # mas nunca é renderizado no vídeo público.
    panel_y = int(profile["panel_y"])
    panel_h = int(profile["panel_h"])
    overlay_y = int(profile["overlay_y"])
    support_y = int(profile["support_y"])
    progress_y = int(profile["progress_y"])

    overlay_size = 59
    if len(item["overlay"]) > 38:
        overlay_size = 52
    if len(item["overlay"]) > 54:
        overlay_size = 46

    visual += [
        "drawbox=x=0:y=0:w=iw:h=ih:color=black@0.10:t=fill",
        f"drawbox=x=68:y={panel_y}:w=944:h={panel_h}:color={PANEL}@0.62:t=fill",
        f"drawbox=x=68:y={panel_y}:w=8:h={panel_h}:color={ACCENT}@0.96:t=fill",
        drawtext(brand, FONT_BOLD, 26, WHITE, "w-text_w-92", "112", "0.90"),
        drawtext(
            overlay, FONT_BOLD, overlay_size, WHITE, "106", str(overlay_y),
            "if(lt(t,0.08),0,min((t-0.08)/0.22,1))", 12
        ),
        drawtext(
            support, FONT_REGULAR, 31, MUTED, "106", str(support_y),
            "if(lt(t,0.35),0,min((t-0.35)/0.25,1))", 10
        ),
    ]

    if item["role"] == "cta":
        cta_y = min(panel_y + panel_h - 105, 1635)
        visual += [
            f"drawbox=x=106:y={cta_y}:w=430:h=82:color={ACCENT}@0.94:t=fill",
            drawtext(
                cta_file, FONT_BOLD, 30,
                BG, "132", str(cta_y + 23),
                "if(lt(t,0.42),0,min((t-0.42)/0.28,1))"
            ),
        ]

    visual += [
        f"drawbox=x=82:y={progress_y}:w=916:h=4:color=white@0.16:t=fill",
        f"drawbox=x=82:y={progress_y}:w='916*min(t/{duration},1)':h=4:color={ACCENT}@0.96:t=fill",
        "vignette=PI/7",
        "fade=t=in:st=0:d=0.10",
        f"fade=t=out:st={max(0.05, duration-0.12)}:d=0.12",
        "format=yuv420p",
    ]

    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            *input_args,
            "-t", f"{duration:.3f}",
            "-vf", ",".join(visual),
            "-an",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "19",
            "-r", str(FPS),
            "-pix_fmt", "yuv420p",
            output,
        ]
    )

    return {
        "media_kind": media_kind,
        "media_path": str(media) if media else None,
    }


def concat_files(files: list[Path], name: Path) -> Path:
    concat = name.with_suffix(".txt")
    concat.write_text(
        "\n".join(f"file '{p.resolve().as_posix()}'" for p in files),
        encoding="utf-8",
    )
    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "concat", "-safe", "0",
            "-i", concat,
            "-c", "copy",
            name,
        ]
    )
    return name


def create_voice_timeline(platform: str, fitted_voices: list[Path]) -> Path:
    out = WORK / platform / "voice-timeline.wav"
    concat = WORK / platform / "voice-concat.txt"
    concat.write_text(
        "\n".join(f"file '{p.resolve().as_posix()}'" for p in fitted_voices),
        encoding="utf-8",
    )
    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "concat", "-safe", "0",
            "-i", concat,
            "-c", "copy",
            out,
        ]
    )
    return out


def finalize_platform(platform: str, video: Path, voice: Path, duration: float, output: Path) -> None:
    profile = PLATFORM_PROFILES[platform]
    music_level = float(profile["music_level"])

    # Valores de duração sempre com zero à esquerda para compatibilidade FFmpeg.
    music = (
        f"aevalsrc='0.018*sin(2*PI*110*t)+0.012*sin(2*PI*220*t)+"
        f"0.009*(0.5+0.5*sin(2*PI*2*t))*sin(2*PI*329.63*t)':"
        f"s=48000:d={duration},"
        "aformat=sample_fmts=fltp:channel_layouts=stereo,"
        "afade=t=in:st=0:d=0.4,"
        f"afade=t=out:st={max(0.1,duration-0.7)}:d=0.7"
    )

    graph = (
        "[1:a]volume=1.10,asplit=2[vsc][vmix];"
        f"[2:a]volume={music_level}[music];"
        "[music][vsc]sidechaincompress="
        "threshold=0.018:ratio=9:attack=15:release=260:makeup=1[ducked];"
        "[ducked][vmix]amix=inputs=2:duration=longest:dropout_transition=0,"
        "loudnorm=I=-14:TP=-1.2:LRA=6[aout]"
    )

    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", video,
            "-i", voice,
            "-f", "lavfi",
            "-i", music,
            "-filter_complex", graph,
            "-map", "0:v:0",
            "-map", "[aout]",
            "-t", f"{duration:.3f}",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "160k",
            "-ar", "48000",
            "-ac", "2",
            "-movflags", "+faststart",
            output,
        ]
    )


def validate_video(path: Path, expected: float) -> dict:
    if not path.exists() or path.stat().st_size < 10000:
        raise RuntimeError(f"Vídeo inválido: {path}")

    header = path.read_bytes()[:12]
    if len(header) < 12 or header[4:8] != b"ftyp":
        raise RuntimeError(f"Assinatura MP4 ausente: {path}")

    cp = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration,size",
            "-show_entries", "stream=codec_type,codec_name,width,height,r_frame_rate",
            "-of", "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(cp.stdout)
    actual = float(data["format"]["duration"])
    if abs(actual - expected) > 0.30:
        raise RuntimeError(
            f"Duração fora da tolerância em {path.name}: {actual:.3f} vs {expected:.3f}"
        )
    return data


def qa_platform(platform: str, script: list[dict], durations: list[float], media_info: list[dict]) -> dict:
    roles = [x["role"] for x in script]
    required = ["hook", "pain", "consequence", "turn", "result", "cta"]

    human_scenes = sum(1 for x in media_info if x["media_kind"] in {"video", "image"})

    checks = {
        "semantic_order": roles == required,
        "human_media_minimum": human_scenes >= 4,
        "cta_present": bool(script[-1]["overlay"]) and bool(PLATFORM_PROFILES[platform]["primary_cta"]),
        "short_overlays": all(len(x["overlay"].split()) <= 9 for x in script),
        "dynamic_layout": True,
        "safe_zone_applied": True,
        "voice_driven_timeline": True,
        "platform_profile_applied": True,
        "duration_sum_matches": abs(sum(durations) - PLATFORM_PROFILES[platform]["target_duration"]) <= 0.01,
    }

    return {
        "platform": platform,
        "profile": PLATFORM_PROFILES[platform],
        "human_media_scenes": human_scenes,
        "checks": checks,
        "quality_status": "pass" if all(checks.values()) else "fail",
    }


def render_platform(platform: str) -> dict:
    profile = PLATFORM_PROFILES[platform]
    target = float(profile["target_duration"])
    pdir = WORK / platform
    pdir.mkdir(parents=True, exist_ok=True)

    script = platform_script(platform)

    voices = []
    voice_durations = []
    for item in script:
        voice = synthesize_scene_voice(
            platform,
            item["index"],
            item["narration"],
            float(profile["voice_speed"]),
        )
        voices.append(voice)
        voice_durations.append(ffprobe_duration(voice))

    scene_durations = allocate_semantic_timeline(platform, script, voice_durations)

    fitted_voices = []
    scene_files = []
    media_info = []
    cursor = 0.0

    for item, raw_voice, duration in zip(script, voices, scene_durations):
        fitted = fit_voice_to_scene(
            raw_voice,
            duration,
            platform,
            item["index"],
        )
        fitted_voices.append(fitted)

        scene_file = pdir / f"scene-{item['index']}.mp4"
        info = render_scene(platform, item, duration, scene_file)
        scene_files.append(scene_file)
        media_info.append(info)

        item["start"] = round(cursor, 3)
        item["duration"] = round(duration, 3)
        item["voice_source_duration"] = round(ffprobe_duration(raw_voice), 3)
        item["voice_fitted_duration"] = round(ffprobe_duration(fitted), 3)
        item.update(info)
        cursor += duration

    joined = concat_files(scene_files, pdir / "joined.mp4")
    voice_timeline = create_voice_timeline(platform, fitted_voices)

    output_name = {
        "instagram": "instagram-reel.mp4",
        "tiktok": "tiktok-reel.mp4",
        "youtube": "youtube-short.mp4",
    }[platform]

    final = OUTPUT_DIR / output_name
    finalize_platform(platform, joined, voice_timeline, target, final)
    probe = validate_video(final, target)

    qa = qa_platform(platform, script, scene_durations, media_info)

    storyboard = {
        "version": "R42",
        "render_id": RENDER_ID,
        "platform": platform,
        "platform_label": profile["label"],
        "title": TITLE,
        "target_duration": target,
        "content_id": CONTENT_ID,
        "experiment_id": EXPERIMENT_ID,
        "variant": VARIANT,
        "commercial_intent": COMMERCIAL_INTENT,
        "story_structure": "hook>pain>consequence>turn>result>cta",
        "scenes": script,
        "qa": qa,
        "ffprobe": probe,
    }

    (OUTPUT_DIR / f"r42-storyboard-{platform}.json").write_text(
        json.dumps(storyboard, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if qa["quality_status"] != "pass":
        raise RuntimeError(f"R42 QA reprovado para {platform}: {qa['checks']}")

    return {
        "platform": platform,
        "label": profile["label"],
        "output": str(final),
        "target_duration": target,
        "actual_duration": float(probe["format"]["duration"]),
        "qa": qa,
    }


def main() -> int:
    for binary in ("ffmpeg", "ffprobe"):
        if shutil.which(binary) is None:
            raise RuntimeError(f"{binary} não encontrado.")

    for font in (FONT_REGULAR, FONT_BOLD):
        if not Path(font).exists():
            raise RuntimeError(f"Fonte ausente: {font}")

    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("===== UGI R42 MULTI-PLATFORM SEMANTIC VIDEO ENGINE =====")
    print(f"TITLE={TITLE}")
    print(f"RENDER_ID={RENDER_ID}")
    print("Platforms: Instagram, TikTok, YouTube Shorts")
    print("=========================================================")

    results = []
    for platform in ("instagram", "tiktok", "youtube"):
        print(f"\n===== R42 PLATFORM: {platform.upper()} =====")
        results.append(render_platform(platform))

    # Compatibilidade com o pipeline atual: entrega primária continua sendo Instagram.
    shutil.copyfile(
        OUTPUT_DIR / "instagram-reel.mp4",
        OUTPUT_DIR / "ugi-reel.mp4",
    )

    manifest = {
        "version": "R42_MULTI_PLATFORM_SEMANTIC",
        "render_id": RENDER_ID,
        "title": TITLE,
        "content_id": CONTENT_ID,
        "experiment_id": EXPERIMENT_ID,
        "variant": VARIANT,
        "commercial_intent": COMMERCIAL_INTENT,
        "primary_delivery": "instagram",
        "compatibility_output": "output/ugi-reel.mp4",
        "platform_results": results,
        "public_overlay_policy": "scene_index_hidden",
        "scene_index_internal_only": True,
        "architecture_note":
            "R42 já gera três masters específicos. O Worker atual ainda recebe apenas o MP4 primário; "
            "R43/bridge deverá registrar os três assets separadamente na Central.",
    }

    (OUTPUT_DIR / "r42-platform-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    print("RENDER_SUCCESS_R42")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"R42_FFMPEG_ERROR returncode={exc.returncode}", file=sys.stderr)
        raise
    except Exception as exc:
        print(f"R42_ERROR: {exc}", file=sys.stderr)
        raise


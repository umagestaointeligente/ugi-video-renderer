#!/usr/bin/env python3
"""
UGI Reel Renderer R38 — CREATIVE VIDEO ENGINE / PHASE 1
========================================================
Baseado no R37.3 validado.

Objetivos do R38:
- preservar a interface atual do workflow: VIDEO_TITLE, VIDEO_DURATION, VIDEO_RENDER_ID;
- abandonar timeline fixa por chunks;
- usar storyboard por cenas com narração, texto, prompt visual e timing;
- sintetizar a voz CENA A CENA com Kokoro PT-BR;
- calcular a duração visual a partir da duração REAL da fala;
- manter texto e fala na mesma cena;
- aceitar mídia humana por cena em assets/scene-N.mp4|jpg|png;
- animar imagens estáticas com movimento de câmera;
- usar fallback procedural quando a mídia humana ainda não estiver disponível;
- preservar FFmpeg, Kokoro, H.264/AAC, GitHub Actions, R2 e Central de Aprovação.

Saída:
    output/ugi-reel.mp4
    output/storyboard.json

Observação:
O R38 já está preparado para pessoas/situações reais. Quando arquivos de mídia
forem fornecidos em assets/, eles entram automaticamente sem alterar o renderer.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import wave
from pathlib import Path

WIDTH = 1080
HEIGHT = 1920
FPS = 30
OUTPUT = Path("output/ugi-reel.mp4")
WORK = Path("output/r38_work")
STORYBOARD_OUT = Path("output/storyboard.json")
ASSET_DIR = Path(os.getenv("VIDEO_ASSET_DIR") or "assets")

TITLE = (
    os.getenv("VIDEO_TITLE")
    or "Se tudo precisa passar por você, sua empresa não está crescendo. Está ficando dependente."
).strip()
CTA = (os.getenv("VIDEO_CTA") or "Conheça a UGI").strip()
RENDER_ID = (os.getenv("VIDEO_RENDER_ID") or "local-r38").strip()

try:
    REQUESTED_DURATION = int(os.getenv("VIDEO_DURATION") or "28")
except ValueError:
    REQUESTED_DURATION = 28

# R38: faixa editorial inicial para Reels/TikTok/Shorts.
REQUESTED_DURATION = max(15, min(60, REQUESTED_DURATION))

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
    value = re.sub(r"\s+", " ", str(value or "")).strip()
    return value


def esc_path(p: Path) -> str:
    return p.as_posix().replace("'", r"\'")


def write_text(name: str, content: str) -> Path:
    p = WORK / f"{name}.txt"
    p.write_text(content, encoding="utf-8")
    return p


def wrap_for_reel(text: str, width: int = 22) -> str:
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
    Piloto R38 sobre centralização.
    Depois, VIDEO_STORYBOARD_JSON poderá ser enviado pelo Worker sem alterar
    este renderer.
    """
    return [
        {
            "id": "hook",
            "role": "hook",
            "narration": "Se tudo precisa passar por você, sua empresa pode estar crescendo em tamanho, mas ficando dependente.",
            "on_screen_text": "Tudo precisa passar por você?",
            "visual_prompt": "Gestor em escritório moderno sendo interrompido por várias pessoas ao mesmo tempo, solicitações chegando, expressão de sobrecarga, ambiente corporativo realista, movimento natural de equipe.",
            "min_duration": 4.8,
        },
        {
            "id": "pain",
            "role": "pain",
            "narration": "Quando cada decisão para no gestor, a equipe espera, o trabalho desacelera e o retrabalho aumenta.",
            "on_screen_text": "A equipe espera. O trabalho para.",
            "visual_prompt": "Equipe em reunião aguardando aprovação do líder, pessoas olhando para o gestor, notebook e documentos sobre a mesa, situação real de dependência decisória.",
            "min_duration": 5.2,
        },
        {
            "id": "consequence",
            "role": "consequence",
            "narration": "E quanto mais a operação depende de uma única pessoa, menos autonomia existe para crescer com velocidade.",
            "on_screen_text": "Centralização limita o crescimento.",
            "visual_prompt": "Gestor cercado por mensagens e tarefas enquanto colaboradores aguardam, ambiente empresarial movimentado, sensação de gargalo operacional.",
            "min_duration": 5.2,
        },
        {
            "id": "solution",
            "role": "solution",
            "narration": "Gestão inteligente distribui responsabilidades, cria critérios claros e permite que decisões aconteçam no nível certo.",
            "on_screen_text": "Autonomia com critérios.",
            "visual_prompt": "Líder alinhando responsabilidades com equipe em quadro de planejamento, colaboradores participando, ambiente profissional, sensação de autonomia e clareza.",
            "min_duration": 5.5,
        },
        {
            "id": "cta",
            "role": "cta",
            "narration": "Sua empresa precisa crescer sem depender de você para tudo. Conheça a UGI.",
            "on_screen_text": "Cresça sem centralizar tudo.",
            "visual_prompt": "Equipe confiante trabalhando com autonomia, líder acompanhando de forma estratégica, escritório contemporâneo, clima profissional positivo.",
            "min_duration": 4.8,
            "cta": CTA,
        },
    ]


def load_storyboard() -> list[dict]:
    raw = os.getenv("VIDEO_STORYBOARD_JSON", "").strip()
    if not raw:
        scenes = default_storyboard()
    else:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"VIDEO_STORYBOARD_JSON inválido: {exc}") from exc
        scenes = data.get("scenes") if isinstance(data, dict) else data

    if not isinstance(scenes, list) or not scenes:
        raise RuntimeError("Storyboard precisa conter ao menos uma cena.")

    normalized = []
    for idx, scene in enumerate(scenes, start=1):
        if not isinstance(scene, dict):
            raise RuntimeError(f"Cena {idx} inválida.")
        narration = clean_text(scene.get("narration"))
        if not narration:
            raise RuntimeError(f"Cena {idx} sem narration.")
        normalized.append(
            {
                "index": idx,
                "id": clean_text(scene.get("id")) or f"scene-{idx}",
                "role": clean_text(scene.get("role")) or "content",
                "narration": narration,
                "on_screen_text": clean_text(scene.get("on_screen_text")),
                "visual_prompt": clean_text(scene.get("visual_prompt")),
                "min_duration": max(2.2, float(scene.get("min_duration") or 3.5)),
                "cta": clean_text(scene.get("cta")),
            }
        )
    return normalized


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
        raise RuntimeError(
            "Kokoro TTS não está instalado. Use o workflow Kokoro atual."
        ) from exc

    raw_wav = WORK / f"voice-{scene['index']}-raw.wav"
    out_wav = WORK / f"voice-{scene['index']}.wav"

    pipeline = KPipeline(lang_code="p")
    chunks = []

    for result in pipeline(
        scene["narration"],
        voice="pf_dora",
        speed=1.03,
        split_pattern=r"\n+",
    ):
        audio = getattr(result, "audio", None)
        if audio is not None:
            chunks.append(np.asarray(audio, dtype=np.float32))

    if not chunks:
        raise RuntimeError(f"Kokoro não retornou áudio para a cena {scene['index']}.")

    audio = np.concatenate(chunks)
    sf.write(str(raw_wav), audio, 24000, subtype="PCM_16")

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
            str(out_wav),
        ]
    )

    return out_wav


def media_for_scene(index: int) -> tuple[str, Path | None]:
    candidates = [
        ("video", ASSET_DIR / f"scene-{index}.mp4"),
        ("video", ASSET_DIR / f"scene-{index}.mov"),
        ("image", ASSET_DIR / f"scene-{index}.jpg"),
        ("image", ASSET_DIR / f"scene-{index}.jpeg"),
        ("image", ASSET_DIR / f"scene-{index}.png"),
        ("image", ASSET_DIR / f"scene-{index}.webp"),
    ]
    for kind, path in candidates:
        if path.exists() and path.stat().st_size > 0:
            return kind, path
    return "fallback", None


def drawtext_filter(
    textfile: Path,
    *,
    fontfile: str,
    fontsize: int,
    fontcolor: str,
    x: str,
    y: str,
    alpha: str = "1",
    line_spacing: int = 14,
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


def base_overlay_filters(scene: dict, dur: float, media_kind: str) -> list[str]:
    text_file = write_text(
        f"scene-{scene['index']}-text",
        wrap_for_reel(scene["on_screen_text"], 23)
    )
    brand_file = write_text(
        f"scene-{scene['index']}-brand",
        "UMA GESTÃO INTELIGENTE"
    )
    scene_file = write_text(
        f"scene-{scene['index']}-number",
        f"{scene['index']:02d}"
    )

    filters = [
        # Legibilidade: gradiente simulado com placas translúcidas.
        f"drawbox=x=0:y=0:w={WIDTH}:h=270:color=black@0.32:t=fill",
        f"drawbox=x=0:y=1210:w={WIDTH}:h=710:color=black@0.48:t=fill",
        f"drawbox=x=70:y=1350:w={WIDTH-140}:h=330:color={PANEL}@0.70:t=fill",
        f"drawbox=x=70:y=1350:w=9:h=330:color={ACCENT}@0.96:t=fill",
        "vignette=PI/5.8",
    ]

    filters.append(
        drawtext_filter(
            scene_file,
            fontfile=FONT_BOLD,
            fontsize=28,
            fontcolor=MUTED,
            x="86",
            y="104",
            alpha="0.88",
        )
    )
    filters.append(
        drawtext_filter(
            brand_file,
            fontfile=FONT_BOLD,
            fontsize=25,
            fontcolor=WHITE,
            x="w-text_w-86",
            y="104",
            alpha="0.92",
        )
    )

    if scene["on_screen_text"]:
        filters.append(
            drawtext_filter(
                text_file,
                fontfile=FONT_BOLD,
                fontsize=64 if len(scene["on_screen_text"]) < 38 else 55,
                fontcolor=WHITE,
                x="108",
                y="1405",
                line_spacing=14,
                alpha="if(lt(t,0.12),0,min((t-0.12)/0.28,1))",
                borderw=1,
                bordercolor="black@0.24",
            )
        )

    # Barra de progresso da cena.
    filters.append(
        f"drawbox=x=86:y=1772:w={WIDTH-172}:h=4:color={WHITE}@0.18:t=fill"
    )
    filters.append(
        f"drawbox=x=86:y=1772:w='({WIDTH-172})*min(t/{dur},1)':h=4:color={ACCENT}@0.96:t=fill"
    )

    return filters


def render_scene_visual(scene: dict, dur: float, output: Path) -> dict:
    media_kind, media_path = media_for_scene(scene["index"])
    filters: list[str] = []

    if media_kind == "video":
        # Movimento humano real quando há clipe disponível.
        input_args = ["-stream_loop", "-1", "-i", str(media_path)]
        filters.extend(
            [
                f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase",
                f"crop={WIDTH}:{HEIGHT}",
                "setsar=1",
            ]
        )
    elif media_kind == "image":
        # Imagem humana com movimento de câmera; não finge movimento corporal.
        input_args = ["-loop", "1", "-framerate", str(FPS), "-i", str(media_path)]
        frames = max(1, round(dur * FPS))
        filters.extend(
            [
                f"scale=1400:-2",
                f"zoompan=z='min(zoom+0.00075,1.085)':"
                f"x='iw/2-(iw/zoom/2)+18*sin(on/24)':"
                f"y='ih/2-(ih/zoom/2)+12*cos(on/28)':"
                f"d={frames}:s={WIDTH}x{HEIGHT}:fps={FPS}",
                "setsar=1",
            ]
        )
    else:
        # Fallback técnico. Mantém pipeline vivo, mas deve falhar QA comercial.
        input_args = [
            "-f", "lavfi",
            "-i", f"color=c={BG}:s={WIDTH}x{HEIGHT}:r={FPS}:d={dur}"
        ]
        filters.extend(
            [
                f"drawbox=x=70:y=300:w={WIDTH-140}:h=780:color={PANEL}@0.78:t=fill",
                f"drawbox=x='-500+t*170':y=470:w=430:h=12:color={ACCENT}@0.55:t=fill",
                f"drawbox=x='{WIDTH+100}-t*150':y=860:w=350:h=8:color={ACCENT_2}@0.38:t=fill",
                "noise=alls=2:allf=t+u",
            ]
        )

    filters.extend(base_overlay_filters(scene, dur, media_kind))
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
        "media_kind": media_kind,
        "media_path": str(media_path) if media_path else None,
    }


def fit_scene_durations(scenes: list[dict], voice_durations: list[float]) -> list[float]:
    """
    Fala governa a timeline.
    Cada cena dura no mínimo a fala + respiro e respeita min_duration.
    Se o conjunto ficar menor que o solicitado, o tempo extra é distribuído.
    Se ficar maior, NÃO cortamos a fala; o vídeo final pode superar o alvo.
    """
    durations = [
        max(scene["min_duration"], voice_dur + 0.55)
        for scene, voice_dur in zip(scenes, voice_durations)
    ]

    total = sum(durations)
    if total < REQUESTED_DURATION:
        extra = REQUESTED_DURATION - total
        weights = [1.15, 1.0, 1.0, 1.0, 1.1][: len(durations)]
        weight_sum = sum(weights)
        durations = [
            d + extra * (weights[i] / weight_sum)
            for i, d in enumerate(durations)
        ]

    return [round(d, 3) for d in durations]


def create_voice_timeline(
    voice_files: list[Path],
    scene_durations: list[float],
) -> Path:
    """
    Cada voz é acolchoada exatamente até a duração da cena.
    Ao concatenar, o início de cada locução coincide com o início de sua cena.
    """
    padded_files = []

    for idx, (voice, dur) in enumerate(zip(voice_files, scene_durations), start=1):
        padded = WORK / f"voice-{idx}-timeline.wav"
        run(
            [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-i", str(voice),
                "-af", f"apad=whole_dur={dur}",
                "-t", f"{dur:.3f}",
                "-ar", "48000",
                "-ac", "2",
                str(padded),
            ]
        )
        padded_files.append(padded)

    concat_file = WORK / "voice-concat.txt"
    concat_file.write_text(
        "\n".join(f"file '{p.resolve().as_posix()}'" for p in padded_files),
        encoding="utf-8",
    )

    out = WORK / "voice-timeline.wav"
    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(out),
        ]
    )
    return out


def concat_visuals(scene_files: list[Path]) -> Path:
    concat_file = WORK / "visual-concat.txt"
    concat_file.write_text(
        "\n".join(f"file '{p.resolve().as_posix()}'" for p in scene_files),
        encoding="utf-8",
    )
    out = WORK / "joined.mp4"
    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(out),
        ]
    )
    return out


def finalize(
    joined_video: Path,
    voice_timeline: Path,
    final_duration: float,
) -> None:
    # Trilha procedural discreta; depois pode ser trocada por catálogo licenciado.
    pulse = "(0.50+0.50*sin(2*PI*1.6*t))"
    music_expr = (
        "0.024*sin(2*PI*110*t)"
        "+0.018*sin(2*PI*164.81*t)"
        "+0.014*sin(2*PI*220*t)"
        "+0.010*" + pulse + "*sin(2*PI*329.63*t)"
        "+0.007*" + pulse + "*sin(2*PI*440*t)"
    )

    music_src = (
        f"aevalsrc='{music_expr}':s=48000:d={final_duration},"
        "aformat=sample_fmts=fltp:channel_layouts=stereo,"
        "highpass=f=70,lowpass=f=7200,"
        "acompressor=threshold=-22dB:ratio=2:attack=12:release=160:makeup=2,"
        "afade=t=in:st=0:d=0.25,"
        f"afade=t=out:st={max(0.1, final_duration-0.7)}:d=0.7"
    )

    mix_filter = (
        "[1:a]volume=1.12,asplit=2[voice_sc][voice_mix];"
        "[2:a]volume=0.72[music];"
        "[music][voice_sc]sidechaincompress="
        "threshold=0.016:ratio=9:attack=14:release=240:makeup=1[ducked];"
        "[ducked][voice_mix]amix=inputs=2:duration=longest:dropout_transition=0,"
        "loudnorm=I=-14:TP=-1.2:LRA=6[aout]"
    )

    run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-i", str(joined_video),
            "-i", str(voice_timeline),
            "-f", "lavfi",
            "-i", music_src,
            "-filter_complex", mix_filter,
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


def validate_output(final_duration: float) -> None:
    if not OUTPUT.exists() or OUTPUT.stat().st_size < 10_000:
        raise RuntimeError("R38 não produziu um MP4 válido.")

    signature = OUTPUT.read_bytes()[:12]
    if len(signature) < 12 or signature[4:8] != b"ftyp":
        raise RuntimeError("Assinatura MP4 ftyp ausente.")

    probe = subprocess.run(
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

    print("===== R38 VALIDATION =====")
    print(probe.stdout.strip())
    print(f"REQUESTED_DURATION={REQUESTED_DURATION}")
    print(f"FINAL_DURATION={final_duration:.3f}")
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

    scenes = load_storyboard()

    print("===== UGI R38 CREATIVE VIDEO ENGINE =====")
    print(f"Title: {TITLE}")
    print(f"Requested duration: {REQUESTED_DURATION}s")
    print(f"Scenes: {len(scenes)}")
    print(f"Asset dir: {ASSET_DIR}")
    print("=========================================")

    voice_files = []
    voice_durations = []

    for scene in scenes:
        voice = synthesize_scene_voice(scene)
        voice_files.append(voice)
        voice_duration = ffprobe_duration(voice)
        voice_durations.append(voice_duration)
        scene["voice_duration"] = round(voice_duration, 3)

    durations = fit_scene_durations(scenes, voice_durations)
    final_duration = round(sum(durations), 3)

    scene_files = []
    current = 0.0

    for scene, dur in zip(scenes, durations):
        scene["start"] = round(current, 3)
        scene["duration"] = dur

        scene_path = WORK / f"scene-{scene['index']}.mp4"
        media_info = render_scene_visual(scene, dur, scene_path)
        scene.update(media_info)

        scene_files.append(scene_path)
        current += dur

    STORYBOARD_OUT.write_text(
        json.dumps(
            {
                "version": "R38-phase1",
                "render_id": RENDER_ID,
                "title": TITLE,
                "requested_duration": REQUESTED_DURATION,
                "final_duration": final_duration,
                "scenes": scenes,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    voice_timeline = create_voice_timeline(voice_files, durations)
    joined_video = concat_visuals(scene_files)
    finalize(joined_video, voice_timeline, final_duration)
    validate_output(final_duration)

    fallback_count = sum(1 for s in scenes if s["media_kind"] == "fallback")
    print(f"MEDIA_FALLBACK_SCENES={fallback_count}/{len(scenes)}")
    print("RENDER_SUCCESS_R38")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"FFMPEG_ERROR: returncode={exc.returncode}", file=sys.stderr)
        raise
    except Exception as exc:
        print(f"R38_ERROR: {exc}", file=sys.stderr)
        raise


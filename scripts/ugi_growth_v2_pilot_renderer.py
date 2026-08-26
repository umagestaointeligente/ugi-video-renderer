#!/usr/bin/env python3
from __future__ import annotations

import json, math, os, subprocess, textwrap, time
from pathlib import Path

import numpy as np
import requests
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont
from kokoro import KPipeline

W, H, FPS = 1080, 1920, 30
ROOT = Path.cwd()
OUT = ROOT / "output" / "growth-v2-pilot"
MEDIA = OUT / "media"
WORK = OUT / "work"
OUT.mkdir(parents=True, exist_ok=True)
MEDIA.mkdir(parents=True, exist_ok=True)
WORK.mkdir(parents=True, exist_ok=True)

PILOT_FILE = Path(os.getenv("UGI_GROWTH_PILOT_FILE", "experiments/ugi-growth-v2/pilot-002.json"))
PILOT = json.loads(PILOT_FILE.read_text(encoding="utf-8"))
SCENES = PILOT["scenes"]
VOICE_SPEED = float(PILOT.get("voice_speed", 1.0))
PEXELS_API_KEY = (os.getenv("PEXELS_API_KEY") or "").strip()
PIXABAY_API_KEY = (os.getenv("PIXABAY_API_KEY") or "").strip()

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
LOGO_PATH = ROOT / "assets" / "branding" / "ugi-symbol-transparent.png"

WHITE = (246, 248, 250, 255)
MUTED = (218, 225, 231, 255)
TEAL = (53, 208, 186, 255)
YELLOW = (255, 206, 71, 255)
RED = (255, 96, 96, 255)
INK = (7, 16, 25, 235)


def run(cmd):
    print(">", " ".join(map(str, cmd)), flush=True)
    subprocess.run([str(x) for x in cmd], check=True)


def ffprobe_duration(path: Path) -> float:
    cp = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path)
    ], check=True, capture_output=True, text=True)
    return float(cp.stdout.strip())


def http_get(url, **kwargs):
    last = None
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=(10, 90), **kwargs)
            r.raise_for_status()
            return r
        except Exception as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise last


def download_scene(idx: int, query: str) -> Path:
    if PEXELS_API_KEY:
        data = http_get(
            "https://api.pexels.com/v1/videos/search",
            headers={"Authorization": PEXELS_API_KEY},
            params={"query": query, "orientation": "portrait", "per_page": 20},
        ).json()
        for video in data.get("videos", []):
            files = [f for f in video.get("video_files", []) if f.get("file_type") == "video/mp4" and f.get("link")]
            if not files:
                continue
            files.sort(key=lambda f: (int(f.get("height") or 0) > int(f.get("width") or 0), int(f.get("height") or 0)), reverse=True)
            target = MEDIA / f"scene-{idx}.mp4"
            r = http_get(files[0]["link"], stream=True)
            with target.open("wb") as fh:
                for chunk in r.iter_content(1024 * 1024):
                    if chunk:
                        fh.write(chunk)
            if target.stat().st_size > 100000:
                return target

    if PIXABAY_API_KEY:
        data = http_get(
            "https://pixabay.com/api/videos/",
            params={"key": PIXABAY_API_KEY, "q": query, "video_type": "film", "safesearch": "true", "per_page": 20},
        ).json()
        for video in data.get("hits", []):
            variants = video.get("videos") or {}
            item = variants.get("large") or variants.get("medium") or variants.get("small") or {}
            if item.get("url"):
                target = MEDIA / f"scene-{idx}.mp4"
                r = http_get(item["url"], stream=True)
                with target.open("wb") as fh:
                    for chunk in r.iter_content(1024 * 1024):
                        if chunk:
                            fh.write(chunk)
                if target.stat().st_size > 100000:
                    return target

    raise RuntimeError(f"No usable media for scene {idx}: {query}")


def font(size: int, bold: bool = True):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def wrapped_lines(draw, text, ft, max_width):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        test = word if not cur else cur + " " + word
        if draw.textbbox((0, 0), test, font=ft)[2] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, text, xy, ft, fill, max_width, line_gap=10, anchor="la"):
    x, y = xy
    lines = wrapped_lines(draw, text, ft, max_width)
    for line in lines:
        draw.text((x, y), line, font=ft, fill=fill, anchor=anchor)
        box = draw.textbbox((x, y), line, font=ft, anchor=anchor)
        y += (box[3] - box[1]) + line_gap
    return y


def rounded_box(draw, xy, fill, radius=28, outline=None, width=2):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def add_logo(canvas: Image.Image):
    if not LOGO_PATH.exists():
        return
    logo = Image.open(LOGO_PATH).convert("RGBA")
    ratio = 64 / logo.height
    logo = logo.resize((int(logo.width * ratio), 64))
    canvas.alpha_composite(logo, (W - logo.width - 48, 42))


def make_overlay(idx: int, scene: dict) -> Path:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    layout = scene["layout"]
    headline = scene["headline"]
    support = scene.get("support", "")
    add_logo(img)

    if layout == "hook":
        d.rectangle((0, 0, W, 820), fill=(0, 0, 0, 110))
        d.text((72, 150), "VOCÊ DEIXARIA ISSO PASSAR?", font=font(38), fill=YELLOW)
        draw_wrapped(d, headline, (72, 240), font(72), WHITE, 900, 14)
        rounded_box(d, (72, 1020, 760, 1170), fill=(255,255,255,242), radius=24)
        d.text((110, 1060), "📄  " + support, font=font(40), fill=(20,30,40,255))
        d.text((72, 1255), "UM CLIQUE. UM DADO SENSÍVEL. UMA DECISÃO.", font=font(31, False), fill=MUTED)

    elif layout == "question":
        rounded_box(d, (64, 260, 1016, 800), fill=(5, 12, 20, 178), radius=36)
        d.text((540, 325), "O QUE VOCÊ FARIA?", font=font(40), fill=YELLOW, anchor="ma")
        draw_wrapped(d, headline, (540, 425), font(64), WHITE, 850, 16, anchor="ma")
        rounded_box(d, (150, 1320, 930, 1450), fill=(53,208,186,220), radius=28)
        d.text((540, 1385), support, font=font(31), fill=(7,16,25,255), anchor="mm")

    elif layout == "twist":
        d.rectangle((0, 0, W, H), fill=(0, 0, 0, 48))
        d.text((72, 220), "A VIRADA", font=font(36), fill=TEAL)
        draw_wrapped(d, headline, (72, 310), font(68), WHITE, 900, 14)
        rounded_box(d, (72, 1110, 1008, 1325), fill=(255,255,255,230), radius=30)
        draw_wrapped(d, support.upper(), (112, 1162), font(48), (14,24,32,255), 850, 12)

    elif layout == "rules":
        d.text((72, 160), headline, font=font(44), fill=TEAL)
        rounded_box(d, (72, 320, 1008, 720), fill=(5,12,20,185), radius=32)
        d.text((118, 370), "01", font=font(88), fill=YELLOW)
        draw_wrapped(d, "DADOS SENSÍVEIS NÃO ENTRAM.", (250, 390), font(48), WHITE, 700, 10)
        rounded_box(d, (72, 790, 1008, 1190), fill=(5,12,20,185), radius=32)
        d.text((118, 840), "02", font=font(88), fill=TEAL)
        draw_wrapped(d, "DECISÃO CRÍTICA EXIGE REVISÃO HUMANA.", (250, 860), font(46), WHITE, 700, 10)
        d.text((72, 1320), "Regra simples. Risco menor.", font=font(36, False), fill=MUTED)

    elif layout == "rule3":
        d.text((88, 220), "03", font=font(220), fill=(53,208,186,225))
        draw_wrapped(d, support.upper(), (88, 560), font(68), WHITE, 880, 16)
        rounded_box(d, (88, 1170, 992, 1325), fill=(5,12,20,185), radius=28)
        d.text((540, 1247), "SEM DONO, NINGUÉM RESPONDE PELO RESULTADO.", font=font(31), fill=MUTED, anchor="mm")

    elif layout == "cta":
        d.rectangle((0, 0, W, H), fill=(0, 0, 0, 70))
        d.text((540, 330), "A REGRA NÃO ATRASA A IA.", font=font(38), fill=YELLOW, anchor="ma")
        draw_wrapped(d, headline, (540, 450), font(68), WHITE, 860, 16, anchor="ma")
        draw_wrapped(d, support.upper(), (540, 760), font(52), RED, 800, 12, anchor="ma")
        rounded_box(d, (180, 1180, 900, 1335), fill=(53,208,186,245), radius=32)
        button = scene.get("button", "VEJA NO PERFIL")
        d.text((540, 1257), button, font=font(40), fill=(7,16,25,255), anchor="mm")
        d.text((540, 1430), "Salve este vídeo antes de liberar IA no time.", font=font(31, False), fill=MUTED, anchor="ma")

    target = WORK / f"overlay-{idx}.png"
    img.save(target)
    return target


def synth_voice(pipeline, idx: int, text: str) -> Path:
    chunks = []
    for result in pipeline(text, voice="pf_dora", speed=VOICE_SPEED, split_pattern=r"\n+"):
        audio = getattr(result, "audio", None)
        if audio is not None:
            chunks.append(np.asarray(audio, dtype=np.float32))
    if not chunks:
        raise RuntimeError(f"No TTS audio for scene {idx}")
    raw = WORK / f"voice-{idx}-raw.wav"
    sf.write(raw, np.concatenate(chunks), 24000, subtype="PCM_16")
    out = WORK / f"voice-{idx}.wav"
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",raw,
         "-af","highpass=f=80,lowpass=f=10000,acompressor=threshold=-20dB:ratio=2:attack=8:release=120:makeup=2,loudnorm=I=-16:TP=-2:LRA=5",
         "-ar","48000","-ac","2",out])
    return out


def render_scene(idx: int, scene: dict, media: Path, overlay: Path, voice: Path, duration: float) -> Path:
    out = WORK / f"scene-{idx}-final.mp4"
    # Gentle motion only; no global speed-up and no opening fade.
    vf = (
        "[0:v]scale=1180:2100:force_original_aspect_ratio=increase,"
        "crop=1080:1920:x='(in_w-out_w)/2+18*sin(t*0.38)':y='(in_h-out_h)/2+10*cos(t*0.31)',"
        "eq=brightness=-0.02:saturation=0.94,setsar=1[bg];"
        "[bg][1:v]overlay=0:0:format=auto[v]"
    )
    run([
        "ffmpeg","-hide_banner","-loglevel","error","-y",
        "-stream_loop","-1","-i",media,
        "-loop","1","-i",overlay,
        "-i",voice,
        "-filter_complex",vf,
        "-map","[v]","-map","2:a:0",
        "-t",f"{duration:.3f}","-r",str(FPS),
        "-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","160k","-movflags","+faststart",out
    ])
    return out


def concat_scenes(scene_files):
    concat_file = WORK / "concat.txt"
    concat_file.write_text("\n".join([f"file '{p.resolve()}'" for p in scene_files]) + "\n", encoding="utf-8")
    out = WORK / "pilot-no-music.mp4"
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",concat_file,"-c","copy",out])
    return out


def mix_music(video: Path) -> Path:
    music = ROOT / PILOT["music"]
    final = OUT / "UGI_Growth_V2_1_Pilot_002.mp4"
    if not music.exists():
        run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",video,"-c","copy",final])
        return final
    dur = ffprobe_duration(video)
    run([
        "ffmpeg","-hide_banner","-loglevel","error","-y",
        "-i",video,"-stream_loop","-1","-i",music,
        "-filter_complex","[0:a]volume=1.0[voice];[1:a]volume=0.075[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=2[a]",
        "-map","0:v:0","-map","[a]","-t",f"{dur:.3f}",
        "-c:v","copy","-c:a","aac","-b:a","160k","-movflags","+faststart",final
    ])
    return final


def main():
    safety = PILOT.get("safety") or {}
    assert safety.get("render_only") is True
    assert safety.get("buffer_mutation") is False
    assert safety.get("publication") is False
    assert safety.get("checkout") is False

    pipeline = KPipeline(lang_code="p")
    scene_files, evidence = [], []
    for idx, scene in enumerate(SCENES, start=1):
        media = download_scene(idx, scene["query"])
        overlay = make_overlay(idx, scene)
        voice = synth_voice(pipeline, idx, scene["narration"])
        voice_dur = ffprobe_duration(voice)
        duration = max(float(scene.get("min_duration", 3.5)), voice_dur + 0.55)
        rendered = render_scene(idx, scene, media, overlay, voice, duration)
        scene_files.append(rendered)
        evidence.append({"scene": idx, "layout": scene["layout"], "voiceDuration": round(voice_dur,3), "sceneDuration": round(duration,3), "query": scene["query"]})

    no_music = concat_scenes(scene_files)
    final = mix_music(no_music)
    total = ffprobe_duration(final)
    meta = {
        "project": "UGI",
        "pilotId": PILOT["pilot_id"],
        "renderer": "UGI Growth V2.1 experimental render-only",
        "voiceSpeed": VOICE_SPEED,
        "globalSpeedUp": False,
        "durationSeconds": round(total,3),
        "publicationTriggered": False,
        "bufferMutationPerformed": False,
        "checkoutTriggered": False,
        "firstFrameHook": True,
        "fixedBottomPanel": False,
        "ctaAutoSafe": True,
        "scenes": evidence,
        "output": str(final.relative_to(ROOT)),
    }
    (OUT / "UGI_Growth_V2_1_Pilot_002_EVIDENCE.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

from __future__ import annotations

import hashlib
import json
import math
import os
import random
import struct
import subprocess
import textwrap
import wave
from pathlib import Path
from urllib.parse import quote

import requests
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

OUT = Path("public/ugi/editorial/2026-09-09")
SRC = OUT / "sources"
OUT.mkdir(parents=True, exist_ok=True)
SRC.mkdir(parents=True, exist_ok=True)

UA = {"User-Agent": "UGI-Editorial/1.0 (rights-cleared Wikimedia Commons asset builder)"}

SOURCES = {
    "apple": {
        "filename": "Apple Park - October 2018 - 8809.jpg",
        "license": "CC BY-SA 4.0",
        "author": "Gregory Varnum",
        "page": "https://commons.wikimedia.org/wiki/File:Apple_Park_-_October_2018_-_8809.jpg",
    },
    "qualcomm": {
        "filename": "Qualcomm headquarters.jpg",
        "license": "CC BY-SA 3.0 / GFDL",
        "author": "Coolcaesar",
        "page": "https://commons.wikimedia.org/wiki/File:Qualcomm_headquarters.jpg",
    },
    "datacenter_inside": {
        "filename": "Hardware interno de servidor data center HostDime.jpg",
        "license": "CC BY 4.0",
        "author": "EditorTech20",
        "page": "https://commons.wikimedia.org/wiki/File:Hardware_interno_de_servidor_data_center_HostDime.jpg",
    },
    "datacenter_outside": {
        "filename": "Data Center HostDime.jpg",
        "license": "CC BY-SA 4.0",
        "author": "HostDime Brasil",
        "page": "https://commons.wikimedia.org/wiki/File:Data_Center_HostDime.jpg",
    },
    "mistral": {
        "filename": "Prime Minister of Bharat, Shri Narendra Damodardas Modi with the Co-Founder and CEO of Mistral AI, Mr. Arthur Mensch.jpg",
        "license": "GODL-India",
        "author": "Prime Minister's Office (India) / Press Information Bureau",
        "page": "https://commons.wikimedia.org/wiki/File:Prime_Minister_of_Bharat,_Shri_Narendra_Damodardas_Modi_with_the_Co-Founder_and_CEO_of_Mistral_AI,_Mr._Arthur_Mensch.jpg",
    },
}


def commons_redirect(filename: str) -> str:
    return "https://commons.wikimedia.org/wiki/Special:Redirect/file/" + quote(filename, safe="")


def download(name: str) -> Path:
    spec = SOURCES[name]
    path = SRC / spec["filename"]
    if path.exists() and path.stat().st_size > 100_000:
        return path
    r = requests.get(commons_redirect(spec["filename"]), headers=UA, timeout=90, allow_redirects=True)
    r.raise_for_status()
    ctype = r.headers.get("content-type", "")
    if "image" not in ctype:
        raise RuntimeError(f"{name}: expected image, got {ctype}")
    path.write_bytes(r.content)
    if path.stat().st_size < 100_000:
        raise RuntimeError(f"{name}: source too small: {path.stat().st_size}")
    return path


def font(size: int, bold: bool = False):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p, size)


def cover(img: Image.Image, size: tuple[int, int], allow_upscale: bool = False) -> Image.Image:
    img = img.convert("RGB")
    tw, th = size
    iw, ih = img.size
    scale = max(tw / iw, th / ih)
    if scale > 1.0 and not allow_upscale:
        raise RuntimeError(f"source {iw}x{ih} would require upscale to cover {tw}x{th}")
    nw, nh = round(iw * scale), round(ih * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = max(0, (nw - tw) // 2)
    top = max(0, (nh - th) // 2)
    return resized.crop((left, top, left + tw, top + th))


def dark_gradient(base: Image.Image, strength: int = 185) -> Image.Image:
    w, h = base.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = overlay.load()
    for y in range(h):
        # top remains open; lower third becomes readable while preserving the photo.
        t = max(0.0, min(1.0, (y / h - 0.48) / 0.42))
        a = int(strength * (t * t))
        for x in range(w):
            px[x, y] = (0, 0, 0, a)
    return Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")


def wrap_by_width(draw: ImageDraw.ImageDraw, text: str, fnt, max_width: int) -> list[str]:
    words = text.split()
    lines, cur = [], ""
    for word in words:
        test = word if not cur else cur + " " + word
        box = draw.textbbox((0, 0), test, font=fnt)
        if box[2] - box[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_text_block(img: Image.Image, headline: str, sub: str, credit: str, brand: str = "UGI • Uma Gestão Inteligente") -> Image.Image:
    d = ImageDraw.Draw(img)
    w, h = img.size
    margin = int(w * 0.075)
    maxw = w - margin * 2
    headline_size = 70 if h >= 1500 else 52
    sub_size = 36 if h >= 1500 else 28
    brand_size = 24 if h >= 1500 else 20
    fh = font(headline_size, True)
    fs = font(sub_size, False)
    fb = font(brand_size, True)
    fc = font(18 if h >= 1500 else 15, False)

    hlines = wrap_by_width(d, headline, fh, maxw)
    slines = wrap_by_width(d, sub, fs, maxw)
    line_h = int(headline_size * 1.16)
    sub_h = int(sub_size * 1.32)
    total = len(hlines) * line_h + 24 + len(slines) * sub_h
    y = h - int(h * 0.10) - total - 95
    for line in hlines:
        d.text((margin + 2, y + 3), line, font=fh, fill=(0, 0, 0))
        d.text((margin, y), line, font=fh, fill=(255, 255, 255))
        y += line_h
    y += 18
    for line in slines:
        d.text((margin + 1, y + 2), line, font=fs, fill=(0, 0, 0))
        d.text((margin, y), line, font=fs, fill=(240, 240, 240))
        y += sub_h

    d.text((margin, h - 70), brand, font=fb, fill=(255, 255, 255))
    cb = d.textbbox((0, 0), credit, font=fc)
    d.text((w - margin - (cb[2] - cb[0]), h - 62), credit, font=fc, fill=(215, 215, 215))
    return img


def make_visual(source_key: str, out_name: str, size: tuple[int, int], headline: str, sub: str) -> Path:
    p = download(source_key)
    src = Image.open(p)
    base = cover(src, size, allow_upscale=False)
    base = ImageEnhance.Contrast(base).enhance(1.03)
    base = ImageEnhance.Color(base).enhance(0.96)
    base = dark_gradient(base)
    spec = SOURCES[source_key]
    credit = f"Imagem: {spec['author']} • {spec['license']}"
    final = draw_text_block(base, headline, sub, credit)
    out = OUT / out_name
    final.save(out, "JPEG", quality=94, subsampling=0, optimize=True)
    if out.stat().st_size < 120_000:
        raise RuntimeError(f"final JPEG too small: {out}")
    return out


def make_music(out: Path, seconds: float = 8.0, sr: int = 48000):
    # Original four-chord instrumental bed (C - Am - F - G), no copyrighted source audio.
    chords = [
        [130.81, 164.81, 196.00, 261.63],
        [110.00, 130.81, 164.81, 220.00],
        [87.31, 130.81, 174.61, 261.63],
        [98.00, 146.83, 196.00, 293.66],
    ]
    n = int(seconds * sr)
    rng = random.Random(20260909)
    samples = []
    for i in range(n):
        t = i / sr
        chord = chords[int(t // 2.0) % 4]
        local = t % 2.0
        arp_idx = int(local / 0.25) % len(chord)
        f = chord[arp_idx]
        # soft pluck + pad
        env = math.exp(-3.5 * (local % 0.25))
        v = 0.14 * env * math.sin(2 * math.pi * f * t)
        for pf in chord:
            v += 0.025 * math.sin(2 * math.pi * pf * t)
        # restrained kick every half-second
        beat = t % 0.5
        if beat < 0.08:
            v += 0.10 * math.exp(-35 * beat) * math.sin(2 * math.pi * (70 - 25 * beat) * t)
        # tiny percussive texture on offbeats
        off = (t + 0.25) % 0.5
        if off < 0.03:
            v += 0.018 * math.exp(-80 * off) * (rng.random() * 2 - 1)
        # fade in/out
        fade = min(1.0, t / 0.35, (seconds - t) / 0.45)
        v *= max(0.0, fade)
        v = max(-0.85, min(0.85, v))
        samples.append(int(v * 32767))
    with wave.open(str(out), "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        for s in samples:
            wf.writeframesraw(struct.pack("<hh", s, s))


def story_mp4(jpg: Path, mp4_name: str, seconds: float = 8.0) -> Path:
    wav = OUT / "ugi-original-story-bed.wav"
    if not wav.exists():
        make_music(wav, seconds=seconds)
    out = OUT / mp4_name
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-framerate", "30", "-i", str(jpg), "-i", str(wav),
        "-t", str(seconds), "-c:v", "libx264", "-profile:v", "high", "-level", "4.1",
        "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
        "-movflags", "+faststart", "-shortest", str(out)
    ]
    subprocess.run(cmd, check=True)
    if out.stat().st_size < 300_000:
        raise RuntimeError(f"story mp4 too small: {out}")
    return out


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    # Morning Apple: factual pre-event framing, no unannounced product shown.
    apple1 = make_visual(
        "apple", "story-apple-0900.jpg", (1080, 1920),
        "Hoje a Apple enfrenta um teste de execução.",
        "Hardware, IA e liderança sob expectativa."
    )
    apple2 = make_visual(
        "apple", "story-apple-0907.jpg", (1080, 1920),
        "Liderança herda mais do que uma marca.",
        "Herda expectativas — e precisa transformá-las em entrega."
    )
    story_mp4(apple1, "story-apple-0900.mp4")
    story_mp4(apple2, "story-apple-0907.mp4")

    # Feed: use a real company-identifiable Qualcomm headquarters image.
    make_visual(
        "qualcomm", "feed-qualcomm-amazon-1230.jpg", (1080, 1350),
        "Qualcomm + Amazon: até US$ 60 bi em infraestrutura de IA",
        "O movimento é sobre diversificação — não apenas chips."
    )

    # LinkedIn management angle + later IG Stories: real data-center infrastructure.
    make_visual(
        "datacenter_inside", "linkedin-digital-resilience-1400.jpg", (1200, 627),
        "Seu negócio sobreviveria sem um fornecedor crítico?",
        "Infraestrutura digital virou risco de gestão."
    )
    dc1 = make_visual(
        "datacenter_outside", "story-resilience-1800.jpg", (1080, 1920),
        "Dependência tecnológica virou risco de gestão.",
        "Cloud, dados e IA também exigem plano de continuidade."
    )
    dc2 = make_visual(
        "datacenter_inside", "story-resilience-1812.jpg", (1080, 1920),
        "Eficiência busca o melhor caminho.",
        "Resiliência garante um segundo caminho quando o primeiro falha."
    )
    story_mp4(dc1, "story-resilience-1800.mp4")
    story_mp4(dc2, "story-resilience-1812.mp4")

    # Mistral: visual feed post rather than a fake Reel; the verified reusable source is a real still.
    make_visual(
        "mistral", "feed-mistral-1915.jpg", (1080, 1350),
        "Mistral AI chega a cerca de US$ 24 bi em valuation",
        "Em IA, posicionamento estratégico também vira valor."
    )

    finals = [p for p in OUT.iterdir() if p.is_file() and p.suffix.lower() in {".jpg", ".mp4"}]
    manifest = {
        "schema": "UGI_EDITORIAL_ASSET_PROVENANCE_V1",
        "date": "2026-09-09",
        "state": "FINAL_ASSETS_BUILT_PENDING_EXACT_PREVIEW_APPROVAL",
        "rules": {
            "ai_generated_subject_substitution": False,
            "upscale_low_resolution": False,
            "rights_manifest_required": True,
            "story_music": "original four-chord instrumental baked into MP4",
            "preview_must_match_publish_media": True,
        },
        "sources": SOURCES,
        "finals": [
            {"path": str(p), "bytes": p.stat().st_size, "sha256": sha256(p)} for p in sorted(finals)
        ],
    }
    (OUT / "asset-provenance.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

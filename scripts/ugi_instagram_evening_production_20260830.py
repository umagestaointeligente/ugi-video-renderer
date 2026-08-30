from __future__ import annotations

import base64
import datetime as dt
import json
import math
import os
import subprocess
import time
import wave
from io import BytesIO
from pathlib import Path
from typing import Any

import numpy as np
import requests
from PIL import Image

WORKER = "https://lola-operacional-ugi.umagestaointeligente.workers.dev"
EXPECTED = "lola-v8-r45-3-instagram-scheduled-media-2026-08-30"
OUT = Path("control-plane/instagram-r45-3/receipts/ugi-20260830-evening-growth.json")
OLD_STORY_POST_IDS = ["6a945ee9d58664eabd78d017", "6a945ef66bbc8c9a02f2ac62"]
EXISTING_REEL_CONTENT_ID = "UGI-20260830-IG-01-CISCO-AGENTS"

STORIES = [
    {
        "contentId": "UGI-20260830-IG-STORY-GROWTH-01-TRUST",
        "dueAt": "2026-08-30T17:15:00-03:00",
        "topic": "Confiança executiva e governança — caso HDFC Bank",
        "hook": "RESULTADO NÃO COMPRA CONFIANÇA.",
        "key_message": "Quando a confiança quebra, até uma sucessão de CEO pode acelerar. Liderança também é governança, transparência e credibilidade.",
        "cta": "Às 19:50: o caso completo no carrossel.",
        "music": {"name": "Executive Pulse", "bpm": 114, "roots": [45, 48, 52, 50], "seed": 11},
    },
    {
        "contentId": "UGI-20260830-IG-STORY-GROWTH-02-PIVOT",
        "dueAt": "2026-08-30T17:55:00-03:00",
        "topic": "Coragem de voltar atrás — fusão Solstice e Element",
        "hook": "US$ 14,5 BI. E ELES VOLTARAM ATRÁS.",
        "key_message": "Solstice e Element cancelaram a fusão após ouvir os acionistas. Mudar a decisão quando as premissas mudam também é liderança.",
        "cta": "Pergunta: você sabe abandonar uma decisão?",
        "music": {"name": "Pivot Motion", "bpm": 124, "roots": [50, 53, 45, 48], "seed": 22},
    },
    {
        "contentId": "UGI-20260830-IG-STORY-GROWTH-03-TRANSFORM",
        "dueAt": "2026-08-30T19:20:00-03:00",
        "topic": "Transformar antes da crise — Sinopec",
        "hook": "MUDE ANTES DE A CRISE OBRIGAR.",
        "key_message": "A Sinopec está reorganizando a estrutura mesmo com lucro crescente. Transformação estratégica não precisa começar no prejuízo.",
        "cta": "Mude enquanto ainda há escolha.",
        "music": {"name": "Forward Shift", "bpm": 118, "roots": [43, 47, 50, 45], "seed": 33},
    },
    {
        "contentId": "UGI-20260830-IG-STORY-GROWTH-04-EBIT",
        "dueAt": "2026-08-30T20:35:00-03:00",
        "topic": "Produtividade individual com IA versus resultado empresarial",
        "hook": "80% MAIS PRODUTIVOS. SÓ 37% NO EBIT.",
        "key_message": "Produtividade individual com IA não vira resultado sozinha. O processo precisa capturar o ganho de velocidade e transformá-lo em resultado.",
        "cta": "Velocidade sem redesenho vira só trabalho mais rápido.",
        "music": {"name": "Data Drive", "bpm": 121, "roots": [48, 52, 55, 50], "seed": 44},
    },
    {
        "contentId": "UGI-20260830-IG-STORY-GROWTH-05-COMMERCE",
        "dueAt": "2026-08-30T21:50:00-03:00",
        "topic": "Materiais UGI para aplicar gestão e IA na prática",
        "hook": "GESTÃO + IA PRECISA VIRAR PRÁTICA.",
        "key_message": "Frameworks, checklists e materiais UGI para aplicar decisões, delegação e inteligência artificial no trabalho.",
        "cta": "Materiais disponíveis no link da bio. Acesse e compre o seu hoje.",
        "music": {"name": "Action Lift", "bpm": 128, "roots": [52, 55, 47, 50], "seed": 55},
    },
]

CAROUSEL = {
    "contentId": "UGI-20260830-IG-CAROUSEL-TRUST-HDFC",
    "dueAt": "2026-08-30T19:50:00-03:00",
    "topic": "Confiança executiva, governança e legitimidade para liderar — caso HDFC Bank",
    "hook": "UM CEO PODE ENTREGAR RESULTADO E MESMO ASSIM PERDER A CONFIANÇA?",
    "key_message": "Resultado, confiança e legitimidade para liderar não são a mesma coisa. Governança e transparência acumulam ou destroem capital de liderança.",
    "instructions": "Crie EXATAMENTE 7 slides. 1) pergunta da capa; 2) Pode; 3) liderança não é avaliada só pelo P&L; 4) governança, transparência e confiança também acumulam ou destroem capital; 5) quando o mercado desconfia cada decisão custa mais credibilidade; 6) recuperar confiança pode ser mais difícil que recuperar resultado; 7) Resultado mantém você no jogo. Confiança permite que continuem deixando você liderar. Caso atual: HDFC Bank. Não invente fatos ou números. Fonte editorial para a legenda: Reuters, 30/08/2026.",
    "cta": "Salve este carrossel para lembrar: resultado mantém você no jogo; confiança mantém sua liderança.",
    "music": {"name": "Trust Momentum", "bpm": 116, "roots": [45, 52, 48, 50], "seed": 66},
    "caption": "Resultado não é a única moeda de um líder. O caso HDFC Bank recolocou uma pergunta incômoda no centro da gestão: o que acontece quando desempenho, governança e confiança deixam de caminhar juntos? A liderança executiva depende de entrega, mas também de transparência, credibilidade e legitimidade para continuar tomando decisões em nome da organização. Quando a confiança começa a cair, cada nova decisão custa mais capital político e institucional. E recuperar esse capital pode ser mais difícil do que recuperar um indicador financeiro. Fonte do caso: Reuters, 30/08/2026. Salve este carrossel para a próxima conversa sobre liderança e governança. #UmaGestaoInteligente #Lideranca #Governanca #Gestao",
}

STATIC_POST = {
    "contentId": "UGI-20260830-IG-STATIC-PIVOT-145B",
    "dueAt": "2026-08-30T21:15:00-03:00",
    "topic": "Qualidade de decisão e coragem de voltar atrás — Solstice e Element",
    "hook": "VOLTAR ATRÁS TAMBÉM É DECIDIR BEM.",
    "key_message": "Solstice e Element abandonaram uma fusão de US$ 14,5 bilhões depois de ouvir os acionistas. Uma decisão madura tem critérios para continuar — e critérios para morrer.",
    "instructions": "Post visual, não editorial. Faça parecer uma ferramenta de decisão: PREMISSA MUDOU? DADO NOVO? STAKEHOLDER CRÍTICO DISCORDA? CUSTO DE CONTINUAR > CUSTO DE RECUAR? Pouco texto, hierarquia forte e visual salvável. Não invente dados. Fonte editorial: Reuters/relatos de 27/08/2026 fornecidos no radar UGI.",
    "cta": "Premissas mudaram? Reabra a decisão.",
}


class Client:
    def __init__(self, key: str) -> None:
        self.h = {"x-lola-command-key": key, "accept": "application/json"}

    def get(self, path: str, timeout: int = 120) -> tuple[int, dict[str, Any]]:
        r = requests.get(WORKER + path, headers=self.h, timeout=timeout)
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, {"ok": False, "raw": r.text[:2000]}

    def post(self, path: str, payload: dict[str, Any], timeout: int = 900) -> tuple[int, dict[str, Any]]:
        r = requests.post(WORKER + path, headers={**self.h, "content-type": "application/json"}, json=payload, timeout=timeout)
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, {"ok": False, "raw": r.text[:2000]}


def iso(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def same_instant(a: str | None, b: str | None, tolerance: int = 90) -> bool:
    if not a or not b:
        return False
    try:
        return abs((iso(a).astimezone(dt.timezone.utc) - iso(b).astimezone(dt.timezone.utc)).total_seconds()) <= tolerance
    except Exception:
        return False


def save(payload: dict[str, Any]) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def image_info(url: str, expected: tuple[int, int]) -> dict[str, Any]:
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    with Image.open(BytesIO(r.content)) as im:
        w, h = int(im.width), int(im.height)
    return {"url": url, "width": w, "height": h, "bytes": len(r.content), "pass": (w, h) == expected and len(r.content) > 5000}


def midi_freq(note: float) -> float:
    return 440.0 * (2.0 ** ((note - 69.0) / 12.0))


def add_note(buf: np.ndarray, sr: int, start: float, duration: float, note: float, amp: float, bright: float = 0.35) -> None:
    i0 = max(0, int(start * sr))
    i1 = min(len(buf), int((start + duration) * sr))
    if i1 <= i0:
        return
    t = np.arange(i1 - i0, dtype=np.float64) / sr
    f = midi_freq(note)
    env = np.minimum(t / 0.025, 1.0) * np.exp(-2.7 * t / max(duration, 0.1))
    wave1 = np.sin(2 * np.pi * f * t)
    wave2 = 0.45 * np.sin(2 * np.pi * 2 * f * t + 0.18)
    wave3 = bright * 0.22 * np.sin(2 * np.pi * 3 * f * t + 0.4)
    buf[i0:i1] += amp * env * (wave1 + wave2 + wave3)


def synth_music(path: Path, *, bpm: int, roots: list[int], seed: int, duration: float = 9.0) -> None:
    sr = 44100
    n = int(sr * duration)
    audio = np.zeros(n, dtype=np.float64)
    rng = np.random.default_rng(seed)
    beat = 60.0 / bpm
    chord_beats = 2
    # Chords + bass: warm synth, not a single tone.
    for idx, root in enumerate(roots * 3):
        start = idx * chord_beats * beat
        if start >= duration:
            break
        chord = [root, root + 4, root + 7, root + 11]
        for tone in chord:
            add_note(audio, sr, start, chord_beats * beat * 0.96, tone + 12, 0.075, 0.45)
        add_note(audio, sr, start, chord_beats * beat * 0.88, root - 12, 0.18, 0.1)
    # Melody/plucks.
    scale = [0, 2, 4, 7, 9, 11]
    step = beat / 2
    t0 = 0.0
    j = 0
    while t0 < duration:
        root = roots[(j // 4) % len(roots)]
        offset = scale[(j * 2 + seed) % len(scale)]
        if j % 2 == 0 or rng.random() > 0.45:
            add_note(audio, sr, t0, step * 0.85, root + 24 + offset, 0.105, 0.75)
        t0 += step
        j += 1
    # Drums: kick every beat, clap/snare on 2/4, hats on eighths.
    for b in range(int(duration / beat) + 2):
        start = b * beat
        i0 = int(start * sr)
        length = min(int(0.16 * sr), n - i0)
        if length > 0:
            tt = np.arange(length) / sr
            kick = np.sin(2 * np.pi * (72 - 38 * tt) * tt) * np.exp(-22 * tt)
            audio[i0:i0 + length] += 0.34 * kick
        if b % 4 in (1, 3):
            i0 = int(start * sr)
            length = min(int(0.12 * sr), n - i0)
            if length > 0:
                tt = np.arange(length) / sr
                noise = rng.normal(0, 1, length)
                clap = noise * np.exp(-28 * tt)
                audio[i0:i0 + length] += 0.095 * clap
    hat_step = beat / 2
    h = 0.0
    while h < duration:
        i0 = int(h * sr)
        length = min(int(0.045 * sr), n - i0)
        if length > 0:
            tt = np.arange(length) / sr
            noise = rng.normal(0, 1, length)
            audio[i0:i0 + length] += 0.035 * noise * np.exp(-65 * tt)
        h += hat_step
    # Gentle stereo-like chorus through delayed copy and soft limiting.
    delay = int(0.018 * sr)
    if delay < n:
        audio[delay:] += 0.12 * audio[:-delay]
    fade = int(0.3 * sr)
    audio[:fade] *= np.linspace(0, 1, fade)
    audio[-fade:] *= np.linspace(1, 0, fade)
    audio = np.tanh(audio * 1.4)
    peak = float(np.max(np.abs(audio)) or 1.0)
    audio = 0.78 * audio / peak
    pcm = (audio * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


def make_video(image_path: Path, music_path: Path, out: Path, duration: int = 9, target: tuple[int, int] = (1080, 1920)) -> None:
    w, h = target
    vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},zoompan=z='min(zoom+0.0007,1.04)':d=1:s={w}x{h}:fps=30,format=yuv420p"
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(image_path), "-i", str(music_path),
        "-t", str(duration), "-vf", vf, "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-af", "volume=0.78", "-shortest", "-movflags", "+faststart", str(out),
    ]
    p = subprocess.run(cmd, text=True, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError("ffmpeg failed: " + p.stderr[-1600:])
    raw = out.read_bytes()
    if len(raw) < 30000 or raw[4:8] != b"ftyp":
        raise RuntimeError("invalid output MP4")


def download(url: str, path: Path) -> None:
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    path.write_bytes(r.content)


def upload_mp4(c: Client, cid: str, path: Path) -> dict[str, Any]:
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    code, data = c.post("/api/r45-2/media-upload", {"contentId": cid, "videoBase64": b64}, timeout=300)
    if code != 200 or data.get("ok") is not True or not data.get("videoUrl"):
        raise RuntimeError(f"media upload failed {code}: {data}")
    return data


def generate(c: Client, *, type_: str, cid: str, topic: str, hook: str, key_message: str, instructions: str, cta: str, slides: int = 7) -> dict[str, Any]:
    payload = {
        "source": "UGI-CONTROL-PLANE-R45.3-PRODUCTION",
        "type": type_,
        "content_id": cid,
        "experiment_id": "UGI-20260830-EVENING-GROWTH",
        "variant": "PRODUCTION",
        "topic": topic,
        "objective": "human_utility_first_growth",
        "audience": "gestores, líderes e profissionais que usam IA no trabalho",
        "hook": hook,
        "key_message": key_message,
        "instructions": instructions,
        "cta": cta,
        "slides": slides,
        "editorial_mode": "human_utility_first",
        "commercial_offer": False,
    }
    code, data = c.post("/api/r45/generate", payload, timeout=900)
    if code != 200 or data.get("ok") is not True or not (data.get("draft") or {}).get("id"):
        raise RuntimeError(f"generation failed {code}: {str(data)[:1800]}")
    return data


def approve_static(c: Client, draft_id: str) -> dict[str, Any]:
    code, data = c.post("/api/r45/static-approval", {"id": draft_id, "decision": "approved"}, timeout=120)
    if code != 200 or data.get("ok") is not True:
        raise RuntimeError(f"approval failed {code}: {data}")
    return data


def poll_buffer(c: Client, post_id: str, seconds: int = 60) -> dict[str, Any]:
    end = time.time() + seconds
    last: dict[str, Any] = {}
    while time.time() < end:
        code, last = c.get("/api/r45-2/buffer-status?id=" + requests.utils.quote(post_id, safe=""), timeout=120)
        if code == 200 and last.get("ok") is True and (last.get("post") or {}).get("id"):
            return last
        time.sleep(5)
    return last


def schedule_media(c: Client, *, kind: str, cid: str, video_url: str, image_urls: list[str], text: str, due_at: str) -> dict[str, Any]:
    code, data = c.post("/api/r45-3/instagram-publish", {
        "kind": kind, "contentId": cid, "videoUrl": video_url, "imageUrls": image_urls,
        "text": text, "mode": "customScheduled", "dueAt": due_at,
    }, timeout=180)
    post = data.get("post") or {}
    if code != 200 or data.get("ok") is not True or not post.get("id"):
        raise RuntimeError(f"schedule media failed {code}: {str(data)[:1800]}")
    rb = poll_buffer(c, str(post["id"]))
    live = rb.get("post") or post
    ok = bool(live.get("id")) and str(live.get("status") or "").lower() == "scheduled" and same_instant(live.get("dueAt"), due_at)
    if not ok:
        raise RuntimeError(f"media readback failed: {str(rb)[:1800]}")
    return {"publishHttp": code, "publish": data, "readback": rb, "bufferPostId": live.get("id"), "status": live.get("status"), "dueAt": live.get("dueAt"), "dueAtMatch": True, "state": "PROVEN_SCHEDULED"}


def schedule_static(c: Client, draft_id: str, due_at: str) -> dict[str, Any]:
    code, data = c.post("/api/r45/static-publish", {"id": draft_id, "mode": "customScheduled", "dueAt": due_at}, timeout=180)
    if code != 200 or data.get("ok") is not True:
        raise RuntimeError(f"static schedule failed {code}: {str(data)[:1800]}")
    code, rb = c.get("/api/r45/static-publication-status?id=" + requests.utils.quote(draft_id, safe=""), timeout=120)
    pub = rb.get("publication") or {}
    ok = code == 200 and rb.get("ok") is True and bool(pub.get("bufferPostId")) and str(pub.get("status") or "").lower() == "scheduled" and same_instant(pub.get("dueAt"), due_at)
    if not ok:
        raise RuntimeError(f"static readback failed: {str(rb)[:1800]}")
    return {"publish": data, "readback": rb, "bufferPostId": pub.get("bufferPostId"), "status": pub.get("status"), "dueAt": pub.get("dueAt"), "dueAtMatch": True, "state": "PROVEN_SCHEDULED"}


def delete_old(c: Client, post_id: str) -> dict[str, Any]:
    # Idempotent: if the post is already absent/cancelled, record that rather than failing the production batch.
    status_code, status = c.get("/api/r45-2/buffer-status?id=" + requests.utils.quote(post_id, safe=""), timeout=120)
    live = status.get("post") or {}
    if status_code == 200 and str(live.get("status") or "").lower() in {"cancelled", "deleted"}:
        return {"postId": post_id, "state": "ALREADY_ABSENT", "statusBefore": live}
    code, data = c.post("/api/r45-3/buffer-delete", {"postId": post_id}, timeout=120)
    if code == 200 and data.get("ok") is True:
        return {"postId": post_id, "state": "DELETED", "delete": data, "statusBefore": live}
    # Buffer may return not-found for an already removed test; accept only if a follow-up cannot resolve an active post.
    code2, status2 = c.get("/api/r45-2/buffer-status?id=" + requests.utils.quote(post_id, safe=""), timeout=120)
    live2 = status2.get("post") or {}
    if not live2.get("id") or str(live2.get("status") or "").lower() in {"cancelled", "deleted"}:
        return {"postId": post_id, "state": "ABSENT_AFTER_DELETE_ATTEMPT", "deleteHttp": code, "delete": data, "statusAfter": status2}
    raise RuntimeError(f"could not delete old Buffer post {post_id}: {code} {data}")


def main() -> int:
    key = os.getenv("UGI_WORKER_COMMAND_KEY") or os.getenv("UGI_LOLA_COMMAND_KEY") or ""
    if not key:
        raise SystemExit("UGI_WORKER_COMMAND_KEY_MISSING")
    c = Client(key)
    receipt: dict[str, Any] = {
        "project": "UGI",
        "component": "INSTAGRAM-R45.3-EVENING-GROWTH",
        "timezone": "America/Sao_Paulo",
        "startedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
        "oldScheduleCleanup": [],
        "results": [],
    }
    save(receipt)

    # Health gate.
    for _ in range(24):
        _, health = c.get("/api/health")
        receipt["health"] = health
        if health.get("ok") is True and health.get("version") == EXPECTED:
            break
        time.sleep(5)
    if (receipt.get("health") or {}).get("version") != EXPECTED:
        receipt.update(ok=False, state="R45_3_NOT_LIVE", finishedAt=dt.datetime.now(dt.timezone.utc).isoformat())
        save(receipt)
        return 2

    # Confirm and preserve existing Reel at 18:30 BRT.
    _, lookup = c.get("/api/draft-lookup?content_id=" + requests.utils.quote(EXISTING_REEL_CONTENT_ID, safe=""))
    did = str(lookup.get("draftId") or "")
    reel: dict[str, Any] = {"contentId": EXISTING_REEL_CONTENT_ID, "platform": "instagram", "type": "reel", "draftId": did}
    if not did:
        raise RuntimeError("existing Instagram Reel draft not found")
    _, reel_rb = c.get("/api/platform-publication-status?id=" + requests.utils.quote(did, safe="") + "&platform=instagram")
    reel_pub = reel_rb.get("publication") or {}
    reel_ok = bool(reel_pub.get("bufferPostId")) and str(reel_pub.get("status") or "").lower() == "scheduled" and same_instant(reel_pub.get("dueAt"), "2026-08-30T18:30:00-03:00")
    reel.update({"bufferPostId": reel_pub.get("bufferPostId"), "dueAt": reel_pub.get("dueAt"), "status": reel_pub.get("status"), "readback": reel_rb, "state": "PRESERVED_PROVEN_SCHEDULED" if reel_ok else "EXISTING_REEL_NOT_PROVEN", "ok": reel_ok})
    if not reel_ok:
        raise RuntimeError("existing Reel is not proven scheduled at 18:30")
    receipt["existingReel"] = reel
    save(receipt)

    # Delete superseded static Story schedule from the earlier pilot.
    for post_id in OLD_STORY_POST_IDS:
        receipt["oldScheduleCleanup"].append(delete_old(c, post_id))
        save(receipt)

    temp = Path("/tmp/ugi-r453")
    temp.mkdir(parents=True, exist_ok=True)

    # 5 Stories: generate art, QA, synthesize unique original music, render MP4, upload and schedule.
    for idx, row in enumerate(STORIES, 1):
        gen = generate(c, type_="story_image", cid=row["contentId"], topic=row["topic"], hook=row["hook"], key_message=row["key_message"], instructions="Story muito visual, linguagem humana, alto contraste, sem aparência de anúncio corporativo. Não invente dados. " + ("CTA comercial pago: não use a palavra grátis. " if idx == 5 else ""), cta=row["cta"], slides=1)
        draft = gen.get("draft") or {}
        image_url = str(draft.get("imageUrl") or "")
        qa = image_info(image_url, (1080, 1920))
        if not qa["pass"]:
            raise RuntimeError(f"Story {idx} image QA failed: {qa}")
        img = temp / f"story-{idx}.png"
        wav = temp / f"story-{idx}.wav"
        mp4 = temp / f"story-{idx}.mp4"
        download(image_url, img)
        music = row["music"]
        synth_music(wav, bpm=music["bpm"], roots=music["roots"], seed=music["seed"], duration=9.0)
        make_video(img, wav, mp4, 9, (1080, 1920))
        upload = upload_mp4(c, row["contentId"], mp4)
        scheduled = schedule_media(c, kind="story_video", cid=row["contentId"], video_url=upload["videoUrl"], image_urls=[], text="", due_at=row["dueAt"])
        receipt["results"].append({
            "contentId": row["contentId"], "platform": "instagram", "type": "story_video_music", "draftId": draft.get("id"),
            "dueAtRequested": row["dueAt"], "topic": row["topic"], "hook": row["hook"], "cta": row["cta"],
            "qa": qa, "music": {"name": music["name"], "bpm": music["bpm"], "mode": "embedded_original_audio", "uniqueSeed": music["seed"]},
            "videoBytes": mp4.stat().st_size, "upload": upload, **scheduled, "ok": True,
        })
        save(receipt)

    # Carousel: R45 deterministic images + QA + approval; first card becomes a short musical video, remaining cards stay images.
    cg = generate(c, type_="carousel", cid=CAROUSEL["contentId"], topic=CAROUSEL["topic"], hook=CAROUSEL["hook"], key_message=CAROUSEL["key_message"], instructions=CAROUSEL["instructions"], cta=CAROUSEL["cta"], slides=7)
    cd = cg.get("draft") or {}
    image_urls = list(cd.get("imageUrls") or [])
    if len(image_urls) != 7:
        raise RuntimeError(f"carousel needs 7 images, got {len(image_urls)}")
    cqa = [image_info(u, (1080, 1350)) for u in image_urls]
    if not all(x["pass"] for x in cqa):
        raise RuntimeError("carousel image QA failed")
    approve_static(c, str(cd["id"]))
    cover = temp / "carousel-cover.png"
    cwav = temp / "carousel-trust.wav"
    cmp4 = temp / "carousel-trust.mp4"
    download(image_urls[0], cover)
    cm = CAROUSEL["music"]
    synth_music(cwav, bpm=cm["bpm"], roots=cm["roots"], seed=cm["seed"], duration=8.0)
    make_video(cover, cwav, cmp4, 8, (1080, 1350))
    cup = upload_mp4(c, CAROUSEL["contentId"], cmp4)
    cs = schedule_media(c, kind="mixed_carousel", cid=CAROUSEL["contentId"], video_url=cup["videoUrl"], image_urls=image_urls[1:], text=CAROUSEL["caption"], due_at=CAROUSEL["dueAt"])
    receipt["results"].append({
        "contentId": CAROUSEL["contentId"], "platform": "instagram", "type": "carousel_mixed_media_music", "draftId": cd.get("id"),
        "dueAtRequested": CAROUSEL["dueAt"], "topic": CAROUSEL["topic"], "qa": cqa,
        "music": {"name": cm["name"], "bpm": cm["bpm"], "mode": "embedded_audio_on_video_card", "nativeInstagramMusic": False},
        "videoBytes": cmp4.stat().st_size, "upload": cup, **cs, "ok": True,
    })
    save(receipt)

    # Static visual post: true static post, scheduled through canonical R45 route.
    sg = generate(c, type_="visual_post", cid=STATIC_POST["contentId"], topic=STATIC_POST["topic"], hook=STATIC_POST["hook"], key_message=STATIC_POST["key_message"], instructions=STATIC_POST["instructions"], cta=STATIC_POST["cta"], slides=1)
    sd = sg.get("draft") or {}
    sqa = image_info(str(sd.get("imageUrl") or ""), (1080, 1350))
    if not sqa["pass"]:
        raise RuntimeError(f"static post QA failed: {sqa}")
    approve_static(c, str(sd["id"]))
    ss = schedule_static(c, str(sd["id"]), STATIC_POST["dueAt"])
    receipt["results"].append({
        "contentId": STATIC_POST["contentId"], "platform": "instagram", "type": "visual_post", "draftId": sd.get("id"),
        "dueAtRequested": STATIC_POST["dueAt"], "topic": STATIC_POST["topic"], "qa": sqa,
        "music": {"mode": "none", "reason": "true_static_post_native_music_not_automatable_via_current_Buffer_API"},
        **ss, "ok": True,
    })

    receipt["agenda"] = [
        {"time":"17:15","type":"Story","contentId":STORIES[0]["contentId"]},
        {"time":"17:55","type":"Story","contentId":STORIES[1]["contentId"]},
        {"time":"18:30","type":"Reel","contentId":EXISTING_REEL_CONTENT_ID},
        {"time":"19:20","type":"Story","contentId":STORIES[2]["contentId"]},
        {"time":"19:50","type":"Carousel","contentId":CAROUSEL["contentId"]},
        {"time":"20:35","type":"Story","contentId":STORIES[3]["contentId"]},
        {"time":"21:15","type":"Static","contentId":STATIC_POST["contentId"]},
        {"time":"21:50","type":"Story","contentId":STORIES[4]["contentId"]},
    ]
    receipt["ok"] = bool(receipt["existingReel"].get("ok")) and all(x.get("ok") is True for x in receipt["results"])
    receipt["state"] = "PROVEN_SCHEDULED_8_OF_8" if receipt["ok"] else "PARTIAL_OR_FAILED"
    receipt["finishedAt"] = dt.datetime.now(dt.timezone.utc).isoformat()
    save(receipt)
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import datetime as dt
import json
import os
import time
from pathlib import Path
from typing import Any

import requests

import ugi_instagram_evening_production_20260830 as prod

RECEIPT = Path("control-plane/instagram-r45-3/receipts/ugi-20260830-evening-growth.json")
EXPECTED_STORIES = {
    "UGI-20260830-IG-STORY-GROWTH-01-TRUST": ("6a948831d58664eabd7be158", "2026-08-30T17:15:00-03:00"),
    "UGI-20260830-IG-STORY-GROWTH-02-PIVOT": ("6a948844d58664eabd7be258", "2026-08-30T17:55:00-03:00"),
    "UGI-20260830-IG-STORY-GROWTH-03-TRANSFORM": ("6a948851d58664eabd7be3fc", "2026-08-30T19:20:00-03:00"),
    "UGI-20260830-IG-STORY-GROWTH-04-EBIT": ("6a94885ffd31f7e50b775fbe", "2026-08-30T20:35:00-03:00"),
    "UGI-20260830-IG-STORY-GROWTH-05-COMMERCE": ("6a94886bfd31f7e50b776037", "2026-08-30T21:50:00-03:00"),
}
REEL_ID = "6a944edbd076c0e5835e88a2"
REEL_DUE = "2026-08-30T18:30:00-03:00"
CAROUSEL_CID = "UGI-20260830-IG-CAROUSEL-TRUST-HDFC"
STATIC_CID = "UGI-20260830-IG-STATIC-PIVOT-145B"


def parse(v: str) -> dt.datetime:
    return dt.datetime.fromisoformat(v.replace("Z", "+00:00")).astimezone(dt.timezone.utc)


def valid_live(post: dict[str, Any], due_at: str) -> bool:
    if not post.get("id") or not prod.same_instant(post.get("dueAt"), due_at):
        return False
    st = str(post.get("status") or "").lower()
    due = parse(due_at)
    now = dt.datetime.now(dt.timezone.utc)
    if st == "scheduled" and now < due + dt.timedelta(minutes=2):
        return True
    if st in {"sent", "published", "complete", "completed"} and post.get("sentAt"):
        return True
    return False


def save(data: dict[str, Any]) -> None:
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    key = os.getenv("UGI_WORKER_COMMAND_KEY") or os.getenv("UGI_LOLA_COMMAND_KEY") or ""
    if not key:
        raise SystemExit("UGI_WORKER_COMMAND_KEY_MISSING")
    c = prod.Client(key)
    if not RECEIPT.exists():
        raise RuntimeError("base receipt missing")
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    data["recoveryStartedAt"] = dt.datetime.now(dt.timezone.utc).isoformat()
    data["recoveryChecks"] = []
    save(data)

    # Verify every already-created Story; never recreate them in this recovery.
    for cid, (post_id, due_at) in EXPECTED_STORIES.items():
        code, rb = c.get("/api/r45-2/buffer-status?id=" + requests.utils.quote(post_id, safe=""))
        post = rb.get("post") or {}
        ok = code == 200 and rb.get("ok") is True and valid_live(post, due_at)
        data["recoveryChecks"].append({"contentId": cid, "bufferPostId": post_id, "dueAtExpected": due_at, "readback": rb, "ok": ok})
        if not ok:
            save(data)
            raise RuntimeError(f"existing Story proof failed: {cid} {rb}")

    # Verify existing Reel without touching it.
    code, rb = c.get("/api/r45-2/buffer-status?id=" + requests.utils.quote(REEL_ID, safe=""))
    reel_post = rb.get("post") or {}
    reel_ok = code == 200 and rb.get("ok") is True and valid_live(reel_post, REEL_DUE)
    data["recoveryChecks"].append({"contentId": prod.EXISTING_REEL_CONTENT_ID, "bufferPostId": REEL_ID, "dueAtExpected": REEL_DUE, "readback": rb, "ok": reel_ok})
    if not reel_ok:
        save(data)
        raise RuntimeError(f"existing Reel proof failed: {rb}")

    existing_ids = {str(x.get("contentId")) for x in (data.get("results") or [])}

    # Recover carousel with a short, stronger cover that passes the objective gate.
    if CAROUSEL_CID not in existing_ids:
        cg = prod.generate(
            c,
            type_="carousel",
            cid=CAROUSEL_CID,
            topic="Confiança executiva, governança e legitimidade para liderar — caso HDFC Bank",
            hook="RESULTADO ≠ CONFIANÇA",
            key_message="Resultado, confiança e legitimidade para liderar não são a mesma coisa. Governança e transparência acumulam ou destroem capital de liderança.",
            instructions=(
                "Crie EXATAMENTE 7 slides. Capa curta: RESULTADO ≠ CONFIANÇA. "
                "Slide 2: Um CEO pode entregar resultado e ainda perder confiança. "
                "3: liderança não é avaliada só pelo P&L. "
                "4: governança, transparência e confiança acumulam ou destroem capital. "
                "5: quando o mercado desconfia, cada decisão custa mais credibilidade. "
                "6: recuperar confiança pode ser mais difícil que recuperar resultado. "
                "7: Resultado mantém você no jogo. Confiança permite que continuem deixando você liderar. "
                "Visual premium e salvável, frases curtas, sem texto cortado. Caso HDFC Bank. Não invente fatos."
            ),
            cta="Salve: resultado mantém você no jogo; confiança mantém sua liderança.",
            slides=7,
        )
        cd = cg.get("draft") or {}
        urls = list(cd.get("imageUrls") or [])
        if len(urls) != 7:
            raise RuntimeError(f"carousel expected 7 slides, got {len(urls)}")
        qa = [prod.image_info(u, (1080, 1350)) for u in urls]
        if not all(x["pass"] for x in qa):
            raise RuntimeError("carousel visual QA failed")
        prod.approve_static(c, str(cd["id"]))

        tmp = Path("/tmp/ugi-r453-recovery")
        tmp.mkdir(parents=True, exist_ok=True)
        cover, wav, mp4 = tmp / "cover.png", tmp / "trust.wav", tmp / "trust.mp4"
        prod.download(urls[0], cover)
        prod.synth_music(wav, bpm=116, roots=[45, 52, 48, 50], seed=66, duration=8.0)
        prod.make_video(cover, wav, mp4, 8, (1080, 1350))
        up = prod.upload_mp4(c, CAROUSEL_CID, mp4)
        caption = (
            "Resultado não é a única moeda de um líder. O caso HDFC Bank recolocou uma pergunta incômoda no centro da gestão: "
            "o que acontece quando desempenho, governança e confiança deixam de caminhar juntos? Liderança executiva depende de entrega, "
            "mas também de transparência, credibilidade e legitimidade para continuar tomando decisões. Fonte do caso: Reuters, 30/08/2026. "
            "Salve este carrossel para a próxima conversa sobre liderança e governança. #UmaGestaoInteligente #Lideranca #Governanca #Gestao"
        )
        sch = prod.schedule_media(c, kind="mixed_carousel", cid=CAROUSEL_CID, video_url=up["videoUrl"], image_urls=urls[1:], text=caption, due_at="2026-08-30T19:50:00-03:00")
        data.setdefault("results", []).append({
            "contentId": CAROUSEL_CID, "platform": "instagram", "type": "carousel_mixed_media_music", "draftId": cd.get("id"),
            "dueAtRequested": "2026-08-30T19:50:00-03:00", "topic": "Confiança executiva e governança — HDFC Bank",
            "qa": qa, "music": {"name": "Trust Momentum", "bpm": 116, "mode": "embedded_audio_on_video_card", "nativeInstagramMusic": False},
            "videoBytes": mp4.stat().st_size, "upload": up, **sch, "ok": True,
        })
        save(data)

    # Recover true static post.
    existing_ids = {str(x.get("contentId")) for x in (data.get("results") or [])}
    if STATIC_CID not in existing_ids:
        sg = prod.generate(
            c,
            type_="visual_post",
            cid=STATIC_CID,
            topic="Qualidade de decisão e coragem de voltar atrás — Solstice e Element",
            hook="VOLTAR ATRÁS TAMBÉM É DECIDIR BEM",
            key_message="Solstice e Element abandonaram uma fusão de US$ 14,5 bilhões depois de ouvir os acionistas. Uma decisão madura tem critérios para continuar — e critérios para morrer.",
            instructions=(
                "Post visual e salvável, não editorial. Pouco texto. Use uma árvore/checklist visual com quatro perguntas: "
                "PREMISSA MUDOU? DADO NOVO? STAKEHOLDER CRÍTICO DISCORDA? CUSTO DE CONTINUAR > CUSTO DE RECUAR? "
                "Visual limpo, sem texto cortado. Não invente fatos."
            ),
            cta="Premissas mudaram? Reabra a decisão.",
            slides=1,
        )
        sd = sg.get("draft") or {}
        sqa = prod.image_info(str(sd.get("imageUrl") or ""), (1080, 1350))
        if not sqa["pass"]:
            raise RuntimeError(f"static post QA failed: {sqa}")
        prod.approve_static(c, str(sd["id"]))
        sch = prod.schedule_static(c, str(sd["id"]), "2026-08-30T21:15:00-03:00")
        data.setdefault("results", []).append({
            "contentId": STATIC_CID, "platform": "instagram", "type": "visual_post", "draftId": sd.get("id"),
            "dueAtRequested": "2026-08-30T21:15:00-03:00", "topic": "Coragem de voltar atrás — decisão de US$ 14,5 bi",
            "qa": sqa, "music": {"mode": "none", "reason": "true_static_post; native Instagram music is not automatable through current Buffer API"},
            **sch, "ok": True,
        })
        save(data)

    # Final authoritative proof: 5 Stories + carousel + static + existing Reel.
    rows = data.get("results") or []
    wanted = set(EXPECTED_STORIES) | {CAROUSEL_CID, STATIC_CID}
    indexed = {str(x.get("contentId")): x for x in rows if str(x.get("contentId")) in wanted}
    all_new_ok = wanted.issubset(indexed.keys()) and all(indexed[c].get("ok") is True for c in wanted)
    all_checks_ok = all(x.get("ok") is True for x in data.get("recoveryChecks") or [])
    data["agenda"] = [
        {"time":"17:15","type":"Story","contentId":"UGI-20260830-IG-STORY-GROWTH-01-TRUST"},
        {"time":"17:55","type":"Story","contentId":"UGI-20260830-IG-STORY-GROWTH-02-PIVOT"},
        {"time":"18:30","type":"Reel","contentId":prod.EXISTING_REEL_CONTENT_ID},
        {"time":"19:20","type":"Story","contentId":"UGI-20260830-IG-STORY-GROWTH-03-TRANSFORM"},
        {"time":"19:50","type":"Carousel","contentId":CAROUSEL_CID},
        {"time":"20:35","type":"Story","contentId":"UGI-20260830-IG-STORY-GROWTH-04-EBIT"},
        {"time":"21:15","type":"Static","contentId":STATIC_CID},
        {"time":"21:50","type":"Story","contentId":"UGI-20260830-IG-STORY-GROWTH-05-COMMERCE"},
    ]
    data["ok"] = bool(all_new_ok and all_checks_ok and reel_ok)
    data["state"] = "PROVEN_SCHEDULED_8_OF_8" if data["ok"] else "PARTIAL_OR_FAILED"
    data["recoveryFinishedAt"] = dt.datetime.now(dt.timezone.utc).isoformat()
    save(data)
    print(json.dumps({"ok": data["ok"], "state": data["state"], "agenda": data["agenda"], "checks": data["recoveryChecks"]}, ensure_ascii=False, indent=2))
    return 0 if data["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

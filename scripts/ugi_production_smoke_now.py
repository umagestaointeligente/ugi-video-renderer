from __future__ import annotations

import datetime as dt
import json
import os
import time
from pathlib import Path
from typing import Any

import requests

WORKER = "https://lola-operacional-ugi.umagestaointeligente.workers.dev"
RECEIPT = Path("control-plane/smoke/receipts/production-smoke-latest.json")


class Client:
    def __init__(self, key: str) -> None:
        self.headers = {"x-lola-command-key": key, "accept": "application/json"}

    def get(self, path: str, timeout: int = 120) -> tuple[int, dict[str, Any]]:
        r = requests.get(WORKER + path, headers=self.headers, timeout=timeout)
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, {"ok": False, "raw": r.text[:2000]}

    def post(self, path: str, payload: dict[str, Any], timeout: int = 180) -> tuple[int, dict[str, Any]]:
        r = requests.post(WORKER + path, headers={**self.headers, "content-type": "application/json"}, json=payload, timeout=timeout)
        try:
            return r.status_code, r.json()
        except Exception:
            return r.status_code, {"ok": False, "raw": r.text[:2000]}


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def smoke_scenes(label: str) -> list[dict[str, Any]]:
    platforms = ("instagram", "tiktok", "youtube")
    def triplet(value: str) -> dict[str, str]:
        return {p: value for p in platforms}
    return [
        {"role":"hook","visual_intent":"gestor conferindo painel digital em ambiente de trabalho","pexels_query":"manager digital dashboard office","overlay":triplet(f"{label}: teste real"),"support":triplet("Publicação validada ponta a ponta"),"narration":triplet("Este é um teste operacional real da Uma Gestão Inteligente.")},
        {"role":"pain","visual_intent":"profissional vendo alertas de tarefas e sistema","pexels_query":"professional task alerts computer office","overlay":triplet("Agendar não basta"),"support":triplet("Precisamos provar a entrega"),"narration":triplet("Agendar não basta. O sistema precisa provar que a publicação foi entregue.")},
        {"role":"consequence","visual_intent":"fluxo digital com etapa pendente e verificação","pexels_query":"workflow verification technology office","overlay":triplet("Sem confirmação, sem sucesso"),"support":triplet("Fail closed"),"narration":triplet("Sem confirmação real, a operação não pode ser classificada como sucesso.")},
        {"role":"turn","visual_intent":"automação conectando etapas de um processo","pexels_query":"automation workflow business technology","overlay":triplet("Control Plane UGI"),"support":triplet("Render, QA, Buffer, readback"),"narration":triplet("O novo Control Plane conecta render, qualidade, Buffer e readback.")},
        {"role":"result","visual_intent":"painel de processo concluído com indicador verde","pexels_query":"successful workflow dashboard office","overlay":triplet("Evidência real"),"support":triplet("POST ID + sentAt"),"narration":triplet("Só consideramos concluído quando existe evidência real de entrega.")},
        {"role":"cta","visual_intent":"gestor finalizando tarefa no notebook","pexels_query":"manager completing task laptop office","overlay":triplet("Teste operacional UGI"),"support":triplet("Pode ser removido após a validação"),"narration":triplet("Teste operacional concluído.")},
    ]


def verify_external(url: str | None) -> dict[str, Any]:
    if not url:
        return {"attempted": False, "ok": False, "reason": "external_link_missing"}
    try:
        r = requests.get(url, timeout=30, allow_redirects=True, headers={"User-Agent":"Mozilla/5.0 UGI-Smoke/1.0"})
        return {"attempted": True, "ok": r.status_code < 500, "httpStatus": r.status_code, "finalUrl": r.url}
    except Exception as exc:
        return {"attempted": True, "ok": False, "error": str(exc)}


def wait_static_delivery(client: Client, draft_id: str, timeout_s: int = 420) -> dict[str, Any]:
    deadline = time.time() + timeout_s
    last: dict[str, Any] = {}
    while time.time() < deadline:
        _, data = client.get("/api/r45/static-publication-status?id=" + requests.utils.quote(draft_id, safe=""))
        last = data
        pub = data.get("publication") or {}
        status = str(pub.get("status") or "").lower()
        if status in {"sent", "published", "complete", "completed"} or pub.get("sentAt"):
            return data
        if status in {"error", "failed", "cancelled"}:
            return data
        time.sleep(10)
    return last


def wait_video_ready(client: Client, render_id: str, timeout_s: int = 1200) -> dict[str, Any]:
    deadline = time.time() + timeout_s
    last: dict[str, Any] = {}
    while time.time() < deadline:
        _, data = client.get("/api/video-result/" + requests.utils.quote(render_id, safe=""))
        last = data
        status = str(data.get("status") or "").lower()
        if data.get("ok") is True and data.get("allPlatformsReady") is True:
            return data
        if status in {"failed", "error", "cancelled"} or (data.get("ok") is False and data.get("errorClass")):
            return data
        time.sleep(12)
    return last


def wait_draft(client: Client, content_id: str, timeout_s: int = 300) -> dict[str, Any]:
    deadline = time.time() + timeout_s
    last: dict[str, Any] = {}
    while time.time() < deadline:
        _, data = client.get("/api/draft-lookup?content_id=" + requests.utils.quote(content_id, safe=""))
        last = data
        if data.get("ok") is True and data.get("found") is True and data.get("draftId"):
            return data
        time.sleep(6)
    return last


def wait_video_delivery(client: Client, draft_id: str, platform: str, timeout_s: int = 600) -> dict[str, Any]:
    deadline = time.time() + timeout_s
    last: dict[str, Any] = {}
    while time.time() < deadline:
        path = "/api/platform-publication-status?id=" + requests.utils.quote(draft_id, safe="") + "&platform=" + requests.utils.quote(platform, safe="")
        _, data = client.get(path)
        last = data
        pub = data.get("publication") or {}
        status = str(pub.get("status") or "").lower()
        if status in {"sent", "published", "complete", "completed"} or pub.get("sentAt"):
            return data
        if status in {"error", "failed", "cancelled"}:
            return data
        time.sleep(10)
    return last


def smoke_instagram(client: Client) -> dict[str, Any]:
    cid = "UGI-SMOKE-20260830-INSTAGRAM-R45"
    payload = {
        "source":"UGI-PRODUCTION-SMOKE",
        "type":"visual_post",
        "content_id":cid,
        "experiment_id":"UGI-PRODUCTION-SMOKE-20260830",
        "variant":"IG",
        "topic":"Publicação com evidência real",
        "objective":"provar execução end-to-end sem Lola 5.3",
        "hook":"AGENDAR NÃO BASTA.",
        "key_message":"A UGI só considera uma publicação concluída quando o sistema confirma que ela foi realmente entregue.",
        "instructions":"Peça visual limpa, humana e direta. Este é um smoke test real e temporário.",
        "cta":"Teste operacional UGI — pode ser removido após a validação.",
        "editorial_mode":"human_utility_first",
        "commercial_offer":False,
    }
    code, generated = client.post("/api/r45/generate", payload, 900)
    draft = generated.get("draft") or {}
    out: dict[str, Any] = {"platform":"instagram","contentId":cid,"generateHttp":code,"generation":generated,"draftId":draft.get("id")}
    if code != 200 or generated.get("ok") is not True or not draft.get("id"):
        out["ok"] = False; out["state"]="GENERATION_FAILED"; return out
    code, approval = client.post("/api/r45/static-approval", {"id":draft["id"],"decision":"approved"})
    out["approvalHttp"] = code; out["approval"] = approval
    if code != 200 or approval.get("ok") is not True:
        out["ok"] = False; out["state"]="APPROVAL_FAILED"; return out
    code, published = client.post("/api/r45/static-publish", {"id":draft["id"],"mode":"shareNow"})
    out["publishHttp"] = code; out["publish"] = published
    if code != 200 or published.get("ok") is not True:
        out["ok"] = False; out["state"]="PUBLISH_FAILED"; return out
    readback = wait_static_delivery(client, str(draft["id"]))
    pub = readback.get("publication") or {}
    out["readback"] = readback; out["externalProof"] = verify_external(pub.get("externalLink"))
    out["ok"] = bool(pub.get("bufferPostId")) and bool(pub.get("sentAt")) and str(pub.get("status") or "").lower() not in {"error","failed","cancelled"}
    out["state"] = "DELIVERED" if out["ok"] else "DELIVERY_UNPROVEN"
    return out


def dispatch_video_smoke(client: Client, platform: str) -> dict[str, Any]:
    cid = f"UGI-SMOKE-20260830-{platform.upper()}-R43"
    payload = {
        "title":f"UGI production smoke {platform}",
        "duration":"8",
        "content_id":cid,
        "experiment_id":"UGI-PRODUCTION-SMOKE-20260830",
        "variant":platform.upper(),
        "commercial_intent":"none",
        "scenes":smoke_scenes(platform.upper()),
        "smoke_test":True,
        "smoke_test_duration":4,
        "smoke_test_platform":platform,
        "cta":"Teste operacional UGI concluído.",
        "commercial_offer":False,
        "editorial_mode":"smoke_test",
    }
    code, dispatched = client.post("/api/video-render", payload, 180)
    return {"platform":platform,"contentId":cid,"dispatchHttp":code,"dispatch":dispatched,"renderId":dispatched.get("renderId")}


def finish_video_smoke(client: Client, state: dict[str, Any]) -> dict[str, Any]:
    platform = str(state["platform"])
    rid = str(state.get("renderId") or "")
    if not rid or (state.get("dispatch") or {}).get("ok") is not True or (state.get("dispatch") or {}).get("githubAccepted") is not True:
        state["ok"] = False; state["state"]="DISPATCH_FAILED"; return state
    video = wait_video_ready(client, rid)
    state["videoResult"] = video
    if video.get("ok") is not True or video.get("allPlatformsReady") is not True:
        state["ok"] = False; state["state"]="RENDER_UNPROVEN"; return state
    lookup = wait_draft(client, str(state["contentId"]))
    state["draftLookup"] = lookup
    draft_id = str(lookup.get("draftId") or "")
    state["draftId"] = draft_id
    if not draft_id:
        state["ok"] = False; state["state"]="DRAFT_UNPROVEN"; return state
    code, approval = client.post("/api/platform-approval", {"id":draft_id,"platform":platform,"decision":"approved"})
    state["approvalHttp"] = code; state["approval"] = approval
    if code != 200 or approval.get("ok") is not True:
        state["ok"] = False; state["state"]="APPROVAL_FAILED"; return state
    code, publish = client.post("/api/platform-publish", {"id":draft_id,"platform":platform,"mode":"shareNow"})
    state["publishHttp"] = code; state["publish"] = publish
    if code != 200 or publish.get("ok") is not True:
        state["ok"] = False; state["state"]="PUBLISH_FAILED"; return state
    readback = wait_video_delivery(client, draft_id, platform)
    state["readback"] = readback
    pub = readback.get("publication") or {}
    state["externalProof"] = verify_external(pub.get("externalLink"))
    state["ok"] = bool(pub.get("bufferPostId")) and bool(pub.get("sentAt")) and str(pub.get("status") or "").lower() not in {"error","failed","cancelled"}
    state["state"] = "DELIVERED" if state["ok"] else "DELIVERY_UNPROVEN"
    return state


def verify_existing_tiktok_1300(client: Client) -> dict[str, Any]:
    cid="UGI-20260830-TT-01-MEETINGS"
    _, lookup = client.get("/api/draft-lookup?content_id=" + requests.utils.quote(cid, safe=""))
    draft_id = str(lookup.get("draftId") or "")
    out={"platform":"tiktok","contentId":cid,"purpose":"verify_existing_13h_delivery","draftLookup":lookup,"draftId":draft_id}
    if not draft_id:
        out["ok"]=False; out["state"]="DRAFT_NOT_FOUND"; return out
    _, rb = client.get("/api/platform-publication-status?id=" + requests.utils.quote(draft_id,safe="") + "&platform=tiktok")
    out["readback"] = rb
    pub=rb.get("publication") or {}
    out["externalProof"] = verify_external(pub.get("externalLink"))
    out["ok"] = bool(pub.get("bufferPostId")) and (bool(pub.get("sentAt")) or str(pub.get("status") or "").lower() in {"sent","published","complete","completed"})
    out["state"] = "DELIVERED" if out["ok"] else "NOT_DELIVERED"
    return out


def main() -> int:
    key=os.getenv("UGI_WORKER_COMMAND_KEY") or os.getenv("UGI_LOLA_COMMAND_KEY") or ""
    if not key:
        raise SystemExit("UGI_WORKER_COMMAND_KEY_MISSING")
    client=Client(key)
    _, health=client.get("/api/health")
    _, channels=client.get("/api/buffer/channels")
    receipt: dict[str, Any]={"project":"UGI","component":"PRODUCTION-SMOKE-NOW","startedAt":now_iso(),"health":health,"channels":channels,"results":[]}
    if health.get("ok") is not True or channels.get("ok") is not True:
        receipt["ok"]=False; receipt["state"]="PRECHECK_FAILED"
    else:
        receipt["results"].append(verify_existing_tiktok_1300(client))
        receipt["results"].append(smoke_instagram(client))
        video_states=[dispatch_video_smoke(client,"tiktok"),dispatch_video_smoke(client,"youtube")]
        for item in video_states:
            receipt["results"].append(finish_video_smoke(client,item))
        smoke_results=[x for x in receipt["results"] if x.get("purpose") != "verify_existing_13h_delivery"]
        receipt["ok"]=all(x.get("ok") is True for x in smoke_results)
        receipt["state"]="PRODUCTION_PATHS_PROVEN" if receipt["ok"] else "DEGRADED"
    receipt["finishedAt"]=now_iso()
    RECEIPT.parent.mkdir(parents=True,exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,ensure_ascii=False,indent=2))
    return 0 if receipt.get("ok") else 1

if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import datetime as dt
import json
import os
import time
import urllib.parse
from pathlib import Path
from typing import Any

import requests

from ugi_anti_repeat_gate import EXCEPTION_STATE, TOPIC_HISTORY, load as load_history, topic_history_decision

BASE = "https://lola-operacional-ugi.umagestaointeligente.workers.dev"
EXPECTED_WORKER = "lola-v8-r45-4-story-video-buffer-direct-2026-09-03"
OUT = Path("control-plane/recovery/UGI_20260903_FIXED_AGENDA_RECEIPT.json")


def pmap(text: str) -> dict[str, str]:
    return {"instagram": text, "tiktok": text, "youtube": text}


def scene(role: str, visual: str, query: str, overlay: str, support: str, narration: str) -> dict[str, Any]:
    return {
        "role": role,
        "visual_intent": visual,
        "pexels_query": query,
        "overlay": pmap(overlay),
        "support": pmap(support),
        "narration": pmap(narration),
    }


def six_scenes(item: dict[str, Any]) -> list[dict[str, Any]]:
    h = item["hook"]
    fact = item["fact"]
    mech = item["mechanism"]
    take = item["takeaway"]
    src = item["source"]
    q = item["query"]
    return [
        scene("hook", item["visual"], q, item["overlay"], f"Fonte: {src}", h),
        scene("pain", item["visual2"], item["query2"], "O FATO", f"Fonte: {src}", fact),
        scene("consequence", item["visual3"], item["query3"], "POR QUE ISSO IMPORTA", "Leitura UGI", mech),
        scene("turn", item["visual4"], item["query4"], "A LEITURA DE GESTÃO", "Contexto antes de reação", item["turn"]),
        scene("result", item["visual5"], item["query5"], "O TESTE PRÁTICO", item["result_support"], take),
        scene("cta", item["visual6"], item["query6"], item["cta_overlay"], "UGI • Uma Gestão Inteligente", item["cta"]),
    ]


ITEMS: list[dict[str, Any]] = [
    {
        "contentId": "UGI-20260903-IG-STORY-1030-GOOGLE-ANTITRUST",
        "platform": "instagram", "dueAt": "2026-09-03T10:30:00-03:00",
        "title": "Google não foi dividido — mas a decisão ainda muda como pode competir",
        "topic_key": "google-adtech-antitrust-operating-freedom",
        "topic": "Google ad-tech antitrust e liberdade operacional",
        "event_or_case": "Google ad-tech antitrust ruling 2026-09-02",
        "management_thesis": "Uma empresa pode manter sua estrutura e ainda perder liberdade operacional quando remédios comportamentais mudam as regras de competição.",
        "primary_entities": ["Google"],
        "hook": "O Google não foi dividido. Mas isso não significa que nada mudou.",
        "fact": "A decisão evitou a ruptura estrutural, mas manteve restrições capazes de mudar como a empresa pode competir em publicidade digital.",
        "mechanism": "Para gestão, o ponto é simples: uma regra pode preservar a estrutura e ainda alterar incentivos, processos e liberdade de decisão.",
        "turn": "Não olhe só para a penalidade. Pergunte quais decisões operacionais passam a ter novas fronteiras.",
        "takeaway": "Quando a regra muda, mapeie decisão afetada, processo afetado, dono e risco antes de reagir.",
        "cta": "Na sua empresa, qual regra externa já mudou uma decisão interna?",
        "overlay": "NÃO HOUVE DIVISÃO. E AINDA ASSIM MUDOU.", "source": "Reuters",
        "cta_overlay": "REGRA NOVA = DECISÃO NOVA",
        "visual": "modern digital advertising operations with Google search and ad-tech context without fabricated screens", "query": "digital advertising technology office",
        "visual2": "realistic ad technology ecosystem and business operations", "query2": "digital marketing technology team",
        "visual3": "business rules and operational constraints visualized through real work", "query3": "business compliance operations team",
        "visual4": "executives reviewing operating choices with technology context", "query4": "executive decision technology office",
        "visual5": "manager mapping process risks and decisions", "query5": "manager process risk planning",
        "visual6": "clean modern management workspace closing frame", "query6": "modern management team office",
    },
    {
        "contentId": "UGI-20260903-IG-STORY-1100-BP-GOVERNANCE",
        "platform": "instagram", "dueAt": "2026-09-03T11:00:00-03:00",
        "title": "Quando líderes mudam em sequência, o problema deixa de ser só a cadeira",
        "topic_key": "bp-board-governance-leadership-stability",
        "topic": "BP governança e estabilidade de liderança",
        "event_or_case": "BP board governance changes 2026-09-02",
        "management_thesis": "Mudanças sucessivas de liderança ampliam a necessidade de continuidade de governança, clareza de prioridades e mecanismos de decisão.",
        "primary_entities": ["BP"],
        "hook": "Quando a liderança muda várias vezes, a pergunta deixa de ser apenas quem assume.",
        "fact": "Mudanças recentes na governança da BP voltaram a colocar estabilidade, direção estratégica e papel do conselho no centro da discussão.",
        "mechanism": "Trocas no topo podem acelerar correções, mas também quebrar continuidade, memória decisória e clareza de prioridade.",
        "turn": "Boa governança não depende de uma pessoa só. Ela preserva critérios, donos e ritos de decisão durante a transição.",
        "takeaway": "Teste se três coisas sobrevivem à troca de líder: prioridade, critério de decisão e responsabilidade explícita.",
        "cta": "Se o líder mudasse amanhã, o sistema continuaria funcionando?",
        "overlay": "QUANDO A TROCA VIRA SISTEMA", "source": "Reuters",
        "cta_overlay": "GOVERNANÇA PRECISA SOBREVIVER À TROCA",
        "visual": "energy company leadership and industrial operations without logos", "query": "energy company executives industrial operations",
        "visual2": "corporate board governance meeting realistic", "query2": "board governance meeting executives",
        "visual3": "leadership transition and team continuity", "query3": "leadership transition business team",
        "visual4": "executive governance process review", "query4": "executive governance process",
        "visual5": "management team checking priorities and ownership", "query5": "management priorities planning team",
        "visual6": "clean executive team collaboration closing frame", "query6": "executive team collaboration modern office",
    },
    {
        "contentId": "UGI-20260903-TT-1215-ANTHROPIC-RETAIL-AGENTS",
        "platform": "tiktok", "dueAt": "2026-09-03T12:15:00-03:00",
        "title": "A IA está deixando de só responder — ela já entra na jornada de compra",
        "topic_key": "anthropic-retail-agents-commerce-journey",
        "topic": "Anthropic agentes de varejo e jornada de compra",
        "event_or_case": "Anthropic retail agent blueprints 2026-09-02",
        "management_thesis": "Agentes de IA deslocam automação do apoio interno para etapas da jornada comercial, exigindo novos limites de decisão, dados e responsabilidade.",
        "primary_entities": ["Anthropic"],
        "hook": "A IA já começa a sair do chat e entrar no carrinho. O que muda para quem vende?",
        "fact": "A Anthropic apresentou blueprints de agentes voltados a varejistas e comerciantes para atuar em etapas da jornada de compra.",
        "mechanism": "Quando a IA passa de assistente para agente, ela deixa de só informar e começa a influenciar ação, seleção e fluxo comercial.",
        "turn": "A oportunidade cresce junto com a responsabilidade: dado, permissão e ponto de intervenção humana precisam ser definidos antes.",
        "takeaway": "Escolha uma etapa da jornada, defina o que o agente pode fazer, o que não pode e quando deve escalar para uma pessoa.",
        "cta": "Qual etapa da sua jornada de compra você automatizaria primeiro?",
        "overlay": "A IA JÁ CHEGA AO CARRINHO", "source": "Reuters",
        "cta_overlay": "AUTOMATIZE COM FRONTEIRA",
        "visual": "online shopping and AI assisted commerce realistic", "query": "online shopping ecommerce technology",
        "visual2": "retail digital commerce team", "query2": "ecommerce retail team technology",
        "visual3": "customer journey digital retail operations", "query3": "customer journey ecommerce operations",
        "visual4": "human oversight of automated commerce", "query4": "human oversight automation business",
        "visual5": "manager mapping ecommerce workflow", "query5": "ecommerce workflow planning manager",
        "visual6": "modern retail team closing frame", "query6": "modern retail team office",
    },
    {
        "contentId": "UGI-20260903-IG-1245-AI-PROFILE-TRANSPARENCY",
        "platform": "instagram", "dueAt": "2026-09-03T12:45:00-03:00",
        "title": "O alcance pode cair por causa de IA — e o ponto principal não é o algoritmo",
        "topic_key": "instagram-ai-generated-profile-transparency-distribution",
        "topic": "Instagram transparência de perfis gerados por IA e distribuição",
        "event_or_case": "Instagram AI-generated profiles recommendation transparency 2026-09",
        "management_thesis": "À medida que IA entra na produção de conteúdo, transparência passa a integrar governança de marca e estratégia de distribuição.",
        "primary_entities": ["Instagram", "Meta"],
        "hook": "O Instagram pode limitar distribuição de perfis de pessoas geradas por IA sem identificação adequada.",
        "fact": "A plataforma está reforçando transparência e elegibilidade de recomendação para perfis que usam pessoas geradas por IA.",
        "mechanism": "Quando IA entra na criação, disclosure deixa de ser detalhe jurídico e passa a afetar confiança, reputação e distribuição.",
        "turn": "A pergunta de gestão não é só 'posso usar IA?'. É: o público entende o que está vendo e quem responde por isso?",
        "takeaway": "Defina uma política simples: o que pode ser sintético, quando identificar e quem revisa antes de publicar.",
        "cta": "Sua política de IA inclui transparência ou só produtividade?",
        "overlay": "IA + ALCANCE: O DETALHE QUE MUDA TUDO", "source": "Instagram/Meta + The Verge",
        "cta_overlay": "TRANSPARÊNCIA TAMBÉM DISTRIBUI",
        "visual": "social media creator using phone and content tools realistic", "query": "social media creator phone content",
        "visual2": "content moderation and social media operations", "query2": "social media content moderation team",
        "visual3": "brand trust and digital content governance", "query3": "brand trust digital content team",
        "visual4": "marketing manager reviewing AI content", "query4": "marketing manager reviewing content",
        "visual5": "content policy checklist team", "query5": "content policy checklist team",
        "visual6": "modern creator workspace closing frame", "query6": "modern creator workspace",
    },
    {
        "contentId": "UGI-20260903-IG-STORY-1415-COST-OF-CAPITAL",
        "platform": "instagram", "dueAt": "2026-09-03T14:15:00-03:00",
        "title": "O petróleo sobe longe da sua empresa — o custo pode chegar no seu caixa",
        "topic_key": "oil-bonds-cost-of-capital-operating-impact",
        "topic": "Petróleo juros e custo de capital na operação",
        "event_or_case": "oil bond yields cost of capital 2026-09-02",
        "management_thesis": "Movimentos macro de energia e juros chegam à gestão por frete, capital de giro, investimento, preço e caixa.",
        "primary_entities": ["oil", "bonds"],
        "hook": "O petróleo pode subir longe da sua empresa. O impacto pode aparecer dentro do seu caixa.",
        "fact": "Movimentos em energia e juros alteram expectativas de inflação, custo financeiro e decisões de investimento.",
        "mechanism": "Para a operação, isso pode chegar por frete, fornecedores, capital de giro, preço e custo de financiar crescimento.",
        "turn": "Macroeconomia só vira gestão quando você conecta o indicador à linha do negócio que ele realmente move.",
        "takeaway": "Mapeie três sensibilidades: custo logístico, prazo de estoque e necessidade de capital de giro.",
        "cta": "Qual variável externa mais mexe no seu caixa hoje?",
        "overlay": "O IMPACTO CHEGA PELO CAIXA", "source": "Reuters",
        "cta_overlay": "MACRO SÓ IMPORTA QUANDO VIRA DECISÃO",
        "visual": "oil logistics and business finance realistic", "query": "oil logistics business finance",
        "visual2": "energy markets and business operations", "query2": "energy business operations",
        "visual3": "trucks logistics warehouse costs", "query3": "logistics warehouse trucks costs",
        "visual4": "manager reviewing cash flow operations", "query4": "manager cash flow operations",
        "visual5": "supply chain cost planning", "query5": "supply chain cost planning",
        "visual6": "clean finance operations team closing frame", "query6": "finance operations team office",
    },
    {
        "contentId": "UGI-20260903-YT-1630-HARRY-POTTER-LEGACY-BRAND",
        "platform": "youtube", "dueAt": "2026-09-03T16:30:00-03:00",
        "title": "Harry Potter voltou ao topo — como relançar uma marca que milhões já sentem que é deles",
        "topic_key": "harry-potter-hbo-legacy-brand-relaunch",
        "topic": "Harry Potter e gestão de marca legada",
        "event_or_case": "Harry Potter HBO teaser 2026-09",
        "management_thesis": "Relançar uma marca legada exige preservar códigos que sustentam familiaridade sem transformar nostalgia em imobilidade.",
        "primary_entities": ["Harry Potter", "HBO"],
        "hook": "Harry Potter voltou ao topo da conversa. O desafio da HBO não é só refazer uma história.",
        "fact": "O novo teaser reacendeu a atenção sobre uma franquia que já carrega décadas de memória, expectativa e identidade de fãs.",
        "mechanism": "Em marca legada, mudança demais rompe familiaridade; repetição demais impede um novo ciclo de crescimento.",
        "turn": "A gestão precisa separar o que é código essencial da marca do que pode ser atualizado para uma nova geração.",
        "takeaway": "Faça duas listas: três elementos que o público reconhece como essência e três experiências que precisam evoluir.",
        "cta": "Na sua marca, o que é essência — e o que virou apenas hábito?",
        "overlay": "MARCA LEGADA: MUDAR SEM ROMPER", "source": "HBO / Harry Potter official + radar YouTube",
        "cta_overlay": "PRESERVE O CÓDIGO. RENOVE A EXPERIÊNCIA.",
        "visual": "fantasy book franchise audience and cinema nostalgia without copyrighted footage", "query": "fantasy books cinema audience nostalgia",
        "visual2": "fans reacting to major entertainment launch", "query2": "fans entertainment launch audience",
        "visual3": "brand heritage products and audience memory", "query3": "brand heritage audience nostalgia",
        "visual4": "creative team balancing heritage and innovation", "query4": "creative team brand strategy innovation",
        "visual5": "brand strategy workshop essence evolution", "query5": "brand strategy workshop team",
        "visual6": "cinematic audience closing frame without franchise footage", "query6": "cinema audience cinematic closing",
    },
    {
        "contentId": "UGI-20260903-TT-1945-ANITTA-PORTFOLIO",
        "platform": "tiktok", "dueAt": "2026-09-03T19:45:00-03:00",
        "title": "Quando várias músicas do mesmo projeto aparecem juntas: hit ou arquitetura de portfólio?",
        "topic_key": "anitta-equilibrivm-portfolio-distribution",
        "topic": "Anitta portfólio distribuição e atenção",
        "event_or_case": "Anitta EQUILIBRIVM II TikTok Brazil demand proxy 2026-09",
        "management_thesis": "Um portfólio com colaborações e múltiplos pontos de entrada pode multiplicar distribuição e reduzir dependência de um único ativo.",
        "primary_entities": ["Anitta", "EQUILIBRIVM II"],
        "hook": "Quando várias faixas do mesmo projeto aparecem juntas no radar, talvez o produto não seja só uma música.",
        "fact": "Um proxy público de tendências no Brasil mostrou forte concentração de faixas de Anitta, enquanto o projeto combina gêneros e colaborações diferentes.",
        "mechanism": "Cada faixa cria um ponto de entrada. Colaborações ampliam adjacências e o portfólio distribui o risco de depender de um único hit.",
        "turn": "A lógica vale fora da música: um produto central pode ganhar alcance por versões, parceiros e portas de entrada distintas.",
        "takeaway": "Pergunte quantas portas reais levam hoje ao seu produto — e quantas dependem do mesmo canal.",
        "cta": "Seu negócio tem portfólio ou só vários itens competindo entre si?",
        "overlay": "HIT OU ARQUITETURA DE PORTFÓLIO?", "source": "proxy público TikTok BR + Universal Music",
        "cta_overlay": "MAIS PORTAS. MENOS DEPENDÊNCIA.",
        "visual": "music release portfolio social media audience without copyrighted music", "query": "music release social media audience",
        "visual2": "artist collaboration studio without identifiable celebrity", "query2": "music artist collaboration studio",
        "visual3": "multiple music tracks distribution concept real devices", "query3": "music streaming distribution phones",
        "visual4": "portfolio strategy team mapping channels", "query4": "portfolio strategy team channels",
        "visual5": "manager mapping product entry points", "query5": "product portfolio planning manager",
        "visual6": "social audience closing frame", "query6": "social media audience music",
    },
    {
        "contentId": "UGI-20260903-YT-2030-OPENAI-STOP-CONDITIONS",
        "platform": "youtube", "dueAt": "2026-09-03T20:30:00-03:00",
        "title": "OpenAI e o limite da autonomia: quando um agente precisa parar",
        "topic_key": "openai-autonomous-agent-stop-conditions",
        "topic": "OpenAI agentes autônomos e condições de parada",
        "event_or_case": "OpenAI automated shutdown capabilities 2026-09-02",
        "management_thesis": "Autonomia de agentes precisa nascer acompanhada de teto de permissão, monitoramento, escalonamento humano e condição explícita de parada.",
        "primary_entities": ["OpenAI"],
        "hook": "A OpenAI está desenvolvendo formas de desligar agentes automaticamente. A pergunta de gestão vem antes.",
        "fact": "A empresa disse a legisladores estar desenvolvendo capacidades de desligamento automático, monitoramento e controles de acesso para sistemas autônomos.",
        "mechanism": "Quanto mais ações um agente pode executar sem supervisão, maior a necessidade de fronteiras definidas antes do deploy.",
        "turn": "Autonomia útil não é ausência de controle. É liberdade operacional dentro de limites observáveis e reversíveis.",
        "takeaway": "Defina cinco itens: teto de permissão, ação monitorada, gatilho de escalonamento, dono humano e condição de parada.",
        "cta": "Antes de dar autonomia à IA, você já definiu como ela para?",
        "overlay": "QUEM DECIDE QUANDO A IA PARA?", "source": "Reuters",
        "cta_overlay": "AUTONOMIA PRECISA DE FRONTEIRA",
        "visual": "AI operations monitoring and safety controls realistic", "query": "artificial intelligence monitoring control room technology",
        "visual2": "autonomous software operations team", "query2": "AI software operations team",
        "visual3": "technology risk monitoring", "query3": "technology risk monitoring team",
        "visual4": "human oversight AI systems", "query4": "human oversight artificial intelligence",
        "visual5": "manager defining access controls", "query5": "access control governance manager",
        "visual6": "clean AI governance closing frame", "query6": "AI governance team modern office",
    },
]


class Client:
    def __init__(self, key: str):
        self.h = {"x-lola-command-key": key, "accept": "application/json", "content-type": "application/json"}

    def get(self, path: str, timeout: int = 90) -> dict[str, Any]:
        r = requests.get(BASE + path, headers=self.h, timeout=timeout)
        try: return r.json()
        except Exception: return {"ok": False, "http": r.status_code, "raw": r.text[:1200]}

    def post(self, path: str, payload: dict[str, Any], timeout: int = 180) -> dict[str, Any]:
        r = requests.post(BASE + path, headers=self.h, json=payload, timeout=timeout)
        try: return r.json()
        except Exception: return {"ok": False, "http": r.status_code, "raw": r.text[:1200]}


def due_match(a: str | None, b: str) -> bool:
    if not a: return False
    try:
        x = dt.datetime.fromisoformat(a.replace("Z", "+00:00")).astimezone(dt.timezone.utc)
        y = dt.datetime.fromisoformat(b.replace("Z", "+00:00")).astimezone(dt.timezone.utc)
        return abs((x-y).total_seconds()) <= 90
    except Exception:
        return False


def anti_repeat(item: dict[str, Any], history: dict[str, Any]) -> dict[str, Any]:
    cmd = {
        "platform": item["platform"],
        "topic_key": item["topic_key"],
        "topic": item["topic"],
        "title": item["title"],
        "event_or_case": item["event_or_case"],
        "management_thesis": item["management_thesis"],
        "primary_entities": item["primary_entities"],
        "scenes": six_scenes(item),
    }
    decision, reasons, matches = topic_history_decision(item["contentId"], cmd, history)
    return {"pass": decision in {"ANTI_REPEAT_PASS", EXCEPTION_STATE}, "decision": decision, "reasons": reasons, "matches": matches}


def main() -> int:
    key = os.environ.get("UGI_WORKER_COMMAND_KEY") or os.environ.get("UGI_LOLA_COMMAND_KEY") or ""
    if not key: raise SystemExit("UGI key missing")
    c = Client(key)

    # Wait for the live worker recovery deployment so this run cannot silently publish an IG Story as a Reel.
    health = {}
    for _ in range(60):
        health = c.get("/api/health")
        if health.get("ok") is True and health.get("version") == EXPECTED_WORKER:
            break
        time.sleep(5)
    if health.get("version") != EXPECTED_WORKER:
        raise SystemExit(f"WORKER_RECOVERY_NOT_LIVE:{health}")

    history = load_history(TOPIC_HISTORY)
    receipt: dict[str, Any] = {
        "project": "UGI", "date": "2026-09-03", "publisher": "BUFFER",
        "workerVersion": health.get("version"), "results": [],
        "createdAt": dt.datetime.now(dt.timezone.utc).isoformat(),
    }

    active: dict[str, dict[str, Any]] = {}
    hard_fail = False

    # Dispatch all clean renders first, so GitHub can work concurrently.
    for item in ITEMS:
        gate = anti_repeat(item, history)
        row = {"contentId": item["contentId"], "platform": item["platform"], "dueAt": item["dueAt"], "antiRepeat": gate}
        if not gate["pass"]:
            row.update({"ok": False, "state": gate["decision"]})
            receipt["results"].append(row); hard_fail = True; continue

        scenes = six_scenes(item)
        payload = {
            "title": item["title"], "duration": "45", "content_id": item["contentId"],
            "experiment_id": "UGI-20260903-RECOVERY", "variant": "EDITORIAL_FIXED_AGENDA",
            "commercial_intent": "none", "scenes": scenes, "smoke_test": False,
            "cta": item["cta"], "commercial_offer": False,
            "copy_lock": {"enabled": True, "mode": "exact", "strict": True},
            "exact_copy": {"enabled": True},
            "editorial_mode": "instagram_story" if "-IG-STORY-" in item["contentId"] else "platform_native_management_explainer",
        }
        dispatch = c.post("/api/video-render", payload, timeout=150)
        rid = str(dispatch.get("renderId") or "")
        draft = str(dispatch.get("approvalDraftId") or "")
        row.update({"renderId": rid or None, "draftId": draft or None, "githubAccepted": dispatch.get("githubAccepted")})
        if not (dispatch.get("ok") is True and dispatch.get("githubAccepted") is True and rid and draft):
            row.update({"ok": False, "state": "RENDER_DISPATCH_FAILED", "diagnostic": dispatch})
            receipt["results"].append(row); hard_fail = True; continue
        active[item["contentId"]] = {"item": item, "row": row, "renderId": rid, "draftId": draft}

    # Poll all dispatched renders together. Publish each as soon as its media is proven ready.
    deadline = time.time() + 22 * 60
    pending = set(active)
    while pending and time.time() < deadline:
        for cid in list(pending):
            state = active[cid]; item = state["item"]; row = state["row"]
            vr = c.get("/api/video-result/" + urllib.parse.quote(state["renderId"]), timeout=90)
            asset = ((vr.get("assets") or {}).get(item["platform"]) or {})
            ready = vr.get("ok") is True and vr.get("allPlatformsReady") is True and asset.get("ready") is True and bool(asset.get("videoUrl"))
            if not ready:
                status = str(vr.get("status") or "").lower()
                if status in {"failed", "error", "cancelled"}:
                    row.update({"ok": False, "state": "RENDER_FAILED", "diagnostic": vr})
                    receipt["results"].append(row); pending.remove(cid); hard_fail = True
                continue

            if vr.get("semanticValidationRequired") is True and ((vr.get("semanticValidation") or {}).get("pass")) is not True:
                row.update({"ok": False, "state": "SEMANTIC_QA_FAIL"}); receipt["results"].append(row); pending.remove(cid); hard_fail = True; continue
            if ((vr.get("copyLock") or {}).get("enabled")) is True and ((vr.get("copyLockValidation") or {}).get("pass")) is not True:
                row.update({"ok": False, "state": "COPY_LOCK_QA_FAIL"}); receipt["results"].append(row); pending.remove(cid); hard_fail = True; continue

            draft_id = str(vr.get("approvalDraftId") or state["draftId"])
            elig = c.get("/api/platform-publication-eligibility/" + urllib.parse.quote(draft_id), timeout=90)
            ps = ((elig.get("platformStates") or {}).get(item["platform"]) or {})
            active_id = str(ps.get("bufferPostId") or "")
            active_status = str(ps.get("publicationStatus") or "").lower()

            if active_id and active_status not in {"error", "cancelled"}:
                rb = c.get("/api/platform-publication-status?id=" + urllib.parse.quote(draft_id) + "&platform=" + urllib.parse.quote(item["platform"]), timeout=90)
            else:
                if str(ps.get("approvalStatus") or "").lower() != "approved":
                    ap = c.post("/api/platform-approval", {"id": draft_id, "platform": item["platform"], "decision": "approved"}, timeout=90)
                    if ap.get("ok") is not True:
                        row.update({"ok": False, "state": "APPROVAL_FAIL", "diagnostic": ap}); receipt["results"].append(row); pending.remove(cid); hard_fail = True; continue
                pub = c.post("/api/platform-publish", {"id": draft_id, "platform": item["platform"], "mode": "customScheduled", "dueAt": item["dueAt"]}, timeout=120)
                if pub.get("ok") is not True:
                    row.update({"ok": False, "state": "BUFFER_MUTATION_FAIL", "diagnostic": pub}); receipt["results"].append(row); pending.remove(cid); hard_fail = True; continue
                rb = c.get("/api/platform-publication-status?id=" + urllib.parse.quote(draft_id) + "&platform=" + urllib.parse.quote(item["platform"]), timeout=90)

            publication = rb.get("publication") or {}
            pass_rb = rb.get("ok") is True and bool(publication.get("bufferPostId")) and str(publication.get("status") or "").lower() == "scheduled" and due_match(publication.get("dueAt"), item["dueAt"])
            row.update({
                "ok": pass_rb, "state": "PROVEN_SCHEDULED" if pass_rb else "READBACK_FAILED",
                "draftId": draft_id, "bufferPostId": publication.get("bufferPostId"),
                "bufferStatus": publication.get("status"), "dueAtReadback": publication.get("dueAt"),
                "externalLink": publication.get("externalLink"), "readbackPass": pass_rb,
                "audioAssetBytes": asset.get("videoBytes"), "audioRequired": True if "-IG-STORY-" in cid else None,
            })
            if not pass_rb: hard_fail = True
            receipt["results"].append(row); pending.remove(cid)

        if pending: time.sleep(15)

    for cid in pending:
        state = active[cid]; row = state["row"]
        row.update({"ok": False, "state": "RENDER_TIMEOUT"}); receipt["results"].append(row); hard_fail = True

    receipt["ok"] = not hard_fail and all(x.get("ok") is True for x in receipt["results"])
    receipt["completedAt"] = dt.datetime.now(dt.timezone.utc).isoformat()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 0 if receipt["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())

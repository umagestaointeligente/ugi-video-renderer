# UGI render-reel.py — R43.8.0 DYNAMIC SCENES
# SUBSTITUA SOMENTE o bloco atual que começa em:
#
# SCENES = [
#
# e termina logo antes de:
#
# def run(cmd: list[str | Path]) -> None:
#
# por TODO o bloco abaixo.
#
# Nenhuma outra função do renderer precisa ser removida.

VIDEO_SCENES_JSON = (os.getenv("VIDEO_SCENES_JSON") or "").strip()
VIDEO_ALLOW_LEGACY_SCENES = (
    os.getenv("VIDEO_ALLOW_LEGACY_SCENES") or "false"
).strip().lower() in {"1", "true", "yes", "on"}

def _require_scene_text(value, field: str) -> str:
    value = str(value or "").strip()
    if not value:
        raise RuntimeError(f"R43.8.0 campo obrigatório ausente: {field}")
    return value

def _platform_text_map(value, field: str, index: int) -> dict:
    if not isinstance(value, dict):
        raise RuntimeError(
            f"R43.8.0 {field} da cena {index} precisa ser objeto."
        )

    out = {}
    for platform in ("instagram", "tiktok", "youtube"):
        out[platform] = _require_scene_text(
            value.get(platform),
            f"scene[{index}].{field}.{platform}",
        )
    return out

def load_dynamic_scenes() -> list[SceneTemplate]:
    if not VIDEO_SCENES_JSON:
        raise RuntimeError(
            "R43.8.0 FAIL-CLOSED: VIDEO_SCENES_JSON é obrigatório. "
            "O renderer legado hardcoded foi desativado."
        )

    try:
        payload = json.loads(VIDEO_SCENES_JSON)
    except Exception as exc:
        raise RuntimeError(
            f"R43.8.0 FAIL-CLOSED: VIDEO_SCENES_JSON inválido: {exc}"
        ) from exc

    scenes_raw = payload.get("scenes") if isinstance(payload, dict) else payload

    if not isinstance(scenes_raw, list):
        raise RuntimeError(
            "R43.8.0 FAIL-CLOSED: payload não contém array scenes."
        )

    if not 4 <= len(scenes_raw) <= 10:
        raise RuntimeError(
            f"R43.8.0 quantidade de cenas inválida: {len(scenes_raw)}."
        )

    allowed_roles = {
        "hook",
        "pain",
        "consequence",
        "turn",
        "result",
        "cta",
    }

    scenes = []

    for index, item in enumerate(scenes_raw, start=1):
        if not isinstance(item, dict):
            raise RuntimeError(
                f"R43.8.0 cena {index} precisa ser objeto."
            )

        role = _require_scene_text(
            item.get("role"),
            f"scene[{index}].role",
        )

        if role not in allowed_roles:
            raise RuntimeError(
                f"R43.8.0 role inválido na cena {index}: {role}"
            )

        scenes.append(
            SceneTemplate(
                role=role,
                visual_intent=_require_scene_text(
                    item.get("visual_intent"),
                    f"scene[{index}].visual_intent",
                ),
                pexels_query=_require_scene_text(
                    item.get("pexels_query"),
                    f"scene[{index}].pexels_query",
                ),
                overlay=_platform_text_map(
                    item.get("overlay"),
                    "overlay",
                    index,
                ),
                support=_platform_text_map(
                    item.get("support"),
                    "support",
                    index,
                ),
                narration=_platform_text_map(
                    item.get("narration"),
                    "narration",
                    index,
                ),
            )
        )

    if len(scenes) == 6:
        expected = [
            "hook",
            "pain",
            "consequence",
            "turn",
            "result",
            "cta",
        ]
        actual = [scene.role for scene in scenes]

        if actual != expected:
            raise RuntimeError(
                "R43.8.0 ordem narrativa inválida: "
                + ">".join(actual)
            )

    canonical = json.dumps(
        scenes_raw,
        ensure_ascii=False,
        sort_keys=True,
    ).lower()

    forbidden = [
        "tudo passa por você",
        "tudo depende de você",
        "o líder vira gargalo",
        "você virou o gargalo",
        "autonomia com direção",
        "mais autonomia. mais execução",
    ]

    # O Trial 03 é o smoke test semântico do incidente real.
    cid = CONTENT_ID.lower()
    if "trial03" in cid or "1945" in cid:
        hits = [
            phrase
            for phrase in forbidden
            if phrase in canonical
        ]
        if hits:
            raise RuntimeError(
                "LEGACY_RENDERER_CONTENT_LEAK_DETECTED: "
                + ", ".join(hits)
            )

    return scenes

SCENES = load_dynamic_scenes()

from pathlib import Path

REC = Path('docs/LSI_RECOVERY_CURRENT.md')
REL = Path('career360/releases/MASTER_PILOT_1_0_CLARITY_UI_V16_2026-09-06.md')

OLD_APP_M = 'd3279ea45b3d3bb9f1686249199d2a46d34eaa2b'
NEW_APP_M = '541f962629ed5c3479972f9192401ce2fdf7c077'
OLD_BUNDLE = '239357f0623683bae362a1dd3f122891cdd2d157'
NEW_BUNDLE = 'fc1d20bd73bb48ca77e9e1d522baf6196933b961'
OLD_DEPLOY = 'a60be7807469a42653b9a6668fad1de01071d9e0'
NEW_DEPLOY = '85afb95087a706dc8bca5d99555740b4bc5ed0da'
OLD_RUN = '34007281162'
NEW_RUN = '34008976104'
OLD_JOB = '101416713004'
NEW_JOB = '101421295169'


def replace_required(text, old, new, label, minimum=1):
    count = text.count(old)
    if count < minimum:
        raise SystemExit(f'{label}: expected at least {minimum}, found {count}')
    return text.replace(old, new)


def update_recovery():
    s = REC.read_text()
    s = replace_required(s, OLD_APP_M, NEW_APP_M, 'Recovery app-m')
    s = replace_required(s, OLD_BUNDLE, NEW_BUNDLE, 'Recovery bundle')
    s = replace_required(s, OLD_DEPLOY, NEW_DEPLOY, 'Recovery deploy workflow')
    s = replace_required(s, OLD_RUN, NEW_RUN, 'Recovery smoke run')
    s = replace_required(s, OLD_JOB, NEW_JOB, 'Recovery smoke job')

    anchor = '- `V16_TOUCH_TARGET_POLICY=44PX`;\n'
    if '- `V16_TRUTHFUL_STATUS_POLICY=PASS`;\n' not in s:
        if anchor not in s:
            raise SystemExit('Recovery truthful evidence anchor missing')
        s = s.replace(anchor, anchor + '- `V16_TRUTHFUL_STATUS_POLICY=PASS`;\n', 1)

    hardening_anchor = '''Hardening final antes de promoção:\n- atalhos do agente >=44 px;\n- `Atualizar` >=44 px;\n- `Ok` >=44 px;\n- padding do alerta ajustado para evitar colisão com a ação.\n'''
    hardening_new = '''Hardening final antes de promoção:\n- atalhos do agente >=44 px;\n- `Atualizar` >=44 px;\n- `Ok` >=44 px;\n- padding do alerta ajustado para evitar colisão com a ação;\n- badge sintético `Trabalhando` removido do cabeçalho do agente;\n- status proativo compactado somente a partir do texto de runtime (`Ativo`, `Atualizando`, `Pausado`, `Atenção` ou `Status`);\n- onboarding e suporte com copy reduzida, sem remover guardrails de privacidade/confirmacao;\n- foco visível para teclado e `prefers-reduced-motion` respeitado.\n'''
    if hardening_anchor in s:
        s = s.replace(hardening_anchor, hardening_new, 1)
    elif 'badge sintético `Trabalhando` removido' not in s:
        raise SystemExit('Recovery hardening anchor missing')

    old_gate = '''## 13. Gate único que falta para promoção V15\n\nUma destas condições precisa existir sem expor credenciais no chat:\n\nA. `VERCEL_TOKEN` válido cadastrado como repository secret no GitHub; OU\nB. Remote Desktop Commander conectado a um dispositivo já autenticado na Vercel, permitindo configurar o secret/deploy sem revelar credencial; OU\nC. Browser Connector autenticado na Vercel com acesso suficiente para criar/configurar a credencial/política necessária.\n\nAssim que uma dessas condições existir, a rota canônica já permite executar sem nova arquitetura:\n1. criar Preview project-scoped;\n2. HTTP/pin smoke;\n3. promover o MESMO Preview;\n4. confirmar alias oficial;\n5. checar runtime errors;\n6. Android autenticado;\n7. Photo Studio gerar/comparar/aceitar/reverter;\n8. marcar `UI_V15=LIVE` e `PHOTO_STUDIO_MOBILE_FALLBACK_HARDENING=LIVE` somente após prova.\n'''
    new_gate = '''## 13. Gate único que falta para promoção V15/V16\n\nUma destas condições precisa existir sem expor credenciais no chat:\n\nA. `VERCEL_TOKEN` válido cadastrado como repository secret no GitHub; OU\nB. Browser Connector autenticado na Vercel com acesso suficiente para configurar/autorizar a rota project-scoped; OU\nC. novo OAuth Device Flow em runner efêmero privado, com autorização humana explícita e identidade Vercel validada antes do deploy.\n\nGuardrail absoluto:\n`REMOTE_DESKTOP_COMMANDER=PROHIBITED_BY_USER_FOR_LSI_CAREER360`.\nNão sugerir nem reutilizar Remote Desktop como rota de promoção.\n\nAssim que uma condição válida existir, a rota canônica já permite executar sem nova arquitetura:\n1. criar Preview project-scoped;\n2. HTTP/pin smoke de `app-k`, `app-l` e `app-m`;\n3. promover o MESMO Preview;\n4. confirmar alias oficial;\n5. checar runtime errors;\n6. Android autenticado;\n7. Photo Studio gerar/comparar/aceitar/reverter;\n8. marcar V15/V16 e o hardening móvel como LIVE somente após prova.\n'''
    if old_gate in s:
        s = s.replace(old_gate, new_gate, 1)
    elif '## 13. Gate único que falta para promoção V15/V16' not in s:
        raise SystemExit('Recovery gate section anchor missing')

    old_last = '`LAST_VERIFIED_CHANGE=V15_BROWSER_REGRESSION_PASS_APP_L_428364_APP_K_6DF7B4_BUNDLE_ECE158_DEPLOY_PIPELINE_64FE2_PREVIEW_THEN_PROMOTE_EXACT_ARTIFACT_VERCEL_CLI_59_11_7_OIDC_PROBE_HTTP400_REMOVED_PRODUCTION_STILL_V14_READY_NO_RUNTIME_ERRORS_AUTH_HANDOFF_REQUIRED`'
    new_last = '`LAST_VERIFIED_CHANGE=V16_TRUTHFUL_UI_BROWSER_PASS_APP_M_541F962_APP_L_428364_APP_K_6DF7B4_BUNDLE_FC1D20B_SMOKE_RUN_34008976104_JOB_101421295169_DEPLOY_GATE_85AFB95_PRODUCTION_STILL_V14_NOT_PROMOTED_AUTH_REQUIRED_REMOTE_DESKTOP_PROHIBITED`'
    if old_last in s:
        s = s.replace(old_last, new_last, 1)
    elif new_last not in s:
        raise SystemExit('Recovery LAST_VERIFIED_CHANGE anchor missing')

    REC.write_text(s)


def update_release():
    s = REL.read_text()
    s = replace_required(s, OLD_APP_M, NEW_APP_M, 'Release app-m')
    s = replace_required(s, OLD_BUNDLE, NEW_BUNDLE, 'Release bundle')
    s = replace_required(s, OLD_RUN, NEW_RUN, 'Release smoke run')
    s = replace_required(s, OLD_JOB, NEW_JOB, 'Release smoke job')

    s = s.replace('- working-state indicator;\n', '- no synthetic real-time working badge;\n', 1)
    s = s.replace('- active state becomes `Trabalhando`;\n', '- status is compacted from runtime-originated text; no fixed `Trabalhando` claim is injected;\n', 1)

    visual_anchor = '''## Mobile touch hardening\n'''
    truthful = '''## Truthful status + secondary UX hardening\n\nBefore promotion, V16 received an additional truthfulness/accessibility pass:\n- removed the fixed `Trabalhando` badge from the My Agent header;\n- proactive status now compacts only runtime-originated state into `Ativo`, `Atualizando`, `Pausado`, `Atenção` or neutral `Status`;\n- onboarding headings and secondary copy were shortened without removing privacy, salary or confirmation guardrails;\n- Support became `Ajuda`, with a shorter problem prompt and action;\n- keyboard focus visibility was strengthened;\n- `prefers-reduced-motion` is respected;\n- agent question input has an explicit accessible label.\n\nPolicy:\n`V16_TRUTHFUL_STATUS_POLICY=PASS`\n\n'''
    if truthful.strip() not in s:
        if visual_anchor not in s:
            raise SystemExit('Release truthfulness insertion anchor missing')
        s = s.replace(visual_anchor, truthful + visual_anchor, 1)

    evidence_anchor = '- `V16_TOUCH_TARGET_POLICY=44PX`\n'
    if '- `V16_TRUTHFUL_STATUS_POLICY=PASS`\n' not in s:
        if evidence_anchor not in s:
            raise SystemExit('Release evidence anchor missing')
        s = s.replace(evidence_anchor, evidence_anchor + '- `V16_TRUTHFUL_STATUS_POLICY=PASS`\n', 1)

    s = s.replace('- `app-m@d3279ea...`', '- `app-m@541f962...`')
    REL.write_text(s)


update_recovery()
update_release()
print('V16_CANONICAL_DOC_SEAL=PASS')

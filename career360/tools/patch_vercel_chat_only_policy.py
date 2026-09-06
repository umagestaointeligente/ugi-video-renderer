from pathlib import Path
import re

P=Path('docs/LSI_RECOVERY_CURRENT.md')
s=P.read_text()

s=s.replace('## 9. Deploy Vercel — pipeline final pronto / autenticação externa ausente','## 9. Deploy Vercel — pipeline final pronto / acesso somente pelo ChatGPT')

anchor='Guardrail:\n`UNSCOPED_VERCEL_DEPLOY=DO_NOT_USE`.\n'
insert='Guardrail:\n`UNSCOPED_VERCEL_DEPLOY=DO_NOT_USE`.\n`VERCEL_ACCESS_POLICY=CHATGPT_CONNECTOR_ONLY`.\n`EXTERNAL_VERCEL_AUTH=PROHIBITED_BY_USER`.\n`VERCEL_DEVICE_FLOW=PROHIBITED`.\n`VERCEL_MANUAL_TOKEN_ROUTE=PROHIBITED`.\n`PRODUCTOS_VERCEL_AUTH_ROUTE=PROHIBITED`.\n`REMOTE_DESKTOP_COMMANDER=PROHIBITED_BY_USER_FOR_LSI_CAREER360`.\n'
if anchor not in s:
    raise SystemExit('section 9 guardrail anchor missing')
s=s.replace(anchor,insert,1)

old='''Estado:\n`VERCEL_DEPLOY_ROUTE=PREVIEW_PROMOTE_PIPELINE_READY_WAITING_AUTH`\n`VERCEL_TOKEN=NOT_CONFIGURED`\n`V15_PREVIEW_DEPLOYED=NO`\n`V15_PRODUCTION_DEPLOYED=NO`\n`V16_PREVIEW_DEPLOYED=NO`\n`V16_PRODUCTION_DEPLOYED=NO`\n`DEPLOY_AUTH_BLOCKER=EXTERNAL_AUTHENTICATED_SESSION_OR_SECRET_REQUIRED`\n\nSessões alternativas verificadas neste gate:\n- Remote Desktop Commander = `PROIBIDO` por decisão do usuário; não sugerir esta rota novamente;\n- Opera Browser Connector = browser desconectado.\n\nNão criar token fictício, não extrair magic link/2FA de e-mail, não expor token em código/repositório/chat e não usar deploy sem escopo.\n'''
new='''Estado:\n`VERCEL_DEPLOY_ROUTE=PROJECT_SCOPED_PIPELINE_READY_BUT_CHAT_CONNECTOR_MUTATION_UNSCOPED`\n`V15_PREVIEW_DEPLOYED=NO`\n`V15_PRODUCTION_DEPLOYED=NO`\n`V16_PREVIEW_DEPLOYED=NO`\n`V16_PRODUCTION_DEPLOYED=NO`\n`DEPLOY_BLOCKER=IN_CHAT_VERCEL_DEPLOY_ACTION_DOES_NOT_EXPOSE_PROJECT_ID`\n\nRegra operacional absoluta do usuário:\n- Vercel só pode ser acessada/operada pelo conector Vercel dentro deste ChatGPT;\n- não usar login externo, OAuth Device Flow, navegador externo, token manual, ProductOS como ponte de autenticação ou Remote Desktop;\n- o conector interno já prova leitura do projeto `prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP`, deployments e runtime;\n- a ação interna de deploy atualmente exposta é zero-argument e não permite selecionar `projectId`; como a conta tem múltiplos projetos, `deploy_to_vercel` permanece proibido até existir escopo determinístico dentro do Chat.\n\nNão criar token fictício, não extrair magic link/2FA de e-mail, não expor token em código/repositório/chat e não usar deploy sem escopo.\n'''
if old not in s:
    raise SystemExit('old deploy state block missing')
s=s.replace(old,new,1)

start=s.index('## 13. Gate único que falta para promoção V15/V16')
end=s.index('## 14. Próximos gates depois da V15 LIVE',start)
new13='''## 13. Gate único que falta para promoção V15/V16\n\nA promoção só pode acontecer **dentro deste ChatGPT**, pelo conector Vercel, com escopo determinístico para:\n- Team `team_ZJys00FTE2kK9yVtsqH5fHyF`;\n- Project `prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP`.\n\nEstado atual do conector:\n- leitura project-scoped = `PROVEN`;\n- `get_project`, `list_deployments`, `web_fetch_vercel_url` e runtime errors = disponíveis;\n- mutação de deploy exposta = `deploy_to_vercel()` sem argumentos;\n- seleção explícita de `projectId` para a mutação = `NOT_EXPOSED`;\n- portanto `UNSCOPED_VERCEL_DEPLOY=DO_NOT_USE`.\n\nRotas proibidas por decisão do usuário:\n`EXTERNAL_BROWSER_AUTH=PROHIBITED`\n`OAUTH_DEVICE_FLOW=PROHIBITED`\n`MANUAL_VERCEL_TOKEN=PROHIBITED`\n`PRODUCTOS_VERCEL_AUTH_BRIDGE=PROHIBITED`\n`REMOTE_DESKTOP_COMMANDER=PROHIBITED`\n\nQuando o conector interno expuser deploy/promoção project-scoped, executar sem nova arquitetura:\n1. criar Preview no projeto oficial;\n2. validar HTTP + pins de `app-k`, `app-l` e `app-m`;\n3. promover o MESMO Preview;\n4. confirmar alias oficial;\n5. checar runtime errors;\n6. Android autenticado;\n7. Photo Studio gerar/comparar/aceitar/reverter;\n8. marcar V15/V16 e o hardening móvel como LIVE somente após prova.\n\n'''
s=s[:start]+new13+s[end:]

pat=r'`LAST_VERIFIED_CHANGE=[^`]+`'
m=re.findall(pat,s)
if len(m)!=1:
    raise SystemExit('LAST_VERIFIED_CHANGE cardinality invalid')
last='`LAST_VERIFIED_CHANGE=V16_RUNTIME_TRUTH_BROWSER_PASS_APP_M_3CD06D1_APP_L_428364_APP_K_6DF7B4_BUNDLE_AC8A46F_SMOKE_RUN_34009190125_JOB_101421875198_VERCEL_CHATGPT_ONLY_EXTERNAL_AUTH_PROHIBITED_INTERNAL_DEPLOY_UNSCOPED_PRODUCTION_STILL_V14_NOT_PROMOTED`'
s=re.sub(pat,last,s,count=1)

P.write_text(s)
print('VERCEL_CHAT_ONLY_POLICY_PATCH=PASS')

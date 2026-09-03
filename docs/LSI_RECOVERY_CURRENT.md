# LSI — RECOVERY CURRENT

Status: CURRENT / AUTORITATIVO PARA HANDOFF
Atualizado: 2026-09-03 BRT
Âncora humana: `Recovery LSI`
Alias técnico interno: `LSI::RECOVERY::CURRENT`

## 0. Estado global

`LSI_RECOVERY=TRUE`
`CURRENT_FOCUS=LSI_CAREER_360_MASTER_PILOT_1_0`
`CURRENT_STATUS=MASTER_PILOT_READY_FOR_MASTER_USE`
`VERIFIED_REVENUE=R$0,00` para a lógica de incubação; reconfirmar antes de decisão monetária.

## 1. Localização canônica

Repository: `umagestaointeligente/ugi-video-renderer`
Fonte canônica de código/documentação: `main`
PR #25: MERGED
Merge commit: `1347d4ec4c3221e20fc7f9ce443b86141de1b533`

Backend dedicado:
- Supabase project: `LSI Career 360`
- project ref: `nxjdnzdxclszqyqrkwdk`
- região: `sa-east-1`
- custo confirmado na criação: `R$0/mês`.

Frontend oficial:
`https://lsi-career-360.vercel.app`

Projeto Vercel:
- nome: `lsi-career-360`
- project id: `prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP`
- plano da equipe: Hobby
- production deployment verificado: READY.

Rota antiga:
`https://nxjdnzdxclszqyqrkwdk.supabase.co/functions/v1/career-app`

A rota Supabase NÃO é mais a superfície web. O gateway Supabase força HTML de Edge Function para `text/plain`/sandbox. A função `career-app` foi convertida em redirect para o frontend Vercel.

## 2. Produto entregue

Master Pilot 1.0 funcional com:
- app web responsivo;
- Auth individual;
- papel `master` automático por hash SHA-256 de e-mail autorizado no backend;
- currículo PDF/DOCX;
- quarentena privada;
- validação profunda + parser determinístico;
- rascunho com confirmação humana;
- Proteção de Carreira;
- Matching V1 explicável;
- cadastro/análise manual de oportunidade no piloto;
- radar de oportunidades;
- Meu Agente zero-cash;
- SAC `Resolver agora`;
- incidentes/checkpoints;
- Painel Mestre agregado;
- retenção/cleanup do arquivo bruto;
- audit trail seguro.

## 3. Frontend — correção operacional 2026-09-03

Problema observado em Android/Chrome:
- URL Supabase mostrava o HTML bruto em tela.

Diagnóstico provado:
- Edge Function devolvia HTML correto;
- gateway Supabase sobrescrevia resposta para `content-type: text/plain` e CSP sandbox;
- portanto Supabase Edge não deve hospedar a UI.

Correção:
- frontend separado do backend;
- deploy estático em Vercel;
- `index.html` = HTTP 200 / `text/html; charset=utf-8`;
- `style.css` = HTTP 200 / `text/css; charset=utf-8`;
- `app.js` = HTTP 200 / `application/javascript; charset=utf-8`;
- alias de produção: `https://lsi-career-360.vercel.app`;
- rota antiga do Supabase redireciona para a URL nova.

Arquitetura correta:
`VERCEL FRONTEND -> SUPABASE AUTH/DATA/EDGE BACKEND`

## 4. E2E funcional — PASS

Teste descartável com Auth real e dados 100% sintéticos:
1. conta criada por Supabase Auth;
2. bootstrap executado;
3. role = `master`;
4. sessão JWT real;
5. DOCX sintético;
6. ingest = `QUARANTINED`;
7. deep process = `DRAFT_REQUIRES_CONFIRMATION`;
8. confirmação = `AGENT_READY`;
9. raw file removido;
10. oportunidade avaliada;
11. match = `100 / QUALIFIED_SALARY_CONFIRM`;
12. feed = PASS;
13. agente = PASS;
14. SAC = `resolved`;
15. Painel Mestre = PASS.

Cleanup pós-teste:
- QA users = 0;
- QA opportunities = 0;
- QA hashes = 0;
- gates temporários = 0;
- runner E2E desativado novamente.

## 5. Segurança / Privacidade

`SECURITY_ADVISOR=PASS_ZERO_LINTS` após hardening final.
`MULTIUSER_ISOLATION=PASS_CORE_AB_AND_REAL_AUTH_E2E`.
`PRIVATE_STORAGE=PASS`.
`DIRECT_CLIENT_STORAGE_WRITE=DENIED_BY_RLS`.
`AUTH_REAL_SESSION=PASS_E2E`.
`MASTER_BOOTSTRAP=PASS_E2E`.
`CAREER_PRIVACY_GATE=PASS_SYNTHETIC_SCENARIOS`.

Painel Mestre final:
- somente métricas agregadas em `career_master_metrics`;
- SELECT protegido por RLS para role `master`;
- authenticated não escreve no snapshot;
- refresh interno privilegiado sem EXECUTE para authenticated;
- cron de atualização a cada 5 minutos;
- Edge `career-master-status` sem service role;
- candidato real = HTTP 403 `MASTER_REQUIRED`;
- mestre real = HTTP 200 `PASS_READY_FOR_MASTER_USE`.

## 6. Currículo / arquivos

Bucket: `career-resumes-quarantine`
- privado;
- até 10 MB;
- PDF/DOCX;
- caminho interno aleatório;
- nome original só como display metadata;
- hash/tamanho reconferidos;
- DOCX fail-closed para path traversal/XML inseguro/compressão suspeita;
- PDF protegido ou sem texto rejeitado;
- heurística nunca vira fato confirmado;
- raw removido após confirmação quando possível;
- cleanup automático de hora em hora.

## 7. Matching / privacidade

Matching V1:
- privacidade antes do score;
- idade nunca entra;
- pagamento nunca altera FIT;
- salário oculto/estimado não vira fato;
- salário explícito abaixo do piso pode bloquear;
- sinais somente quando suportados por dados disponíveis;
- `SILENT_BLOCK` para empresa protegida;
- `NO_DISCLOSURE` para empregador não resolvido.

## 8. CI / QA

Referência final da fundação:
- Career 360 Parser Tests = SUCCESS;
- Career 360 Prototype Smoke = SUCCESS;
- Career 360 Edge Typecheck = SUCCESS;
- Master app static test = PASS;
- JavaScript syntax = PASS;
- Hosted frontend Vercel = READY / HTTP 200;
- MIME de HTML/CSS/JS = PASS.

## 9. Gates

`DEDICATED_PROJECT=PASS`
`SECURITY_P0=PASS_MASTER_PILOT_SCOPE`
`CAREER_PRIVACY_P0=PASS_MASTER_PILOT_SCOPE`
`MULTIUSER_ISOLATION=PASS`
`SAFE_FILE_PIPELINE=PASS_MASTER_PILOT_SCOPE`
`RAW_FILE_RETENTION=PASS`
`CV_CONFIRMATION_UI=PASS`
`MATCH_ENGINE_V1=PASS`
`NO_FABRICATION_GUARD=PASS_MASTER_PILOT_SCOPE`
`AUDIT_RECOVERY=PASS_MASTER_PILOT_SCOPE`
`CORE_RELIABILITY=PASS_MASTER_PILOT_SCOPE`
`FRONTEND_HOSTING=PASS_VERCEL`
`MASTER_PILOT=READY_FOR_MASTER_USE`
`PUBLIC_BETA=NOT_OPENED_PRODUCT_DECISION`

## 10. Primeiro uso mestre

1. abrir `https://lsi-career-360.vercel.app`;
2. usar o e-mail mestre já autorizado;
3. criar a conta escolhendo a própria senha;
4. confirmar e-mail se solicitado;
5. entrar;
6. backend atribui `master` automaticamente;
7. completar Minha Carreira;
8. enviar CV ou configurar manualmente;
9. definir ao menos um cargo-alvo;
10. atingir `AGENT_READY`;
11. usar Oportunidades / Meu Agente / Resolver agora / Painel Mestre.

Nunca pedir senha no chat.

## 11. DO NOT REDO

- não reconstruir Career do zero;
- não usar Supabase Edge Function como hospedagem HTML;
- não reutilizar banco de outro produto;
- não reintroduzir service role no frontend/master status;
- não expor `SECURITY DEFINER` ao authenticated;
- não transformar inferência em fato;
- não bypassar MFA/CAPTCHA;
- não abrir Beta pública automaticamente;
- não ativar browser/modelo pago sem Próximo Degrau;
- não criar recovery paralelo.

## 12. NEXT_ACTION

Master Pilot 1.0 está pronto para uso mestre.
Próximos passos são evolutivos:
1. uso mestre real e feedback de UX;
2. corrigir qualquer incidente observado em uso real;
3. Career Learning Engine com outcomes reais;
4. browser/research automation quando houver rota/capacidade adequada;
5. Founding Beta 20 após decisão explícita;
6. Recruiter Agent B2B depois.

## 13. Última alteração verificada

`LAST_VERIFIED_CHANGE=FRONTEND_MOVED_TO_VERCEL_HTML_CSS_JS_MIME_PASS_SUPABASE_OLD_ROUTE_REDIRECTS_RECOVERY_MAIN_FIXED`

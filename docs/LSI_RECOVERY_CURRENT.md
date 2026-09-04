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
Fonte canônica: `main`
PR #25: MERGED
Backend: Supabase `LSI Career 360`, ref `nxjdnzdxclszqyqrkwdk`, região `sa-east-1`.
Frontend oficial: `https://lsi-career-360.vercel.app/`
Projeto Vercel: `lsi-career-360`, project id `prj_DQbCLqrEixa8fTbOkOz3ZtjX9IGP`.

Arquitetura:
`VERCEL FRONTEND -> SUPABASE AUTH/DATA/EDGE BACKEND`

Não usar Supabase Edge Function como superfície HTML; a rota antiga serve apenas como redirecionamento.

## 2. Produto entregue

Master Pilot 1.0 possui:
- Auth individual;
- papel `master` por hash SHA-256 de e-mail autorizado;
- onboarding guiado;
- currículo PDF/DOCX em quarentena privada;
- deep parser determinístico;
- confirmação humana antes de transformar extração em dado operacional;
- Proteção de Carreira;
- Matching V1 explicável;
- radar/análise de oportunidades no piloto;
- Meu Agente zero-cash;
- SAC `Resolver agora`;
- Painel Mestre agregado;
- retenção/cleanup de arquivo bruto;
- audit trail seguro.

## 3. UX atual — Onboarding Guiado V5

Alteração publicada em 2026-09-03 após feedback de uso mestre real.

Quando `onboarding_status != agent_ready`, o usuário entra em um passo a passo visual de 5 etapas:

1. `Sobre você`
   - nome;
   - cargo atual;
   - cidade;
   - UF.

2. `Seu objetivo`
   - cargos-alvo;
   - locais aceitos;
   - salário mínimo opcional;
   - salário alvo opcional.

3. `Proteção`
   - situação profissional atual;
   - empregador atual;
   - proteção do empregador atual;
   - empresas adicionais bloqueadas.

4. `Competências`
   - competências principais confirmadas.

5. `Currículo — agora ou depois`
   - PDF textual/DOCX até 10 MB;
   - currículo é opcional para ativação;
   - pode ser adicionado depois;
   - interface explica que o currículo automatiza organização/preenchimento, sempre sujeito à confirmação.

UX adicional:
- barra de progresso 1/5;
- Próximo / Voltar;
- `Continuar depois` / `Fazer depois`;
- progresso temporário preservado em `sessionStorage`;
- Home lembra `Termine de preparar seu agente`;
- Minha Carreira permite revisar dados e adicionar currículo posteriormente;
- senha e confirmação possuem mostrar/ocultar senha (olho).

Princípio preservado:
`O CLIENTE NÃO PREENCHE. O CLIENTE CONFIRMA.`

Release note:
`career360/releases/MASTER_PILOT_1_0_ONBOARDING_GUIADO_2026-09-03.md`

## 4. Auth real do usuário mestre

Conta mestre real criada e verificada:
- e-mail confirmado = TRUE;
- role = `master`;
- onboarding = `started` no último readback antes da conclusão do fluxo guiado.

Incidente encontrado em primeiro cadastro:
- confirmação de e-mail redirecionou para `localhost:3000`;
- confirmação em si funcionou;
- frontend passou a enviar `emailRedirectTo=https://lsi-career-360.vercel.app/?email-confirmado=1`;
- release: `career360/releases/MASTER_PILOT_1_0_AUTH_REDIRECT_FIX_2026-09-03.md`.

PENDÊNCIA antes de Beta pública:
`SUPABASE_GLOBAL_SITE_URL_REDIRECT_ALLOWLIST=NOT_YET_PROVEN`
A configuração global do provider deve ser alinhada ao domínio oficial; não declarar concluída sem evidência real.

## 5. E2E funcional

PASS com Auth real e dados sintéticos descartáveis:
- create user;
- bootstrap master;
- JWT real;
- DOCX ingest;
- quarantine;
- deep parser;
- draft;
- confirm;
- `AGENT_READY`;
- raw deleted;
- Matching = `100 / QUALIFIED_SALARY_CONFIRM` no cenário sintético;
- feed;
- agent;
- support;
- master panel.

Cleanup pós-teste: 0 QA users, 0 QA opportunities, 0 QA master hashes e runner temporário desativado.

## 6. Segurança / Privacidade

`SECURITY_ADVISOR=PASS_ZERO_LINTS` no último hardening verificado.
`MULTIUSER_ISOLATION=PASS`
`PRIVATE_STORAGE=PASS`
`DIRECT_CLIENT_STORAGE_WRITE=DENIED_BY_RLS`
`AUTH_REAL_SESSION=PASS_E2E`
`CAREER_PRIVACY_GATE=PASS_SYNTHETIC_SCENARIOS`

Painel Mestre:
- somente agregados em `career_master_metrics`;
- leitura protegida por RLS para role `master`;
- authenticated não escreve no snapshot;
- refresh interno sem EXECUTE para authenticated;
- candidato = HTTP 403;
- mestre = HTTP 200.

## 7. Currículo

Pipeline:
`FILE -> QUARANTINED -> DEEP VALIDATION -> DRAFT_REQUIRES_CONFIRMATION -> CONFIRMED -> RAW DELETE`

Controles principais:
- bucket privado `career-resumes-quarantine`;
- 10 MB;
- PDF textual/DOCX;
- tipo real + SHA-256;
- DOCX fail-closed para path traversal/XML inseguro/compressão suspeita;
- PDF protegido/sem texto rejeitado;
- retry idempotente;
- cleanup automático;
- nenhuma heurística vira fato confirmado.

## 8. Matching V1

- privacidade antes do score;
- idade nunca entra;
- pagamento nunca altera FIT;
- salário oculto/estimado não vira fato;
- salário explicitamente abaixo do piso pode bloquear;
- `SILENT_BLOCK` para empresa protegida;
- `NO_DISCLOSURE` para empregador não resolvido.

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
`GUIDED_ONBOARDING_V5=LIVE`
`MASTER_PILOT=READY_FOR_MASTER_USE`
`PUBLIC_BETA=NOT_OPENED_PRODUCT_DECISION`

## 10. DO NOT REDO

- não reconstruir Career do zero;
- não usar Supabase Edge como hospedagem da UI;
- não reutilizar banco de outro produto;
- não reintroduzir service role no frontend;
- não expor `SECURITY DEFINER` ao authenticated;
- não transformar inferência em fato;
- não bypassar MFA/CAPTCHA;
- não abrir Beta pública automaticamente;
- não ativar browser/modelo pago sem Próximo Degrau;
- não criar recovery paralelo.

## 11. NEXT_ACTION

1. continuar uso mestre real e coletar feedback de UX;
2. corrigir incidentes observados no fluxo real;
3. provar/corrigir `Site URL` + Redirect allowlist global do Supabase antes da Beta;
4. evoluir Career Learning Engine com outcomes reais;
5. preparar browser/research automation conforme capacidade;
6. Founding Beta 20 somente após decisão explícita.

## 12. Última alteração verificada

`LAST_VERIFIED_CHANGE=GUIDED_ONBOARDING_V5_LIVE_PASSWORD_EYE_AUTH_REDIRECT_FRONTEND_FIXED_MASTER_ACCOUNT_CONFIRMED`
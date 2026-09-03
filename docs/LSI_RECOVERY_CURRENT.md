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

## 1. Localização

Repository: `umagestaointeligente/ugi-video-renderer`
Branch: `lsi-career360-beta1-foundation-20260902`
PR: Draft #25
Main: Career ainda não promovido.
Supabase dedicado: `LSI Career 360`
Project ref: `nxjdnzdxclszqyqrkwdk`
Região: `sa-east-1`
Custo confirmado do projeto: `R$0/mês`.

## 2. Produto entregue

Master Pilot 1.0 funcional com:
- app web responsivo;
- pacote PWA local;
- Auth individual;
- papel `master` automático pelo e-mail autorizado usando SHA-256 no backend;
- currículo PDF/DOCX;
- quarentena privada;
- validação profunda + parser determinístico;
- rascunho com confirmação humana;
- Proteção de Carreira;
- Matching V1 explicável;
- cadastro manual de oportunidade para piloto zero-cash;
- radar de oportunidades;
- Meu Agente zero-cash;
- SAC `Resolver agora`;
- incidentes/checkpoints;
- Painel Mestre agregado;
- retenção/cleanup do arquivo bruto;
- audit trail seguro.

Hosted app:
`https://nxjdnzdxclszqyqrkwdk.supabase.co/functions/v1/career-app`

## 3. E2E final — PASS

Teste descartável com Auth real e dados 100% sintéticos:
1. conta criada via Supabase Auth Admin;
2. trigger `on_auth_user_created_career_bootstrap` executado;
3. papel atribuído = `master`;
4. login por senha produziu sessão JWT real;
5. DOCX sintético enviado;
6. ingest = `QUARANTINED`;
7. deep process = `DRAFT_REQUIRES_CONFIRMATION`;
8. confirmação = `AGENT_READY`;
9. arquivo bruto removido após confirmação;
10. oportunidade sintética avaliada;
11. match = `100 / QUALIFIED_SALARY_CONFIRM`;
12. feed retornou 1 oportunidade visível;
13. Meu Agente respondeu intent `opportunities`;
14. SAC retornou `resolved`;
15. Painel Mestre retornou role `master`.

Resultado: `MASTER_PILOT_E2E=PASS`.

Cleanup pós-teste verificado:
- QA users = 0;
- QA opportunities = 0;
- QA master hashes = 0;
- runner E2E redeployado em modo desativado;
- gate temporário removido.

## 4. Segurança / Privacidade

`SECURITY_ADVISOR=PASS_ZERO_LINTS` no último hardening.
`MULTIUSER_ISOLATION=PASS_CORE_AB_TEST`.
`PRIVATE_STORAGE=PASS`.
`DIRECT_CLIENT_STORAGE_WRITE=DENIED_BY_RLS`.
`AUTH_REAL_SESSION=PASS_E2E`.
`MASTER_BOOTSTRAP=PASS_E2E`.
`CAREER_PRIVACY_GATE=PASS_SYNTHETIC_SCENARIOS`.

Painel Mestre foi endurecido depois do E2E:
- agregação movida para `public.career_master_status_v1()`;
- `SECURITY DEFINER` com `auth.uid()` + verificação de role master;
- Edge `career-master-status` não precisa mais de service role;
- função retorna apenas agregados, nunca CV/nome/e-mail/histórico de outro usuário.

## 5. Currículo / arquivos

Bucket: `career-resumes-quarantine`
- privado;
- até 10 MB;
- PDF/DOCX;
- caminho interno aleatório;
- nome original só como display metadata;
- hash e tamanho reconferidos no deep process;
- DOCX protegido contra path traversal, XML inseguro e zip bomb suspeito;
- PDF protegido/sem texto rejeitado;
- heurística nunca vira fato confirmado;
- raw removido após confirmação quando possível;
- cleanup automático de hora em hora.

Funções ativas:
- `career-document-ingest`
- `career-document-process`
- `career-document-delete`
- `career-document-cleanup`
- `career-profile-confirm`

## 6. Matching / privacidade

Matching V1:
- privacidade antes do score;
- idade nunca entra;
- pagamento nunca altera FIT;
- salário oculto/estimado não vira fato;
- salário explícito abaixo do piso pode bloquear;
- trabalho/localização/setor/cargo/skills entram somente quando suportados por dados disponíveis;
- bloqueado = `SILENT_BLOCK`;
- empregador não resolvido = `NO_DISCLOSURE`.

## 7. Agente / suporte

Ativos:
- `career-opportunity-add`
- `career-opportunity-list`
- `career-agent`
- `career-support`
- `career-master-status`

Meu Agente V1 é determinístico e zero-cash; responde com o estado real do usuário, não inventa vagas ou resultados.
SAC registra incidente seguro sem currículo/senha/token em metadata geral.

## 8. CI / QA

Referência final antes do release:
- `Career 360 Parser Tests` = SUCCESS;
- `Career 360 Prototype Smoke` = SUCCESS;
- `Career 360 Edge Typecheck` = SUCCESS.

Aplicação local final:
- `MASTER_APP_STATIC_TEST=PASS`;
- `node --check app/app.js` = PASS.

Hosted app:
- HTTP 200 verificado internamente via `pg_net`.

## 9. Gates

`DEDICATED_PROJECT=PASS`
`SECURITY_P0=PASS_MASTER_PILOT_SCOPE`
`CAREER_PRIVACY_P0=PASS_MASTER_PILOT_SCOPE`
`MULTIUSER_ISOLATION=PASS_CORE_AB_AND_REAL_AUTH_E2E`
`SAFE_FILE_PIPELINE=PASS_MASTER_PILOT_SCOPE`
`RAW_FILE_RETENTION=PASS_CRON_AND_E2E_DELETE`
`CV_CONFIRMATION_UI=PASS`
`MATCH_ENGINE_V1=PASS`
`NO_FABRICATION_GUARD=PASS_MASTER_PILOT_SCOPE`
`AUDIT_RECOVERY=PASS_MASTER_PILOT_SCOPE`
`CORE_RELIABILITY=PASS_MASTER_PILOT_SCOPE`
`MASTER_PILOT=READY_FOR_MASTER_USE`
`PUBLIC_BETA=NOT_OPENED_PRODUCT_DECISION`

Importante: `PUBLIC_BETA` não é sinônimo de Master Pilot pronto. Abrir Primeira Turma continua uma decisão separada de produto/comercial.

## 10. Primeiro uso mestre

1. abrir hosted app;
2. usar o e-mail mestre já autorizado;
3. criar a conta escolhendo a própria senha;
4. confirmar e-mail se o provedor solicitar;
5. login;
6. o trigger atribui `master` automaticamente;
7. completar Minha Carreira;
8. enviar CV ou configurar manualmente;
9. definir ao menos um cargo-alvo;
10. estado vira `AGENT_READY`;
11. usar Oportunidades / Meu Agente / Resolver agora / Painel Mestre.

Nunca pedir senha no chat.

## 11. DO NOT REDO

- não reconstruir Career do zero;
- não reutilizar banco de outro produto;
- não reintroduzir service role no frontend ou no master status;
- não criar acesso mestre baseado em e-mail enviado pelo cliente;
- não transformar inferência em fato;
- não bypassar MFA/CAPTCHA;
- não abrir Beta pública automaticamente só porque Master Pilot passou;
- não ativar browser/modelo pago sem decisão de Próximo Degrau;
- não criar metodologia paralela de recovery.

## 12. NEXT_ACTION

Master Pilot 1.0 está finalizado para uso mestre.
Próximas frentes são evolutivas, não blockers do piloto:
1. uso mestre real e feedback;
2. browser/research automation no Próximo Degrau quando houver orçamento/rota adequada;
3. Career Learning Engine com evidência real;
4. preparação da Founding Beta 20 quando houver decisão explícita de abertura;
5. B2B Recruiter Agent em fase posterior.

## 13. Última alteração verificada

`LAST_VERIFIED_CHANGE=MASTER_PILOT_E2E_PASS_HOSTED_APP_HTTP200_QA_CLEAN_MASTER_STATUS_NO_SERVICE_ROLE`

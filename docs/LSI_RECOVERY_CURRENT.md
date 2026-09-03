# LSI — RECOVERY CURRENT

Status: CURRENT / AUTORITATIVO PARA HANDOFF
Atualizado: 2026-09-03 BRT
Âncora humana: `Recovery LSI`
Alias técnico interno: `LSI::RECOVERY::CURRENT`

## 0. Estado global

`LSI_RECOVERY=TRUE`
`CURRENT_FOCUS=LSI_CAREER_360_BETA_1_0`
`CURRENT_STATUS=CORE_DATA_QUARANTINE_AND_RETENTION_IN_PROGRESS`
`VERIFIED_REVENUE=R$0,00` para esta lógica de incubação; reconfirmar fonte antes de decisão monetária.

## 1. Recovery canônico

Entrada estável no `main`: `docs/LSI_RECOVERY_POINTER.md`.
Ler depois:
- `docs/LSI_CANONICAL_INDEX.md`
- este CURRENT
- `docs/projects/LSI_CAREER360.md`
- especializados somente sob demanda.

Runtime/evidência vence memória para estado operacional atual.

## 2. Localização Career

Repository: `umagestaointeligente/ugi-video-renderer`
Branch: `lsi-career360-beta1-foundation-20260902`
PR: Draft #25
Main: código Career ainda não promovido.

## 3. Produto/UX já implementado

- PWA mobile/desktop;
- onboarding currículo / voz / gradual;
- cinco áreas: Início / Oportunidades / Jornada / Carreira / Agente;
- Proteção de Carreira inicial;
- etapa `Confira o que entendemos` integrada ao mesmo PWA;
- UI aceita o contrato `candidate_profile_draft`;
- campos exibem confiança e permitem correção;
- exemplo visual marcado como `MODO QA`, 100% sintético;
- protótipo local segue sem envio remoto silencioso.

Princípio: `O CLIENTE NÃO PREENCHE. O CLIENTE CONFIRMA.`

PWA smoke:
- workflow `Career 360 Prototype Smoke`;
- run `33709551771`;
- job `prototype-smoke`;
- conclusion `SUCCESS`.

## 4. Parser de currículo

Arquivos:
- `career360/parser/resume_parser.py`
- `career360/parser/test_resume_parser.py`
- `career360/parser/requirements.txt`

Características:
- PDF textual via `pypdf==6.16.2`;
- DOCX ZIP/XML fail-closed;
- limite inicial 10 MB;
- valida tipo real;
- bloqueia path traversal, XML inseguro e compressão suspeita;
- rejeita PDF protegido/sem texto;
- saída sempre requer confirmação;
- heurística nunca vira fato confirmado.

Parser CI: PASS.

## 5. Supabase dedicado — CRIADO

Organização selecionada pelo usuário:
`paulosk8.sk8@gmail.com`

Projeto:
- nome: `LSI Career 360`;
- project ref/id: `nxjdnzdxclszqyqrkwdk`;
- região: `sa-east-1`;
- status verificado: `ACTIVE_HEALTHY`;
- custo consultado e confirmado: `R$0/mês`.

Regra preservada:
- NÃO reutilizar `lsi-revenue-autopilot`;
- NÃO compartilhar banco Career com outro produto.

## 6. Schema/RLS — APLICADO E TESTADO

Migrations aplicadas:
- `career360_schema_v1` = SUCCESS;
- `career360_cover_foreign_keys` = SUCCESS;
- `career360_private_quarantine_bucket` = SUCCESS.

Correção capturada antes de dados reais:
- coluna `current_role` colidia com palavra reservada PostgreSQL `CURRENT_ROLE`;
- renomeada para `current_role_title`;
- primeira migration falhou sem aplicar schema;
- correção versionada e migration reaplicada com sucesso.

Tabelas atuais:
- `career_profiles`
- `career_preferences`
- `career_employer_blocks`
- `career_documents`
- `career_profile_drafts`
- `career_confirmed_facts`
- `career_action_permissions`
- `career_audit_events`

Controles provados:
- RLS habilitado em todas as 8 tabelas;
- `anon` sem SELECT/INSERT;
- authenticated com acesso apenas conforme grants + ownership;
- USER_A enxergou exatamente 1 linha própria em teste A/B;
- USER_A tentando gravar dado de USER_B foi bloqueado por RLS (`42501`);
- transações sintéticas revertidas;
- 0 usuários sintéticos e 0 linhas sintéticas permaneceram após testes.

Security Advisor Supabase:
`LINTS=[]`.

Performance Advisor:
- três FKs sem índice foram detectadas e corrigidas;
- avisos remanescentes são apenas `unused_index` INFO, esperados em banco recém-criado e vazio.

## 7. Quarentena/storage — ATIVO PARCIAL

Bucket:
`career-resumes-quarantine`

Configuração verificada:
- `public=false`;
- limite 10 MB;
- MIME permitido: PDF e DOCX;
- sem política de upload direto do cliente.

Teste negativo:
- escrita direta como `authenticated` em `storage.objects` foi bloqueada por RLS (`42501`).

Edge Functions ativas:
- `career-document-ingest` — `verify_jwt=true`;
- `career-document-delete` — `verify_jwt=true`.

Código versionado:
- `career360/edge-functions/career-document-ingest/index.ts`;
- `career360/edge-functions/career-document-delete/index.ts`.

`career-document-ingest`:
- exige sessão válida;
- bloqueia request/file acima do limite;
- aceita apenas extensão PDF/DOCX;
- verifica assinatura real mínima e compatibilidade extensão/assinatura;
- calcula SHA-256;
- gera caminho interno aleatório por user_id + UUID;
- nunca usa nome original como object path;
- grava somente em bucket privado;
- cria metadado em `career_documents` como `quarantined`;
- limita documentos ativos de onboarding a 3;
- define retenção inicial máxima de 7 dias;
- remove objeto se a escrita de metadado falhar.

`career-document-delete`:
- exige sessão válida;
- resolve ownership por user_id;
- usuário não consegue deletar documento de terceiro;
- remove objeto privado;
- marca tombstone `deleted`;
- limpa `storage_object_path`;
- é idempotente para documento já deletado.

## 8. Retenção do arquivo bruto — POLÍTICA DEFINIDA

Documento:
`career360/docs/CAREER360_RAW_FILE_RETENTION_V1.md`

Beta 1.0:
- QUARANTINED/PARSED aguardando confirmação: máximo inicial 7 dias;
- REJECTED: alvo de exclusão em até 24h;
- após confirmação do perfil: excluir bruto imediatamente quando possível, SLO máximo 24h;
- exclusão pedida pelo usuário: imediata best-effort, com recovery se terceiro falhar.

Ainda falta:
- cleanup automático para abandonados/rejeitados expirados;
- teste end-to-end autenticado real das Edge Functions;
- conexão deep validation/parser ao objeto em quarentena.

IMPORTANTE:
- assinatura ZIP compatível com DOCX não equivale a `SAFE_FOR_PARSE`;
- parser determinístico continua sendo o gate de validação profunda;
- funções ainda não foram ligadas ao PWA de testers reais.

## 9. Proteção de Carreira — P0

Fluxo obrigatório:
`OPORTUNIDADE -> IDENTIFICAR_EMPREGADOR -> RESOLVER_GRUPO -> PORTA_DE_PRIVACIDADE -> MATCHING/APRESENTAÇÃO`

Regras duras:
- atual/grupo bloqueados quando configurados;
- bloqueado = `SILENT_BLOCK`;
- desconhecido = `NO_DISCLOSURE`;
- B2B não consulta se empregado nominal usa Career;
- idade nunca entra no matching;
- pagamento nunca altera FIT.

## 10. Gates atuais

`SECURITY_P0=PARTIAL_CORE_DB_SECURITY_ADVISOR_CLEAN`
`CAREER_PRIVACY_P0=NOT_YET_PROVEN`
`MULTIUSER_ISOLATION=CORE_DB_AB_TEST_PASS`
`SAFE_FILE_PIPELINE=PARTIAL_AUTH_QUARANTINE_DELETE_ACTIVE_DEEP_SCAN_AND_CLEANUP_PENDING`
`RAW_FILE_RETENTION_POLICY=DEFINED`
`CV_CONFIRMATION_UI=PASS_STATIC_SMOKE`
`MATCH_ENGINE_V1=NOT_YET_PROVEN`
`AUDIT_RECOVERY=NOT_YET_PROVEN`
`BETA_ENVIRONMENT=NOT_YET_PROVEN`
`BETA_USERS_REAL=BLOCKED`

## 11. NEXT_ACTION

1. implementar cleanup automático dos raws expirados/rejeitados;
2. conectar deep validation/parser ao objeto `QUARANTINED` e promover somente após PASS para `SAFE_FOR_PARSE`;
3. criar teste end-to-end autenticado das Edge Functions com usuário sintético controlado;
4. conectar `LSI_DOCUMENT_INGEST` ao PWA somente em ambiente de teste;
5. completar Proteção de Carreira P0;
6. Matching Engine V1;
7. audit/checkpoints/recovery operacional;
8. Security + Privacy P0 end-to-end tests;
9. UX/visual QA;
10. Primeira Turma somente após PASS.

## 12. DO NOT REDO

- não reconstruir Career;
- não mergear código Career no main antes dos gates;
- não usar banco de outro produto;
- não transformar dados sintéticos em fatos;
- não confundir core DB/RLS verde com Beta segura;
- não tratar `QUARANTINED` como arquivo seguro;
- não declarar retenção cumprida sem cleanup verificado;
- não bypassar MFA/CAPTCHA;
- não ativar API/modelo pago sem decisão de reinvestimento;
- não criar centenas de handoffs; atualizar CURRENT + manifestos estáveis.

## 13. READ NEXT

Obrigatórios:
- `docs/LSI_CANONICAL_INDEX.md`
- `docs/LSI_RECOVERY_CURRENT.md`
- `docs/projects/LSI_CAREER360.md`

Sob demanda:
- ingestão: `career360/docs/CAREER360_FILE_INGESTION_V1.md`
- retenção: `career360/docs/CAREER360_RAW_FILE_RETENTION_V1.md`
- auth: `career360/docs/CAREER360_AUTH_ISOLATION_V1.md`
- segurança: `career360/docs/CAREER360_SECURITY_PRIVACY_P0_V1.md`
- dados: `career360/docs/CAREER360_DATA_CONTRACT_V1.md`
- UX: `career360/docs/CAREER360_BETA1_FOUNDATION_V1.md`

## 14. Última alteração verificada

`LAST_VERIFIED_CHANGE=DEDICATED_SUPABASE_RLS_AB_PASS_PRIVATE_QUARANTINE_INGEST_AND_AUTH_DELETE_ACTIVE_RETENTION_DEFINED`

# LSI — RECOVERY CURRENT

Status: CURRENT / AUTORITATIVO PARA HANDOFF
Atualizado: 2026-09-02 BRT
Âncora humana: `Recovery LSI`
Alias técnico interno: `LSI::RECOVERY::CURRENT`

## 0. Estado global

`LSI_RECOVERY=TRUE`
`CURRENT_FOCUS=LSI_CAREER_360_BETA_1_0`
`CURRENT_STATUS=FOUNDATION_AND_CORE_PIPELINE_IN_PROGRESS`
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
Main: código Career não promovido.

## 3. Produto/UX implementado

- PWA mobile/desktop;
- onboarding currículo / voz / gradual;
- cinco áreas: Início / Oportunidades / Jornada / Carreira / Agente;
- Proteção de Carreira inicial;
- texto + voz;
- etapa `Confira o que entendemos` integrada ao mesmo PWA;
- UI aceita o contrato `candidate_profile_draft` do parser;
- campos exibem confiança e permitem correção;
- exemplo visual é explicitamente `MODO QA`, 100% sintético e não vira dado do cliente;
- arquivo real continua sem upload/leitura remota no protótipo local.

Princípio: `O CLIENTE NÃO PREENCHE. O CLIENTE CONFIRMA.`

## 4. Evidências PWA

Workflow: `Career 360 Prototype Smoke`
Run: `33709551771`
Job: `prototype-smoke`
Conclusion: `SUCCESS`

Passaram:
- testes estáticos de IDs/estrutura;
- funções de confirmação de rascunho;
- marcação explícita de dados sintéticos;
- ausência de fetch/XHR/WebSocket/sendBeacon no protótipo;
- restrição do file input a PDF/DOCX;
- `node --check` no JavaScript inline.

## 5. Parser de currículo

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
- saída = `DRAFT_REQUIRES_CONFIRMATION`;
- heurística nunca vira fato confirmado.

Parser CI já teve run `33708953941` = SUCCESS e execuções subsequentes continuam verdes.

`SAFE_FILE_PIPELINE` ainda NÃO é PASS porque faltam upload autenticado, quarentena, storage privado, retenção e isolamento provado.

## 6. Dados/Auth — desenho pronto, implantação pendente

Docs:
- `career360/docs/CAREER360_AUTH_ISOLATION_V1.md`
- `career360/docs/CAREER360_DATA_CONTRACT_V1.md`
- `career360/schema/CAREER360_SCHEMA_V1.sql`

Rota candidata: Supabase Auth + Postgres RLS em projeto **dedicado ao Career**.
Não reutilizar `lsi-revenue-autopilot` nem projeto de outro produto.

Schema desenhado com:
- RLS explícito;
- anon sem grants;
- ownership por `auth.uid() = user_id`;
- UPDATE com USING + WITH CHECK;
- audit events sem insert direto do frontend;
- nenhuma autorização por `user_metadata`.

Projeto real Career ainda não foi criado porque o conector exige escolha explícita de organização + confirmação de custo antes da criação.

## 7. Proteção de Carreira — P0

Fluxo:
`OPORTUNIDADE -> IDENTIFICAR_EMPREGADOR -> RESOLVER_GRUPO -> PORTA_DE_PRIVACIDADE -> MATCHING/APRESENTAÇÃO`

Regras duras:
- atual/grupo bloqueados quando configurados;
- bloqueado = `SILENT_BLOCK`;
- desconhecido = `NO_DISCLOSURE`;
- B2B não consulta se empregado nominal usa Career;
- idade nunca entra no matching;
- pagamento nunca altera FIT.

## 8. Incubadora / infraestrutura

Pilares:
- Provar a Custo Zero
- Autonomia desde a Origem
- Estrutura Espelho
- Evidência antes de capital
- Próximo Degrau

Fluxo interno:
`CURRENT -> SHADOW -> TEST -> CANARY -> PROMOTE -> ROLLBACK_IF_NEEDED`

Regra externa:
`ZERO_CUSTOMER_MIGRATION` sempre que possível.

## 9. Ecossistema

NEXO permanece frente paralela conceitual: educação/inteligência financeira acessível; NEXO Product != NEXO Capital.

Pós-Career: Primeiros 90 Dias, Management, Career Guardian, Cofre de Conquistas, Skills/Promotion/Leadership, Network/Personal Brand, Sales, Business.

Career concluído com sucesso = `MISSÃO CUMPRIDA`.

## 10. Gates atuais

`SECURITY_P0=NOT_YET_PROVEN`
`CAREER_PRIVACY_P0=NOT_YET_PROVEN`
`MULTIUSER_ISOLATION=NOT_YET_PROVEN`
`SAFE_FILE_PIPELINE=PARTIAL_PARSER_CI_PASS`
`CV_CONFIRMATION_UI=PASS_STATIC_SMOKE`
`MATCH_ENGINE_V1=NOT_YET_PROVEN`
`AUDIT_RECOVERY=NOT_YET_PROVEN`
`BETA_ENVIRONMENT=NOT_YET_PROVEN`

## 11. NEXT_ACTION

1. criar projeto Auth/Data Career isolado quando passar o gate obrigatório de organização/custo;
2. aplicar schema e testar RLS usuário A / usuário B / anônimo;
3. criar storage privado + quarentena + política de retenção/exclusão;
4. conectar parser autenticado à tela de confirmação;
5. implementar Proteção de Carreira P0 completa;
6. Matching Engine V1;
7. audit/checkpoints/recovery operacional;
8. Security + Privacy P0 tests;
9. UX/visual QA;
10. Primeira Turma somente após PASS.

## 12. DO NOT REDO

- não reconstruir Career;
- não mergear código Career no main antes dos gates;
- não usar banco de outro produto;
- não transformar dados sintéticos em fatos;
- não confundir parser/PWA CI verde com Beta segura;
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
- auth: `career360/docs/CAREER360_AUTH_ISOLATION_V1.md`
- segurança: `career360/docs/CAREER360_SECURITY_PRIVACY_P0_V1.md`
- dados: `career360/docs/CAREER360_DATA_CONTRACT_V1.md`
- UX: `career360/docs/CAREER360_BETA1_FOUNDATION_V1.md`

## 14. Última alteração verificada

`LAST_VERIFIED_CHANGE=CV_CONFIRMATION_UI_IMPLEMENTED_AND_PWA_SMOKE_CI_PASS`

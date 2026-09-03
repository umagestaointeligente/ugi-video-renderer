# LSI — RECOVERY CURRENT

Status: CURRENT / AUTORITATIVO PARA HANDOFF
Atualizado: 2026-09-02 BRT
Âncora humana: `Recovery LSI`
Alias técnico interno: `LSI::RECOVERY::CURRENT`

## 0. Estado global

`LSI_RECOVERY=TRUE`
`CURRENT_FOCUS=LSI_CAREER_360_BETA_1_0`
`CURRENT_STATUS=FOUNDATION_AND_CORE_PIPELINE_IN_PROGRESS`
`VERIFIED_REVENUE=R$0,00` para esta lógica de incubação; reconfirmar fonte antes de qualquer decisão monetária.

## 1. Recovery canônico

Arquitetura vigente:
- ponteiro estável no `main`: `docs/LSI_RECOVERY_POINTER.md`;
- índice: `docs/LSI_CANONICAL_INDEX.md`;
- este snapshot CURRENT;
- manifesto CURRENT do projeto ativo;
- documentos especializados somente sob demanda;
- ADR apenas para decisão estrutural material;
- runtime/evidência vence memória para estado operacional atual.

Comando do usuário em chat novo: `Recovery LSI`.

## 2. Career 360 — localização

Repository: `umagestaointeligente/ugi-video-renderer`
Branch isolada: `lsi-career360-beta1-foundation-20260902`
PR Draft: `#25 — Career 360 Beta 1.0 — fundação zero-cost e protótipo PWA`
Main: código Career permanece não promovido.

## 3. Entregas já existentes

### Produto/UX
- protótipo PWA mobile/desktop;
- onboarding curto: currículo / voz / gradual;
- Proteção de Carreira inicial;
- cinco áreas: Início / Oportunidades / Jornada / Carreira / Agente;
- texto + voz;
- manifest + service worker;
- princípio: `O CLIENTE NÃO PREENCHE. O CLIENTE CONFIRMA.`

### Documentação
- `career360/docs/CAREER360_BETA1_FOUNDATION_V1.md`
- `career360/docs/CAREER360_SECURITY_PRIVACY_P0_V1.md`
- `career360/docs/CAREER360_DATA_CONTRACT_V1.md`
- `career360/docs/CAREER360_FILE_INGESTION_V1.md`
- `docs/projects/LSI_CAREER360.md`

### Parser de currículo
- `career360/parser/resume_parser.py`
- `career360/parser/test_resume_parser.py`
- `career360/parser/requirements.txt`
- PDF textual via `pypdf==6.16.2`;
- DOCX via ZIP/XML fail-closed;
- limite inicial 10 MB;
- validação de assinatura real;
- proteção contra path traversal / XML inseguro / compressão suspeita;
- saída sempre `DRAFT_REQUIRES_CONFIRMATION`;
- heurística nunca vira fato confirmado.

### Evidência CI
Workflow: `Career 360 Parser Tests`
Run: `33708953941`
Job: `parser-tests`
Conclusão: `SUCCESS`
Passaram: checkout, Python, instalação limpa e testes determinísticos.

IMPORTANTE: parser verde isolado NÃO equivale a `SAFE_FILE_PIPELINE=PASS`.

### Schema lógico candidato
- `career360/schema/CAREER360_SCHEMA_V1.sql`
- ainda NÃO aplicado a banco real;
- RLS explícito;
- `anon` sem grants;
- ownership por `auth.uid() = user_id`;
- nenhuma autorização baseada em `user_metadata`;
- audit events sem insert direto do cliente;
- Candidate side isolado por ownership.

## 4. Decisão de infraestrutura de dados

Supabase foi avaliado como rota candidata zero-custo para Auth/Postgres/RLS.
Há projetos Supabase já existentes na conta, mas NÃO reutilizar `lsi-revenue-autopilot` para Career.
Career deve possuir projeto próprio para preservar isolamento.
Criação de projeto real permanece pendente porque o conector exige confirmação explícita da organização e custo antes da criação.

Até lá:
- código/schema/testes avançam na branch;
- nenhum dado real de cliente é colocado em projeto compartilhado.

## 5. Princípios obrigatórios Career

### Produto
- PWA/web app primeiro;
- cliente não precisa ter ChatGPT;
- interface guiada;
- PDF/DOCX pré-preenche e usuário confirma;
- voz crítica exige confirmação;
- poucos campos visíveis;
- Português por Fora, Padrão Técnico por Dentro.

### Público/UX
- público amplo;
- atenção a profissionais experientes/40+ é hipótese de mercado, nunca filtro de matching;
- interface simples, legível e confortável;
- otimizar valor por visita, não tempo de tela.

### Privacidade
- Proteção de Carreira = P0;
- empregador atual/grupo bloqueados quando configurados;
- empresa bloqueada = silêncio total;
- empregador desconhecido = sem divulgação automática;
- B2B não consulta nominalmente se empregado usa Career;
- pagamento nunca aumenta FIT;
- idade nunca entra no matching.

### Segurança
- custo zero não vence segurança/privacidade/legalidade;
- secrets nunca em Git;
- least privilege;
- logs sem PII desnecessária;
- suporte/recuperação fazem parte do produto.

## 6. Incubadora LSI

Pilares transversais aprovados:
1. `PROVAR A CUSTO ZERO`.
2. `AUTONOMIA DESDE A ORIGEM`.
3. `ESTRUTURA ESPELHO` como requisito técnico.
4. investimento compra o `PRÓXIMO DEGRAU` útil.
5. evidência antes de capital.
6. projeto ruim morre barato; vencedor recebe capital.

Exceção de investimento inicial somente via `EXCEPTIONAL_BUILD` com evidência forte, risco controlado e payback plausível.

## 7. Infraestrutura progressiva

Pilares:
- Browser
- IA
- Reliability
- Security
- Database
- Observability
- Support
- Scale

Fluxo interno permitido:
`CURRENT -> SHADOW -> TEST -> CANARY -> PROMOTE -> ROLLBACK_IF_NEEDED`

Regra externa:
`ZERO_CUSTOMER_MIGRATION` sempre que tecnicamente possível.

## 8. Caixa/ecossistema

Separar:
- receita bruta;
- taxas/impostos/chargebacks/obrigações;
- reserva operacional;
- reinvestimento empresarial;
- excedente livre.

Níveis:
1. Ecosystem Capital Allocator — qual projeto recebe.
2. Project Infrastructure Allocator — qual Próximo Degrau recebe.

NEXO Product != NEXO Capital.

## 9. NEXO

NEXO = Núcleo de Entendimento, eXplicação e Oportunidades.
Tagline: `Entenda antes de investir.`

Direção:
- educação/inteligência financeira acessível;
- provar metodologia antes de produto maduro;
- execução/recomendação financeira regulada exige gates próprios;
- avançar em paralelo conforme allocator, sem drenar recursos críticos.

## 10. Ecossistema pós-Career

Tese: reter relação com LSI, não prender usuário ao Career.
Caminhos conceituais:
- Primeiros 90 Dias
- Management
- Career Guardian
- Cofre de Conquistas
- Skills / Promotion / Leadership
- Network / Personal Brand
- Sales
- Business

Career concluído com sucesso = `MISSÃO CUMPRIDA`.

## 11. Bloqueios antes de tester real

`SECURITY_P0=NOT_YET_PROVEN`
`CAREER_PRIVACY_P0=NOT_YET_PROVEN`
`MULTIUSER_ISOLATION=NOT_YET_PROVEN`
`SAFE_FILE_PIPELINE=PARTIAL_PARSER_CI_PASS`
`MATCH_ENGINE_V1=NOT_YET_PROVEN`
`AUDIT_RECOVERY=NOT_YET_PROVEN`
`BETA_ENVIRONMENT=NOT_YET_PROVEN`

## 12. NEXT_ACTION

1. criar tela de confirmação/correção conectada ao contrato do parser;
2. fechar arquitetura de Auth + isolamento multiusuário;
3. preparar/applicar schema somente em projeto Career isolado;
4. completar quarentena/storage/retention do upload;
5. Proteção de Carreira P0 completa;
6. Matching Engine V1;
7. audit log/checkpoints/recovery operacional;
8. Security + Privacy P0 tests;
9. UX/visual QA;
10. liberar Primeira Turma somente após PASS.

## 13. DO NOT REDO

- não reconstruir Career do zero;
- não mergear código Career no main antes dos gates;
- não usar projeto Supabase de outro produto;
- não confundir parser CI verde com upload de produção seguro;
- não fabricar fatos de CV;
- não bypassar MFA/CAPTCHA;
- não ativar API/modelo pago sem decisão de reinvestimento;
- não criar centenas de handoffs; atualizar CURRENT + manifestos estáveis;
- não deixar decisão material apenas no chat.

## 14. READ NEXT

Obrigatórios no Recovery:
- `docs/LSI_CANONICAL_INDEX.md`
- `docs/LSI_RECOVERY_CURRENT.md`
- `docs/projects/LSI_CAREER360.md`

Sob demanda:
- ingestão: `career360/docs/CAREER360_FILE_INGESTION_V1.md`
- segurança: `career360/docs/CAREER360_SECURITY_PRIVACY_P0_V1.md`
- dados: `career360/docs/CAREER360_DATA_CONTRACT_V1.md`
- UX: `career360/docs/CAREER360_BETA1_FOUNDATION_V1.md`

## 15. Última alteração verificada

`LAST_VERIFIED_CHANGE=RESUME_PARSER_IMPLEMENTED_AND_CI_PASS_SCHEMA_DESIGN_ADDED`

O CURRENT deve ser atualizado durante o trabalho, não somente no fim do chat.

# LSI CAREER 360 — MANIFESTO CURRENT

Status: ACTIVE_BUILD
Versão do manifesto: 1.2
Data-base: 2026-09-02 BRT
Owner/CEO: Paulo
Orquestração: Lola / LSI

## 1. Missão

Construir agente de carreira B2C e, futuramente, Recruiter Agent B2B conectados por matching bilateral, com experiência simples, privacidade forte, automação responsável e aprendizado contínuo.

Posicionamento:
- IA para quem não quer aprender IA.
- Enquanto você trabalha na sua carreira, nós trabalhamos na sua próxima oportunidade.
- Evidência antes de promessa.

## 2. Estado técnico atual

Repository: `umagestaointeligente/ugi-video-renderer`
Branch: `lsi-career360-beta1-foundation-20260902`
PR: Draft #25
Main: código Career ainda não promovido.

- PWA protótipo = EXISTS
- confirmação/correção de rascunho do CV = IMPLEMENTED_IN_PROTOTYPE
- PWA static smoke = PASS
- parser PDF/DOCX = IMPLEMENTED
- parser security CI = PASS
- schema lógico + RLS = DESIGNED_NOT_APPLIED
- Auth/isolamento = DESIGNED_NOT_PROVEN
- testers reais = BLOCKED_BY_P0_GATES

## 3. Recovery

Âncora humana: `Recovery LSI`.
Ponteiro: `main/docs/LSI_RECOVERY_POINTER.md`.
Obrigatórios: `docs/LSI_CANONICAL_INDEX.md`, `docs/LSI_RECOVERY_CURRENT.md`, este manifesto.

## 4. Arquivos canônicos

- Fundação/UX: `career360/docs/CAREER360_BETA1_FOUNDATION_V1.md`
- Segurança/Privacidade: `career360/docs/CAREER360_SECURITY_PRIVACY_P0_V1.md`
- Dados: `career360/docs/CAREER360_DATA_CONTRACT_V1.md`
- Entrada de currículo: `career360/docs/CAREER360_FILE_INGESTION_V1.md`
- Auth/isolamento: `career360/docs/CAREER360_AUTH_ISOLATION_V1.md`
- Schema: `career360/schema/CAREER360_SCHEMA_V1.sql`
- Parser: `career360/parser/`
- PWA: `career360/prototype/`

## 5. Superfície do cliente

PWA/web app, navegador + instalação opcional, mesma conta mobile/desktop, sem dependência de ChatGPT.

Navegação inicial:
1. Início
2. Oportunidades
3. Jornada
4. Carreira
5. Agente

Princípio: `O CLIENTE NÃO PREENCHE. O CLIENTE CONFIRMA.`

Entradas:
- currículo PDF/DOCX;
- voz;
- texto;
- gradual como fallback.

## 6. Onboarding

Fluxo alvo:
1. boas-vindas;
2. currículo/voz/gradual;
3. extração;
4. rascunho com confiança/evidência;
5. confirmação/correção;
6. lacunas;
7. objetivos;
8. Proteção de Carreira;
9. permissões/autonomia;
10. `AGENT_READY=true`;
11. trial/prova de valor só depois.

A etapa 5 já existe no protótipo e aceita o shape do parser. Exemplo QA é sintético e explicitamente marcado.

## 7. PWA — evidência

Workflow: `Career 360 Prototype Smoke`
Run: `33709551771`
Job: `prototype-smoke`
Conclusion: SUCCESS.

Testes cobrem:
- IDs/estrutura críticos;
- funções de confirmação do rascunho;
- marcação de modo sintético;
- ausência de chamadas remotas silenciosas;
- PDF/DOCX no input;
- sintaxe JavaScript via `node --check`.

## 8. Parser de currículo

PDF textual via `pypdf==6.16.2`; DOCX via ZIP/XML fail-closed.
Proteções: limite 10 MB, tipo real, path traversal, XML inseguro, compressão suspeita, arquivo vazio/corrompido, PDF protegido/sem texto.

Saída = `DRAFT_REQUIRES_CONFIRMATION`.
Heurística nunca vira fato.

Parser CI verde; run de referência `33708953941` = SUCCESS.

`SAFE_FILE_PIPELINE` permanece PARTIAL: faltam upload autenticado, quarentena, storage privado, retention e isolamento provado.

## 9. Proteção de Carreira — P0

`OPORTUNIDADE -> IDENTIFICAR_EMPREGADOR -> RESOLVER_GRUPO -> PORTA_DE_PRIVACIDADE -> MATCHING/APRESENTAÇÃO`

- atual/grupo bloqueados quando configurados;
- bloqueado = `SILENT_BLOCK`;
- desconhecido = `NO_DISCLOSURE`;
- B2B não consulta se empregado nominal usa Career;
- idade não entra no matching;
- pagamento não altera FIT.

## 10. Auth / isolamento

Rota candidata: Supabase Auth + Postgres RLS em projeto Career dedicado.

NÃO reutilizar `lsi-revenue-autopilot` ou qualquer projeto de outro produto.

Regras:
- `auth.uid() = user_id`;
- RLS em tabela exposta;
- anon sem grants;
- UPDATE com USING + WITH CHECK;
- service role nunca frontend;
- `user_metadata` nunca autoridade.

Projeto real ainda não criado: conector exige escolha explícita de organização + confirmação de custo.

## 11. Schema Candidate V1

Tabelas:
- `career_profiles`
- `career_preferences`
- `career_employer_blocks`
- `career_documents`
- `career_profile_drafts`
- `career_confirmed_facts`
- `career_action_permissions`
- `career_audit_events`

Status: design executável versionado; NÃO aplicado.

## 12. Matching V1

Sinais permitidos: experiência/competências confirmadas, senioridade, responsabilidades, localização/modelo, remuneração compatível quando suportada, setor, preferências explícitas, resultados reais do funil.

Nunca fabricar fato, usar idade, aumentar FIT por plano ou automatizar rejeição humana final no B2B.

## 13. Learning / suporte

Aprender de resultados verificados; hard policies não decaem. Mudança de estratégia passa por versão atual vs versão em teste.

Suporte interno:
- L0 prevenção
- L1 self-heal/checkpoint
- L2 recuperação econômica
- L3 inteligência avançada
- L4 humano inevitável

Externamente: Resolvido / Preciso de Você / Bloqueio Externo.

## 14. Incubação / Estrutura Espelho

- Provar a Custo Zero
- Autonomia desde a Origem
- Estrutura Espelho
- Evidência antes de capital
- Próximo Degrau

Capacidades lógicas: `LSI_AI`, `LSI_BROWSER`, `LSI_STORAGE`, `LSI_AUTH`, `LSI_EMAIL`, `LSI_OBSERVABILITY`, `LSI_SUPPORT`.

Fluxo: `CURRENT -> SHADOW -> TEST -> CANARY -> PROMOTE -> ROLLBACK_IF_NEEDED`.
Cliente não deve recriar conta/perfil por troca de provider quando evitável.

## 15. Beta / Primeira Turma

Alvo: ~20 testers diversos.
Medir onboarding, time to first value, relevância, ações reais, respostas/entrevistas, incidentes, resolução autônoma, tempo poupado, satisfação e disposição a pagar quando testada.

## 16. Gates

`SECURITY_P0=NOT_YET_PROVEN`
`CAREER_PRIVACY_P0=NOT_YET_PROVEN`
`MULTIUSER_ISOLATION=NOT_YET_PROVEN`
`SAFE_FILE_PIPELINE=PARTIAL_PARSER_CI_PASS`
`CV_CONFIRMATION_UI=PASS_STATIC_SMOKE`
`NO_FABRICATION_GUARD=PARTIAL_BY_PARSER_CONTRACT`
`AUDIT_RECOVERY=NOT_YET_PROVEN`
`CORE_RELIABILITY=NOT_YET_PROVEN`
`BETA_ENVIRONMENT=NOT_YET_PROVEN`

## 17. NEXT ACTION

1. projeto Auth/Data Career isolado após gate obrigatório de organização/custo;
2. aplicar schema e provar RLS A/B/anon;
3. storage/quarentena/retention;
4. conectar parser autenticado à confirmação;
5. Proteção de Carreira P0 completa;
6. Matching V1;
7. audit/checkpoints/recovery;
8. Security/Privacy P0 tests;
9. UX/visual QA;
10. Primeira Turma.

## 18. READ_NEXT_IF_NEEDED

- ingestão: `career360/docs/CAREER360_FILE_INGESTION_V1.md`
- auth: `career360/docs/CAREER360_AUTH_ISOLATION_V1.md`
- segurança: `career360/docs/CAREER360_SECURITY_PRIVACY_P0_V1.md`
- dados: `career360/docs/CAREER360_DATA_CONTRACT_V1.md`
- UX: `career360/docs/CAREER360_BETA1_FOUNDATION_V1.md`

## 19. DO NOT REDO

- não criar protótipo paralelo;
- não mergear main antes dos gates;
- não usar banco de outro produto;
- não tratar CI isolada como Beta segura;
- não fabricar CV/dados;
- não bypassar MFA/CAPTCHA;
- não acoplar domínio a provider;
- não deixar mudança material somente no chat.

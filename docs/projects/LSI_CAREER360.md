# LSI CAREER 360 — MANIFESTO CURRENT

Status: ACTIVE_BUILD
Versão do manifesto: 1.1
Data-base: 2026-09-02 BRT
Owner/CEO: Paulo
Orquestração: Lola / LSI

## 1. Missão

Construir agente de carreira B2C e, futuramente, Recruiter Agent B2B conectados por matching bilateral, com experiência simples, privacidade forte, automação responsável e aprendizado contínuo.

Posicionamento:
- IA para quem não quer aprender IA.
- Enquanto você trabalha na sua carreira, nós trabalhamos na sua próxima oportunidade.
- Evidência antes de promessa.

## 2. Estado atual

Repository: `umagestaointeligente/ugi-video-renderer`
Branch: `lsi-career360-beta1-foundation-20260902`
PR: Draft #25
Main: não contém o código Career em construção.

Estado técnico:
- PWA protótipo navegável = EXISTS;
- parser PDF/DOCX determinístico = IMPLEMENTED;
- parser security CI = PASS;
- schema lógico com RLS = DESIGNED_NOT_APPLIED;
- Auth/isolamento = DESIGNED_NOT_PROVEN;
- testers reais = BLOCKED_BY_P0_GATES.

## 3. Arquivos canônicos

Fundação/UX:
- `career360/docs/CAREER360_BETA1_FOUNDATION_V1.md`

Segurança/privacidade:
- `career360/docs/CAREER360_SECURITY_PRIVACY_P0_V1.md`

Dados:
- `career360/docs/CAREER360_DATA_CONTRACT_V1.md`

Entrada de currículo:
- `career360/docs/CAREER360_FILE_INGESTION_V1.md`

Auth/isolamento:
- `career360/docs/CAREER360_AUTH_ISOLATION_V1.md`

Schema lógico:
- `career360/schema/CAREER360_SCHEMA_V1.sql`

Parser:
- `career360/parser/`

Protótipo:
- `career360/prototype/`

## 4. Recovery

Âncora humana:
`Recovery LSI`

Arquivos obrigatórios:
- `docs/LSI_CANONICAL_INDEX.md`
- `docs/LSI_RECOVERY_CURRENT.md`
- este manifesto.

Ponteiro estável:
- `main/docs/LSI_RECOVERY_POINTER.md`.

## 5. Superfície do cliente

Formato Beta:
- PWA/web app;
- navegador + instalação opcional;
- mesma conta celular/desktop;
- sem dependência de conta ChatGPT.

Navegação inicial:
1. Início
2. Oportunidades
3. Jornada
4. Carreira
5. Agente

Princípio:
`O CLIENTE NÃO PREENCHE. O CLIENTE CONFIRMA.`

Entradas:
- currículo PDF/DOCX;
- voz;
- texto;
- gradual como fallback.

## 6. Onboarding

Fluxo:
1. boas-vindas;
2. currículo/voz/gradual;
3. extração de currículo;
4. rascunho com confiança/evidência;
5. usuário confirma/corrige;
6. perguntar lacunas;
7. objetivos;
8. Proteção de Carreira;
9. permissões/autonomia;
10. `AGENT_READY=true`;
11. trial/prova de valor só depois.

## 7. Parser de currículo — estado

Implementação:
- PDF textual via `pypdf==6.16.2`;
- DOCX via ZIP/XML;
- máximo inicial 10 MB;
- tipo real vs extensão;
- path traversal bloqueado;
- XML DTD/entity bloqueado;
- compressão suspeita controlada;
- arquivo vazio/corrompido bloqueado;
- PDF sem texto pede novo arquivo/voz/texto;
- saída nunca confirmada automaticamente.

CI:
- workflow: `Career 360 Parser Tests`;
- run: `33708953941`;
- job: `parser-tests`;
- conclusion: SUCCESS.

`SAFE_FILE_PIPELINE` permanece PARTIAL porque upload autenticado/quarentena/storage/retention ainda não existem.

## 8. Proteção de Carreira — P0

Fluxo:
`OPORTUNIDADE -> IDENTIFICAR_EMPREGADOR -> RESOLVER_GRUPO -> PORTA_DE_PRIVACIDADE -> MATCHING/APRESENTAÇÃO`

Regras:
- atual/grupo bloqueados quando configurados;
- bloqueio adicional permitido;
- antigos empregadores podem ser sugeridos a partir do CV, nunca bloqueados silenciosamente sem política definida;
- bloqueado = `SILENT_BLOCK`;
- desconhecido = `NO_DISCLOSURE`;
- B2B não consulta se empregado específico usa Career;
- idade não entra no matching;
- pagamento não altera FIT.

## 9. Auth / isolamento — direção

Rota candidata:
- Supabase Auth + Postgres RLS em projeto Career dedicado.

Não reutilizar:
- `lsi-revenue-autopilot`;
- qualquer projeto de outro produto.

Ownership:
- `auth.uid() = user_id`;
- RLS em tabela exposta;
- anon sem grants;
- `TO authenticated` sempre combinado com ownership;
- UPDATE com USING + WITH CHECK;
- service role nunca no frontend;
- `user_metadata` nunca como autorização.

O conector Supabase exige seleção explícita de organização + confirmação de custo para criar projeto; portanto o projeto real ainda não foi criado.

## 10. Schema Candidate V1

Tabelas desenhadas:
- `career_profiles`
- `career_preferences`
- `career_employer_blocks`
- `career_documents`
- `career_profile_drafts`
- `career_confirmed_facts`
- `career_action_permissions`
- `career_audit_events`

Status: design executável versionado; não aplicado.

## 11. Matching V1

Sinais permitidos:
- experiência confirmada;
- competências confirmadas;
- senioridade/responsabilidades;
- localização/modelo;
- remuneração compatível quando suportada;
- setor;
- preferências explícitas;
- resultados reais do funil como aprendizagem controlada.

Nunca:
- fabricar fato;
- usar idade;
- aumentar FIT por plano pago;
- automatizar rejeição humana final no B2B.

## 12. Learning Engine

Aprender com:
- match;
- aceitação/rejeição + motivo;
- candidatura;
- resposta;
- entrevista;
- avanço/oferta/contratação;
- erro;
- tempo;
- intervenção humana;
- qualidade UX.

Hard policies não podem decair.
Versão atual vs versão em teste antes de promoção.

## 13. Suporte/recuperação

Camadas internas:
- L0 prevenção;
- L1 self-heal/checkpoint;
- L2 recuperação econômica;
- L3 inteligência avançada;
- L4 humano quando inevitável.

Externamente:
- Resolvido
- Preciso de Você
- Bloqueio Externo

Falha externa não justifica loop caro.

## 14. Incubação/custo

Career segue:
- Provar a Custo Zero;
- Autonomia desde a Origem;
- Estrutura Espelho;
- Evidência antes de capital;
- Próximo Degrau;
- segurança/privacidade acima de custo zero.

Capacidades lógicas:
- LSI_AI
- LSI_BROWSER
- LSI_STORAGE
- LSI_AUTH
- LSI_EMAIL
- LSI_OBSERVABILITY
- LSI_SUPPORT

## 15. Estrutura Espelho

Fluxo interno:
`CURRENT -> SHADOW -> TEST -> CANARY -> PROMOTE -> ROLLBACK_IF_NEEDED`

Regra externa:
- cliente não recria conta/perfil por troca de provider, salvo exigência inevitável de terceiro.

## 16. Beta / Primeira Turma

Alvo inicial: ~20 testers diversos.

Medir:
- onboarding completion;
- time to first value;
- relevância de match;
- ações concluídas;
- respostas/entrevistas reais;
- erros/incidentes;
- resolução autônoma;
- tempo poupado;
- satisfação;
- disposição/pagamento quando houver experimento comercial.

## 17. Gates de promoção

`SECURITY_P0=NOT_YET_PROVEN`
`CAREER_PRIVACY_P0=NOT_YET_PROVEN`
`MULTIUSER_ISOLATION=NOT_YET_PROVEN`
`SAFE_FILE_PIPELINE=PARTIAL_PARSER_CI_PASS`
`NO_FABRICATION_GUARD=PARTIAL_BY_PARSER_CONTRACT`
`AUDIT_RECOVERY=NOT_YET_PROVEN`
`CORE_RELIABILITY=NOT_YET_PROVEN`
`BETA_ENVIRONMENT=NOT_YET_PROVEN`

## 18. NEXT ACTION

1. confirmação/correção do rascunho do CV na UI;
2. projeto Auth/Data Career isolado;
3. aplicar schema + testar RLS A/B/anon;
4. storage/quarentena/retention;
5. Proteção de Carreira P0;
6. Matching V1;
7. audit/checkpoints/recovery;
8. Security/Privacy P0 tests;
9. UX/visual QA;
10. Primeira Turma.

## 19. READ_NEXT_IF_NEEDED

Ingestão:
`career360/docs/CAREER360_FILE_INGESTION_V1.md`

Auth/isolamento:
`career360/docs/CAREER360_AUTH_ISOLATION_V1.md`

Segurança:
`career360/docs/CAREER360_SECURITY_PRIVACY_P0_V1.md`

Dados:
`career360/docs/CAREER360_DATA_CONTRACT_V1.md`

UX:
`career360/docs/CAREER360_BETA1_FOUNDATION_V1.md`

## 20. DO NOT REDO

- não criar protótipo paralelo;
- não mergear main antes dos gates;
- não usar banco de outro produto;
- não tratar parser isolado como pipeline de upload seguro;
- não quebrar privacidade por conversão;
- não inventar CV;
- não bypassar MFA/CAPTCHA;
- não acoplar domínio a provider;
- não deixar mudança material apenas no chat.

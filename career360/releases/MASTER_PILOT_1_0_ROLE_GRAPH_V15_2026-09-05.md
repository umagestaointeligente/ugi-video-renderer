# LSI Career 360 — Role Graph / De-Para de Cargos V15

Data: 2026-09-05 BRT
Status: ROLE GRAPH V1.1 LIVE / SEARCH PLAN V2 LIVE / MATCHING V3.1 CHAMPION / V2 ROLLBACK

## Objetivo

Evitar perda de boas oportunidades causada por diferenças de nomenclatura entre empresas, setores, países e idiomas.

Princípio:
`NÃO PROCURAR APENAS PELO NOME DO CARGO. ENTENDER FAMÍLIA + SENIORIDADE + ESCOPO + MERCADO.`

## 1. Relações não são todas iguais

O grafo distingue:
- `exact_alias`: mesmo conceito / tradução / alias;
- `market_equivalent`: equivalência forte de mercado;
- `scope_overlap`: escopo profissional parcialmente sobreposto;
- `career_adjacent`: movimento plausível, mas não equivalência;
- `progression_up`: evolução de carreira;
- `progression_down`: nível formal abaixo;
- `excluded_lookalike`: título parecido, função diferente.

Isso impede que palavras como `Manager`, `Lead` ou `Head` sozinhas criem falso match.

## 2. Fontes registradas

### CBO — Ministério do Trabalho e Emprego
Estado: `bulk_pending`.
Uso previsto:
- ocupações brasileiras;
- famílias ocupacionais;
- títulos sinônimos;
- perfil/atividades.

### O*NET 31.0
Estado: `bulk_pending`.
Uso previsto:
- Job Titles / alternate titles;
- occupation definitions;
- related occupations;
- tasks/work activities.

### ESCO 1.2.1
Estado registrado: `live_api`.
Uso previsto:
- labels multilíngues;
- ocupações;
- competências;
- relações ocupação ↔ skill.

### LSI Curated Role Graph
Estado: `live_bulk`.
Uso:
- relações revisadas;
- traduções/aliases de mercado;
- exclusões de falsos parecidos;
- pesos e progressões.

Importante: `bulk_pending` não significa fonte importada. Não declarar CBO/O*NET hidratados até a carga e validação serem comprovadas.

## 3. Runtime atual

Tabelas existentes:
- `career_role_taxonomy_sources`;
- `career_role_concepts`;
- `career_role_aliases`;
- `career_role_relations`;
- `career_role_scope_terms`;
- `career_role_expansion_preferences`;
- `career_role_external_candidates`.

Funções:
- `career_role_resolve`;
- `career_role_expand`;
- `career_role_graph_fit`;
- `career_role_scope_fit`;
- `career_role_pair_diagnostic`;
- `career_role_scope_fit_v3`;
- `career_role_pair_diagnostic_v3`.

## 4. Exemplo real — Gerente de Categoria

`career_role_expand('Gerente de Categoria')` já expande, com pesos distintos, para exemplos como:
- Category Manager;
- Procurement Category Manager;
- Head of Category;
- Procurement Manager;
- Purchasing Manager;
- Strategic Sourcing Manager;
- Senior Buyer;
- Buyer.

Não trata todos como sinônimos.

Exemplo de proteção:
`Account Manager -> Gerente de Categoria = excluded_lookalike`.

## 5. Scope Match V3

A descrição da vaga pode complementar o título, mas não pode resgatar uma vaga apenas por palavra genérica.

V3 introduz `is_core` em termos de escopo.

Para título não resolvido, escopo só pode elevar aderência quando houver:
- pelo menos 2 evidências de escopo;
- pelo menos 1 evidência `core` da função.

Termos genéricos como `leadership`, `strategy` ou `P&L` isolados não bastam.

QA:
- `Procurement Category Manager` x `Gerente de Categoria`: relação `market_equivalent`, graph fit 0.90, mesma senioridade e múltiplas evidências de escopo;
- `Senior Buyer` x `Gerente de Categoria`: `scope_overlap`, não tratado como equivalência;
- `Account Manager` x `Gerente de Categoria`: `excluded_lookalike`;
- `Head of Sales` x `Head Comercial`: `same_concept`;
- `Talent Lead` x `Diretor Comercial`: título não resolvido + P&L isolado = baixa aderência; escopo não resgata.

## 6. Matching V3.1 — Champion

Função de engine:
`career_score_opportunity_v3`

Router canônico:
`career_score_opportunity`

Engine LIVE:
`v3.1-rolegraph`.

O V3.1 preserva os hard gates do V2 para privacidade, salário, localização, modelo de trabalho e expiração, e usa Role Graph + scope + seniority no componente de cargo.

Promoção comprovada no histórico vivo do Supabase:
`20260905183743 — career_matching_v31_promote_and_router`.

Governança atual:
- `MATCHING CHAMPION = v3.1-rolegraph`;
- `ROLLBACK = v2.0`;
- `ROLE GRAPH = v1.1 active`.

Evidência de promoção registrada no runtime:
- 7 casos sintéticos positivos;
- 4 casos sintéticos negativos/hard-gate;
- corpus 57;
- 0 mudanças de classificação antes da promoção;
- threshold 72;
- role-fit floor 0.55.

Revalidação 2026-09-06:
- 57/57 pares V2/V3.1 mantiveram classificação;
- 0 mudanças de classe;
- scores: 3 subiram, 11 caíram, 43 ficaram iguais;
- delta médio -0.69;
- router genérico e V3.1 direto produziram o mesmo resultado no smoke não persistente amostrado.

A migration viva foi espelhada em:
`career360/migrations/20260905183743_career_matching_v31_promote_and_router.sql`.

Reconciliação detalhada:
`career360/docs/MATCHING_V31_RUNTIME_RECONCILIATION_2026-09-06.md`.

## 7. Role Search Plan V2 — LIVE

Tabela:
`career_role_search_plans`.

Edge autenticada:
`career-role-search-plan` V2.

O plano usa:
- cargo atual;
- cargos-alvo;
- Role Graph;
- modo de expansão do usuário;
- termos de escopo.

Modos:
- `strict`: títulos exatos/equivalentes;
- `balanced`: equivalentes + progressão para cima + sobreposição forte de escopo;
- `broad`: amplia adjacências, preservando gates posteriores.

Regras:
- `excluded_lookalike` nunca entra;
- `progression_down` não entra por padrão;
- salário/local/modelo/privacidade continuam independentes;
- expansão de busca não aumenta FIT automaticamente.

Piloto atual:
- expansion mode: `balanced`;
- 35 títulos de busca;
- 40 termos de escopo.

Exemplos do plano atual incluem:
- Head Comercial;
- Head of Sales;
- Commercial Head;
- Diretor Comercial;
- Commercial Director;
- Sales Director;
- Director of Sales;
- Category Manager;
- Procurement Category Manager;
- Head of Category;
- Strategic Sourcing Manager;
- Procurement Manager;
- Commercial Manager;
- Senior Buyer.

## 8. Radar V5

`career-opportunity-research` V5 está ACTIVE.

Em cada ciclo:
1. lê champion/rollback do `career_engine_control`;
2. mantém o Role Search Plan V2 pronto para usuários `agent_ready`;
3. cada oportunidade nova/alterada é pontuada uma única vez pelo router canônico `career_score_opportunity`;
4. telemetria registra `matching_engine`, `rollback_engine` e `champion_match_operations`;
5. não existe mais execução paralela do antigo `v3.0-challenger` depois da promoção V3.1.

Source commit:
`d2a2665c8823f1bbc10e4ad4d4cd94c8b2ea96a9`.

Deployed SHA:
`c77784d8d50d3b861c8b9c61ede2ee385ef053d1d79da06e1305a84ac2bcbc40`.

O `career-agent` V3 também foi alinhado ao champion para não somar linhas históricas de múltiplos engines.
Source commit `b12ca88fcb38f5dcf7b3d8ef7e9cb01591f79a48`; deployed SHA `0877ba595f53f680a2a926440aa0bfba59919460515501913cb1ae405eb36724`.

As fontes ATS atuais fornecem boards completos; o Search Plan continua particularmente importante para matching e para futuras fontes keyword-based.

## 9. Market Learning Queue — LIVE

Tabela:
`career_role_unresolved_titles`.

Trigger:
`career_capture_unresolved_role_title`.

Quando uma vaga traz um título que o grafo ainda não resolve:
- título normalizado entra na fila;
- frequência é acumulada;
- fontes são registradas;
- estado fica `pending` para posterior mapeamento oficial/curado.

Exemplos atuais incluem:
- Product Manager, Stablecoin & Digital Assets;
- Sales Senior Account Executive;
- Sales Enablement & Onboarding Manager;
- Revenue Operations Analyst;
- Partner Development Manager, Brazil;
- Technical Recruiter.

A fila serve para apontar onde a taxonomia precisa crescer; não converte títulos desconhecidos em equivalência automaticamente.

## 10. Próximos passos

1. sincronizar bulk CBO;
2. sincronizar bulk O*NET;
3. usar ESCO para enriquecimento multilíngue e ocupação-skill;
4. mapear títulos frequentes da unresolved queue com evidência;
5. expandir conceitos para outras famílias de carreira;
6. ligar Search Plan a fontes por palavra-chave;
7. manter V2 como rollback operacional e revalidar V3.1 em corpus crescente antes de qualquer V4.

## Do not fake

- não chamar adjacência de equivalência;
- não aumentar score só porque palavras genéricas aparecem na descrição;
- não promover uma nova versão de matching sem benchmark e rollback comprovados;
- não declarar CBO/O*NET sincronizados enquanto `bulk_pending`;
- não relaxar salário/localização/privacidade para aumentar volume.

`LAST_VERIFIED_CHANGE=ROLE_GRAPH_V11_SEARCH_PLAN_V2_LIVE_MATCHING_V31_ROLEGRAPH_CHAMPION_V2_ROLLBACK_CORPUS_57_CLASS_STABLE_AGENT_V3_AND_RESEARCH_V5_ALIGNED`

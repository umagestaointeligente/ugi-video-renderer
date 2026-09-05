# LSI Career 360 — Role Graph / De-Para de Cargos V15

Data: 2026-09-05 BRT
Status: ROLE GRAPH LIVE FOUNDATION / SEARCH PLAN LIVE / MATCHING V3 CHALLENGER / V2 REMAINS CHAMPION

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

## 6. Matching V3 — Challenger

Função:
`career_score_opportunity_v3`

Engine:
`v3.0-challenger`.

O V3 preserva gates do V2 para:
- privacidade;
- salário;
- localização;
- modelo de trabalho;
- expiração.

Depois substitui apenas o componente de cargo por:
`ROLE GRAPH + SCOPE + SENIORITY`.

Governança:
- `MATCHING CHAMPION = v2.0`;
- `ROLE GRAPH CHALLENGER = v3.0-challenger`.

Não promover V3 até comprovar ganho de cobertura com precisão igual ou superior.

Comparação no corpus atual de 57 oportunidades:
- V2 qualificadas: 0;
- V3 qualificadas: 0;
- nenhuma mudança de classificação após hardening;
- V3 ficou mais conservador em média;
- não introduziu falsa oportunidade qualificada.

Todas as 57 oportunidades ativas foram também persistidas no challenger para baseline de comparação.

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

## 8. Radar V4

`career-opportunity-research` V4 está ACTIVE.

Em cada oportunidade nova/alterada:
1. V2 campeão é calculado e persistido;
2. V3 challenger é calculado e persistido em paralelo;
3. usuário continua vendo somente o motor campeão;
4. Role Search Plan é mantido pronto para o usuário.

Ciclo real pós-V4:
- HTTP 200;
- matching champion informado como `v2.0`;
- challenger informado como `v3.0-challenger`;
- Search Plan pronto para 1 agente ativo;
- nenhuma regressão operacional na fonte testada.

As fontes ATS atuais fornecem boards completos; portanto o Search Plan influencia especialmente o matching hoje. Futuras fontes keyword-based devem consumir os títulos do plano diretamente na descoberta.

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
7. manter champion/challenger até V3 provar ganho real.

## Do not fake

- não chamar adjacência de equivalência;
- não aumentar score só porque palavras genéricas aparecem na descrição;
- não promover V3 antes do benchmark;
- não declarar CBO/O*NET sincronizados enquanto `bulk_pending`;
- não relaxar salário/localização/privacidade para aumentar volume.

`LAST_VERIFIED_CHANGE=ROLE_GRAPH_V15_SEARCH_PLAN_V2_LIVE_V3_CHALLENGER_RADAR_PARALLEL_SCORING_UNRESOLVED_MARKET_QUEUE_LIVE`

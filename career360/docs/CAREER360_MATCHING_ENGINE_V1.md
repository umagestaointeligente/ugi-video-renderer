# LSI Career 360 — Motor de Aderência V1

Status: CANÔNICO / BETA 1.0
Data: 2026-09-03 BRT

## 1. Objetivo

Classificar oportunidades com base em dados confirmados e preferências explícitas do candidato, preservando privacidade e explicabilidade.

Princípio externo:
`MOSTRAR MENOS, MAS MOSTRAR MELHOR.`

Princípio interno:
`PRIVACIDADE ANTES DO SCORE.`

## 2. Ordem obrigatória

`OPORTUNIDADE`
→ `RESOLVER EMPREGADOR`
→ `PROTEÇÃO DE CARREIRA`
→ `GATES DUROS`
→ `SCORE DE ADERÊNCIA`
→ `CLASSIFICAÇÃO`
→ `EXPLICAÇÃO`
→ `USUÁRIO DECIDE / AUTONOMIA PERMITIDA`.

Se a Proteção de Carreira retornar `SILENT_BLOCK`, a oportunidade não entra no radar do candidato como recomendação acionável e nenhuma identidade é divulgada.

## 3. Dados permitidos no V1

- cargos-alvo explícitos;
- localização/modelo de trabalho explícitos;
- faixa salarial mínima/objetivo explicitamente informada;
- competências confirmadas pelo usuário;
- setor preferido quando explicitamente configurado;
- experiência/cargo atual confirmados;
- dados factuais da oportunidade com evidência de fonte.

## 4. Dados proibidos no score

- idade;
- raça/etnia;
- religião;
- orientação sexual;
- saúde;
- opinião política;
- condição familiar;
- preço/plano pago;
- probabilidade de pagar mais;
- qualquer dado inferido não confirmado que possa alterar o resultado material.

Pagamento nunca aumenta aderência.

## 5. Evidência salarial

`EXPLICIT` — salário/range publicado pela fonte; pode participar de gate duro.

`ESTIMATED` — estimativa/triangulação; nunca vira fato e não pode bloquear sozinho.

`HIDDEN` / `UNKNOWN` — salário não confirmado.

Se o usuário definiu piso salarial e o salário é oculto/estimado, a oportunidade pode ser classificada como:
`QUALIFICADA_SALARIO_A_CONFIRMAR`.

Se uma faixa EXPLÍCITA tiver teto abaixo do piso definido pelo usuário:
`BLOQUEADA_REQUISITO`.

## 6. Componentes iniciais do score

Pesos máximos iniciais:
- cargo/alvo: 40;
- competências confirmadas: 30;
- modelo/localização: 20;
- setor: 10.

Salário explícito é gate/compatibilidade, não mecanismo para inflar score.

O score é normalizado apenas sobre componentes aplicáveis, evitando penalizar informação que não existe.

## 7. Cargos

Usar similaridade determinística entre título da oportunidade e cargos-alvo explícitos.

V1 pode usar `pg_trgm` como componente técnico.

Score de cargo = melhor similaridade entre o título e os cargos-alvo, limitado ao peso definido.

Não reescrever currículo nem inventar senioridade para elevar aderência.

## 8. Competências

Competências candidatas só entram no score se existirem em `career_confirmed_facts` com `fact_type='skill'` e não estiverem superseded.

Competências requeridas da oportunidade devem ser estruturadas a partir da fonte e preservadas com evidência.

V1 usa correspondência normalizada determinística. Sinônimos/embeddings entram apenas em versão futura após avaliação controlada.

## 9. Modelo/localização

Se o usuário definiu modelos aceitos e a oportunidade informa um modelo fora dessa lista, classificar como `BLOQUEADA_REQUISITO` quando a preferência estiver marcada como restritiva no escopo futuro.

Na Beta V1, a lista de `work_models` é tratada como conjunto permitido quando não vazia.

Localização é aplicada quando há preferência explícita e a oportunidade não é remota.

## 10. Classificações

- `QUALIFICADA`
- `QUALIFICADA_SALARIO_A_CONFIRMAR`
- `PENDENTE_DADOS`
- `BLOQUEADA_PRIVACIDADE`
- `BLOQUEADA_REQUISITO`
- `ABAIXO_DA_ADERENCIA`
- `EXPIRADA`

Externamente usar linguagem natural em português.

## 11. Threshold inicial

Threshold operacional inicial:
`72/100`.

É um parâmetro de Beta e pode ser recalibrado com evidência. Não pode ser reduzido automaticamente apenas para gerar mais volume.

## 12. Explicabilidade

Cada match deve guardar:
- score total;
- pesos aplicáveis;
- score por componente;
- gates acionados;
- classificação;
- razão de privacidade;
- estado salarial;
- versão do motor.

A UI deve conseguir responder:
`Por que esta oportunidade apareceu para mim?`

## 13. Machine Learning futuro

O V1 é determinístico por design.

O Learning Engine pode futuramente propor pesos, sinônimos e regras challenger, mas:
- hard policies não mudam;
- privacidade não decai;
- plano pago nunca entra no FIT;
- produção só muda após avaliação champion/challenger.

## 14. Critério de PASS V1

`MATCH_ENGINE_V1=PASS` somente quando:
- schema aplicado;
- função de score aplicada;
- casos sintéticos positivos e negativos passarem;
- privacy gate estiver integrado;
- salário oculto/estimado não virar fato;
- explicação/breakdown persistido;
- nenhuma feature proibida existir no cálculo;
- Security Advisor sem finding relevante não aceita.

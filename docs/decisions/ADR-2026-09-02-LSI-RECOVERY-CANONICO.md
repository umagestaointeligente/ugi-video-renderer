# ADR — Recovery Canônico LSI entre Chats

Data: 2026-09-02 BRT
Status: ACCEPTED
Escopo: Ecossistema LSI

## Contexto

Chats têm limite de contexto. Projetos LSI são longos, paralelos e acumulam decisões técnicas, comerciais, de segurança e operação. Handoffs enormes consomem a capacidade do chat novo; dezenas/centenas de arquivos fragmentados tornam recuperação lenta e sujeita a erro.

## Decisão

Adotar um recovery hierárquico e enxuto:

1. `docs/LSI_CANONICAL_INDEX.md` — mapa/regras estáveis.
2. `docs/LSI_RECOVERY_CURRENT.md` — snapshot curto, sempre atualizado, do estado do ecossistema.
3. `docs/projects/<PROJETO>.md` — manifesto CURRENT por projeto.
4. Documentos especializados somente sob demanda.
5. ADR apenas para decisões materiais como esta.
6. Configuração machine-readable em `config/lsi/recovery-policy.json`.

Comando único:
`LSI::RECOVERY::CURRENT`

Primeira linha esperada:
`LSI_RECOVERY=TRUE`

## Regras

- Não reler biblioteca inteira por padrão.
- Não reconstruir estado por memória de conversa.
- Runtime/evidência viva vence para estado operacional atual.
- Git canônico vigente vence para arquitetura/política intencional.
- CURRENT é atualizado em vez de duplicado a cada alteração pequena.
- Git history preserva histórico de mudanças.
- Mudança material atualiza artefato + manifesto + CURRENT na mesma rodada ou imediatamente após.
- Segredos e dados de clientes nunca entram nessa documentação.

## Consequências positivas

- recuperação rápida em chat novo;
- menos consumo de contexto;
- menor risco de divergência;
- continuidade exata do NEXT_ACTION;
- detalhes disponíveis sem sobrecarregar o readback inicial;
- arquitetura aplicável a Career, NEXO e futuros projetos da Incubadora LSI.

## Trade-off

Exige disciplina operacional: estado canônico deve ser atualizado durante o trabalho, não apenas quando o chat estiver terminando.

## Não fazer

- um handoff monolítico de centenas/milhares de páginas;
- um arquivo novo para toda pequena conversa;
- snapshots duplicados com números de versão sem mudança incompatível;
- confiar somente em chat history como memória operacional.

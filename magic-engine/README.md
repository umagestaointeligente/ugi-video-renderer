# Lola Magic Engine V1

Núcleo autônomo de mídia multi-canal, desenhado para custo marginal zero no MVP e operação fail-closed.

## Canais V1
1. `curiosidades` — conteúdo factual transformativo com assets licenciados/originais.
2. `universo_esportes` — contexto, curiosidades e análise; transmissões/clipes de terceiros nunca passam automaticamente no Rights Gate.
3. `podcast_intelligence` — cortes somente com autorização/licença ou transformação validada.
4. `cinema_transformativo` — análise/crítica; trechos de filmes permanecem bloqueados sem base de direitos registrada.
5. `sleep_focus` — áudio/visual original gerado localmente; prioridade de publicação longa no YouTube.

## Arquitetura
`DISCOVERY -> TREND_SCORE -> VIRALITY_SCORE -> RIGHTS_GATE -> FACT_GATE -> CONTENT_PLAN -> RENDER -> QA -> PUBLISH -> ANALYTICS -> LEARNING`

## Princípios
- Zero-cost-first: GitHub Actions standard runner em repo público + FFmpeg/Kokoro + fontes públicas/APIs free-tier.
- Autonomia com gates: nenhum conteúdo com direito incerto é publicado.
- Sem dependência obrigatória de LLM paga.
- Um master por conteúdo e adapters por plataforma.
- Toda decisão gera evidência JSON para aprendizado posterior.
- Credenciais de plataforma são secrets; nunca entram no repositório.

## Status da V1
O workflow `magic-engine-v1.yml` executa radar periódico, classifica oportunidades e produz manifests. Publicação só é habilitada quando as credenciais OAuth/API das contas forem conectadas e os gates de cada item estiverem verdes.

## Gates obrigatórios
- `RIGHTS_GATE=GREEN`
- `FACT_GATE=PASS`
- `QA_GATE=PASS`
- `COST_GATE=PASS`
- `PLATFORM_AUTH=READY`

Qualquer falha resulta em `HARD_STOP` para aquele item, sem bloquear os demais canais.

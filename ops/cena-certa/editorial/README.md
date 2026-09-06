# Cena Certa — Editorial Radar Engine

Objetivo: transformar o Cena Certa em operação híbrida de vídeo + curadoria editorial sem alterar a Factory V2 de vídeos.

## Cadência alvo
- 8 vídeos/dia: Facebook Reels + Instagram Reels + TikTok + YouTube Shorts.
- 4 editoriais/dia: Facebook + Instagram + TikTok (photo/carousel quando suportado).
- 4 Stories/dia: Instagram + Facebook. TikTok recebe adaptação em photo post ou microvídeo enquanto Story via publisher não estiver comprovado.
- YouTube permanece vídeo-only por decisão editorial atual.

## Radar D+2
O radar diário pesquisa o horizonte D+2 e cruza fontes oficiais de streaming, bilheteria, festivais, releases, imprensa e sinais públicos de comunidade/social.

## Gates editoriais
Um item só pode ir ao planner quando TODOS passarem:
1. FACT_PASS — afirmações verificadas em fonte primária/alta autoridade.
2. FRESHNESS_PASS — fatos dinâmicos revalidados no dia ou antes da publicação.
3. ASSET_SOURCE_PASS — origem visual identificada.
4. ASSET_RIGHTS_PASS — press/editorial use ou licença explícita compatível.
5. VISUAL_RELEVANCE_PASS — imagem identifica inequivocamente a obra/pessoa/evento.
6. COPY_PASS — texto original Cena Certa, sem copiar crítica de terceiros.
7. CTA_PASS — pergunta/opinião que gere conversa sem clickbait enganoso.
8. PLATFORM_PASS — formato compatível com a rede.

## Asset policy
Preferência: press kit oficial / Media Center / Global Asset Hub / festival press distribution.
Não assumir que imagem pública, pôster ou frame é reutilizável. `OFFICIAL_ASSET_RIGHTS_PENDING` continua bloqueado.
Assets Disney de press pages com termo editorial só podem ser usados segundo as limitações declaradas, sem alteração indevida. Netflix/Sony/Biennale podem exigir conta/acreditação; nesse caso o gate permanece pendente até acesso/termos comprovados.

## Trend score 0–100
- Freshness: 25
- Relevância Brasil: 20
- Social/engagement signal: 20
- Fonte factual oficial: 15
- Asset readiness: 10
- Potencial de discussão: 10

## Estados
`DISCOVERED -> FACT_PASS -> ASSET_PENDING -> ASSET_RIGHTS_PASS -> CREATIVE_READY -> QA_PASS -> SCHEDULED -> PUBLISHED_RECONCILED`

Fail closed: não publicar item com direitos visuais, fato dinâmico ou QA pendente.

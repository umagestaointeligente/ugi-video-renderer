# Cena Certa — Editorial Radar Engine

Objetivo: transformar o Cena Certa em operação híbrida de vídeo + curadoria editorial sem alterar a Factory V2 de vídeos.

## Cadência alvo
- 8 vídeos/dia: Facebook Reels + Instagram Reels + TikTok + YouTube Shorts.
- 4 editoriais/dia: Facebook Reels + Instagram Reels + TikTok, sempre em VÍDEO.
- 4 Stories/dia: Instagram + Facebook, somente onde o formato Story nativo estiver disponível e comprovado pelo publisher.
- Não criar adaptação, repost ou microvídeo compensatório no TikTok apenas porque Story nativo não está disponível.
- YouTube permanece vídeo-only para a linha principal por decisão editorial atual; os editoriais não são enviados ao YouTube salvo decisão posterior explícita.

## Radar D+2
O radar diário pesquisa o horizonte D+2 e cruza fontes oficiais de streaming, bilheteria, festivais, releases, imprensa e sinais públicos de comunidade/social.

## Gates editoriais
Um item só pode ir ao planner quando TODOS passarem:
1. FACT_PASS — afirmações verificadas em fonte primária/alta autoridade.
2. FRESHNESS_PASS — fatos dinâmicos revalidados no dia ou antes da publicação.
3. ASSET_SOURCE_PASS — origem audiovisual identificada.
4. ASSET_RIGHTS_PASS — press/editorial/media use ou licença explícita compatível.
5. VISUAL_RELEVANCE_PASS — todo material mostrado pertence inequivocamente à obra/pessoa/evento discutido naquele trecho.
6. MOTION_VIDEO_PASS — a peça editorial final é vídeo real com material audiovisual em movimento; não é foto, pôster, slideshow, zoom/parallax de still nem card animado usado como substituto de vídeo.
7. COPY_PASS — texto original Cena Certa, sem copiar crítica de terceiros.
8. CTA_PASS — pergunta/opinião que gere conversa sem clickbait enganoso.
9. PLATFORM_PASS — formato compatível com a rede.

## Editorial audiovisual hard gate — regra canônica a partir de 10/09/2026
- TODO editorial novo do Cena Certa é uma peça em VÍDEO.
- A base visual deve ser clipe, EPK, B-roll, cena, featurette ou outro MATERIAL AUDIOVISUAL EM MOVIMENTO oficialmente liberado pelo estúdio/produtora para press/editorial/media use ou sob licença explicitamente compatível.
- O assunto determina o material: lançamento mostra o próprio lançamento; recomendação mostra os próprios títulos recomendados; comparação alterna material dos títulos comparados; discussão de personagem/franquia mostra a obra/personagem discutido.
- É HARD REJECT usar pôster, key art, still, foto, frame congelado, carrossel de fotos, slideshow, zoom em imagem, parallax de imagem ou card tipográfico como conteúdo editorial principal ou como fallback para completar volume.
- É HARD REJECT usar stock, imagem decorativa, ilustração genérica, vídeo genérico ou qualquer visual sem nexo direto com a fala naquele momento.
- Texto, headline, CC e CTA podem ser sobrepostos ao vídeo pertinente, desde que o material da obra continue sendo o protagonista visual.
- Se uma pauta possuir apenas stills/pôsteres autorizados e não houver vídeo autorizado utilizável, TROCAR A PAUTA. Não converter imagem em falso vídeo para cumprir a meta.
- Nenhum editorial é `QA_PASS` sem MOTION_VIDEO_PASS e THEME_MATCH_PASS.
- Esta regra prevalece sobre qualquer plano diário, versão anterior deste README ou memória operacional que permita editorial estático.

## Story audiovisual automático — padrão canônico
Todo Story novo do Cena Certa deve ser tratado como peça audiovisual curta, e não como simples imagem estática, salvo impedimento técnico explícito e aprovação excepcional.

Padrão obrigatório:
1. ASSET OFICIAL RELACIONADO — priorizar clipe audiovisual diretamente ligado à obra/pauta, com ASSET_RIGHTS_PASS. Quando a exceção de Story permitir still/pôster, nunca confundir essa exceção com a regra dos 4 editoriais de feed, que permanecem vídeo-only.
2. MOVIMENTO ELEGANTE — quando houver vídeo, usar cortes/transições discretos; na exceção autorizada de Story baseado em still, microanimação mínima sem distorcer o asset. Proibidos zoom brusco, flash, fundo preto prolongado ou movimento sem nexo.
3. TRILHA LICENCIADA COERENTE — faixa instrumental com licença compatível e clima semanticamente aderente. Não reutilizar música original da obra sem licença específica.
4. CTA CURTO — pergunta, escolha ou chamada simples de interação; o conteúdo visual continua protagonista.
5. DURAÇÃO ALVO — 7 a 10 segundos para Story curto; clipes oficiais podem variar quando material/licença exigirem.
6. ÁUDIO — trilha incorporada ao arquivo final quando o publisher não expuser biblioteca musical nativa. Se houver fala/narração, música em segundo plano.
7. THEME_MATCH_PASS — asset, movimento, trilha e CTA precisam falar do mesmo assunto.
8. STORY_QA_PASS — verificar direitos, relevância visual, safe area, ausência de distorção, legibilidade e ausência de card text-only.

Hard rejects específicos de Story:
- fundo monocromático + texto como conteúdo principal;
- imagem genérica ou stock não relacionado;
- asset oficial acompanhado de música sem relação temática;
- música comercial/original da obra sem licença compatível;
- CTA maior ou mais dominante que o próprio conteúdo visual;
- qualquer Story sem THEME_MATCH_PASS e STORY_QA_PASS.

Regra de distribuição de Stories:
- Publicar Story somente nas redes em que o formato Story nativo estiver realmente disponível e validado no publisher.
- Hoje, a rota comprovada é Facebook Stories + Instagram Stories.
- Se TikTok Story não estiver disponível, não publicar a mesma peça no TikTok em formato alternativo apenas para compensar a ausência do recurso.

## Asset policy
Preferência: press kit oficial / Media Center / Global Asset Hub / EPK / B-roll / festival press distribution.
Não assumir que um vídeo publicamente visível é reutilizável. `OFFICIAL_ASSET_RIGHTS_PENDING` continua bloqueado.
Assets Disney/20th/Pixar/Marvel/Lucasfilm provenientes de press pages e media hubs só podem ser usados conforme as limitações declaradas e com proveniência registrada. Netflix/Sony/Biennale e outros portais que exijam conta/acreditação permanecem pendentes até acesso e termos comprovados.

## Trend score 0–100
- Freshness: 25
- Relevância Brasil: 20
- Social/engagement signal: 20
- Fonte factual oficial: 15
- Asset readiness: 10
- Potencial de discussão: 10

## Estados
`DISCOVERED -> FACT_PASS -> ASSET_PENDING -> ASSET_RIGHTS_PASS -> MOTION_VIDEO_PASS -> CREATIVE_READY -> QA_PASS -> SCHEDULED -> PUBLISHED_RECONCILED`

Fail closed: não publicar item com direitos audiovisuais, fato dinâmico, relevância visual, MOTION_VIDEO_PASS ou QA pendente.

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

## Visual editorial hard gate
- Editorial pode usar pôster oficial, key art, still, foto de cena, frame, clipe, EPK ou outro material visual oficialmente liberado para press/editorial/media use.
- O visual usado DEVE pertencer diretamente ao filme, série, personagem, lançamento ou pauta específica discutida naquele editorial.
- Pôster e foto estática são permitidos quando forem assets oficiais/utilizáveis e forem editorialmente relevantes.
- Carrosséis podem combinar pôsteres, stills, fotos e clipes de títulos diferentes somente quando cada slide identifica claramente o título citado naquele slide.
- É HARD REJECT usar fundo monocromático, página vazia, bloco de cor ou card apenas tipográfico como substituto do material relacionado à obra.
- É HARD REJECT usar imagem decorativa, stock, ilustração genérica ou qualquer visual sem nexo direto com o assunto apenas para preencher o criativo.
- Texto, headline e CTA podem ser sobrepostos ao material pertinente, desde que não transformem a peça em uma página essencialmente textual.
- Se uma pauta não possuir material visual legalmente utilizável e diretamente relacionado, TROCAR A PAUTA por outra relevante que possua asset adequado. Não criar fallback genérico ou monocromático.
- Esta regra prevalece sobre qualquer plano diário anterior que sugira `original typographic card`, `abstract Cena Certa visual`, `text-led poll` ou equivalente como fallback sem imagem/material da obra.

## Story audiovisual automático — padrão canônico
Todo Story novo do Cena Certa deve ser tratado como peça audiovisual curta, e não como simples imagem estática, salvo quando houver impedimento técnico explícito e aprovação excepcional.

Padrão obrigatório:
1. ASSET OFICIAL RELACIONADO — usar pôster, key art, still, foto, frame ou clipe diretamente ligado à obra/pauta, com ASSET_RIGHTS_PASS.
2. MICROANIMAÇÃO ELEGANTE — criar movimento discreto de câmera, parallax leve, recorte dinâmico, transição suave ou animação mínima que preserve a integridade do asset. Proibidos zoom brusco, efeito genérico chamativo, flash, fundo preto prolongado ou movimento sem nexo.
3. TRILHA LICENCIADA COERENTE — usar faixa instrumental com licença compatível e clima semanticamente aderente à obra. Ex.: ficção científica -> synth/ambient; super-herói -> épico/orquestral; nostalgia automotiva -> rock/upbeat; fantasia -> orquestral/fantasia. Não reutilizar música original do filme/série sem licença específica.
4. CTA CURTO — pergunta, escolha ou chamada simples de interação, visualmente legível e sem ocupar a peça inteira. O asset continua sendo o protagonista visual.
5. DURAÇÃO ALVO — 7 a 10 segundos para Story baseado em pôster/still; clipes oficiais podem variar quando o material e a licença exigirem outra duração.
6. ÁUDIO — trilha incorporada ao arquivo final antes do upload quando o publisher não expuser biblioteca musical nativa. Se houver fala/narração, a música deve permanecer em segundo plano.
7. THEME_MATCH_PASS — asset, movimento, trilha e CTA precisam falar do mesmo assunto. Qualquer elemento genérico ou desconectado reprova a peça.
8. STORY_QA_PASS — antes do planner, verificar relevância visual, direitos do asset, licença da música, safe area, ausência de card monocromático/text-only, ausência de distorção e legibilidade do CTA.

Hard rejects específicos de Story:
- fundo monocromático + texto como conteúdo principal;
- imagem genérica ou stock não relacionado;
- asset oficial acompanhado de música sem relação temática;
- música comercial/original da obra sem licença compatível;
- CTA maior ou mais dominante que o próprio conteúdo visual;
- Story estático simples quando a rota automática de microanimação estiver disponível;
- qualquer Story agendado sem THEME_MATCH_PASS e STORY_QA_PASS.

Enquanto o publisher conectado não oferecer Story nativo no TikTok, a mesma peça deve ser adaptada como microvídeo vertical regular para TikTok quando fizer sentido editorialmente, sem chamá-la de Story nativo.

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

# Cena Certa — 12 agendamentos confirmados — 10/11/2026

Marca: Cena Certa Ofc / 6809869. Fuso: America/Sao_Paulo.

**12/12 agendamentos conferidos no Planner; 12/12 arquivos recebidos pelo Metricool têm o SHA-256 idêntico ao master local.** Status na consulta: PENDING, aguardando o horário. Agendamento não equivale a publicação concluída.

| Rede | Obra | Horário BRT | ID / Planner |
|---|---|---|---|
| Facebook Reels | Intocáveis (2011) | 21:10 | [423831478](https://app.metricool.com/planner/calendar?blogId=6809869&openWithPostUuid=1122090293981104714) |
| Facebook Reels | Um Senhor Estagiário (2015) | 22:10 | [423831605](https://app.metricool.com/planner/calendar?blogId=6809869&openWithPostUuid=6506291858332076320) |
| Facebook Reels | À Procura da Felicidade (2006) | 23:10 | [423831818](https://app.metricool.com/planner/calendar?blogId=6809869&openWithPostUuid=8724248731144962780) |
| Instagram Reels | Extraordinário (2017) | 21:15 | [423829797](https://app.metricool.com/planner/calendar?blogId=6809869&openWithPostUuid=-5110019752701770596) |
| Instagram Reels | Meninas Malvadas (2004) | 22:15 | [423832009](https://app.metricool.com/planner/calendar?blogId=6809869&openWithPostUuid=5424850151909639161) |
| Instagram Reels | Top Gun: Maverick (2022) | 23:15 | [423832117](https://app.metricool.com/planner/calendar?blogId=6809869&openWithPostUuid=3174317318456885567) |
| TikTok | As Branquelas (2004) | 21:05 | [423832458](https://app.metricool.com/planner/calendar?blogId=6809869&openWithPostUuid=-5192378564419239859) |
| TikTok | Se Beber, Não Case! (2009) | 22:05 | [423832553](https://app.metricool.com/planner/calendar?blogId=6809869&openWithPostUuid=-1269468006601700489) |
| TikTok | Gente Grande (2010) | 23:05 | [423832699](https://app.metricool.com/planner/calendar?blogId=6809869&openWithPostUuid=-7668972853826204346) |
| YouTube Shorts | Batman: O Cavaleiro das Trevas (2008) | 21:20 | [423833012](https://app.metricool.com/planner/calendar?blogId=6809869&openWithPostUuid=-6657112836427921286) |
| YouTube Shorts | Breaking Bad (2008) | 22:20 | [423833166](https://app.metricool.com/planner/calendar?blogId=6809869&openWithPostUuid=44554833174743389) |
| YouTube Shorts | Missão: Impossível — Efeito Fallout (2018) | 23:20 | [423833281](https://app.metricool.com/planner/calendar?blogId=6809869&openWithPostUuid=5438097070426179644) |

## Método recuperável que funcionou

1. Recuperar ou renderizar o MP4 local; confirmar arquivo, codec, legendas e hash.
2. Consultar marca e Planner para impedir duplicatas e escolher horários futuros.
3. Chamar createScheduledPost do conector Metricool com blogId=6809869, date ISO futuro, info como JSON e mediaFiles=[caminho_absoluto_do_MP4]. O conector envia os bytes locais e retorna uma mídia hospedada no static.metricool.com.
4. Consultar novamente o Planner, conferindo ID, data/fuso, rede, formato, draft=false e vídeo anexado.
5. Baixar a mídia retornada e comparar SHA-256 com o master local. Só então confirmar o agendamento.

Não foi necessário Creative Claw, crédito de geração, link público do Google Drive ou credencial R2 local. Um arquivo foi copiado ao Drive durante a avaliação de alternativas e permaneceu privado; a entrega confirmada não usa esse arquivo.

## Estrutura usada no conector

```json
{
  "blogId": "6809869",
  "date": "DATA_FUTURA_ISO_COM_OFFSET",
  "info": "JSON_SERIALIZADO_DOS_DADOS_DO_POST",
  "mediaFiles": [
    "CAMINHO_ABSOLUTO_DO_MP4_LOCAL"
  ]
}
```

No info: text, providers=[{network}], publicationDate={dateTime local,timezone:America/Sao_Paulo}, autoPublish=true, draft=false, media=[].
Instagram: instagramData={type:REEL,autoPublish:true,showReelOnFeed:true}.
Facebook: facebookData={type:REEL,title}. Omitir boost: o campo não aceita booleano.
YouTube: youtubeData={title,type:short,privacy:public,category:ENTERTAINMENT,madeForKids:false,tags:[]}.
TikTok: tiktokData={privacyOption:PUBLIC_TO_EVERYONE,title,autoAddMusic:false,disableComment:false,disableDuet:false,disableStitch:false,commercialContentThirdParty:false,commercialContentOwnBrand:false}.

A operação inicial do Facebook falhou na desserialização de boost=false, antes de criar o post. Uma consulta ao Planner confirmou ausência; o campo foi omitido e a nova tentativa gerou um único post. Nenhum retry cego foi realizado.

## Limites preservados

A busca de 180 dias retornou 422 registros e não encontrou os títulos escolhidos. A comparação visual integral continua incompleta; não converter isso em PASS de 180 dias. Direitos de republicação continuam NOT_VERIFIED; não foi criada licença fictícia. As legendas usam ASR local com ajustes editoriais; não são uma transcrição certificada. O lote foi agendado após a instrução de Paulo para encontrar alternativa e fazer os agendamentos, com as limitações previamente comunicadas.

## Continuidade

A rotina Cena Certa diário continua ativa, pela manhã por volta das 08h BRT, preparando o dia seguinte. O prompt foi atualizado com o caminho de upload comprovado e os 12 IDs para impedir recriação. Não prometer entrega real antes de conferir as redes. A implementação e os recibos operacionais estão no PR #97 do repositório umagestaointeligente/ugi-video-renderer; o PR continua em rascunho, sem merge.


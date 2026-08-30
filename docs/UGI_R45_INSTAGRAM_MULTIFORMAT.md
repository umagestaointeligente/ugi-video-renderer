# UGI R45 — Instagram MultiFormat

## Estado

Produção ativa desde 30/08/2026.

Worker autoritativo: `lola-operacional-ugi.umagestaointeligente.workers.dev`

Publisher: **Buffer exclusivamente**.

Um conteúdo só pode ser declarado `SCHEDULED` depois de readback real com `bufferPostId`, `status=scheduled` e horário correspondente ao solicitado.

## Formatos ativos

| type | destino | asset | tamanho | publicação |
|---|---|---|---|---|
| `reel` | Instagram Feed/Reels | MP4 | 9:16 | pipeline R43.8.6 existente |
| `carousel` | Instagram Feed | 5–10 PNGs | 1080×1350 | R45 |
| `visual_post` | Instagram Feed | PNG | 1080×1350 | R45 |
| `story_image` | Instagram Stories | PNG | 1080×1920 | R45 |

## Formatos planejados

`story_video` entra em R45.1 somente quando houver QA e publicação real comprovada. Música, quando usada em Story autônomo, deverá ser incorporada ao MP4 por fonte licenciada/permitida. Não declarar música nativa do Instagram, link sticker, enquete ou outros stickers como automáticos sem suporte real da API.

## Rotas R45

- `POST /api/r45/generate`
- `POST /api/r45/static-approval`
- `GET /api/r45/static-eligibility/{draftId}`
- `POST /api/r45/static-publish`
- `GET /api/r45/static-publication-status?id={draftId}`

## Contrato editorial

Todo manifest deve responder:

1. Por que alguém pararia o feed para consumir isso?
2. Qual utilidade concreta é entregue?
3. Qual ação a pessoa consegue executar depois?
4. Por que este formato é melhor que um Reel para este conteúdo?

Evitar por padrão:

- executivo genérico + overlay escuro;
- aparência de anúncio corporativo;
- logo como protagonista;
- motivação sem ferramenta;
- mesmo template todos os dias;
- CTA genérico de seguir/link na bio sem explicar o valor.

## Frequência do sprint de 14 dias

Stories: alvo inicial de 4/dia; mínimo 2; máximo 6 durante o teste.

Ondas de referência:

- manhã: 2 Stories a partir de 09:00, espaçados aproximadamente 7 min;
- noite: 2 Stories a partir de 18:00, espaçados aproximadamente 12 min.

Feed semanal de referência:

- 3 carrosséis;
- 2 posts visuais;
- 2 Reels.

Máximo inicial: 2 publicações de feed por dia e, fora de pilotos controlados, pelo menos 3 horas entre posts de feed.

## Manifest R45

Campos principais por item:

```json
{
  "contentId": "UGI-YYYYMMDD-IG-...",
  "type": "carousel | visual_post | story_image",
  "publish": true,
  "dueAt": "2026-08-30T18:00:00-03:00",
  "topic": "...",
  "objective": "...",
  "hook": "...",
  "key_message": "...",
  "instructions": "...",
  "cta": "...",
  "slides": 7
}
```

`slides` é usado somente para carrossel e deve ficar entre 5 e 10 na política editorial atual.

## Hub autônomo

Fila:

`control-plane/instagram-multiformat/queue/*.json`

Receipts:

`control-plane/instagram-multiformat/receipts/*.json`

Workflow:

`.github/workflows/ugi-instagram-multiformat-hub.yml`

O Hub roda por push e também em reconciliação recorrente. Receipts terminais com `ok=true` são idempotentes e não devem ser republicados.

## Gate

Fluxo obrigatório:

`manifest → geração → asset real → QA de dimensões/integridade → aprovação → Buffer → readback → receipt`.

Sem receipt real, não declarar agendamento concluído.

## Métricas do sprint

Prioridade:

- alcance de não seguidores;
- saves;
- shares;
- visitas ao perfil;
- follows;
- cliques na bio;
- conclusão dos Stories.

Revisões formais em D+3, D+7 e D+14.

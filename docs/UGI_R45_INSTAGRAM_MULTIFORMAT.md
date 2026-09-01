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

## Story Standard V2 — effective 2026-09-01

Stories passam a operar como **gatilhos de atenção e navegação**, não como slides corporativos estáticos.

Estrutura preferencial:

`FATO/IMAGEM REAL → GANCHO/NÚMERO → LEITURA DE GESTÃO → PERGUNTA/CTA`

Regras obrigatórias:
- fato real exige visual relacionado ao fato;
- pessoa real exige a pessoa correta;
- empresa real exige contexto visual reconhecível da empresa;
- evento real deve mostrar local, consequência, infraestrutura, operação, objeto ou evidência contextual relacionada;
- quando houver menores em evento sensível, evitar mostrar crianças identificáveis ou em sofrimento; usar escola/local, danos, equipe adulta, resgate, infraestrutura ou aftermath;
- conceito abstrato pode usar arte editorial gerada, preferencialmente com elemento humano;
- um único insight principal por Story;
- hook curto e visualmente dominante;
- design premium, moderno, com forte hierarquia e contraste;
- sem ghost text, lorem, idiomas aleatórios ou ruído decorativo;
- música moderna e coerente; evitar chiptune, ringtone, game-like e trilha morta;
- músicas diferentes entre Stories, salvo sequência deliberada;
- CTA deve levar a perfil, feed, carrossel ou material UGI quando a ponte tiver sido conquistada.

Referência visual de direção aprovada: cena/contexto real ocupando parte relevante do frame + painel editorial UGI + número/fato de forte impacto + pergunta de gestão.

## Carousel Standard V2 — real story / leader / company

Quando o carrossel for ancorado em pessoa, empresa ou caso real:

1. **Slide 1** — foto/contexto real + hook forte.
2. **Slide 2** — contexto: o que aconteceu.
3. **Slide 3** — por que importa.
4. **Slide 4** — mecanismo/decisão de gestão.
5. **Slide 5** — ensinamento prático.
6. **Slide 6** — síntese/pergunta/transição; evitar depender novamente de retrato frontal da figura pública.
7. **Slide 7** — CTA 100% UGI, sem figura pública e sem aparência de endosso.

Hard gates de figura pública:
- mesma pessoa ao longo da parte editorial;
- variar enquadramento é permitido; trocar identidade não;
- não fabricar citação;
- separar claramente citação verificada de interpretação UGI;
- CTA comercial nunca pode sugerir que a pessoa recomenda ou endossa a UGI.

## Carousel audio rule

Não usar a técnica "primeiro card em vídeo com música + demais cards estáticos" como substituto de áudio contínuo: quando o usuário avança, a música deixa de acompanhar o carrossel e a experiência fica quebrada.

Enquanto a rota automática não suportar música nativa contínua em carrossel, preferir carrossel estático silencioso e editorialmente forte.

## Static Post Standard V2

Post estático deve ter uma única razão forte para parar o feed:
- fato/número verificado;
- dilema executivo;
- citação com atribuição confirmada;
- framework visual memorável.

Evitar arte motivacional genérica e imagem de IA sem relação concreta com o tema.

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

Além do QA técnico, antes da publicação o asset deve passar por:
- `VISUAL_CONTEXT_PASS`: visual realmente relacionado ao assunto;
- `HOOK_PASS`: primeira tela/frame cria motivo para continuar;
- `IDENTITY_CONTINUITY_PASS`: figura pública/empresa mantida corretamente;
- `ENDORSEMENT_SAFETY_PASS`: CTA UGI sem falso endosso;
- `TEXT_CLEAN_PASS`: sem gibberish, ghost text ou idioma aleatório;
- `MUSIC_FIT_PASS` quando houver áudio.

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

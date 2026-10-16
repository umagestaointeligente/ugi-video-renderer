# Cena Certa — status de agendamento 16/10/2026

**Marca:** Metricool 6809869 (Cena Certa Ofc). **Fuso:** America/Sao_Paulo.
**Conferência:** 16/10/2026, 12h47 de Brasília. `getScheduledPosts` para a data inteira retornou `data=[]` (nenhum post agendado).
**Resultado:** 12 masters V2 tecnicamente aprovados; 0 liberados e 0 agendamentos confirmados. Não foram chamadas operações de criação no Metricool: os recibos permanecem bloqueados.

## Horários possíveis, ainda futuros na consulta e ainda NÃO agendados

Os horários abaixo derivam do mapa de atividade real do Metricool em 16/10, com defasagem de minutos entre plataformas. São propostas operacionais, não postagens.

| Rede | Obra | Master V2 na Biblioteca | Horário Brasília | QA técnico | Liberação | Metricool ID |
|---|---|---|---|---|---|---|
| tiktok | As Branquelas | `CC-OCT16-TIKTOK-01-V2-REVIEW.mp4` | 15:05 (proposto) | PASS | BLOQUEADA | — |
| tiktok | Se Beber, Não Case! | `CC-OCT16-TIKTOK-02-V2-REVIEW.mp4` | 16:15 (proposto) | PASS | BLOQUEADA | — |
| tiktok | A Hora do Rush 2 | `CC-OCT16-TIKTOK-03-V2-REVIEW.mp4` | 18:15 (proposto) | PASS | BLOQUEADA | — |
| instagram | Meninas Malvadas | `CC-OCT16-INSTAGRAM-04-V2-REVIEW.mp4` | 13:10 (proposto) | PASS | BLOQUEADA | — |
| instagram | Extraordinário | `CC-OCT16-INSTAGRAM-05-V2-REVIEW.mp4` | 15:25 (proposto) | PASS | BLOQUEADA | — |
| instagram | Top Gun: Maverick | `CC-OCT16-INSTAGRAM-06-V2-REVIEW.mp4` | 17:20 (proposto) | PASS | BLOQUEADA | — |
| facebook | Intocáveis | `CC-OCT16-FACEBOOK-07-V2-REVIEW.mp4` | 13:30 (proposto) | PASS | BLOQUEADA | — |
| facebook | Um Senhor Estagiário | `CC-OCT16-FACEBOOK-08-V2-REVIEW.mp4` | 15:45 (proposto) | PASS | BLOQUEADA | — |
| facebook | À Procura da Felicidade | `CC-OCT16-FACEBOOK-09-V2-REVIEW.mp4` | 16:40 (proposto) | PASS | BLOQUEADA | — |
| youtube | Batman: O Cavaleiro das Trevas | `CC-OCT16-YOUTUBE-10-V2-REVIEW.mp4` | 13:55 (proposto) | PASS | BLOQUEADA | — |
| youtube | Breaking Bad | `CC-OCT16-YOUTUBE-11-V2-REVIEW.mp4` | 14:55 (proposto) | PASS | BLOQUEADA | — |
| youtube | Missão: Impossível — Efeito Fallout | `CC-OCT16-YOUTUBE-12-V2-REVIEW.mp4` | 16:55 (proposto) | PASS | BLOQUEADA | — |

## Fontes canônicas

- Manual: docs/CENA_CERTA_METODO_PRODUCAO.md.
- V2 QA: ops/cena-certa-oct16/CONTINUIDADE_QA_V2.md.
- Biblioteca: Cena_Certa_12_Candidatos_V2_Revisao_2026-10-16.zip e doze MP4s V2 individuais.
- Decisão anterior de Paulo: ops/cena-certa-oct16/user-rights-decision.json — PROCEED_WITH_UNVERIFIED_RIGHTS. Permite produzir candidatos; não concede licença nem suspende o gate de 180 dias.

## Bloqueios comprovados

1. História de 180 dias: NOT_VERIFIED; apenas 66 comparações internas entre vídeos do lote, sem abrangência de 180 dias.
2. Direitos de republicação: NOT_VERIFIED para 12/12 (decisão de prosseguir registrada sem alegar licença).
3. Revisão integral do áudio PT-BR, sincronismo/legendas e alinhamento ao editorial: PENDING para 12/12; legendas de diálogo NOT_ADDED.
4. Alertas: TikTok 03 tem legendas embutidas bilíngues; YouTube 11 traz marca AdoroCinema; Batman não é interrogatório, Facebook Felicidade não é oferta de emprego, Top Gun não é voo solo.

**Nenhum post foi criado, alterado ou removido.** Depois de liberar o item por revisão e histórico, conferir o horário ainda futuro, subir master em URL aceito pelo Metricool, consultar duplicatas, agendar na rede única e realizar readback de id e plannerUrl.

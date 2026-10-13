# CENA CERTA — Método operacional canônico (restauração em 13/10/2026)

**Base observada:** runs efetivamente aprovados `37712185703` (08/10), `38022343452` (11/10), `38196309142` (12/10); issues #75, #77, #80; scripts `scripts/cena_certa_oct09_pack.py`, `scripts/cena_certa_oct11_pack.py`, `scripts/cena_certa_oct12_pack.py`.

Este documento fixa **o método**, não a programação de um único dia. Os critérios de conteúdo já aprovados pelo usuário continuam prevalecendo sobre os títulos usados nas execuções antigas.

## Procedimento obrigatório — nesta ordem

1. **Editorial por rede**: 3 publicações para TikTok, 3 para Instagram, 3 para Facebook, 3 para YouTube; obras reais em movimento, filmes e séries novos/consagrados, diversidade, cenas claras com payoff; YouTube sem títulos/fontes Globo; não trocar cenas por curtas independentes, poster, slideshow, imagens fixas ou vídeo abstrato; sem trailer no vídeo final.
2. **Descoberta da fonte antes do gate de produção**: pesquisa de fontes reais (páginas e clipes oficiais, provedores de mídia e, quando pertinente, Wikimedia Commons); usar `yt-dlp` como nos probes Oct09–Oct12 e `ffprobe`/FFmpeg para fontes diretas. Capturar URL, origem e identidade do conteúdo. Um link ou trailer promocional **não equivale a autorização de republicação**.
3. **Probes + curadoria da cena**: confirmar se a fonte é acessível e contém imagem em movimento e áudio correspondente; selecionar `source_id` e janela de vídeo explícita de 12–60s. Registrar prova dos direitos necessários. Falta de prova bloqueia somente a liberação do conteúdo; **não impede pesquisar e registrar fontes candidatas**.
4. **Manifesto de 12 itens**: rede, horário `America/Sao_Paulo`, título escolhido pelo usuário, fonte, source ID, janelas sem sobreposição, hook, CTA, legendas e direitos; anti-repetição de 60 dias por fonte/janela e fingerprints visuais.
5. **Ingestão + render FFmpeg**: ffmpeg + `yt-dlp`; para VP9/Opus em fluxo de remux usar `.mkv` ou transcodificar de forma compatível (nunca VP9 em `.mov`); H.264/AAC, 1080x1920, 30fps, áudio original coerente e audível, logo safe-zone, títulos/CTA sincronizados. Sem música genérica cobrindo diálogo, sem tail mudo.
6. **QA real fail-closed**: verificar códec/duração/fps, movimento real, quadros pretos, áudio/silêncio, aderência editorial, redundância de cenas, repetição temporal 60 dias, vínculos run/commit/SHA-256. Não substituir testes por campos booleanos `PASS` sem verificação. Sem histórico completo, registrar cobertura e bloquear liberação insegura.
7. **Entrega**: somente depois de 12 masters aprovados criar/atualizar GitHub Releases com SHA e evidências imutáveis; confirmar no Metricool o ID e status de cada agendamento; publicar/agendar **apenas os masters corretos**, sem duplicar rede/cena.

## Antirregressão

- **Não** trocar o fluxo acima por pacote fictício de roteiro, por inventário de 2025 sem URLs, por duas cenas independentes ou por geração de IA sem autorização do usuário.
- **Não** inserir pré-gate que proíba sequer a **descoberta** de fontes. Os campos obrigatórios são checados **depois** da descoberta.
- **Não** preencher provas de direitos, URLs de origem, horários da cena, histórico de 60 dias ou evidências falsos para forçar sucesso.
- **Não** tratar `Source Probe=PASS` como `render=PASS` nem `Release=PASS` como `Metricool=SCHEDULED`.
- **Não** clobber/reaproveitar masters antigos como se fossem cenas novas; preservar histórico e antirrepetição.
- Custo adicional zero; não utilizar Make/Vercel/Opera externos como requisito.

## Recuperação 13/10 — diagnóstico

- Run `38335340619`: 60 campos de entrada ausentes nos 12 títulos novos, compilador executado **antes da descoberta**. Fail-closed correto para release, ordem errada para descoberta.
- Run `38340112727`: recibo correto de 0/12 fontes e bloqueio preservado; ainda sem pesquisa automatizada.
- Correção: tornar novamente a etapa de pesquisa `yt-dlp` anterior ao compilador, guardando possíveis fontes e pendências separadamente; compilador e render continuam fail-closed. A pesquisa não substitui a validação de direitos e nem produz os 12 arquivos por si só.

**Fonte primária e testes:** GitHub Actions, manifests, code dos packs Oct09–Oct12, releases Oct11/Oct12 e os issues #75/#77/#80.

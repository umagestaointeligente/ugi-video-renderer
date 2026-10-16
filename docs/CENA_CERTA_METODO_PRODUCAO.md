# Cena Certa — método de produção recuperável v1
Data: 16/10/2026. Fuso operacional: America/Sao_Paulo. Responsável: Paulo.
Chave de recuperação: CENA_CERTA_METODO_PRODUCAO_V1_2026-10-16.
Repositório: umagestaointeligente/ugi-video-renderer.

## Como recuperar em qualquer chat
Peça: “Lola, recupere o CENA_CERTA_METODO_PRODUCAO_V1_2026-10-16, leia o manual e os recibos do lote, e continue do estado registrado sem reiniciar a arquitetura.”
Buscar o arquivo CENA_CERTA_METODO_PRODUCAO_V1_2026-10-16.md nos arquivos conectados ou ler docs/CENA_CERTA_METODO_PRODUCAO.md no repositório. Se o chat não tiver acesso aos arquivos/conectores, anexar o manual; não presumir recuperação automática de conversas ou de pastas temporárias.

## Estado comprovado e alcance
O método gerou 12 MP4s candidatos diferentes, três por rede: TikTok, Instagram, Facebook e YouTube. Os 12 passaram pela validação técnica do renderizador. O compilador aceitou os 12 arquivos reais locais com zero erros de entrada.
Isso NÃO certifica o padrão editorial final nem publicação: revisão editorial, legendas de diálogo e comparação visual completa com 180 dias de histórico continuaram pendentes. Não houve agendamento deste lote; a consulta ao Metricool retornou lista vazia para 16/10 no momento registrado.
Algumas cenas e chamadas diferem do editorial inicialmente proposto. Este documento preserva a receita realmente executada, não a apresenta como formato final aprovado.

## Referências persistentes
| Item | Nome exato / identificador |
|---|---|
| Este manual | CENA_CERTA_METODO_PRODUCAO_V1_2026-10-16.md |
| 12 vídeos e recibos | Cena_Certa_12_Candidatos_2026-10-16.zip — libfile_9bd67a8226e08191a25e6439a74d875f |
| Trechos de origem e editorial | Cena_Certa_Fontes_Candidatos_2026-10-16.zip — libfile_759adf75d97881918fcb7b7a932ccf11 |
| Correção de política | PR #93: https://github.com/umagestaointeligente/ugi-video-renderer/pull/93 |
| Commit integrado da correção | 6d37e8b27de242af87f99d1e2f73e7813c278f6a |
| Compilador | scripts/cena_certa_oct13_compile.py |
| Entrada reutilizável | scripts/cena_certa_render_candidates.py |
| Motor e QA | scripts/cena_certa_oct13_pack.py |
| Workflow manual | .github/workflows/cena-certa-render-candidates.yml |
| Decisão registrada | ops/cena-certa-oct16/user-rights-decision.json |
| Logo | assets/cena-certa-logo.png.b64 |
| Marca Metricool | 6809869 |

O primeiro ZIP contém LEIA-ME.md, delivery-receipt.json, editorial-candidates.json, compiled-input-receipt.json, user-rights-decision.json e os masters em subpastas por rede. O ZIP de fontes contém os arquivos nos caminhos relativos tmp/cc-oct16-unverified/ e uma cópia do editorial. Os SHA256 exatos estão nos JSONs; não reconstruí-los a partir de memória.

## Receita executada
1. Recuperar os dois ZIPs e os scripts da versão indicada. Restaurar as fontes na raiz do checkout, preservando os caminhos source_file. Verificar seus SHA256 contra editorial-candidates.json.
2. Para novas fontes, resolver metadados de páginas públicas com yt-dlp. Neste lote funcionaram páginas públicas TokyVideo e um vídeo público do AdoroCinema no Facebook para Breaking Bad. Disponibilidade pública não equivale a licença.
3. Selecionar a URL de mídia dos metadados e baixar somente uma janela limitada com FFmpeg. Não gravar URLs temporárias assinadas no manual ou nos logs públicos. Não usar cookies, contornar login, DRM ou paywall.
4. Conferir código de saída, streams de áudio/vídeo e duração com ffprobe. O primeiro download de Intocáveis veio sem moov atom e foi descartado; nova aquisição válida foi usada. Tamanho de arquivo e mensagem de download não bastam.
5. Gerar prancha de quadros para identificar a cena; selecionar uma janela local contínua e adaptar a chamada ao que realmente aparece. Confirmar idioma e diálogo na revisão audiovisual, não apenas pelo título “dublado” da página.
6. Preencher source_url, source_id, source_file, source_sha256, source_segments, media_type=LIVE_ACTION, hook, CTA e caption. Os segmentos abaixo referem-se ao ARQUIVO LOCAL adquirido, não ao filme completo.
7. Compilar com compile_editorial(documento, expected_date=data, rights_decision=decisao). Em 16/10 foram zero erros com os 12 arquivos reais. O editorial inicial com fontes nulas não serve para render.
8. Renderizar com pack.render_item(item, arquivo_local, logo, None); a entrada reutilizável faz compilação, aquisição local por hash, render e recibo. A execução original fez chamadas diretas por pequenos grupos e validou cada item; não foi um único workflow de publicação.
9. Validar o master com pack.validate_master, calcular SHA256 e salvar recibo. Batman teve um primeiro master sem moov atom; o segundo render, com threads limitadas, passou. A causa do primeiro encerramento não foi comprovada.
10. Persistir vídeos, fontes e recibos fora de scratch; só depois de QA editorial/histórico e agendamento confirmado atualizar o estado operacional.

### Dependências e comandos
Dependências do caminho: Python 3, FFmpeg/ffprobe, DejaVu Sans Bold, yt-dlp, requests e Pillow. curl_cffi foi instalado em uma tentativa de outro provedor, mas não é necessário para restaurar e renderizar estas fontes locais.

Extrair os ZIPs para uma pasta de trabalho confiável e colocar o editorial e a decisão em caminhos dentro do checkout. Rodar a partir da raiz:

```bash
python -m pip install yt-dlp requests Pillow
python scripts/cena_certa_render_candidates.py \
  --editorial out/cc-restaurado/editorial-candidates.json \
  --rights-decision ops/cena-certa-oct16/user-rights-decision.json \
  --out out/cc-reproducao-oct16
```

O diretório de saída deve ficar sob out/. Para repetir em nuvem, o checkout do runner também precisa ter acesso aos arquivos source_file; fontes apenas locais no chat não aparecem automaticamente no GitHub Actions. O workflow guarda artefatos por um dia: não é arquivo permanente.

Aquisição pública limitada, exemplo com variáveis locais já resolvidas:

```bash
python -m yt_dlp --compat-options no-certifi --skip-download \
  --dump-single-json --socket-timeout 15 --retries 0 "$PAGINA_PUBLICA"
ffmpeg -y -rw_timeout 15000000 -ss "$INICIO_ORIGINAL" \
  -i "$URL_MIDIA_TEMPORARIA" -t 55 -c copy \
  -avoid_negative_ts make_zero trecho.mp4
ffprobe -v error -show_streams -show_format -of json trecho.mp4
ffmpeg -y -i trecho.mp4 -vf "fps=1/7,scale=320:-1,tile=3x3" \
  -frames:v 1 prancha.jpg
```

no-certifi selecionou os certificados do sistema; não desabilitar TLS. Stream copy pode incluir quadros anteriores por keyframes: medir a duração, inspecionar o arquivo e escolher os segmentos locais depois. Para um retry de render com concorrência limitada, foram usados -threads 2 e -filter_complex_threads 1 e threads 2 no encoder. Essa limitação foi aplicada na execução local, não adicionada como configuração permanente ao código do PR #93. Começar sequencialmente em ambiente novo.

## Formato realmente renderizado
| Componente | Configuração |
|---|---|
| Tela | 1080×1920, vertical 9:16 |
| Vídeo | H.264/libx264, veryfast, CRF 18, yuv420p, 30 fps, faststart |
| Áudio | Áudio original da fonte, AAC 192 kbit/s, 48 kHz |
| Normalização | loudnorm I=-16, TP=-2, LRA=7 |
| Fundo | Própria cena ampliada para preencher a tela, gblur sigma 25, brilho -0,20, saturação 0,92 |
| Cena em primeiro plano | Proporção preservada; caixa 1060×1840 em TikTok/Instagram e 1040×1800 em Facebook/YouTube, centralizada |
| Logo | Largura 124 px, canto superior direito, margem 22 px |
| Gancho | y=145; fonte 44 no YouTube e 47 nas demais; 1,35 s no YouTube e 1,8 s nas demais |
| CTA | Fonte 36, y=h-220, últimos 1,35 s |
| Fonte | DejaVu Sans Bold com contorno e caixa translúcida |
| Narração e trilha novas | Não adicionadas neste lote; preservado o áudio da cena |

Não afirmar que este lote contém nome do filme fixo no topo, legendas de diálogo prontas, trilha nova por gênero ou CTAs exclusivos em todos os itens: esses recursos não foram todos implementados aqui. O título do filme está no editorial/recibo/caption; o gancho temporário não substitui a revisão da identificação visual exigida pelo canal.

## Catálogo reproduzível do lote
| ID (sufixo) | Rede | Filme/série | Fonte local | Segmento local | Duração |
|---|---|---|---|---|---|
| TIKTOK-01 | TikTok | As Branquelas | branquelas-inspection.mp4 | 12–58 | 46 s |
| TIKTOK-02 | TikTok | Se Beber, Não Case! | ressaca-inspection.mp4 | 4–48 | 44 s |
| TIKTOK-03 | TikTok | A Hora do Rush 2 | rush-inspection.mp4 | 10–54 | 44 s |
| INSTAGRAM-04 | Instagram | Meninas Malvadas | meninas-source.mp4 | 22–62 | 40 s |
| INSTAGRAM-05 | Instagram | Extraordinário | extraordinario-inspection.mp4 | 24–65 | 41 s |
| INSTAGRAM-06 | Instagram | Top Gun: Maverick | topgun-inspection.mp4 | 10–50 | 40 s |
| FACEBOOK-07 | Facebook | Intocáveis | intocaveis-interview.mp4 | 10–60 | 50 s |
| FACEBOOK-08 | Facebook | Um Senhor Estagiário | estagiario-inspection.mp4 | 2–48 | 46 s |
| FACEBOOK-09 | Facebook | À Procura da Felicidade | felicidade-inspection.mp4 | 10–58 | 48 s |
| YOUTUBE-10 | YouTube | Batman: O Cavaleiro das Trevas | batman-inspection.mp4 | 10–52 | 42 s |
| YOUTUBE-11 | YouTube | Breaking Bad | breakingbad-inspection.mp4 | 143–188 | 45 s |
| YOUTUBE-12 | YouTube | Missão: Impossível — Efeito Fallout | fallout-inspection.mp4 | 10–52 | 42 s |

IDs completos começam por CC-OCT16-. Meninas Malvadas foi entregue com o nome CC-OCT16-INSTAGRAM-04-CANDIDATE.mp4. Não criar um décimo terceiro item ao encontrar esse sufixo. Breaking Bad veio do trecho final de uma compilação pública; foi recortada a cena do deserto, não a compilação inteira. À Procura da Felicidade não é a oferta final de emprego; Batman não é o interrogatório; Top Gun não é a demonstração solo inicialmente proposta.

## QA, direitos e continuidade
QA técnico existente: codec, resolução, pixel format, fps, AAC/48 kHz, ffprobe, quadros pretos prolongados, movimento binário e perceptual central, e silêncio prolongado no final. Movimento perceptual impede que ruído de compressão faça um quadro congelado passar.
A aprovação técnica não prova idioma, compreensão, gancho legível, nome do filme, legendas, CTA adequado, ausência de repetição histórica ou licença.

A instrução “Utilize mesmo sem autorização” está registrada em user-rights-decision.json. No código atual, a exceção é vinculada a Paulo, marca 6809869, data 16/10 e aos 12 IDs exatos. Ela permite compilar candidatos mantendo NOT_VERIFIED; não concede licença, não transforma direitos em VERIFIED e não se estende automaticamente a outro lote/data. Preservar a instrução do usuário ao operar, respeitando o escopo validado pelo compilador; não falsificar evidências para resolver um bloqueio.

Para novos dias: reaproveitar o motor e a receita; criar editorial com nova data, novos IDs, novas cenas e janelas verificadas. Não reativar automaticamente pacotes antigos, não reutilizar os horários de 16/10, não copiar a exceção datada como se fosse genérica.
Não executar o main legado de cena_certa_oct13_pack.py para um novo dia: ele ainda tem contratos fixos de 13/10 e checagens próprias. Usar a entrada date-independent render_candidates.py.

A rotina history_index legada usa um arquivo de histórico de 60 dias e limiar mínimo de cobertura 0,80; seu PASS não comprova os 180 dias exigidos atualmente. Reconciliar histórico completo e comparação visual com evidência antes de marcar anti_repeat_180d como verificado. Metadata/título ausente não prova cena inédita.
O renderer de candidatos sempre mantém release_allowed=false e não chama o Metricool. Publicação/agendamento é uma etapa separada: consultar dados atuais por rede, escolher horários futuros, confirmar arquivos enviados e registrar IDs/URLs retornados pelo provedor, sem declarar sucesso só por ausência de erro.

## Manutenção
Atualizar este manual e o recibo quando houver mudança comprovada. Registrar commit, fontes, janelas, hash, dependências, QA e pendências. Preservar versões anteriores e não substituir evidência histórica por alegações de execução recente.


## Continuidade comprovada — V2 de revisão, 16/10/2026

Esta atualização é **aditiva**: não substitui o lote original nem altera os recibos históricos. Em nova sessão, os dois ZIPs canônicos deste manual foram restaurados da Biblioteca, os SHA-256 dos 12 arquivos-fonte e dos 12 masters originais conferidos (24/24), e 12 revisões V2 foram renderizadas a partir dos masters preservados. As V2 identificam permanentemente cada obra e têm CTA específico, com máscara corrigida para não sobrepor o CTA antigo.

**QA V2 realizado:** 12/12 vídeos H.264 1080×1920/30 fps, áudio AAC/48 kHz, duração e SHA-256 conferidos; decodificação integral FFmpeg sem erros. Inspeção visual **amostrada** das aberturas e encerramentos; 164 quadros amostrados das origens e 66 pares comparados **somente dentro do lote**. Não é aprovação de 180 dias nem revisão integral dos diálogos.

**Pendências mantidas:** direitos de republicação NOT_VERIFIED; legendas de diálogo NOT_ADDED; idioma e alinhamento de áudio editorial PENDING; histórico visual completo de 180 dias NOT_VERIFIED; nenhum item elegível para liberação e nenhum agendamento novo no Metricool. A decisão de direitos do usuário foi preservada sem transformá-la em licença.

**Evidência/recuperação V2:** relatório `ops/cena-certa-oct16/CONTINUIDADE_QA_V2.md`; cópia privada na Biblioteca `Cena_Certa_12_Candidatos_V2_Revisao_2026-10-16.zip` (12 MP4s V2, recibos SHA, QA, pranchas e código de revisão) e `CENA_CERTA_16OUT_CONTINUIDADE_QA_V2.md`. O ZIP original de 12 masters e o ZIP de fontes seguem a base de reprodução. Se houver divergência em valores auxiliares do resumo da primeira cópia, consultar os recibos JSON; contagem correta da amostragem é 164.

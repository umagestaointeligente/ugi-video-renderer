# Cena Certa — continuidade auditada do método de 16/10/2026

**Base canônica:** `CENA_CERTA_METODO_PRODUCAO_V1_2026-10-16` — `docs/CENA_CERTA_METODO_PRODUCAO.md` no GitHub.

**Originais recuperados:** `Cena_Certa_12_Candidatos_2026-10-16.zip` e `Cena_Certa_Fontes_Candidatos_2026-10-16.zip`.

## Estado da retomada

- 12 arquivos-fonte e 12 masters originais: os 24 hashes SHA-256 corresponderam aos recibos.
- 12 versões V2 novas, com filme identificado permanentemente e CTA específico por cena, sem sobrescrever os 12 masters originais.
- 12/12 V2 decodificadas integralmente e verificadas por FFprobe (H.264, AAC, 1080×1920, 30 fps, amostragem áudio 48 kHz, duração e SHA-256).
- Inspeção visual amostrada das aberturas e encerramentos: títulos e novos CTAs presentes. Essa inspeção não comprova revisão quadro a quadro, idioma do áudio ou sincronismo de legendas.
- Fingerprints amostrados dos 12 originais: 164 quadros amostrados em 12 itens, todos diferenciados dentro de cada vídeo, 66 comparações entre títulos; não é um índice de histórico de 180 dias.
- Direitos de republicação: **NOT_VERIFIED**; o registro de decisão do proprietário permite produzir candidatos mas não comprova licença.
- Legendas de diálogo PT-BR: **NOT_ADDED**. Áudio original preservado. Verificação de idioma de cada fonte: **PENDING**.
- Trava de 180 dias: **NOT_VERIFIED**. Histórico visual completo não foi recuperado; nenhuma publicação foi liberada por essa checagem.
- Metricool Brand ID 6809869: **0 agendamentos** para 16/10 na última leitura conectada. Nenhuma tentativa de agendamento foi efetuada nesta continuação.

## Itens da revisão V2

| Rede | ID | Obra | Original hash | V2 hash | FFmpeg | CTA específico | Agendamento |
|---|---|---|---|---|---|---|---|
| tiktok | CC-OCT16-TIKTOK-01 | As Branquelas (2004) | 6a22bb1d4cfa | 6943501a9a5e | PASS | A transformação convenceu você? | NÃO |
| tiktok | CC-OCT16-TIKTOK-02 | Se Beber, Não Case! (2009) | cb57b6b52950 | f401e631cff1 | PASS | Qual descoberta foi a mais absurda? | NÃO |
| tiktok | CC-OCT16-TIKTOK-03 | A Hora do Rush 2 (2001) | a85e0b3d577e | b219780f188a | PASS | Quem teria escapado dessa confusão? | NÃO |
| instagram | CC-OCT16-INSTAGRAM-04 | Meninas Malvadas (2004) | 667970d97604 | 1c14df5c212a | PASS | Como seria seu primeiro dia nessa escola? | NÃO |
| instagram | CC-OCT16-INSTAGRAM-05 | Extraordinário (2017) | d7f71193a445 | b62a72dc86ff | PASS | Qual gesto de apoio marcou sua vida? | NÃO |
| instagram | CC-OCT16-INSTAGRAM-06 | Top Gun: Maverick (2022) | c66d04f590f2 | d4e50df65455 | PASS | Você encararia esse voo? | NÃO |
| facebook | CC-OCT16-FACEBOOK-07 | Intocáveis (2011) | 175402981d3d | dbeb7b20dc9d | PASS | Você contrataria Driss? | NÃO |
| facebook | CC-OCT16-FACEBOOK-08 | Um Senhor Estagiário (2015) | ec5c1feb7b9b | 881cdba7fa84 | PASS | Experiência pode surpreender? | NÃO |
| facebook | CC-OCT16-FACEBOOK-09 | À Procura da Felicidade (2006) | 1e702df9807c | 5c8b75436445 | PASS | Você teria desistido nessa situação? | NÃO |
| youtube | CC-OCT16-YOUTUBE-10 | Batman: O Cavaleiro das Trevas (2008) | e1f6ea90cced | 35d12cbdcfe3 | PASS | Quem está no controle dessa conversa? | NÃO |
| youtube | CC-OCT16-YOUTUBE-11 | Breaking Bad (2008) | 84007f79c82c | d9e6e68dae09 | PASS | Foi coragem ou arrogância? | NÃO |
| youtube | CC-OCT16-YOUTUBE-12 | Missão: Impossível — Efeito Fallout (2018) | 5f9cdf18a20b | 2411a668365b | PASS | Quem levou vantagem nessa luta? | NÃO |

## Pendências e alertas concretos

- **TikTok 03 — A Hora do Rush 2:** o quadro de abertura mostra legendas gravadas em inglês e português na própria fonte. Conferir diálogo original/PT-BR e a legibilidade antes de qualquer aprovação.
- **YouTube 11 — Breaking Bad:** a cena contém identificações originais do canal AdoroCinema, visíveis no enquadramento. Não foram retiradas ou tratadas como licença.
- **YouTube 10 — Batman:** a cena presente é o confronto próximo ao fogo, não o interrogatório do editorial original; a chamada deve refletir o trecho real.
- **Facebook 09 — À Procura da Felicidade:** a cena é do contexto de trabalho, e não a oferta de emprego inicialmente sugerida.
- **Instagram 06 — Top Gun: Maverick:** cenas aéreas, não a demonstração solo descrita no planejamento inicial.
- Nenhuma das 12 revisões contém legendas novas de diálogo, trilha sonora adicional por gênero ou narração criada. Os CTAs novos estão em texto visual; não há prova de CTA falado.
- O selo de QA técnico e os novos SHA-256 não são recibo de autorização editorial, licença, unicidade em 180 dias nem agendamento.

## Próximas validações exigidas pelo manual

1. Comparar as V2 com o banco completo de cenas de 180 dias, inclusive publicações externas ao Metricool, por fonte, janela temporal e fingerprint visual.
2. Verificar idioma em PT-BR, transcrever os diálogos com revisão humana e produzir legendas sincronizadas onde forem necessárias.
3. Revisar entendimento da cena, áudio, título, gancho, segurança visual, CTA e narrativa por rede em cada arquivo reproduzido integralmente.
4. Obter a licença/permissão aplicável, ou manter direitos não verificados sem alegar aprovação.
5. Gerar recibo de liberação por SHA. Somente então enviar master elegível para o Metricool, evitando duplicatas e conferindo ID, data, rede e status por leitura posterior.

## Referências de arquivo

- `v2_receipt.json`: relação 1:1 com os 12 arquivos V2 e hashes novos.
- `v2_ffmpeg_qa.json`: FFprobe, decodificação de início ao fim, áudio e status técnico.
- `qa_integrity.json`: hashes SHA dos 12 originais e das 12 fontes do manual.
- `batch_fingerprint_samples.json`: amostragem perceptual interna; não equivale a PASS do histórico.
- `v2_open_close_sheet.jpg`: prancha de abertura e encerramento dos 12 masters revisados.
- `build_v2.py`: receita local das alterações; requer original e dependências, não modifica arquivos de origem.
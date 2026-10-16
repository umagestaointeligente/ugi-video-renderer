# Recuperação de produção — 15/10/2026

## Baselines observados, não inferidos do nome do job

| Canal | Execução aprovada | Evidência real |
|---|---|---|
| Cena Certa | 38196309142, SHA 222431b34c40235566bd63e3f2df06e913bfead3 | 12 SOURCE_INGEST_PASS/MASTER_RENDER_PASS; uploads de masters |
| VSA | 37878641844, SHA c30f29c24320d3de159b249b7c6d68ffb104c47c | 3 MP4s, durações 51.68/51.42/47.42s; recibos e upload |
| UGI | 37570527380, SHA 6af864be514b4acec7ec7cc49d716d2e3e373235 | 2 MP4s reais; commit de arquivos de 07/out |

Logs dos jobs 114639618003, 113652933601, 112627876177 foram comparados aos jobs falhos 115115448713, 115010052608 e 115638701209.

## Causas confirmadas

1. VSA Oct13 (38308406238): voz Edge TTS 7.2.8 recebe HTTP 403 antes de qualquer render. Mesma versão funcionava em 09/out; não é evidência de falha de FFmpeg. A correção preventiva existente ficou fora de main e não resolveu o provedor.
2. Cena Certa Oct13 (38342192438): descoberta encontrou 48 candidatos, mas os 12 itens continuaram sem fonte/janela/direitos. Zero fontes prontas e 60 campos ausentes. O render nem chegou a executar.
3. Cena Certa Oct14 (38498197125): YouTube exige autenticação; não confundir com render quebrado. A rota antiga Globoplay continua como ingestão possível para redes permitidas; permanece proibida no YouTube.
4. UGI: o último render editorial observado foi em 07/out. Workflows por data só rodam em push no próprio YAML. Magic Engine 38727049581 executa radar/council/auth, sem comando de renderização. SUCCESS desse job não significa vídeo produzido.
5. Compilador Cena Certa exigia exclusivamente 2025, restrição ausente da preferência geral recuperada (1990+, preferencialmente 2000+). Isso fechava a seleção mesmo antes dos requisitos técnicos.
6. O ambiente local exige raízes de certificado do sistema. Isso é distinto do 403 remoto histórico. A validação TLS não foi desabilitada.

## Correções

- Worker de voz com Edge TTS 7.3.1, mesma voz AntonioNeural, confiança certifi + sistema, timeout, remoção de parcial e erros sanitizados. Integração no renderer VSA e no novo runner UGI.
- Corrigida fonte de multidão do VSA: o arquivo tem 5,806s, mas a janela antiga exigia 8,124s. A fala foi encurtada, mantendo a ideia, e a entrada passou a 0s.
- Falha de uma pauta VSA não descarta as outras; lote incompleto permanece FAIL e salva candidatos e falhas por item.
- Ingestão VSA agora adquire somente o prefixo necessário de cada fonte e aceita cache apenas com URL, hash e duração verificados. A narração exata pode ser reutilizada pelo bundle, sem nova síntese.
- Recuperado renderer VSA Oct13 da branch preventiva, sem booleans inventados de aprovação. Preserva MP4s candidatos antes do gate de liberação, para que revisão pendente não descarte o resultado do render.
- UGI recebe runner por manifesto com hashes da fonte, texto e narração; valida decodificação, SAR, duração e formato. Workflow permite disparo manual ou novo manifesto em ops/production/ugi/current.json. Não recria automaticamente conteúdo antigo.
- Cena Certa: anos permitidos retornam a 1990–2026; ingestão local por arquivo/hash é suportada; yt-dlp executa no mesmo Python, com certificados do sistema verificados. Janela truncada bloqueia, e erro nos detectores de preto/silêncio não vira PASS.
- QA técnico e aprovação editorial continuam separados. Os replays históricos não são uma grade nova, não podem passar pela antirrepetição como inéditos e não foram publicados/agendados.

## Operação

UGI: `python scripts/ugi_render_manifest.py --manifest <manifesto-no-repositorio.json> --out out/ugi-candidates`.
O manifesto de replay em ops/production/baselines documenta a interface com fontes e voz reais. Para nova pauta, fornecer fonte correspondente e texto novos; omitir narration_file para síntese pela mesma voz.

VSA: `python production/vsa/pilots/oct13_triple/render_oct13_triple.py`.
A produção gera candidatos, metadados e contact sheets. O gate final permanece pendente até QA independente dos masters; não emitir token por autodeclaração.

Cena Certa: `python scripts/cena_certa_render_candidates.py --editorial <editorial.json> --out out/cc-candidates` aceita datas novas e preserva candidatos por item. O workflow manual correspondente não publica.

Cena Certa: descoberta → ingestão → recorte/render → QA → liberação. `source_file`+`source_sha256` permite usar mídia já adquirida e verificada; isso não comprova direitos ou idioma. Fontes que pedem autenticação continuam bloqueadas. Histórico de 180 dias e QA editorial vigentes precisam acompanhar uma grade nova.

Não houve merge, release pública, alteração no Metricool, agendas, billing, secrets ou exclusão de evidências. Rollback da proposta: descartar esta branch/PR. O ramo main permanece preservado.

## Validação local concluída

- 74 testes descobertos: 73 passaram e 1 teste preexistente foi ignorado; 14 casos inválidos bloqueados pelo self-test do gate.
- Quatro workflows passaram por parse YAML e validação de shell.
- Cena Certa: ingestão real da fonte antiga e master de 34s, SHA ef030448daef90e13a04b6a9f1160159c427aa178ba6a834a50b0be25b223d7d. Replay histórico, não inédito.
- UGI: dois masters de replay, 24,000s e 115,968s. Hashes e identidades de fonte/voz nos recibos.
- VSA: três masters novos: pêndulo 48,404s, semáforo 50,414s, Olivia 51,804s. Todos passaram pelo validador técnico independente de formato, movimento, preto e silêncio final. Inspecionados contact sheets e quadro de CTA; revisão editorial/direitos/histórico não foi substituída por esse teste.
- O envio da branch ao GitHub foi recusado pela revisão automática por falta de autorização explícita para a mutação externa. A branch remota não existe; não houve CI, PR, merge ou ativação em main. Commits preparados localmente. A solicitação final é para enviar a branch e abrir o PR; publicação continua fora deste pacote.

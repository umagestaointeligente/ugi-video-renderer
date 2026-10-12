# AGENTS.md — UGI Video Renderer

## Leitura obrigatória

Antes de qualquer alteração, ler:

1. `docs/LOLA-PROJECT-CONTROL-PLANE.md`
2. `canonical/tooling/VIDEO_TOOLCHAIN_CURRENT.json`
3. O manifesto canônico do projeto/canal afetado.

Para VSA, ler `canonical/vsa/CURRENT.json` e os arquivos apontados por ele.
Para Cena Certa, ler o contrato vigente em `canonical/cena-certa/`.
Não reconstruir regras por memória de conversa.

## HyperFrames / HeyGen

HyperFrames é a ferramenta canônica aprovada para pilotos de composição e renderização determinística de vídeo. Ele pode ser usado para animações explicativas, mapas, gráficos, overlays, legendas, áudio, transições e CTA.

Usar a skill `orbit-hyperframes-video` e, quando disponíveis, as skills oficiais `hyperframes`, `hyperframes-cli`, `hyperframes-core`, `hyperframes-animation`, `hyperframes-audio`, `embedded-captions`, `faceless-explainer` e `media-use`.

HyperFrames não é gerador autônomo de footage, pessoas, atores, avatares ou vozes. Não declarar capacidade que dependa de outra ferramenta.

## Segurança operacional

- Manter mudanças em branch/PR isolado.
- Não fazer merge, deploy, publicação ou agendamento sem gate e evidência.
- Preservar custo incremental zero; preferir execução local ou runner próprio.
- Não criar Vercel, Make, AWS Lambda ou serviço pago sem autorização explícita.
- Não misturar VSA, Cena Certa e UGI em contas, rotas, agendas ou assets.
- Fixar versão/commit; nunca usar `latest` em produção.
- Tratar estado sem readback como `UNKNOWN/NOT_PROVEN`.

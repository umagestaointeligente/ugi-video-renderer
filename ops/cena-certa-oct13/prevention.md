# Correção preventiva — Cena Certa Oct13

Base: b91c5ec71e2c9542f834173ad656b3887d264e92.

O bloqueio do run 38335340619 por 60 dados ausentes é preservado. Não foram inventadas fontes, direitos, cenas ou aprovações. A compatibilidade VP9/Opus com Matroska já corrigida na base permanece.

Correções: rejeição de IDs duplicados/inseguros, colisão source_id/URL, horários impossíveis e NaN; alinhamento integral com manifest recompilado; sem truncamento de segmentos nem teto de ingestão inferior à janela; ingestão única por fonte com união das janelas; erro dos detectores de preto/silêncio bloqueia; histórico vazio, stale >24h, incompleto ou parcialmente decodificado bloqueia; QA de conteúdo obrigatório vinculado a manifest e masters; revalidação independente de todos os gates obrigatórios, arquivos, hashes, run, commit e tentativa; summary atômico; artifact obrigatório antes de release e issue; tags por tentativa sem clobber; evidência inclui ID/digest do artifact; log do compilador bloqueado preservado por 3 dias.

Revisão de conteúdo: fornecer `ops/cena-certa-oct13/content-qa.json` com `reviewer`, `manifest_sha256` (hash exato do manifest produzido pelo compilador) e `items` por id. Cada item deve conter `sha256` do master e `gates` com os oito CONTENT_GATES definidos no guard. Revisão está vinculada aos bytes, não ao commit que contém o próprio documento, evitando referência circular. Nenhum documento de QA real foi fabricado. Reviewer é atestação de processo, não autenticação criptográfica.

Testes: suíte offline, casos negativos de hashes/gates/proveniência, compilador, histórico, Matroska VP9/Opus real e master sintético H264/AAC 1080×1920/30fps. Fixtures são sintéticas e não representam direitos ou aprovação de conteúdo real. Workflow de testes tem somente contents:read, sem upload, release, publicação ou Metricool.

Estado operacional: código corrigido em branch para revisão, sem merge. Produção continua bloqueada enquanto o editorial canônico não contiver fontes e direitos reais e QA válido. Isso é ausência de entrada, não defeito a ser mascarado por retry.

Limites: completude de exportação dos 60 dias precisa ser atestada pela origem; cobertura de decode não prova exportação completa. Algoritmo dHash e limiares vigentes preservados, sem promessa de detectar qualquer repetição. Atualização do snapshot e autenticação de direitos/revisor dependem do processo de origem. Não há garantia de inexistência de qualquer falha futura.

Rollback: fechar a branch de correção ou reverter seus arquivos antes de qualquer merge. Nenhuma mudança de agenda, publicação, secret, billing ou proteção de branch faz parte desta correção.

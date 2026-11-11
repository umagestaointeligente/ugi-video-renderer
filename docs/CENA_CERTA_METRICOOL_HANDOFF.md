# Cena Certa: entrega ao Metricool

O renderer de candidatos continua sem publicar. `scripts/cena_certa_metricool_bridge.py`
liga os recibos de liberação a uma fila persistente, operada pelo conector Metricool.
O script **não é um cliente da API e não agenda sozinho**. Não há credencial
Metricool no ambiente local verificado em 10/11/2026.

## Entrada e preparo

O lote deve identificar data, marca 6809869, timezone America/Sao_Paulo e 12 itens,
três por rede. Cada item usa o contrato de `cena_certa_render_evidence_guard.py`,
mais network, slot futuro, title, caption e master_mp4_url. Os arquivos devem
estar em media-dir/ID.mp4 com o SHA aprovado.

Os recibos de áudio PT-BR, legendas e editorial devem conter status PASS e
evidence. O recibo uploaded_master registra url, sha256, downloaded_sha256 e
checked_at: baixar o arquivo da URL de entrega e verificar seus bytes antes de
preenchê-lo. Isso não pode ser inferido do nome nem do upload local.

Consultar o Planner completo da marca para a data antes de preparar. Preservar
a resposta original. Normalizar em brand_id, checked_at, complete e posts,
com id, network, slot, media_url, status e planner_url por publicação. Somente
usar complete=true depois de verificar todo o intervalo e eventual paginação.
Uma resposta vazia não dispensa o registro da marca, intervalo e horário da consulta.

```bash
python scripts/cena_certa_metricool_bridge.py prepare \
  --batch out/daily/batch.json --receipts out/daily/release-receipts.json \
  --media-dir out/daily/masters --snapshot out/daily/planner.json \
  --out out/daily/handoff.json
```

BLOCKED sai com código 1, erros globais, erros por item e resultado do gate
original. Nenhum recibo de qualidade é criado por este comando. Candidatos
técnicos antigos sem evidência de liberação continuam bloqueados.

## Envio e confirmação

1. Revalidar o lote e a consulta antes do envio (máximo 15 minutos).
2. Executar claim com plan, id e ledger **antes** de chamar createScheduledPost.
   A chave reserva marca/rede/SHA, inclusive se o horário mudar. Usar o mesmo
   ledger persistente em todas as execuções, sem apagar UNKNOWN em retries.
3. Agendar pelo conector, exclusivamente na marca/rede do item, com URL do
   arquivo aprovado, título/legenda e parâmetros próprios da rede. O comando
   claim não substitui essa chamada externa.
4. Guardar a resposta original. Ler o Planner novamente após a criação.
5. Executar reconcile com ledger, key, post-id e snapshot. Somente ID único,
   rede, instante, mídia, status SCHEDULED e link Metricool corretos confirmam.
6. Gerar evidências com summary(ledger, publication_date): só SCHEDULE_CONFIRMED da data entra na contagem.
   Agendamento confirmado não é prova de publicação.

```bash
python scripts/cena_certa_metricool_bridge.py claim \
  --plan out/daily/handoff.json --id CC-ITEM --ledger out/daily/ledger.json
python scripts/cena_certa_metricool_bridge.py reconcile \
  --ledger out/daily/ledger.json --key CHAVE_RETORNADA \
  --post-id ID_RETORNADO_PELO_METRICOOL --snapshot out/daily/planner-after.json
```

Timeout ou erro ambíguo mantém UNKNOWN e impede nova criação. Investigar a
operação no provedor; não apagar a reserva para repetir. O lock protege
processos no mesmo filesystem. Execuções em máquinas diferentes exigem ledger
compartilhado e um único publicador; arquivos locais isolados não garantem
idempotência global.

## Estado em 10/11/2026

A consulta conectada para 10 e 11/11 retornou `data=[]`. Zero agendamentos
confirmados. A integração foi testada com fixtures, sem publicar conteúdo
de teste. O lote de 16/10 mantém os bloqueios descritos em
`ops/cena-certa-oct16/CONTINUIDADE_QA_V2.md`; este componente não resolve
aquisição/licença, transcrição, revisão audiovisual ou cobertura histórica.

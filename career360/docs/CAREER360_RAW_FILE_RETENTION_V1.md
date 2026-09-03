# LSI Career 360 — Retenção do Currículo Bruto V1

Status: POLÍTICA BETA 1.0 / BLOQUEIO DE GATE
Data: 2026-09-03 BRT

## 1. Princípio

`MINIMIZAR O BRUTO. PRESERVAR O NECESSÁRIO.`

O arquivo PDF/DOCX existe para extrair e confirmar informações. Ele não deve ser mantido indefinidamente por conveniência técnica.

## 2. Prazos Beta 1.0

- arquivo novo em `QUARANTINED`: retenção máxima inicial de 7 dias;
- arquivo `REJECTED`: alvo de exclusão do objeto bruto em até 24 horas;
- arquivo `PARSED` ainda aguardando confirmação: pode permanecer apenas enquanto necessário para retry/continuidade, nunca além do limite inicial de 7 dias;
- após confirmação do perfil estruturado: excluir o bruto imediatamente quando possível, com SLO máximo de 24 horas;
- exclusão solicitada pelo usuário: execução imediata best-effort; falha externa entra em recovery/checkpoint e não é tratada como concluída até verificação.

## 3. Dados estruturados

A exclusão do bruto não apaga automaticamente fatos estruturados que o próprio usuário confirmou, salvo solicitação de exclusão de conta/dados aplicável.

Nenhum campo inferido é promovido por causa da retenção ou exclusão do arquivo.

## 4. Metadados mínimos

Após exclusão do objeto bruto, o sistema pode preservar metadados operacionais mínimos necessários para auditoria/recovery, como:
- document_id interno;
- tipo detectado;
- tamanho;
- parser version;
- status `deleted`;
- timestamps;
- código de erro quando aplicável.

Não preservar o texto integral do currículo em log geral.

Hash/checksum permanece somente enquanto houver finalidade operacional legítima e deve ser removido junto com exclusão integral da conta/dados quando aplicável.

## 5. Implementação

Rotas previstas:
- `career-document-ingest`: cria objeto privado e define `raw_file_retention_until`;
- `career-document-delete`: exclusão autenticada/idempotente do objeto e marcação de tombstone;
- cleanup automático: obrigatório antes de `SAFE_FILE_PIPELINE=PASS` para casos abandonados/rejeitados que ultrapassem o prazo.

## 6. Gate

Esta política definida é necessária, mas NÃO suficiente para PASS.

`SAFE_FILE_PIPELINE=PASS` exige também:
- delete autenticado testado;
- cleanup automático testado;
- deep validation antes de `SAFE_FOR_PARSE`;
- isolamento A/B;
- confirmação do usuário;
- logs sem conteúdo sensível;
- recovery verificável.

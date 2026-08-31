# Brazil Opportunity Radar — Apify R1

Actor para descobrir e priorizar oportunidades de compras públicas brasileiras usando exclusivamente fontes oficiais abertas: PNCP e Compras.gov.br.

## Entrada
- `query`: palavras-chave opcionais.
- `uf`: UF opcional com duas letras.
- `limit`: 1–100 resultados.

## Saída
Cada oportunidade é gravada no Dataset com objeto, valor estimado quando disponível, prazo, UF, órgão/unidade, modalidade, fonte e `opportunityScore` de 0 a 100. O `OUTPUT` inclui telemetria das fontes e latência.

## Estratégia R3
A seleção de fontes foi definida por medição real de densidade e latência em 31/08/2026: Compras.gov modalidades 5/6 e PNCP modalidades 5/4. As consultas rodam em paralelo com timeout de 5 segundos.

## Segurança e verdade econômica
- Não requer nem coleta PII.
- Não movimenta dinheiro diretamente.
- `Actor.charge` apenas solicita o evento `radar-run-completed`; faturamento real depende da configuração oficial de monetização da Apify.
- Nenhum resultado comercial ou financeiro é garantido.
- Receita só pode ser contabilizada após evidência do provedor.

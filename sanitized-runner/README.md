# Orbit Sanitized Public Runner

Rota de renderização em GitHub-hosted runner público, isolada do repositório privado.

## Regras

- Nunca versione vídeos-fonte, roteiros, cookies, tokens ou credenciais.
- O pacote de entrada fica em armazenamento privado e é baixado por HTTPS autenticado.
- O resultado é criptografado antes de virar artefato.
- Os arquivos temporários são removidos ao final do job.
- Inputs públicos contêm apenas um identificador operacional não sensível.

## Secrets necessários

- `ORBIT_BUNDLE_ENDPOINT`: endpoint HTTPS privado que entrega o pacote atual.
- `ORBIT_BUNDLE_TOKEN`: token Bearer de leitura.
- `ORBIT_BUNDLE_SHA256`: SHA-256 esperado.
- `ORBIT_OUTPUT_AGE_RECIPIENT`: chave pública age para criptografar o resultado.

O pacote `.tar.gz` deve conter um `render.sh` executável e os ativos autorizados. O script recebe o caminho de saída como primeiro argumento.

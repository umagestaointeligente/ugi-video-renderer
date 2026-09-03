# LSI Career 360 — Entrada Segura de Currículo V1

Status: DESIGN CANÔNICO / IMPLEMENTAÇÃO PENDENTE
Data: 2026-09-02 BRT
Escopo Beta 1.0: PDF textual + DOCX

## 1. Objetivo

Permitir que o usuário envie um currículo e receba um perfil pré-preenchido sem transformar inferência em fato, sem expor dados pessoais desnecessariamente e sem depender de um fornecedor específico.

Princípio de experiência:
`O CLIENTE NÃO PREENCHE. O CLIENTE CONFIRMA.`

Princípio de segurança:
`ARQUIVO NÃO É CONFIÁVEL POR PADRÃO.`

## 2. Fluxo canônico

`SELECIONAR_ARQUIVO`
→ `PREFLIGHT_LOCAL`
→ `UPLOAD_AUTENTICADO`
→ `QUARENTENA`
→ `VALIDAR_TIPO_REAL`
→ `VALIDAR_TAMANHO`
→ `SCAN/INSPEÇÃO_SEGURA`
→ `EXTRAIR_TEXTO`
→ `NORMALIZAR`
→ `EXTRAIR_CAMPOS_COM_EVIDÊNCIA`
→ `GERAR_RASCUNHO`
→ `USUÁRIO_CONFIRMA/CORRIGE`
→ `PERSISTIR_DADOS_CONFIRMADOS`
→ `APLICAR_POLÍTICA_DE_RETENÇÃO_AO_ARQUIVO`

Nenhuma etapa posterior pode tratar o arquivo como confiável só porque extensão/MIME declarado parece correto.

## 3. Formatos Beta 1.0

Permitidos inicialmente:
- `.pdf` textual;
- `.docx`.

Bloqueados inicialmente:
- `.doc` legado;
- `.rtf`;
- `.odt`;
- planilhas;
- executáveis;
- arquivos compactados genéricos enviados pelo usuário;
- documentos protegidos por senha;
- PDF escaneado sem camada textual como caminho automático principal.

Se PDF não tiver texto utilizável:
- informar claramente;
- oferecer novo PDF/DOCX;
- permitir entrada por voz/texto;
- OCR só entra depois de gate próprio de privacidade/custo/qualidade.

## 4. Limites

Configuração inicial sugerida:
`MAX_UPLOAD_MB=10`
`MAX_FILES_PER_ONBOARDING=3`

Valores devem permanecer configuráveis.

O limite existe para reduzir abuso, custo, memória e superfície de ataque; não é requisito de produto imutável.

## 5. Preflight local

Antes de enviar:
- extensão permitida;
- tamanho aparente;
- arquivo vazio;
- feedback visual do nome/tamanho;
- consentimento/aviso de finalidade.

Preflight local melhora UX, mas NÃO substitui validação server-side.

## 6. Validação server-side

Obrigatória:
- usuário autenticado;
- request size limit;
- rate limit;
- content-length coerente quando disponível;
- magic bytes/tipo real;
- extensão compatível com tipo real;
- nome original nunca usado diretamente como caminho interno;
- novo identificador aleatório interno;
- impedir path traversal;
- impedir execução;
- impedir servir arquivo bruto como conteúdo ativo.

## 7. Quarentena

Arquivo novo entra como:
`FILE_STATUS=QUARANTINED`

Somente após validação:
`FILE_STATUS=SAFE_FOR_PARSE`

Falha:
`FILE_STATUS=REJECTED`

O parser só aceita `SAFE_FOR_PARSE`.

## 8. Extração

Saída do parser NÃO é perfil final.

Gerar:
`candidate_profile_draft`.

Cada campo deve conter:
- `value`;
- `confidence`;
- `source_document_id`;
- `source_excerpt` ou localização textual quando seguro/viável;
- `inferred=false/true`;
- `user_confirmed=false` inicialmente.

Campos inferidos não podem ser promovidos silenciosamente a fatos.

## 9. Campos iniciais a extrair

Quando presentes de forma explícita:
- nome;
- cidade/UF;
- telefone/e-mail para conferência, sem usar automaticamente como canal externo;
- resumo profissional;
- experiências;
- empregadores;
- cargos;
- datas;
- formação;
- cursos/certificações;
- idiomas;
- competências citadas;
- links profissionais citados.

Não inferir automaticamente:
- idade;
- raça/etnia;
- religião;
- orientação sexual;
- condição de saúde;
- opinião política;
- salário desejado;
- disponibilidade para mudança;
- autorização de candidatura;
- autorização de exposição ao empregador.

## 10. Confiança

Faixas iniciais:
- `HIGH`: explicitamente identificado com estrutura consistente;
- `MEDIUM`: provável, mas exige atenção do usuário;
- `LOW`: mostrar como sugestão separada ou perguntar, nunca pré-confirmar.

Mesmo HIGH continua precisando da confirmação do usuário para campos operacionais críticos.

## 11. Tela de confirmação

Mostrar cartões por seção, não um formulário gigante.

Exemplo:
`Encontramos estas experiências. Está certo?`

Ações:
- `Tudo certo`
- `Editar`
- `Não é isso`

Campos críticos de privacidade/autonomia sempre têm confirmação explícita própria.

## 12. Empregadores e Proteção de Carreira

Empregadores extraídos do CV alimentam um RASCUNHO de histórico.

Depois perguntar:
- qual é o empregador atual?;
- deseja bloquear o atual e grupo relacionado?;
- quais antigos empregadores deseja bloquear?;
- existem outras empresas a bloquear?

Extração de nome de empresa NÃO equivale a autorização para apresentação ou candidatura.

## 13. Retenção do arquivo bruto

Beta deve adotar minimização.

Preferência arquitetural:
- extrair;
- confirmar;
- manter dados estruturados necessários;
- não reter o arquivo bruto indefinidamente por padrão.

A política exata de retenção deve ser definida antes de testers reais e refletida em aviso/consentimento aplicável.

Usuário deve conseguir saber se o arquivo bruto foi mantido e solicitar exclusão quando aplicável.

## 14. Logs

Permitido registrar:
- document_id interno;
- tamanho;
- tipo detectado;
- status;
- duração;
- código de erro;
- parser version;
- checksum/hash quando necessário para integridade/dedup.

Não registrar em logs gerais:
- texto integral do currículo;
- e-mail/telefone;
- histórico completo;
- trechos sensíveis desnecessários.

## 15. Provider abstraction

Domínio chama:
`LSI_DOCUMENT_INGEST`
`LSI_DOCUMENT_PARSE`
`LSI_FILE_SCAN`

Implementação concreta fica atrás de adapter.

Isso preserva Estrutura Espelho e troca futura de storage/parser/scan sem alterar UX ou contrato lógico.

## 16. Testes mínimos

PASS obrigatório para:
- PDF textual válido;
- DOCX válido;
- extensão falsa;
- MIME falso;
- arquivo vazio;
- arquivo acima do limite;
- PDF protegido;
- DOCX corrompido;
- conteúdo malicioso de teste seguro/EICAR apenas em ambiente apropriado quando scanner existir;
- nomes com caracteres estranhos/path traversal;
- upload sem autenticação;
- upload de usuário A inacessível a usuário B;
- falha de parser sem perda do onboarding;
- retry idempotente;
- exclusão/cleanup;
- logs sem conteúdo sensível.

## 17. Gates

`SAFE_FILE_PIPELINE=PASS` somente quando:
- implementação server-side existir;
- validação real existir;
- isolamento multiusuário estiver provado;
- testes negativos passarem;
- política de retenção estiver definida;
- confirmação de campos estiver implementada;
- evidência de teste estiver registrada.

Documento sozinho NÃO é PASS.

## 18. Próximo passo técnico

Implementar primeiro um parser determinístico em ambiente de desenvolvimento com arquivos sintéticos, sem dados pessoais reais.

Depois conectar ao adapter `LSI_DOCUMENT_PARSE`.

Somente após auth/isolamento e gates negativos, permitir upload por tester real.

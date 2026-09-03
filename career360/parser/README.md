# Career 360 — Parser de Currículo Beta 1.0

Implementação determinística e fail-closed para o primeiro estágio de entrada de currículo.

## Escopo

- PDF textual: `pypdf` open source.
- DOCX: leitura ZIP/XML sem executar macros ou conteúdo ativo.
- Saída: `candidate_profile_draft` com evidência, confiança e `user_confirmed=false`.
- Nenhum dado é persistido ou enviado a terceiros por este módulo.

## Executar

```bash
cd career360/parser
python -m pip install -r requirements.txt
python -m unittest -v test_resume_parser.py
python resume_parser.py /caminho/curriculo.docx
```

## Regra de promoção

Este parser isolado NÃO torna `SAFE_FILE_PIPELINE=PASS`.

Ainda são necessários antes de usuário real:
- upload autenticado server-side;
- quarentena/storage privado;
- autorização por workspace;
- rate limit;
- scan/inspeção de arquivo na arquitetura escolhida;
- política de retenção/exclusão;
- integração da tela de confirmação;
- testes multiusuário e negativos;
- evidência de CI.

Documento canônico: `career360/docs/CAREER360_FILE_INGESTION_V1.md`.

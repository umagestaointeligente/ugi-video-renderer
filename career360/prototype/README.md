# Career 360 — Protótipo Beta 1.0

Protótipo zero-cost, local-first e sem backend obrigatório.

## Objetivo

Validar experiência antes de persistir dados reais:

- onboarding curto;
- currículo como entrada principal;
- voz/texto;
- Proteção de Carreira;
- navegação de cinco áreas;
- linguagem em português;
- dashboard orientado a resultado;
- PWA instalável quando servido por HTTPS/localhost.

## Segurança desta versão

- Nenhum upload é enviado pela implementação atual.
- O protótipo registra apenas estado demonstrativo no `localStorage` do navegador.
- Dados e oportunidades mostrados na Home são demonstrativos.
- Nenhuma candidatura é realizada.
- Nenhuma integração externa é ativada.
- Nenhum modelo pago é chamado.

## Como executar localmente

Em um ambiente com Python 3:

```bash
cd career360/prototype
python -m http.server 8080
```

Abrir `http://localhost:8080`.

Servir por HTTP local ou HTTPS é preferível a abrir o arquivo diretamente, porque Service Workers/PWA dependem de contexto seguro.

## Próximo Degrau

1. teste visual e de usabilidade;
2. parser seguro PDF/DOCX com classificação de confiança;
3. tela de confirmação dos dados extraídos;
4. autenticação e isolamento multiusuário;
5. persistência com políticas de acesso por usuário;
6. Proteção de Carreira com resolução de grupo econômico;
7. Matching Engine V1;
8. logs/auditoria e recuperação;
9. piloto com testers somente após gates P0.

## Regra

> Conte uma vez. A LSI organiza o resto.

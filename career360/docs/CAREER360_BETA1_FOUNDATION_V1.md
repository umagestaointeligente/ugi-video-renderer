# LSI Career 360 — Fundação Canônica Beta 1.0

Status: FOUNDATION / ZERO-COST FIRST
Data: 2026-09-02 BRT

## 1. Missão

Construir o primeiro piloto utilizável do LSI Career 360 com custo incremental zero, arquitetura preparada para evolução progressiva e experiência centrada em redução de esforço.

Regra de experiência:

> Conte uma vez. A LSI organiza o resto.

Regra operacional:

> O cliente não preenche tudo. O cliente confirma, corrige e decide.

## 2. Linguagem

Externamente, priorizar português do Brasil e nomes próprios do ecossistema.

Internamente, nomes técnicos podem permanecer em inglês quando isso melhorar implementação, logs, interoperabilidade ou manutenção.

Exemplos externos:
- Zero-Cost First → Provar a Custo Zero
- Mirror First → Estrutura Espelho
- Minimum Useful Increment → Próximo Degrau
- Infrastructure ROI Score → Índice de Prioridade
- Capacity Stress Simulator → Teste de Fôlego
- Human Action Required → Preciso de Você
- Successful Churn → Missão Cumprida
- Achievement Vault → Cofre de Conquistas
- Career Privacy Shield → Proteção de Carreira
- LSI Hub → Central LSI

## 3. Pilares da incubadora aplicados ao Career 360

1. Provar a Custo Zero.
2. Autonomia desde a Origem.
3. Estrutura Espelho.
4. Evidência antes de capital.
5. Falhar barato e escalar vencedores.
6. Segurança e privacidade nunca podem ser sacrificadas por custo zero.
7. O cliente não deve perceber a complexidade interna.

## 4. Interface Beta 1.0

A interface deve ser simples, legível, agradável e responsiva.

Tela inicial de onboarding:
- Tenho meu currículo
- Prefiro contar minha carreira
- Quero preencher aos poucos

O currículo deverá aceitar inicialmente:
- PDF
- DOCX

Fluxo futuro de extração:
1. arquivo recebido;
2. extração estruturada;
3. dados classificados por nível de confiança;
4. usuário confirma ou corrige;
5. apenas dados confirmados entram no perfil operacional.

Nunca converter inferência em fato.

## 5. Campos mínimos

O onboarding deverá perguntar explicitamente somente o que não puder ser obtido com segurança do currículo ou de informações previamente confirmadas.

Campos críticos iniciais:
- objetivo profissional;
- cargos alvo;
- localizações/modelos de trabalho aceitos;
- faixa salarial quando aplicável;
- situação profissional atual;
- empregador atual;
- empresas que não podem receber o perfil;
- antigos empregadores que o usuário deseje bloquear;
- preferências de autonomia;
- canais de alerta.

## 6. Proteção de Carreira

Usuários empregados devem ter proteção padrão contra exposição ao empregador atual.

Fluxo:
JOB → IDENTIFY_EMPLOYER → RESOLVE_GROUP → PRIVACY_GATE → MATCHING

Se houver bloqueio:
SILENT_BLOCK

Se empregador estiver desconhecido:
EMPLOYER_UNKNOWN = NO_DISCLOSURE

O usuário pode manter lista adicional de empresas bloqueadas.

Nenhum cliente B2B poderá pesquisar nominalmente se um funcionário utiliza Career 360.

## 7. Home do produto

A Home deve responder:

> O que aconteceu desde a última vez que entrei?

Blocos principais:
- Oportunidades
- Retornos
- Preciso de Você
- Tempo economizado
- Insight de carreira
- Meu agente

Navegação inicial:
- Início
- Oportunidades
- Minha Jornada
- Minha Carreira
- Meu Agente

## 8. Voz e texto

A voz é função de primeira classe.

Toda entrada por voz que altere preferência relevante deve ser transcrita e confirmada pelo usuário antes de se tornar uma regra operacional.

O áudio original não precisa ser retido por padrão após transcrição e confirmação, salvo autorização/necessidade específica.

## 9. Motor de Experiência

Nome externo: Motor de Experiência LSI.

Função interna: UX_LEARNING_ENGINE.

Aprender com:
- abandono de onboarding;
- tempo até primeiro valor;
- correções em dados extraídos;
- uso de voz versus texto;
- cliques e navegação;
- erros;
- retornos;
- tarefas concluídas;
- visitas que geraram valor;
- preferências de interface.

Hard rules de segurança não podem ser enfraquecidas pelo aprendizado.

## 10. Evolução controlada

Internamente manter:
- CURRENT_STRATEGY / CHAMPION
- NEW_HYPOTHESIS / CHALLENGER
- SHADOW
- CANARY
- ROLLBACK

Externamente comunicar apenas resultados e melhorias úteis.

## 11. Estrutura Espelho

A arquitetura deverá separar interface de provedores específicos.

A interface chama capacidades lógicas:
- LSI_AI
- LSI_BROWSER
- LSI_STORAGE
- LSI_AUTH
- LSI_ALERTS
- LSI_SUPPORT

Nunca acoplar a experiência do usuário diretamente a um fornecedor.

Objetivo:
ZERO_CUSTOMER_MIGRATION

Mudanças de modelo, banco, browser ou fornecedor devem ser invisíveis ao usuário sempre que tecnicamente possível.

## 12. Próximo Degrau

Investimento futuro somente quando comprar um incremento útil completo de capacidade.

Cada componente deverá registrar:
- nível atual;
- capacidade usada;
- próximo nível;
- custo estimado;
- benefício esperado;
- dependências;
- shadow readiness;
- rollback readiness.

## 13. Operação e suporte

O suporte é parte nativa do produto.

Fluxo:
DETECT → DIAGNOSE → RECOVER → VERIFY → RESUME

Escalonamento:
1. regra determinística;
2. IA econômica/gratuita;
3. IA forte;
4. inteligência crítica em sprint curto e limitado;
5. ação humana apenas quando inevitável.

Falhas externas não devem gerar loops caros de raciocínio.

## 14. Segurança Beta 1.0

Gates mínimos antes de usuários reais:
- SECURITY_P0 = PASS
- CAREER_PRIVACY_P0 = PASS
- DATA_ISOLATION = PASS
- NO_FABRICATION_GUARD = PASS
- HUMAN_ACTION_GATE = PASS
- COST_GUARD = PASS
- SUPPORT_RECOVERY = PASS
- AUDIT_LOG = PASS

## 15. Beta

Meta inicial: 20 testers reais, com diversidade de senioridade, região, setor e situação profissional.

A Beta 1.0 deverá medir:
- ativação;
- tempo até primeiro valor;
- relevância dos matches;
- taxa de correção de dados extraídos;
- incidência de bloqueios;
- resolução autônoma;
- satisfação;
- intenção de pagar;
- custo por usuário;
- intervenção humana.

## 16. North Star de experiência

Não otimizar tempo de tela.

Otimizar:
- clareza;
- confiança;
- valor por visita;
- autonomia;
- redução de esforço;
- resultado útil.

## 17. Primeiro protótipo

O primeiro protótipo deve funcionar sem backend obrigatório e sem armazenamento remoto de dados sensíveis.

Objetivo:
- validar navegação;
- validar linguagem;
- validar onboarding;
- validar hierarquia de informação;
- testar carregamento de currículo como entrada;
- testar Proteção de Carreira;
- testar voz/texto;
- coletar feedback antes de integrar dados reais.

Somente após aprovação de segurança o protótipo evolui para persistência multiusuário real.

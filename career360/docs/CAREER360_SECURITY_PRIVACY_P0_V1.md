# LSI Career 360 — Segurança e Privacidade P0 V1

Status: BLOCKING GATE
Data: 2026-09-02 BRT

Nenhum tester real pode entrar enquanto todos os controles P0 aplicáveis estiverem implementados e testados.

## 1. Princípios

1. Menor privilégio.
2. Menor coleta possível.
3. Nenhuma inferência crítica vira fato sem confirmação.
4. Dados de carreira e dados de empregador devem permanecer segregados.
5. Nenhum cliente B2B pode descobrir se um funcionário utiliza Career 360.
6. Nenhum agente recebe mais contexto do que precisa.
7. Logs não devem registrar segredos, tokens, CV integral ou PII desnecessária.
8. Segurança não pode ser enfraquecida pelo Motor de Experiência ou pelo aprendizado contínuo.

## 2. Gate de Identidade

- autenticação individual;
- IDs internos não derivados de e-mail/CPF;
- sessão expirada/rotacionada adequadamente;
- suporte a MFA quando a camada de autenticação escolhida permitir;
- nenhuma credencial de terceiro armazenada em texto claro;
- nenhum segredo em frontend.

## 3. Gate de Isolamento

Cada recurso sensível deve possuir escopo de usuário/workspace.

Objetos mínimos:
- profile;
- career_preferences;
- documents;
- employer_denies;
- opportunities;
- applications;
- messages/events;
- agent_permissions;
- audit_events;
- incidents.

Teste obrigatório:
USER_A nunca consegue ler/escrever dados de USER_B por alteração de URL, ID, payload, cache ou chamada direta.

## 4. Proteção de Carreira

Fluxo obrigatório antes de exposição:

JOB
→ IDENTIFY_EMPLOYER
→ RESOLVE_GROUP
→ PRIVACY_GATE
→ MATCHING

Se a empresa ou grupo estiver bloqueado:
SILENT_BLOCK

Se empregador for desconhecido/confidencial:
NO_DISCLOSURE

O candidato pode visualizar oportunidade sem ter sua identidade apresentada automaticamente.

## 5. Dados do currículo

Upload permitido inicialmente:
- PDF;
- DOCX.

Pipeline futuro:
UPLOAD
→ FILE_VALIDATION
→ MALWARE/TYPE_CHECK
→ TEXT_EXTRACTION
→ STRUCTURED_CANDIDATES
→ CONFIDENCE_SCORE
→ USER_CONFIRMATION
→ VERIFIED_PROFILE

Dados extraídos com baixa confiança nunca entram silenciosamente em campos operacionais.

## 6. Áudio

- consentimento explícito para acesso ao microfone;
- transcrição mostrada ao usuário;
- instruções críticas exigem confirmação;
- áudio bruto não deve ser retido por padrão se a finalidade puder ser satisfeita com transcrição estruturada confirmada;
- nenhuma gravação silenciosa.

## 7. Ações externas

Classificar cada ação:

AUTONOMIA SEGURA
- pode executar dentro de autorização prévia e regras conhecidas.

PRECISO DE VOCÊ
- MFA, CAPTCHA, decisão pessoal, confirmação sensível ou ação não autorizada.

BLOQUEIO EXTERNO
- indisponibilidade, rate limit, mudança de site, erro do terceiro.

Nunca contornar CAPTCHA/MFA.

## 8. No-Fabrication Guard

Proibido inventar:
- empregador;
- cargo;
- datas;
- salário;
- formação;
- habilidade;
- experiência;
- resultado;
- candidatura;
- resposta;
- entrevista;
- oferta.

Estados sem evidência permanecem UNKNOWN/PENDING.

## 9. Logs e auditoria

Cada ação material deve registrar:
- event_id;
- workspace_id;
- actor_type;
- action_type;
- target_type;
- timestamp;
- outcome;
- evidence_class;
- reason_code;
- correlation_id.

Não registrar conteúdo sensível quando metadado suficiente resolver a finalidade operacional.

## 10. Recuperação

Fluxo:
DETECT → DIAGNOSE → RECOVER → VERIFY → RESUME

Circuit breaker obrigatório para erros repetidos.

Falha externa:
CHECKPOINT_SAFE → CHEAP_PROBE → RESUME_WHEN_HEALTHY

Inteligência cara nunca fica em loop aguardando terceiro voltar.

## 11. Exclusão e portabilidade

A arquitetura deve permitir:
- exportar dados do usuário;
- excluir dados sujeitos a exclusão;
- revogar permissões;
- retirar empresas da lista de bloqueio;
- encerrar agente sem perder rastreabilidade legal mínima quando aplicável.

## 12. Segurança do protótipo atual

O protótipo `career360/prototype` deliberadamente:
- não possui backend;
- não envia currículo;
- não persiste dados remotamente;
- não executa candidaturas;
- não utiliza modelos pagos;
- não possui integração B2B.

Ele existe apenas para validar UX/fluxo antes da abertura da superfície de dados.

## 13. Critério de liberação Beta

Só liberar usuários reais após:

SECURITY_P0 = PASS
PRIVACY_P0 = PASS
ISOLATION_TEST = PASS
NO_FABRICATION = PASS
FILE_PIPELINE_SAFE = PASS
AUDIT_LOG = PASS
RECOVERY_FLOW = PASS
COST_GUARD = PASS

Qualquer FAIL mantém:
BETA_USERS_REAL = BLOCKED

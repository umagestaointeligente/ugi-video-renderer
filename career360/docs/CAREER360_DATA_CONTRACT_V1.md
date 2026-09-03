# LSI Career 360 — Contrato de Dados V1

Status: DESIGN CONTRACT

Objetivo: permitir que banco, autenticação e provedores possam evoluir sem exigir migração de experiência do cliente.

## Entidades lógicas

### workspace
- workspace_id
- user_id
- status
- created_at
- locale

### verified_profile
- workspace_id
- full_name
- city
- region
- current_role
- current_employer
- employment_status
- seniority
- summary
- verification_state
- updated_at

### career_preference
- workspace_id
- target_roles[]
- target_seniority[]
- locations[]
- work_models[]
- salary_floor
- salary_currency
- search_mode
- alert_frequency

### document
- document_id
- workspace_id
- type
- original_name
- storage_pointer
- malware_state
- extraction_state
- created_at

### extracted_claim
- claim_id
- workspace_id
- document_id
- claim_type
- raw_value
- normalized_value
- confidence
- confirmation_state
- source_locator

Regra: apenas CONFIRMED pode promover informação sensível para `verified_profile` ou experiência operacional.

### employer_deny
- deny_id
- workspace_id
- employer_name
- employer_identifier
- deny_reason
- scope
- source
- status

### employer_graph_edge
- edge_id
- employer_identifier_a
- employer_identifier_b
- relation_type
- evidence_level
- source
- verified_at

### opportunity
- opportunity_id
- employer_identifier
- external_source
- external_reference
- role_title
- location
- work_model
- compensation_state
- active_state
- evidence_level

### match_result
- match_id
- workspace_id
- opportunity_id
- candidate_fit
- company_fit
- mutual_quality
- explanation
- privacy_gate_state
- generated_at

### application
- application_id
- workspace_id
- opportunity_id
- status
- execution_mode
- evidence_level
- external_reference
- last_action_at

Estados recomendados:
DISCOVERED / QUALIFIED / READY / APPLIED / RESPONSE / INTERVIEW / FINAL_STAGE / OFFER / REJECTED / WITHDRAWN / CLOSED / BLOCKED

### agent_permission
- permission_id
- workspace_id
- capability
- scope
- granted_at
- revoked_at

### incident
- incident_id
- workspace_id
- capability
- severity
- reason_code
- state
- checkpoint
- created_at
- resolved_at

### audit_event
- event_id
- workspace_id
- actor_type
- action_type
- target_type
- target_id
- outcome
- evidence_class
- reason_code
- correlation_id
- created_at

## Regras transversais

1. Toda entidade sensível deve ser escopada por workspace quando aplicável.
2. IDs devem ser opacos e não sequenciais quando expostos externamente.
3. O frontend nunca recebe segredo de serviço.
4. Dados de empresa B2B e candidato B2C devem usar domínios de autorização separados.
5. O Matching Engine recebe apenas os atributos necessários para cálculo.
6. Logs não substituem banco de negócio.
7. Dados derivados devem apontar para evidência/origem quando possível.
8. UNKNOWN não pode ser promovido silenciosamente a fato.
9. Schema deve ser versionado.
10. Exportação e exclusão devem ser possíveis por workspace dentro das obrigações aplicáveis.

## Abstração de provedor

A aplicação deve consumir interfaces lógicas:
- IdentityRepository
- ProfileRepository
- DocumentRepository
- OpportunityRepository
- MatchingRepository
- AuditRepository
- IncidentRepository

O provedor físico pode mudar sem alterar contratos da interface do usuário.

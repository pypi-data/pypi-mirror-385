# Actions

Transform Ontologia into an interactive, operational platform by enabling user‑triggered Actions on objects. Actions encapsulate business logic with strong typing, safe validation, and optional external writebacks.

- Control plane: Action definitions live in SQLModel (`ActionType`).
- Data plane: Actions operate on instances (objects) and may update state.
- Execution: Safe, registry‑based Python functions referenced by `executor_key`.

## Philosophy

- Metadata in DB, code in repo. No executable code in the database.
- Strong contracts: typed parameters, submission criteria, and validation rules.
- Safe evaluation: restricted DSL for rules; no arbitrary Python execution.
- Modular: register new Actions without changing core services.

## Metamodel: `ActionType`

Path: `ontologia/domain/metamodels/types/action_type.py`

Important fields:
- `api_name` / `display_name` / `description` — resource identity
- `target_object_type_api_name` — the ObjectType this Action applies to
- `parameters: dict[str, dict]` — parameter schema (per param):
  - `dataType`: string | integer | double | boolean | date | timestamp
  - `displayName`: human‑readable label
  - `description`: optional
  - `required`: default true
- `submission_criteria: list[dict]` — when to show/allow this Action
  - `{ "description": str, "rule_logic": str }`
- `validation_rules: list[dict]` — pre-execution business validation
  - `{ "description": str, "rule_logic": str }`
- `executor_key: str` — maps to a registered Python function

## Registry: map `executor_key` to code

Path: `api/actions/registry.py`

- Register functions with `@register_action("domain.action_name")`.
- Signature: `def func(context: dict, params: dict) -> dict`
  - `context`: `{ "target_object": ObjectInstanceDTO, "session": Session, "user": dict, ... }`
    - `user` is injected by the API (see Authentication & User Context). Use it for auditing and authorization checks.
  - Return: JSON-serializable dict (merged into API response).

Example (bundled): `api/actions/test_actions.py`

## Service: `ActionsService`

Path: `api/services/actions_service.py`

Responsibilities:
- Resolve `ActionType` from metamodel
- Fetch target object (DTO) via `InstancesService`
- Evaluate `submission_criteria` and `validation_rules` (restricted AST)
- Validate and coerce parameters to expected types
- Execute the registered function within a DB transaction (commit/rollback)
- Provide `context['user']` to executors and rules (when Authorization is present)
- Map `ActionValidationError` to structured HTTP errors

## API

Base prefix: `/v2/ontologies/{ontologyApiName}`

- Discover
  - `GET /objects/{objectTypeApiName}/{pk}/actions`
  - Response: `{ "data": [ { "apiName", "displayName", "targetObjectType", "parameters"... } ] }`
- Execute
  - `POST /objects/{objectTypeApiName}/{pk}/actions/{actionApiName}/execute`
  - Body: `{ "parameters": { ... } }`
  - Response: action-specific dict (must be JSON serializable)

- Asynchronous (Temporal; requires `USE_TEMPORAL_ACTIONS=1`)
  - `POST /objects/{objectTypeApiName}/{pk}/actions/{actionApiName}/start` → fire-and-forget; returns `{workflowId, runId, status: "started"}`
  - `GET  /actions/runs/{workflowId}` → returns `{workflowId, runId, status}`
  - `POST /actions/runs/{workflowId}:cancel` → returns `{workflowId, runId, status: "canceled"}`

Ordering note: The Actions router is registered before the dynamic traversal route to ensure `/actions` resolves to the Actions endpoint, not as a `linkTypeApiName`.

## Authentication & User Context

- The Actions endpoints accept the standard `Authorization` header. The default implementation provides a minimal stub that injects a user object into `context`:
  - If present: `context['user'] = {"id": <token>, "role": "user"}` (replace with real JWT/session in production).
  - If absent: `context['user'] = {"id": "anonymous", "role": "user"}`.
- Rules can reference the user via `context`:
  - Example: `context['user']['role'] == 'admin'`.
- Executors can audit the actor via `context['user']`.

## Error Semantics

- 404 Not Found
  - ActionType not found, or target object not found.
- 403 Forbidden
  - Submission criteria not satisfied (Action not available for the current target/context).
- 400 Bad Request
  - Parameter validation failed (coercion/type/required) with payload: `{ "message": "Invalid parameters", "errors": [ {"field","code","message"}, ... ] }`.
  - Business validation failed: API maps `ActionValidationError` to a structured payload `{ "code", "message", "details"? }`.
- 501 Not Implemented
  - `executor_key` not registered.

Examples (error payloads):

```json
{ "detail": "Action not available" }
```

```json
{ "detail": { "message": "Invalid parameters", "errors": [ {"field": "amount", "code": "type_error.integer", "message": "Must be integer"} ] } }
```

```json
{ "detail": { "code": "business_rule", "message": "Limit exceeded", "details": {"max": 1000} } }
```

## Quickstart (local)

1) Define an `ObjectType` and upsert an instance.
2) Create an `ActionType` via API:

```bash
curl -X PUT http://localhost:8000/v2/ontologies/default/actionTypes/approve_expense \
  -H 'Content-Type: application/json' \
  -d '{
    "displayName": "Approve Expense",
    "targetObjectType": "expense",
    "parameters": {"message": {"dataType": "string", "displayName": "Message", "required": true}},
    "submissionCriteria": [{"description": "only pending", "ruleLogic": "target_object['properties']['status']=='PENDING'"}],
    "validationRules": [],
    "executorKey": "system.log_message"
  }'
```

3) Call the API:

```bash
curl http://localhost:8000/v2/ontologies/default/objects/expense/e1/actions | jq
curl -X POST http://localhost:8000/v2/ontologies/default/objects/expense/e1/actions/approve_expense/execute \
  -H 'Content-Type: application/json' \
  -d '{"parameters": {"message": "approved"}}' | jq
```

### Asynchronous execution (Temporal)

Prerequisites:

- `export USE_TEMPORAL_ACTIONS=1`
- Temporal dev stack running: `just temporal-up`
- Worker running: `just temporal-worker`

Examples:

```bash
# 1) Start (returns workflow/run IDs)
curl -X POST \
  http://localhost:8000/v2/ontologies/default/objects/expense/e1/actions/approve_expense/start \
  -H 'Content-Type: application/json' \
  -d '{"parameters": {"message": "approved"}}' | jq

# 2) Status
curl "http://localhost:8000/v2/ontologies/default/actions/runs/<workflowId>?runId=<runId>" | jq

# 3) Cancel
curl -X POST \
  "http://localhost:8000/v2/ontologies/default/actions/runs/<workflowId>:cancel?runId=<runId>" | jq
```

## Roadmap

- Enhance Temporal workflows:
  - richer status payloads and progress reporting
  - list runs by object/action
  - retries/backoff policies per action
- Bulk Actions endpoint to execute a single Action across multiple objects.
- Enrich `context` with request metadata and real authz integration.
- Expanded rule DSL (e.g., date math helpers) while preserving sandbox safety.

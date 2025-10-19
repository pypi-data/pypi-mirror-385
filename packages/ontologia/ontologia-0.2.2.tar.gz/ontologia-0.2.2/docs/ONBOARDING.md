# Developer Onboarding

Fast, practical guide to get productive with Ontologia in minutes.

## Prerequisites

- Python 3.11+ (see `pyproject.toml` → `requires-python = ">=3.11"`)
- uv (recommended) or pip
- Optional for graph: KùzuDB (`pip install kuzu`), DuckDB (`pip install duckdb`), Polars (`pip install polars`)

## Clone & Setup

```bash
# Clone
git clone https://github.com/kevinqz/ontologia.git
cd ontologia

# Install deps (dev)
uv sync --dev

# Run tests
uv run pytest -q
```

## Run the API

```bash
uv run uvicorn api.main:app --reload
# http://localhost:8000/docs
```

Graph-backed reads (default) and optional writes/unified mode are configured via `[features]` in `ontologia.toml`. For quick, temporary overrides:

```bash
# Reads use KùzuDB when available; adjust path as needed
export KUZU_DB_PATH=instance_graph.kuzu
# Enable graph write-through for this shell even if the manifest disables it
export USE_GRAPH_WRITES=1
# Unified graph mode is always active; exporting USE_UNIFIED_GRAPH only reinforces the default
export USE_UNIFIED_GRAPH=1
```

## Quick Workflow (Metamodel → Data → Traversal)

1) Define ObjectTypes and LinkTypes

```bash
# Create an ObjectType
curl -X PUT http://localhost:8000/v2/ontologies/default/objectTypes/employee \
  -H 'Content-Type: application/json' \
  -d '{
    "displayName": "Employee",
    "primaryKey": "id",
    "properties": {"id": {"dataType": "string", "displayName": "ID", "required": true}}
  }'

# Create a LinkType (employee -> company)
curl -X PUT http://localhost:8000/v2/ontologies/default/linkTypes/works_for \
  -H 'Content-Type: application/json' \
  -d '{
    "displayName": "Works For",
    "cardinality": "MANY_TO_ONE",
    "fromObjectType": "employee",
    "toObjectType": "company",
    "inverse": {"apiName": "has_employees", "displayName": "Has Employees"}
  }'
```

### Interfaces (Contratos Semânticos)

Veja `docs/INTERFACES.md` para uma visão completa. Resumo rápido:

```bash
# Criar uma Interface
curl -X PUT http://localhost:8000/v2/ontologies/default/interfaces/Localizavel \
  -H 'Content-Type: application/json' \
  -d '{
    "displayName": "Localizável",
    "properties": {"address": {"dataType": "string", "displayName": "Address"}}
  }'

# Fazer um ObjectType implementar a Interface
curl -X PUT http://localhost:8000/v2/ontologies/default/objectTypes/cliente \
  -H 'Content-Type: application/json' \
  -d '{
    "displayName": "Cliente",
    "primaryKey": "id",
    "properties": {"id": {"dataType": "string", "displayName": "ID", "required": true}},
    "implements": ["Localizavel"]
  }'
```

Quando o KùzuDB está disponível, as leituras são "graph-first" por padrão (`features.use_graph_reads = true`). O modo unificado do grafo está sempre ativo, então a listagem por Interface usa um único caminho sobre o nó `Object` sem `UNION`.

2) Upsert instances and links

```bash
# Upsert objects
curl -X PUT http://localhost:8000/v2/ontologies/default/objects/employee/e1 -H 'Content-Type: application/json' -d '{"properties": {}}'
curl -X PUT http://localhost:8000/v2/ontologies/default/objects/company/c1 -H 'Content-Type: application/json' -d '{"properties": {}}'

# Create link e1 -> c1
curl -X POST http://localhost:8000/v2/ontologies/default/links/works_for \
  -H 'Content-Type: application/json' \
  -d '{"fromPk": "e1", "toPk": "c1"}'
```

3) Traverse the graph

```bash
curl "http://localhost:8000/v2/ontologies/default/objects/employee/e1/works_for?limit=100&offset=0"
```

### Actions (Operações de Negócio)

Defina Actions no plano de controle e exponha botões/fluxos operacionais para objetos.

1) Crie um `ActionType` via API:

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

2) Descobrir e executar:

```bash
curl http://localhost:8000/v2/ontologies/default/objects/expense/e1/actions | jq
curl -X POST http://localhost:8000/v2/ontologies/default/objects/expense/e1/actions/approve_expense/execute \
  -H 'Content-Type: application/json' \
  -d '{"parameters": {"message": "approved"}}' | jq
```

Autenticação & contexto:

- Os endpoints aceitam `Authorization: Bearer <token>`. Por padrão, o usuário é injetado no `context['user']` para regras e executores. Em produção, substitua pelo seu provedor de identidade.

Veja `docs/ACTIONS.md` para detalhes (DSL de regras, registro de executores, melhores práticas, semântica de erro estruturada).

4) Search objects (Busca avançada)

```bash
curl -X POST http://localhost:8000/v2/ontologies/default/objects/person/search \
  -H 'Content-Type: application/json' \
  -d '{
    "where": [
      {"property": "city", "op": "eq", "value": "São Paulo"},
      {"property": "age", "op": "gt", "value": 30}
    ],
    "orderBy": [{"property": "age", "direction": "desc"}],
    "limit": 100,
    "offset": 0
  }'
```

5) Bulk load (Carga em lote)

```bash
# Objetos
curl -X POST http://localhost:8000/v2/ontologies/default/objects/employee/load \
  -H 'Content-Type: application/json' \
  -d '{
    "items": [
      {"pk": "e1", "properties": {"age": 25, "dept": "ENG"}},
      {"pk": "e2", "properties": {"age": 35, "dept": "ENG"}}
    ]
  }'

# Links (create/delete)
curl -X POST http://localhost:8000/v2/ontologies/default/links/works_in/load \
  -H 'Content-Type: application/json' \
  -d '{
    "mode": "create",
    "items": [
      {"fromPk": "e1", "toPk": "d1"},
      {"fromPk": "e2", "toPk": "d1"}
    ]
  }'
```

6) Analytics (Agregações)

```bash
curl -X POST http://localhost:8000/v2/ontologies/default/aggregate \
  -H 'Content-Type: application/json' \
  -d '{
    "objectTypeApiName": "employee",
    "groupBy": ["dept"],
    "metrics": [
      {"func": "count"},
      {"func": "avg", "property": "age"}
    ]
  }'
```

## Schema Evolution (Manifest-First)

1. Atualize os YAMLs em `ontologia/project/definitions/**` (ObjectTypes e LinkTypes).
2. Use a Ferramenta MCP `plan_schema_changes` (exposta pelo ArchitectAgent) para validar o plano e opcionalmente incluir `impact`/`dependencies`.
3. Aplique o plano com `apply_schema_changes`; passe `allow_destructive=true` apenas quando o plano apontar remoções ou mudanças de tipo.
4. Acompanhe tarefas de migração geradas via `list_migration_tasks` e marque a conclusão com `update_migration_task` depois de executar a migração de dados correspondente.
5. Automatize a execução via CLI: `ontologia migrations run <rid>` para uma tarefa específica ou `ontologia migrations run-pending` para processar todas as pendentes (use `--dry-run` para validar sem aplicar).

## ArchitectAgent (Autonomia)

- **Nova ferramenta relacional**: use `analyze_relational_schema` quando trabalhar com bancos SQL completos. Ela lista tabelas e chaves estrangeiras, facilitando a proposição de novos `LinkTypes` a partir de relações `MANY_TO_ONE`.
- **Loop de autocorreção**: o comando `ontologia agent` agora aplica o plano, executa o pipeline (`run_pipeline`) e, em caso de erro, reapresenta o log para que o agente gere um plano corretivo minimalista. Você pode cancelar ou aceitar cada iteração.
- **Monitoramento em tempo real**: o agente pode chamar `stream_ontology_events` para amostrar eventos WebSocket sem manter conexões longas. Útil para detectar propriedades que surgem em produção.
- **Modo vigilante**: rode `uv run python scripts/run_watcher_agent.py` para coletar eventos periodicamente. Planos não vazios são gravados em `plans_for_review/` para revisão humana antes de qualquer aplicação.

## Sync Service (Optional)

Use `scripts/main_sync.py` to set up a minimal control plane and run a sync:

```bash
export DUCKDB_PATH=analytics.duckdb
export SYNC_SETUP=1
uv run python scripts/main_sync.py
```

- Relationship loading can use a fast COPY path when `SYNC_ENABLE_COPY_RELS=1`.
- Data Quality: defina `quality_checks` nos `PropertyType` (p.ex. `not_null`, `in[...]`, `between[...]`); linhas inválidas são quarentenadas em `data/quarantine/` e não carregadas no grafo.
- Time Travel: vincule `ObjectTypeDataSource` a um `DatasetBranch`; a sincronização lê da `head_transaction` do branch. O vínculo legado via `dataset_rid` ainda é suportado.
- See `SYNC_SERVICE_GUIDE.md` and `docs/SYNC.md` for details.

### Data Quality (qualityChecks) — Exemplo Rápido

1) Defina regras de qualidade na propriedade via API:

```bash
curl -X PUT http://localhost:8000/v2/ontologies/default/objectTypes/customer \
  -H 'Content-Type: application/json' \
  -d '{
    "displayName": "Customer",
    "primaryKey": "id",
    "properties": {
      "id": {"dataType": "string", "displayName": "ID", "required": true},
      "name": {"dataType": "string", "displayName": "Name", "qualityChecks": ["not_null", "min_length[3]"]},
      "status": {"dataType": "string", "displayName": "Status", "qualityChecks": ["in[ACTIVE,INACTIVE]"]}
    }
  }'
```

2) Leia o ObjectType e verifique o retorno de `qualityChecks`:

```bash
curl http://localhost:8000/v2/ontologies/default/objectTypes/customer | jq
```

3) Ao executar o sync, linhas que não atendem às regras são isoladas em `data/quarantine/<objectType>-<timestamp>.parquet` e não são carregadas no grafo.

## Codebase Layout

- `api/` FastAPI app, routers, services, repositories, schemas
- `ontologia/` domain models and application services (e.g., sync)
- `datacatalog/` dataset/metadata models
- `tests/` unit and integration tests

## Where to Read Next

- `docs/ARCHITECTURE.md` — Big picture
- `docs/API_REFERENCE.md` — Endpoints
- `docs/ENVIRONMENT.md` — Flags and behavior
- `SYNC_SERVICE_GUIDE.md` — Deep dive into sync

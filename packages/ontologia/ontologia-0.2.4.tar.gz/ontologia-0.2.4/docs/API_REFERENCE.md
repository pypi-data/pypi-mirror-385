# API Reference (v2)

Base path prefix: `/v2/ontologies/{ontologyApiName}`

- Replace `{ontologyApiName}` with your tenant/ontology ID, e.g. `default`.

## Health

- **GET /** — Basic health
- **GET /health** — Detailed component status

## Object Types

- **GET /objectTypes** — List all ObjectTypes
- **GET /objectTypes/{objectTypeApiName}** — Get one
- **PUT /objectTypes/{objectTypeApiName}** — Create/Update
- **DELETE /objectTypes/{objectTypeApiName}** — Delete

Example (PUT):

```bash
curl -X PUT http://localhost:8000/v2/ontologies/default/objectTypes/employee \
  -H 'Content-Type: application/json' \
  -d '{
    "displayName": "Employee",
    "primaryKey": "id",
    "properties": {"id": {"dataType": "string", "displayName": "ID", "required": true}}
  }'
```

## Link Types

- **GET /linkTypes** — List all LinkTypes
- **GET /linkTypes/{linkTypeApiName}** — Get one
- **PUT /linkTypes/{linkTypeApiName}** — Create/Update
- **DELETE /linkTypes/{linkTypeApiName}** — Delete

Example (PUT):

```bash
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

## Interfaces

- **GET /interfaces** — List all Interfaces
- **GET /interfaces/{interfaceApiName}** — Get one
- **PUT /interfaces/{interfaceApiName}** — Create/Update
- **DELETE /interfaces/{interfaceApiName}** — Delete

Example (PUT):

```bash
curl -X PUT http://localhost:8000/v2/ontologies/default/interfaces/Localizavel \
  -H 'Content-Type: application/json' \
  -d '{
    "displayName": "Localizável",
    "properties": {"address": {"dataType": "string", "displayName": "Address"}}
  }'
```

## Objects

- **PUT /objects/{objectTypeApiName}/{pk}** — Upsert instance
- **GET /objects/{objectTypeApiName}/{pk}** — Get instance
- **DELETE /objects/{objectTypeApiName}/{pk}** — Delete instance
- **GET /objects** — List instances (optional `objectType`, `limit`, `offset`)
- **GET /objects/{objectTypeApiName}** — List by type (`limit`, `offset`)
- **GET /objects/{objectTypeApiName}/{pk}/{linkTypeApiName}** — Traverse linked objects (`limit`, `offset`)
- **POST /objects/{objectTypeApiName}/search** — Advanced search by properties (filters, order, pagination)
- **POST /objects/{objectTypeApiName}/load** — Bulk upsert objects
- **POST /objects/{objectTypeApiName}/aggregate** — Nested aggregate for a specific ObjectType

Example (Upsert):

```bash
curl -X PUT http://localhost:8000/v2/ontologies/default/objects/employee/e1 \
  -H 'Content-Type: application/json' \
  -d '{"properties": {"id": "e1"}}'
```

Example (Traversal):

```bash
curl "http://localhost:8000/v2/ontologies/default/objects/employee/e1/works_for?limit=100&offset=0"
```

Example (Search):

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

Example (Bulk load objects):

```bash
curl -X POST http://localhost:8000/v2/ontologies/default/objects/employee/load \
  -H 'Content-Type: application/json' \
  -d '{
    "items": [
      {"pk": "e1", "properties": {"age": 25, "dept": "ENG"}},
      {"pk": "e2", "properties": {"age": 35, "dept": "ENG"}}
    ]
  }'
```

Example (Nested aggregate for a specific ObjectType):

```bash
curl -X POST \
  http://localhost:8000/v2/ontologies/default/objects/employee/aggregate \
  -H 'Content-Type: application/json' \
  -d '{
    "where": [],
    "groupBy": ["dept"],
    "metrics": [
      {"func": "count"},
      {"func": "avg", "property": "age"}
    ]
  }'
```

## Links (Edges)

- **POST /links/{linkTypeApiName}** — Create link
  - Body: `{ "fromPk": "...", "toPk": "..." }`
- **GET /links/{linkTypeApiName}** — List links (optional `fromPk`, `toPk`)
- **GET /links/{linkTypeApiName}/{fromPk}/{toPk}** — Get one link
- **DELETE /links/{linkTypeApiName}/{fromPk}/{toPk}** — Delete link
- **POST /links/{linkTypeApiName}/load** — Bulk create/delete links (body includes `mode`: create|delete)

Example (Create link):

```bash
curl -X POST http://localhost:8000/v2/ontologies/default/links/works_for \
  -H 'Content-Type: application/json' \
  -d '{"fromPk": "e1", "toPk": "c1"}'
```

Example (Bulk load links):

```bash
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

## Datasets (Data Catalog)

- **GET /datasets** — List datasets
- **GET /datasets/{datasetApiName}** — Get dataset
- **PUT /datasets/{datasetApiName}** — Create/Update dataset
- **DELETE /datasets/{datasetApiName}** — Delete dataset (and dependent branches/transactions)
- **POST /datasets/{datasetApiName}/transactions** — Create transaction (SNAPSHOT/APPEND)
- **GET /datasets/{datasetApiName}/branches** — List branches
- **PUT /datasets/{datasetApiName}/branches/{branchName}** — Create/Update branch (points to a transaction)

Example (Create dataset):

```bash
curl -X PUT http://localhost:8000/v2/ontologies/default/datasets/sales_gold \
  -H 'Content-Type: application/json' \
  -d '{
    "displayName": "Sales (Gold)",
    "sourceType": "duckdb_table",
    "sourceIdentifier": "gold.sales",
    "schemaDefinition": {"columns": [{"name": "id", "type": "string"}]}
  }'
```

Example (Create transaction):

```bash
curl -X POST http://localhost:8000/v2/ontologies/default/datasets/sales_gold/transactions \
  -H 'Content-Type: application/json' \
  -d '{"transactionType": "SNAPSHOT", "commitMessage": "initial"}'
```

Example (Create branch):

```bash
curl -X PUT \
  http://localhost:8000/v2/ontologies/default/datasets/sales_gold/branches/main \
  -H 'Content-Type: application/json' \
  -d '{"headTransactionRid": "<RID_FROM_TRANSACTION_RESPONSE>"}'
```

Example (List branches):

```bash
curl http://localhost:8000/v2/ontologies/default/datasets/sales_gold/branches | jq
```

Example (Delete dataset):

```bash
curl -X DELETE http://localhost:8000/v2/ontologies/default/datasets/sales_gold
```

## Analytics

- **POST /aggregate** — Aggregations over objects (COUNT/SUM/AVG) with optional `groupBy` and filters

Example (Aggregate: count by dept, avg age):

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

## Query Types

- **GET /queryTypes** — List QueryTypes
- **GET /queryTypes/{queryApiName}** — Get one
- **PUT /queryTypes/{queryApiName}** — Create/Update
- **DELETE /queryTypes/{queryApiName}** — Delete
- **POST /queries/{queryApiName}/execute** — Execute a saved query with parameters

Example (PUT with SDK-parity aliases: targetApiName + unified query object):

```bash
curl -X PUT http://localhost:8000/v2/ontologies/default/queryTypes/adults_in_region \
  -H 'Content-Type: application/json' \
  -d '{
    "displayName": "Adults In Region",
    "targetApiName": "customer",
    "parameters": {
      "minAge": {"dataType": "integer", "displayName": "Min Age", "required": true},
      "region": {"dataType": "string", "displayName": "Region", "required": true}
    },
    "query": {
      "where": [
        {"property": "age", "op": "gte", "value": "{{minAge}}"},
        {"property": "region", "op": "eq", "value": "{{region}}"}
      ],
      "orderBy": [{"property": "age", "direction": "asc"}]
    }
  }'
```

Example (Execute):

```bash
curl -X POST \
  http://localhost:8000/v2/ontologies/default/queries/adults_in_region/execute \
  -H 'Content-Type: application/json' \
  -d '{"parameters": {"minAge": 30, "region": "EU"}, "limit": 100, "offset": 0}'
```

Alternative (backward-compatible templates):

```bash
curl -X PUT http://localhost:8000/v2/ontologies/default/queryTypes/adults_in_region \
  -H 'Content-Type: application/json' \
  -d '{
    "displayName": "Adults In Region",
    "targetObjectType": "customer",
    "parameters": {
      "minAge": {"dataType": "integer", "displayName": "Min Age", "required": true},
      "region": {"dataType": "string", "displayName": "Region", "required": true}
    },
    "whereTemplate": [
      {"property": "age", "op": "gte", "value": {"param": "minAge"}},
      {"property": "region", "op": "eq", "value": {"param": "region"}}
    ],
    "orderByTemplate": [{"property": "age", "direction": "asc"}]
  }'
```

Notes:

- **Placeholders**: Both `{ "param": "name" }` and string templates `"{{name}}"` are accepted.
- **Interface targets**: `targetApiName` may reference an Interface. Execution will union results across implementers (graph-first with SQL fallback).

## Actions

- **GET /objects/{objectTypeApiName}/{pk}/actions** — List available Actions for a specific object (after evaluating submission criteria)
- **POST /objects/{objectTypeApiName}/{pk}/actions/{actionApiName}/execute** — Execute an Action with parameters (blocking)
 - **POST /objects/{objectTypeApiName}/{pk}/actions/{actionApiName}/start** — Start an Action asynchronously via Temporal (returns workflow identifiers)
 - **GET /actions/runs/{workflowId}** — Get Action run status (Temporal)
 - **POST /actions/runs/{workflowId}:cancel** — Cancel Action run (Temporal)

Temporal (when `USE_TEMPORAL_ACTIONS=1`):

- **POST /objects/{objectTypeApiName}/{pk}/actions/{actionApiName}/start** — Fire-and-forget; returns workflow identifiers
- **GET /actions/runs/{workflowId}** — Workflow status by `workflowId` (optional `runId`)
- **POST /actions/runs/{workflowId}:cancel** — Cancel a running workflow (optional `runId`)

Schemas (see `api/v2/schemas/actions.py`):

- `ActionParameterDefinition`
- `ActionReadResponse`
- `ActionListResponse`
- `ActionExecuteRequest`
- `ActionExecuteResponse` (allows extra fields)

Example (Discovery):

```bash
curl http://localhost:8000/v2/ontologies/default/objects/expense/e1/actions | jq
```

Example (Discovery response structure):

```json
{
  "data": [
    {
      "apiName": "approve_expense",
      "rid": "...",
      "displayName": "Approve Expense",
      "description": "Approve expense when pending",
      "targetObjectType": "expense",
      "parameters": {
        "message": {
          "dataType": "string",
          "displayName": "Message",
          "description": null,
          "required": true
        }
      }
    }
  ],
  "nextPageToken": null
}
```

### Link properties

Foundry supports properties on links (edges) in addition to object properties. These are first-class attributes that belong to the relation itself (e.g., "sinceDate" on an Employee → Company employment link).

- Defined in `LinkTypePutRequest.properties` as a map `propertyApiName → PropertyDefinition`.
- Returned on link reads under `linkProperties` in `LinkedObjectReadResponse`.
- During sync, use `propertyMappings` to map dataset columns to link property names and `incrementalField` to perform APPEND incremental syncs for relations.

Example: define a link with properties and a backing dataset mapping

```http
PUT /v2/ontologies/{ontologyApiName}/linkTypes/works_for
```

```json
{
  "displayName": "Works For",
  "cardinality": "MANY_TO_ONE",
  "fromObjectType": "employee",
  "toObjectType": "company",
  "inverse": { "apiName": "has_employees", "displayName": "Has Employees" },
  "description": "Employment relation",
  "properties": {
    "sinceDate": { "dataType": "date", "displayName": "Since", "required": false },
    "role": { "dataType": "string", "displayName": "Role" }
  },
  "backingDatasetApiName": "works_for_ds",
  "fromPropertyMapping": "emp_id",
  "toPropertyMapping": "company_id",
  "propertyMappings": {
    "sinceDate": "since_date_col",
    "role": "role_col"
  },
  "incrementalField": "updated_at"
}
```

Reading links returns edge attributes under `linkProperties`:

```http
GET /v2/ontologies/{ontologyApiName}/links/works_for
```

```json
{
  "data": [
    {
      "rid": "works_for:e1->c1",
      "linkTypeApiName": "works_for",
      "fromObjectType": "employee",
      "toObjectType": "company",
      "fromPk": "e1",
      "toPk": "c1",
      "linkProperties": {
        "sinceDate": "2021-06-01",
        "role": "Engineer"
      }
    }
  ]
}
```

Incremental APPEND sync for relations:

- When `incrementalField` is set on the `LinkType`, sync filters the backing dataset rows using `dataset[incrementalField] > lastSyncTime`.
- `lastSyncTime` is automatically updated after a successful sync.

Notes:

- When graph-backed reads are enabled (`features.use_graph_reads = true` or `USE_GRAPH_READS=1` override), edge properties may be returned diretamente do grafo; caso contrário, retornos vêm do repositório SQLModel.
- If using COPY mode to ingest relations into Kùzu, ensure that link property columns exist in the REL TABLE schema.

Example (Execute):

```bash
curl -X POST http://localhost:8000/v2/ontologies/default/objects/expense/e1/actions/approve_expense/execute \
  -H 'Content-Type: application/json' \
  -d '{"parameters": {"message": "approved"}}' | jq
```

Example (Start with Idempotency-Key):

```bash
curl -X POST \
  http://localhost:8000/v2/ontologies/default/objects/expense/e1/actions/approve_expense/start \
  -H 'Content-Type: application/json' \
  -H 'Idempotency-Key: 7c1f2d0a-0b2a-4d22-bfb6-6aa78fd8a111' \
  -d '{"parameters": {"message": "approved"}}' | jq
```

Notes:

- **Idempotency-Key**: When provided to the `start` endpoint, repeated requests with the same key will return the same `{workflowId, runId}` instead of starting a duplicate run (best-effort; logged in `ActionExecutionLog`).

Temporal examples:

```bash
# Start (non-blocking)
curl -X POST \
  http://localhost:8000/v2/ontologies/default/objects/expense/e1/actions/approve_expense/start \
  -H 'Content-Type: application/json' \
  -d '{"parameters": {"message": "approved"}}' | jq

# Status
curl "http://localhost:8000/v2/ontologies/default/actions/runs/<workflowId>?runId=<runId>" | jq

# Cancel
curl -X POST \
  "http://localhost:8000/v2/ontologies/default/actions/runs/<workflowId>:cancel?runId=<runId>" | jq
```

## Notes

- Reads are served from graph when KùzuDB is available; otherwise repositories fall back to SQLModel automatically.
- Unified graph mode (`features.use_unified_graph = true`) é obrigatório e habilita listagem por Interface e consultas unificadas sobre o nó `Object` com `properties` em JSON. Overrides que tentam desativar são ignorados.
- Pagination (`limit`, `offset`) is supported on list/traversal endpoints.
- Search, bulk load, and aggregate also work in SQL fallback; graph-backed write-through can be enabled with `features.use_graph_writes = true` (override with `USE_GRAPH_WRITES`).
- Bulk endpoints leverage optimized graph writes (Kùzu `UNWIND` + `MERGE`/`CREATE`) when graph writes are enabled and Kùzu is available; otherwise, they upsert via SQL which is correct but less performant for large batches.

### Derived properties

You can define properties that are computed dynamically on reads via `derivationScript` in `PropertyDefinition`.

- Stored on the metamodel (`PropertyType.derivation_script`). Not persisted on instances.
- Evaluated at read time in the `InstancesService` using a restricted, safe evaluator.
- Expression context exposes `props`, a dict of the object's current properties.
- Allowed constructs: constants, `props['key']` indexing, boolean ops (`and`, `or`, `not`), unary `+`/`-`, arithmetic `+ - * /`, comparisons, inline `a if cond else b`.
- Disallowed: function calls, attribute access, imports, external I/O.

Example:

```json
{
  "displayName": "Person",
  "primaryKey": "id",
  "properties": {
    "id": {"dataType": "string", "displayName": "ID", "required": true},
    "birthYear": {"dataType": "integer", "displayName": "Birth Year"},
    "age": {
      "dataType": "integer",
      "displayName": "Age",
      "derivationScript": "2050 - props['birthYear']"
    }
  }
}
```

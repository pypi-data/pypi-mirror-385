# Interfaces in Ontologia

This document explains the Interfaces concept in the Ontologia metamodel, how to manage them via the API, and how they are used in graph reads.

## Concept

- **Interfaces** are semantic contracts implemented by one or more `ObjectType`s.
- They allow building generic logic (UI, queries) against abstract capabilities (e.g., `[Localizable]`).
- In the relational metamodel, Interfaces are first-class entities (`InterfaceType`) with a many-to-many association to `ObjectType`.
- Interface property contracts are stored as JSON for flexibility (no persistence coupling to `PropertyType`).

## Data Model

- `InterfaceType` (table: `interfacetype`)
- M2M link `objecttype_interfacetype`
- `ObjectType` includes a relationship `interfaces: List[InterfaceType]`

## API

Base path: `/v2/ontologies/{ontologyApiName}`

See also:

- Actions guide: `docs/ACTIONS.md` (includes synchronous `execute` and Temporal `start`/`status`/`cancel` endpoints)

### Create/Update Interface

PUT `/interfaces/{interfaceApiName}`

```json
{
  "displayName": "Localizável",
  "description": "Qualquer coisa com endereço.",
  "properties": {
    "address": { "dataType": "string", "displayName": "Address" }
  }
}
```

Response includes `apiName`, `rid`, `displayName`, `description`, `properties`.

### Get Interface

GET `/interfaces/{interfaceApiName}`

### List Interfaces

GET `/interfaces`

### Delete Interface

DELETE `/interfaces/{interfaceApiName}`

### Declare that an ObjectType implements Interfaces

PUT `/objectTypes/{objectTypeApiName}` with field `implements: ["InterfaceApiName", ...]` alongside normal `properties` and `primaryKey`.

Example:

```json
{
  "displayName": "Cliente",
  "primaryKey": "id",
  "properties": {
    "id": { "dataType": "string", "displayName": "Id", "required": true },
    "name": { "dataType": "string", "displayName": "Name", "required": true },
    "address": { "dataType": "string", "displayName": "Address" }
  },
  "implements": ["Localizavel"]
}
```

`GET /objectTypes/{objectTypeApiName}` returns `implements` in the response for discoverability.

## Graph Reads

- Graph reads are graph-first automatically when KùzuDB is available (no flag required).
- Interfaces are labels on o nó unificado `Object`; listagens por Interface usam uma única consulta com filtro em `labels` (unified graph obrigatório).
- Supported in:
  - `InstancesService.list_objects()` — lists by concrete `ObjectType` or by `Interface`.
  - `InstancesService.search_objects()` — search across implementers when targeting an `Interface`.

## Sync (Kùzu)

- O `OntologySyncService` materializa uma tabela `Object` única com `labels` e `properties` em JSON. Interfaces viram labels adicionais nesse nó.
- Relações (`LinkType`) são persistidas como `REL TABLE` entre `Object`→`Object`.
- Ajustes adicionais de schema/uniones não são mais necessários.

## Notes

- `ObjectTypeDataSource` remains under `ontologia/domain/metamodels/instances/`.
- All existing tests continue to pass; new behavior is covered by service logic behind feature flags.

# Ontologia SDK

This package provides a typed, ergonomic client for interacting with Ontologia object graphs.
It is generated from your ontology definitions via `ontologia-cli generate-sdk`, then extended
with a fluent query DSL, link collection helpers, action namespaces, and typed pagination.

## Quick Start

```bash
# Generate the SDK from local YAML definitions
uv run ontologia-cli --dir example_project/ontology generate-sdk --source local

# Or from a running Ontologia instance
uv run ontologia-cli generate-sdk --host http://127.0.0.1:8000 --ontology default
```

```python
from ontologia_sdk.client import OntologyClient
from ontologia_sdk.ontology import Employee

client = OntologyClient(host="http://127.0.0.1:8000", ontology="default")
alice = Employee.get(client, "e1")
print(alice.name)
```

## Query DSL

Generated objects expose class-level `FieldDescriptor`s, enabling fluent boolean expressions
and ordering. All query helpers retain dict compatibility for incremental adoption.

```python
from ontologia_sdk.ontology import Employee

builder = Employee.search_builder(client)
results = (
    builder
    .where((Employee.dept == "Engineering") & (Employee.age >= 30))
    .order_by(Employee.age.asc())
    .limit(50)
    .all()
)

typed_page = builder.limit(50).all_typed()
for engineer in typed_page.data:
    assert engineer.dept == "Engineering"
```

Additional helpers:

- `Employee.search(...)` / `Employee.search_typed(...)`
- `Employee.iter_search(...)` / `Employee.iter_search_typed(...)`

`QueryBuilder` also supports `iter_pages()` and `iter_pages_typed()` for manual pagination. Typed
variants yield `Page[T]` containers that expose `.data` and `.next_page_token`.

## Links as Collections

Outgoing links are exposed via `LinkDescriptor`, providing a rich collection API while keeping
legacy helpers (`create_<link>`, `list_<link>`, etc.) intact.

```python
companies = alice.works_for.all()

# Create a link with typed properties
alice.works_for.create("c1", {"role": "Engineer"})
edge = alice.works_for.get_typed("c1")
assert edge.role == "Engineer"

# Iterate pages with typed link properties
for page in alice.works_for.iter_pages_typed(page_size=100):
    for edge in page.data:
        print(edge.link_properties.role)
```

## Actions Namespace

Actions are available through both client- and object-level namespaces with optional validation.

```python
# Client-level invocation (parameters validated against cached metadata)
client.actions.promote_employee(object_type="employee", pk="e1", level="L3")

# Object-level invocation
alice.actions.promote(level="L3")

# Inspect available actions
for action in alice.actions.available():
    print(action["apiName"], action.get("parameters", []))
```

## Typed Pagination Helpers

- `LinkDescriptor.all_typed()` / `list_typed()` / `iter_pages_typed()` return `TraversalResult`
  objects with typed link-property payloads.
- `QueryBuilder.all_typed()` and `iter_pages_typed()` build typed `Page[T]` results using the
  generated object classes.

## Testing with MockOntologyClient

Use `ontologia_sdk.testing.MockOntologyClient` for unit tests without hitting a live API. The
mock stores objects, links, and actions entirely in memory and supports the same interfaces as
`OntologyClient`.

```python
from ontologia_sdk.ontology import Employee
from ontologia_sdk.testing import MockOntologyClient

client = MockOntologyClient()
client.upsert_object("employee", "e1", {"name": "Alice", "dept": "Eng"})

alice = Employee.get(client, "e1")
assert alice.name == "Alice"

client.register_action(
    "employee",
    "promote",
    parameters=[{"apiName": "level", "required": True}],
)

alice.actions.promote(level="L3")
```

## Packaging & CI

- `just pkg-build` produces sdist/wheel artifacts via `python -m build`.
- `just pkg-verify` runs `pkg-build` followed by `twine check`.
- The default CI workflow (`.github/workflows/ci.yml`) runs dependency sync, linting, package
  build/verification, dbt tasks, and pytest for every push/PR.

## Next Steps

- Regenerate the SDK whenever the ontology changes to keep descriptors, link proxies, and
  typed helpers in sync.
- Extend generated classes as needed by adding handwritten mixins and using Python imports
  to compose additional behavior.

# Ontology as Code (OaC)

This guide describes how to manage your ontology definitions as source code and apply them to the running API.

## Repository layout

```
example_project/ontology/
├── ontology.yml                # optional root metadata
├── object_types/
│   ├── employee.yml
│   └── company.yml
└── link_types/
    └── works_for.yml
```

- Each YAML file mirrors the corresponding API DTO (`ObjectTypePutRequest`, `LinkTypePutRequest`).
- The `apiName` can be specified in the file or inferred from the filename.

## Example YAML

`link_types/works_for.yml`:

```yaml
apiName: works_for
displayName: Works For
cardinality: MANY_TO_ONE
fromObjectType: employee
toObjectType: company
inverse: { apiName: has_employees, displayName: Has Employees }
properties:
  sinceDate: { dataType: date, displayName: Since }
  role: { dataType: string, displayName: Role }
backingDatasetApiName: works_for_ds
fromPropertyMapping: emp_id
toPropertyMapping: company_id
propertyMappings:
  sinceDate: since_date_col
  role: role_col
incrementalField: updated_at
```

## CLI

The CLI now bundles lifecycle commands alongside the classic ontology management verbs:

- `genesis`: Scaffold a sandbox project (ontology YAML, Docker Compose, local context state).
- `agent`: Open an interactive session with the Architect agent to draft ontology changes.
- `projects`: Inspect or switch the active sandbox tracked in `~/.ontologia/config.json`.
- `validate`, `diff`, `apply`: Validate, preview, and apply ontology deltas (unchanged usage).

- `validate`: Validates local YAML files against the API schemas.
- `diff`: Compares local YAML with server state and prints a migration plan.
- `apply`: Applies the plan by upserting object and link types.

### Installation

The CLI is bundled with the project. Ensure dependencies are installed:

```bash
just setup
```

### Usage

```bash
# Bootstrap a sandbox (creates ontologia/, docker-compose.yml, etc.)
uv run ontologia-cli genesis --name my_sandbox --directory ./sandboxes --start-services --bootstrap

# Chat with the Architect agent from inside the sandbox directory
ontologia agent

# List or switch projects tracked under ~/.ontologia/config.json
ontologia projects list
ontologia projects switch my_sandbox
```

Ontology operations remain available both inside and outside a sandbox:

```bash
# Validate local YAML
uv run ontologia-cli validate --dir example_project/ontology --host http://localhost:8000 --ontology default

# Show migration plan (no changes applied)
uv run ontologia-cli diff --dir example_project/ontology --host http://localhost:8000 --ontology default

# Apply plan (with confirmation)
uv run ontologia-cli apply --dir example_project/ontology --host http://localhost:8000 --ontology default

# Apply without prompt
uv run ontologia-cli apply --dir example_project/ontology --host http://localhost:8000 --ontology default --yes
```

Alternatively, you can run via Python module:

```bash
uv run python -m ontologia_cli.main diff --dir example_project/ontology --host http://localhost:8000 --ontology default
```

### Advanced flags

- `--fail-on-dangerous` (diff): Fail the PR/job when the plan contains dangerous operations (primary key changes, deletes, link endpoint changes).
- `--impact` (diff): Print instance counts for affected `ObjectType`s using `POST /v2/ontologies/{ontology}/analytics/aggregate`.
- `--deps` (diff): Print dependency summary of `LinkType`s that reference changed `ObjectType`s and endpoints for changed `LinkType`s.
- `--allow-destructive` (apply): Allow deletes. Without this flag, `apply` refuses to execute any planned deletions.

Examples:

```bash
# Fail CI on dangerous plans and show dependency/impact summary
uv run ontologia-cli diff --dir example_project/ontology --host http://localhost:8000 --ontology default \
  --fail-on-dangerous --deps --impact

# Apply including deletions (use with care)
uv run ontologia-cli apply --dir example_project/ontology --host http://localhost:8000 --ontology default \
  --yes --allow-destructive
```

### Justfile helpers

```bash
just oac-validate
just oac-diff -- --deps --impact --fail-on-dangerous
just oac-apply -- --yes
```

### Dev tip

In development environments where an installed package could shadow the local code, prefer invoking the CLI as a module:

```bash
uv run python -m ontologia_cli.main diff --dir example_project/ontology --host http://localhost:8000 --ontology default
```

## CI integration (example)

- On pull requests, run `ontologia-cli validate` and `ontologia-cli diff`.
- Fail the PR if the plan contains dangerous operations using `--fail-on-dangerous`.

## Notes

- Link properties are fully supported. See `docs/API_REFERENCE.md` → Link properties.
- Incremental APPEND fields for relations are supported via `incrementalField`.

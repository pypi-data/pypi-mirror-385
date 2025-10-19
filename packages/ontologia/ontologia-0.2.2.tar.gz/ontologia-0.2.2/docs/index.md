# Ontologia Documentation

Ontologia is an ontology-as-code platform that unifies schema management, code generation, and
runtime graph evaluation. This site curates the most important references for contributors and
operators.

## How to Use This Site

1. **Start here:** follow the [Getting Started](getting-started.md) guide to set up your development
   environment, generate the SDK, and run the first smoke tests.
2. **Explore the platform:** dive into the [Architecture Overview](platform/architecture.md), API
   reference, sync service documentation, and the ontology-as-code (OaC) workflow.
3. **Go deeper:** the Cookbook (in progress) and archive sections contain historical reports and
   architectural decision records (ADRs) for advanced research.

## Quick Links

| Area | Description | Link |
| --- | --- | --- |
| Getting Started | Development setup, CLI usage, smoke checks | [Guide](getting-started.md) |
| Architecture | Components, data flow, deployment topology | [Overview](platform/architecture.md) |
| REST API | Endpoint catalogue with request/response examples | [API Reference](API_REFERENCE.md) |
| Sync Service | dbt integration, DuckDB pipeline, runner usage | [Sync Docs](SYNC.md) |
| Actions | Dynamic action discovery, execution, and DSL rules | [Actions Guide](ACTIONS.md) |
| Ontology as Code | YAML conventions, CLI generation, CI workflows | [OaC Guide](OAC_GUIDE.md) |

> **Tip:** The documentation is generated with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/).
> Run `mkdocs serve` from the repository root for a live-reloading development server.

## Building the Site Locally

```bash
uvx mkdocs serve  # or: python -m mkdocs serve
```

This command watches for changes to Markdown files under `docs/` and reloads the local preview at
`http://127.0.0.1:8000`.

## Contributing to Documentation

* Keep new content under the appropriate section (Platform, Guides, Cookbook, or Archive).
* Prefer diagrams written in [Mermaid](https://mermaid.js.org/) so they remain version-controlled
  and editable.
* Link directly to source files or code snippets when documenting a feature.
* Major structural changes should be accompanied by updates to `mkdocs.yml` and a note in the pull
  request description.

For historical reports and decisions, see the [Archive](archive/reports.md) and
[Decision Records](archive/adrs.md) sections.

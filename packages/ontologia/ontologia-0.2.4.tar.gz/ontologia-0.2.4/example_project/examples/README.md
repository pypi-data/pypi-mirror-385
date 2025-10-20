# Examples

This folder contains runnable examples and snippets.

- `example_unified_linktype.py` — Define and interact with a unified LinkType.

## Quickstarts

- `library_quickstart.py` — use services directly without HTTP
  ```bash
  uv run python example_project/examples/library_quickstart.py
  ```

- `api_quickstart.py` — call the HTTP API via FastAPI TestClient
  ```bash
  uv run python example_project/examples/api_quickstart.py
  ```

- `mcp_tooling_quickstart.py` — manage the ontology via the MCP surface using a service token
  ```bash
  uv run python example_project/examples/mcp_tooling_quickstart.py
  ```

- `issue_agent_service_token.py` — mint a JWT for `agent-architect-01` (prints JSON with the token)
  ```bash
  uv run python example_project/examples/issue_agent_service_token.py
  ```

- `agent_apply_plan.py` — apply a sample ObjectType plan inside a sandbox created with `ontologia-cli genesis`
  ```bash
  uv run python example_project/examples/agent_apply_plan.py
  ```

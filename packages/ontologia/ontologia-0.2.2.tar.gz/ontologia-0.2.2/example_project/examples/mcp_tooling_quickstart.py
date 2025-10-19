"""End-to-end example using the MCP server with a service token."""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any

try:
    from fastmcp.client import Client as MCPClient
except ImportError as exc:  # pragma: no cover - optional dependency
    raise SystemExit(
        "fastmcp is required for this example. Install it via `uv sync --group agents`."
    ) from exc

from api.core.auth import USERS_DB, create_service_account_token


def _service_token() -> str:
    token = os.getenv("ONTOLOGIA_AGENT_TOKEN")
    if token:
        return token

    record = USERS_DB.get("agent-architect-01")
    if record is None:
        raise SystemExit("agent-architect-01 user missing. Add it to USERS_DB first.")

    print("Generating ephemeral service token for agent-architect-01...")
    return create_service_account_token(
        subject=record.username,
        roles=list(record.roles),
        tenants=dict(record.tenants),
    )


async def _call_tool(client: MCPClient, name: str, arguments: dict[str, Any]) -> Any:
    result = await client.call_tool(name, arguments)
    if result.is_error:
        raise RuntimeError(f"Tool {name} failed: {result.error}")
    return (
        result.data
        or result.structured_content
        or [getattr(block, "text", None) for block in result.content]
    )


async def main() -> None:
    api_url = os.getenv("ONTOLOGIA_API_URL", "http://127.0.0.1:8000")
    mcp_url = os.getenv("ONTOLOGIA_MCP_URL", f"{api_url.rstrip('/')}/mcp")
    token = _service_token()

    async with MCPClient(mcp_url, auth=f"Bearer {token}") as client:
        tools = await client.list_tools()
        print("Available tools:")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")

        print("\nCreating product ObjectType via MCP...")
        product_payload = {
            "api_name": "product",
            "schema": {
                "displayName": "Product",
                "description": "Catalog entry managed by agents",
                "primaryKey": "sku",
                "properties": {
                    "sku": {
                        "dataType": "string",
                        "displayName": "SKU",
                        "required": True,
                    },
                    "name": {
                        "dataType": "string",
                        "displayName": "Name",
                        "required": True,
                    },
                    "price": {
                        "dataType": "double",
                        "displayName": "Price",
                    },
                    "category": {
                        "dataType": "string",
                        "displayName": "Category",
                    },
                },
                "implements": [],
            },
        }
        product = await _call_tool(client, "upsert_object_type", product_payload)
        print("ObjectType created:")
        print(json.dumps(product, indent=2))

        category_payload = {
            "api_name": "category",
            "schema": {
                "displayName": "Category",
                "description": "Product category",
                "primaryKey": "id",
                "properties": {
                    "id": {
                        "dataType": "string",
                        "displayName": "ID",
                        "required": True,
                    },
                    "name": {
                        "dataType": "string",
                        "displayName": "Name",
                        "required": True,
                    },
                },
                "implements": [],
            },
        }
        await _call_tool(client, "upsert_object_type", category_payload)

        print("\nCreating product-category link type via MCP...")
        link_payload = {
            "api_name": "product_belongs_to_category",
            "schema": {
                "displayName": "Product belongs to Category",
                "cardinality": "MANY_TO_ONE",
                "fromObjectType": "product",
                "toObjectType": "category",
                "inverse": {
                    "apiName": "category_has_product",
                    "displayName": "Category has Product",
                },
                "description": "Connect products to their category",
            },
        }
        link_type = await _call_tool(client, "upsert_link_type", link_payload)
        print(json.dumps(link_type, indent=2))

        print("\nSeeding products dataset via MCP...")
        dataset_payload = {
            "api_name": "products_dataset",
            "schema": {
                "displayName": "Products Dataset",
                "sourceType": "IN_MEMORY",
                "sourceIdentifier": "products.csv",
                "schemaDefinition": {
                    "columns": [
                        {"name": "sku", "type": "string"},
                        {"name": "name", "type": "string"},
                        {"name": "price", "type": "double"},
                    ]
                },
            },
        }
        dataset = await _call_tool(client, "upsert_dataset", dataset_payload)
        print("Dataset registered:")
        print(json.dumps(dataset, indent=2))

        print("\nListing datasets to confirm registration...")
        datasets = await _call_tool(client, "list_datasets", {})
        print(json.dumps(datasets, indent=2))

        print("\nUpserting category and product instances...")
        await _call_tool(
            client,
            "upsert_object",
            {
                "object_type_api_name": "category",
                "pk_value": "electronics",
                "body": {"properties": {"id": "electronics", "name": "Electronics"}},
            },
        )
        product_instance = await _call_tool(
            client,
            "upsert_object",
            {
                "object_type_api_name": "product",
                "pk_value": "sku-001",
                "body": {
                    "properties": {
                        "sku": "sku-001",
                        "name": "Noise Cancelling Headphones",
                        "price": 349.0,
                        "category": "electronics",
                    }
                },
            },
        )
        print(json.dumps(product_instance, indent=2))

        print("\nListing products via MCP...")
        products = await _call_tool(
            client,
            "list_objects",
            {"object_type_api_name": "product", "limit": 10},
        )
        print(json.dumps(products, indent=2))

        print("\nAggregating products by category...")
        aggregates = await _call_tool(
            client,
            "aggregate_objects",
            {
                "body": {
                    "objectTypeApiName": "product",
                    "groupBy": ["category"],
                    "metrics": [{"func": "count"}],
                }
            },
        )
        print(json.dumps(aggregates, indent=2))

        print("\nLinking product to its category...")
        link_instance = await _call_tool(
            client,
            "create_link",
            {
                "link_type_api_name": "product_belongs_to_category",
                "body": {"fromPk": "sku-001", "toPk": "electronics"},
            },
        )
        print(json.dumps(link_instance, indent=2))

        print("\nListing links for product_belongs_to_category...")
        links = await _call_tool(
            client,
            "list_links",
            {"link_type_api_name": "product_belongs_to_category"},
        )
        print(json.dumps(links, indent=2))

        print("\nSearching for premium products (price > 300)...")
        search = await _call_tool(
            client,
            "search_objects",
            {
                "object_type_api_name": "product",
                "body": {
                    "where": [{"property": "price", "op": "gt", "value": 300}],
                    "limit": 5,
                    "offset": 0,
                    "orderBy": [],
                    "traverse": [],
                },
            },
        )
        print(json.dumps(search, indent=2))

        print("\nChecking available actions (expected empty unless configured)...")
        actions = await _call_tool(
            client,
            "list_actions",
            {"object_type_api_name": "product", "pk_value": "sku-001"},
        )
        print(json.dumps(actions, indent=2))


if __name__ == "__main__":  # pragma: no cover - script entrypoint
    asyncio.run(main())

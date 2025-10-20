import json
from typing import Any, Dict

import httpx
import pytest

from stateset import Stateset
from stateset.resources import GenericResource, Inventory, Orders, Returns, Warranties, Workflows


@pytest.mark.asyncio
async def test_request_uses_underlying_transport() -> None:
    captured: Dict[str, Any] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        captured["url"] = str(request.url)
        captured["headers"] = dict(request.headers)
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    async_client = httpx.AsyncClient(transport=transport, base_url="https://example.com")
    client = Stateset(
        api_key="test-key",
        base_url="https://example.com",
        client=async_client,
    )

    try:
        result = await client.request("GET", "returns", params={"limit": 5})
        assert result == {"ok": True}
        assert captured["method"] == "GET"
        assert captured["url"] == "https://example.com/returns?limit=5"
        # Authorization header should be attached automatically (case-insensitive).
        auth_header = captured["headers"].get("Authorization") or captured["headers"].get("authorization")
        assert auth_header == "Bearer test-key"
    finally:
        await client.aclose()
        await async_client.aclose()


@pytest.mark.asyncio
async def test_request_accepts_data_positional_argument() -> None:
    body: Dict[str, Any] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        body.update(json.loads(request.content))
        return httpx.Response(201, json={"id": "return_123"})

    transport = httpx.MockTransport(handler)
    async_client = httpx.AsyncClient(transport=transport, base_url="https://example.com")
    client = Stateset(api_key="key", base_url="https://example.com", client=async_client)

    try:
        result = await client.request("POST", "returns", {"name": "sample"})
        assert result == {"id": "return_123"}
        assert body == {"name": "sample"}
    finally:
        await client.aclose()
        await async_client.aclose()


@pytest.mark.asyncio
async def test_resource_registration() -> None:
    client = Stateset(api_key="key")
    try:
        assert isinstance(client.orders, Orders)
        assert isinstance(client.returns, Returns)
        assert isinstance(client.inventory, Inventory)
        assert isinstance(client.workflows, Workflows)
        assert isinstance(client.warranties, Warranties)
        assert client.warranty is client.warranties
        # Generic fallbacks
        assert isinstance(client.activities, GenericResource)
        assert isinstance(client.agents, GenericResource)
        assert isinstance(client.channels, GenericResource)
        assert isinstance(client.purchase_orders, GenericResource)
        assert isinstance(client.workorders, GenericResource)
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_sync_context_manager_not_supported() -> None:
    client = Stateset(api_key="key")
    with pytest.raises(TypeError):
        with client:
            pass
    await client.aclose()


@pytest.mark.asyncio
async def test_get_resource_lookup() -> None:
    client = Stateset(api_key="key")
    try:
        assert client.get_resource("orders") is client.orders
        with pytest.raises(AttributeError):
            client.get_resource("unknown")
    finally:
        await client.aclose()

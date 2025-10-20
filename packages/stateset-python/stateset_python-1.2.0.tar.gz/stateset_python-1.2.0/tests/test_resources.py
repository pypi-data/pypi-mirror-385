from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Tuple
from urllib.parse import parse_qs

import httpx
import pytest

from stateset import Stateset


def _make_client(
    handler: httpx.MockTransport,
) -> Tuple[Stateset, httpx.AsyncClient]:
    async_client = httpx.AsyncClient(transport=handler, base_url="https://example.com")
    client = Stateset(api_key="test-key", base_url="https://example.com", client=async_client)
    return client, async_client


def _capture_handler(
    calls: List[Dict[str, Any]],
    responses: Dict[Tuple[str, str], Dict[str, Any]] | None = None,
) -> httpx.MockTransport:
    async def handler(request: httpx.Request) -> httpx.Response:
        content = request.content.decode() if request.content else None
        try:
            payload = json.loads(content) if content else None
        except json.JSONDecodeError:
            payload = content
        query = request.url.query.decode() if isinstance(request.url.query, bytes) else str(
            request.url.query
        )

        record = {
            "method": request.method,
            "path": request.url.path,
            "query": query,
            "payload": payload,
        }
        calls.append(record)

        if request.method == "DELETE":
            return httpx.Response(204)

        key = (request.method, request.url.path)
        body = responses.get(key, {}) if responses else {}
        if not body:
            body = {
                "method": request.method,
                "path": request.url.path,
                "query": query,
                "payload": payload,
            }

        return httpx.Response(200, json=body)

    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_collection_resource_crud_operations() -> None:
    calls: List[Dict[str, Any]] = []
    client, async_client = _make_client(_capture_handler(calls))

    try:
        list_result = await client.inventory.list(status="active")
        list_query = parse_qs(list_result["query"])
        assert list_result["path"] == "/inventory"
        assert list_query["status"] == ["active"]

        item = await client.inventory.get("item-1")
        assert item["path"] == "/inventory/item-1"

        created = await client.inventory.create({"sku": "A-1"})
        assert created["payload"] == {"sku": "A-1"}

        updated = await client.inventory.update("item-1", {"quantity": 3})
        assert updated["path"] == "/inventory/item-1"
        assert updated["payload"] == {"quantity": 3}

        await client.inventory.delete("item-2")
        assert calls[-1]["method"] == "DELETE"
        assert calls[-1]["path"] == "/inventory/item-2"

        search_result = await client.inventory.search(query="widget", page=2)
        search_query = parse_qs(search_result["query"])
        assert search_result["path"] == "/inventory/search"
        assert search_query["query"] == ["widget"]
        assert search_query["page"] == ["2"]
    finally:
        await client.aclose()
        await async_client.aclose()


@pytest.mark.asyncio
async def test_orders_and_returns_helpers() -> None:
    calls: List[Dict[str, Any]] = []
    client, async_client = _make_client(_capture_handler(calls))

    try:
        await client.orders.cancel("order_123", reason="customer request")
        cancel_call = calls[-1]
        assert cancel_call["path"] == "/orders/order_123/cancel"
        assert cancel_call["payload"] == {"reason": "customer request"}

        shipped_at = datetime(2023, 5, 1, 12, 30, 45)
        await client.orders.mark_as_shipped(
            "order_123",
            tracking_number="1Z123",
            carrier="UPS",
            shipped_at=shipped_at,
        )
        ship_call = calls[-1]
        assert ship_call["path"] == "/orders/order_123/ship"
        assert ship_call["payload"] == {
            "tracking_number": "1Z123",
            "carrier": "UPS",
            "shipped_at": shipped_at.isoformat(),
        }

        await client.returns.approve("ret_1", notes="all good")
        approve_call = calls[-1]
        assert approve_call["path"] == "/returns/ret_1/approve"
        assert approve_call["payload"] == {"notes": "all good"}

        await client.returns.cancel("ret_2", reason="duplicate")
        cancel_return_call = calls[-1]
        assert cancel_return_call["path"] == "/returns/ret_2/cancel"
        assert cancel_return_call["payload"] == {"reason": "duplicate"}

        await client.returns.mark_received("ret_3", received_by="Agent")
        received_call = calls[-1]
        assert received_call["path"] == "/returns/ret_3/receive"
        assert received_call["payload"] == {"received_by": "Agent"}

        await client.inventory.adjust(
            "item-9",
            quantity=5,
            reason="stocktake",
            metadata={"location": "A1"},
        )
        adjust_call = calls[-1]
        assert adjust_call["path"] == "/inventory/item-9/adjust"
        assert adjust_call["payload"] == {
            "quantity": 5,
            "reason": "stocktake",
            "metadata": {"location": "A1"},
        }

        await client.warranties.change_status("war_1", "approved")
        warranty_call = calls[-1]
        assert warranty_call["path"] == "/warranties/war_1/status"
        assert warranty_call["payload"] == {"status": "approved"}
    finally:
        await client.aclose()
        await async_client.aclose()


@pytest.mark.asyncio
async def test_workflows_helper_shapes_response() -> None:
    calls: List[Dict[str, Any]] = []
    responses = {
        ("GET", "/workflows"): {"workflows": [{"id": "wf_1"}]},
        ("GET", "/workflows/wf_2"): {"workflow": {"id": "wf_2"}},
        ("POST", "/workflows"): {"workflow": {"id": "wf_created"}},
        ("PUT", "/workflows/wf_2"): {"workflow": {"id": "wf_updated"}},
    }
    handler = _capture_handler(calls, responses=responses)
    client, async_client = _make_client(handler)

    try:
        listing = await client.workflows.list(status="active", tag="urgent")
        list_query = parse_qs(calls[-1]["query"])
        assert listing == [{"id": "wf_1"}]
        assert list_query["status"] == ["active"]
        assert list_query["tag"] == ["urgent"]

        workflow = await client.workflows.get("wf_2")
        assert workflow == {"id": "wf_2"}

        created = await client.workflows.create({"name": "New workflow"})
        assert created == {"id": "wf_created"}

        updated = await client.workflows.update("wf_2", {"name": "Updated"})
        assert updated == {"id": "wf_updated"}

        await client.workflows.delete("wf_2")
        assert calls[-1]["method"] == "DELETE"
        assert calls[-1]["path"] == "/workflows/wf_2"
    finally:
        await client.aclose()
        await async_client.aclose()

import json
from typing import Any, Dict, List

import httpx
import pytest

from stateset import Stateset
from stateset.client import RetryConfig
from stateset.errors import StatesetAPIError, StatesetConnectionError, StatesetRateLimitError
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
        client._register_generic_resources({"orders": "orders"})
        assert client.get_resource("orders") is client.orders
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


@pytest.mark.asyncio
async def test_request_raises_rate_limit_error_without_retry_after() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(429)

    transport = httpx.MockTransport(handler)
    async_client = httpx.AsyncClient(transport=transport, base_url="https://example.com")
    client = Stateset(api_key="key", base_url="https://example.com", client=async_client)

    try:
        with pytest.raises(StatesetRateLimitError):
            await client.request("GET", "orders")
    finally:
        await client.aclose()
        await async_client.aclose()


@pytest.mark.asyncio
async def test_request_returns_none_for_no_content_response() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(204)

    transport = httpx.MockTransport(handler)
    async_client = httpx.AsyncClient(transport=transport, base_url="https://example.com")
    client = Stateset(api_key="key", base_url="https://example.com", client=async_client)

    try:
        result = await client.returns.delete("return_1")
        assert result is None
    finally:
        await client.aclose()
        await async_client.aclose()


@pytest.mark.asyncio
async def test_request_handles_text_response() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="plain text", headers={"Content-Type": "text/plain"})

    transport = httpx.MockTransport(handler)
    async_client = httpx.AsyncClient(transport=transport, base_url="https://example.com")
    client = Stateset(api_key="key", base_url="https://example.com", client=async_client)

    try:
        result = await client.request("GET", "notes")
        assert result == "plain text"
    finally:
        await client.aclose()
        await async_client.aclose()


@pytest.mark.asyncio
async def test_request_returns_none_for_empty_body() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200)

    transport = httpx.MockTransport(handler)
    async_client = httpx.AsyncClient(transport=transport, base_url="https://example.com")
    client = Stateset(api_key="key", base_url="https://example.com", client=async_client)

    try:
        result = await client.request("GET", "empty")
        assert result is None
    finally:
        await client.aclose()
        await async_client.aclose()


@pytest.mark.asyncio
async def test_request_allows_raw_content() -> None:
    captured: Dict[str, Any] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["content"] = request.content
        captured["headers"] = dict(request.headers)
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    async_client = httpx.AsyncClient(transport=transport, base_url="https://example.com")
    client = Stateset(api_key="key", base_url="https://example.com", client=async_client)

    try:
        payload = b"\x00\x01binary"
        await client.request(
            "POST",
            "uploads",
            content=payload,
            headers={"Content-Type": "application/octet-stream"},
        )
        assert captured["content"] == payload
        header_value = captured["headers"].get("Content-Type") or captured["headers"].get(
            "content-type"
        )
        assert header_value == "application/octet-stream"
    finally:
        await client.aclose()
        await async_client.aclose()


@pytest.mark.asyncio
async def test_request_preserves_form_data_sequences() -> None:
    captured: Dict[str, Any] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        body = await request.aread()
        captured["content"] = body.decode()
        captured["headers"] = dict(request.headers)
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    async_client = httpx.AsyncClient(transport=transport, base_url="https://example.com")
    client = Stateset(api_key="key", base_url="https://example.com", client=async_client)

    try:
        await client.request(
            "POST",
            "forms",
            data=[("field", "value"), ("field", "second")],
        )
        assert captured["content"] in {"field=value&field=second", "field=second&field=value"}
        content_type = captured["headers"].get("Content-Type") or captured["headers"].get(
            "content-type"
        )
        assert content_type and content_type.startswith("application/x-www-form-urlencoded")
    finally:
        await client.aclose()
        await async_client.aclose()


@pytest.mark.asyncio
async def test_request_merges_additional_headers() -> None:
    captured: Dict[str, str] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured.update(dict(request.headers))
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    async_client = httpx.AsyncClient(transport=transport, base_url="https://example.com")
    client = Stateset(
        api_key="key",
        base_url="https://example.com",
        client=async_client,
        additional_headers={"X-Test": "value"},
    )

    try:
        await client.request("GET", "orders")
        test_header = captured.get("X-Test") or captured.get("x-test")
        auth_header = captured.get("Authorization") or captured.get("authorization")
        assert test_header == "value"
        assert auth_header == "Bearer key"
    finally:
        await client.aclose()
        await async_client.aclose()


@pytest.mark.asyncio
async def test_request_allows_per_request_headers() -> None:
    captured: Dict[str, str] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured.update(dict(request.headers))
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    async_client = httpx.AsyncClient(transport=transport, base_url="https://example.com")
    client = Stateset(api_key="key", base_url="https://example.com", client=async_client)

    try:
        await client.request("GET", "orders", headers={"X-Request": "value"})
        header_value = captured.get("X-Request") or captured.get("x-request")
        assert header_value == "value"
    finally:
        await client.aclose()
        await async_client.aclose()


@pytest.mark.asyncio
async def test_request_retries_timeout_and_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    sleep_calls: List[float] = []

    async def fake_sleep(delay: float) -> None:
        sleep_calls.append(delay)

    monkeypatch.setattr("stateset.client.asyncio.sleep", fake_sleep)

    async def handler(_: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("boom")

    transport = httpx.MockTransport(handler)
    async_client = httpx.AsyncClient(transport=transport, base_url="https://example.com")
    client = Stateset(
        api_key="key",
        base_url="https://example.com",
        client=async_client,
        retry_config=RetryConfig(max_attempts=2, backoff_factor=0.5),
    )

    try:
        with pytest.raises(StatesetConnectionError):
            await client.request("GET", "orders")
        assert sleep_calls  # ensures retry attempted
    finally:
        await client.aclose()
        await async_client.aclose()


@pytest.mark.asyncio
async def test_request_retries_on_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    sleep_calls: List[float] = []

    async def fake_sleep(delay: float) -> None:
        sleep_calls.append(delay)

    monkeypatch.setattr("stateset.client.asyncio.sleep", fake_sleep)

    async def handler(_: httpx.Request) -> httpx.Response:
        raise httpx.HTTPError("boom")

    transport = httpx.MockTransport(handler)
    async_client = httpx.AsyncClient(transport=transport, base_url="https://example.com")
    client = Stateset(
        api_key="key",
        base_url="https://example.com",
        client=async_client,
        retry_config=RetryConfig(max_attempts=2, backoff_factor=0.5),
    )

    try:
        with pytest.raises(StatesetConnectionError):
            await client.request("GET", "orders")
        assert sleep_calls
    finally:
        await client.aclose()
        await async_client.aclose()


@pytest.mark.asyncio
async def test_request_retries_on_rate_limit_with_retry_after(monkeypatch: pytest.MonkeyPatch) -> None:
    sleep_calls: List[float] = []

    async def fake_sleep(delay: float) -> None:
        sleep_calls.append(delay)

    monkeypatch.setattr("stateset.client.asyncio.sleep", fake_sleep)

    attempts = 0

    async def handler(_: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(429, headers={"Retry-After": "1.5"})
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    async_client = httpx.AsyncClient(transport=transport, base_url="https://example.com")
    client = Stateset(api_key="key", base_url="https://example.com", client=async_client)

    try:
        result = await client.request("GET", "orders")
        assert result == {"ok": True}
        assert sleep_calls == [1.5]
        assert attempts == 2
    finally:
        await client.aclose()
        await async_client.aclose()


@pytest.mark.asyncio
async def test_request_retries_rate_limit_without_retry_after(monkeypatch: pytest.MonkeyPatch) -> None:
    sleep_calls: List[float] = []

    async def fake_sleep(delay: float) -> None:
        sleep_calls.append(delay)

    monkeypatch.setattr("stateset.client.asyncio.sleep", fake_sleep)

    attempts = 0

    async def handler(_: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            return httpx.Response(429)
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    async_client = httpx.AsyncClient(transport=transport, base_url="https://example.com")
    client = Stateset(api_key="key", base_url="https://example.com", client=async_client)

    try:
        result = await client.request("GET", "orders")
        assert result == {"ok": True}
        assert attempts == 3
        assert pytest.approx(sleep_calls[0]) == 0.25
        assert pytest.approx(sleep_calls[1]) == 0.5
    finally:
        await client.aclose()
        await async_client.aclose()

@pytest.mark.asyncio
async def test_request_retries_on_server_error_with_backoff(monkeypatch: pytest.MonkeyPatch) -> None:
    sleep_calls: List[float] = []

    async def fake_sleep(delay: float) -> None:
        sleep_calls.append(delay)

    monkeypatch.setattr("stateset.client.asyncio.sleep", fake_sleep)

    attempts = 0

    async def handler(_: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(503)
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    async_client = httpx.AsyncClient(transport=transport, base_url="https://example.com")
    client = Stateset(api_key="key", base_url="https://example.com", client=async_client)

    try:
        result = await client.request("GET", "orders")
        assert result == {"ok": True}
        expected_backoff = 0.5 * (2 ** -1)
        assert pytest.approx(sleep_calls[0]) == expected_backoff
    finally:
        await client.aclose()
        await async_client.aclose()


@pytest.mark.asyncio
async def test_request_accepts_expected_status_codes() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(409, json={"status": "conflict"})

    transport = httpx.MockTransport(handler)
    async_client = httpx.AsyncClient(transport=transport, base_url="https://example.com")
    client = Stateset(api_key="key", base_url="https://example.com", client=async_client)

    try:
        result = await client.request("GET", "orders", expected=[409])
        assert result == {"status": "conflict"}
    finally:
        await client.aclose()
        await async_client.aclose()


@pytest.mark.asyncio
async def test_request_raises_for_non_retryable_status() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(418, json={"error": "teapot"})

    transport = httpx.MockTransport(handler)
    async_client = httpx.AsyncClient(transport=transport, base_url="https://example.com")
    client = Stateset(api_key="key", base_url="https://example.com", client=async_client)

    try:
        with pytest.raises(StatesetAPIError):
            await client.request("GET", "brew")
    finally:
        await client.aclose()
        await async_client.aclose()


@pytest.mark.asyncio
async def test_async_context_manager_closes_client() -> None:
    async with Stateset(api_key="key", base_url="https://example.com") as client:
        assert client.get_resource("orders") is client.orders
    assert client._requestor._client.is_closed


@pytest.mark.asyncio
async def test_rate_limit_retry_after_fallback_backoff(monkeypatch: pytest.MonkeyPatch) -> None:
    sleep_calls: List[float] = []

    async def fake_sleep(delay: float) -> None:
        sleep_calls.append(delay)

    monkeypatch.setattr("stateset.client.asyncio.sleep", fake_sleep)

    attempts = 0

    async def handler(_: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(429, headers={"Retry-After": "later"})
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    async_client = httpx.AsyncClient(transport=transport, base_url="https://example.com")
    client = Stateset(api_key="key", base_url="https://example.com", client=async_client)

    try:
        result = await client.request("GET", "orders")
        assert result == {"ok": True}
        assert pytest.approx(sleep_calls[0]) == 0.5 * (2**-1)
    finally:
        await client.aclose()
        await async_client.aclose()


@pytest.mark.asyncio
async def test_workflows_get_requires_workflow_key() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": {}})

    transport = httpx.MockTransport(handler)
    async_client = httpx.AsyncClient(transport=transport, base_url="https://example.com")
    client = Stateset(api_key="key", base_url="https://example.com", client=async_client)

    try:
        with pytest.raises(StatesetAPIError):
            await client.workflows.get("wf_123")
    finally:
        await client.aclose()
        await async_client.aclose()


@pytest.mark.asyncio
async def test_workflows_list_requires_array() -> None:
    async def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"workflows": {}})

    transport = httpx.MockTransport(handler)
    async_client = httpx.AsyncClient(transport=transport, base_url="https://example.com")
    client = Stateset(api_key="key", base_url="https://example.com", client=async_client)

    try:
        with pytest.raises(StatesetAPIError):
            await client.workflows.list()
    finally:
        await client.aclose()
        await async_client.aclose()

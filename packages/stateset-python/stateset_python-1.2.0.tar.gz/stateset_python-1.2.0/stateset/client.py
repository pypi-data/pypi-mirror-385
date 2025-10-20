from __future__ import annotations

import asyncio
import math
from dataclasses import dataclass
from typing import Any, Dict, Mapping, MutableMapping, Optional, Sequence

import httpx

from ._version import __version__
from .errors import StatesetConnectionError, raise_for_status_code
from .resources import GenericResource, Inventory, Orders, Returns, Warranties, Workflows

DEFAULT_BASE_URL = "https://api.stateset.com"
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 0.5


@dataclass(frozen=True)
class RetryConfig:
    """Basic retry configuration for the Stateset HTTP client."""

    max_attempts: int = DEFAULT_MAX_RETRIES
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR
    retryable_statuses: Sequence[int] = (408, 409, 425, 429, 500, 502, 503, 504)


class _AsyncRequestor:
    """Thin wrapper around ``httpx.AsyncClient`` with retry and error handling."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: float,
        retry_config: RetryConfig,
        client: Optional[httpx.AsyncClient] = None,
        additional_headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        self._owns_client = client is None
        default_headers: Dict[str, str] = {
            "Authorization": f"Bearer {api_key}",
            "User-Agent": f"stateset-python/{__version__}",
            "Accept": "application/json",
        }
        if additional_headers:
            default_headers.update(additional_headers)

        if client is None:
            self._client = httpx.AsyncClient(
                base_url=base_url.rstrip("/"),
                timeout=timeout,
                headers=default_headers,
            )
        else:
            self._client = client
            for header, value in default_headers.items():
                self._client.headers.setdefault(header, value)
        self._retry_config = retry_config
        self._default_headers = dict(self._client.headers)

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def request(
        self,
        method: str,
        path: str,
        data: Optional[Any] = None,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json: Optional[Any] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected: Optional[Sequence[int]] = None,
        content: Optional[bytes] = None,
        files: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        expected_statuses = set(expected) if expected else set(range(200, 300))
        merged_headers = self._merge_headers(headers)
        attempts = 0

        while True:
            try:
                response = await self._client.request(
                    method=method.upper(),
                    url=path,
                    params=params,
                    json=json,
                    data=data,
                    content=content,
                    files=files,
                    headers=merged_headers,
                )
            except httpx.TimeoutException as exc:
                attempts += 1
                await self._handle_network_error(exc, attempts)
                continue
            except httpx.HTTPError as exc:
                attempts += 1
                await self._handle_network_error(exc, attempts)
                continue

            if response.status_code in expected_statuses:
                if response.status_code == 204:
                    return None
                return await self._deserialize_response(response)

            if self._should_retry(response.status_code, attempts):
                await self._sleep_for_retry(response, attempts)
                attempts += 1
                continue

            content = await response.aread()
            raise_for_status_code(
                response.status_code,
                content,
                expected_codes=expected_statuses or None,
            )

    async def _handle_network_error(
        self,
        exc: httpx.HTTPError,
        attempts: int,
    ) -> None:
        if attempts >= self._retry_config.max_attempts:
            raise StatesetConnectionError(
                message="Failed to reach the Stateset API",
                detail=str(exc),
            ) from exc
        await asyncio.sleep(self._compute_backoff(attempts))

    def _should_retry(self, status_code: int, attempts: int) -> bool:
        return (
            attempts < self._retry_config.max_attempts
            and status_code in self._retry_config.retryable_statuses
        )

    async def _sleep_for_retry(self, response: httpx.Response, attempts: int) -> None:
        if response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                try:
                    delay = float(retry_after)
                except ValueError:
                    delay = self._compute_backoff(attempts)
                await asyncio.sleep(delay)
                return
        await asyncio.sleep(self._compute_backoff(attempts))

    def _compute_backoff(self, attempts: int) -> float:
        exponential = self._retry_config.backoff_factor * math.pow(2, attempts - 1)
        return min(exponential, 10.0)

    async def _deserialize_response(self, response: httpx.Response) -> Any:
        await response.aread()
        if not response.content:
            return None
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return response.json()
        return response.text

    def _merge_headers(
        self,
        headers: Optional[Mapping[str, str]],
    ) -> MutableMapping[str, str]:
        merged = dict(self._default_headers)
        if headers:
            merged.update(headers)
        return merged


class Stateset:
    """High-level asynchronous client for interacting with the Stateset API."""

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        retry_config: Optional[RetryConfig] = None,
        client: Optional[httpx.AsyncClient] = None,
        additional_headers: Optional[Mapping[str, str]] = None,
    ) -> None:
        self._requestor = _AsyncRequestor(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            retry_config=retry_config or RetryConfig(),
            client=client,
            additional_headers=additional_headers,
        )

        # Core resource accessors
        self.orders = Orders(self)
        self.returns = Returns(self)
        self.inventory = Inventory(self)
        self.workflows = Workflows(self)
        self.warranties = Warranties(self)
        self.warranty = self.warranties

        self._resource_registry: Dict[str, Any] = {
            "orders": self.orders,
            "returns": self.returns,
            "inventory": self.inventory,
            "workflows": self.workflows,
            "warranties": self.warranties,
            "warranty": self.warranty,
        }

        self._register_generic_resources(
            {
                "activities": "activities",
                "agents": "agents",
                "channels": "channels",
                "messages": "messages",
                "shipments": "shipments",
                "purchase_orders": "purchase-orders",
                "rules": "rules",
                "workorders": "work-orders",
            }
        )

    async def request(
        self,
        method: str,
        path: str,
        data: Optional[Any] = None,
        *,
        params: Optional[Mapping[str, Any]] = None,
        json: Optional[Any] = None,
        headers: Optional[Mapping[str, str]] = None,
        expected: Optional[Sequence[int]] = None,
        content: Optional[bytes] = None,
        files: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        """
        Execute a raw API request against the Stateset service.

        Args:
            method: HTTP verb, e.g. ``"GET"`` or ``"POST"``.
            path: Relative URL path such as ``"returns"``.
            params: Optional query string arguments.
            json: JSON-serialisable request body for write operations.
            headers: Additional headers to merge with the defaults.
            expected: Optional list of acceptable status codes.
            content: Raw byte content to send without JSON encoding.
            files: Optional multipart/form-data mapping passed to ``httpx``.
        """

        def looks_like_form_sequence(value: Any) -> bool:
            if not isinstance(value, (list, tuple)):
                return False
            return all(
                isinstance(item, (list, tuple))
                and len(item) == 2
                and isinstance(item[0], str)
                for item in value
            )

        send_json = json
        send_data = data
        send_content = content
        header_values: Dict[str, str] = dict(headers) if headers else {}
        form_encoded = False

        if send_json is None and send_content is None and files is None:
            if isinstance(send_data, dict):
                send_json = send_data
                send_data = None
            elif isinstance(send_data, (list, tuple)) and not looks_like_form_sequence(send_data):
                send_json = send_data
                send_data = None
            elif isinstance(send_data, (list, tuple)) and looks_like_form_sequence(send_data):
                from urllib.parse import urlencode

                encoded = urlencode(send_data, doseq=True).encode("utf-8")
                send_content = encoded
                send_data = None
                form_encoded = True

        if form_encoded and not any(key.lower() == "content-type" for key in header_values):
            header_values["Content-Type"] = "application/x-www-form-urlencoded"

        return await self._requestor.request(
            method=method,
            path=path,
            params=params,
            json=send_json,
            data=send_data,
            content=send_content,
            files=files,
            headers=header_values,
            expected=expected,
        )

    async def aclose(self) -> None:
        """Close the underlying HTTP client."""
        await self._requestor.aclose()

    def get_resource(self, name: str) -> Any:
        """Fetch a registered resource by name."""
        try:
            return self._resource_registry[name]
        except KeyError as exc:
            raise AttributeError(f"No resource named '{name}' is registered") from exc

    def _register_generic_resources(self, mapping: Mapping[str, str]) -> None:
        for attribute_name, resource_path in mapping.items():
            if attribute_name in self.__dict__:
                continue
            resource = GenericResource(self, resource_path)
            setattr(self, attribute_name, resource)
            self._resource_registry[attribute_name] = resource

    async def __aenter__(self) -> "Stateset":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    # Synchronous context management is intentionally not supported to
    # avoid confusing behaviour around implicit event loops.
    def __enter__(self) -> "Stateset":  # pragma: no cover - defensive
        raise TypeError(
            "Stateset client only supports asynchronous usage. "
            "Use 'async with Stateset(...)' instead."
        )

    def __exit__(self, *_: object) -> None:  # pragma: no cover - defensive
        raise TypeError(
            "Stateset client only supports asynchronous usage. "
            "Use 'async with Stateset(...)' instead."
        )

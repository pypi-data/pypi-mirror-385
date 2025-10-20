from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Sequence


class CollectionResource:
    """Generic helper that provides CRUD-style helpers for API collections."""

    def __init__(self, client: Any, resource_path: str) -> None:
        self._client = client
        self._resource_path = resource_path.strip("/")

    async def list(self, **params: Any) -> Any:
        return await self._client.request("GET", self._resource_path, params=params or None)

    async def get(self, resource_id: str) -> Any:
        return await self._client.request("GET", f"{self._resource_path}/{resource_id}")

    async def create(self, payload: Mapping[str, Any]) -> Any:
        return await self._client.request("POST", self._resource_path, dict(payload))

    async def update(self, resource_id: str, payload: Mapping[str, Any]) -> Any:
        return await self._client.request("PUT", f"{self._resource_path}/{resource_id}", dict(payload))

    async def delete(self, resource_id: str) -> None:
        await self._client.request("DELETE", f"{self._resource_path}/{resource_id}")

    async def search(self, *, query: Optional[str] = None, **params: Any) -> Any:
        if query:
            params.setdefault("query", query)
        return await self._client.request("GET", f"{self._resource_path}/search", params=params or None)

from __future__ import annotations

from typing import Any, Dict, Optional

from .base import CollectionResource


class Returns(CollectionResource):
    """Convenience helpers for the ``/returns`` API."""

    def __init__(self, client: Any) -> None:
        super().__init__(client, "returns")

    async def approve(self, return_id: str, *, notes: Optional[str] = None) -> Any:
        payload: Dict[str, Any] = {}
        if notes:
            payload["notes"] = notes
        return await self._client.request("POST", f"returns/{return_id}/approve", payload or None)

    async def cancel(self, return_id: str, *, reason: Optional[str] = None) -> Any:
        payload: Dict[str, Any] = {}
        if reason:
            payload["reason"] = reason
        return await self._client.request("POST", f"returns/{return_id}/cancel", payload or None)

    async def mark_received(self, return_id: str, *, received_by: Optional[str] = None) -> Any:
        payload: Dict[str, Any] = {}
        if received_by:
            payload["received_by"] = received_by
        return await self._client.request("POST", f"returns/{return_id}/receive", payload or None)

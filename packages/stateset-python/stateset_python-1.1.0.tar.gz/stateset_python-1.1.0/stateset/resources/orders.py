from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from .base import CollectionResource


class Orders(CollectionResource):
    """Helper for interacting with order resources."""

    def __init__(self, client: Any) -> None:
        super().__init__(client, "orders")

    async def cancel(self, order_id: str, *, reason: Optional[str] = None) -> Any:
        payload: Dict[str, Any] = {}
        if reason:
            payload["reason"] = reason
        return await self._client.request("POST", f"orders/{order_id}/cancel", payload or None)

    async def mark_as_shipped(
        self,
        order_id: str,
        *,
        tracking_number: str,
        carrier: str,
        shipped_at: Optional[datetime] = None,
    ) -> Any:
        payload: Dict[str, Any] = {
            "tracking_number": tracking_number,
            "carrier": carrier,
        }
        if shipped_at:
            payload["shipped_at"] = shipped_at.isoformat()
        return await self._client.request("POST", f"orders/{order_id}/ship", payload)

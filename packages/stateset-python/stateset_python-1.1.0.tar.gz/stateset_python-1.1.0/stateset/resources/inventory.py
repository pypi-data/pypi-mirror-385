from __future__ import annotations

from typing import Any, Dict, Optional

from .base import CollectionResource


class Inventory(CollectionResource):
    def __init__(self, client: Any) -> None:
        super().__init__(client, "inventory")

    async def adjust(
        self,
        item_id: str,
        *,
        quantity: int,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        payload: Dict[str, Any] = {
            "quantity": quantity,
        }
        if reason:
            payload["reason"] = reason
        if metadata:
            payload["metadata"] = metadata
        return await self._client.request("POST", f"inventory/{item_id}/adjust", payload)

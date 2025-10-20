from __future__ import annotations

from typing import Any, Dict

from .base import CollectionResource


class Warranties(CollectionResource):
    def __init__(self, client: Any) -> None:
        super().__init__(client, "warranties")

    async def change_status(self, warranty_id: str, status: str) -> Any:
        return await self._client.request(
            "POST", f"warranties/{warranty_id}/status", {"status": status}
        )

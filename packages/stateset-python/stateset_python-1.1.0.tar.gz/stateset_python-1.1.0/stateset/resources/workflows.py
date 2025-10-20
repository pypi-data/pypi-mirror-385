from __future__ import annotations

from typing import Any, Dict, List, Optional


class Workflows:
    """Lightweight helper around the Stateset workflow API."""

    def __init__(self, stateset_client: Any) -> None:
        self.stateset = stateset_client

    async def list(
        self,
        *,
        status: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, str] = {}
        if status:
            params["status"] = status
        if tag:
            params["tag"] = tag
        response = await self.stateset.request("GET", "workflows", params=params or None)
        return response.get("workflows", [])

    async def get(self, workflow_id: str) -> Dict[str, Any]:
        response = await self.stateset.request("GET", f"workflows/{workflow_id}")
        return response["workflow"]

    async def create(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.stateset.request("POST", "workflows", workflow_data)
        return response["workflow"]

    async def update(self, workflow_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.stateset.request("PUT", f"workflows/{workflow_id}", workflow_data)
        return response["workflow"]

    async def delete(self, workflow_id: str) -> None:
        await self.stateset.request("DELETE", f"workflows/{workflow_id}")

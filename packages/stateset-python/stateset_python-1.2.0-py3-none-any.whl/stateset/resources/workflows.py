from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional

from ..errors import StatesetAPIError


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
        payload = self._ensure_mapping(response, operation="List workflows")
        workflows = payload.get("workflows", [])
        if not isinstance(workflows, list):
            raise StatesetAPIError(
                message="List workflows response did not include a 'workflows' array",
                raw_response=payload,
            )
        return workflows

    async def get(self, workflow_id: str) -> Dict[str, Any]:
        response = await self.stateset.request("GET", f"workflows/{workflow_id}")
        return self._extract_workflow(response, operation="Get workflow")

    async def create(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.stateset.request("POST", "workflows", workflow_data)
        return self._extract_workflow(response, operation="Create workflow")

    async def update(self, workflow_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.stateset.request("PUT", f"workflows/{workflow_id}", workflow_data)
        return self._extract_workflow(response, operation="Update workflow")

    async def delete(self, workflow_id: str) -> None:
        await self.stateset.request("DELETE", f"workflows/{workflow_id}")

    def _ensure_mapping(self, payload: Any, *, operation: str) -> Mapping[str, Any]:
        if not isinstance(payload, Mapping):
            raise StatesetAPIError(
                message=f"{operation} response payload is not a JSON object",
                raw_response={"payload": payload},
            )
        return payload

    def _extract_workflow(self, payload: Any, *, operation: str) -> Dict[str, Any]:
        mapping = self._ensure_mapping(payload, operation=operation)
        workflow = mapping.get("workflow")
        if not isinstance(workflow, Mapping):
            raise StatesetAPIError(
                message=f"{operation} response did not include a 'workflow' object",
                raw_response=mapping,
            )
        return dict(workflow)

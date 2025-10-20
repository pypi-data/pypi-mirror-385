from __future__ import annotations

from .base import CollectionResource


class GenericResource(CollectionResource):
    """Collection resource with no additional behaviour."""

    def __init__(self, client, resource_path: str) -> None:
        super().__init__(client, resource_path)

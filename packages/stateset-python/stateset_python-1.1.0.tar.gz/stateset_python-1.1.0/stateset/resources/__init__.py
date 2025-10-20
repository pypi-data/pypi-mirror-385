"""Lightweight resource wrappers provided by the Stateset SDK."""

from .base import CollectionResource
from .generic import GenericResource
from .inventory import Inventory
from .orders import Orders
from .returns import Returns
from .warranties import Warranties
from .workflows import Workflows

__all__ = [
    "CollectionResource",
    "GenericResource",
    "Inventory",
    "Orders",
    "Returns",
    "Warranties",
    "Workflows",
]

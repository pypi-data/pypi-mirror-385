"""
Stateset Python SDK
===================

This package provides an asynchronous client for the Stateset API together
with a small set of typed helper utilities.
"""

from ._version import __api_version__, __version__
from .client import Stateset
from .errors import (
    StatesetAPIError,
    StatesetAuthenticationError,
    StatesetConnectionError,
    StatesetError,
    StatesetInvalidRequestError,
    StatesetNotFoundError,
    StatesetPermissionError,
    StatesetRateLimitError,
)
from .types import (
    File,
    FileUploadError,
    Metadata,
    OrderStatus,
    PaginationParams,
    PaginatedList,
    ReturnStatus,
    StatesetID,
    StatesetObject,
    Timestamp,
    UNSET,
    WarrantyStatus,
)

__all__ = [
    "Stateset",
    "StatesetError",
    "StatesetInvalidRequestError",
    "StatesetAPIError",
    "StatesetAuthenticationError",
    "StatesetPermissionError",
    "StatesetNotFoundError",
    "StatesetConnectionError",
    "StatesetRateLimitError",
    "StatesetID",
    "Timestamp",
    "Metadata",
    "StatesetObject",
    "OrderStatus",
    "ReturnStatus",
    "WarrantyStatus",
    "PaginationParams",
    "PaginatedList",
    "File",
    "FileUploadError",
    "UNSET",
    "__version__",
    "__api_version__",
]

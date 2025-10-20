"""
Contains type definitions and data structures for the Stateset SDK.

This module provides shared types, data classes, and utilities for handling
various Stateset API operations including responses, pagination, and file operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import (
    Any,
    BinaryIO,
    Dict,
    Generic,
    List,
    Literal,
    Mapping,
    MutableMapping,
    Optional,
    Protocol,
    TextIO,
    Tuple,
    TypeVar,
    Union,
)
from http import HTTPStatus
from pathlib import Path
import mimetypes
import json

from attrs import define, field


class UnsetType:
    """Represents an unset value, distinct from None."""
    
    def __bool__(self) -> Literal[False]:
        return False
    
    def __repr__(self) -> str:
        return "UNSET"
    
    def __copy__(self) -> UnsetType:
        return self
    
    def __deepcopy__(self, _: Any) -> UnsetType:
        return self


UNSET: UnsetType = UnsetType()

# Type variable for generic response types
T = TypeVar("T")

# Type alias for values that can be unset
OptionalUnset = Union[T, UnsetType]  # type: ignore

# Common Stateset types
StatesetID = str
Timestamp = Union[int, datetime]
Metadata = Dict[str, str]

class OrderStatus(str, Enum):
    """Possible states for an order."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"
    FAILED = "failed"

class ReturnStatus(str, Enum):
    """Possible states for a return."""
    REQUESTED = "requested"
    APPROVED = "approved"
    RECEIVED = "received"
    INSPECTED = "inspected"
    COMPLETED = "completed"
    REJECTED = "rejected"

class WarrantyStatus(str, Enum):
    """Possible states for a warranty claim."""
    FILED = "filed"
    PROCESSING = "processing"
    APPROVED = "approved"
    DENIED = "denied"
    COMPLETED = "completed"

@define
class StatesetObject:
    """Base class for Stateset API objects."""
    
    id: StatesetID
    object: str
    created: Timestamp
    updated: Optional[Timestamp] = None
    metadata: Metadata = field(factory=dict)
    
    def __attrs_post_init__(self) -> None:
        """Convert timestamp strings to datetime objects."""
        if isinstance(self.created, (int, str)):
            self.created = datetime.fromtimestamp(int(self.created))
        if isinstance(self.updated, (int, str)):
            self.updated = datetime.fromtimestamp(int(self.updated))

@define
class PaginationParams:
    """Parameters for paginated requests."""
    
    page: int = field(default=1)
    per_page: int = field(default=20)
    sort_by: Optional[str] = None
    sort_order: Optional[Literal["asc", "desc"]] = None

@define
class PaginatedList(Generic[T]):
    """A paginated list of items from the Stateset API."""
    
    data: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool

    @property
    def next_page(self) -> Optional[int]:
        """Get the next page number if available."""
        return self.page + 1 if self.has_next else None

    @property
    def prev_page(self) -> Optional[int]:
        """Get the previous page number if available."""
        return self.page - 1 if self.has_prev else None

class FileUploadError(Exception):
    """Raised when there's an error preparing a file for upload."""
    pass

@define
class File:
    """Contains information for file uploads to Stateset API.
    
    Attributes:
        payload: The file content to upload
        file_name: Optional name for the file
        mime_type: Optional MIME type. If not provided, will attempt to guess
        purpose: Optional purpose of the file (e.g., "warranty_evidence", "return_label")
        encoding: Optional file encoding for text files
        chunk_size: Size of chunks when reading large files
    """
    
    payload: Union[BinaryIO, TextIO, Path, bytes, str]
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    purpose: Optional[str] = None
    encoding: str = field(default="utf-8")
    chunk_size: int = field(default=8192)
    
    def __attrs_post_init__(self) -> None:
        """Process the payload and set defaults after initialization."""
        if isinstance(self.payload, Path):
            self.file_name = self.file_name or self.payload.name
            if not self.mime_type:
                guessed_type, _ = mimetypes.guess_type(str(self.payload))
                self.mime_type = guessed_type or "application/octet-stream"
    
    @classmethod
    def from_path(
        cls, 
        path: Union[str, Path], 
        purpose: Optional[str] = None,
        mime_type: Optional[str] = None,
        encoding: Optional[str] = None
    ) -> File:
        """Create a File instance from a file path."""
        path_obj = Path(path)
        if not path_obj.exists():
            raise FileUploadError(f"File not found: {path}")
        
        return cls(
            payload=path_obj,
            file_name=path_obj.name,
            mime_type=mime_type,
            purpose=purpose,
            encoding=encoding or "utf-8"
        )

    def to_upload_data(self) -> Tuple[Optional[str], BinaryIO, Optional[str]]:
        """Prepare the file for upload to Stateset API."""
        try:
            if isinstance(self.payload, (str, bytes)):
                import io
                if isinstance(self.payload, str):
                    bio = io.BytesIO(self.payload.encode(self.encoding))
                else:
                    bio = io.BytesIO(self.payload)
                return self.file_name, bio, self.mime_type
            
            elif isinstance(self.payload, Path):
                return self.file_name, self.payload.open('rb'), self.mime_type
            
            elif hasattr(self.payload, 'read'):
                if hasattr(self.payload, 'mode') and 'b' not in getattr(self.payload, 'mode'):
                    raise FileUploadError("File must be opened in binary mode")
                return self.file_name, self.payload, self.mime_type
            
            else:
                raise FileUploadError(f"Unsupported payload type: {type(self.payload)}")
            
        except Exception as e:
            raise FileUploadError(f"Failed to prepare file for upload: {str(e)}")


@dataclass
class Response(Generic[T]):
    """Represents an HTTP response from the Stateset API."""

    status_code: HTTPStatus
    content: bytes
    headers: MutableMapping[str, str]
    parsed: Optional[T]

__all__ = [
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
    "Response",
    "UNSET",
    "UnsetType",
    "OptionalUnset",
]

from __future__ import annotations
from datetime import datetime
from pathlib import Path

import pytest

from stateset.types import (
    File,
    FileUploadError,
    PaginatedList,
    PaginationParams,
    StatesetObject,
    UNSET,
)


def test_stateset_object_normalises_timestamps() -> None:
    obj = StatesetObject(
        id="obj_123",
        object="test",
        created=str(int(datetime.now().timestamp())),
        updated=int(datetime.now().timestamp()),
    )
    assert isinstance(obj.created, datetime)
    assert isinstance(obj.updated, datetime)


def test_file_to_upload_data_from_bytes() -> None:
    file = File(payload=b"payload", file_name="payload.bin", mime_type="application/octet-stream")
    name, stream, mime = file.to_upload_data()
    assert name == "payload.bin"
    assert stream.read() == b"payload"
    assert mime == "application/octet-stream"


def test_file_to_upload_data_from_str_uses_encoding() -> None:
    file = File(payload="hello", file_name="hello.txt", encoding="utf-16")
    name, stream, mime = file.to_upload_data()
    assert name == "hello.txt"
    assert stream.read() == "hello".encode("utf-16")
    assert mime is None


def test_file_from_path(tmp_path: Path) -> None:
    target = tmp_path / "example.txt"
    target.write_text("content", encoding="utf-8")
    file = File.from_path(target, purpose="test")
    name, stream, mime = file.to_upload_data()
    try:
        assert name == "example.txt"
        assert stream.read() == b"content"
        assert mime == "text/plain"
    finally:
        stream.close()


def test_file_from_path_missing_raises(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.txt"
    with pytest.raises(FileUploadError):
        File.from_path(missing_path)


def test_paginated_list_navigation() -> None:
    plist = PaginatedList(
        data=[1, 2],
        total=4,
        page=1,
        per_page=2,
        total_pages=2,
        has_next=True,
        has_prev=False,
    )
    assert plist.next_page == 2
    assert plist.prev_page is None


def test_pagination_params_defaults() -> None:
    params = PaginationParams()
    assert params.page == 1
    assert params.per_page == 20
    assert params.sort_by is None
    assert params.sort_order is None


def test_unset_evaluates_false_and_repr() -> None:
    assert not UNSET
    assert repr(UNSET) == "UNSET"

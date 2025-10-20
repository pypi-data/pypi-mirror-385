from __future__ import annotations

import pytest

from stateset.errors import (
    StatesetAPIError,
    StatesetAuthenticationError,
    StatesetConnectionError,
    StatesetError,
    StatesetInvalidRequestError,
    StatesetNotFoundError,
    StatesetPermissionError,
    StatesetRateLimitError,
    raise_for_status_code,
)


def test_raise_for_status_code_maps_to_specific_errors() -> None:
    with pytest.raises(StatesetNotFoundError) as exc:
        raise_for_status_code(
            404,
            b'{"type": "not_found_error", "message": "missing", "path": "/orders"}',
        )
    assert exc.value.path == "/orders"
    assert exc.value.status_code == 404


def test_raise_for_status_code_handles_invalid_payloads() -> None:
    with pytest.raises(StatesetAPIError) as exc:
        raise_for_status_code(500, b"<html>fail</html>")
    assert exc.value.status_code == 500


def test_stateset_error_from_response_handles_json() -> None:
    error = StatesetError.from_response(
        b'{"type": "invalid_request_error", "message": "bad input"}',
        status_code=422,
    )
    assert isinstance(error, StatesetInvalidRequestError)
    assert error.args[0] == "bad input"


def test_stateset_error_from_response_unknown_type() -> None:
    error = StatesetError.from_response(
        b'{"type": "custom_error", "message": "oops"}',
        status_code=500,
    )
    assert isinstance(error, StatesetError)
    assert error.type == "custom_error"


def test_error_subclasses_initialise() -> None:
    auth = StatesetAuthenticationError()
    perm = StatesetPermissionError()
    conn = StatesetConnectionError(detail="timeout")
    rate = StatesetRateLimitError(retry_after=5)
    missing = StatesetNotFoundError(resource_type="order", resource_id="ord_1")

    assert "[authentication_error]" in str(auth)
    assert perm.type == "permission_error"
    assert conn.detail == "timeout"
    assert rate.retry_after == 5
    assert "Retry after" in str(rate)
    assert "order not found: ord_1" in str(missing)
    assert missing.resource_id == "ord_1"


def test_raise_for_status_code_respects_expected_codes() -> None:
    raise_for_status_code(409, b"", expected_codes={409})


def test_raise_for_status_code_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*args, **kwargs):
        raise ValueError("explode")

    monkeypatch.setattr("stateset.errors.StatesetError.from_response", boom)
    with pytest.raises(StatesetAPIError) as exc:
        raise_for_status_code(499, b"", expected_codes=None)
    assert "HTTP 499" in str(exc.value)


def test_raise_for_status_code_success_returns() -> None:
    raise_for_status_code(204, b"")

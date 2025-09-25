"""Tests for PowerPath Test Assignments endpoints.

This module contains tests for the PowerPath Test Assignments API wrappers.
They verify that methods:
- call the correct endpoint paths
- use the correct HTTP method
- pass through params/data unchanged

Note: These are thin wrapper tests modeled after existing tests (components/courses),
but remain unit-style to avoid making assumptions about server data shape.
"""

from typing import Any, Dict
import types
import logging
from timeback_client.api.powerpath import PowerPathAPI

# Configure logging similar to other tests
logging.basicConfig(level=logging.INFO)

# Use a base URL constant for consistency with other test modules
STAGING_URL = "https://staging.alpha-1edtech.com"


def _mock_make_request(expected: Dict[str, Any]):
    """Return a stub _make_request that asserts inputs and returns a sentinel."""
    def _inner(*, endpoint: str, method: str = "GET", data: Dict[str, Any] | None = None, params: Dict[str, Any] | None = None):
        assert endpoint == expected.get("endpoint")
        assert method == expected.get("method")
        if "data" in expected:
            assert data == expected.get("data")
        if "params" in expected:
            assert params == expected.get("params")
        return {"ok": True, "endpoint": endpoint, "method": method, "data": data, "params": params}
    return _inner


def test_create_test_assignment_calls_post_with_body():
    api = PowerPathAPI(STAGING_URL)
    expected = {
        "endpoint": "/test-assignments",
        "method": "POST",
        "data": {"a": 1, "b": 2},
    }
    api._make_request = types.MethodType(lambda self, **kwargs: _mock_make_request(expected)(**kwargs), api)  # type: ignore
    resp = api.create_test_assignment({"a": 1, "b": 2})
    assert resp["ok"] is True


def test_update_test_assignment_calls_put_with_body():
    api = PowerPathAPI(STAGING_URL)
    expected = {
        "endpoint": "/test-assignments/abc123",
        "method": "PUT",
        "data": {"name": "New Name"},
    }
    api._make_request = types.MethodType(lambda self, **kwargs: _mock_make_request(expected)(**kwargs), api)  # type: ignore
    resp = api.update_test_assignment("abc123", {"name": "New Name"})
    assert resp["ok"] is True


def test_get_test_assignment_calls_get():
    api = PowerPathAPI(STAGING_URL)
    expected = {
        "endpoint": "/test-assignments/abc123",
        "method": "GET",
    }
    api._make_request = types.MethodType(lambda self, **kwargs: _mock_make_request(expected)(**kwargs), api)  # type: ignore
    resp = api.get_test_assignment("abc123")
    assert resp["ok"] is True


def test_delete_test_assignment_calls_delete():
    api = PowerPathAPI(STAGING_URL)
    expected = {
        "endpoint": "/test-assignments/abc123",
        "method": "DELETE",
    }
    api._make_request = types.MethodType(lambda self, **kwargs: _mock_make_request(expected)(**kwargs), api)  # type: ignore
    resp = api.delete_test_assignment("abc123")
    assert resp["ok"] is True


def test_list_test_assignments_calls_get_with_query_params():
    api = PowerPathAPI(STAGING_URL)
    expected = {
        "endpoint": "/test-assignments",
        "method": "GET",
        "params": {"student": "stu1", "status": "active", "subject": "Math", "grade": "5", "page": 2, "limit": 10},
    }
    api._make_request = types.MethodType(lambda self, **kwargs: _mock_make_request(expected)(**kwargs), api)  # type: ignore
    resp = api.list_test_assignments(student="stu1", status="active", subject="Math", grade="5", page=2, limit=10)
    assert resp["ok"] is True


def test_list_test_assignments_admin_calls_get_with_optional_query_params():
    api = PowerPathAPI(STAGING_URL)
    expected = {
        "endpoint": "/test-assignments/admin",
        "method": "GET",
        "params": {"student": "stu1", "status": "completed"},
    }
    api._make_request = types.MethodType(lambda self, **kwargs: _mock_make_request(expected)(**kwargs), api)  # type: ignore
    resp = api.list_test_assignments_admin(student="stu1", status="completed")
    assert resp["ok"] is True


if __name__ == "__main__":
    # Allow running this test module directly like others
    print("Running PowerPath Test Assignments thin wrapper tests...")
    test_create_test_assignment_calls_post_with_body()
    test_update_test_assignment_calls_put_with_body()
    test_get_test_assignment_calls_get()
    test_delete_test_assignment_calls_delete()
    test_list_test_assignments_calls_get_with_query_params()
    test_list_test_assignments_admin_calls_get_with_optional_query_params()



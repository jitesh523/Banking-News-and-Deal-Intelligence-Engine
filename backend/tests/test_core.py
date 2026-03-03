"""
Unit tests for core modules: cache, responses, auth, and error_handler.
"""

import time
import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException


# ─── Cache Tests ────────────────────────────────────────────

class TestTTLCache:
    """Tests for app.core.cache.TTLCache."""

    def setup_method(self):
        from app.core.cache import TTLCache
        self.cache = TTLCache(default_ttl=2, max_size=5)

    def test_set_and_get(self):
        self.cache.set("key1", "value1")
        assert self.cache.get("key1") == "value1"

    def test_get_missing_key(self):
        assert self.cache.get("nonexistent") is None

    def test_expiration(self):
        self.cache.set("key2", "value2", ttl=0)
        time.sleep(0.01)
        assert self.cache.get("key2") is None

    def test_invalidate(self):
        self.cache.set("key3", "value3")
        assert self.cache.invalidate("key3") is True
        assert self.cache.get("key3") is None
        assert self.cache.invalidate("key3") is False

    def test_clear(self):
        self.cache.set("a", 1)
        self.cache.set("b", 2)
        count = self.cache.clear()
        assert count == 2
        assert self.cache.size == 0

    def test_max_size_eviction(self):
        for i in range(6):
            self.cache.set(f"k{i}", i)
        # Should never exceed max_size
        assert self.cache.size <= 5

    def test_stats(self):
        self.cache.set("x", 1)
        stats = self.cache.stats()
        assert stats["entries"] == 1
        assert stats["max_size"] == 5
        assert stats["default_ttl_seconds"] == 2


# ─── Responses Tests ────────────────────────────────────────

class TestPaginationMeta:
    """Tests for app.core.responses.PaginationMeta."""

    def test_single_page(self):
        from app.core.responses import PaginationMeta
        meta = PaginationMeta.create(page=1, per_page=20, total=5)
        assert meta.total_pages == 1
        assert meta.has_next is False
        assert meta.has_prev is False

    def test_multiple_pages(self):
        from app.core.responses import PaginationMeta
        meta = PaginationMeta.create(page=2, per_page=10, total=25)
        assert meta.total_pages == 3
        assert meta.has_next is True
        assert meta.has_prev is True

    def test_last_page(self):
        from app.core.responses import PaginationMeta
        meta = PaginationMeta.create(page=3, per_page=10, total=25)
        assert meta.has_next is False
        assert meta.has_prev is True

    def test_empty_results(self):
        from app.core.responses import PaginationMeta
        meta = PaginationMeta.create(page=1, per_page=20, total=0)
        assert meta.total_pages == 1
        assert meta.has_next is False


class TestAPIResponse:
    """Tests for app.core.responses.APIResponse."""

    def test_ok_response(self):
        from app.core.responses import APIResponse
        resp = APIResponse.ok(data={"key": "value"})
        assert resp.success is True
        assert resp.data == {"key": "value"}
        assert resp.timestamp is not None

    def test_error_response(self):
        from app.core.responses import APIResponse
        resp = APIResponse.error("Something went wrong")
        assert resp.success is False
        assert resp.message == "Something went wrong"


class TestPaginatedResponse:
    """Tests for app.core.responses.PaginatedResponse."""

    def test_create(self):
        from app.core.responses import PaginatedResponse
        resp = PaginatedResponse.create(
            items=[1, 2, 3],
            total=10,
            page=1,
            per_page=3,
        )
        assert resp.success is True
        assert len(resp.data) == 3
        assert resp.pagination.total == 10
        assert resp.pagination.total_pages == 4
        assert resp.pagination.has_next is True


# ─── Auth Tests ─────────────────────────────────────────────

class TestAuth:
    """Tests for app.core.auth module."""

    @pytest.mark.asyncio
    async def test_dev_mode_allows_all(self):
        """When no API keys configured, all requests pass."""
        from app.core.auth import require_api_key, _valid_keys
        # Clear valid keys to simulate dev mode
        original = _valid_keys.copy()
        _valid_keys.clear()
        try:
            result = await require_api_key(api_key=None)
            assert result == "dev-mode"
        finally:
            _valid_keys.update(original)

    @pytest.mark.asyncio
    async def test_missing_key_raises_401(self):
        """Missing key returns 401 when keys are configured."""
        from app.core import auth
        original = auth._valid_keys.copy()
        auth._valid_keys.clear()
        auth._valid_keys.add("test-key-123")
        try:
            with pytest.raises(HTTPException) as exc_info:
                await auth.require_api_key(api_key=None)
            assert exc_info.value.status_code == 401
        finally:
            auth._valid_keys.clear()
            auth._valid_keys.update(original)

    @pytest.mark.asyncio
    async def test_invalid_key_raises_403(self):
        """Invalid key returns 403."""
        from app.core import auth
        original = auth._valid_keys.copy()
        auth._valid_keys.clear()
        auth._valid_keys.add("test-key-123")
        try:
            with pytest.raises(HTTPException) as exc_info:
                await auth.require_api_key(api_key="wrong-key")
            assert exc_info.value.status_code == 403
        finally:
            auth._valid_keys.clear()
            auth._valid_keys.update(original)

    @pytest.mark.asyncio
    async def test_valid_key_passes(self):
        """Valid key returns the key."""
        from app.core import auth
        original = auth._valid_keys.copy()
        auth._valid_keys.clear()
        auth._valid_keys.add("test-key-123")
        try:
            result = await auth.require_api_key(api_key="test-key-123")
            assert result == "test-key-123"
        finally:
            auth._valid_keys.clear()
            auth._valid_keys.update(original)


# ─── Error Handler Tests ────────────────────────────────────

class TestErrorHandler:
    """Tests for app.core.error_handler."""

    @pytest.mark.asyncio
    async def test_handler_returns_json(self):
        from app.core.error_handler import global_exception_handler
        from unittest.mock import MagicMock

        mock_request = MagicMock()
        mock_request.method = "GET"
        mock_request.url.path = "/test"

        response = await global_exception_handler(mock_request, ValueError("test error"))
        assert response.status_code == 500
        assert b'"success": false' in response.body

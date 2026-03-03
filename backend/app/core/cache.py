"""
Simple in-memory TTL cache for expensive analytics calls.

Usage:
    from app.core.cache import cache

    @router.get("/expensive")
    async def expensive_endpoint():
        cached = cache.get("my_key")
        if cached is not None:
            return cached
        result = compute_expensive()
        cache.set("my_key", result, ttl=300)
        return result
"""

import time
from typing import Any, Optional
from loguru import logger


class TTLCache:
    """
    Thread-safe in-memory cache with per-key TTL expiration.

    Designed for caching analytics results that are expensive to compute
    but don't change frequently.
    """

    def __init__(self, default_ttl: int = 300, max_size: int = 500):
        """
        Args:
            default_ttl: Default time-to-live in seconds.
            max_size: Maximum number of entries before eviction.
        """
        self._store: dict[str, tuple[Any, float]] = {}
        self.default_ttl = default_ttl
        self.max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        """Return cached value or None if missing / expired."""
        entry = self._store.get(key)
        if entry is None:
            return None

        value, expires_at = entry
        if time.time() > expires_at:
            del self._store[key]
            return None

        return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Store a value with a TTL (seconds)."""
        if len(self._store) >= self.max_size:
            self._evict_expired()
            # If still full, remove oldest entry
            if len(self._store) >= self.max_size:
                oldest_key = next(iter(self._store))
                del self._store[oldest_key]

        expires_at = time.time() + (ttl if ttl is not None else self.default_ttl)
        self._store[key] = (value, expires_at)

    def invalidate(self, key: str) -> bool:
        """Remove a specific key. Returns True if it existed."""
        return self._store.pop(key, None) is not None

    def clear(self) -> int:
        """Clear all entries. Returns the number of entries removed."""
        count = len(self._store)
        self._store.clear()
        logger.debug(f"Cache cleared: {count} entries removed")
        return count

    def _evict_expired(self) -> int:
        """Remove all expired entries. Returns count removed."""
        now = time.time()
        expired = [k for k, (_, exp) in self._store.items() if now > exp]
        for k in expired:
            del self._store[k]
        return len(expired)

    @property
    def size(self) -> int:
        """Current number of entries (including possibly expired)."""
        return len(self._store)

    def stats(self) -> dict:
        """Return cache statistics."""
        self._evict_expired()
        return {
            "entries": len(self._store),
            "max_size": self.max_size,
            "default_ttl_seconds": self.default_ttl,
        }


# Singleton cache instance
cache = TTLCache(default_ttl=300, max_size=500)

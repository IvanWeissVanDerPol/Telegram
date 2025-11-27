"""
The Phantom Bot - Caching Service
In-memory caching with TTL support.
"""
import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class CacheEntry:
    """A single cache entry with expiration."""
    value: Any
    expires_at: datetime
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_expired(self) -> bool:
        """Check if the entry has expired."""
        return datetime.now(timezone.utc) >= self.expires_at


class CacheService:
    """
    Simple in-memory cache with TTL support.

    Usage:
        cache = CacheService()

        # Set a value with 60 second TTL
        await cache.set("key", value, ttl_seconds=60)

        # Get a value
        value = await cache.get("key")

        # Get or compute
        value = await cache.get_or_set("key", compute_fn, ttl_seconds=60)
    """

    def __init__(self):
        self._cache: dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start(self, cleanup_interval: int = 60) -> None:
        """Start the background cleanup task."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(
                self._cleanup_loop(cleanup_interval)
            )
            logger.info("Cache cleanup task started")

    async def stop(self) -> None:
        """Stop the background cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
            logger.info("Cache cleanup task stopped")

    async def _cleanup_loop(self, interval: int) -> None:
        """Background task to clean up expired entries."""
        while True:
            await asyncio.sleep(interval)
            await self.cleanup()

    async def cleanup(self) -> int:
        """Remove all expired entries. Returns count of removed entries."""
        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items() if entry.is_expired
            ]
            for key in expired_keys:
                del self._cache[key]

            if expired_keys:
                logger.debug(f"Cache cleanup: removed {len(expired_keys)} expired entries")

            return len(expired_keys)

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            The cached value, or None if not found or expired
        """
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None

            if entry.is_expired:
                del self._cache[key]
                return None

            return entry.value

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int = 60,
    ) -> None:
        """
        Set a value in the cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time-to-live in seconds
        """
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        async with self._lock:
            self._cache[key] = CacheEntry(value=value, expires_at=expires_at)

    async def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.

        Args:
            key: Cache key

        Returns:
            True if the key existed and was deleted
        """
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def get_or_set(
        self,
        key: str,
        compute_fn: Callable[[], T],
        ttl_seconds: int = 60,
    ) -> T:
        """
        Get a value from cache, or compute and cache it if not present.

        Args:
            key: Cache key
            compute_fn: Function to compute the value if not cached
            ttl_seconds: Time-to-live in seconds

        Returns:
            The cached or computed value
        """
        # Try to get existing value
        value = await self.get(key)
        if value is not None:
            return value

        # Compute new value
        if asyncio.iscoroutinefunction(compute_fn):
            value = await compute_fn()
        else:
            value = compute_fn()

        # Cache and return
        await self.set(key, value, ttl_seconds)
        return value

    async def clear(self) -> int:
        """
        Clear all entries from the cache.

        Returns:
            Number of entries cleared
        """
        async with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count

    @property
    def size(self) -> int:
        """Return the number of entries in the cache."""
        return len(self._cache)


# Global cache instance
_cache: Optional[CacheService] = None


def get_cache() -> CacheService:
    """Get the global cache instance."""
    global _cache
    if _cache is None:
        _cache = CacheService()
    return _cache


async def init_cache() -> CacheService:
    """Initialize and start the global cache."""
    cache = get_cache()
    await cache.start()
    return cache


async def close_cache() -> None:
    """Stop the global cache."""
    global _cache
    if _cache:
        await _cache.stop()
        _cache = None

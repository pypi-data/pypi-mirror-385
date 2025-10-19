"""
Multi-Layer Cache Implementation
Purpose: L1 (in-memory) -> L2 (Redis) -> L3 (Database) caching strategy
"""

import time
import hashlib
import json
from typing import Any, Optional, Callable
from functools import wraps
import redis
from cachetools import TTLCache


class MultiLayerCache:
    """
    Three-tier caching system:
    - L1: In-memory cache (fastest, smallest capacity)
    - L2: Redis cache (medium speed, medium capacity)
    - L3: Database (slowest, unlimited capacity)
    """

    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        l1_maxsize: int = 1000,
        l1_ttl: int = 60,
        l2_ttl: int = 3600,
    ):
        # L1: In-memory cache (TTL-based)
        self.l1_cache = TTLCache(maxsize=l1_maxsize, ttl=l1_ttl)

        # L2: Redis cache
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True,
        )
        self.l2_ttl = l2_ttl

        # Metrics
        self.metrics = {
            "l1_hits": 0,
            "l1_misses": 0,
            "l2_hits": 0,
            "l2_misses": 0,
            "l3_hits": 0,
        }

    def _generate_key(self, namespace: str, key: str) -> str:
        """Generate cache key with namespace."""
        return f"{namespace}:{key}"

    def _serialize(self, value: Any) -> str:
        """Serialize value for storage."""
        return json.dumps(value)

    def _deserialize(self, value: str) -> Any:
        """Deserialize value from storage."""
        return json.loads(value)

    def get(self, namespace: str, key: str) -> Optional[Any]:
        """
        Get value from cache, checking L1 -> L2 -> L3.
        """
        cache_key = self._generate_key(namespace, key)

        # L1: Check in-memory cache
        if cache_key in self.l1_cache:
            self.metrics["l1_hits"] += 1
            return self.l1_cache[cache_key]

        self.metrics["l1_misses"] += 1

        # L2: Check Redis cache
        l2_value = self.redis_client.get(cache_key)
        if l2_value:
            self.metrics["l2_hits"] += 1
            deserialized = self._deserialize(l2_value)
            # Populate L1 cache
            self.l1_cache[cache_key] = deserialized
            return deserialized

        self.metrics["l2_misses"] += 1
        return None

    def set(
        self,
        namespace: str,
        key: str,
        value: Any,
        l1_ttl: Optional[int] = None,
        l2_ttl: Optional[int] = None,
    ):
        """
        Set value in both L1 and L2 caches.
        """
        cache_key = self._generate_key(namespace, key)

        # L1: Set in-memory cache
        self.l1_cache[cache_key] = value

        # L2: Set Redis cache
        serialized = self._serialize(value)
        ttl = l2_ttl or self.l2_ttl
        self.redis_client.setex(cache_key, ttl, serialized)

    def delete(self, namespace: str, key: str):
        """
        Delete value from all cache layers.
        """
        cache_key = self._generate_key(namespace, key)

        # L1: Delete from in-memory cache
        self.l1_cache.pop(cache_key, None)

        # L2: Delete from Redis
        self.redis_client.delete(cache_key)

    def invalidate_pattern(self, namespace: str, pattern: str = "*"):
        """
        Invalidate all keys matching pattern in namespace.
        """
        full_pattern = f"{namespace}:{pattern}"

        # L1: Clear matching keys (simple iteration)
        keys_to_delete = [
            k for k in self.l1_cache.keys() if k.startswith(f"{namespace}:")
        ]
        for k in keys_to_delete:
            del self.l1_cache[k]

        # L2: Use Redis SCAN for safe deletion
        cursor = 0
        while True:
            cursor, keys = self.redis_client.scan(cursor, match=full_pattern, count=100)
            if keys:
                self.redis_client.delete(*keys)
            if cursor == 0:
                break

    def get_metrics(self) -> dict:
        """
        Get cache performance metrics.
        """
        total_requests = (
            self.metrics["l1_hits"]
            + self.metrics["l1_misses"]
            + self.metrics["l2_hits"]
            + self.metrics["l2_misses"]
        )

        if total_requests == 0:
            return {**self.metrics, "hit_rate": 0.0}

        hit_rate = (
            self.metrics["l1_hits"] + self.metrics["l2_hits"]
        ) / total_requests

        return {
            **self.metrics,
            "total_requests": total_requests,
            "hit_rate": hit_rate,
        }


def cached(
    namespace: str,
    key_func: Optional[Callable] = None,
    l1_ttl: int = 60,
    l2_ttl: int = 3600,
):
    """
    Decorator for caching function results.

    Usage:
        @cached(namespace="users", l1_ttl=60, l2_ttl=3600)
        def get_user(user_id: int):
            return db.query(User).filter(User.id == user_id).first()

        @cached(namespace="products", key_func=lambda product_id: f"product:{product_id}")
        def get_product(product_id: int):
            return db.query(Product).filter(Product.id == product_id).first()
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default: hash function name + args
                key_parts = [func.__name__] + [str(arg) for arg in args]
                key_parts += [f"{k}={v}" for k, v in sorted(kwargs.items())]
                cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()

            # Try to get from cache
            cache = MultiLayerCache()
            cached_value = cache.get(namespace, cache_key)
            if cached_value is not None:
                return cached_value

            # Cache miss - execute function
            result = func(*args, **kwargs)

            # Store in cache
            cache.set(namespace, cache_key, result, l1_ttl=l1_ttl, l2_ttl=l2_ttl)

            return result

        return wrapper

    return decorator


# Example Usage
if __name__ == "__main__":
    cache = MultiLayerCache()

    # Set values
    cache.set("users", "user:123", {"id": 123, "name": "Alice"})
    cache.set("products", "product:456", {"id": 456, "name": "Widget"})

    # Get values (L1 hit)
    user = cache.get("users", "user:123")
    print(f"User: {user}")

    # Get values (L2 hit after L1 expires)
    time.sleep(61)  # Wait for L1 to expire
    user = cache.get("users", "user:123")
    print(f"User from L2: {user}")

    # Invalidate pattern
    cache.invalidate_pattern("users", "user:*")

    # Get metrics
    metrics = cache.get_metrics()
    print(f"Cache metrics: {metrics}")

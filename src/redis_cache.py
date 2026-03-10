from __future__ import annotations

from typing import Optional

import redis

_redis_client: redis.Redis | None = None


def connect(redis_url: str) -> redis.Redis:
    client = redis.Redis.from_url(redis_url, decode_responses=True)
    client.ping()
    return client


def configure(client: redis.Redis) -> None:
    global _redis_client
    _redis_client = client


def _client() -> redis.Redis:
    if _redis_client is None:
        raise RuntimeError("Redis client is not configured")
    return _redis_client


def _key(symbol: str) -> str:
    return f"price:{symbol.upper()}"


def get_cached_price(symbol: str) -> Optional[float]:
    value = _client().get(_key(symbol))
    if value is None:
        return None
    return float(value)


def set_cached_price(symbol: str, price: float, ttl_seconds: int) -> None:
    _client().set(_key(symbol), str(price), ex=ttl_seconds)


def get_last_price_before_update(symbol: str) -> Optional[float]:
    return get_cached_price(symbol)

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    symbol: str = "BTCUSDT"
    ttl_seconds: int = 25
    interval_seconds: int = 5

    redis_url: str = "redis://localhost:6379/0"
    mongo_url: str = "mongodb://localhost:27017"
    cassandra_host: str = "localhost"
    cassandra_port: int = 9042
    cassandra_keyspace: str = "market_intel"

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password123"

    investors: list[str] = field(default_factory=lambda: ["Alice", "Bob", "Carlos"])


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


def load_settings() -> Settings:
    return Settings(
        symbol=os.getenv("SYMBOL", "BTCUSDT").upper(),
        ttl_seconds=_env_int("TTL_SECONDS", 25),
        interval_seconds=_env_int("INTERVAL_SECONDS", 5),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        mongo_url=os.getenv("MONGO_URL", "mongodb://localhost:27017"),
        cassandra_host=os.getenv("CASSANDRA_HOST", "localhost"),
        cassandra_port=_env_int("CASSANDRA_PORT", 9042),
        cassandra_keyspace=os.getenv("CASSANDRA_KEYSPACE", "market_intel"),
        neo4j_uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        neo4j_user=os.getenv("NEO4J_USER", "neo4j"),
        neo4j_password=os.getenv("NEO4J_PASSWORD", "password123"),
    )

from __future__ import annotations

import time
from typing import Callable, TypeVar

from src import cassandra_ts, mongo_lake, neo4j_alerts, orchestrator, redis_cache
from src.config import Settings, load_settings

T = TypeVar("T")


def with_retry(name: str, fn: Callable[[], T], attempts: int = 5, base_delay: float = 1.0) -> T:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except Exception as exc:
            last_error = exc
            print(f"[{name}] Tentativa {attempt}/{attempts} falhou: {exc}")
            if attempt < attempts:
                time.sleep(base_delay * attempt)
    assert last_error is not None
    raise last_error


def setup_connections(settings: Settings) -> None:
    redis_client = with_retry("REDIS", lambda: redis_cache.connect(settings.redis_url))
    redis_cache.configure(redis_client)
    print("[REDIS] Conexao OK")

    mongo_client = with_retry("MONGO", lambda: mongo_lake.connect(settings.mongo_url))
    mongo_lake.configure(mongo_client)
    print("[MONGO] Conexao OK")

    cassandra_session = with_retry(
        "CASSANDRA", lambda: cassandra_ts.connect(settings.cassandra_host, settings.cassandra_port)
    )
    cassandra_ts.configure(cassandra_session, settings.cassandra_keyspace)
    with_retry("CASSANDRA", cassandra_ts.ensure_schema)
    print("[CASSANDRA] Conexao e schema OK")

    neo4j_driver = with_retry(
        "NEO4J", lambda: neo4j_alerts.connect(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)
    )
    neo4j_alerts.configure(neo4j_driver)
    with_retry("NEO4J", lambda: neo4j_alerts.ensure_seed(settings.symbol, settings.investors))
    print("[NEO4J] Conexao e seed inicial OK")


def main() -> None:
    settings = load_settings()
    setup_connections(settings)
    orchestrator.initialize_runtime()
    orchestrator.run_forever(settings)


if __name__ == "__main__":
    main()

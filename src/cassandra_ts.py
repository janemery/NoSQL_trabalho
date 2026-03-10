from __future__ import annotations

from datetime import datetime

from cassandra.cluster import Cluster, Session

_session: Session | None = None
_keyspace: str | None = None


def connect(host: str, port: int) -> Session:
    cluster = Cluster([host], port=port)
    return cluster.connect()


def configure(session: Session, keyspace: str) -> None:
    global _session, _keyspace
    _session = session
    _keyspace = keyspace


def _session_or_raise() -> Session:
    if _session is None:
        raise RuntimeError("Cassandra session is not configured")
    return _session


def _keyspace_or_raise() -> str:
    if _keyspace is None:
        raise RuntimeError("Cassandra keyspace is not configured")
    return _keyspace


def ensure_schema() -> None:
    session = _session_or_raise()
    keyspace = _keyspace_or_raise()

    session.execute(
        f"""
        CREATE KEYSPACE IF NOT EXISTS {keyspace}
        WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}
        """
    )
    session.set_keyspace(keyspace)
    session.execute(
        """
        CREATE TABLE IF NOT EXISTS historico_precos (
            symbol text,
            ts timestamp,
            price double,
            source text,
            PRIMARY KEY ((symbol), ts)
        ) WITH CLUSTERING ORDER BY (ts DESC)
        """
    )


def insert_price(symbol: str, ts: datetime, price: float, source: str) -> None:
    session = _session_or_raise()
    keyspace = _keyspace_or_raise()
    session.set_keyspace(keyspace)
    session.execute(
        """
        INSERT INTO historico_precos (symbol, ts, price, source)
        VALUES (%s, %s, %s, %s)
        """,
        (symbol.upper(), ts, price, source),
    )


def get_latest(symbol: str, limit: int = 5) -> list[dict]:
    session = _session_or_raise()
    keyspace = _keyspace_or_raise()
    session.set_keyspace(keyspace)
    rows = session.execute(
        """
        SELECT symbol, ts, price, source
        FROM historico_precos
        WHERE symbol = %s
        LIMIT %s
        """,
        (symbol.upper(), limit),
    )
    return [
        {"symbol": row.symbol, "ts": row.ts, "price": row.price, "source": row.source}
        for row in rows
    ]

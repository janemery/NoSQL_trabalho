from __future__ import annotations

from datetime import datetime

from neo4j import Driver, GraphDatabase

_driver: Driver | None = None


def connect(uri: str, user: str, password: str) -> Driver:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    driver.verify_connectivity()
    return driver


def configure(driver: Driver) -> None:
    global _driver
    _driver = driver


def _driver_or_raise() -> Driver:
    if _driver is None:
        raise RuntimeError("Neo4j driver is not configured")
    return _driver


def ensure_seed(symbol: str, investors: list[str]) -> None:
    driver = _driver_or_raise()
    with driver.session() as session:
        session.run("MERGE (:Moeda {codigo: $symbol})", symbol=symbol.upper())
        for investor in investors:
            session.run(
                """
                MERGE (i:Investidor {nome: $name})
                WITH i
                MATCH (m:Moeda {codigo: $symbol})
                MERGE (i)-[:ACOMPANHA]->(m)
                """,
                name=investor,
                symbol=symbol.upper(),
            )


def get_watchers(symbol: str) -> list[str]:
    driver = _driver_or_raise()
    with driver.session() as session:
        records = session.run(
            """
            MATCH (i:Investidor)-[:ACOMPANHA]->(m:Moeda {codigo: $symbol})
            RETURN i.nome AS nome
            ORDER BY nome
            """,
            symbol=symbol.upper(),
        )
        return [record["nome"] for record in records]


def touch_last_notification(symbol: str, when: datetime) -> None:
    driver = _driver_or_raise()
    with driver.session() as session:
        session.run(
            """
            MATCH (i:Investidor)-[r:ACOMPANHA]->(m:Moeda {codigo: $symbol})
            SET r.ultima_notificacao = $when
            """,
            symbol=symbol.upper(),
            when=when.isoformat(),
        )

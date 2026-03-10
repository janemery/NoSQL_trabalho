from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.api_client import fetch_binance_price
from src.cassandra_ts import configure, connect, ensure_schema, get_latest, insert_price
from src.config import load_settings


def main() -> None:
    settings = load_settings()

    session = connect(settings.cassandra_host, settings.cassandra_port)
    configure(session, settings.cassandra_keyspace)
    ensure_schema()

    quote = fetch_binance_price(settings.symbol)
    insert_price(quote.symbol, quote.collected_at, quote.price, quote.source)

    latest = get_latest(settings.symbol, limit=5)

    print("[SCENARIO 04] Cassandra insert/query OK")
    print(latest)


if __name__ == "__main__":
    main()

from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.config import load_settings
from src.neo4j_alerts import configure, connect, ensure_seed, get_watchers


def main() -> None:
    settings = load_settings()

    driver = connect(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)
    configure(driver)

    ensure_seed(settings.symbol, settings.investors)
    watchers = get_watchers(settings.symbol)

    print("[SCENARIO 05] Neo4j seed/match OK")
    print(f"Investidores para {settings.symbol}: {watchers}")


if __name__ == "__main__":
    main()

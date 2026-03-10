from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.api_client import fetch_binance_price
from src.config import load_settings


def main() -> None:
    settings = load_settings()
    quote = fetch_binance_price(settings.symbol)
    print("[SCENARIO 01] API Binance OK")
    print(
        {
            "symbol": quote.symbol,
            "price": quote.price,
            "variation": quote.variation,
            "source": quote.source,
            "collected_at": quote.collected_at.isoformat(),
        }
    )


if __name__ == "__main__":
    main()

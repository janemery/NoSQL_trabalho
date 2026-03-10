from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import requests


@dataclass
class NormalizedQuote:
    symbol: str
    price: float
    variation: float | None
    source: str
    collected_at: datetime
    raw_payload: dict


def fetch_binance_price(symbol: str) -> NormalizedQuote:
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    payload = response.json()
    if "price" not in payload or "symbol" not in payload:
        raise ValueError(f"Unexpected Binance payload: {payload}")

    return NormalizedQuote(
        symbol=str(payload["symbol"]).upper(),
        price=float(payload["price"]),
        variation=None,
        source="binance",
        collected_at=datetime.now(timezone.utc),
        raw_payload=payload,
    )

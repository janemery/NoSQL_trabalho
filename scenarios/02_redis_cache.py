from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.api_client import fetch_binance_price
from src.config import load_settings
from src.redis_cache import configure, connect, get_cached_price, set_cached_price


def main() -> None:
    settings = load_settings()
    client = connect(settings.redis_url)
    configure(client)

    symbol = settings.symbol
    ttl = settings.ttl_seconds

    print("[SCENARIO 02] Teste Redis cache hit/miss")

    first = get_cached_price(symbol)
    if first is None:
        print("Primeira leitura: MISS")
        quote = fetch_binance_price(symbol)
        set_cached_price(symbol, quote.price, ttl)
        print(f"Cache gravado: {quote.price:.6f} (TTL={ttl}s)")
    else:
        print(f"Primeira leitura: HIT ({first:.6f})")

    second = get_cached_price(symbol)
    if second is None:
        print("Segunda leitura imediata: MISS (inesperado)")
    else:
        print(f"Segunda leitura imediata: HIT ({second:.6f})")

    print(f"Aguardando TTL ({ttl + 1}s) para validar expiracao...")
    time.sleep(ttl + 1)

    third = get_cached_price(symbol)
    if third is None:
        print("Leitura apos TTL: MISS (ok)")
    else:
        print(f"Leitura apos TTL: HIT ({third:.6f})")


if __name__ == "__main__":
    main()

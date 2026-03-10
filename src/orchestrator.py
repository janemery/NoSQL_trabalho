from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone

from src import api_client, cassandra_ts, mongo_lake, neo4j_alerts, redis_cache
from src.config import Settings


@dataclass
class CycleResult:
    symbol: str
    price: float | None
    cache_hit: bool
    persisted: bool
    watchers: list[str]
    source: str


_initialized = False


def initialize_runtime() -> None:
    global _initialized
    _initialized = True


def run_once(settings: Settings) -> CycleResult:
    if not _initialized:
        raise RuntimeError("Orchestrator is not initialized. Call initialize_runtime() first.")

    symbol = settings.symbol.upper()
    price: float | None = None
    cache_hit = False
    persisted = False
    source = "unknown"

    print(f"Consultando preco de {symbol}...")

    try:
        cached = redis_cache.get_cached_price(symbol)
    except Exception as exc:
        print(f"[REDIS] Erro ao consultar cache: {exc}")
        cached = None

    if cached is not None:
        cache_hit = True
        price = cached
        source = "redis"
        print(f"[REDIS] Cache Hit! Preco em cache: {price:.6f}")
    else:
        print("[REDIS] Cache Miss! Buscando na API Binance...")
        try:
            last_price = redis_cache.get_last_price_before_update(symbol)
            quote = api_client.fetch_binance_price(symbol)
            price = quote.price
            source = quote.source
            redis_cache.set_cached_price(symbol, price, settings.ttl_seconds)
            print(
                f"[REDIS] Cache atualizado (TTL={settings.ttl_seconds}s). "
                f"Preco atual: {price:.6f}"
            )
            if last_price is not None:
                if price > last_price:
                    trend = "subiu"
                elif price < last_price:
                    trend = "caiu"
                else:
                    trend = "estavel"
                print(f"[VOLATILIDADE] Ultimo: {last_price:.6f} | Atual: {price:.6f} ({trend})")

            try:
                mongo_id = mongo_lake.insert_quote(quote)
                print(f"[MONGO] Payload bruto salvo no Data Lake (id={mongo_id}).")
            except Exception as exc:
                print(f"[MONGO] Erro ao salvar payload: {exc}")

            try:
                cassandra_ts.insert_price(quote.symbol, quote.collected_at, quote.price, quote.source)
                print("[CASSANDRA] Preco gravado na serie temporal.")
            except Exception as exc:
                print(f"[CASSANDRA] Erro ao gravar serie temporal: {exc}")

            persisted = True
        except Exception as exc:
            print(f"[API] Erro ao buscar preco na Binance: {exc}")

    watchers: list[str] = []
    try:
        watchers = neo4j_alerts.get_watchers(symbol)
        if watchers:
            print(f"[NEO4J] Notificando investidores: {', '.join(watchers)}")
            neo4j_alerts.touch_last_notification(symbol, datetime.now(timezone.utc))
        else:
            print("[NEO4J] Nenhum investidor acompanha esta moeda.")
    except Exception as exc:
        print(f"[NEO4J] Erro ao consultar investidores: {exc}")

    return CycleResult(
        symbol=symbol,
        price=price,
        cache_hit=cache_hit,
        persisted=persisted,
        watchers=watchers,
        source=source,
    )


def run_forever(settings: Settings) -> None:
    while True:
        try:
            run_once(settings)
        except Exception as exc:
            print(f"[ORCHESTRATOR] Erro inesperado no ciclo: {exc}")
        time.sleep(settings.interval_seconds)

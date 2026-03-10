from __future__ import annotations

from pymongo import MongoClient
from pymongo.collection import Collection

from src.api_client import NormalizedQuote

_mongo_collection: Collection | None = None


def connect(mongo_url: str) -> MongoClient:
    client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    return client


def configure(client: MongoClient) -> None:
    global _mongo_collection
    _mongo_collection = client["market_data"]["raw_quotes"]


def _collection() -> Collection:
    if _mongo_collection is None:
        raise RuntimeError("Mongo collection is not configured")
    return _mongo_collection


def insert_quote(quote: NormalizedQuote) -> str:
    doc = {
        "symbol": quote.symbol,
        "price": quote.price,
        "variation": quote.variation,
        "source": quote.source,
        "collected_at": quote.collected_at,
        "raw_payload": quote.raw_payload,
    }
    result = _collection().insert_one(doc)
    return str(result.inserted_id)

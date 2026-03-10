from __future__ import annotations

import sys
from pathlib import Path

from bson import ObjectId

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.api_client import fetch_binance_price
from src.config import load_settings
from src.mongo_lake import configure, connect, insert_quote


def main() -> None:
    settings = load_settings()
    mongo_client = connect(settings.mongo_url)
    configure(mongo_client)

    quote = fetch_binance_price(settings.symbol)
    inserted_id = insert_quote(quote)
    document = mongo_client["market_data"]["raw_quotes"].find_one({"_id": ObjectId(inserted_id)})

    print("[SCENARIO 03] Mongo insert OK")
    print(f"Documento inserido: {inserted_id}")
    if document is None:
        print("Consulta por _id falhou: documento nao encontrado.")
    else:
        print(
            {
                "_id": str(document["_id"]),
                "symbol": document.get("symbol"),
                "price": document.get("price"),
                "source": document.get("source"),
                "collected_at": str(document.get("collected_at")),
            }
        )


if __name__ == "__main__":
    main()

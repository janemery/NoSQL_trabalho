from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from monitor import setup_connections
from src.config import load_settings
from src.orchestrator import initialize_runtime, run_once


def main() -> None:
    settings = load_settings()
    setup_connections(settings)
    initialize_runtime()
    result = run_once(settings)

    print("[SCENARIO 06] Ciclo integrado unico OK")
    print(result)


if __name__ == "__main__":
    main()

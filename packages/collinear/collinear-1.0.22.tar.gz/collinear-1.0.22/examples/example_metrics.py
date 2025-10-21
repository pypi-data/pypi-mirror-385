"""Timing demo: quick round-trip durations (concise).

Runs several short conversations, measures durations, and prints simple stats.
"""

from __future__ import annotations

import os
import statistics
import time
from pathlib import Path

from dotenv import load_dotenv

from collinear.client import Client


RUNS = 5
EXCHANGES = 6
BATCH_DELAY = 0.0
ESTIMATE_ROUND_TRIPS = 6


def main() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(env_path, override=True)

    api_key = os.environ["OPENAI_API_KEY"]
    collinear_api_key = os.environ["COLLINEAR_API_KEY"]

    client = Client(
        assistant_model_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        assistant_model_api_key=api_key,
        assistant_model_name=os.getenv("OPENAI_ASSISTANT_MODEL", "gpt-4o-mini"),
        collinear_api_key=collinear_api_key,
    )

    durations: list[float] = []
    for _ in range(RUNS):
        start = time.perf_counter()
        _ = client.simulate(
            traitmix_config={
                "ages": ["25-34", "35-44"],
                "genders": ["male", "female"],
                "occupations": ["Employed", "Student"],
                "intents": ["Resolve billing issue", "Cancel service"],
                "traits": {"impatience": ["medium", "high"]},
                "locations": ["United States"],
                "languages": ["English"],
                "tasks": ["telecom metrics"],
            },
            k=1,
            num_exchanges=EXCHANGES,
            batch_delay=BATCH_DELAY,
        )
        durations.append(time.perf_counter() - start)

    avg_conv = statistics.fmean(durations)
    min_conv = min(durations)
    max_conv = max(durations)
    stdev_conv = statistics.pstdev(durations) if len(durations) > 1 else 0.0
    avg_round_trip = avg_conv / EXCHANGES
    est_duration = avg_round_trip * ESTIMATE_ROUND_TRIPS

    print("== Timing Metrics ==")
    print(f"Runs: {RUNS}")
    print(f"Exchanges per conversation: {EXCHANGES} (user+assistant pairs)")
    print(
        f"Average conversation: {avg_conv:.3f}s (min={min_conv:.3f}s, max={max_conv:.3f}s, stdev={stdev_conv:.3f}s)"
    )
    print(f"Avg time per round trip: {avg_round_trip:.3f}s")
    print(
        f"Estimated duration for {ESTIMATE_ROUND_TRIPS} round trips (~{ESTIMATE_ROUND_TRIPS * 2} turns): {est_duration:.3f}s"
    )


if __name__ == "__main__":
    main()

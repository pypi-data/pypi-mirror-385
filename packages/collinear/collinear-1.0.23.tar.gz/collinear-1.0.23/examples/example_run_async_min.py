from __future__ import annotations

import os
import asyncio
from pathlib import Path

from dotenv import load_dotenv

from collinear.client import Client
from collinear.schemas.traitmix import TraitMixConfig


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
        timeout=30.0,
    )

    runner = client.simulation_runner

    cfg = TraitMixConfig(traits={"impatience": ["medium"]})

    sims = asyncio.run(
        runner.run_async(
            cfg,
            k=1,
            num_exchanges=1,
            batch_delay=0.0,
            assistant_max_tokens=32,
            assistant_seed=123,
            progress=False,
        )
    )

    for idx, sim in enumerate(sims, start=1):
        print(f"Conversation {idx}")
        for message in sim.conv_prefix:
            role = message.get("role", "")
            content = message.get("content", "")
            if content:
                print(f"{role}: {content}")
        print(f"assistant: {sim.response}\n")


if __name__ == "__main__":
    main()

"""Run a simulation from a JSON config (concise).

Loads a config file in `examples/example_configs`, runs one short
simulation, and prints the transcript.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

from collinear.client import Client


CONFIG_PATH = Path(__file__).with_name("example_configs").joinpath("config_hotel.json")


def main() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    load_dotenv(env_path, override=True)

    api_key = os.environ["OPENAI_API_KEY"]
    collinear_api_key = os.environ["COLLINEAR_API_KEY"]

    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        traitmix_config = json.load(f)

    client = Client(
        assistant_model_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        assistant_model_api_key=api_key,
        assistant_model_name=os.getenv("OPENAI_ASSISTANT_MODEL", "gpt-4o-mini"),
        collinear_api_key=collinear_api_key,
    )

    sims = client.simulate(traitmix_config=traitmix_config, k=1, num_exchanges=2)

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

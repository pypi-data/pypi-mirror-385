"""Minimal simulation demo.

Loads `.env`, runs a few simulations, and prints transcripts.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from collinear.client import Client


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

    sims = client.simulate(
        traitmix_config={
            "ages": ["25-34", "35-44"],
            "genders": ["male", "female"],
            "occupations": ["Employed", "Student"],
            "intents": ["Resolve billing issue", "Cancel service"],
            "traits": {"confusion": ["high"]},
            "locations": ["United States"],
            "languages": ["English"],
            "tasks": ["telecom quickstart"],
        },
        k=1,
        num_exchanges=40,
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

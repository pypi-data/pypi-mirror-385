"""Inspect traitmix payloads with role swapping in action.

Loads environment variables, runs a short simulation, and logs each request
payload sent to the traitmix service together with the raw responses. This makes it
easy to verify that the SDK swaps ``user``/``assistant`` roles before hitting
the TraitMix API.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any
from typing import Iterable

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from collinear.schemas.traitmix import TraitMixConfig
from collinear.simulate.runner import SimulationRunner


class LoggingSimulationRunner(SimulationRunner):
    """Simulation runner that prints traitmix payloads and responses."""

    async def call_batch_endpoint(
        self,
        url: str,
        payloads: list[dict[str, object]],
        *,
        headers: dict[str, str],
    ) -> list[str]:
        self._log_payloads(payloads)
        responses = await super().call_batch_endpoint(url, payloads, headers=headers)
        self._log_responses(responses)
        return responses

    def _log_payloads(self, payloads: Iterable[dict[str, Any]]) -> None:
        for idx, payload in enumerate(payloads, start=1):
            print("\n=== TraitMix Request %d ===" % idx)
            print(json.dumps(payload, indent=2))
            messages = payload.get("messages")
            if isinstance(messages, list) and messages:
                print("-- Message Timeline --")
                for turn_idx, message in enumerate(messages, start=1):
                    role = str(message.get("role", "?"))
                    content = str(message.get("content", ""))
                    print(f"{role} {turn_idx:02d}: {content}")

    def _log_responses(self, responses: Iterable[str]) -> None:
        for idx, response in enumerate(responses, start=1):
            print("\n=== TraitMix Response %d ===" % idx)
            print(response)


async def _run() -> None:
    # Load shared .env at repository root if present.
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)

    collinear_api_key = os.environ["COLLINEAR_API_KEY"]
    assistant_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    assistant_api_key = os.getenv("OPENAI_API_KEY", "")
    assistant_model = os.getenv("OPENAI_ASSISTANT_MODEL", "gpt-4o-mini")

    runner = LoggingSimulationRunner(
        assistant_model_url=assistant_url,
        assistant_model_api_key=assistant_api_key,
        assistant_model_name=assistant_model,
        collinear_api_key=collinear_api_key,
    )

    if not assistant_api_key:
        print("Assistant API key not found; using placeholder assistant responses.")

        async def fake_call_with_retry(
            _self: SimulationRunner,
            _messages: list[dict[str, object]],
            _system_prompt: str,
        ) -> str:
            return "FAKE_ASSISTANT"

        # Bind coroutine to the runner instance.
        runner.call_with_retry = fake_call_with_retry.__get__(runner, SimulationRunner)

    config = TraitMixConfig.from_input(
        {
            "intents": ["Resolve billing issue"],
            "traits": {"confusion": ["low"]},
            "languages": ["English"],
        }
    )

    results = await runner.run_async(
        config=config,
        k=1,
        num_exchanges=5,
        batch_delay=0.0,
        progress=False,
    )

    for idx, result in enumerate(results, start=1):
        print("\n=== Conversation %d Transcript ===" % idx)
        for turn_idx, message in enumerate(result.conv_prefix, start=1):
            role = message.get("role", "?")
            content = message.get("content", "")
            print(f"{role} {turn_idx:02d}: {content}")
        final_turn = len(result.conv_prefix) + 1
        print(f"assistant {final_turn:02d}: {result.response}")


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()

"""Minimal SDK Redteam example.

This example demonstrates how to run a red-team evaluation using the Collinear SDK.
The server will automatically load the attack plan, so no need to provide behaviors manually.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

from collinear.client import Client


def main() -> None:
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)

    os.environ.setdefault("COLLINEAR_BACKEND_URL", "http://localhost:8000")

    client = Client(
        assistant_model_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        assistant_model_api_key=os.environ["OPENAI_API_KEY"],
        assistant_model_name=os.getenv("OPENAI_ASSISTANT_MODEL", "gpt-4o-mini"),
        collinear_api_key=os.getenv("COLLINEAR_API_KEY", "demo-placeholder"),
    )

    # Start red-team evaluation
    # Attack plan is loaded automatically on the server
    evaluation = client.redteam(max_turns=2)
    result = evaluation.poll(timeout=600.0, interval=5.0)

    print(f"\nEvaluation {evaluation.id}: {result.get('status')}")

    summary = evaluation.summary()
    print(f"\nSummary:")
    print(f"  Total behaviors: {summary['total_behaviors']}")
    print(f"  Successful: {summary['successful']}")
    print(f"  Failed: {summary['failed']}")
    if summary['errors_by_type']:
        print(f"  Errors by type: {summary['errors_by_type']}")

    if evaluation.has_errors():
        print(f"\nErrors detected:")
        for behavior_num, error in evaluation.get_errors().items():
            print(f"  Behavior {behavior_num}: {error}")

    print(f"\nFull results:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

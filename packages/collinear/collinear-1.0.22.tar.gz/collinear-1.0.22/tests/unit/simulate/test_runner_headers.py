"""Ensure SimulationRunner sends only the canonical TraitMix API header."""

from __future__ import annotations

from collinear.schemas.traitmix import TraitMixConfig
from tests.helpers.runners import CaptureRunner


def test_traitmix_headers_use_api_key_only() -> None:
    """USER calls include only `API-Key` header (no `X-API-Key`)."""
    runner = CaptureRunner(collinear_api_key="traitmix-secret")

    cfg = TraitMixConfig(
        ages=["25-34"],
        genders=["female"],
        occupations=["Employed"],
        intents=["billing"],
        traits={"impatience": ["medium"]},
    )

    runner.run(config=cfg, k=1, num_exchanges=1, batch_delay=0.0, progress=False)
    assert runner.captured_headers
    headers = runner.captured_headers[-1]
    assert headers == {"Content-Type": "application/json", "API-Key": "traitmix-secret"}

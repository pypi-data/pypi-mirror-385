"""Tests for building redteam payloads from configuration."""

from collinear.redteam.payloads import build_redteam_payload
from collinear.redteam.schemas import ModelConfig
from collinear.redteam.schemas import RedteamConfig


def _cfg() -> RedteamConfig:
    attacker = ModelConfig(model="a")
    target = ModelConfig(model="b")
    eval_ = ModelConfig(model="c")
    return RedteamConfig(
        attacker=attacker,
        target=target,
        evaluation=eval_,
        judge_template="JT",
        scoring_policy="SP",
        detailed_policy="DP",
        target_system_prompt="TSP",
    )


def test_build_payload_includes_optional_fields() -> None:
    """Optional config fields appear in the payload when provided."""
    payload = build_redteam_payload(_cfg())
    # required top-level keys
    required = {
        "attacker_config",
        "target_config",
        "evaluation_config",
        "max_workers",
    }
    assert required <= payload.keys()
    # optional fields included when provided
    assert payload["custom_judge_prompt"] == "JT"
    assert payload["custom_scoring_policy"] == "SP"
    assert payload["custom_detailed_policy"] == "DP"
    assert payload["target_system_prompt"] == "TSP"

"""Tests for building redteam payloads from configuration."""

from collinear.redteam.payloads import build_redteam_payload
from collinear.redteam.schemas import ModelConfig
from collinear.redteam.schemas import RedteamConfig


def _cfg() -> RedteamConfig:
    behavior: dict[str, object] = {
        "behavior_number": 1,
        "behavior_details": {"intent": "x"},
        "attack_strategies": {
            "Set_1": {
                f"strategy_{i}": {
                    "conversation_plan": {"turn_1": "a", "final_turn": "b"},
                    "approach": "d",
                }
                for i in range(1, 11)
            },
            "Set_2": {
                f"strategy_{i}": {
                    "conversation_plan": {"turn_1": "a", "final_turn": "b"},
                    "approach": "d",
                }
                for i in range(1, 11)
            },
            "Set_3": {
                f"strategy_{i}": {
                    "conversation_plan": {"turn_1": "a", "final_turn": "b"},
                    "approach": "d",
                }
                for i in range(1, 11)
            },
            "Set_4": {
                f"strategy_{i}": {
                    "conversation_plan": {"turn_1": "a", "final_turn": "b"},
                    "approach": "d",
                }
                for i in range(1, 11)
            },
            "Set_5": {
                f"strategy_{i}": {
                    "conversation_plan": {"turn_1": "a", "final_turn": "b"},
                    "approach": "d",
                }
                for i in range(1, 11)
            },
        },
    }
    attacker = ModelConfig(model="a")
    target = ModelConfig(model="b")
    eval_ = ModelConfig(model="c")
    return RedteamConfig(
        behaviors=[behavior],
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
        "selected_behaviors",
        "max_workers",
    }
    assert required <= payload.keys()
    # optional fields included when provided
    assert payload["custom_judge_prompt"] == "JT"
    assert payload["custom_scoring_policy"] == "SP"
    assert payload["custom_detailed_policy"] == "DP"
    assert payload["target_system_prompt"] == "TSP"

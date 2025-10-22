"""Schema-level validation tests for redteam behaviors."""

import pytest

from collinear.redteam.schemas import Behavior


def test_behavior_validation_errors() -> None:
    """Invalid behavior structures raise validation errors."""
    # Too few sets
    with pytest.raises(ValueError):
        Behavior.model_validate(
            {
                "behavior_number": 1,
                "behavior_details": {"intent": "x"},
                "attack_strategies": {"Set_1": {}},
            }
        )

    # Enough sets but too few strategies in a set
    sets: dict[str, dict[str, object]] = {f"Set_{i}": {} for i in range(1, 6)}
    sets["Set_1"]["strategy_1"] = {
        "conversation_plan": {"turn_1": "a", "final_turn": "b"},
        "approach": "d",
    }
    with pytest.raises(ValueError):
        Behavior.model_validate(
            {
                "behavior_number": 1,
                "behavior_details": {"intent": "x"},
                "attack_strategies": sets,
            }
        )

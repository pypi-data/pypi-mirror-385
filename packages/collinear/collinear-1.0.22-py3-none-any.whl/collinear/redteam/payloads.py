"""Pure functions for constructing red-team API payloads."""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING
from typing import cast

if TYPE_CHECKING:
    from collinear.redteam.schemas import RedteamConfig


def build_redteam_payload(config: RedteamConfig) -> dict[str, object]:
    """Construct API payload from validated config.

    Args:
        config: Validated red-team configuration

    Returns:
        JSON-serializable payload for the redteam API

    """
    payload: dict[str, object] = {
        "attacker_config": cast("dict[str, object]", dataclasses.asdict(config.attacker)),
        "target_config": cast("dict[str, object]", dataclasses.asdict(config.target)),
        "evaluation_config": cast("dict[str, object]", dataclasses.asdict(config.evaluation)),
        "selected_behaviors": list(config.behaviors),
        "max_workers": config.max_workers,
    }

    if config.judge_template is not None:
        payload["custom_judge_prompt"] = config.judge_template

    if config.scoring_policy is not None:
        payload["custom_scoring_policy"] = config.scoring_policy

    if config.detailed_policy is not None:
        payload["custom_detailed_policy"] = config.detailed_policy

    if config.target_system_prompt is not None:
        payload["target_system_prompt"] = config.target_system_prompt

    return payload

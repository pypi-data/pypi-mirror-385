"""Configuration schemas for red-team evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING

from pydantic import Field

if TYPE_CHECKING:
    # Provide a minimal stub to avoid strict mypy complaining about pydantic's Any types.
    class BaseModel:
        """Typed stub for pydantic BaseModel used only for type checking."""

        model_config: dict[str, object]

        @classmethod
        def model_validate(cls, obj: object) -> BaseModel:
            """Validate and construct a model instance from ``obj``."""
            ...

        def model_post_init(self, __context: object, /) -> None:
            """Execute hook after model initialization."""
            ...
else:
    from pydantic import BaseModel


class BehaviorDetails(BaseModel):
    """Details describing a behavior to test."""

    intent: str
    BehaviorID: str | None = None


class ConversationPlan(BaseModel):
    """Planned conversation turns for an attack strategy."""

    turn_1: str
    final_turn: str
    model_config = {"extra": "allow"}


class AttackStrategy(BaseModel):
    """A single attack strategy."""

    conversation_plan: ConversationPlan
    approach: str
    persona: str | None = None
    context: str | None = None
    turns_needed: str | None = None
    model_config = {"extra": "allow"}


class Behavior(BaseModel):
    """A complete behavior definition with attack strategies."""

    behavior_number: int
    behavior_details: BehaviorDetails
    attack_strategies: dict[str, dict[str, AttackStrategy]] = Field(
        description="Nested dict: Set name -> Strategy name -> Strategy"
    )
    model_config = {"extra": "allow"}

    def model_post_init(self, __context: object, /) -> None:
        """Validate presence of sufficient sets and strategies.

        Requires at least five sets (``Set_1``..``Set_5``), each containing at
        least ten strategies (``strategy_1``..``strategy_10``).
        """
        min_sets = 5
        min_strategies = 10
        sets = [key for key in self.attack_strategies if key.startswith("Set_")]
        if len(sets) < min_sets:
            msg = f"Behavior must have at least 5 sets (Set_1 through Set_5), found {len(sets)}"
            raise ValueError(msg)

        for set_name in sets:
            strategies = [k for k in self.attack_strategies[set_name] if k.startswith("strategy_")]
            if len(strategies) < min_strategies:
                msg = (
                    f"{set_name} must have at least 10 strategies "
                    f"(strategy_1 through strategy_10), found {len(strategies)}"
                )
                raise ValueError(msg)


@dataclass
class ModelConfig:
    """Configuration for a model (attacker, target, or evaluator)."""

    provider: str = "openai_compat"
    model: str = ""
    base_url: str = ""
    api_key: str = ""
    max_turns: int = 5
    generation_args: dict[str, object] = field(
        default_factory=lambda: {"temperature": 0.3, "max_tokens": 512}
    )
    use_gpt_judge: bool = False
    judge_model: str = ""
    strategies_per_behavior: int = 1
    sets_per_behavior: int = 5
    strategies_per_set: int = 1


@dataclass
class RedteamConfig:
    """Validated configuration for red-team evaluation."""

    behaviors: list[dict[str, object]]
    attacker: ModelConfig
    target: ModelConfig
    evaluation: ModelConfig
    max_workers: int = 2
    judge_template: str | None = None
    scoring_policy: str | None = None
    detailed_policy: str | None = None
    target_system_prompt: str | None = None

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if not self.behaviors:
            msg = "behaviors must be non-empty"
            raise ValueError(msg)
        if self.max_workers <= 0:
            msg = "max_workers must be positive"
            raise ValueError(msg)

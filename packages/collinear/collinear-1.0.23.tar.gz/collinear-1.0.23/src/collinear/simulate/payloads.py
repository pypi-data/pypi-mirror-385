"""Pure helpers to build Steering API payloads from SDK types."""

from __future__ import annotations

from openai.types.chat import ChatCompletionMessageParam

from collinear.schemas.traitmix import TraitMixCombination
from collinear.simulate.conversation import swap_roles


def level_to_label(value: int | str) -> str:
    """Normalize a trait level into the steering API's low/medium/high labels."""
    mapping = {0: "low", 1: "medium", 2: "high"}
    if isinstance(value, int):
        if value not in mapping:
            raise ValueError(f"Trait level int must be 0,1,2; got {value!r}")
        return mapping[value]
    raw = str(value).strip()
    try:
        iv = int(raw)
    except Exception as err:
        lv = raw.lower()
        if lv in {"low", "medium", "high"}:
            return lv
        raise ValueError(f"Unknown trait level: {value!r}. Use 0/1/2 or low/medium/high.") from err
    else:
        if iv not in mapping:
            raise ValueError(f"Trait level string-int must be 0,1,2; got {raw!r}")
        return mapping[iv]


def user_characteristics_from_combo(combo: TraitMixCombination) -> dict[str, object]:
    """Extract the non-empty persona attributes for the Steering API payload."""
    payload: dict[str, object] = {}
    if combo.age is not None:
        payload["age"] = combo.age
    optional: dict[str, str | None] = {
        "gender": combo.gender,
        "occupation": combo.occupation,
        "location": combo.location,
        "language": combo.language,
        "intent": combo.intent,
        "task": combo.task,
    }
    for k, v in optional.items():
        if v is not None:
            trimmed = str(v).strip()
            if trimmed:
                payload[k] = trimmed
    return payload


def build_traitmix_payload(
    *,
    trait_dict: dict[str, int | str],
    conversation: list[ChatCompletionMessageParam],
    combo: TraitMixCombination,
    temperature: float,
    max_tokens: int,
    seed: int,
) -> dict[str, object]:
    """Assemble the request body sent to the Steering API batch endpoint."""
    td: dict[str, str] = {k: level_to_label(v) for k, v in trait_dict.items()}
    messages = swap_roles(conversation)
    return {
        "trait_dict": td,
        "user_characteristics": user_characteristics_from_combo(combo),
        "messages": messages,
        "temperature": float(temperature),
        "max_tokens": int(max_tokens),
        "seed": int(seed),
    }

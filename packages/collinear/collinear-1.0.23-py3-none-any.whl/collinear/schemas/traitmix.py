"""TraitMix configuration schemas."""

from collections.abc import Iterable
from collections.abc import Mapping
from dataclasses import field
from enum import Enum
from itertools import combinations
from itertools import product
from typing import TypedDict

from openai.types.chat import ChatCompletionMessageParam
from pydantic.dataclasses import dataclass

MIN_INTENSITY: int = 0
MAX_INTENSITY: int = 2
ALLOWED_LEVELS: tuple[str, ...] = ("low", "medium", "high")
MIN_MIXED_TRAITS: int = 2


ALLOWED_AGE_RANGES: tuple[str, ...] = (
    "13-17",
    "18-24",
    "25-34",
    "35-44",
    "45-54",
    "55-64",
    "65+",
)

ALLOWED_OCCUPATIONS: tuple[str, ...] = (
    "Unemployed",
    "Employed",
    "Student",
    "Retired",
    "Not in Labor Force",
)

_AGE_INDEX: dict[str, int] = {age: idx for idx, age in enumerate(ALLOWED_AGE_RANGES)}
_MIN_RETIREMENT_INDEX: int = _AGE_INDEX["35-44"]


class Role(Enum):
    """Conversation role for a single turn."""

    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class TraitMixCombination:
    """Type definition for traitmix combinations.

    Each combination represents one concrete traitmix sample. The canonical
    representation stores ``traits`` as a mapping from trait name to its
    level label ("low"/"medium"/"high"). For convenience, ``trait`` and
    ``intensity`` properties expose the singular values when exactly one trait
    is used, else return ``None``.
    """

    age: str | None
    gender: str | None
    occupation: str | None
    intent: str | None
    traits: dict[str, int | str]
    location: str | None
    language: str | None
    task: str | None

    @property
    def trait(self) -> str | None:
        """Return the single trait name if exactly one; else ``None``."""
        if len(self.traits) == 1:
            return next(iter(self.traits))
        return None

    @property
    def intensity(self) -> int | str | None:
        """Return the single trait level if exactly one; else ``None``."""
        if len(self.traits) == 1:
            return next(iter(self.traits.values()))
        return None


@dataclass
class SimulationResult:
    """Type definition for simulation results."""

    conv_prefix: list[ChatCompletionMessageParam]
    response: str
    traitmix: TraitMixCombination | None = None


@dataclass
class TraitMixConfig:
    """Configuration for traitmix generation.

    ``traits`` maps each trait name to a list of levels, each either an int ``0``, ``1``, or ``2``
    or a label in {"low", "medium", "high"}. The generator emits one
    combination per level value for each
    trait. ``ages`` must use the canonical buckets in ``ALLOWED_AGE_RANGES`` and
    ``occupations`` must come from ``ALLOWED_OCCUPATIONS``.
    """

    ages: list[str] = field(default_factory=list)
    genders: list[str] = field(default_factory=list)
    occupations: list[str] = field(default_factory=list)
    intents: list[str] = field(default_factory=list)
    traits: dict[str, list[int | str]] = field(default_factory=dict)
    locations: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)
    tasks: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Verify the inputs of the various fields."""
        if self.ages:
            self.ages = _validate_age_ranges(self.ages)
        if self.occupations:
            self.occupations = _validate_occupations(self.occupations)

    @classmethod
    def from_input(cls, data: Mapping[str, object]) -> "TraitMixConfig":
        """Construct a TraitMixConfig from a potentially sparse mapping.

        - Missing axes default to empty lists (neutral in product).
        - Trait levels must be integers ``0``, ``1``, or ``2``; or strings in
          {"low", "medium", "high"}. Other values raise errors.
        - Only the exact keys ``languages`` and ``locations`` are supported.
        """
        if not isinstance(data, Mapping):
            raise TypeError("from_input expects a mapping-like object")

        ages = TraitMixConfigFactory.get_age_ranges(data, "ages")
        genders = TraitMixConfigFactory.get_str_list(data, "genders")
        occupations = TraitMixConfigFactory.get_occupations(data, "occupations")
        intents = TraitMixConfigFactory.get_str_list(data, "intents")
        locations = TraitMixConfigFactory.get_str_list(data, "locations")
        languages = TraitMixConfigFactory.get_str_list(data, "languages")
        tasks = TraitMixConfigFactory.get_tasks(data)
        traits = TraitMixConfigFactory.get_traits(data)

        return cls(
            ages=ages,
            genders=genders,
            occupations=occupations,
            intents=intents,
            traits=traits,
            locations=locations,
            languages=languages,
            tasks=tasks,
        )

    def combinations(self, *, mix_traits: bool = False) -> list[TraitMixCombination]:
        """Generate all traitmix combinations from this config.

        - Default (``mix_traits=False``): one trait per combination, identical to
          the previous behavior.
        - Mixed (``mix_traits=True``): exactly two distinct traits are combined
          per combination. For each unordered trait pair (t1, t2), the Cartesian
          product of their intensity lists is used to form ``trait_dict`` values
          ``{t1: l1, t2: l2}``.

        Returns combinations in deterministic order based on input ordering.
        """
        ages: list[str | None] = list(self.ages) if self.ages else [None]
        genders: list[str | None] = list(self.genders) if self.genders else [None]
        occupations: list[str | None] = list(self.occupations) if self.occupations else [None]
        intents: list[str | None] = list(self.intents) if self.intents else [None]
        locations: list[str | None] = list(self.locations) if self.locations else [None]
        languages: list[str | None] = list(self.languages) if self.languages else [None]
        tasks: list[str | None] = list(self.tasks) if self.tasks else [None]

        base = list(product(ages, genders, occupations, intents, locations, languages, tasks))
        base = [
            item for item in base if not _retired_age_is_disallowed(age=item[0], occupation=item[2])
        ]

        levels_map = _normalize_trait_levels_map(self.traits)

        if not mix_traits:
            single_pairs = [
                (trait, level) for trait, levels in levels_map.items() for level in levels
            ]

            def _build_single(
                item: tuple[
                    tuple[
                        str | None,
                        str | None,
                        str | None,
                        str | None,
                        str | None,
                        str | None,
                        str | None,
                    ],
                    tuple[str, int | str],
                ],
            ) -> TraitMixCombination:
                (
                    (
                        age,
                        gender,
                        occupation,
                        intent,
                        location,
                        language,
                        task,
                    ),
                    (trait, level),
                ) = item
                return TraitMixCombination(
                    age=age,
                    gender=gender,
                    occupation=occupation,
                    intent=intent,
                    traits={trait: level},
                    location=location,
                    language=language,
                    task=task,
                )

            return list(map(_build_single, product(base, single_pairs)))

        trait_names = [t for t, lvls in levels_map.items() if lvls]
        if len(trait_names) < MIN_MIXED_TRAITS:
            raise ValueError("mix_traits=True requires at least two traits with levels.")

        trait_pairs = list(combinations(trait_names, 2))

        pair_levels: list[tuple[str, int | str, str, int | str]] = []
        for t1, t2 in trait_pairs:
            pair_levels.extend((t1, l1, t2, l2) for l1 in levels_map[t1] for l2 in levels_map[t2])

        def _build_mixed(
            item: tuple[
                tuple[
                    str | None,
                    str | None,
                    str | None,
                    str | None,
                    str | None,
                    str | None,
                    str | None,
                ],
                tuple[str, int | str, str, int | str],
            ],
        ) -> TraitMixCombination:
            (
                (
                    age,
                    gender,
                    occupation,
                    intent,
                    location,
                    language,
                    task,
                ),
                (t1, l1, t2, l2),
            ) = item
            return TraitMixCombination(
                age=age,
                gender=gender,
                occupation=occupation,
                intent=intent,
                traits={t1: l1, t2: l2},
                location=location,
                language=language,
                task=task,
            )

        return list(map(_build_mixed, product(base, pair_levels)))


class TraitMixConfigInput(TypedDict, total=False):
    """TypedDict describing the expected TraitMixConfig input shape.

    All keys are optional. When omitted or empty, axes are treated as neutral
    elements (i.e., they do not multiply combinations). An empty ``traits``
    mapping results in zero combinations in single-trait mode.
    """

    ages: list[str]
    genders: list[str]
    occupations: list[str]
    intents: list[str]
    traits: dict[str, list[int | str]]
    locations: list[str]
    languages: list[str]
    task: str
    tasks: list[str]


def _coerce_trait_value(trait: str, value: object) -> int | str:
    """Validate and normalize a trait level.

    - Integers must be within [MIN_INTENSITY, MAX_INTENSITY] (i.e., 0, 1, or 2).
    - Strings: if numeric, parse to int and range-check; otherwise accept
      labels low/medium/high (case-insensitive) and normalize to lowercase.
    """
    # Fast path: real integers
    if isinstance(value, bool):  # bool is int subclass; keep legacy behavior
        iv = int(value)
        if iv < MIN_INTENSITY or iv > MAX_INTENSITY:
            raise ValueError(
                f"Trait '{trait}' has intensity {iv} outside [{MIN_INTENSITY}, {MAX_INTENSITY}]."
            )
        return iv
    if isinstance(value, int):
        if value < MIN_INTENSITY or value > MAX_INTENSITY:
            raise ValueError(
                f"Trait '{trait}' has intensity {value} outside [{MIN_INTENSITY}, {MAX_INTENSITY}]."
            )
        return value
    if isinstance(value, (str, bytes)):
        raw = str(value).strip()
        # Try numeric
        try:
            iv = int(raw)
        except Exception as err:
            lv = raw.lower()
            if lv not in ALLOWED_LEVELS:
                allowed = ", ".join(ALLOWED_LEVELS)
                message = (
                    f"Trait '{trait}' has invalid level {value!r}. Expected one of: {allowed} "
                    f"or an integer in [{MIN_INTENSITY}, {MAX_INTENSITY}]."
                )
                raise ValueError(message) from err
            return lv
        else:
            if iv < MIN_INTENSITY or iv > MAX_INTENSITY:
                message = (
                    f"Trait '{trait}' has intensity {iv} outside "
                    f"[{MIN_INTENSITY}, {MAX_INTENSITY}]."
                )
                raise ValueError(message)
            return iv
    # Other types unsupported
    raise TypeError(f"Trait '{trait}' has unsupported level type {type(value).__name__!s}.")


def _normalize_trait_levels(
    traits: dict[str, list[int | str]],
) -> Iterable[tuple[str, int | str]]:
    """Return an iterator over valid ``(trait, level)`` pairs (int or label)."""
    return (
        (trait, _coerce_trait_value(trait, lvl))
        for trait, levels in traits.items()
        for lvl in levels
    )


def _normalize_trait_levels_map(traits: dict[str, list[int | str]]) -> dict[str, list[int | str]]:
    """Return an ordered mapping of trait -> list[int|str] with validated levels.

    Preserves insertion order of both trait names and their level lists.
    """
    result: dict[str, list[int | str]] = {}
    for trait, levels in traits.items():
        result[trait] = [_coerce_trait_value(trait, lvl) for lvl in levels]
    return result


def _validate_age_ranges(values: Iterable[str]) -> list[str]:
    """Ensure all provided age buckets are allowed and return them as a list."""
    normalized: list[str] = []
    allowed = set(ALLOWED_AGE_RANGES)
    for value in values:
        if not isinstance(value, str):
            raise TypeError("Age ranges must be provided as strings.")
        if value not in allowed:
            allowed_str = ", ".join(ALLOWED_AGE_RANGES)
            raise ValueError(f"Age range '{value}' is unsupported. Expected one of: {allowed_str}.")
        normalized.append(value)
    return normalized


def _validate_occupations(values: Iterable[str]) -> list[str]:
    """Ensure occupations align with the approved taxonomy and return them."""
    normalized: list[str] = []
    allowed = set(ALLOWED_OCCUPATIONS)
    for value in values:
        if not isinstance(value, str):
            raise TypeError("Occupations must be provided as strings.")
        if value not in allowed:
            allowed_str = ", ".join(ALLOWED_OCCUPATIONS)
            raise ValueError(
                f"Occupation '{value}' is unsupported. Expected one of: {allowed_str}."
            )
        normalized.append(value)
    return normalized


def _retired_age_is_disallowed(*, age: str | None, occupation: str | None) -> bool:
    """Return True when a retired occupation is paired with an under-35-44 age."""
    if occupation != "Retired" or age is None:
        return False
    index = _AGE_INDEX.get(age)
    if index is None:
        return False
    return index < _MIN_RETIREMENT_INDEX


@dataclass
class TraitMixConfigFactory:
    """Helper factory to construct a validated TraitMixConfig from loose input."""

    @staticmethod
    def get_str_list(data: Mapping[str, object], key: str) -> list[str]:
        """Return ``data[key]`` if it is a list[str]; else []."""
        value = data.get(key)
        if isinstance(value, list) and all(isinstance(x, str) for x in value):
            return list(value)
        return []

    @staticmethod
    def get_age_ranges(data: Mapping[str, object], key: str) -> list[str]:
        """Validate and return age ranges if provided; else []."""
        value = data.get(key)
        if not isinstance(value, list):
            return []
        return _validate_age_ranges(value)

    @staticmethod
    def get_occupations(data: Mapping[str, object], key: str) -> list[str]:
        """Validate and return occupations if provided; else []."""
        value = data.get(key)
        if value is None:
            return []
        if not isinstance(value, list):
            raise TypeError("occupations must be provided as a list of strings.")
        return _validate_occupations(value)

    @staticmethod
    def get_tasks(data: Mapping[str, object]) -> list[str]:
        """Return normalized list of tasks (singular/plural) from ``data``."""
        tasks: list[str] = []

        raw_tasks = data.get("tasks")
        if isinstance(raw_tasks, list):
            for item in raw_tasks:
                if isinstance(item, (str, bytes)):
                    stripped = str(item).strip()
                    if stripped:
                        tasks.append(stripped)

        raw_task = data.get("task")
        if isinstance(raw_task, (str, bytes)):
            stripped = str(raw_task).strip()
            if stripped:
                tasks.append(stripped)

        return tasks

    @staticmethod
    def get_traits(data: Mapping[str, object]) -> dict[str, list[int | str]]:
        """Return normalized trait->levels mapping from a loose input mapping.

        Accepts ints 0, 1, or 2 and labels ("low", "medium", "high").
        """
        raw = data.get("traits")
        if not isinstance(raw, dict):
            return {}

        traits: dict[str, list[int | str]] = {}
        for k, v in raw.items():
            if not isinstance(k, str):
                continue
            if not isinstance(v, list):
                continue

            traits[k] = v
        return _normalize_trait_levels_map(traits)

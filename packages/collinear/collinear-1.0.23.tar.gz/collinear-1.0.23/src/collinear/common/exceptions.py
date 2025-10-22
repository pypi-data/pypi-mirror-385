"""SDK domain exception types used across modules.

These classes exist to decouple higher-level orchestration from transport-
level errors, while preserving the current public surface via aliases in
SimulationRunner for backward compatibility in tests/imports.
"""

from __future__ import annotations


class UnauthorizedError(RuntimeError):
    """401 Unauthorized from the Steering API (TraitMix).

    The message should avoid leaking full secrets. Callers may log a masked
    key preview separately.
    """


class InvalidTraitError(RuntimeError):
    """Raised when the Steering API signals unknown/unsupported trait(s)."""

    def __init__(self, trait: str | None = None) -> None:
        """Store the offending trait name when provided."""
        super().__init__(trait or "invalid trait")
        self.trait = trait


class TransportError(RuntimeError):
    """Non-2xx transport or JSON parsing failure when calling Steering API."""


class BuildConversationError(RuntimeError):
    """Raised when building a conversation fails during simulation.

    Carries metadata about how many user turns were completed before failure,
    and whether the failure was due to an invalid trait.
    """

    def __init__(
        self,
        completed_user_turns: int,
        *,
        invalid_trait: bool = False,
        trait: str | None = None,
    ) -> None:
        """Initialise the exception with progress metadata."""
        super().__init__("Conversation build failed")
        self.completed_user_turns = completed_user_turns
        self.invalid_trait = invalid_trait
        self.trait = trait

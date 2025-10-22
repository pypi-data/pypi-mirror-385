"""Orchestrator for red-team evaluation workflow."""

from __future__ import annotations

from typing import TYPE_CHECKING

from collinear.redteam.client import RedteamClient
from collinear.redteam.client import RedteamHandle
from collinear.redteam.payloads import build_redteam_payload

if TYPE_CHECKING:
    from collinear.redteam.schemas import RedteamConfig


class RedteamOrchestrator:
    """Coordinates red-team evaluation workflow.

    Responsible for:
    - Managing the transport client lifecycle
    - Building API payloads from configuration
    - Initiating evaluations and returning handles for polling
    """

    def __init__(self, *, timeout: float = 30.0) -> None:
        """Initialize the orchestrator.

        Args:
            timeout: HTTP request timeout in seconds

        """
        self.timeout = timeout
        self.client: RedteamClient | None = None

    @property
    def redteam_client(self) -> RedteamClient:
        """Lazy-load the redteam transport client."""
        if self.client is None:
            self.client = RedteamClient(timeout=self.timeout)
        return self.client

    def run(self, config: RedteamConfig) -> RedteamHandle:
        """Execute a red-team evaluation with the given configuration.

        Args:
            config: Validated red-team configuration

        Returns:
            Handle for polling evaluation status and retrieving results

        Raises:
            RuntimeError: If the API does not return an evaluation_id

        """
        payload = build_redteam_payload(config)
        started = self.redteam_client.start(payload)

        eval_id = str(started.get("evaluation_id") or "")
        if not eval_id:
            msg = "SDK redteam evaluate did not return an evaluation_id."
            raise RuntimeError(msg)

        return RedteamHandle(
            api=self.redteam_client,
            evaluation_id=eval_id,
            initial=started,
        )

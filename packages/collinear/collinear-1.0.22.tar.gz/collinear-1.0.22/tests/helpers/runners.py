"""Shared SimulationRunner test doubles."""

from __future__ import annotations

from openai.types.chat import ChatCompletionMessageParam

from collinear.simulate.runner import SimulationRunner


class CaptureRunner(SimulationRunner):
    """SimulationRunner subclass that records TraitMix requests."""

    def __init__(
        self,
        *,
        assistant_model_url: str = "https://example.test",
        assistant_model_api_key: str = "k",
        assistant_model_name: str = "gpt-test",
        collinear_api_key: str = "demo-001",
        assistant_response: str = "assistant",
        traitmix_response: str = "ok",
    ) -> None:
        """Initialize the runner and set capture buffers + canned responses."""
        super().__init__(
            assistant_model_url=assistant_model_url,
            assistant_model_api_key=assistant_model_api_key,
            assistant_model_name=assistant_model_name,
            collinear_api_key=collinear_api_key,
        )
        self.assistant_response = assistant_response
        self.traitmix_response = traitmix_response
        self.captured_headers: list[dict[str, str]] = []
        self.captured_payloads: list[list[dict[str, object]]] = []

    async def call_batch_endpoint(
        self,
        url: str,
        payloads: list[dict[str, object]],
        *,
        headers: dict[str, str],
    ) -> list[str]:
        """Capture payloads/headers and return canned responses."""
        assert url.endswith("steer_batch")
        self.captured_headers.append(headers)
        self.captured_payloads.append(payloads)
        return [self.traitmix_response] * len(payloads)

    async def call_with_retry(
        self,
        messages: list[ChatCompletionMessageParam],
        system_prompt: str,
    ) -> str:
        """Return the canned assistant response."""
        del messages, system_prompt
        return self.assistant_response

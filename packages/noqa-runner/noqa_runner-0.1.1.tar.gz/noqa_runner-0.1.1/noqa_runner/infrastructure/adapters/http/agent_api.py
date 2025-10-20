"""Agent API client using httpx"""

from __future__ import annotations

import httpx

from shared.infrastructure.adapters.http.base_client import BaseHttpClient
from shared.models.state.test_state import TestState
from shared.utils.retry_decorator import with_retry


class AgentApiAdapter(BaseHttpClient):
    """Adapter for Agent API operations"""

    def __init__(self, base_url: str, api_token: str):
        super().__init__(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_token}"},
            timeout=300.0,
            limits=httpx.Limits(
                max_connections=10, max_keepalive_connections=5, keepalive_expiry=30.0
            ),
            http2=True,
        )

    @with_retry(max_attempts=2, exceptions=(httpx.HTTPError,))
    async def prepare_test(self, state: TestState) -> TestState:
        """Prepare test by sending state to agent API"""
        response = await self._post("/v1/agent/preparation", json=state.model_dump())
        response.raise_for_status()
        return TestState(**response.json())

    @with_retry(max_attempts=2, exceptions=(httpx.HTTPError,))
    async def execute_step(self, state: TestState) -> TestState:
        """Execute test step by sending state to agent API"""
        response = await self._post("/v1/agent/step", json=state.model_dump())
        response.raise_for_status()
        return TestState(**response.json())

    @with_retry(max_attempts=2, exceptions=(httpx.HTTPError,))
    async def get_screenshot_urls(
        self, test_id: str, step_number: int
    ) -> tuple[str, str]:
        """Get presigned URLs for screenshot upload

        Returns:
            Tuple of (upload_url, download_url)
        """
        response = await self._get(
            "/v1/agent/screenshot-urls",
            params={"test_id": test_id, "step_number": step_number},
        )
        response.raise_for_status()
        data = response.json()

        return data["upload_url"], data["download_url"]

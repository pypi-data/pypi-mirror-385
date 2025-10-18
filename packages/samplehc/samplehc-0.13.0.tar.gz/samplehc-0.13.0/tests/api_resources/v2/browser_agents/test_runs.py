# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from samplehc import SampleHealthcare, AsyncSampleHealthcare
from tests.utils import assert_matches_type
from samplehc.types.v2.browser_agents import RunListEventsResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRuns:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_events(self, client: SampleHealthcare) -> None:
        run = client.v2.browser_agents.runs.list_events(
            browser_agent_run_id="browserAgentRunId",
        )
        assert_matches_type(RunListEventsResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_events_with_all_params(self, client: SampleHealthcare) -> None:
        run = client.v2.browser_agents.runs.list_events(
            browser_agent_run_id="browserAgentRunId",
            cursor="cursor",
            limit=1,
        )
        assert_matches_type(RunListEventsResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_events(self, client: SampleHealthcare) -> None:
        response = client.v2.browser_agents.runs.with_raw_response.list_events(
            browser_agent_run_id="browserAgentRunId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(RunListEventsResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_events(self, client: SampleHealthcare) -> None:
        with client.v2.browser_agents.runs.with_streaming_response.list_events(
            browser_agent_run_id="browserAgentRunId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = response.parse()
            assert_matches_type(RunListEventsResponse, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_events(self, client: SampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_agent_run_id` but received ''"):
            client.v2.browser_agents.runs.with_raw_response.list_events(
                browser_agent_run_id="",
            )


class TestAsyncRuns:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_events(self, async_client: AsyncSampleHealthcare) -> None:
        run = await async_client.v2.browser_agents.runs.list_events(
            browser_agent_run_id="browserAgentRunId",
        )
        assert_matches_type(RunListEventsResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_events_with_all_params(self, async_client: AsyncSampleHealthcare) -> None:
        run = await async_client.v2.browser_agents.runs.list_events(
            browser_agent_run_id="browserAgentRunId",
            cursor="cursor",
            limit=1,
        )
        assert_matches_type(RunListEventsResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_events(self, async_client: AsyncSampleHealthcare) -> None:
        response = await async_client.v2.browser_agents.runs.with_raw_response.list_events(
            browser_agent_run_id="browserAgentRunId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = await response.parse()
        assert_matches_type(RunListEventsResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_events(self, async_client: AsyncSampleHealthcare) -> None:
        async with async_client.v2.browser_agents.runs.with_streaming_response.list_events(
            browser_agent_run_id="browserAgentRunId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = await response.parse()
            assert_matches_type(RunListEventsResponse, run, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_events(self, async_client: AsyncSampleHealthcare) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `browser_agent_run_id` but received ''"):
            await async_client.v2.browser_agents.runs.with_raw_response.list_events(
                browser_agent_run_id="",
            )

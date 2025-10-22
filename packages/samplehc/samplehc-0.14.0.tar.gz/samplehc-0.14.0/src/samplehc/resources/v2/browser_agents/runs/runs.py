# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .help_requests import (
    HelpRequestsResource,
    AsyncHelpRequestsResource,
    HelpRequestsResourceWithRawResponse,
    AsyncHelpRequestsResourceWithRawResponse,
    HelpRequestsResourceWithStreamingResponse,
    AsyncHelpRequestsResourceWithStreamingResponse,
)
from ....._base_client import make_request_options
from .....types.v2.browser_agents import run_list_events_params
from .....types.v2.browser_agents.run_list_events_response import RunListEventsResponse

__all__ = ["RunsResource", "AsyncRunsResource"]


class RunsResource(SyncAPIResource):
    @cached_property
    def help_requests(self) -> HelpRequestsResource:
        return HelpRequestsResource(self._client)

    @cached_property
    def with_raw_response(self) -> RunsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return RunsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RunsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return RunsResourceWithStreamingResponse(self)

    def list_events(
        self,
        browser_agent_run_id: str,
        *,
        cursor: str | Omit = omit,
        limit: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RunListEventsResponse:
        """
        Get events for a browser agent run.

        Args:
          cursor: Cursor from previous page

          limit: Maximum number of events to return

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_agent_run_id:
            raise ValueError(
                f"Expected a non-empty value for `browser_agent_run_id` but received {browser_agent_run_id!r}"
            )
        return self._get(
            f"/api/v2/browser-agents/runs/{browser_agent_run_id}/events",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "cursor": cursor,
                        "limit": limit,
                    },
                    run_list_events_params.RunListEventsParams,
                ),
            ),
            cast_to=RunListEventsResponse,
        )


class AsyncRunsResource(AsyncAPIResource):
    @cached_property
    def help_requests(self) -> AsyncHelpRequestsResource:
        return AsyncHelpRequestsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncRunsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRunsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRunsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncRunsResourceWithStreamingResponse(self)

    async def list_events(
        self,
        browser_agent_run_id: str,
        *,
        cursor: str | Omit = omit,
        limit: float | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RunListEventsResponse:
        """
        Get events for a browser agent run.

        Args:
          cursor: Cursor from previous page

          limit: Maximum number of events to return

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not browser_agent_run_id:
            raise ValueError(
                f"Expected a non-empty value for `browser_agent_run_id` but received {browser_agent_run_id!r}"
            )
        return await self._get(
            f"/api/v2/browser-agents/runs/{browser_agent_run_id}/events",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "cursor": cursor,
                        "limit": limit,
                    },
                    run_list_events_params.RunListEventsParams,
                ),
            ),
            cast_to=RunListEventsResponse,
        )


class RunsResourceWithRawResponse:
    def __init__(self, runs: RunsResource) -> None:
        self._runs = runs

        self.list_events = to_raw_response_wrapper(
            runs.list_events,
        )

    @cached_property
    def help_requests(self) -> HelpRequestsResourceWithRawResponse:
        return HelpRequestsResourceWithRawResponse(self._runs.help_requests)


class AsyncRunsResourceWithRawResponse:
    def __init__(self, runs: AsyncRunsResource) -> None:
        self._runs = runs

        self.list_events = async_to_raw_response_wrapper(
            runs.list_events,
        )

    @cached_property
    def help_requests(self) -> AsyncHelpRequestsResourceWithRawResponse:
        return AsyncHelpRequestsResourceWithRawResponse(self._runs.help_requests)


class RunsResourceWithStreamingResponse:
    def __init__(self, runs: RunsResource) -> None:
        self._runs = runs

        self.list_events = to_streamed_response_wrapper(
            runs.list_events,
        )

    @cached_property
    def help_requests(self) -> HelpRequestsResourceWithStreamingResponse:
        return HelpRequestsResourceWithStreamingResponse(self._runs.help_requests)


class AsyncRunsResourceWithStreamingResponse:
    def __init__(self, runs: AsyncRunsResource) -> None:
        self._runs = runs

        self.list_events = async_to_streamed_response_wrapper(
            runs.list_events,
        )

    @cached_property
    def help_requests(self) -> AsyncHelpRequestsResourceWithStreamingResponse:
        return AsyncHelpRequestsResourceWithStreamingResponse(self._runs.help_requests)

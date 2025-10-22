# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import Body, Query, Headers, NotGiven, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.v2.integrations import snowflake_query_params
from ....types.v2.integrations.snowflake_query_response import SnowflakeQueryResponse

__all__ = ["SnowflakeResource", "AsyncSnowflakeResource"]


class SnowflakeResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SnowflakeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return SnowflakeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SnowflakeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return SnowflakeResourceWithStreamingResponse(self)

    def query(
        self,
        slug: str,
        *,
        query: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SnowflakeQueryResponse:
        """
        Execute a query against a configured Snowflake instance.

        Args:
          query: The SQL query to execute.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return self._post(
            f"/api/v2/integrations/snowflake/{slug}/query",
            body=maybe_transform({"query": query}, snowflake_query_params.SnowflakeQueryParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SnowflakeQueryResponse,
        )


class AsyncSnowflakeResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSnowflakeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/samplehc/samplehc-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSnowflakeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSnowflakeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/samplehc/samplehc-python#with_streaming_response
        """
        return AsyncSnowflakeResourceWithStreamingResponse(self)

    async def query(
        self,
        slug: str,
        *,
        query: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SnowflakeQueryResponse:
        """
        Execute a query against a configured Snowflake instance.

        Args:
          query: The SQL query to execute.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not slug:
            raise ValueError(f"Expected a non-empty value for `slug` but received {slug!r}")
        return await self._post(
            f"/api/v2/integrations/snowflake/{slug}/query",
            body=await async_maybe_transform({"query": query}, snowflake_query_params.SnowflakeQueryParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SnowflakeQueryResponse,
        )


class SnowflakeResourceWithRawResponse:
    def __init__(self, snowflake: SnowflakeResource) -> None:
        self._snowflake = snowflake

        self.query = to_raw_response_wrapper(
            snowflake.query,
        )


class AsyncSnowflakeResourceWithRawResponse:
    def __init__(self, snowflake: AsyncSnowflakeResource) -> None:
        self._snowflake = snowflake

        self.query = async_to_raw_response_wrapper(
            snowflake.query,
        )


class SnowflakeResourceWithStreamingResponse:
    def __init__(self, snowflake: SnowflakeResource) -> None:
        self._snowflake = snowflake

        self.query = to_streamed_response_wrapper(
            snowflake.query,
        )


class AsyncSnowflakeResourceWithStreamingResponse:
    def __init__(self, snowflake: AsyncSnowflakeResource) -> None:
        self._snowflake = snowflake

        self.query = async_to_streamed_response_wrapper(
            snowflake.query,
        )

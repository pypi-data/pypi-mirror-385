# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import Body, Query, Headers, NotGiven, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.sessions import context_report_usage_params
from ...types.sessions.session_context_usage import SessionContextUsage
from ...types.sessions.context_report_usage_response import ContextReportUsageResponse

__all__ = ["ContextResource", "AsyncContextResource"]


class ContextResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ContextResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#accessing-raw-response-data-eg-headers
        """
        return ContextResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ContextResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#with_streaming_response
        """
        return ContextResourceWithStreamingResponse(self)

    def clear(
        self,
        name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionContextUsage:
        """
        Clear context (set new cutoff)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._post(
            f"/sessions/{name}/context/clear",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionContextUsage,
        )

    def compact(
        self,
        name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionContextUsage:
        """
        Compact context (summarize)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._post(
            f"/sessions/{name}/context/compact",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionContextUsage,
        )

    def get_usage(
        self,
        name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionContextUsage:
        """
        Get context usage

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._get(
            f"/sessions/{name}/context",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionContextUsage,
        )

    def report_usage(
        self,
        name: str,
        *,
        tokens: int,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ContextReportUsageResponse:
        """
        Report latest context length (tokens)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._post(
            f"/sessions/{name}/context/usage",
            body=maybe_transform({"tokens": tokens}, context_report_usage_params.ContextReportUsageParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ContextReportUsageResponse,
        )


class AsyncContextResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncContextResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncContextResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncContextResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#with_streaming_response
        """
        return AsyncContextResourceWithStreamingResponse(self)

    async def clear(
        self,
        name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionContextUsage:
        """
        Clear context (set new cutoff)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return await self._post(
            f"/sessions/{name}/context/clear",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionContextUsage,
        )

    async def compact(
        self,
        name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionContextUsage:
        """
        Compact context (summarize)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return await self._post(
            f"/sessions/{name}/context/compact",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionContextUsage,
        )

    async def get_usage(
        self,
        name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionContextUsage:
        """
        Get context usage

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return await self._get(
            f"/sessions/{name}/context",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionContextUsage,
        )

    async def report_usage(
        self,
        name: str,
        *,
        tokens: int,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ContextReportUsageResponse:
        """
        Report latest context length (tokens)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return await self._post(
            f"/sessions/{name}/context/usage",
            body=await async_maybe_transform({"tokens": tokens}, context_report_usage_params.ContextReportUsageParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ContextReportUsageResponse,
        )


class ContextResourceWithRawResponse:
    def __init__(self, context: ContextResource) -> None:
        self._context = context

        self.clear = to_raw_response_wrapper(
            context.clear,
        )
        self.compact = to_raw_response_wrapper(
            context.compact,
        )
        self.get_usage = to_raw_response_wrapper(
            context.get_usage,
        )
        self.report_usage = to_raw_response_wrapper(
            context.report_usage,
        )


class AsyncContextResourceWithRawResponse:
    def __init__(self, context: AsyncContextResource) -> None:
        self._context = context

        self.clear = async_to_raw_response_wrapper(
            context.clear,
        )
        self.compact = async_to_raw_response_wrapper(
            context.compact,
        )
        self.get_usage = async_to_raw_response_wrapper(
            context.get_usage,
        )
        self.report_usage = async_to_raw_response_wrapper(
            context.report_usage,
        )


class ContextResourceWithStreamingResponse:
    def __init__(self, context: ContextResource) -> None:
        self._context = context

        self.clear = to_streamed_response_wrapper(
            context.clear,
        )
        self.compact = to_streamed_response_wrapper(
            context.compact,
        )
        self.get_usage = to_streamed_response_wrapper(
            context.get_usage,
        )
        self.report_usage = to_streamed_response_wrapper(
            context.report_usage,
        )


class AsyncContextResourceWithStreamingResponse:
    def __init__(self, context: AsyncContextResource) -> None:
        self._context = context

        self.clear = async_to_streamed_response_wrapper(
            context.clear,
        )
        self.compact = async_to_streamed_response_wrapper(
            context.compact,
        )
        self.get_usage = async_to_streamed_response_wrapper(
            context.get_usage,
        )
        self.report_usage = async_to_streamed_response_wrapper(
            context.report_usage,
        )

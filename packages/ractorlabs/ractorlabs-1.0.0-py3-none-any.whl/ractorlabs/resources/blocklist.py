# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal

import httpx

from ..types import blocklist_block_params, blocklist_unblock_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.blocklist_list_response import BlocklistListResponse
from ..types.blocklist_block_response import BlocklistBlockResponse
from ..types.blocklist_unblock_response import BlocklistUnblockResponse

__all__ = ["BlocklistResource", "AsyncBlocklistResource"]


class BlocklistResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> BlocklistResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#accessing-raw-response-data-eg-headers
        """
        return BlocklistResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> BlocklistResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#with_streaming_response
        """
        return BlocklistResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BlocklistListResponse:
        """List blocked principals (admin)"""
        return self._get(
            "/blocklist",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BlocklistListResponse,
        )

    def block(
        self,
        *,
        principal: str,
        type: Optional[Literal["User", "Admin"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BlocklistBlockResponse:
        """
        Block a principal (admin)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/blocklist/block",
            body=maybe_transform(
                {
                    "principal": principal,
                    "type": type,
                },
                blocklist_block_params.BlocklistBlockParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BlocklistBlockResponse,
        )

    def unblock(
        self,
        *,
        principal: str,
        type: Optional[Literal["User", "Admin"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BlocklistUnblockResponse:
        """
        Unblock a principal (admin)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/blocklist/unblock",
            body=maybe_transform(
                {
                    "principal": principal,
                    "type": type,
                },
                blocklist_unblock_params.BlocklistUnblockParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BlocklistUnblockResponse,
        )


class AsyncBlocklistResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncBlocklistResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncBlocklistResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncBlocklistResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#with_streaming_response
        """
        return AsyncBlocklistResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BlocklistListResponse:
        """List blocked principals (admin)"""
        return await self._get(
            "/blocklist",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BlocklistListResponse,
        )

    async def block(
        self,
        *,
        principal: str,
        type: Optional[Literal["User", "Admin"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BlocklistBlockResponse:
        """
        Block a principal (admin)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/blocklist/block",
            body=await async_maybe_transform(
                {
                    "principal": principal,
                    "type": type,
                },
                blocklist_block_params.BlocklistBlockParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BlocklistBlockResponse,
        )

    async def unblock(
        self,
        *,
        principal: str,
        type: Optional[Literal["User", "Admin"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BlocklistUnblockResponse:
        """
        Unblock a principal (admin)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/blocklist/unblock",
            body=await async_maybe_transform(
                {
                    "principal": principal,
                    "type": type,
                },
                blocklist_unblock_params.BlocklistUnblockParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BlocklistUnblockResponse,
        )


class BlocklistResourceWithRawResponse:
    def __init__(self, blocklist: BlocklistResource) -> None:
        self._blocklist = blocklist

        self.list = to_raw_response_wrapper(
            blocklist.list,
        )
        self.block = to_raw_response_wrapper(
            blocklist.block,
        )
        self.unblock = to_raw_response_wrapper(
            blocklist.unblock,
        )


class AsyncBlocklistResourceWithRawResponse:
    def __init__(self, blocklist: AsyncBlocklistResource) -> None:
        self._blocklist = blocklist

        self.list = async_to_raw_response_wrapper(
            blocklist.list,
        )
        self.block = async_to_raw_response_wrapper(
            blocklist.block,
        )
        self.unblock = async_to_raw_response_wrapper(
            blocklist.unblock,
        )


class BlocklistResourceWithStreamingResponse:
    def __init__(self, blocklist: BlocklistResource) -> None:
        self._blocklist = blocklist

        self.list = to_streamed_response_wrapper(
            blocklist.list,
        )
        self.block = to_streamed_response_wrapper(
            blocklist.block,
        )
        self.unblock = to_streamed_response_wrapper(
            blocklist.unblock,
        )


class AsyncBlocklistResourceWithStreamingResponse:
    def __init__(self, blocklist: AsyncBlocklistResource) -> None:
        self._blocklist = blocklist

        self.list = async_to_streamed_response_wrapper(
            blocklist.list,
        )
        self.block = async_to_streamed_response_wrapper(
            blocklist.block,
        )
        self.unblock = async_to_streamed_response_wrapper(
            blocklist.unblock,
        )

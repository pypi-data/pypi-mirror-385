# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal

import httpx

from ..types import auth_create_token_params
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
from ..types.login_response import LoginResponse
from ..types.auth_retrieve_current_principal_response import AuthRetrieveCurrentPrincipalResponse

__all__ = ["AuthResource", "AsyncAuthResource"]


class AuthResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AuthResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AuthResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AuthResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#with_streaming_response
        """
        return AuthResourceWithStreamingResponse(self)

    def create_token(
        self,
        *,
        principal: str,
        type: Literal["User", "Admin"],
        ttl_hours: Optional[int] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> LoginResponse:
        """
        Create token for a principal (admin only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/auth/token",
            body=maybe_transform(
                {
                    "principal": principal,
                    "type": type,
                    "ttl_hours": ttl_hours,
                },
                auth_create_token_params.AuthCreateTokenParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LoginResponse,
        )

    def retrieve_current_principal(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AuthRetrieveCurrentPrincipalResponse:
        """Current principal"""
        return self._get(
            "/auth",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuthRetrieveCurrentPrincipalResponse,
        )


class AsyncAuthResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAuthResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAuthResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAuthResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#with_streaming_response
        """
        return AsyncAuthResourceWithStreamingResponse(self)

    async def create_token(
        self,
        *,
        principal: str,
        type: Literal["User", "Admin"],
        ttl_hours: Optional[int] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> LoginResponse:
        """
        Create token for a principal (admin only)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/auth/token",
            body=await async_maybe_transform(
                {
                    "principal": principal,
                    "type": type,
                    "ttl_hours": ttl_hours,
                },
                auth_create_token_params.AuthCreateTokenParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LoginResponse,
        )

    async def retrieve_current_principal(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AuthRetrieveCurrentPrincipalResponse:
        """Current principal"""
        return await self._get(
            "/auth",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AuthRetrieveCurrentPrincipalResponse,
        )


class AuthResourceWithRawResponse:
    def __init__(self, auth: AuthResource) -> None:
        self._auth = auth

        self.create_token = to_raw_response_wrapper(
            auth.create_token,
        )
        self.retrieve_current_principal = to_raw_response_wrapper(
            auth.retrieve_current_principal,
        )


class AsyncAuthResourceWithRawResponse:
    def __init__(self, auth: AsyncAuthResource) -> None:
        self._auth = auth

        self.create_token = async_to_raw_response_wrapper(
            auth.create_token,
        )
        self.retrieve_current_principal = async_to_raw_response_wrapper(
            auth.retrieve_current_principal,
        )


class AuthResourceWithStreamingResponse:
    def __init__(self, auth: AuthResource) -> None:
        self._auth = auth

        self.create_token = to_streamed_response_wrapper(
            auth.create_token,
        )
        self.retrieve_current_principal = to_streamed_response_wrapper(
            auth.retrieve_current_principal,
        )


class AsyncAuthResourceWithStreamingResponse:
    def __init__(self, auth: AsyncAuthResource) -> None:
        self._auth = auth

        self.create_token = async_to_streamed_response_wrapper(
            auth.create_token,
        )
        self.retrieve_current_principal = async_to_streamed_response_wrapper(
            auth.retrieve_current_principal,
        )

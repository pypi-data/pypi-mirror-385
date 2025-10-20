# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..types import (
    operator_login_params,
    operator_create_params,
    operator_update_params,
    operator_update_password_params,
)
from .._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
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
from ..types.operator import Operator
from ..types.login_response import LoginResponse
from ..types.operator_list_response import OperatorListResponse

__all__ = ["OperatorsResource", "AsyncOperatorsResource"]


class OperatorsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OperatorsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#accessing-raw-response-data-eg-headers
        """
        return OperatorsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OperatorsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#with_streaming_response
        """
        return OperatorsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        pass_: str,
        user: str,
        description: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Operator:
        """
        Create operator (admin)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/operators",
            body=maybe_transform(
                {
                    "pass_": pass_,
                    "user": user,
                    "description": description,
                },
                operator_create_params.OperatorCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Operator,
        )

    def retrieve(
        self,
        name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Operator:
        """
        Get operator (self or admin)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._get(
            f"/operators/{name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Operator,
        )

    def update(
        self,
        name: str,
        *,
        active: Optional[bool] | Omit = omit,
        description: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Operator:
        """
        Update operator (admin)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._put(
            f"/operators/{name}",
            body=maybe_transform(
                {
                    "active": active,
                    "description": description,
                },
                operator_update_params.OperatorUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Operator,
        )

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OperatorListResponse:
        """List operators (admin sees all; others see self)"""
        return self._get(
            "/operators",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OperatorListResponse,
        )

    def delete(
        self,
        name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete operator (admin)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/operators/{name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def login(
        self,
        name: str,
        *,
        pass_: str,
        ttl_hours: Optional[int] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> LoginResponse:
        """
        Operator login (password)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._post(
            f"/operators/{name}/login",
            body=maybe_transform(
                {
                    "pass_": pass_,
                    "ttl_hours": ttl_hours,
                },
                operator_login_params.OperatorLoginParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LoginResponse,
        )

    def update_password(
        self,
        name: str,
        *,
        current_password: str,
        new_password: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Update own password (or admin)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._put(
            f"/operators/{name}/password",
            body=maybe_transform(
                {
                    "current_password": current_password,
                    "new_password": new_password,
                },
                operator_update_password_params.OperatorUpdatePasswordParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncOperatorsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOperatorsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncOperatorsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOperatorsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#with_streaming_response
        """
        return AsyncOperatorsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        pass_: str,
        user: str,
        description: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Operator:
        """
        Create operator (admin)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/operators",
            body=await async_maybe_transform(
                {
                    "pass_": pass_,
                    "user": user,
                    "description": description,
                },
                operator_create_params.OperatorCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Operator,
        )

    async def retrieve(
        self,
        name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Operator:
        """
        Get operator (self or admin)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return await self._get(
            f"/operators/{name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Operator,
        )

    async def update(
        self,
        name: str,
        *,
        active: Optional[bool] | Omit = omit,
        description: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Operator:
        """
        Update operator (admin)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return await self._put(
            f"/operators/{name}",
            body=await async_maybe_transform(
                {
                    "active": active,
                    "description": description,
                },
                operator_update_params.OperatorUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Operator,
        )

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OperatorListResponse:
        """List operators (admin sees all; others see self)"""
        return await self._get(
            "/operators",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OperatorListResponse,
        )

    async def delete(
        self,
        name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete operator (admin)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/operators/{name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def login(
        self,
        name: str,
        *,
        pass_: str,
        ttl_hours: Optional[int] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> LoginResponse:
        """
        Operator login (password)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return await self._post(
            f"/operators/{name}/login",
            body=await async_maybe_transform(
                {
                    "pass_": pass_,
                    "ttl_hours": ttl_hours,
                },
                operator_login_params.OperatorLoginParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LoginResponse,
        )

    async def update_password(
        self,
        name: str,
        *,
        current_password: str,
        new_password: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Update own password (or admin)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._put(
            f"/operators/{name}/password",
            body=await async_maybe_transform(
                {
                    "current_password": current_password,
                    "new_password": new_password,
                },
                operator_update_password_params.OperatorUpdatePasswordParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class OperatorsResourceWithRawResponse:
    def __init__(self, operators: OperatorsResource) -> None:
        self._operators = operators

        self.create = to_raw_response_wrapper(
            operators.create,
        )
        self.retrieve = to_raw_response_wrapper(
            operators.retrieve,
        )
        self.update = to_raw_response_wrapper(
            operators.update,
        )
        self.list = to_raw_response_wrapper(
            operators.list,
        )
        self.delete = to_raw_response_wrapper(
            operators.delete,
        )
        self.login = to_raw_response_wrapper(
            operators.login,
        )
        self.update_password = to_raw_response_wrapper(
            operators.update_password,
        )


class AsyncOperatorsResourceWithRawResponse:
    def __init__(self, operators: AsyncOperatorsResource) -> None:
        self._operators = operators

        self.create = async_to_raw_response_wrapper(
            operators.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            operators.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            operators.update,
        )
        self.list = async_to_raw_response_wrapper(
            operators.list,
        )
        self.delete = async_to_raw_response_wrapper(
            operators.delete,
        )
        self.login = async_to_raw_response_wrapper(
            operators.login,
        )
        self.update_password = async_to_raw_response_wrapper(
            operators.update_password,
        )


class OperatorsResourceWithStreamingResponse:
    def __init__(self, operators: OperatorsResource) -> None:
        self._operators = operators

        self.create = to_streamed_response_wrapper(
            operators.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            operators.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            operators.update,
        )
        self.list = to_streamed_response_wrapper(
            operators.list,
        )
        self.delete = to_streamed_response_wrapper(
            operators.delete,
        )
        self.login = to_streamed_response_wrapper(
            operators.login,
        )
        self.update_password = to_streamed_response_wrapper(
            operators.update_password,
        )


class AsyncOperatorsResourceWithStreamingResponse:
    def __init__(self, operators: AsyncOperatorsResource) -> None:
        self._operators = operators

        self.create = async_to_streamed_response_wrapper(
            operators.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            operators.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            operators.update,
        )
        self.list = async_to_streamed_response_wrapper(
            operators.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            operators.delete,
        )
        self.login = async_to_streamed_response_wrapper(
            operators.login,
        )
        self.update_password = async_to_streamed_response_wrapper(
            operators.update_password,
        )

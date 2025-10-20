# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Optional
from typing_extensions import Literal

import httpx

from ...types import (
    session_list_params,
    session_wake_params,
    session_sleep_params,
    session_branch_params,
    session_create_params,
    session_update_params,
    session_publish_params,
    session_update_state_params,
)
from .context import (
    ContextResource,
    AsyncContextResource,
    ContextResourceWithRawResponse,
    AsyncContextResourceWithRawResponse,
    ContextResourceWithStreamingResponse,
    AsyncContextResourceWithStreamingResponse,
)
from ..._types import Body, Omit, Query, Headers, NoneType, NotGiven, SequenceNotStr, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from .responses import (
    ResponsesResource,
    AsyncResponsesResource,
    ResponsesResourceWithRawResponse,
    AsyncResponsesResourceWithRawResponse,
    ResponsesResourceWithStreamingResponse,
    AsyncResponsesResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .files.files import (
    FilesResource,
    AsyncFilesResource,
    FilesResourceWithRawResponse,
    AsyncFilesResourceWithRawResponse,
    FilesResourceWithStreamingResponse,
    AsyncFilesResourceWithStreamingResponse,
)
from ..._base_client import make_request_options
from ...types.published.session import Session
from ...types.session_list_response import SessionListResponse
from ...types.session_cancel_response import SessionCancelResponse
from ...types.session_mark_busy_response import SessionMarkBusyResponse
from ...types.session_mark_idle_response import SessionMarkIdleResponse
from ...types.session_get_runtime_response import SessionGetRuntimeResponse
from ...types.session_update_state_response import SessionUpdateStateResponse

__all__ = ["SessionsResource", "AsyncSessionsResource"]


class SessionsResource(SyncAPIResource):
    @cached_property
    def context(self) -> ContextResource:
        return ContextResource(self._client)

    @cached_property
    def responses(self) -> ResponsesResource:
        return ResponsesResource(self._client)

    @cached_property
    def files(self) -> FilesResource:
        return FilesResource(self._client)

    @cached_property
    def with_raw_response(self) -> SessionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#accessing-raw-response-data-eg-headers
        """
        return SessionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SessionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#with_streaming_response
        """
        return SessionsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        name: str,
        busy_timeout_seconds: Optional[int] | Omit = omit,
        description: Optional[str] | Omit = omit,
        env: Dict[str, str] | Omit = omit,
        idle_timeout_seconds: Optional[int] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        metadata: object | Omit = omit,
        prompt: Optional[str] | Omit = omit,
        setup: Optional[str] | Omit = omit,
        tags: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Session:
        """
        Create session

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/sessions",
            body=maybe_transform(
                {
                    "name": name,
                    "busy_timeout_seconds": busy_timeout_seconds,
                    "description": description,
                    "env": env,
                    "idle_timeout_seconds": idle_timeout_seconds,
                    "instructions": instructions,
                    "metadata": metadata,
                    "prompt": prompt,
                    "setup": setup,
                    "tags": tags,
                },
                session_create_params.SessionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Session,
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
    ) -> Session:
        """
        Get session by name

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._get(
            f"/sessions/{name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Session,
        )

    def update(
        self,
        name: str,
        *,
        busy_timeout_seconds: Optional[int] | Omit = omit,
        description: Optional[str] | Omit = omit,
        idle_timeout_seconds: Optional[int] | Omit = omit,
        metadata: Optional[object] | Omit = omit,
        tags: Optional[SequenceNotStr[str]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Session:
        """
        Update session metadata/timeouts

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._put(
            f"/sessions/{name}",
            body=maybe_transform(
                {
                    "busy_timeout_seconds": busy_timeout_seconds,
                    "description": description,
                    "idle_timeout_seconds": idle_timeout_seconds,
                    "metadata": metadata,
                    "tags": tags,
                },
                session_update_params.SessionUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Session,
        )

    def list(
        self,
        *,
        limit: int | Omit = omit,
        offset: int | Omit = omit,
        page: int | Omit = omit,
        q: str | Omit = omit,
        state: str | Omit = omit,
        tags: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionListResponse:
        """List sessions (admin all; others own)

        Args:
          tags: Repeatable tag filter.

        Use tags=alpha&tags=beta.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/sessions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "limit": limit,
                        "offset": offset,
                        "page": page,
                        "q": q,
                        "state": state,
                        "tags": tags,
                    },
                    session_list_params.SessionListParams,
                ),
            ),
            cast_to=SessionListResponse,
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
        Delete session

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
            f"/sessions/{name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def branch(
        self,
        path_name: str,
        *,
        body_name: str,
        code: bool | Omit = omit,
        content: bool | Omit = omit,
        env: bool | Omit = omit,
        metadata: Optional[object] | Omit = omit,
        prompt: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Session:
        """
        Branch a session into a new one

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_name:
            raise ValueError(f"Expected a non-empty value for `path_name` but received {path_name!r}")
        return self._post(
            f"/sessions/{path_name}/branch",
            body=maybe_transform(
                {
                    "body_name": body_name,
                    "code": code,
                    "content": content,
                    "env": env,
                    "metadata": metadata,
                    "prompt": prompt,
                },
                session_branch_params.SessionBranchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Session,
        )

    def cancel(
        self,
        name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionCancelResponse:
        """
        Cancel latest in‑progress response and set session idle

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._post(
            f"/sessions/{name}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionCancelResponse,
        )

    def get_runtime(
        self,
        name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionGetRuntimeResponse:
        """
        Total runtime (seconds)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._get(
            f"/sessions/{name}/runtime",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionGetRuntimeResponse,
        )

    def mark_busy(
        self,
        name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionMarkBusyResponse:
        """
        Mark session busy (session container)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._post(
            f"/sessions/{name}/busy",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionMarkBusyResponse,
        )

    def mark_idle(
        self,
        name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionMarkIdleResponse:
        """
        Mark session idle (session container)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._post(
            f"/sessions/{name}/idle",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionMarkIdleResponse,
        )

    def publish(
        self,
        name: str,
        *,
        code: bool | Omit = omit,
        content: bool | Omit = omit,
        env: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Publish session content/env/code (as permitted)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/sessions/{name}/publish",
            body=maybe_transform(
                {
                    "code": code,
                    "content": content,
                    "env": env,
                },
                session_publish_params.SessionPublishParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def sleep(
        self,
        name: str,
        *,
        delay_seconds: int | Omit = omit,
        note: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Session:
        """
        Sleep session (destroy container; keep volume)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._post(
            f"/sessions/{name}/sleep",
            body=maybe_transform(
                {
                    "delay_seconds": delay_seconds,
                    "note": note,
                },
                session_sleep_params.SessionSleepParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Session,
        )

    def unpublish(
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
        Unpublish session content

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/sessions/{name}/unpublish",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def update_state(
        self,
        name: str,
        *,
        state: Literal["init", "idle", "busy", "slept"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionUpdateStateResponse:
        """
        Update session state (internal)

        Args:
          state: New session state

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._put(
            f"/sessions/{name}/state",
            body=maybe_transform({"state": state}, session_update_state_params.SessionUpdateStateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionUpdateStateResponse,
        )

    def wake(
        self,
        name: str,
        *,
        prompt: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Session:
        """
        Wake session (recreate container)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return self._post(
            f"/sessions/{name}/wake",
            body=maybe_transform({"prompt": prompt}, session_wake_params.SessionWakeParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Session,
        )


class AsyncSessionsResource(AsyncAPIResource):
    @cached_property
    def context(self) -> AsyncContextResource:
        return AsyncContextResource(self._client)

    @cached_property
    def responses(self) -> AsyncResponsesResource:
        return AsyncResponsesResource(self._client)

    @cached_property
    def files(self) -> AsyncFilesResource:
        return AsyncFilesResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncSessionsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSessionsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSessionsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#with_streaming_response
        """
        return AsyncSessionsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        name: str,
        busy_timeout_seconds: Optional[int] | Omit = omit,
        description: Optional[str] | Omit = omit,
        env: Dict[str, str] | Omit = omit,
        idle_timeout_seconds: Optional[int] | Omit = omit,
        instructions: Optional[str] | Omit = omit,
        metadata: object | Omit = omit,
        prompt: Optional[str] | Omit = omit,
        setup: Optional[str] | Omit = omit,
        tags: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Session:
        """
        Create session

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/sessions",
            body=await async_maybe_transform(
                {
                    "name": name,
                    "busy_timeout_seconds": busy_timeout_seconds,
                    "description": description,
                    "env": env,
                    "idle_timeout_seconds": idle_timeout_seconds,
                    "instructions": instructions,
                    "metadata": metadata,
                    "prompt": prompt,
                    "setup": setup,
                    "tags": tags,
                },
                session_create_params.SessionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Session,
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
    ) -> Session:
        """
        Get session by name

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return await self._get(
            f"/sessions/{name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Session,
        )

    async def update(
        self,
        name: str,
        *,
        busy_timeout_seconds: Optional[int] | Omit = omit,
        description: Optional[str] | Omit = omit,
        idle_timeout_seconds: Optional[int] | Omit = omit,
        metadata: Optional[object] | Omit = omit,
        tags: Optional[SequenceNotStr[str]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Session:
        """
        Update session metadata/timeouts

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return await self._put(
            f"/sessions/{name}",
            body=await async_maybe_transform(
                {
                    "busy_timeout_seconds": busy_timeout_seconds,
                    "description": description,
                    "idle_timeout_seconds": idle_timeout_seconds,
                    "metadata": metadata,
                    "tags": tags,
                },
                session_update_params.SessionUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Session,
        )

    async def list(
        self,
        *,
        limit: int | Omit = omit,
        offset: int | Omit = omit,
        page: int | Omit = omit,
        q: str | Omit = omit,
        state: str | Omit = omit,
        tags: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionListResponse:
        """List sessions (admin all; others own)

        Args:
          tags: Repeatable tag filter.

        Use tags=alpha&tags=beta.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/sessions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "limit": limit,
                        "offset": offset,
                        "page": page,
                        "q": q,
                        "state": state,
                        "tags": tags,
                    },
                    session_list_params.SessionListParams,
                ),
            ),
            cast_to=SessionListResponse,
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
        Delete session

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
            f"/sessions/{name}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def branch(
        self,
        path_name: str,
        *,
        body_name: str,
        code: bool | Omit = omit,
        content: bool | Omit = omit,
        env: bool | Omit = omit,
        metadata: Optional[object] | Omit = omit,
        prompt: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Session:
        """
        Branch a session into a new one

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not path_name:
            raise ValueError(f"Expected a non-empty value for `path_name` but received {path_name!r}")
        return await self._post(
            f"/sessions/{path_name}/branch",
            body=await async_maybe_transform(
                {
                    "body_name": body_name,
                    "code": code,
                    "content": content,
                    "env": env,
                    "metadata": metadata,
                    "prompt": prompt,
                },
                session_branch_params.SessionBranchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Session,
        )

    async def cancel(
        self,
        name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionCancelResponse:
        """
        Cancel latest in‑progress response and set session idle

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return await self._post(
            f"/sessions/{name}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionCancelResponse,
        )

    async def get_runtime(
        self,
        name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionGetRuntimeResponse:
        """
        Total runtime (seconds)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return await self._get(
            f"/sessions/{name}/runtime",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionGetRuntimeResponse,
        )

    async def mark_busy(
        self,
        name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionMarkBusyResponse:
        """
        Mark session busy (session container)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return await self._post(
            f"/sessions/{name}/busy",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionMarkBusyResponse,
        )

    async def mark_idle(
        self,
        name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionMarkIdleResponse:
        """
        Mark session idle (session container)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return await self._post(
            f"/sessions/{name}/idle",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionMarkIdleResponse,
        )

    async def publish(
        self,
        name: str,
        *,
        code: bool | Omit = omit,
        content: bool | Omit = omit,
        env: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Publish session content/env/code (as permitted)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/sessions/{name}/publish",
            body=await async_maybe_transform(
                {
                    "code": code,
                    "content": content,
                    "env": env,
                },
                session_publish_params.SessionPublishParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def sleep(
        self,
        name: str,
        *,
        delay_seconds: int | Omit = omit,
        note: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Session:
        """
        Sleep session (destroy container; keep volume)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return await self._post(
            f"/sessions/{name}/sleep",
            body=await async_maybe_transform(
                {
                    "delay_seconds": delay_seconds,
                    "note": note,
                },
                session_sleep_params.SessionSleepParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Session,
        )

    async def unpublish(
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
        Unpublish session content

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/sessions/{name}/unpublish",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def update_state(
        self,
        name: str,
        *,
        state: Literal["init", "idle", "busy", "slept"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SessionUpdateStateResponse:
        """
        Update session state (internal)

        Args:
          state: New session state

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return await self._put(
            f"/sessions/{name}/state",
            body=await async_maybe_transform({"state": state}, session_update_state_params.SessionUpdateStateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SessionUpdateStateResponse,
        )

    async def wake(
        self,
        name: str,
        *,
        prompt: Optional[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Session:
        """
        Wake session (recreate container)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not name:
            raise ValueError(f"Expected a non-empty value for `name` but received {name!r}")
        return await self._post(
            f"/sessions/{name}/wake",
            body=await async_maybe_transform({"prompt": prompt}, session_wake_params.SessionWakeParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Session,
        )


class SessionsResourceWithRawResponse:
    def __init__(self, sessions: SessionsResource) -> None:
        self._sessions = sessions

        self.create = to_raw_response_wrapper(
            sessions.create,
        )
        self.retrieve = to_raw_response_wrapper(
            sessions.retrieve,
        )
        self.update = to_raw_response_wrapper(
            sessions.update,
        )
        self.list = to_raw_response_wrapper(
            sessions.list,
        )
        self.delete = to_raw_response_wrapper(
            sessions.delete,
        )
        self.branch = to_raw_response_wrapper(
            sessions.branch,
        )
        self.cancel = to_raw_response_wrapper(
            sessions.cancel,
        )
        self.get_runtime = to_raw_response_wrapper(
            sessions.get_runtime,
        )
        self.mark_busy = to_raw_response_wrapper(
            sessions.mark_busy,
        )
        self.mark_idle = to_raw_response_wrapper(
            sessions.mark_idle,
        )
        self.publish = to_raw_response_wrapper(
            sessions.publish,
        )
        self.sleep = to_raw_response_wrapper(
            sessions.sleep,
        )
        self.unpublish = to_raw_response_wrapper(
            sessions.unpublish,
        )
        self.update_state = to_raw_response_wrapper(
            sessions.update_state,
        )
        self.wake = to_raw_response_wrapper(
            sessions.wake,
        )

    @cached_property
    def context(self) -> ContextResourceWithRawResponse:
        return ContextResourceWithRawResponse(self._sessions.context)

    @cached_property
    def responses(self) -> ResponsesResourceWithRawResponse:
        return ResponsesResourceWithRawResponse(self._sessions.responses)

    @cached_property
    def files(self) -> FilesResourceWithRawResponse:
        return FilesResourceWithRawResponse(self._sessions.files)


class AsyncSessionsResourceWithRawResponse:
    def __init__(self, sessions: AsyncSessionsResource) -> None:
        self._sessions = sessions

        self.create = async_to_raw_response_wrapper(
            sessions.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            sessions.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            sessions.update,
        )
        self.list = async_to_raw_response_wrapper(
            sessions.list,
        )
        self.delete = async_to_raw_response_wrapper(
            sessions.delete,
        )
        self.branch = async_to_raw_response_wrapper(
            sessions.branch,
        )
        self.cancel = async_to_raw_response_wrapper(
            sessions.cancel,
        )
        self.get_runtime = async_to_raw_response_wrapper(
            sessions.get_runtime,
        )
        self.mark_busy = async_to_raw_response_wrapper(
            sessions.mark_busy,
        )
        self.mark_idle = async_to_raw_response_wrapper(
            sessions.mark_idle,
        )
        self.publish = async_to_raw_response_wrapper(
            sessions.publish,
        )
        self.sleep = async_to_raw_response_wrapper(
            sessions.sleep,
        )
        self.unpublish = async_to_raw_response_wrapper(
            sessions.unpublish,
        )
        self.update_state = async_to_raw_response_wrapper(
            sessions.update_state,
        )
        self.wake = async_to_raw_response_wrapper(
            sessions.wake,
        )

    @cached_property
    def context(self) -> AsyncContextResourceWithRawResponse:
        return AsyncContextResourceWithRawResponse(self._sessions.context)

    @cached_property
    def responses(self) -> AsyncResponsesResourceWithRawResponse:
        return AsyncResponsesResourceWithRawResponse(self._sessions.responses)

    @cached_property
    def files(self) -> AsyncFilesResourceWithRawResponse:
        return AsyncFilesResourceWithRawResponse(self._sessions.files)


class SessionsResourceWithStreamingResponse:
    def __init__(self, sessions: SessionsResource) -> None:
        self._sessions = sessions

        self.create = to_streamed_response_wrapper(
            sessions.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            sessions.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            sessions.update,
        )
        self.list = to_streamed_response_wrapper(
            sessions.list,
        )
        self.delete = to_streamed_response_wrapper(
            sessions.delete,
        )
        self.branch = to_streamed_response_wrapper(
            sessions.branch,
        )
        self.cancel = to_streamed_response_wrapper(
            sessions.cancel,
        )
        self.get_runtime = to_streamed_response_wrapper(
            sessions.get_runtime,
        )
        self.mark_busy = to_streamed_response_wrapper(
            sessions.mark_busy,
        )
        self.mark_idle = to_streamed_response_wrapper(
            sessions.mark_idle,
        )
        self.publish = to_streamed_response_wrapper(
            sessions.publish,
        )
        self.sleep = to_streamed_response_wrapper(
            sessions.sleep,
        )
        self.unpublish = to_streamed_response_wrapper(
            sessions.unpublish,
        )
        self.update_state = to_streamed_response_wrapper(
            sessions.update_state,
        )
        self.wake = to_streamed_response_wrapper(
            sessions.wake,
        )

    @cached_property
    def context(self) -> ContextResourceWithStreamingResponse:
        return ContextResourceWithStreamingResponse(self._sessions.context)

    @cached_property
    def responses(self) -> ResponsesResourceWithStreamingResponse:
        return ResponsesResourceWithStreamingResponse(self._sessions.responses)

    @cached_property
    def files(self) -> FilesResourceWithStreamingResponse:
        return FilesResourceWithStreamingResponse(self._sessions.files)


class AsyncSessionsResourceWithStreamingResponse:
    def __init__(self, sessions: AsyncSessionsResource) -> None:
        self._sessions = sessions

        self.create = async_to_streamed_response_wrapper(
            sessions.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            sessions.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            sessions.update,
        )
        self.list = async_to_streamed_response_wrapper(
            sessions.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            sessions.delete,
        )
        self.branch = async_to_streamed_response_wrapper(
            sessions.branch,
        )
        self.cancel = async_to_streamed_response_wrapper(
            sessions.cancel,
        )
        self.get_runtime = async_to_streamed_response_wrapper(
            sessions.get_runtime,
        )
        self.mark_busy = async_to_streamed_response_wrapper(
            sessions.mark_busy,
        )
        self.mark_idle = async_to_streamed_response_wrapper(
            sessions.mark_idle,
        )
        self.publish = async_to_streamed_response_wrapper(
            sessions.publish,
        )
        self.sleep = async_to_streamed_response_wrapper(
            sessions.sleep,
        )
        self.unpublish = async_to_streamed_response_wrapper(
            sessions.unpublish,
        )
        self.update_state = async_to_streamed_response_wrapper(
            sessions.update_state,
        )
        self.wake = async_to_streamed_response_wrapper(
            sessions.wake,
        )

    @cached_property
    def context(self) -> AsyncContextResourceWithStreamingResponse:
        return AsyncContextResourceWithStreamingResponse(self._sessions.context)

    @cached_property
    def responses(self) -> AsyncResponsesResourceWithStreamingResponse:
        return AsyncResponsesResourceWithStreamingResponse(self._sessions.responses)

    @cached_property
    def files(self) -> AsyncFilesResourceWithStreamingResponse:
        return AsyncFilesResourceWithStreamingResponse(self._sessions.files)

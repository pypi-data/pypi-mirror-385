# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from .sessions import (
    SessionsResource,
    AsyncSessionsResource,
    SessionsResourceWithRawResponse,
    AsyncSessionsResourceWithRawResponse,
    SessionsResourceWithStreamingResponse,
    AsyncSessionsResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["PublishedResource", "AsyncPublishedResource"]


class PublishedResource(SyncAPIResource):
    @cached_property
    def sessions(self) -> SessionsResource:
        return SessionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> PublishedResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#accessing-raw-response-data-eg-headers
        """
        return PublishedResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PublishedResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#with_streaming_response
        """
        return PublishedResourceWithStreamingResponse(self)


class AsyncPublishedResource(AsyncAPIResource):
    @cached_property
    def sessions(self) -> AsyncSessionsResource:
        return AsyncSessionsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncPublishedResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPublishedResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPublishedResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/harshapalnati/Ractor-sdk-python#with_streaming_response
        """
        return AsyncPublishedResourceWithStreamingResponse(self)


class PublishedResourceWithRawResponse:
    def __init__(self, published: PublishedResource) -> None:
        self._published = published

    @cached_property
    def sessions(self) -> SessionsResourceWithRawResponse:
        return SessionsResourceWithRawResponse(self._published.sessions)


class AsyncPublishedResourceWithRawResponse:
    def __init__(self, published: AsyncPublishedResource) -> None:
        self._published = published

    @cached_property
    def sessions(self) -> AsyncSessionsResourceWithRawResponse:
        return AsyncSessionsResourceWithRawResponse(self._published.sessions)


class PublishedResourceWithStreamingResponse:
    def __init__(self, published: PublishedResource) -> None:
        self._published = published

    @cached_property
    def sessions(self) -> SessionsResourceWithStreamingResponse:
        return SessionsResourceWithStreamingResponse(self._published.sessions)


class AsyncPublishedResourceWithStreamingResponse:
    def __init__(self, published: AsyncPublishedResource) -> None:
        self._published = published

    @cached_property
    def sessions(self) -> AsyncSessionsResourceWithStreamingResponse:
        return AsyncSessionsResourceWithStreamingResponse(self._published.sessions)

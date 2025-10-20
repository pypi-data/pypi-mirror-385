# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Dict, Mapping, cast
from typing_extensions import Self, Literal, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
    not_given,
)
from ._utils import is_given, get_async_library
from ._version import __version__
from .resources import auth, version, blocklist, operators, responses
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError, RactorlabsError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)
from .resources.sessions import sessions
from .resources.published import published

__all__ = [
    "ENVIRONMENTS",
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "Ractorlabs",
    "AsyncRactorlabs",
    "Client",
    "AsyncClient",
]

ENVIRONMENTS: Dict[str, str] = {
    "production": "http://localhost:9000/api/v0",
    "environment_1": "https://{host}/api/v0",
}


class Ractorlabs(SyncAPIClient):
    version: version.VersionResource
    operators: operators.OperatorsResource
    published: published.PublishedResource
    auth: auth.AuthResource
    blocklist: blocklist.BlocklistResource
    sessions: sessions.SessionsResource
    responses: responses.ResponsesResource
    with_raw_response: RactorlabsWithRawResponse
    with_streaming_response: RactorlabsWithStreamedResponse

    # client options
    api_key: str
    host: str

    _environment: Literal["production", "environment_1"] | NotGiven

    def __init__(
        self,
        *,
        api_key: str | None = None,
        host: str | None = None,
        environment: Literal["production", "environment_1"] | NotGiven = not_given,
        base_url: str | httpx.URL | None | NotGiven = not_given,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Ractorlabs client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `RACTORLABS_API_KEY`
        - `host` from `RACTORLABS_HOST`
        """
        if api_key is None:
            api_key = os.environ.get("RACTORLABS_API_KEY")
        if api_key is None:
            raise RactorlabsError(
                "The api_key client option must be set either by passing api_key to the client or by setting the RACTORLABS_API_KEY environment variable"
            )
        self.api_key = api_key

        if host is None:
            host = os.environ.get("RACTORLABS_HOST") or "api.example.com"
        self.host = host

        self._environment = environment

        base_url_env = os.environ.get("RACTORLABS_BASE_URL")
        if is_given(base_url) and base_url is not None:
            # cast required because mypy doesn't understand the type narrowing
            base_url = cast("str | httpx.URL", base_url)  # pyright: ignore[reportUnnecessaryCast]
        elif is_given(environment):
            if base_url_env and base_url is not None:
                raise ValueError(
                    "Ambiguous URL; The `RACTORLABS_BASE_URL` env var and the `environment` argument are given. If you want to use the environment, you must pass base_url=None",
                )

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc
        elif base_url_env is not None:
            base_url = base_url_env
        else:
            self._environment = environment = "production"

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.version = version.VersionResource(self)
        self.operators = operators.OperatorsResource(self)
        self.published = published.PublishedResource(self)
        self.auth = auth.AuthResource(self)
        self.blocklist = blocklist.BlocklistResource(self)
        self.sessions = sessions.SessionsResource(self)
        self.responses = responses.ResponsesResource(self)
        self.with_raw_response = RactorlabsWithRawResponse(self)
        self.with_streaming_response = RactorlabsWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        host: str | None = None,
        environment: Literal["production", "environment_1"] | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            host=host or self.host,
            base_url=base_url or self.base_url,
            environment=environment or self._environment,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncRactorlabs(AsyncAPIClient):
    version: version.AsyncVersionResource
    operators: operators.AsyncOperatorsResource
    published: published.AsyncPublishedResource
    auth: auth.AsyncAuthResource
    blocklist: blocklist.AsyncBlocklistResource
    sessions: sessions.AsyncSessionsResource
    responses: responses.AsyncResponsesResource
    with_raw_response: AsyncRactorlabsWithRawResponse
    with_streaming_response: AsyncRactorlabsWithStreamedResponse

    # client options
    api_key: str
    host: str

    _environment: Literal["production", "environment_1"] | NotGiven

    def __init__(
        self,
        *,
        api_key: str | None = None,
        host: str | None = None,
        environment: Literal["production", "environment_1"] | NotGiven = not_given,
        base_url: str | httpx.URL | None | NotGiven = not_given,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncRactorlabs client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `RACTORLABS_API_KEY`
        - `host` from `RACTORLABS_HOST`
        """
        if api_key is None:
            api_key = os.environ.get("RACTORLABS_API_KEY")
        if api_key is None:
            raise RactorlabsError(
                "The api_key client option must be set either by passing api_key to the client or by setting the RACTORLABS_API_KEY environment variable"
            )
        self.api_key = api_key

        if host is None:
            host = os.environ.get("RACTORLABS_HOST") or "api.example.com"
        self.host = host

        self._environment = environment

        base_url_env = os.environ.get("RACTORLABS_BASE_URL")
        if is_given(base_url) and base_url is not None:
            # cast required because mypy doesn't understand the type narrowing
            base_url = cast("str | httpx.URL", base_url)  # pyright: ignore[reportUnnecessaryCast]
        elif is_given(environment):
            if base_url_env and base_url is not None:
                raise ValueError(
                    "Ambiguous URL; The `RACTORLABS_BASE_URL` env var and the `environment` argument are given. If you want to use the environment, you must pass base_url=None",
                )

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc
        elif base_url_env is not None:
            base_url = base_url_env
        else:
            self._environment = environment = "production"

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.version = version.AsyncVersionResource(self)
        self.operators = operators.AsyncOperatorsResource(self)
        self.published = published.AsyncPublishedResource(self)
        self.auth = auth.AsyncAuthResource(self)
        self.blocklist = blocklist.AsyncBlocklistResource(self)
        self.sessions = sessions.AsyncSessionsResource(self)
        self.responses = responses.AsyncResponsesResource(self)
        self.with_raw_response = AsyncRactorlabsWithRawResponse(self)
        self.with_streaming_response = AsyncRactorlabsWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": f"Bearer {api_key}"}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        host: str | None = None,
        environment: Literal["production", "environment_1"] | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            host=host or self.host,
            base_url=base_url or self.base_url,
            environment=environment or self._environment,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class RactorlabsWithRawResponse:
    def __init__(self, client: Ractorlabs) -> None:
        self.version = version.VersionResourceWithRawResponse(client.version)
        self.operators = operators.OperatorsResourceWithRawResponse(client.operators)
        self.published = published.PublishedResourceWithRawResponse(client.published)
        self.auth = auth.AuthResourceWithRawResponse(client.auth)
        self.blocklist = blocklist.BlocklistResourceWithRawResponse(client.blocklist)
        self.sessions = sessions.SessionsResourceWithRawResponse(client.sessions)
        self.responses = responses.ResponsesResourceWithRawResponse(client.responses)


class AsyncRactorlabsWithRawResponse:
    def __init__(self, client: AsyncRactorlabs) -> None:
        self.version = version.AsyncVersionResourceWithRawResponse(client.version)
        self.operators = operators.AsyncOperatorsResourceWithRawResponse(client.operators)
        self.published = published.AsyncPublishedResourceWithRawResponse(client.published)
        self.auth = auth.AsyncAuthResourceWithRawResponse(client.auth)
        self.blocklist = blocklist.AsyncBlocklistResourceWithRawResponse(client.blocklist)
        self.sessions = sessions.AsyncSessionsResourceWithRawResponse(client.sessions)
        self.responses = responses.AsyncResponsesResourceWithRawResponse(client.responses)


class RactorlabsWithStreamedResponse:
    def __init__(self, client: Ractorlabs) -> None:
        self.version = version.VersionResourceWithStreamingResponse(client.version)
        self.operators = operators.OperatorsResourceWithStreamingResponse(client.operators)
        self.published = published.PublishedResourceWithStreamingResponse(client.published)
        self.auth = auth.AuthResourceWithStreamingResponse(client.auth)
        self.blocklist = blocklist.BlocklistResourceWithStreamingResponse(client.blocklist)
        self.sessions = sessions.SessionsResourceWithStreamingResponse(client.sessions)
        self.responses = responses.ResponsesResourceWithStreamingResponse(client.responses)


class AsyncRactorlabsWithStreamedResponse:
    def __init__(self, client: AsyncRactorlabs) -> None:
        self.version = version.AsyncVersionResourceWithStreamingResponse(client.version)
        self.operators = operators.AsyncOperatorsResourceWithStreamingResponse(client.operators)
        self.published = published.AsyncPublishedResourceWithStreamingResponse(client.published)
        self.auth = auth.AsyncAuthResourceWithStreamingResponse(client.auth)
        self.blocklist = blocklist.AsyncBlocklistResourceWithStreamingResponse(client.blocklist)
        self.sessions = sessions.AsyncSessionsResourceWithStreamingResponse(client.sessions)
        self.responses = responses.AsyncResponsesResourceWithStreamingResponse(client.responses)


Client = Ractorlabs

AsyncClient = AsyncRactorlabs

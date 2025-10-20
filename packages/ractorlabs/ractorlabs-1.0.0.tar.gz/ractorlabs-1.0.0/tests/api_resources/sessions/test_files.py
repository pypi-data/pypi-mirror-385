# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter

from ractorlabs import Ractorlabs, AsyncRactorlabs
from tests.utils import assert_matches_type
from ractorlabs._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
)
from ractorlabs.types.sessions import FileDeleteResponse, FileGetMetadataResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFiles:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Ractorlabs) -> None:
        file = client.sessions.files.delete(
            path="path",
            name="name",
        )
        assert_matches_type(FileDeleteResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Ractorlabs) -> None:
        response = client.sessions.files.with_raw_response.delete(
            path="path",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileDeleteResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Ractorlabs) -> None:
        with client.sessions.files.with_streaming_response.delete(
            path="path",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(FileDeleteResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.files.with_raw_response.delete(
                path="path",
                name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path` but received ''"):
            client.sessions.files.with_raw_response.delete(
                path="",
                name="name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_metadata(self, client: Ractorlabs) -> None:
        file = client.sessions.files.get_metadata(
            path="path",
            name="name",
        )
        assert_matches_type(FileGetMetadataResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_metadata(self, client: Ractorlabs) -> None:
        response = client.sessions.files.with_raw_response.get_metadata(
            path="path",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = response.parse()
        assert_matches_type(FileGetMetadataResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_metadata(self, client: Ractorlabs) -> None:
        with client.sessions.files.with_streaming_response.get_metadata(
            path="path",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = response.parse()
            assert_matches_type(FileGetMetadataResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_metadata(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.files.with_raw_response.get_metadata(
                path="path",
                name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path` but received ''"):
            client.sessions.files.with_raw_response.get_metadata(
                path="",
                name="name",
            )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_read(self, client: Ractorlabs, respx_mock: MockRouter) -> None:
        respx_mock.get("/sessions/name/files/read/path").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        file = client.sessions.files.read(
            path="path",
            name="name",
        )
        assert file.is_closed
        assert file.json() == {"foo": "bar"}
        assert cast(Any, file.is_closed) is True
        assert isinstance(file, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_read(self, client: Ractorlabs, respx_mock: MockRouter) -> None:
        respx_mock.get("/sessions/name/files/read/path").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        file = client.sessions.files.with_raw_response.read(
            path="path",
            name="name",
        )

        assert file.is_closed is True
        assert file.http_request.headers.get("X-Stainless-Lang") == "python"
        assert file.json() == {"foo": "bar"}
        assert isinstance(file, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_read(self, client: Ractorlabs, respx_mock: MockRouter) -> None:
        respx_mock.get("/sessions/name/files/read/path").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        with client.sessions.files.with_streaming_response.read(
            path="path",
            name="name",
        ) as file:
            assert not file.is_closed
            assert file.http_request.headers.get("X-Stainless-Lang") == "python"

            assert file.json() == {"foo": "bar"}
            assert cast(Any, file.is_closed) is True
            assert isinstance(file, StreamedBinaryAPIResponse)

        assert cast(Any, file.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_read(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.files.with_raw_response.read(
                path="path",
                name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path` but received ''"):
            client.sessions.files.with_raw_response.read(
                path="",
                name="name",
            )


class TestAsyncFiles:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncRactorlabs) -> None:
        file = await async_client.sessions.files.delete(
            path="path",
            name="name",
        )
        assert_matches_type(FileDeleteResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.files.with_raw_response.delete(
            path="path",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(FileDeleteResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.files.with_streaming_response.delete(
            path="path",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(FileDeleteResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.files.with_raw_response.delete(
                path="path",
                name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path` but received ''"):
            await async_client.sessions.files.with_raw_response.delete(
                path="",
                name="name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_metadata(self, async_client: AsyncRactorlabs) -> None:
        file = await async_client.sessions.files.get_metadata(
            path="path",
            name="name",
        )
        assert_matches_type(FileGetMetadataResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_metadata(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.files.with_raw_response.get_metadata(
            path="path",
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        file = await response.parse()
        assert_matches_type(FileGetMetadataResponse, file, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_metadata(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.files.with_streaming_response.get_metadata(
            path="path",
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            file = await response.parse()
            assert_matches_type(FileGetMetadataResponse, file, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_metadata(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.files.with_raw_response.get_metadata(
                path="path",
                name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path` but received ''"):
            await async_client.sessions.files.with_raw_response.get_metadata(
                path="",
                name="name",
            )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_read(self, async_client: AsyncRactorlabs, respx_mock: MockRouter) -> None:
        respx_mock.get("/sessions/name/files/read/path").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        file = await async_client.sessions.files.read(
            path="path",
            name="name",
        )
        assert file.is_closed
        assert await file.json() == {"foo": "bar"}
        assert cast(Any, file.is_closed) is True
        assert isinstance(file, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_read(self, async_client: AsyncRactorlabs, respx_mock: MockRouter) -> None:
        respx_mock.get("/sessions/name/files/read/path").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        file = await async_client.sessions.files.with_raw_response.read(
            path="path",
            name="name",
        )

        assert file.is_closed is True
        assert file.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await file.json() == {"foo": "bar"}
        assert isinstance(file, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_read(self, async_client: AsyncRactorlabs, respx_mock: MockRouter) -> None:
        respx_mock.get("/sessions/name/files/read/path").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        async with async_client.sessions.files.with_streaming_response.read(
            path="path",
            name="name",
        ) as file:
            assert not file.is_closed
            assert file.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await file.json() == {"foo": "bar"}
            assert cast(Any, file.is_closed) is True
            assert isinstance(file, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, file.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_read(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.files.with_raw_response.read(
                path="path",
                name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path` but received ''"):
            await async_client.sessions.files.with_raw_response.read(
                path="",
                name="name",
            )

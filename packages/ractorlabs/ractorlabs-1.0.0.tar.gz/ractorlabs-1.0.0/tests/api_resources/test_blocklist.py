# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from ractorlabs import Ractorlabs, AsyncRactorlabs
from tests.utils import assert_matches_type
from ractorlabs.types import (
    BlocklistListResponse,
    BlocklistBlockResponse,
    BlocklistUnblockResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBlocklist:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Ractorlabs) -> None:
        blocklist = client.blocklist.list()
        assert_matches_type(BlocklistListResponse, blocklist, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Ractorlabs) -> None:
        response = client.blocklist.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        blocklist = response.parse()
        assert_matches_type(BlocklistListResponse, blocklist, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Ractorlabs) -> None:
        with client.blocklist.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            blocklist = response.parse()
            assert_matches_type(BlocklistListResponse, blocklist, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_block(self, client: Ractorlabs) -> None:
        blocklist = client.blocklist.block(
            principal="principal",
        )
        assert_matches_type(BlocklistBlockResponse, blocklist, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_block_with_all_params(self, client: Ractorlabs) -> None:
        blocklist = client.blocklist.block(
            principal="principal",
            type="User",
        )
        assert_matches_type(BlocklistBlockResponse, blocklist, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_block(self, client: Ractorlabs) -> None:
        response = client.blocklist.with_raw_response.block(
            principal="principal",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        blocklist = response.parse()
        assert_matches_type(BlocklistBlockResponse, blocklist, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_block(self, client: Ractorlabs) -> None:
        with client.blocklist.with_streaming_response.block(
            principal="principal",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            blocklist = response.parse()
            assert_matches_type(BlocklistBlockResponse, blocklist, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_unblock(self, client: Ractorlabs) -> None:
        blocklist = client.blocklist.unblock(
            principal="principal",
        )
        assert_matches_type(BlocklistUnblockResponse, blocklist, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_unblock_with_all_params(self, client: Ractorlabs) -> None:
        blocklist = client.blocklist.unblock(
            principal="principal",
            type="User",
        )
        assert_matches_type(BlocklistUnblockResponse, blocklist, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_unblock(self, client: Ractorlabs) -> None:
        response = client.blocklist.with_raw_response.unblock(
            principal="principal",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        blocklist = response.parse()
        assert_matches_type(BlocklistUnblockResponse, blocklist, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_unblock(self, client: Ractorlabs) -> None:
        with client.blocklist.with_streaming_response.unblock(
            principal="principal",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            blocklist = response.parse()
            assert_matches_type(BlocklistUnblockResponse, blocklist, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncBlocklist:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncRactorlabs) -> None:
        blocklist = await async_client.blocklist.list()
        assert_matches_type(BlocklistListResponse, blocklist, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.blocklist.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        blocklist = await response.parse()
        assert_matches_type(BlocklistListResponse, blocklist, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.blocklist.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            blocklist = await response.parse()
            assert_matches_type(BlocklistListResponse, blocklist, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_block(self, async_client: AsyncRactorlabs) -> None:
        blocklist = await async_client.blocklist.block(
            principal="principal",
        )
        assert_matches_type(BlocklistBlockResponse, blocklist, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_block_with_all_params(self, async_client: AsyncRactorlabs) -> None:
        blocklist = await async_client.blocklist.block(
            principal="principal",
            type="User",
        )
        assert_matches_type(BlocklistBlockResponse, blocklist, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_block(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.blocklist.with_raw_response.block(
            principal="principal",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        blocklist = await response.parse()
        assert_matches_type(BlocklistBlockResponse, blocklist, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_block(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.blocklist.with_streaming_response.block(
            principal="principal",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            blocklist = await response.parse()
            assert_matches_type(BlocklistBlockResponse, blocklist, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_unblock(self, async_client: AsyncRactorlabs) -> None:
        blocklist = await async_client.blocklist.unblock(
            principal="principal",
        )
        assert_matches_type(BlocklistUnblockResponse, blocklist, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_unblock_with_all_params(self, async_client: AsyncRactorlabs) -> None:
        blocklist = await async_client.blocklist.unblock(
            principal="principal",
            type="User",
        )
        assert_matches_type(BlocklistUnblockResponse, blocklist, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_unblock(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.blocklist.with_raw_response.unblock(
            principal="principal",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        blocklist = await response.parse()
        assert_matches_type(BlocklistUnblockResponse, blocklist, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_unblock(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.blocklist.with_streaming_response.unblock(
            principal="principal",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            blocklist = await response.parse()
            assert_matches_type(BlocklistUnblockResponse, blocklist, path=["response"])

        assert cast(Any, response.is_closed) is True

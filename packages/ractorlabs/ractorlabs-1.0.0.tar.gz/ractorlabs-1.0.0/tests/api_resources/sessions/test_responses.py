# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from ractorlabs import Ractorlabs, AsyncRactorlabs
from tests.utils import assert_matches_type
from ractorlabs.types.sessions import (
    ResponseView,
    ResponseListResponse,
    ResponseCountResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestResponses:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Ractorlabs) -> None:
        response = client.sessions.responses.create(
            name="name",
            input={},
        )
        assert_matches_type(ResponseView, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Ractorlabs) -> None:
        response = client.sessions.responses.create(
            name="name",
            input={},
            background=True,
        )
        assert_matches_type(ResponseView, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Ractorlabs) -> None:
        http_response = client.sessions.responses.with_raw_response.create(
            name="name",
            input={},
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = http_response.parse()
        assert_matches_type(ResponseView, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Ractorlabs) -> None:
        with client.sessions.responses.with_streaming_response.create(
            name="name",
            input={},
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = http_response.parse()
            assert_matches_type(ResponseView, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.responses.with_raw_response.create(
                name="",
                input={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Ractorlabs) -> None:
        response = client.sessions.responses.retrieve(
            id="id",
            name="name",
        )
        assert_matches_type(ResponseView, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Ractorlabs) -> None:
        http_response = client.sessions.responses.with_raw_response.retrieve(
            id="id",
            name="name",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = http_response.parse()
        assert_matches_type(ResponseView, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Ractorlabs) -> None:
        with client.sessions.responses.with_streaming_response.retrieve(
            id="id",
            name="name",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = http_response.parse()
            assert_matches_type(ResponseView, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.responses.with_raw_response.retrieve(
                id="id",
                name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.sessions.responses.with_raw_response.retrieve(
                id="",
                name="name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Ractorlabs) -> None:
        response = client.sessions.responses.update(
            id="id",
            name="name",
        )
        assert_matches_type(ResponseView, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Ractorlabs) -> None:
        response = client.sessions.responses.update(
            id="id",
            name="name",
            input={},
            output={},
            status="status",
        )
        assert_matches_type(ResponseView, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Ractorlabs) -> None:
        http_response = client.sessions.responses.with_raw_response.update(
            id="id",
            name="name",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = http_response.parse()
        assert_matches_type(ResponseView, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Ractorlabs) -> None:
        with client.sessions.responses.with_streaming_response.update(
            id="id",
            name="name",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = http_response.parse()
            assert_matches_type(ResponseView, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.responses.with_raw_response.update(
                id="id",
                name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.sessions.responses.with_raw_response.update(
                id="",
                name="name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Ractorlabs) -> None:
        response = client.sessions.responses.list(
            name="name",
        )
        assert_matches_type(ResponseListResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Ractorlabs) -> None:
        response = client.sessions.responses.list(
            name="name",
            limit=1,
            offset=0,
        )
        assert_matches_type(ResponseListResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Ractorlabs) -> None:
        http_response = client.sessions.responses.with_raw_response.list(
            name="name",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = http_response.parse()
        assert_matches_type(ResponseListResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Ractorlabs) -> None:
        with client.sessions.responses.with_streaming_response.list(
            name="name",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = http_response.parse()
            assert_matches_type(ResponseListResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.responses.with_raw_response.list(
                name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_count(self, client: Ractorlabs) -> None:
        response = client.sessions.responses.count(
            "name",
        )
        assert_matches_type(ResponseCountResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_count(self, client: Ractorlabs) -> None:
        http_response = client.sessions.responses.with_raw_response.count(
            "name",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = http_response.parse()
        assert_matches_type(ResponseCountResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_count(self, client: Ractorlabs) -> None:
        with client.sessions.responses.with_streaming_response.count(
            "name",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = http_response.parse()
            assert_matches_type(ResponseCountResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_count(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.responses.with_raw_response.count(
                "",
            )


class TestAsyncResponses:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.responses.create(
            name="name",
            input={},
        )
        assert_matches_type(ResponseView, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.responses.create(
            name="name",
            input={},
            background=True,
        )
        assert_matches_type(ResponseView, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncRactorlabs) -> None:
        http_response = await async_client.sessions.responses.with_raw_response.create(
            name="name",
            input={},
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = await http_response.parse()
        assert_matches_type(ResponseView, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.responses.with_streaming_response.create(
            name="name",
            input={},
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = await http_response.parse()
            assert_matches_type(ResponseView, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.responses.with_raw_response.create(
                name="",
                input={},
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.responses.retrieve(
            id="id",
            name="name",
        )
        assert_matches_type(ResponseView, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncRactorlabs) -> None:
        http_response = await async_client.sessions.responses.with_raw_response.retrieve(
            id="id",
            name="name",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = await http_response.parse()
        assert_matches_type(ResponseView, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.responses.with_streaming_response.retrieve(
            id="id",
            name="name",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = await http_response.parse()
            assert_matches_type(ResponseView, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.responses.with_raw_response.retrieve(
                id="id",
                name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.sessions.responses.with_raw_response.retrieve(
                id="",
                name="name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.responses.update(
            id="id",
            name="name",
        )
        assert_matches_type(ResponseView, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.responses.update(
            id="id",
            name="name",
            input={},
            output={},
            status="status",
        )
        assert_matches_type(ResponseView, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncRactorlabs) -> None:
        http_response = await async_client.sessions.responses.with_raw_response.update(
            id="id",
            name="name",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = await http_response.parse()
        assert_matches_type(ResponseView, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.responses.with_streaming_response.update(
            id="id",
            name="name",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = await http_response.parse()
            assert_matches_type(ResponseView, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.responses.with_raw_response.update(
                id="id",
                name="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.sessions.responses.with_raw_response.update(
                id="",
                name="name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.responses.list(
            name="name",
        )
        assert_matches_type(ResponseListResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.responses.list(
            name="name",
            limit=1,
            offset=0,
        )
        assert_matches_type(ResponseListResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncRactorlabs) -> None:
        http_response = await async_client.sessions.responses.with_raw_response.list(
            name="name",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = await http_response.parse()
        assert_matches_type(ResponseListResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.responses.with_streaming_response.list(
            name="name",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = await http_response.parse()
            assert_matches_type(ResponseListResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.responses.with_raw_response.list(
                name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_count(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.responses.count(
            "name",
        )
        assert_matches_type(ResponseCountResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_count(self, async_client: AsyncRactorlabs) -> None:
        http_response = await async_client.sessions.responses.with_raw_response.count(
            "name",
        )

        assert http_response.is_closed is True
        assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"
        response = await http_response.parse()
        assert_matches_type(ResponseCountResponse, response, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_count(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.responses.with_streaming_response.count(
            "name",
        ) as http_response:
            assert not http_response.is_closed
            assert http_response.http_request.headers.get("X-Stainless-Lang") == "python"

            response = await http_response.parse()
            assert_matches_type(ResponseCountResponse, response, path=["response"])

        assert cast(Any, http_response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_count(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.responses.with_raw_response.count(
                "",
            )

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from ractorlabs import Ractorlabs, AsyncRactorlabs
from tests.utils import assert_matches_type
from ractorlabs.types import (
    Operator,
    LoginResponse,
    OperatorListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOperators:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Ractorlabs) -> None:
        operator = client.operators.create(
            pass_="pass",
            user="user",
        )
        assert_matches_type(Operator, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Ractorlabs) -> None:
        operator = client.operators.create(
            pass_="pass",
            user="user",
            description="description",
        )
        assert_matches_type(Operator, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Ractorlabs) -> None:
        response = client.operators.with_raw_response.create(
            pass_="pass",
            user="user",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operator = response.parse()
        assert_matches_type(Operator, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Ractorlabs) -> None:
        with client.operators.with_streaming_response.create(
            pass_="pass",
            user="user",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operator = response.parse()
            assert_matches_type(Operator, operator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Ractorlabs) -> None:
        operator = client.operators.retrieve(
            "name",
        )
        assert_matches_type(Operator, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Ractorlabs) -> None:
        response = client.operators.with_raw_response.retrieve(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operator = response.parse()
        assert_matches_type(Operator, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Ractorlabs) -> None:
        with client.operators.with_streaming_response.retrieve(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operator = response.parse()
            assert_matches_type(Operator, operator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.operators.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Ractorlabs) -> None:
        operator = client.operators.update(
            name="name",
        )
        assert_matches_type(Operator, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Ractorlabs) -> None:
        operator = client.operators.update(
            name="name",
            active=True,
            description="description",
        )
        assert_matches_type(Operator, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Ractorlabs) -> None:
        response = client.operators.with_raw_response.update(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operator = response.parse()
        assert_matches_type(Operator, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Ractorlabs) -> None:
        with client.operators.with_streaming_response.update(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operator = response.parse()
            assert_matches_type(Operator, operator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.operators.with_raw_response.update(
                name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Ractorlabs) -> None:
        operator = client.operators.list()
        assert_matches_type(OperatorListResponse, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Ractorlabs) -> None:
        response = client.operators.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operator = response.parse()
        assert_matches_type(OperatorListResponse, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Ractorlabs) -> None:
        with client.operators.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operator = response.parse()
            assert_matches_type(OperatorListResponse, operator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Ractorlabs) -> None:
        operator = client.operators.delete(
            "name",
        )
        assert operator is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Ractorlabs) -> None:
        response = client.operators.with_raw_response.delete(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operator = response.parse()
        assert operator is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Ractorlabs) -> None:
        with client.operators.with_streaming_response.delete(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operator = response.parse()
            assert operator is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.operators.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_login(self, client: Ractorlabs) -> None:
        operator = client.operators.login(
            name="name",
            pass_="pass",
        )
        assert_matches_type(LoginResponse, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_login_with_all_params(self, client: Ractorlabs) -> None:
        operator = client.operators.login(
            name="name",
            pass_="pass",
            ttl_hours=0,
        )
        assert_matches_type(LoginResponse, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_login(self, client: Ractorlabs) -> None:
        response = client.operators.with_raw_response.login(
            name="name",
            pass_="pass",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operator = response.parse()
        assert_matches_type(LoginResponse, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_login(self, client: Ractorlabs) -> None:
        with client.operators.with_streaming_response.login(
            name="name",
            pass_="pass",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operator = response.parse()
            assert_matches_type(LoginResponse, operator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_login(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.operators.with_raw_response.login(
                name="",
                pass_="pass",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_password(self, client: Ractorlabs) -> None:
        operator = client.operators.update_password(
            name="name",
            current_password="current_password",
            new_password="new_password",
        )
        assert operator is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_password(self, client: Ractorlabs) -> None:
        response = client.operators.with_raw_response.update_password(
            name="name",
            current_password="current_password",
            new_password="new_password",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operator = response.parse()
        assert operator is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_password(self, client: Ractorlabs) -> None:
        with client.operators.with_streaming_response.update_password(
            name="name",
            current_password="current_password",
            new_password="new_password",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operator = response.parse()
            assert operator is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_password(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.operators.with_raw_response.update_password(
                name="",
                current_password="current_password",
                new_password="new_password",
            )


class TestAsyncOperators:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncRactorlabs) -> None:
        operator = await async_client.operators.create(
            pass_="pass",
            user="user",
        )
        assert_matches_type(Operator, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncRactorlabs) -> None:
        operator = await async_client.operators.create(
            pass_="pass",
            user="user",
            description="description",
        )
        assert_matches_type(Operator, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.operators.with_raw_response.create(
            pass_="pass",
            user="user",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operator = await response.parse()
        assert_matches_type(Operator, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.operators.with_streaming_response.create(
            pass_="pass",
            user="user",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operator = await response.parse()
            assert_matches_type(Operator, operator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncRactorlabs) -> None:
        operator = await async_client.operators.retrieve(
            "name",
        )
        assert_matches_type(Operator, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.operators.with_raw_response.retrieve(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operator = await response.parse()
        assert_matches_type(Operator, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.operators.with_streaming_response.retrieve(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operator = await response.parse()
            assert_matches_type(Operator, operator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.operators.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncRactorlabs) -> None:
        operator = await async_client.operators.update(
            name="name",
        )
        assert_matches_type(Operator, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncRactorlabs) -> None:
        operator = await async_client.operators.update(
            name="name",
            active=True,
            description="description",
        )
        assert_matches_type(Operator, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.operators.with_raw_response.update(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operator = await response.parse()
        assert_matches_type(Operator, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.operators.with_streaming_response.update(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operator = await response.parse()
            assert_matches_type(Operator, operator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.operators.with_raw_response.update(
                name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncRactorlabs) -> None:
        operator = await async_client.operators.list()
        assert_matches_type(OperatorListResponse, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.operators.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operator = await response.parse()
        assert_matches_type(OperatorListResponse, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.operators.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operator = await response.parse()
            assert_matches_type(OperatorListResponse, operator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncRactorlabs) -> None:
        operator = await async_client.operators.delete(
            "name",
        )
        assert operator is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.operators.with_raw_response.delete(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operator = await response.parse()
        assert operator is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.operators.with_streaming_response.delete(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operator = await response.parse()
            assert operator is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.operators.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_login(self, async_client: AsyncRactorlabs) -> None:
        operator = await async_client.operators.login(
            name="name",
            pass_="pass",
        )
        assert_matches_type(LoginResponse, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_login_with_all_params(self, async_client: AsyncRactorlabs) -> None:
        operator = await async_client.operators.login(
            name="name",
            pass_="pass",
            ttl_hours=0,
        )
        assert_matches_type(LoginResponse, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_login(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.operators.with_raw_response.login(
            name="name",
            pass_="pass",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operator = await response.parse()
        assert_matches_type(LoginResponse, operator, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_login(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.operators.with_streaming_response.login(
            name="name",
            pass_="pass",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operator = await response.parse()
            assert_matches_type(LoginResponse, operator, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_login(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.operators.with_raw_response.login(
                name="",
                pass_="pass",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_password(self, async_client: AsyncRactorlabs) -> None:
        operator = await async_client.operators.update_password(
            name="name",
            current_password="current_password",
            new_password="new_password",
        )
        assert operator is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_password(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.operators.with_raw_response.update_password(
            name="name",
            current_password="current_password",
            new_password="new_password",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        operator = await response.parse()
        assert operator is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_password(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.operators.with_streaming_response.update_password(
            name="name",
            current_password="current_password",
            new_password="new_password",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            operator = await response.parse()
            assert operator is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_password(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.operators.with_raw_response.update_password(
                name="",
                current_password="current_password",
                new_password="new_password",
            )

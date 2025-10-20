# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from ractorlabs import Ractorlabs, AsyncRactorlabs
from tests.utils import assert_matches_type
from ractorlabs.types.sessions import SessionContextUsage, ContextReportUsageResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestContext:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_clear(self, client: Ractorlabs) -> None:
        context = client.sessions.context.clear(
            "name",
        )
        assert_matches_type(SessionContextUsage, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_clear(self, client: Ractorlabs) -> None:
        response = client.sessions.context.with_raw_response.clear(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        context = response.parse()
        assert_matches_type(SessionContextUsage, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_clear(self, client: Ractorlabs) -> None:
        with client.sessions.context.with_streaming_response.clear(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            context = response.parse()
            assert_matches_type(SessionContextUsage, context, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_clear(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.context.with_raw_response.clear(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_compact(self, client: Ractorlabs) -> None:
        context = client.sessions.context.compact(
            "name",
        )
        assert_matches_type(SessionContextUsage, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_compact(self, client: Ractorlabs) -> None:
        response = client.sessions.context.with_raw_response.compact(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        context = response.parse()
        assert_matches_type(SessionContextUsage, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_compact(self, client: Ractorlabs) -> None:
        with client.sessions.context.with_streaming_response.compact(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            context = response.parse()
            assert_matches_type(SessionContextUsage, context, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_compact(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.context.with_raw_response.compact(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_usage(self, client: Ractorlabs) -> None:
        context = client.sessions.context.get_usage(
            "name",
        )
        assert_matches_type(SessionContextUsage, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_usage(self, client: Ractorlabs) -> None:
        response = client.sessions.context.with_raw_response.get_usage(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        context = response.parse()
        assert_matches_type(SessionContextUsage, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_usage(self, client: Ractorlabs) -> None:
        with client.sessions.context.with_streaming_response.get_usage(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            context = response.parse()
            assert_matches_type(SessionContextUsage, context, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_usage(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.context.with_raw_response.get_usage(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_report_usage(self, client: Ractorlabs) -> None:
        context = client.sessions.context.report_usage(
            name="name",
            tokens=0,
        )
        assert_matches_type(ContextReportUsageResponse, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_report_usage(self, client: Ractorlabs) -> None:
        response = client.sessions.context.with_raw_response.report_usage(
            name="name",
            tokens=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        context = response.parse()
        assert_matches_type(ContextReportUsageResponse, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_report_usage(self, client: Ractorlabs) -> None:
        with client.sessions.context.with_streaming_response.report_usage(
            name="name",
            tokens=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            context = response.parse()
            assert_matches_type(ContextReportUsageResponse, context, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_report_usage(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.context.with_raw_response.report_usage(
                name="",
                tokens=0,
            )


class TestAsyncContext:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_clear(self, async_client: AsyncRactorlabs) -> None:
        context = await async_client.sessions.context.clear(
            "name",
        )
        assert_matches_type(SessionContextUsage, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_clear(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.context.with_raw_response.clear(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        context = await response.parse()
        assert_matches_type(SessionContextUsage, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_clear(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.context.with_streaming_response.clear(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            context = await response.parse()
            assert_matches_type(SessionContextUsage, context, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_clear(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.context.with_raw_response.clear(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_compact(self, async_client: AsyncRactorlabs) -> None:
        context = await async_client.sessions.context.compact(
            "name",
        )
        assert_matches_type(SessionContextUsage, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_compact(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.context.with_raw_response.compact(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        context = await response.parse()
        assert_matches_type(SessionContextUsage, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_compact(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.context.with_streaming_response.compact(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            context = await response.parse()
            assert_matches_type(SessionContextUsage, context, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_compact(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.context.with_raw_response.compact(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_usage(self, async_client: AsyncRactorlabs) -> None:
        context = await async_client.sessions.context.get_usage(
            "name",
        )
        assert_matches_type(SessionContextUsage, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_usage(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.context.with_raw_response.get_usage(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        context = await response.parse()
        assert_matches_type(SessionContextUsage, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_usage(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.context.with_streaming_response.get_usage(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            context = await response.parse()
            assert_matches_type(SessionContextUsage, context, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_usage(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.context.with_raw_response.get_usage(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_report_usage(self, async_client: AsyncRactorlabs) -> None:
        context = await async_client.sessions.context.report_usage(
            name="name",
            tokens=0,
        )
        assert_matches_type(ContextReportUsageResponse, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_report_usage(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.context.with_raw_response.report_usage(
            name="name",
            tokens=0,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        context = await response.parse()
        assert_matches_type(ContextReportUsageResponse, context, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_report_usage(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.context.with_streaming_response.report_usage(
            name="name",
            tokens=0,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            context = await response.parse()
            assert_matches_type(ContextReportUsageResponse, context, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_report_usage(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.context.with_raw_response.report_usage(
                name="",
                tokens=0,
            )

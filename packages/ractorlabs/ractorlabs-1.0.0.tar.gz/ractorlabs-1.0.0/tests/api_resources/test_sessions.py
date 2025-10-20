# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from ractorlabs import Ractorlabs, AsyncRactorlabs
from tests.utils import assert_matches_type
from ractorlabs.types import (
    SessionListResponse,
    SessionCancelResponse,
    SessionMarkBusyResponse,
    SessionMarkIdleResponse,
    SessionGetRuntimeResponse,
    SessionUpdateStateResponse,
)
from ractorlabs.types.published import Session

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSessions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Ractorlabs) -> None:
        session = client.sessions.create(
            name="name",
        )
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Ractorlabs) -> None:
        session = client.sessions.create(
            name="name",
            busy_timeout_seconds=0,
            description="description",
            env={"foo": "string"},
            idle_timeout_seconds=0,
            instructions="instructions",
            metadata={},
            prompt="prompt",
            setup="setup",
            tags=["string"],
        )
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Ractorlabs) -> None:
        response = client.sessions.with_raw_response.create(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Ractorlabs) -> None:
        with client.sessions.with_streaming_response.create(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(Session, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Ractorlabs) -> None:
        session = client.sessions.retrieve(
            "name",
        )
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Ractorlabs) -> None:
        response = client.sessions.with_raw_response.retrieve(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Ractorlabs) -> None:
        with client.sessions.with_streaming_response.retrieve(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(Session, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Ractorlabs) -> None:
        session = client.sessions.update(
            name="name",
        )
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Ractorlabs) -> None:
        session = client.sessions.update(
            name="name",
            busy_timeout_seconds=0,
            description="description",
            idle_timeout_seconds=0,
            metadata={},
            tags=["string"],
        )
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Ractorlabs) -> None:
        response = client.sessions.with_raw_response.update(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Ractorlabs) -> None:
        with client.sessions.with_streaming_response.update(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(Session, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.with_raw_response.update(
                name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Ractorlabs) -> None:
        session = client.sessions.list()
        assert_matches_type(SessionListResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Ractorlabs) -> None:
        session = client.sessions.list(
            limit=1,
            offset=0,
            page=1,
            q="q",
            state="state",
            tags=["string"],
        )
        assert_matches_type(SessionListResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Ractorlabs) -> None:
        response = client.sessions.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionListResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Ractorlabs) -> None:
        with client.sessions.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionListResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Ractorlabs) -> None:
        session = client.sessions.delete(
            "name",
        )
        assert session is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Ractorlabs) -> None:
        response = client.sessions.with_raw_response.delete(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert session is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Ractorlabs) -> None:
        with client.sessions.with_streaming_response.delete(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert session is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_branch(self, client: Ractorlabs) -> None:
        session = client.sessions.branch(
            path_name="name",
            body_name="name",
        )
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_branch_with_all_params(self, client: Ractorlabs) -> None:
        session = client.sessions.branch(
            path_name="name",
            body_name="name",
            code=True,
            content=True,
            env=True,
            metadata={},
            prompt="prompt",
        )
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_branch(self, client: Ractorlabs) -> None:
        response = client.sessions.with_raw_response.branch(
            path_name="name",
            body_name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_branch(self, client: Ractorlabs) -> None:
        with client.sessions.with_streaming_response.branch(
            path_name="name",
            body_name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(Session, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_branch(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_name` but received ''"):
            client.sessions.with_raw_response.branch(
                path_name="",
                body_name="name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_cancel(self, client: Ractorlabs) -> None:
        session = client.sessions.cancel(
            "name",
        )
        assert_matches_type(SessionCancelResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_cancel(self, client: Ractorlabs) -> None:
        response = client.sessions.with_raw_response.cancel(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionCancelResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_cancel(self, client: Ractorlabs) -> None:
        with client.sessions.with_streaming_response.cancel(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionCancelResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_cancel(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.with_raw_response.cancel(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_runtime(self, client: Ractorlabs) -> None:
        session = client.sessions.get_runtime(
            "name",
        )
        assert_matches_type(SessionGetRuntimeResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_runtime(self, client: Ractorlabs) -> None:
        response = client.sessions.with_raw_response.get_runtime(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionGetRuntimeResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_runtime(self, client: Ractorlabs) -> None:
        with client.sessions.with_streaming_response.get_runtime(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionGetRuntimeResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_runtime(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.with_raw_response.get_runtime(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_mark_busy(self, client: Ractorlabs) -> None:
        session = client.sessions.mark_busy(
            "name",
        )
        assert_matches_type(SessionMarkBusyResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_mark_busy(self, client: Ractorlabs) -> None:
        response = client.sessions.with_raw_response.mark_busy(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionMarkBusyResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_mark_busy(self, client: Ractorlabs) -> None:
        with client.sessions.with_streaming_response.mark_busy(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionMarkBusyResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_mark_busy(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.with_raw_response.mark_busy(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_mark_idle(self, client: Ractorlabs) -> None:
        session = client.sessions.mark_idle(
            "name",
        )
        assert_matches_type(SessionMarkIdleResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_mark_idle(self, client: Ractorlabs) -> None:
        response = client.sessions.with_raw_response.mark_idle(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionMarkIdleResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_mark_idle(self, client: Ractorlabs) -> None:
        with client.sessions.with_streaming_response.mark_idle(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionMarkIdleResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_mark_idle(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.with_raw_response.mark_idle(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_publish(self, client: Ractorlabs) -> None:
        session = client.sessions.publish(
            name="name",
        )
        assert session is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_publish_with_all_params(self, client: Ractorlabs) -> None:
        session = client.sessions.publish(
            name="name",
            code=True,
            content=True,
            env=True,
        )
        assert session is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_publish(self, client: Ractorlabs) -> None:
        response = client.sessions.with_raw_response.publish(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert session is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_publish(self, client: Ractorlabs) -> None:
        with client.sessions.with_streaming_response.publish(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert session is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_publish(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.with_raw_response.publish(
                name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_sleep(self, client: Ractorlabs) -> None:
        session = client.sessions.sleep(
            name="name",
        )
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_sleep_with_all_params(self, client: Ractorlabs) -> None:
        session = client.sessions.sleep(
            name="name",
            delay_seconds=5,
            note="note",
        )
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_sleep(self, client: Ractorlabs) -> None:
        response = client.sessions.with_raw_response.sleep(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_sleep(self, client: Ractorlabs) -> None:
        with client.sessions.with_streaming_response.sleep(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(Session, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_sleep(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.with_raw_response.sleep(
                name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_unpublish(self, client: Ractorlabs) -> None:
        session = client.sessions.unpublish(
            "name",
        )
        assert session is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_unpublish(self, client: Ractorlabs) -> None:
        response = client.sessions.with_raw_response.unpublish(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert session is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_unpublish(self, client: Ractorlabs) -> None:
        with client.sessions.with_streaming_response.unpublish(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert session is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_unpublish(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.with_raw_response.unpublish(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_state(self, client: Ractorlabs) -> None:
        session = client.sessions.update_state(
            name="name",
        )
        assert_matches_type(SessionUpdateStateResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_state_with_all_params(self, client: Ractorlabs) -> None:
        session = client.sessions.update_state(
            name="name",
            state="init",
        )
        assert_matches_type(SessionUpdateStateResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_state(self, client: Ractorlabs) -> None:
        response = client.sessions.with_raw_response.update_state(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(SessionUpdateStateResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_state(self, client: Ractorlabs) -> None:
        with client.sessions.with_streaming_response.update_state(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(SessionUpdateStateResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_state(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.with_raw_response.update_state(
                name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_wake(self, client: Ractorlabs) -> None:
        session = client.sessions.wake(
            name="name",
        )
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_wake_with_all_params(self, client: Ractorlabs) -> None:
        session = client.sessions.wake(
            name="name",
            prompt="prompt",
        )
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_wake(self, client: Ractorlabs) -> None:
        response = client.sessions.with_raw_response.wake(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = response.parse()
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_wake(self, client: Ractorlabs) -> None:
        with client.sessions.with_streaming_response.wake(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = response.parse()
            assert_matches_type(Session, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_wake(self, client: Ractorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            client.sessions.with_raw_response.wake(
                name="",
            )


class TestAsyncSessions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncRactorlabs) -> None:
        session = await async_client.sessions.create(
            name="name",
        )
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncRactorlabs) -> None:
        session = await async_client.sessions.create(
            name="name",
            busy_timeout_seconds=0,
            description="description",
            env={"foo": "string"},
            idle_timeout_seconds=0,
            instructions="instructions",
            metadata={},
            prompt="prompt",
            setup="setup",
            tags=["string"],
        )
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.with_raw_response.create(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.with_streaming_response.create(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(Session, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncRactorlabs) -> None:
        session = await async_client.sessions.retrieve(
            "name",
        )
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.with_raw_response.retrieve(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.with_streaming_response.retrieve(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(Session, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncRactorlabs) -> None:
        session = await async_client.sessions.update(
            name="name",
        )
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncRactorlabs) -> None:
        session = await async_client.sessions.update(
            name="name",
            busy_timeout_seconds=0,
            description="description",
            idle_timeout_seconds=0,
            metadata={},
            tags=["string"],
        )
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.with_raw_response.update(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.with_streaming_response.update(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(Session, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.with_raw_response.update(
                name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncRactorlabs) -> None:
        session = await async_client.sessions.list()
        assert_matches_type(SessionListResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncRactorlabs) -> None:
        session = await async_client.sessions.list(
            limit=1,
            offset=0,
            page=1,
            q="q",
            state="state",
            tags=["string"],
        )
        assert_matches_type(SessionListResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(SessionListResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionListResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncRactorlabs) -> None:
        session = await async_client.sessions.delete(
            "name",
        )
        assert session is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.with_raw_response.delete(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert session is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.with_streaming_response.delete(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert session is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.with_raw_response.delete(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_branch(self, async_client: AsyncRactorlabs) -> None:
        session = await async_client.sessions.branch(
            path_name="name",
            body_name="name",
        )
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_branch_with_all_params(self, async_client: AsyncRactorlabs) -> None:
        session = await async_client.sessions.branch(
            path_name="name",
            body_name="name",
            code=True,
            content=True,
            env=True,
            metadata={},
            prompt="prompt",
        )
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_branch(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.with_raw_response.branch(
            path_name="name",
            body_name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_branch(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.with_streaming_response.branch(
            path_name="name",
            body_name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(Session, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_branch(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `path_name` but received ''"):
            await async_client.sessions.with_raw_response.branch(
                path_name="",
                body_name="name",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_cancel(self, async_client: AsyncRactorlabs) -> None:
        session = await async_client.sessions.cancel(
            "name",
        )
        assert_matches_type(SessionCancelResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_cancel(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.with_raw_response.cancel(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(SessionCancelResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_cancel(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.with_streaming_response.cancel(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionCancelResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_cancel(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.with_raw_response.cancel(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_runtime(self, async_client: AsyncRactorlabs) -> None:
        session = await async_client.sessions.get_runtime(
            "name",
        )
        assert_matches_type(SessionGetRuntimeResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_runtime(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.with_raw_response.get_runtime(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(SessionGetRuntimeResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_runtime(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.with_streaming_response.get_runtime(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionGetRuntimeResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_runtime(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.with_raw_response.get_runtime(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_mark_busy(self, async_client: AsyncRactorlabs) -> None:
        session = await async_client.sessions.mark_busy(
            "name",
        )
        assert_matches_type(SessionMarkBusyResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_mark_busy(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.with_raw_response.mark_busy(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(SessionMarkBusyResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_mark_busy(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.with_streaming_response.mark_busy(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionMarkBusyResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_mark_busy(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.with_raw_response.mark_busy(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_mark_idle(self, async_client: AsyncRactorlabs) -> None:
        session = await async_client.sessions.mark_idle(
            "name",
        )
        assert_matches_type(SessionMarkIdleResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_mark_idle(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.with_raw_response.mark_idle(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(SessionMarkIdleResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_mark_idle(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.with_streaming_response.mark_idle(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionMarkIdleResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_mark_idle(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.with_raw_response.mark_idle(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_publish(self, async_client: AsyncRactorlabs) -> None:
        session = await async_client.sessions.publish(
            name="name",
        )
        assert session is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_publish_with_all_params(self, async_client: AsyncRactorlabs) -> None:
        session = await async_client.sessions.publish(
            name="name",
            code=True,
            content=True,
            env=True,
        )
        assert session is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_publish(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.with_raw_response.publish(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert session is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_publish(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.with_streaming_response.publish(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert session is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_publish(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.with_raw_response.publish(
                name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_sleep(self, async_client: AsyncRactorlabs) -> None:
        session = await async_client.sessions.sleep(
            name="name",
        )
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_sleep_with_all_params(self, async_client: AsyncRactorlabs) -> None:
        session = await async_client.sessions.sleep(
            name="name",
            delay_seconds=5,
            note="note",
        )
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_sleep(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.with_raw_response.sleep(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_sleep(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.with_streaming_response.sleep(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(Session, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_sleep(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.with_raw_response.sleep(
                name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_unpublish(self, async_client: AsyncRactorlabs) -> None:
        session = await async_client.sessions.unpublish(
            "name",
        )
        assert session is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_unpublish(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.with_raw_response.unpublish(
            "name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert session is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_unpublish(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.with_streaming_response.unpublish(
            "name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert session is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_unpublish(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.with_raw_response.unpublish(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_state(self, async_client: AsyncRactorlabs) -> None:
        session = await async_client.sessions.update_state(
            name="name",
        )
        assert_matches_type(SessionUpdateStateResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_state_with_all_params(self, async_client: AsyncRactorlabs) -> None:
        session = await async_client.sessions.update_state(
            name="name",
            state="init",
        )
        assert_matches_type(SessionUpdateStateResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_state(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.with_raw_response.update_state(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(SessionUpdateStateResponse, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_state(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.with_streaming_response.update_state(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(SessionUpdateStateResponse, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_state(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.with_raw_response.update_state(
                name="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_wake(self, async_client: AsyncRactorlabs) -> None:
        session = await async_client.sessions.wake(
            name="name",
        )
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_wake_with_all_params(self, async_client: AsyncRactorlabs) -> None:
        session = await async_client.sessions.wake(
            name="name",
            prompt="prompt",
        )
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_wake(self, async_client: AsyncRactorlabs) -> None:
        response = await async_client.sessions.with_raw_response.wake(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        session = await response.parse()
        assert_matches_type(Session, session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_wake(self, async_client: AsyncRactorlabs) -> None:
        async with async_client.sessions.with_streaming_response.wake(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            session = await response.parse()
            assert_matches_type(Session, session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_wake(self, async_client: AsyncRactorlabs) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `name` but received ''"):
            await async_client.sessions.with_raw_response.wake(
                name="",
            )

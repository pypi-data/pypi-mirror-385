# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from anchorbrowser import Anchorbrowser, AsyncAnchorbrowser
from anchorbrowser.types.task import RunExecuteResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRun:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute(self, client: Anchorbrowser) -> None:
        run = client.task.run.execute(
            task_id="550e8400-e29b-41d4-a716-446655440000",
        )
        assert_matches_type(RunExecuteResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_with_all_params(self, client: Anchorbrowser) -> None:
        run = client.task.run.execute(
            task_id="550e8400-e29b-41d4-a716-446655440000",
            inputs={
                "ANCHOR_TARGET_URL": "https://example.com",
                "ANCHOR_MAX_PAGES": "10",
            },
            override_browser_configuration={
                "initial_url": "https://example.com",
                "live_view": {"read_only": True},
                "proxy": {
                    "active": True,
                    "city": "city",
                    "country_code": "af",
                    "region": "region",
                    "type": "anchor_proxy",
                },
                "recording": {"active": True},
                "timeout": {
                    "idle_timeout": 0,
                    "max_duration": 0,
                },
            },
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            task_session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            version="1",
        )
        assert_matches_type(RunExecuteResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_execute(self, client: Anchorbrowser) -> None:
        response = client.task.run.with_raw_response.execute(
            task_id="550e8400-e29b-41d4-a716-446655440000",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = response.parse()
        assert_matches_type(RunExecuteResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_execute(self, client: Anchorbrowser) -> None:
        with client.task.run.with_streaming_response.execute(
            task_id="550e8400-e29b-41d4-a716-446655440000",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = response.parse()
            assert_matches_type(RunExecuteResponse, run, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncRun:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute(self, async_client: AsyncAnchorbrowser) -> None:
        run = await async_client.task.run.execute(
            task_id="550e8400-e29b-41d4-a716-446655440000",
        )
        assert_matches_type(RunExecuteResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_with_all_params(self, async_client: AsyncAnchorbrowser) -> None:
        run = await async_client.task.run.execute(
            task_id="550e8400-e29b-41d4-a716-446655440000",
            inputs={
                "ANCHOR_TARGET_URL": "https://example.com",
                "ANCHOR_MAX_PAGES": "10",
            },
            override_browser_configuration={
                "initial_url": "https://example.com",
                "live_view": {"read_only": True},
                "proxy": {
                    "active": True,
                    "city": "city",
                    "country_code": "af",
                    "region": "region",
                    "type": "anchor_proxy",
                },
                "recording": {"active": True},
                "timeout": {
                    "idle_timeout": 0,
                    "max_duration": 0,
                },
            },
            session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            task_session_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            version="1",
        )
        assert_matches_type(RunExecuteResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_execute(self, async_client: AsyncAnchorbrowser) -> None:
        response = await async_client.task.run.with_raw_response.execute(
            task_id="550e8400-e29b-41d4-a716-446655440000",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        run = await response.parse()
        assert_matches_type(RunExecuteResponse, run, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_execute(self, async_client: AsyncAnchorbrowser) -> None:
        async with async_client.task.run.with_streaming_response.execute(
            task_id="550e8400-e29b-41d4-a716-446655440000",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            run = await response.parse()
            assert_matches_type(RunExecuteResponse, run, path=["response"])

        assert cast(Any, response.is_closed) is True

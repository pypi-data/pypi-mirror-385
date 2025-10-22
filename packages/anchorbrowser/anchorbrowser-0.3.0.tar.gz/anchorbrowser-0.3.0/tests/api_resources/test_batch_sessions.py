# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from anchorbrowser import Anchorbrowser, AsyncAnchorbrowser
from anchorbrowser.types import BatchSessionCreateResponse, BatchSessionRetrieveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestBatchSessions:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Anchorbrowser) -> None:
        batch_session = client.batch_sessions.create(
            count=10,
        )
        assert_matches_type(BatchSessionCreateResponse, batch_session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Anchorbrowser) -> None:
        batch_session = client.batch_sessions.create(
            count=10,
            configuration={
                "browser": {
                    "adblock": {"active": True},
                    "captcha_solver": {"active": True},
                    "disable_web_security": {"active": True},
                    "extensions": ["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
                    "extra_stealth": {"active": True},
                    "fullscreen": {"active": True},
                    "headless": {"active": True},
                    "p2p_download": {"active": True},
                    "popup_blocker": {"active": True},
                    "profile": {
                        "name": "name",
                        "persist": True,
                    },
                    "viewport": {
                        "height": 900,
                        "width": 1440,
                    },
                },
                "integrations": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "configuration": {"load_mode": "all"},
                        "type": "1PASSWORD",
                    }
                ],
                "session": {
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
                        "idle_timeout": 10,
                        "max_duration": 300,
                    },
                },
            },
            metadata={
                "project": "bar",
                "environment": "bar",
            },
        )
        assert_matches_type(BatchSessionCreateResponse, batch_session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Anchorbrowser) -> None:
        response = client.batch_sessions.with_raw_response.create(
            count=10,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_session = response.parse()
        assert_matches_type(BatchSessionCreateResponse, batch_session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Anchorbrowser) -> None:
        with client.batch_sessions.with_streaming_response.create(
            count=10,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_session = response.parse()
            assert_matches_type(BatchSessionCreateResponse, batch_session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Anchorbrowser) -> None:
        batch_session = client.batch_sessions.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(BatchSessionRetrieveResponse, batch_session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Anchorbrowser) -> None:
        response = client.batch_sessions.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_session = response.parse()
        assert_matches_type(BatchSessionRetrieveResponse, batch_session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Anchorbrowser) -> None:
        with client.batch_sessions.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_session = response.parse()
            assert_matches_type(BatchSessionRetrieveResponse, batch_session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Anchorbrowser) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_id` but received ''"):
            client.batch_sessions.with_raw_response.retrieve(
                "",
            )


class TestAsyncBatchSessions:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncAnchorbrowser) -> None:
        batch_session = await async_client.batch_sessions.create(
            count=10,
        )
        assert_matches_type(BatchSessionCreateResponse, batch_session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncAnchorbrowser) -> None:
        batch_session = await async_client.batch_sessions.create(
            count=10,
            configuration={
                "browser": {
                    "adblock": {"active": True},
                    "captcha_solver": {"active": True},
                    "disable_web_security": {"active": True},
                    "extensions": ["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
                    "extra_stealth": {"active": True},
                    "fullscreen": {"active": True},
                    "headless": {"active": True},
                    "p2p_download": {"active": True},
                    "popup_blocker": {"active": True},
                    "profile": {
                        "name": "name",
                        "persist": True,
                    },
                    "viewport": {
                        "height": 900,
                        "width": 1440,
                    },
                },
                "integrations": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "configuration": {"load_mode": "all"},
                        "type": "1PASSWORD",
                    }
                ],
                "session": {
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
                        "idle_timeout": 10,
                        "max_duration": 300,
                    },
                },
            },
            metadata={
                "project": "bar",
                "environment": "bar",
            },
        )
        assert_matches_type(BatchSessionCreateResponse, batch_session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncAnchorbrowser) -> None:
        response = await async_client.batch_sessions.with_raw_response.create(
            count=10,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_session = await response.parse()
        assert_matches_type(BatchSessionCreateResponse, batch_session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncAnchorbrowser) -> None:
        async with async_client.batch_sessions.with_streaming_response.create(
            count=10,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_session = await response.parse()
            assert_matches_type(BatchSessionCreateResponse, batch_session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncAnchorbrowser) -> None:
        batch_session = await async_client.batch_sessions.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(BatchSessionRetrieveResponse, batch_session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncAnchorbrowser) -> None:
        response = await async_client.batch_sessions.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        batch_session = await response.parse()
        assert_matches_type(BatchSessionRetrieveResponse, batch_session, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncAnchorbrowser) -> None:
        async with async_client.batch_sessions.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            batch_session = await response.parse()
            assert_matches_type(BatchSessionRetrieveResponse, batch_session, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncAnchorbrowser) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `batch_id` but received ''"):
            await async_client.batch_sessions.with_raw_response.retrieve(
                "",
            )

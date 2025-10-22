# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from gcore import Gcore, AsyncGcore
from tests.utils import assert_matches_type
from gcore.types.waap.ip_info import WaapIPInfoCounts

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMetrics:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: Gcore) -> None:
        metric = client.waap.ip_info.metrics.list(
            ip="192.168.1.1",
        )
        assert_matches_type(WaapIPInfoCounts, metric, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Gcore) -> None:
        metric = client.waap.ip_info.metrics.list(
            ip="192.168.1.1",
            domain_id=1,
        )
        assert_matches_type(WaapIPInfoCounts, metric, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Gcore) -> None:
        response = client.waap.ip_info.metrics.with_raw_response.list(
            ip="192.168.1.1",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        metric = response.parse()
        assert_matches_type(WaapIPInfoCounts, metric, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Gcore) -> None:
        with client.waap.ip_info.metrics.with_streaming_response.list(
            ip="192.168.1.1",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            metric = response.parse()
            assert_matches_type(WaapIPInfoCounts, metric, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncMetrics:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_list(self, async_client: AsyncGcore) -> None:
        metric = await async_client.waap.ip_info.metrics.list(
            ip="192.168.1.1",
        )
        assert_matches_type(WaapIPInfoCounts, metric, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncGcore) -> None:
        metric = await async_client.waap.ip_info.metrics.list(
            ip="192.168.1.1",
            domain_id=1,
        )
        assert_matches_type(WaapIPInfoCounts, metric, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncGcore) -> None:
        response = await async_client.waap.ip_info.metrics.with_raw_response.list(
            ip="192.168.1.1",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        metric = await response.parse()
        assert_matches_type(WaapIPInfoCounts, metric, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncGcore) -> None:
        async with async_client.waap.ip_info.metrics.with_streaming_response.list(
            ip="192.168.1.1",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            metric = await response.parse()
            assert_matches_type(WaapIPInfoCounts, metric, path=["response"])

        assert cast(Any, response.is_closed) is True

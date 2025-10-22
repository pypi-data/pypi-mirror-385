# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from gcore import Gcore, AsyncGcore
from tests.utils import assert_matches_type
from gcore.pagination import SyncOffsetPage, AsyncOffsetPage
from gcore.types.waap.domains import WaapInsight

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestInsights:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: Gcore) -> None:
        insight = client.waap.domains.insights.list(
            domain_id=1,
        )
        assert_matches_type(SyncOffsetPage[WaapInsight], insight, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Gcore) -> None:
        insight = client.waap.domains.insights.list(
            domain_id=1,
            id=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e", "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            description="description",
            insight_type=["string", "string"],
            limit=0,
            offset=0,
            ordering="id",
            status=["OPEN", "ACKED"],
        )
        assert_matches_type(SyncOffsetPage[WaapInsight], insight, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Gcore) -> None:
        response = client.waap.domains.insights.with_raw_response.list(
            domain_id=1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        insight = response.parse()
        assert_matches_type(SyncOffsetPage[WaapInsight], insight, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Gcore) -> None:
        with client.waap.domains.insights.with_streaming_response.list(
            domain_id=1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            insight = response.parse()
            assert_matches_type(SyncOffsetPage[WaapInsight], insight, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get(self, client: Gcore) -> None:
        insight = client.waap.domains.insights.get(
            insight_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            domain_id=1,
        )
        assert_matches_type(WaapInsight, insight, path=["response"])

    @parametrize
    def test_raw_response_get(self, client: Gcore) -> None:
        response = client.waap.domains.insights.with_raw_response.get(
            insight_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            domain_id=1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        insight = response.parse()
        assert_matches_type(WaapInsight, insight, path=["response"])

    @parametrize
    def test_streaming_response_get(self, client: Gcore) -> None:
        with client.waap.domains.insights.with_streaming_response.get(
            insight_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            domain_id=1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            insight = response.parse()
            assert_matches_type(WaapInsight, insight, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_get(self, client: Gcore) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `insight_id` but received ''"):
            client.waap.domains.insights.with_raw_response.get(
                insight_id="",
                domain_id=1,
            )

    @parametrize
    def test_method_replace(self, client: Gcore) -> None:
        insight = client.waap.domains.insights.replace(
            insight_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            domain_id=1,
            status="OPEN",
        )
        assert_matches_type(WaapInsight, insight, path=["response"])

    @parametrize
    def test_raw_response_replace(self, client: Gcore) -> None:
        response = client.waap.domains.insights.with_raw_response.replace(
            insight_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            domain_id=1,
            status="OPEN",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        insight = response.parse()
        assert_matches_type(WaapInsight, insight, path=["response"])

    @parametrize
    def test_streaming_response_replace(self, client: Gcore) -> None:
        with client.waap.domains.insights.with_streaming_response.replace(
            insight_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            domain_id=1,
            status="OPEN",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            insight = response.parse()
            assert_matches_type(WaapInsight, insight, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_replace(self, client: Gcore) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `insight_id` but received ''"):
            client.waap.domains.insights.with_raw_response.replace(
                insight_id="",
                domain_id=1,
                status="OPEN",
            )


class TestAsyncInsights:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_list(self, async_client: AsyncGcore) -> None:
        insight = await async_client.waap.domains.insights.list(
            domain_id=1,
        )
        assert_matches_type(AsyncOffsetPage[WaapInsight], insight, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncGcore) -> None:
        insight = await async_client.waap.domains.insights.list(
            domain_id=1,
            id=["182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e", "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e"],
            description="description",
            insight_type=["string", "string"],
            limit=0,
            offset=0,
            ordering="id",
            status=["OPEN", "ACKED"],
        )
        assert_matches_type(AsyncOffsetPage[WaapInsight], insight, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncGcore) -> None:
        response = await async_client.waap.domains.insights.with_raw_response.list(
            domain_id=1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        insight = await response.parse()
        assert_matches_type(AsyncOffsetPage[WaapInsight], insight, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncGcore) -> None:
        async with async_client.waap.domains.insights.with_streaming_response.list(
            domain_id=1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            insight = await response.parse()
            assert_matches_type(AsyncOffsetPage[WaapInsight], insight, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get(self, async_client: AsyncGcore) -> None:
        insight = await async_client.waap.domains.insights.get(
            insight_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            domain_id=1,
        )
        assert_matches_type(WaapInsight, insight, path=["response"])

    @parametrize
    async def test_raw_response_get(self, async_client: AsyncGcore) -> None:
        response = await async_client.waap.domains.insights.with_raw_response.get(
            insight_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            domain_id=1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        insight = await response.parse()
        assert_matches_type(WaapInsight, insight, path=["response"])

    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncGcore) -> None:
        async with async_client.waap.domains.insights.with_streaming_response.get(
            insight_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            domain_id=1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            insight = await response.parse()
            assert_matches_type(WaapInsight, insight, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_get(self, async_client: AsyncGcore) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `insight_id` but received ''"):
            await async_client.waap.domains.insights.with_raw_response.get(
                insight_id="",
                domain_id=1,
            )

    @parametrize
    async def test_method_replace(self, async_client: AsyncGcore) -> None:
        insight = await async_client.waap.domains.insights.replace(
            insight_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            domain_id=1,
            status="OPEN",
        )
        assert_matches_type(WaapInsight, insight, path=["response"])

    @parametrize
    async def test_raw_response_replace(self, async_client: AsyncGcore) -> None:
        response = await async_client.waap.domains.insights.with_raw_response.replace(
            insight_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            domain_id=1,
            status="OPEN",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        insight = await response.parse()
        assert_matches_type(WaapInsight, insight, path=["response"])

    @parametrize
    async def test_streaming_response_replace(self, async_client: AsyncGcore) -> None:
        async with async_client.waap.domains.insights.with_streaming_response.replace(
            insight_id="182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
            domain_id=1,
            status="OPEN",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            insight = await response.parse()
            assert_matches_type(WaapInsight, insight, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_replace(self, async_client: AsyncGcore) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `insight_id` but received ''"):
            await async_client.waap.domains.insights.with_raw_response.replace(
                insight_id="",
                domain_id=1,
                status="OPEN",
            )

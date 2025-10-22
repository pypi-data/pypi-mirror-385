# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from gcore import Gcore, AsyncGcore
from tests.utils import assert_matches_type
from gcore.pagination import SyncOffsetPage, AsyncOffsetPage
from gcore.types.cloud.inference.deployments import InferenceDeploymentLog

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestLogs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_list(self, client: Gcore) -> None:
        log = client.cloud.inference.deployments.logs.list(
            deployment_name="my-instance",
            project_id=1,
        )
        assert_matches_type(SyncOffsetPage[InferenceDeploymentLog], log, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Gcore) -> None:
        log = client.cloud.inference.deployments.logs.list(
            deployment_name="my-instance",
            project_id=1,
            limit=1000,
            offset=0,
            order_by="time.asc",
            region_id=1,
        )
        assert_matches_type(SyncOffsetPage[InferenceDeploymentLog], log, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Gcore) -> None:
        response = client.cloud.inference.deployments.logs.with_raw_response.list(
            deployment_name="my-instance",
            project_id=1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        log = response.parse()
        assert_matches_type(SyncOffsetPage[InferenceDeploymentLog], log, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Gcore) -> None:
        with client.cloud.inference.deployments.logs.with_streaming_response.list(
            deployment_name="my-instance",
            project_id=1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            log = response.parse()
            assert_matches_type(SyncOffsetPage[InferenceDeploymentLog], log, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_list(self, client: Gcore) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_name` but received ''"):
            client.cloud.inference.deployments.logs.with_raw_response.list(
                deployment_name="",
                project_id=1,
            )


class TestAsyncLogs:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_list(self, async_client: AsyncGcore) -> None:
        log = await async_client.cloud.inference.deployments.logs.list(
            deployment_name="my-instance",
            project_id=1,
        )
        assert_matches_type(AsyncOffsetPage[InferenceDeploymentLog], log, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncGcore) -> None:
        log = await async_client.cloud.inference.deployments.logs.list(
            deployment_name="my-instance",
            project_id=1,
            limit=1000,
            offset=0,
            order_by="time.asc",
            region_id=1,
        )
        assert_matches_type(AsyncOffsetPage[InferenceDeploymentLog], log, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncGcore) -> None:
        response = await async_client.cloud.inference.deployments.logs.with_raw_response.list(
            deployment_name="my-instance",
            project_id=1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        log = await response.parse()
        assert_matches_type(AsyncOffsetPage[InferenceDeploymentLog], log, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncGcore) -> None:
        async with async_client.cloud.inference.deployments.logs.with_streaming_response.list(
            deployment_name="my-instance",
            project_id=1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            log = await response.parse()
            assert_matches_type(AsyncOffsetPage[InferenceDeploymentLog], log, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_list(self, async_client: AsyncGcore) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `deployment_name` but received ''"):
            await async_client.cloud.inference.deployments.logs.with_raw_response.list(
                deployment_name="",
                project_id=1,
            )

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from gcore import Gcore, AsyncGcore
from tests.utils import assert_matches_type
from gcore.pagination import SyncOffsetPage, AsyncOffsetPage
from gcore.types.waap import (
    WaapPolicyMode,
    WaapSummaryDomain,
    WaapDetailedDomain,
    DomainListRuleSetsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDomains:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_update(self, client: Gcore) -> None:
        domain = client.waap.domains.update(
            domain_id=1,
            status="active",
        )
        assert domain is None

    @parametrize
    def test_raw_response_update(self, client: Gcore) -> None:
        response = client.waap.domains.with_raw_response.update(
            domain_id=1,
            status="active",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        domain = response.parse()
        assert domain is None

    @parametrize
    def test_streaming_response_update(self, client: Gcore) -> None:
        with client.waap.domains.with_streaming_response.update(
            domain_id=1,
            status="active",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            domain = response.parse()
            assert domain is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list(self, client: Gcore) -> None:
        domain = client.waap.domains.list()
        assert_matches_type(SyncOffsetPage[WaapSummaryDomain], domain, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Gcore) -> None:
        domain = client.waap.domains.list(
            ids=[1],
            limit=0,
            name="*example.com",
            offset=0,
            ordering="id",
            status="active",
        )
        assert_matches_type(SyncOffsetPage[WaapSummaryDomain], domain, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Gcore) -> None:
        response = client.waap.domains.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        domain = response.parse()
        assert_matches_type(SyncOffsetPage[WaapSummaryDomain], domain, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Gcore) -> None:
        with client.waap.domains.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            domain = response.parse()
            assert_matches_type(SyncOffsetPage[WaapSummaryDomain], domain, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: Gcore) -> None:
        domain = client.waap.domains.delete(
            1,
        )
        assert domain is None

    @parametrize
    def test_raw_response_delete(self, client: Gcore) -> None:
        response = client.waap.domains.with_raw_response.delete(
            1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        domain = response.parse()
        assert domain is None

    @parametrize
    def test_streaming_response_delete(self, client: Gcore) -> None:
        with client.waap.domains.with_streaming_response.delete(
            1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            domain = response.parse()
            assert domain is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get(self, client: Gcore) -> None:
        domain = client.waap.domains.get(
            1,
        )
        assert_matches_type(WaapDetailedDomain, domain, path=["response"])

    @parametrize
    def test_raw_response_get(self, client: Gcore) -> None:
        response = client.waap.domains.with_raw_response.get(
            1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        domain = response.parse()
        assert_matches_type(WaapDetailedDomain, domain, path=["response"])

    @parametrize
    def test_streaming_response_get(self, client: Gcore) -> None:
        with client.waap.domains.with_streaming_response.get(
            1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            domain = response.parse()
            assert_matches_type(WaapDetailedDomain, domain, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list_rule_sets(self, client: Gcore) -> None:
        domain = client.waap.domains.list_rule_sets(
            1,
        )
        assert_matches_type(DomainListRuleSetsResponse, domain, path=["response"])

    @parametrize
    def test_raw_response_list_rule_sets(self, client: Gcore) -> None:
        response = client.waap.domains.with_raw_response.list_rule_sets(
            1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        domain = response.parse()
        assert_matches_type(DomainListRuleSetsResponse, domain, path=["response"])

    @parametrize
    def test_streaming_response_list_rule_sets(self, client: Gcore) -> None:
        with client.waap.domains.with_streaming_response.list_rule_sets(
            1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            domain = response.parse()
            assert_matches_type(DomainListRuleSetsResponse, domain, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_toggle_policy(self, client: Gcore) -> None:
        domain = client.waap.domains.toggle_policy(
            policy_id="policy_id",
            domain_id=1,
        )
        assert_matches_type(WaapPolicyMode, domain, path=["response"])

    @parametrize
    def test_raw_response_toggle_policy(self, client: Gcore) -> None:
        response = client.waap.domains.with_raw_response.toggle_policy(
            policy_id="policy_id",
            domain_id=1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        domain = response.parse()
        assert_matches_type(WaapPolicyMode, domain, path=["response"])

    @parametrize
    def test_streaming_response_toggle_policy(self, client: Gcore) -> None:
        with client.waap.domains.with_streaming_response.toggle_policy(
            policy_id="policy_id",
            domain_id=1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            domain = response.parse()
            assert_matches_type(WaapPolicyMode, domain, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_path_params_toggle_policy(self, client: Gcore) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `policy_id` but received ''"):
            client.waap.domains.with_raw_response.toggle_policy(
                policy_id="",
                domain_id=1,
            )


class TestAsyncDomains:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_update(self, async_client: AsyncGcore) -> None:
        domain = await async_client.waap.domains.update(
            domain_id=1,
            status="active",
        )
        assert domain is None

    @parametrize
    async def test_raw_response_update(self, async_client: AsyncGcore) -> None:
        response = await async_client.waap.domains.with_raw_response.update(
            domain_id=1,
            status="active",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        domain = await response.parse()
        assert domain is None

    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncGcore) -> None:
        async with async_client.waap.domains.with_streaming_response.update(
            domain_id=1,
            status="active",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            domain = await response.parse()
            assert domain is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list(self, async_client: AsyncGcore) -> None:
        domain = await async_client.waap.domains.list()
        assert_matches_type(AsyncOffsetPage[WaapSummaryDomain], domain, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncGcore) -> None:
        domain = await async_client.waap.domains.list(
            ids=[1],
            limit=0,
            name="*example.com",
            offset=0,
            ordering="id",
            status="active",
        )
        assert_matches_type(AsyncOffsetPage[WaapSummaryDomain], domain, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncGcore) -> None:
        response = await async_client.waap.domains.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        domain = await response.parse()
        assert_matches_type(AsyncOffsetPage[WaapSummaryDomain], domain, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncGcore) -> None:
        async with async_client.waap.domains.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            domain = await response.parse()
            assert_matches_type(AsyncOffsetPage[WaapSummaryDomain], domain, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncGcore) -> None:
        domain = await async_client.waap.domains.delete(
            1,
        )
        assert domain is None

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncGcore) -> None:
        response = await async_client.waap.domains.with_raw_response.delete(
            1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        domain = await response.parse()
        assert domain is None

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncGcore) -> None:
        async with async_client.waap.domains.with_streaming_response.delete(
            1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            domain = await response.parse()
            assert domain is None

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get(self, async_client: AsyncGcore) -> None:
        domain = await async_client.waap.domains.get(
            1,
        )
        assert_matches_type(WaapDetailedDomain, domain, path=["response"])

    @parametrize
    async def test_raw_response_get(self, async_client: AsyncGcore) -> None:
        response = await async_client.waap.domains.with_raw_response.get(
            1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        domain = await response.parse()
        assert_matches_type(WaapDetailedDomain, domain, path=["response"])

    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncGcore) -> None:
        async with async_client.waap.domains.with_streaming_response.get(
            1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            domain = await response.parse()
            assert_matches_type(WaapDetailedDomain, domain, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list_rule_sets(self, async_client: AsyncGcore) -> None:
        domain = await async_client.waap.domains.list_rule_sets(
            1,
        )
        assert_matches_type(DomainListRuleSetsResponse, domain, path=["response"])

    @parametrize
    async def test_raw_response_list_rule_sets(self, async_client: AsyncGcore) -> None:
        response = await async_client.waap.domains.with_raw_response.list_rule_sets(
            1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        domain = await response.parse()
        assert_matches_type(DomainListRuleSetsResponse, domain, path=["response"])

    @parametrize
    async def test_streaming_response_list_rule_sets(self, async_client: AsyncGcore) -> None:
        async with async_client.waap.domains.with_streaming_response.list_rule_sets(
            1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            domain = await response.parse()
            assert_matches_type(DomainListRuleSetsResponse, domain, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_toggle_policy(self, async_client: AsyncGcore) -> None:
        domain = await async_client.waap.domains.toggle_policy(
            policy_id="policy_id",
            domain_id=1,
        )
        assert_matches_type(WaapPolicyMode, domain, path=["response"])

    @parametrize
    async def test_raw_response_toggle_policy(self, async_client: AsyncGcore) -> None:
        response = await async_client.waap.domains.with_raw_response.toggle_policy(
            policy_id="policy_id",
            domain_id=1,
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        domain = await response.parse()
        assert_matches_type(WaapPolicyMode, domain, path=["response"])

    @parametrize
    async def test_streaming_response_toggle_policy(self, async_client: AsyncGcore) -> None:
        async with async_client.waap.domains.with_streaming_response.toggle_policy(
            policy_id="policy_id",
            domain_id=1,
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            domain = await response.parse()
            assert_matches_type(WaapPolicyMode, domain, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_path_params_toggle_policy(self, async_client: AsyncGcore) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `policy_id` but received ''"):
            await async_client.waap.domains.with_raw_response.toggle_policy(
                policy_id="",
                domain_id=1,
            )

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ....._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from ....._utils import maybe_transform, async_maybe_transform
from ....._compat import cached_property
from ....._resource import SyncAPIResource, AsyncAPIResource
from ....._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....._base_client import make_request_options
from .....types.cloud.task_id_list import TaskIDList
from .....types.cloud.load_balancers.pools import member_add_params

__all__ = ["MembersResource", "AsyncMembersResource"]


class MembersResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MembersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/G-Core/gcore-python#accessing-raw-response-data-eg-headers
        """
        return MembersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MembersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/G-Core/gcore-python#with_streaming_response
        """
        return MembersResourceWithStreamingResponse(self)

    def add(
        self,
        pool_id: str,
        *,
        project_id: int | None = None,
        region_id: int | None = None,
        address: str,
        protocol_port: int,
        admin_state_up: bool | Omit = omit,
        backup: bool | Omit = omit,
        instance_id: Optional[str] | Omit = omit,
        monitor_address: Optional[str] | Omit = omit,
        monitor_port: Optional[int] | Omit = omit,
        subnet_id: Optional[str] | Omit = omit,
        weight: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskIDList:
        """
        Create load balancer pool member

        Args:
          project_id: Project ID

          region_id: Region ID

          pool_id: Pool ID

          address: Member IP address

          protocol_port: Member IP port

          admin_state_up: Administrative state of the resource. When set to true, the resource is enabled
              and operational. When set to false, the resource is disabled and will not
              process traffic. When null is passed, the value is skipped and defaults to true.

          backup: Set to true if the member is a backup member, to which traffic will be sent
              exclusively when all non-backup members will be unreachable. It allows to
              realize ACTIVE-BACKUP load balancing without thinking about VRRP and VIP
              configuration. Default is false.

          instance_id: Either `subnet_id` or `instance_id` should be provided

          monitor_address: An alternate IP address used for health monitoring of a backend member. Default
              is null which monitors the member address.

          monitor_port: An alternate protocol port used for health monitoring of a backend member.
              Default is null which monitors the member `protocol_port`.

          subnet_id: `subnet_id` in which `address` is present. Either `subnet_id` or `instance_id`
              should be provided

          weight: Member weight. Valid values are 0 < `weight` <= 256, defaults to 1. Controls
              traffic distribution based on the pool's load balancing algorithm:

              - `ROUND_ROBIN`: Distributes connections to each member in turn according to
                weights. Higher weight = more turns in the cycle. Example: weights 3 vs 1 =
                ~75% vs ~25% of requests.
              - `LEAST_CONNECTIONS`: Sends new connections to the member with fewest active
                connections, performing round-robin within groups of the same normalized load.
                Higher weight = allowed to hold more simultaneous connections before being
                considered 'more loaded'. Example: weights 2 vs 1 means 20 vs 10 active
                connections is treated as balanced.
              - `SOURCE_IP`: Routes clients consistently to the same member by hashing client
                source IP; hash result is modulo total weight of running members. Higher
                weight = more hash buckets, so more client IPs map to that member. Example:
                weights 2 vs 1 = roughly two-thirds of distinct client IPs map to the
                higher-weight member.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_cloud_project_id_path_param()
        if region_id is None:
            region_id = self._client._get_cloud_region_id_path_param()
        if not pool_id:
            raise ValueError(f"Expected a non-empty value for `pool_id` but received {pool_id!r}")
        return self._post(
            f"/cloud/v1/lbpools/{project_id}/{region_id}/{pool_id}/member",
            body=maybe_transform(
                {
                    "address": address,
                    "protocol_port": protocol_port,
                    "admin_state_up": admin_state_up,
                    "backup": backup,
                    "instance_id": instance_id,
                    "monitor_address": monitor_address,
                    "monitor_port": monitor_port,
                    "subnet_id": subnet_id,
                    "weight": weight,
                },
                member_add_params.MemberAddParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskIDList,
        )

    def remove(
        self,
        member_id: str,
        *,
        project_id: int | None = None,
        region_id: int | None = None,
        pool_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskIDList:
        """
        Delete load balancer pool member

        Args:
          project_id: Project ID

          region_id: Region ID

          pool_id: Pool ID

          member_id: Member ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_cloud_project_id_path_param()
        if region_id is None:
            region_id = self._client._get_cloud_region_id_path_param()
        if not pool_id:
            raise ValueError(f"Expected a non-empty value for `pool_id` but received {pool_id!r}")
        if not member_id:
            raise ValueError(f"Expected a non-empty value for `member_id` but received {member_id!r}")
        return self._delete(
            f"/cloud/v1/lbpools/{project_id}/{region_id}/{pool_id}/member/{member_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskIDList,
        )


class AsyncMembersResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMembersResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/G-Core/gcore-python#accessing-raw-response-data-eg-headers
        """
        return AsyncMembersResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMembersResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/G-Core/gcore-python#with_streaming_response
        """
        return AsyncMembersResourceWithStreamingResponse(self)

    async def add(
        self,
        pool_id: str,
        *,
        project_id: int | None = None,
        region_id: int | None = None,
        address: str,
        protocol_port: int,
        admin_state_up: bool | Omit = omit,
        backup: bool | Omit = omit,
        instance_id: Optional[str] | Omit = omit,
        monitor_address: Optional[str] | Omit = omit,
        monitor_port: Optional[int] | Omit = omit,
        subnet_id: Optional[str] | Omit = omit,
        weight: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskIDList:
        """
        Create load balancer pool member

        Args:
          project_id: Project ID

          region_id: Region ID

          pool_id: Pool ID

          address: Member IP address

          protocol_port: Member IP port

          admin_state_up: Administrative state of the resource. When set to true, the resource is enabled
              and operational. When set to false, the resource is disabled and will not
              process traffic. When null is passed, the value is skipped and defaults to true.

          backup: Set to true if the member is a backup member, to which traffic will be sent
              exclusively when all non-backup members will be unreachable. It allows to
              realize ACTIVE-BACKUP load balancing without thinking about VRRP and VIP
              configuration. Default is false.

          instance_id: Either `subnet_id` or `instance_id` should be provided

          monitor_address: An alternate IP address used for health monitoring of a backend member. Default
              is null which monitors the member address.

          monitor_port: An alternate protocol port used for health monitoring of a backend member.
              Default is null which monitors the member `protocol_port`.

          subnet_id: `subnet_id` in which `address` is present. Either `subnet_id` or `instance_id`
              should be provided

          weight: Member weight. Valid values are 0 < `weight` <= 256, defaults to 1. Controls
              traffic distribution based on the pool's load balancing algorithm:

              - `ROUND_ROBIN`: Distributes connections to each member in turn according to
                weights. Higher weight = more turns in the cycle. Example: weights 3 vs 1 =
                ~75% vs ~25% of requests.
              - `LEAST_CONNECTIONS`: Sends new connections to the member with fewest active
                connections, performing round-robin within groups of the same normalized load.
                Higher weight = allowed to hold more simultaneous connections before being
                considered 'more loaded'. Example: weights 2 vs 1 means 20 vs 10 active
                connections is treated as balanced.
              - `SOURCE_IP`: Routes clients consistently to the same member by hashing client
                source IP; hash result is modulo total weight of running members. Higher
                weight = more hash buckets, so more client IPs map to that member. Example:
                weights 2 vs 1 = roughly two-thirds of distinct client IPs map to the
                higher-weight member.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_cloud_project_id_path_param()
        if region_id is None:
            region_id = self._client._get_cloud_region_id_path_param()
        if not pool_id:
            raise ValueError(f"Expected a non-empty value for `pool_id` but received {pool_id!r}")
        return await self._post(
            f"/cloud/v1/lbpools/{project_id}/{region_id}/{pool_id}/member",
            body=await async_maybe_transform(
                {
                    "address": address,
                    "protocol_port": protocol_port,
                    "admin_state_up": admin_state_up,
                    "backup": backup,
                    "instance_id": instance_id,
                    "monitor_address": monitor_address,
                    "monitor_port": monitor_port,
                    "subnet_id": subnet_id,
                    "weight": weight,
                },
                member_add_params.MemberAddParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskIDList,
        )

    async def remove(
        self,
        member_id: str,
        *,
        project_id: int | None = None,
        region_id: int | None = None,
        pool_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TaskIDList:
        """
        Delete load balancer pool member

        Args:
          project_id: Project ID

          region_id: Region ID

          pool_id: Pool ID

          member_id: Member ID

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_cloud_project_id_path_param()
        if region_id is None:
            region_id = self._client._get_cloud_region_id_path_param()
        if not pool_id:
            raise ValueError(f"Expected a non-empty value for `pool_id` but received {pool_id!r}")
        if not member_id:
            raise ValueError(f"Expected a non-empty value for `member_id` but received {member_id!r}")
        return await self._delete(
            f"/cloud/v1/lbpools/{project_id}/{region_id}/{pool_id}/member/{member_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TaskIDList,
        )


class MembersResourceWithRawResponse:
    def __init__(self, members: MembersResource) -> None:
        self._members = members

        self.add = to_raw_response_wrapper(
            members.add,
        )
        self.remove = to_raw_response_wrapper(
            members.remove,
        )


class AsyncMembersResourceWithRawResponse:
    def __init__(self, members: AsyncMembersResource) -> None:
        self._members = members

        self.add = async_to_raw_response_wrapper(
            members.add,
        )
        self.remove = async_to_raw_response_wrapper(
            members.remove,
        )


class MembersResourceWithStreamingResponse:
    def __init__(self, members: MembersResource) -> None:
        self._members = members

        self.add = to_streamed_response_wrapper(
            members.add,
        )
        self.remove = to_streamed_response_wrapper(
            members.remove,
        )


class AsyncMembersResourceWithStreamingResponse:
    def __init__(self, members: AsyncMembersResource) -> None:
        self._members = members

        self.add = async_to_streamed_response_wrapper(
            members.add,
        )
        self.remove = async_to_streamed_response_wrapper(
            members.remove,
        )

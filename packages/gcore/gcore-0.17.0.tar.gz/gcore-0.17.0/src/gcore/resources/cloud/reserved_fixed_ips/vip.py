# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ...._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...._base_client import make_request_options
from ....types.cloud.reserved_fixed_ip import ReservedFixedIP
from ....types.cloud.reserved_fixed_ips import (
    vip_toggle_params,
    vip_update_connected_ports_params,
    vip_replace_connected_ports_params,
)
from ....types.cloud.reserved_fixed_ips.candidate_port_list import CandidatePortList
from ....types.cloud.reserved_fixed_ips.connected_port_list import ConnectedPortList

__all__ = ["VipResource", "AsyncVipResource"]


class VipResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> VipResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/G-Core/gcore-python#accessing-raw-response-data-eg-headers
        """
        return VipResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> VipResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/G-Core/gcore-python#with_streaming_response
        """
        return VipResourceWithStreamingResponse(self)

    def list_candidate_ports(
        self,
        port_id: str,
        *,
        project_id: int | None = None,
        region_id: int | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CandidatePortList:
        """
        List all instance ports that are available for connecting to a VIP.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_cloud_project_id_path_param()
        if region_id is None:
            region_id = self._client._get_cloud_region_id_path_param()
        if not port_id:
            raise ValueError(f"Expected a non-empty value for `port_id` but received {port_id!r}")
        return self._get(
            f"/cloud/v1/reserved_fixed_ips/{project_id}/{region_id}/{port_id}/available_devices",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CandidatePortList,
        )

    def list_connected_ports(
        self,
        port_id: str,
        *,
        project_id: int | None = None,
        region_id: int | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectedPortList:
        """
        List all instance ports that share a VIP.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_cloud_project_id_path_param()
        if region_id is None:
            region_id = self._client._get_cloud_region_id_path_param()
        if not port_id:
            raise ValueError(f"Expected a non-empty value for `port_id` but received {port_id!r}")
        return self._get(
            f"/cloud/v1/reserved_fixed_ips/{project_id}/{region_id}/{port_id}/connected_devices",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectedPortList,
        )

    def replace_connected_ports(
        self,
        port_id: str,
        *,
        project_id: int | None = None,
        region_id: int | None = None,
        port_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectedPortList:
        """
        Replace the list of instance ports that share a VIP.

        Args:
          port_ids: List of port IDs that will share one VIP

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_cloud_project_id_path_param()
        if region_id is None:
            region_id = self._client._get_cloud_region_id_path_param()
        if not port_id:
            raise ValueError(f"Expected a non-empty value for `port_id` but received {port_id!r}")
        return self._put(
            f"/cloud/v1/reserved_fixed_ips/{project_id}/{region_id}/{port_id}/connected_devices",
            body=maybe_transform(
                {"port_ids": port_ids}, vip_replace_connected_ports_params.VipReplaceConnectedPortsParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectedPortList,
        )

    def toggle(
        self,
        port_id: str,
        *,
        project_id: int | None = None,
        region_id: int | None = None,
        is_vip: bool,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ReservedFixedIP:
        """
        Update the VIP status of a reserved fixed IP.

        Args:
          is_vip: If reserved fixed IP should be a VIP

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_cloud_project_id_path_param()
        if region_id is None:
            region_id = self._client._get_cloud_region_id_path_param()
        if not port_id:
            raise ValueError(f"Expected a non-empty value for `port_id` but received {port_id!r}")
        return self._patch(
            f"/cloud/v1/reserved_fixed_ips/{project_id}/{region_id}/{port_id}",
            body=maybe_transform({"is_vip": is_vip}, vip_toggle_params.VipToggleParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ReservedFixedIP,
        )

    def update_connected_ports(
        self,
        port_id: str,
        *,
        project_id: int | None = None,
        region_id: int | None = None,
        port_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectedPortList:
        """
        Add instance ports to share a VIP.

        Args:
          port_ids: List of port IDs that will share one VIP

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_cloud_project_id_path_param()
        if region_id is None:
            region_id = self._client._get_cloud_region_id_path_param()
        if not port_id:
            raise ValueError(f"Expected a non-empty value for `port_id` but received {port_id!r}")
        return self._patch(
            f"/cloud/v1/reserved_fixed_ips/{project_id}/{region_id}/{port_id}/connected_devices",
            body=maybe_transform(
                {"port_ids": port_ids}, vip_update_connected_ports_params.VipUpdateConnectedPortsParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectedPortList,
        )


class AsyncVipResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncVipResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/G-Core/gcore-python#accessing-raw-response-data-eg-headers
        """
        return AsyncVipResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncVipResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/G-Core/gcore-python#with_streaming_response
        """
        return AsyncVipResourceWithStreamingResponse(self)

    async def list_candidate_ports(
        self,
        port_id: str,
        *,
        project_id: int | None = None,
        region_id: int | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CandidatePortList:
        """
        List all instance ports that are available for connecting to a VIP.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_cloud_project_id_path_param()
        if region_id is None:
            region_id = self._client._get_cloud_region_id_path_param()
        if not port_id:
            raise ValueError(f"Expected a non-empty value for `port_id` but received {port_id!r}")
        return await self._get(
            f"/cloud/v1/reserved_fixed_ips/{project_id}/{region_id}/{port_id}/available_devices",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=CandidatePortList,
        )

    async def list_connected_ports(
        self,
        port_id: str,
        *,
        project_id: int | None = None,
        region_id: int | None = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectedPortList:
        """
        List all instance ports that share a VIP.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_cloud_project_id_path_param()
        if region_id is None:
            region_id = self._client._get_cloud_region_id_path_param()
        if not port_id:
            raise ValueError(f"Expected a non-empty value for `port_id` but received {port_id!r}")
        return await self._get(
            f"/cloud/v1/reserved_fixed_ips/{project_id}/{region_id}/{port_id}/connected_devices",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectedPortList,
        )

    async def replace_connected_ports(
        self,
        port_id: str,
        *,
        project_id: int | None = None,
        region_id: int | None = None,
        port_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectedPortList:
        """
        Replace the list of instance ports that share a VIP.

        Args:
          port_ids: List of port IDs that will share one VIP

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_cloud_project_id_path_param()
        if region_id is None:
            region_id = self._client._get_cloud_region_id_path_param()
        if not port_id:
            raise ValueError(f"Expected a non-empty value for `port_id` but received {port_id!r}")
        return await self._put(
            f"/cloud/v1/reserved_fixed_ips/{project_id}/{region_id}/{port_id}/connected_devices",
            body=await async_maybe_transform(
                {"port_ids": port_ids}, vip_replace_connected_ports_params.VipReplaceConnectedPortsParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectedPortList,
        )

    async def toggle(
        self,
        port_id: str,
        *,
        project_id: int | None = None,
        region_id: int | None = None,
        is_vip: bool,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ReservedFixedIP:
        """
        Update the VIP status of a reserved fixed IP.

        Args:
          is_vip: If reserved fixed IP should be a VIP

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_cloud_project_id_path_param()
        if region_id is None:
            region_id = self._client._get_cloud_region_id_path_param()
        if not port_id:
            raise ValueError(f"Expected a non-empty value for `port_id` but received {port_id!r}")
        return await self._patch(
            f"/cloud/v1/reserved_fixed_ips/{project_id}/{region_id}/{port_id}",
            body=await async_maybe_transform({"is_vip": is_vip}, vip_toggle_params.VipToggleParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ReservedFixedIP,
        )

    async def update_connected_ports(
        self,
        port_id: str,
        *,
        project_id: int | None = None,
        region_id: int | None = None,
        port_ids: SequenceNotStr[str] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ConnectedPortList:
        """
        Add instance ports to share a VIP.

        Args:
          port_ids: List of port IDs that will share one VIP

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if project_id is None:
            project_id = self._client._get_cloud_project_id_path_param()
        if region_id is None:
            region_id = self._client._get_cloud_region_id_path_param()
        if not port_id:
            raise ValueError(f"Expected a non-empty value for `port_id` but received {port_id!r}")
        return await self._patch(
            f"/cloud/v1/reserved_fixed_ips/{project_id}/{region_id}/{port_id}/connected_devices",
            body=await async_maybe_transform(
                {"port_ids": port_ids}, vip_update_connected_ports_params.VipUpdateConnectedPortsParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ConnectedPortList,
        )


class VipResourceWithRawResponse:
    def __init__(self, vip: VipResource) -> None:
        self._vip = vip

        self.list_candidate_ports = to_raw_response_wrapper(
            vip.list_candidate_ports,
        )
        self.list_connected_ports = to_raw_response_wrapper(
            vip.list_connected_ports,
        )
        self.replace_connected_ports = to_raw_response_wrapper(
            vip.replace_connected_ports,
        )
        self.toggle = to_raw_response_wrapper(
            vip.toggle,
        )
        self.update_connected_ports = to_raw_response_wrapper(
            vip.update_connected_ports,
        )


class AsyncVipResourceWithRawResponse:
    def __init__(self, vip: AsyncVipResource) -> None:
        self._vip = vip

        self.list_candidate_ports = async_to_raw_response_wrapper(
            vip.list_candidate_ports,
        )
        self.list_connected_ports = async_to_raw_response_wrapper(
            vip.list_connected_ports,
        )
        self.replace_connected_ports = async_to_raw_response_wrapper(
            vip.replace_connected_ports,
        )
        self.toggle = async_to_raw_response_wrapper(
            vip.toggle,
        )
        self.update_connected_ports = async_to_raw_response_wrapper(
            vip.update_connected_ports,
        )


class VipResourceWithStreamingResponse:
    def __init__(self, vip: VipResource) -> None:
        self._vip = vip

        self.list_candidate_ports = to_streamed_response_wrapper(
            vip.list_candidate_ports,
        )
        self.list_connected_ports = to_streamed_response_wrapper(
            vip.list_connected_ports,
        )
        self.replace_connected_ports = to_streamed_response_wrapper(
            vip.replace_connected_ports,
        )
        self.toggle = to_streamed_response_wrapper(
            vip.toggle,
        )
        self.update_connected_ports = to_streamed_response_wrapper(
            vip.update_connected_ports,
        )


class AsyncVipResourceWithStreamingResponse:
    def __init__(self, vip: AsyncVipResource) -> None:
        self._vip = vip

        self.list_candidate_ports = async_to_streamed_response_wrapper(
            vip.list_candidate_ports,
        )
        self.list_connected_ports = async_to_streamed_response_wrapper(
            vip.list_connected_ports,
        )
        self.replace_connected_ports = async_to_streamed_response_wrapper(
            vip.replace_connected_ports,
        )
        self.toggle = async_to_streamed_response_wrapper(
            vip.toggle,
        )
        self.update_connected_ports = async_to_streamed_response_wrapper(
            vip.update_connected_ports,
        )

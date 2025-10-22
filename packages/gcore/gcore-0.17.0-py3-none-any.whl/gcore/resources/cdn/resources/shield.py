# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ...._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
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
from ....types.cdn.resources import shield_replace_params
from ....types.cdn.resources.origin_shielding import OriginShielding

__all__ = ["ShieldResource", "AsyncShieldResource"]


class ShieldResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ShieldResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/G-Core/gcore-python#accessing-raw-response-data-eg-headers
        """
        return ShieldResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ShieldResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/G-Core/gcore-python#with_streaming_response
        """
        return ShieldResourceWithStreamingResponse(self)

    def get(
        self,
        resource_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OriginShielding:
        """
        Get information about origin shielding.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            f"/cdn/resources/{resource_id}/shielding_v2",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OriginShielding,
        )

    def replace(
        self,
        resource_id: int,
        *,
        shielding_pop: Optional[int] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Change origin shielding settings or disabled origin shielding.

        Args:
          shielding_pop: Shielding location ID.

              If origin shielding is disabled, the parameter value is **null**.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._put(
            f"/cdn/resources/{resource_id}/shielding_v2",
            body=maybe_transform({"shielding_pop": shielding_pop}, shield_replace_params.ShieldReplaceParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncShieldResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncShieldResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/G-Core/gcore-python#accessing-raw-response-data-eg-headers
        """
        return AsyncShieldResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncShieldResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/G-Core/gcore-python#with_streaming_response
        """
        return AsyncShieldResourceWithStreamingResponse(self)

    async def get(
        self,
        resource_id: int,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OriginShielding:
        """
        Get information about origin shielding.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            f"/cdn/resources/{resource_id}/shielding_v2",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=OriginShielding,
        )

    async def replace(
        self,
        resource_id: int,
        *,
        shielding_pop: Optional[int] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> object:
        """
        Change origin shielding settings or disabled origin shielding.

        Args:
          shielding_pop: Shielding location ID.

              If origin shielding is disabled, the parameter value is **null**.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._put(
            f"/cdn/resources/{resource_id}/shielding_v2",
            body=await async_maybe_transform(
                {"shielding_pop": shielding_pop}, shield_replace_params.ShieldReplaceParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class ShieldResourceWithRawResponse:
    def __init__(self, shield: ShieldResource) -> None:
        self._shield = shield

        self.get = to_raw_response_wrapper(
            shield.get,
        )
        self.replace = to_raw_response_wrapper(
            shield.replace,
        )


class AsyncShieldResourceWithRawResponse:
    def __init__(self, shield: AsyncShieldResource) -> None:
        self._shield = shield

        self.get = async_to_raw_response_wrapper(
            shield.get,
        )
        self.replace = async_to_raw_response_wrapper(
            shield.replace,
        )


class ShieldResourceWithStreamingResponse:
    def __init__(self, shield: ShieldResource) -> None:
        self._shield = shield

        self.get = to_streamed_response_wrapper(
            shield.get,
        )
        self.replace = to_streamed_response_wrapper(
            shield.replace,
        )


class AsyncShieldResourceWithStreamingResponse:
    def __init__(self, shield: AsyncShieldResource) -> None:
        self._shield = shield

        self.get = async_to_streamed_response_wrapper(
            shield.get,
        )
        self.replace = async_to_streamed_response_wrapper(
            shield.replace,
        )

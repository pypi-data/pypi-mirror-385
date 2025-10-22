# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .metrics import (
    MetricsResource,
    AsyncMetricsResource,
    MetricsResourceWithRawResponse,
    AsyncMetricsResourceWithRawResponse,
    MetricsResourceWithStreamingResponse,
    AsyncMetricsResourceWithStreamingResponse,
)
from ...._types import Body, Query, Headers, NotGiven, not_given
from ...._utils import maybe_transform, async_maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource, AsyncAPIResource
from ...._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ....types.waap import (
    ip_info_get_ip_info_params,
    ip_info_get_top_urls_params,
    ip_info_get_top_user_agents_params,
    ip_info_get_blocked_requests_params,
    ip_info_get_top_user_sessions_params,
    ip_info_get_attack_time_series_params,
    ip_info_get_ddos_attack_series_params,
    ip_info_list_attacked_countries_params,
)
from ...._base_client import make_request_options
from ....types.waap.waap_ip_info import WaapIPInfo
from ....types.waap.waap_ip_ddos_info_model import WaapIPDDOSInfoModel
from ....types.waap.ip_info_get_top_urls_response import IPInfoGetTopURLsResponse
from ....types.waap.ip_info_get_top_user_agents_response import IPInfoGetTopUserAgentsResponse
from ....types.waap.ip_info_get_blocked_requests_response import IPInfoGetBlockedRequestsResponse
from ....types.waap.ip_info_get_top_user_sessions_response import IPInfoGetTopUserSessionsResponse
from ....types.waap.ip_info_get_attack_time_series_response import IPInfoGetAttackTimeSeriesResponse
from ....types.waap.ip_info_list_attacked_countries_response import IPInfoListAttackedCountriesResponse

__all__ = ["IPInfoResource", "AsyncIPInfoResource"]


class IPInfoResource(SyncAPIResource):
    @cached_property
    def metrics(self) -> MetricsResource:
        return MetricsResource(self._client)

    @cached_property
    def with_raw_response(self) -> IPInfoResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/G-Core/gcore-python#accessing-raw-response-data-eg-headers
        """
        return IPInfoResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> IPInfoResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/G-Core/gcore-python#with_streaming_response
        """
        return IPInfoResourceWithStreamingResponse(self)

    def get_attack_time_series(
        self,
        *,
        ip: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IPInfoGetAttackTimeSeriesResponse:
        """
        Retrieve a time-series of attacks originating from a specified IP address.

        Args:
          ip: The IP address to check

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/waap/v1/ip-info/attack-time-series",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"ip": ip}, ip_info_get_attack_time_series_params.IPInfoGetAttackTimeSeriesParams
                ),
            ),
            cast_to=IPInfoGetAttackTimeSeriesResponse,
        )

    def get_blocked_requests(
        self,
        *,
        domain_id: int,
        ip: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IPInfoGetBlockedRequestsResponse:
        """
        Retrieve metrics, which enumerate blocked requests originating from a specific
        IP to a domain, grouped by rule name and taken action. Each metric provides
        insights into the request count blocked under a specific rule and the
        corresponding action that was executed.

        Args:
          domain_id: The identifier for a domain. When specified, the response will exclusively
              contain data pertinent to the indicated domain, filtering out information from
              other domains.

          ip: The IP address to check

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/waap/v1/ip-info/blocked-requests",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "domain_id": domain_id,
                        "ip": ip,
                    },
                    ip_info_get_blocked_requests_params.IPInfoGetBlockedRequestsParams,
                ),
            ),
            cast_to=IPInfoGetBlockedRequestsResponse,
        )

    def get_ddos_attack_series(
        self,
        *,
        ip: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WaapIPDDOSInfoModel:
        """
        Fetch and analyze DDoS (Distributed Denial of Service) attack metrics for a
        specified IP address. The endpoint provides time-series data, enabling users to
        evaluate the frequency and intensity of attacks across various time intervals,
        and it returns metrics in Prometheus format to offer a systematic view of DDoS
        attack patterns.

        Args:
          ip: The IP address to check

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/waap/v1/ip-info/ddos",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"ip": ip}, ip_info_get_ddos_attack_series_params.IPInfoGetDDOSAttackSeriesParams
                ),
            ),
            cast_to=WaapIPDDOSInfoModel,
        )

    def get_ip_info(
        self,
        *,
        ip: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WaapIPInfo:
        """
        Fetch details about a particular IP address, including WHOIS data, risk score,
        and additional tags.

        Args:
          ip: The IP address to check

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/waap/v1/ip-info/ip-info",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"ip": ip}, ip_info_get_ip_info_params.IPInfoGetIPInfoParams),
            ),
            cast_to=WaapIPInfo,
        )

    def get_top_urls(
        self,
        *,
        domain_id: int,
        ip: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IPInfoGetTopURLsResponse:
        """
        Returns a list of the top 10 URLs accessed by a specified IP address within a
        specific domain. This data is vital to understand user navigation patterns,
        pinpoint high-traffic pages, and facilitate more targeted enhancements or
        security monitoring based on URL popularity.

        Args:
          domain_id: The identifier for a domain. When specified, the response will exclusively
              contain data pertinent to the indicated domain, filtering out information from
              other domains.

          ip: The IP address to check

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/waap/v1/ip-info/top-urls",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "domain_id": domain_id,
                        "ip": ip,
                    },
                    ip_info_get_top_urls_params.IPInfoGetTopURLsParams,
                ),
            ),
            cast_to=IPInfoGetTopURLsResponse,
        )

    def get_top_user_agents(
        self,
        *,
        domain_id: int,
        ip: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IPInfoGetTopUserAgentsResponse:
        """
        Retrieve the top 10 user agents interacting with a specified domain, filtered by
        IP.

        Args:
          domain_id: The identifier for a domain. When specified, the response will exclusively
              contain data pertinent to the indicated domain, filtering out information from
              other domains.

          ip: The IP address to check

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/waap/v1/ip-info/top-user-agents",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "domain_id": domain_id,
                        "ip": ip,
                    },
                    ip_info_get_top_user_agents_params.IPInfoGetTopUserAgentsParams,
                ),
            ),
            cast_to=IPInfoGetTopUserAgentsResponse,
        )

    def get_top_user_sessions(
        self,
        *,
        domain_id: int,
        ip: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IPInfoGetTopUserSessionsResponse:
        """
        Obtain the top 10 user sessions interfacing with a particular domain, identified
        by IP.

        Args:
          domain_id: The identifier for a domain. When specified, the response will exclusively
              contain data pertinent to the indicated domain, filtering out information from
              other domains.

          ip: The IP address to check

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/waap/v1/ip-info/top-sessions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "domain_id": domain_id,
                        "ip": ip,
                    },
                    ip_info_get_top_user_sessions_params.IPInfoGetTopUserSessionsParams,
                ),
            ),
            cast_to=IPInfoGetTopUserSessionsResponse,
        )

    def list_attacked_countries(
        self,
        *,
        ip: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IPInfoListAttackedCountriesResponse:
        """
        Retrieve a list of countries attacked by the specified IP address

        Args:
          ip: The IP address to check

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/waap/v1/ip-info/attack-map",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"ip": ip}, ip_info_list_attacked_countries_params.IPInfoListAttackedCountriesParams
                ),
            ),
            cast_to=IPInfoListAttackedCountriesResponse,
        )


class AsyncIPInfoResource(AsyncAPIResource):
    @cached_property
    def metrics(self) -> AsyncMetricsResource:
        return AsyncMetricsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncIPInfoResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/G-Core/gcore-python#accessing-raw-response-data-eg-headers
        """
        return AsyncIPInfoResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncIPInfoResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/G-Core/gcore-python#with_streaming_response
        """
        return AsyncIPInfoResourceWithStreamingResponse(self)

    async def get_attack_time_series(
        self,
        *,
        ip: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IPInfoGetAttackTimeSeriesResponse:
        """
        Retrieve a time-series of attacks originating from a specified IP address.

        Args:
          ip: The IP address to check

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/waap/v1/ip-info/attack-time-series",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"ip": ip}, ip_info_get_attack_time_series_params.IPInfoGetAttackTimeSeriesParams
                ),
            ),
            cast_to=IPInfoGetAttackTimeSeriesResponse,
        )

    async def get_blocked_requests(
        self,
        *,
        domain_id: int,
        ip: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IPInfoGetBlockedRequestsResponse:
        """
        Retrieve metrics, which enumerate blocked requests originating from a specific
        IP to a domain, grouped by rule name and taken action. Each metric provides
        insights into the request count blocked under a specific rule and the
        corresponding action that was executed.

        Args:
          domain_id: The identifier for a domain. When specified, the response will exclusively
              contain data pertinent to the indicated domain, filtering out information from
              other domains.

          ip: The IP address to check

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/waap/v1/ip-info/blocked-requests",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "domain_id": domain_id,
                        "ip": ip,
                    },
                    ip_info_get_blocked_requests_params.IPInfoGetBlockedRequestsParams,
                ),
            ),
            cast_to=IPInfoGetBlockedRequestsResponse,
        )

    async def get_ddos_attack_series(
        self,
        *,
        ip: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WaapIPDDOSInfoModel:
        """
        Fetch and analyze DDoS (Distributed Denial of Service) attack metrics for a
        specified IP address. The endpoint provides time-series data, enabling users to
        evaluate the frequency and intensity of attacks across various time intervals,
        and it returns metrics in Prometheus format to offer a systematic view of DDoS
        attack patterns.

        Args:
          ip: The IP address to check

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/waap/v1/ip-info/ddos",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"ip": ip}, ip_info_get_ddos_attack_series_params.IPInfoGetDDOSAttackSeriesParams
                ),
            ),
            cast_to=WaapIPDDOSInfoModel,
        )

    async def get_ip_info(
        self,
        *,
        ip: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> WaapIPInfo:
        """
        Fetch details about a particular IP address, including WHOIS data, risk score,
        and additional tags.

        Args:
          ip: The IP address to check

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/waap/v1/ip-info/ip-info",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"ip": ip}, ip_info_get_ip_info_params.IPInfoGetIPInfoParams),
            ),
            cast_to=WaapIPInfo,
        )

    async def get_top_urls(
        self,
        *,
        domain_id: int,
        ip: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IPInfoGetTopURLsResponse:
        """
        Returns a list of the top 10 URLs accessed by a specified IP address within a
        specific domain. This data is vital to understand user navigation patterns,
        pinpoint high-traffic pages, and facilitate more targeted enhancements or
        security monitoring based on URL popularity.

        Args:
          domain_id: The identifier for a domain. When specified, the response will exclusively
              contain data pertinent to the indicated domain, filtering out information from
              other domains.

          ip: The IP address to check

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/waap/v1/ip-info/top-urls",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "domain_id": domain_id,
                        "ip": ip,
                    },
                    ip_info_get_top_urls_params.IPInfoGetTopURLsParams,
                ),
            ),
            cast_to=IPInfoGetTopURLsResponse,
        )

    async def get_top_user_agents(
        self,
        *,
        domain_id: int,
        ip: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IPInfoGetTopUserAgentsResponse:
        """
        Retrieve the top 10 user agents interacting with a specified domain, filtered by
        IP.

        Args:
          domain_id: The identifier for a domain. When specified, the response will exclusively
              contain data pertinent to the indicated domain, filtering out information from
              other domains.

          ip: The IP address to check

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/waap/v1/ip-info/top-user-agents",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "domain_id": domain_id,
                        "ip": ip,
                    },
                    ip_info_get_top_user_agents_params.IPInfoGetTopUserAgentsParams,
                ),
            ),
            cast_to=IPInfoGetTopUserAgentsResponse,
        )

    async def get_top_user_sessions(
        self,
        *,
        domain_id: int,
        ip: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IPInfoGetTopUserSessionsResponse:
        """
        Obtain the top 10 user sessions interfacing with a particular domain, identified
        by IP.

        Args:
          domain_id: The identifier for a domain. When specified, the response will exclusively
              contain data pertinent to the indicated domain, filtering out information from
              other domains.

          ip: The IP address to check

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/waap/v1/ip-info/top-sessions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "domain_id": domain_id,
                        "ip": ip,
                    },
                    ip_info_get_top_user_sessions_params.IPInfoGetTopUserSessionsParams,
                ),
            ),
            cast_to=IPInfoGetTopUserSessionsResponse,
        )

    async def list_attacked_countries(
        self,
        *,
        ip: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> IPInfoListAttackedCountriesResponse:
        """
        Retrieve a list of countries attacked by the specified IP address

        Args:
          ip: The IP address to check

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/waap/v1/ip-info/attack-map",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"ip": ip}, ip_info_list_attacked_countries_params.IPInfoListAttackedCountriesParams
                ),
            ),
            cast_to=IPInfoListAttackedCountriesResponse,
        )


class IPInfoResourceWithRawResponse:
    def __init__(self, ip_info: IPInfoResource) -> None:
        self._ip_info = ip_info

        self.get_attack_time_series = to_raw_response_wrapper(
            ip_info.get_attack_time_series,
        )
        self.get_blocked_requests = to_raw_response_wrapper(
            ip_info.get_blocked_requests,
        )
        self.get_ddos_attack_series = to_raw_response_wrapper(
            ip_info.get_ddos_attack_series,
        )
        self.get_ip_info = to_raw_response_wrapper(
            ip_info.get_ip_info,
        )
        self.get_top_urls = to_raw_response_wrapper(
            ip_info.get_top_urls,
        )
        self.get_top_user_agents = to_raw_response_wrapper(
            ip_info.get_top_user_agents,
        )
        self.get_top_user_sessions = to_raw_response_wrapper(
            ip_info.get_top_user_sessions,
        )
        self.list_attacked_countries = to_raw_response_wrapper(
            ip_info.list_attacked_countries,
        )

    @cached_property
    def metrics(self) -> MetricsResourceWithRawResponse:
        return MetricsResourceWithRawResponse(self._ip_info.metrics)


class AsyncIPInfoResourceWithRawResponse:
    def __init__(self, ip_info: AsyncIPInfoResource) -> None:
        self._ip_info = ip_info

        self.get_attack_time_series = async_to_raw_response_wrapper(
            ip_info.get_attack_time_series,
        )
        self.get_blocked_requests = async_to_raw_response_wrapper(
            ip_info.get_blocked_requests,
        )
        self.get_ddos_attack_series = async_to_raw_response_wrapper(
            ip_info.get_ddos_attack_series,
        )
        self.get_ip_info = async_to_raw_response_wrapper(
            ip_info.get_ip_info,
        )
        self.get_top_urls = async_to_raw_response_wrapper(
            ip_info.get_top_urls,
        )
        self.get_top_user_agents = async_to_raw_response_wrapper(
            ip_info.get_top_user_agents,
        )
        self.get_top_user_sessions = async_to_raw_response_wrapper(
            ip_info.get_top_user_sessions,
        )
        self.list_attacked_countries = async_to_raw_response_wrapper(
            ip_info.list_attacked_countries,
        )

    @cached_property
    def metrics(self) -> AsyncMetricsResourceWithRawResponse:
        return AsyncMetricsResourceWithRawResponse(self._ip_info.metrics)


class IPInfoResourceWithStreamingResponse:
    def __init__(self, ip_info: IPInfoResource) -> None:
        self._ip_info = ip_info

        self.get_attack_time_series = to_streamed_response_wrapper(
            ip_info.get_attack_time_series,
        )
        self.get_blocked_requests = to_streamed_response_wrapper(
            ip_info.get_blocked_requests,
        )
        self.get_ddos_attack_series = to_streamed_response_wrapper(
            ip_info.get_ddos_attack_series,
        )
        self.get_ip_info = to_streamed_response_wrapper(
            ip_info.get_ip_info,
        )
        self.get_top_urls = to_streamed_response_wrapper(
            ip_info.get_top_urls,
        )
        self.get_top_user_agents = to_streamed_response_wrapper(
            ip_info.get_top_user_agents,
        )
        self.get_top_user_sessions = to_streamed_response_wrapper(
            ip_info.get_top_user_sessions,
        )
        self.list_attacked_countries = to_streamed_response_wrapper(
            ip_info.list_attacked_countries,
        )

    @cached_property
    def metrics(self) -> MetricsResourceWithStreamingResponse:
        return MetricsResourceWithStreamingResponse(self._ip_info.metrics)


class AsyncIPInfoResourceWithStreamingResponse:
    def __init__(self, ip_info: AsyncIPInfoResource) -> None:
        self._ip_info = ip_info

        self.get_attack_time_series = async_to_streamed_response_wrapper(
            ip_info.get_attack_time_series,
        )
        self.get_blocked_requests = async_to_streamed_response_wrapper(
            ip_info.get_blocked_requests,
        )
        self.get_ddos_attack_series = async_to_streamed_response_wrapper(
            ip_info.get_ddos_attack_series,
        )
        self.get_ip_info = async_to_streamed_response_wrapper(
            ip_info.get_ip_info,
        )
        self.get_top_urls = async_to_streamed_response_wrapper(
            ip_info.get_top_urls,
        )
        self.get_top_user_agents = async_to_streamed_response_wrapper(
            ip_info.get_top_user_agents,
        )
        self.get_top_user_sessions = async_to_streamed_response_wrapper(
            ip_info.get_top_user_sessions,
        )
        self.list_attacked_countries = async_to_streamed_response_wrapper(
            ip_info.list_attacked_countries,
        )

    @cached_property
    def metrics(self) -> AsyncMetricsResourceWithStreamingResponse:
        return AsyncMetricsResourceWithStreamingResponse(self._ip_info.metrics)

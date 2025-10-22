# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ..._utils import PropertyInfo

__all__ = ["StatisticGetResourceUsageAggregatedParams"]


class StatisticGetResourceUsageAggregatedParams(TypedDict, total=False):
    from_: Required[Annotated[str, PropertyInfo(alias="from")]]
    """Beginning of the requested time period (ISO 8601/RFC 3339 format, UTC.)

    Examples:

    - &from=2018-11-01T00:00:00.000
    - &from=2018-11-01
    """

    metrics: Required[str]
    """Types of statistics data.

    Possible values:

    - **`upstream_bytes`** – Traffic in bytes from an origin server to CDN servers
      or to origin shielding when used.
    - **`sent_bytes`** – Traffic in bytes from CDN servers to clients.
    - **`shield_bytes`** – Traffic in bytes from origin shielding to CDN servers.
    - **`backblaze_bytes`** - Traffic in bytes from Backblaze origin.
    - **`total_bytes`** – `shield_bytes`, `upstream_bytes` and `sent_bytes`
      combined.
    - **`cdn_bytes`** – `sent_bytes` and `shield_bytes` combined.
    - **requests** – Number of requests to edge servers.
    - **`responses_2xx`** – Number of 2xx response codes.
    - **`responses_3xx`** – Number of 3xx response codes.
    - **`responses_4xx`** – Number of 4xx response codes.
    - **`responses_5xx`** – Number of 5xx response codes.
    - **`responses_hit`** – Number of responses with the header Cache: HIT.
    - **`responses_miss`** – Number of responses with the header Cache: MISS.
    - **`response_types`** – Statistics by content type. It returns a number of
      responses for content with different MIME types.
    - **`cache_hit_traffic_ratio`** – Formula: 1 - `upstream_bytes` / `sent_bytes`.
      We deduct the non-cached traffic from the total traffic amount.
    - **`cache_hit_requests_ratio`** – Formula: `responses_hit` / requests. The
      share of sending cached content.
    - **`shield_traffic_ratio`** – Formula: (`shield_bytes` - `upstream_bytes`) /
      `shield_bytes`. The efficiency of the Origin Shielding: how much more traffic
      is sent from the Origin Shielding than from the origin.
    - **`image_processed`** - Number of images transformed on the Image optimization
      service.
    - **`request_time`** - Time elapsed between the first bytes of a request were
      processed and logging after the last bytes were sent to a user.
    - **`upstream_response_time`** - Number of milliseconds it took to receive a
      response from an origin. If upstream `response_time_` contains several
      indications for one request (in case of more than 1 origin), we summarize
      them. In case of aggregating several queries, the average of this amount is
      calculated.
    - **`95_percentile`** - Represents the 95th percentile of network bandwidth
      usage in bytes per second. This means that 95% of the time, the network
      resource usage was below this value.
    - **`max_bandwidth`** - The maximum network bandwidth that was used during the
      selected time represented in bytes per second.
    - **`min_bandwidth`** - The minimum network bandwidth that was used during the
      selected time represented in bytes per second.

    Metrics **`upstream_response_time`** and **`request_time`** should be requested
    separately from other metrics
    """

    service: Required[str]
    """Service name.

    Possible value:

    - CDN
    """

    to: Required[str]
    """End of the requested time period (ISO 8601/RFC 3339 format, UTC.)

    Examples:

    - &to=2018-11-01T00:00:00.000
    - &to=2018-11-01
    """

    countries: str
    """Names of countries for which data is displayed.

    English short name from [ISO 3166 standard][1] without the definite article
    "the" should be used.

    [1]: https://www.iso.org/obp/ui/#search/code/

    To request multiple values, use:

    - &countries=france&countries=denmark
    """

    flat: bool
    """The waу the parameters are arranged in the response.

    Possible values:

    - **true** – Flat structure is used.
    - **false** – Embedded structure is used (default.)
    """

    group_by: str
    """Output data grouping.

    Possible values:

    - **resource** – Data is grouped by CDN resources IDs.
    - **region** – Data is grouped by regions of CDN edge servers.
    - **country** – Data is grouped by countries of CDN edge servers.
    - **vhost** – Data is grouped by resources CNAME.

    To request multiple values, use:

    - &`group_by`=region&`group_by`=resource
    """

    regions: str
    """Regions for which data is displayed.

    Possible values:

    - **na** – North America
    - **eu** – Europe
    - **cis** – Commonwealth of Independent States
    - **asia** – Asia
    - **au** – Australia
    - **latam** – Latin America
    - **me** – Middle East
    - **africa** - Africa
    - **sa** - South America
    """

    resource: int
    """CDN resources IDs by which statistics data is grouped.

    To request multiple values, use:

    - &resource=1&resource=2

    If CDN resource ID is not specified, data related to all CDN resources is
    returned.
    """

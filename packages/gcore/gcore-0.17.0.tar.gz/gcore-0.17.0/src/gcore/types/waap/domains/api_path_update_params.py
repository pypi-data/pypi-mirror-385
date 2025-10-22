# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from ...._types import SequenceNotStr

__all__ = ["APIPathUpdateParams"]


class APIPathUpdateParams(TypedDict, total=False):
    domain_id: Required[int]
    """The domain ID"""

    api_groups: SequenceNotStr[str]

    path: str
    """The updated API path.

    When updating the path, variables can be renamed, path parts can be converted to
    variables and vice versa.
    """

    status: Literal["CONFIRMED_API", "POTENTIAL_API", "NOT_API", "DELISTED_API"]
    """The different statuses an API path can have"""

    tags: SequenceNotStr[str]

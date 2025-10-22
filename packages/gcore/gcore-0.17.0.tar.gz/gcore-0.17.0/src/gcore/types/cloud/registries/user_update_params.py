# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["UserUpdateParams"]


class UserUpdateParams(TypedDict, total=False):
    project_id: int

    region_id: int

    registry_id: Required[int]

    duration: Required[int]
    """User account operating time, days"""

    read_only: bool
    """Read-only user"""

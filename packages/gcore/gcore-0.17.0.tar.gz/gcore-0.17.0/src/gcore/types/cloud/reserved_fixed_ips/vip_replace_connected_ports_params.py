# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

from ...._types import SequenceNotStr

__all__ = ["VipReplaceConnectedPortsParams"]


class VipReplaceConnectedPortsParams(TypedDict, total=False):
    project_id: int

    region_id: int

    port_ids: SequenceNotStr[str]
    """List of port IDs that will share one VIP"""

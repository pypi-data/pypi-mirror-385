# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import TypedDict

__all__ = ["TaskAcknowledgeAllParams"]


class TaskAcknowledgeAllParams(TypedDict, total=False):
    project_id: Optional[int]
    """Project ID"""

    region_id: Optional[int]
    """Region ID"""

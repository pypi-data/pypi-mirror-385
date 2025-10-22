# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["RunListEventsParams"]


class RunListEventsParams(TypedDict, total=False):
    cursor: str
    """Cursor from previous page"""

    limit: float
    """Maximum number of events to return"""

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Required, TypedDict

__all__ = ["TaskUpdateColumnParams"]


class TaskUpdateColumnParams(TypedDict, total=False):
    key: Required[str]
    """The column key to update or insert."""

    value: Required[Optional[str]]
    """The value to set for the column."""

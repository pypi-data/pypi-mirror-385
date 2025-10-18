# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from ...._models import BaseModel

__all__ = ["RunListEventsResponse", "Event"]


class Event(BaseModel):
    created_at: datetime = FieldInfo(alias="createdAt")

    type: Literal["log", "help-request"]

    data: Optional[object] = None


class RunListEventsResponse(BaseModel):
    events: List[Event]
    """Events for the browser agent run"""

    has_more: bool = FieldInfo(alias="hasMore")
    """Whether more events are available"""

    next_cursor: Optional[str] = FieldInfo(alias="nextCursor", default=None)
    """Cursor to fetch the next page"""

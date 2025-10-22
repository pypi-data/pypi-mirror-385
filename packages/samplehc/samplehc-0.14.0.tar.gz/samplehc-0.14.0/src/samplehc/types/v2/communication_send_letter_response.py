# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["CommunicationSendLetterResponse"]


class CommunicationSendLetterResponse(BaseModel):
    tracking_id: str = FieldInfo(alias="trackingId")
    """The letter ID for tracking the mail delivery"""

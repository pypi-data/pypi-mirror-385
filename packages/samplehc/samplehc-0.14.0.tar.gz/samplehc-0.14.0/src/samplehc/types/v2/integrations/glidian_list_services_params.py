# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["GlidianListServicesParams"]


class GlidianListServicesParams(TypedDict, total=False):
    insurance_id: Annotated[float, PropertyInfo(alias="insuranceId")]

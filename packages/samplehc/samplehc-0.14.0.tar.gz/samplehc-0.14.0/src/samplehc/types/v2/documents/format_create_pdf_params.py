# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from ...._utils import PropertyInfo

__all__ = ["FormatCreatePdfParams"]


class FormatCreatePdfParams(TypedDict, total=False):
    file_name: Required[Annotated[str, PropertyInfo(alias="fileName")]]

    mime_type: Required[Annotated[str, PropertyInfo(alias="mimeType")]]

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["RawUserGraphParams"]


class RawUserGraphParams(TypedDict, total=False):
    id: Required[str]
    """GitHub node ID or BountyLab ID of the user"""

    after: str
    """Cursor for pagination (opaque base64-encoded string from previous response)"""

    first: str
    """Number of items to return (default: 100, max: 100)"""

    include_attributes: Annotated[object, PropertyInfo(alias="includeAttributes")]
    """Optional graph relationships to include (varies based on relationship type)"""

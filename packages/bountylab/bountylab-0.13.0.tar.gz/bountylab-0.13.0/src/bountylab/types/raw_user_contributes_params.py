# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["RawUserContributesParams"]


class RawUserContributesParams(TypedDict, total=False):
    after: str
    """Cursor for pagination (opaque base64-encoded string from previous response)"""

    first: str
    """Number of items to return (default: 100, max: 100)"""

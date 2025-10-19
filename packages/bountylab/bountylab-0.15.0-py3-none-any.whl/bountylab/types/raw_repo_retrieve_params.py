# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = ["RawRepoRetrieveParams", "IncludeAttributes", "IncludeAttributesContributors", "IncludeAttributesStarrers"]


class RawRepoRetrieveParams(TypedDict, total=False):
    github_ids: Required[Annotated[SequenceNotStr[str], PropertyInfo(alias="githubIds")]]
    """Array of GitHub node IDs (1-100)"""

    include_attributes: Annotated[IncludeAttributes, PropertyInfo(alias="includeAttributes")]
    """Optional graph relationships to include (owner, contributors, starrers)"""


class IncludeAttributesContributors(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""


class IncludeAttributesStarrers(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""


class IncludeAttributes(TypedDict, total=False):
    contributors: IncludeAttributesContributors
    """Include repository contributors with cursor pagination"""

    owner: bool
    """Include repository owner information"""

    starrers: IncludeAttributesStarrers
    """Include users who starred the repository with cursor pagination"""

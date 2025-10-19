# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = [
    "RawUserGraphParams",
    "IncludeAttributes",
    "IncludeAttributesContributes",
    "IncludeAttributesContributors",
    "IncludeAttributesFollowers",
    "IncludeAttributesFollowing",
    "IncludeAttributesOwns",
    "IncludeAttributesStarrers",
    "IncludeAttributesStars",
]


class RawUserGraphParams(TypedDict, total=False):
    id: Required[str]
    """GitHub node ID or BountyLab ID of the user"""

    after: str
    """Cursor for pagination (opaque base64-encoded string from previous response)"""

    first: float
    """Number of items to return (default: 100, max: 100)"""

    include_attributes: Annotated[IncludeAttributes, PropertyInfo(alias="includeAttributes")]
    """Optional graph relationships to include.

    Use user attributes (followers, following, owns, stars, contributes) for
    user-returning relationships, or repo attributes (owner, contributors, starrers)
    for repo-returning relationships.
    """


class IncludeAttributesContributes(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""


class IncludeAttributesContributors(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""


class IncludeAttributesFollowers(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""


class IncludeAttributesFollowing(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""


class IncludeAttributesOwns(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""


class IncludeAttributesStarrers(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""


class IncludeAttributesStars(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""


class IncludeAttributes(TypedDict, total=False):
    contributes: IncludeAttributesContributes
    """Include contributed repositories with cursor pagination"""

    contributors: IncludeAttributesContributors
    """Include repository contributors with cursor pagination"""

    followers: IncludeAttributesFollowers
    """Include followers with cursor pagination"""

    following: IncludeAttributesFollowing
    """Include users this user follows with cursor pagination"""

    owner: bool
    """Include repository owner information"""

    owns: IncludeAttributesOwns
    """Include owned repositories with cursor pagination"""

    starrers: IncludeAttributesStarrers
    """Include users who starred the repository with cursor pagination"""

    stars: IncludeAttributesStars
    """Include starred repositories with cursor pagination"""

# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = [
    "RawUserByLoginParams",
    "IncludeAttributes",
    "IncludeAttributesContributes",
    "IncludeAttributesFollowers",
    "IncludeAttributesFollowing",
    "IncludeAttributesOwns",
    "IncludeAttributesStars",
]


class RawUserByLoginParams(TypedDict, total=False):
    logins: Required[SequenceNotStr[str]]
    """Array of GitHub usernames (1-100)"""

    include_attributes: Annotated[IncludeAttributes, PropertyInfo(alias="includeAttributes")]
    """
    Optional graph relationships to include (followers, following, stars, owns,
    contributes)
    """


class IncludeAttributesContributes(TypedDict, total=False):
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


class IncludeAttributesStars(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""


class IncludeAttributes(TypedDict, total=False):
    contributes: IncludeAttributesContributes
    """Include contributed repositories with cursor pagination"""

    followers: IncludeAttributesFollowers
    """Include followers with cursor pagination"""

    following: IncludeAttributesFollowing
    """Include users this user follows with cursor pagination"""

    owns: IncludeAttributesOwns
    """Include owned repositories with cursor pagination"""

    stars: IncludeAttributesStars
    """Include starred repositories with cursor pagination"""

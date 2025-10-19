# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo

__all__ = [
    "RawRepoGraphParams",
    "Variant0",
    "Variant0IncludeAttributes",
    "Variant0IncludeAttributesContributes",
    "Variant0IncludeAttributesFollowers",
    "Variant0IncludeAttributesFollowing",
    "Variant0IncludeAttributesOwns",
    "Variant0IncludeAttributesStars",
    "Variant1",
    "Variant1IncludeAttributes",
    "Variant1IncludeAttributesContributors",
    "Variant1IncludeAttributesStarrers",
]


class Variant0(TypedDict, total=False):
    id: Required[str]
    """GitHub node ID or BountyLab ID of the repository"""

    after: str
    """Cursor for pagination (opaque base64-encoded string from previous response)"""

    first: float
    """Number of items to return (default: 100, max: 100)"""

    include_attributes: Annotated[Variant0IncludeAttributes, PropertyInfo(alias="includeAttributes")]
    """
    Optional graph relationships to include (followers, following, stars, owns,
    contributes)
    """


class Variant0IncludeAttributesContributes(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""


class Variant0IncludeAttributesFollowers(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""


class Variant0IncludeAttributesFollowing(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""


class Variant0IncludeAttributesOwns(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""


class Variant0IncludeAttributesStars(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""


class Variant0IncludeAttributes(TypedDict, total=False):
    contributes: Variant0IncludeAttributesContributes
    """Include contributed repositories with cursor pagination"""

    followers: Variant0IncludeAttributesFollowers
    """Include followers with cursor pagination"""

    following: Variant0IncludeAttributesFollowing
    """Include users this user follows with cursor pagination"""

    owns: Variant0IncludeAttributesOwns
    """Include owned repositories with cursor pagination"""

    stars: Variant0IncludeAttributesStars
    """Include starred repositories with cursor pagination"""


class Variant1(TypedDict, total=False):
    id: Required[str]
    """GitHub node ID or BountyLab ID of the repository"""

    after: str
    """Cursor for pagination (opaque base64-encoded string from previous response)"""

    first: float
    """Number of items to return (default: 100, max: 100)"""

    include_attributes: Annotated[Variant1IncludeAttributes, PropertyInfo(alias="includeAttributes")]
    """Optional graph relationships to include (owner, contributors, starrers)"""


class Variant1IncludeAttributesContributors(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""


class Variant1IncludeAttributesStarrers(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""


class Variant1IncludeAttributes(TypedDict, total=False):
    contributors: Variant1IncludeAttributesContributors
    """Include repository contributors with cursor pagination"""

    owner: bool
    """Include repository owner information"""

    starrers: Variant1IncludeAttributesStarrers
    """Include users who starred the repository with cursor pagination"""


RawRepoGraphParams: TypeAlias = Union[Variant0, Variant1]

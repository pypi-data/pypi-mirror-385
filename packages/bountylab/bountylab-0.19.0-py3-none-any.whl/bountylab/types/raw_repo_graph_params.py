# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = [
    "RawRepoGraphParams",
    "IncludeAttributes",
    "IncludeAttributesContributes",
    "IncludeAttributesContributesFilters",
    "IncludeAttributesContributesFiltersUnionMember0",
    "IncludeAttributesContributesFiltersUnionMember1",
    "IncludeAttributesContributesFiltersUnionMember1Filter",
    "IncludeAttributesContributesFiltersUnionMember2",
    "IncludeAttributesContributesFiltersUnionMember2Filter",
    "IncludeAttributesContributesFiltersUnionMember2FilterUnionMember0",
    "IncludeAttributesContributesFiltersUnionMember2FilterUnionMember1",
    "IncludeAttributesContributesFiltersUnionMember2FilterUnionMember1Filter",
    "IncludeAttributesContributors",
    "IncludeAttributesContributorsFilters",
    "IncludeAttributesContributorsFiltersUnionMember0",
    "IncludeAttributesContributorsFiltersUnionMember1",
    "IncludeAttributesContributorsFiltersUnionMember1Filter",
    "IncludeAttributesContributorsFiltersUnionMember2",
    "IncludeAttributesContributorsFiltersUnionMember2Filter",
    "IncludeAttributesContributorsFiltersUnionMember2FilterUnionMember0",
    "IncludeAttributesContributorsFiltersUnionMember2FilterUnionMember1",
    "IncludeAttributesContributorsFiltersUnionMember2FilterUnionMember1Filter",
    "IncludeAttributesFollowers",
    "IncludeAttributesFollowersFilters",
    "IncludeAttributesFollowersFiltersUnionMember0",
    "IncludeAttributesFollowersFiltersUnionMember1",
    "IncludeAttributesFollowersFiltersUnionMember1Filter",
    "IncludeAttributesFollowersFiltersUnionMember2",
    "IncludeAttributesFollowersFiltersUnionMember2Filter",
    "IncludeAttributesFollowersFiltersUnionMember2FilterUnionMember0",
    "IncludeAttributesFollowersFiltersUnionMember2FilterUnionMember1",
    "IncludeAttributesFollowersFiltersUnionMember2FilterUnionMember1Filter",
    "IncludeAttributesFollowing",
    "IncludeAttributesFollowingFilters",
    "IncludeAttributesFollowingFiltersUnionMember0",
    "IncludeAttributesFollowingFiltersUnionMember1",
    "IncludeAttributesFollowingFiltersUnionMember1Filter",
    "IncludeAttributesFollowingFiltersUnionMember2",
    "IncludeAttributesFollowingFiltersUnionMember2Filter",
    "IncludeAttributesFollowingFiltersUnionMember2FilterUnionMember0",
    "IncludeAttributesFollowingFiltersUnionMember2FilterUnionMember1",
    "IncludeAttributesFollowingFiltersUnionMember2FilterUnionMember1Filter",
    "IncludeAttributesOwns",
    "IncludeAttributesOwnsFilters",
    "IncludeAttributesOwnsFiltersUnionMember0",
    "IncludeAttributesOwnsFiltersUnionMember1",
    "IncludeAttributesOwnsFiltersUnionMember1Filter",
    "IncludeAttributesOwnsFiltersUnionMember2",
    "IncludeAttributesOwnsFiltersUnionMember2Filter",
    "IncludeAttributesOwnsFiltersUnionMember2FilterUnionMember0",
    "IncludeAttributesOwnsFiltersUnionMember2FilterUnionMember1",
    "IncludeAttributesOwnsFiltersUnionMember2FilterUnionMember1Filter",
    "IncludeAttributesStarrers",
    "IncludeAttributesStarrersFilters",
    "IncludeAttributesStarrersFiltersUnionMember0",
    "IncludeAttributesStarrersFiltersUnionMember1",
    "IncludeAttributesStarrersFiltersUnionMember1Filter",
    "IncludeAttributesStarrersFiltersUnionMember2",
    "IncludeAttributesStarrersFiltersUnionMember2Filter",
    "IncludeAttributesStarrersFiltersUnionMember2FilterUnionMember0",
    "IncludeAttributesStarrersFiltersUnionMember2FilterUnionMember1",
    "IncludeAttributesStarrersFiltersUnionMember2FilterUnionMember1Filter",
    "IncludeAttributesStars",
    "IncludeAttributesStarsFilters",
    "IncludeAttributesStarsFiltersUnionMember0",
    "IncludeAttributesStarsFiltersUnionMember1",
    "IncludeAttributesStarsFiltersUnionMember1Filter",
    "IncludeAttributesStarsFiltersUnionMember2",
    "IncludeAttributesStarsFiltersUnionMember2Filter",
    "IncludeAttributesStarsFiltersUnionMember2FilterUnionMember0",
    "IncludeAttributesStarsFiltersUnionMember2FilterUnionMember1",
    "IncludeAttributesStarsFiltersUnionMember2FilterUnionMember1Filter",
]


class RawRepoGraphParams(TypedDict, total=False):
    id: Required[str]
    """GitHub node ID or BountyLab ID of the repository"""

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


class IncludeAttributesContributesFiltersUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributesFiltersUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributesFiltersUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesContributesFiltersUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesContributesFiltersUnionMember2FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributesFiltersUnionMember2FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributesFiltersUnionMember2FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesContributesFiltersUnionMember2FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesContributesFiltersUnionMember2Filter: TypeAlias = Union[
    IncludeAttributesContributesFiltersUnionMember2FilterUnionMember0,
    IncludeAttributesContributesFiltersUnionMember2FilterUnionMember1,
]


class IncludeAttributesContributesFiltersUnionMember2(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesContributesFiltersUnionMember2Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesContributesFilters: TypeAlias = Union[
    IncludeAttributesContributesFiltersUnionMember0,
    IncludeAttributesContributesFiltersUnionMember1,
    IncludeAttributesContributesFiltersUnionMember2,
]


class IncludeAttributesContributes(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""

    filters: IncludeAttributesContributesFilters
    """Optional filters for location-based filtering.

    Supports Eq (exact match), In (one of array), Like (partial match with %
    wildcards). Can combine filters with And/Or operators.
    """


class IncludeAttributesContributorsFiltersUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributorsFiltersUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributorsFiltersUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesContributorsFiltersUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesContributorsFiltersUnionMember2FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributorsFiltersUnionMember2FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesContributorsFiltersUnionMember2FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesContributorsFiltersUnionMember2FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesContributorsFiltersUnionMember2Filter: TypeAlias = Union[
    IncludeAttributesContributorsFiltersUnionMember2FilterUnionMember0,
    IncludeAttributesContributorsFiltersUnionMember2FilterUnionMember1,
]


class IncludeAttributesContributorsFiltersUnionMember2(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesContributorsFiltersUnionMember2Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesContributorsFilters: TypeAlias = Union[
    IncludeAttributesContributorsFiltersUnionMember0,
    IncludeAttributesContributorsFiltersUnionMember1,
    IncludeAttributesContributorsFiltersUnionMember2,
]


class IncludeAttributesContributors(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""

    filters: IncludeAttributesContributorsFilters
    """Optional filters for location-based filtering.

    Supports Eq (exact match), In (one of array), Like (partial match with %
    wildcards). Can combine filters with And/Or operators.
    """


class IncludeAttributesFollowersFiltersUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowersFiltersUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowersFiltersUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesFollowersFiltersUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesFollowersFiltersUnionMember2FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowersFiltersUnionMember2FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowersFiltersUnionMember2FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesFollowersFiltersUnionMember2FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesFollowersFiltersUnionMember2Filter: TypeAlias = Union[
    IncludeAttributesFollowersFiltersUnionMember2FilterUnionMember0,
    IncludeAttributesFollowersFiltersUnionMember2FilterUnionMember1,
]


class IncludeAttributesFollowersFiltersUnionMember2(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesFollowersFiltersUnionMember2Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesFollowersFilters: TypeAlias = Union[
    IncludeAttributesFollowersFiltersUnionMember0,
    IncludeAttributesFollowersFiltersUnionMember1,
    IncludeAttributesFollowersFiltersUnionMember2,
]


class IncludeAttributesFollowers(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""

    filters: IncludeAttributesFollowersFilters
    """Optional filters for location-based filtering.

    Supports Eq (exact match), In (one of array), Like (partial match with %
    wildcards). Can combine filters with And/Or operators.
    """


class IncludeAttributesFollowingFiltersUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowingFiltersUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowingFiltersUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesFollowingFiltersUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesFollowingFiltersUnionMember2FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowingFiltersUnionMember2FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesFollowingFiltersUnionMember2FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesFollowingFiltersUnionMember2FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesFollowingFiltersUnionMember2Filter: TypeAlias = Union[
    IncludeAttributesFollowingFiltersUnionMember2FilterUnionMember0,
    IncludeAttributesFollowingFiltersUnionMember2FilterUnionMember1,
]


class IncludeAttributesFollowingFiltersUnionMember2(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesFollowingFiltersUnionMember2Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesFollowingFilters: TypeAlias = Union[
    IncludeAttributesFollowingFiltersUnionMember0,
    IncludeAttributesFollowingFiltersUnionMember1,
    IncludeAttributesFollowingFiltersUnionMember2,
]


class IncludeAttributesFollowing(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""

    filters: IncludeAttributesFollowingFilters
    """Optional filters for location-based filtering.

    Supports Eq (exact match), In (one of array), Like (partial match with %
    wildcards). Can combine filters with And/Or operators.
    """


class IncludeAttributesOwnsFiltersUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesOwnsFiltersUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesOwnsFiltersUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesOwnsFiltersUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesOwnsFiltersUnionMember2FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesOwnsFiltersUnionMember2FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesOwnsFiltersUnionMember2FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesOwnsFiltersUnionMember2FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesOwnsFiltersUnionMember2Filter: TypeAlias = Union[
    IncludeAttributesOwnsFiltersUnionMember2FilterUnionMember0,
    IncludeAttributesOwnsFiltersUnionMember2FilterUnionMember1,
]


class IncludeAttributesOwnsFiltersUnionMember2(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesOwnsFiltersUnionMember2Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesOwnsFilters: TypeAlias = Union[
    IncludeAttributesOwnsFiltersUnionMember0,
    IncludeAttributesOwnsFiltersUnionMember1,
    IncludeAttributesOwnsFiltersUnionMember2,
]


class IncludeAttributesOwns(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""

    filters: IncludeAttributesOwnsFilters
    """Optional filters for location-based filtering.

    Supports Eq (exact match), In (one of array), Like (partial match with %
    wildcards). Can combine filters with And/Or operators.
    """


class IncludeAttributesStarrersFiltersUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarrersFiltersUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarrersFiltersUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesStarrersFiltersUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesStarrersFiltersUnionMember2FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarrersFiltersUnionMember2FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarrersFiltersUnionMember2FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesStarrersFiltersUnionMember2FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesStarrersFiltersUnionMember2Filter: TypeAlias = Union[
    IncludeAttributesStarrersFiltersUnionMember2FilterUnionMember0,
    IncludeAttributesStarrersFiltersUnionMember2FilterUnionMember1,
]


class IncludeAttributesStarrersFiltersUnionMember2(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesStarrersFiltersUnionMember2Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesStarrersFilters: TypeAlias = Union[
    IncludeAttributesStarrersFiltersUnionMember0,
    IncludeAttributesStarrersFiltersUnionMember1,
    IncludeAttributesStarrersFiltersUnionMember2,
]


class IncludeAttributesStarrers(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""

    filters: IncludeAttributesStarrersFilters
    """Optional filters for location-based filtering.

    Supports Eq (exact match), In (one of array), Like (partial match with %
    wildcards). Can combine filters with And/Or operators.
    """


class IncludeAttributesStarsFiltersUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarsFiltersUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarsFiltersUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesStarsFiltersUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


class IncludeAttributesStarsFiltersUnionMember2FilterUnionMember0(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarsFiltersUnionMember2FilterUnionMember1Filter(TypedDict, total=False):
    field: Required[Literal["resolvedCountry", "resolvedState", "resolvedCity"]]
    """Location field to filter on"""

    op: Required[Literal["Eq", "In", "Like"]]
    """
    Filter operator: Eq (exact match), In (one of array), Like (SQL LIKE with %
    wildcards)
    """

    value: Required[Union[str, SequenceNotStr[str]]]
    """Filter value - string for Eq/Like, array of strings for In"""


class IncludeAttributesStarsFiltersUnionMember2FilterUnionMember1(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesStarsFiltersUnionMember2FilterUnionMember1Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesStarsFiltersUnionMember2Filter: TypeAlias = Union[
    IncludeAttributesStarsFiltersUnionMember2FilterUnionMember0,
    IncludeAttributesStarsFiltersUnionMember2FilterUnionMember1,
]


class IncludeAttributesStarsFiltersUnionMember2(TypedDict, total=False):
    filters: Required[Iterable[IncludeAttributesStarsFiltersUnionMember2Filter]]

    op: Required[Literal["And", "Or"]]
    """Logical operator to combine filters"""


IncludeAttributesStarsFilters: TypeAlias = Union[
    IncludeAttributesStarsFiltersUnionMember0,
    IncludeAttributesStarsFiltersUnionMember1,
    IncludeAttributesStarsFiltersUnionMember2,
]


class IncludeAttributesStars(TypedDict, total=False):
    first: Required[int]
    """Number of items to return (max: 100)"""

    after: str
    """Cursor for pagination (opaque base64-encoded)"""

    filters: IncludeAttributesStarsFilters
    """Optional filters for location-based filtering.

    Supports Eq (exact match), In (one of array), Like (partial match with %
    wildcards). Can combine filters with And/Or operators.
    """


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

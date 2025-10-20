# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Iterable, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = [
    "SearchRepoSearchParams",
    "Filters",
    "FiltersGenericFieldFilter",
    "FiltersCompositeFilter",
    "FiltersCompositeFilterFilter",
    "IncludeAttributes",
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
]


class SearchRepoSearchParams(TypedDict, total=False):
    query: Required[str]
    """
    Natural language search query for semantic search across repository README and
    description using vector embeddings
    """

    filters: Optional[Filters]
    """Optional filters for narrowing search results.

    Supports filtering on: githubId, ownerLogin, ownerLocation, name,
    stargazerCount, language, totalIssuesCount, totalIssuesOpen, totalIssuesClosed,
    lastContributorLocations.

    Filter structure:

    - Field filters: { field: "fieldName", op: "Eq"|"In"|"Gte"|"Lte", value:
      string|number|array }
    - Composite filters: { op: "And"|"Or", filters: [...] }

    Supported operators:

    - String fields: Eq (exact match), In (one of array)
    - Number fields: Eq (exact), In (one of array), Gte (>=), Lte (<=)
    - Use And/Or to combine multiple filters
    """

    include_attributes: Annotated[IncludeAttributes, PropertyInfo(alias="includeAttributes")]
    """Optional graph relationships to include (owner, contributors, starrers)"""

    max_results: Annotated[int, PropertyInfo(alias="maxResults")]
    """Maximum number of results to return (default: 100, max: 1000)"""


class FiltersGenericFieldFilter(TypedDict, total=False):
    field: Required[str]
    """Field name to filter on"""

    op: Required[str]
    """Operation (Eq, In, Gte, etc.)"""

    value: Required[Union[str, float, SequenceNotStr[str], Iterable[float]]]
    """Filter value"""


class FiltersCompositeFilterFilter(TypedDict, total=False):
    field: Required[str]
    """Field name to filter on"""

    op: Required[str]
    """Operation (Eq, In, Gte, etc.)"""

    value: Required[Union[str, float, SequenceNotStr[str], Iterable[float]]]
    """Filter value"""


class FiltersCompositeFilter(TypedDict, total=False):
    filters: Required[Iterable[FiltersCompositeFilterFilter]]
    """Array of filters to combine"""

    op: Required[Literal["And", "Or"]]
    """Logical operator"""


Filters: TypeAlias = Union[FiltersGenericFieldFilter, FiltersCompositeFilter]


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


class IncludeAttributes(TypedDict, total=False):
    contributors: IncludeAttributesContributors
    """Include repository contributors with cursor pagination"""

    owner: bool
    """Include repository owner information"""

    starrers: IncludeAttributesStarrers
    """Include users who starred the repository with cursor pagination"""

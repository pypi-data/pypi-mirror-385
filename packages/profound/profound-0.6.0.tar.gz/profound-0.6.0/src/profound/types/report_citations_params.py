# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo
from .shared_params.pagination import Pagination

__all__ = ["ReportCitationsParams", "Filter"]


class ReportCitationsParams(TypedDict, total=False):
    category_id: Required[str]

    end_date: Required[Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]]
    """End date for the report.

    Accepts formats: YYYY-MM-DD, YYYY-MM-DD HH:MM, or full ISO timestamp.
    """

    metrics: Required[List[Literal["count", "share_of_voice"]]]

    start_date: Required[Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]]
    """Start date for the report.

    Accepts formats: YYYY-MM-DD, YYYY-MM-DD HH:MM, or full ISO timestamp.
    """

    date_interval: Literal["day", "week", "month", "year"]
    """Date interval for the report. (only used with date dimension)"""

    dimensions: List[
        Literal["hostname", "path", "date", "region", "topic", "model", "tag", "prompt", "url", "root_domain"]
    ]
    """Dimensions to group the report by."""

    filters: Iterable[Filter]
    """List of filters to apply to the report.

    Each filter has an operator, field, and value.
    """

    order_by: Dict[str, Literal["asc", "desc"]]
    """Custom ordering of the report results.

    The order is a record of key-value pairs where:

    - key is the field to order by, which can be a metric or dimension
    - value is the direction of the order, either 'asc' for ascending or 'desc' for
      descending.

    When not specified, the default order is the first metric in the query
    descending.
    """

    pagination: Pagination
    """Pagination settings for the report results."""


class Filter(TypedDict, total=False):
    field: Required[Literal["hostname", "path", "region", "topic", "model", "tag", "url", "root_domain", "prompt_type"]]

    operator: Required[
        Literal[
            "is",
            "not_is",
            "in",
            "not_in",
            "contains",
            "not_contains",
            "contains_case_insensitive",
            "not_contains_case_insensitive",
            "matches",
        ]
    ]

    value: Required[Union[str, SequenceNotStr[str], int, Iterable[int]]]
    """Value for the filter.

    Can be a single value or a list of depending on the operator.
    """

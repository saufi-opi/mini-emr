from enum import Enum
from fastapi import Query
from sqlmodel import SQLModel


# Pagination parameters
class PaginationParams:
    """
    Pagination parameters for list endpoints.

    Attributes:
        skip: Number of records to skip (offset)
        limit: Maximum number of records to return
    """

    def __init__(
        self,
        skip: int = Query(default=0, ge=0, description="Number of records to skip"),
        limit: int = Query(
            default=100, ge=0, le=1000, description="Maximum records to return"
        ),
    ):
        self.skip = skip
        self.limit = limit


# Sorting parameters
class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"

class SortParams:
    """
    Sorting parameters for list endpoints.

    Supports a sort string with optional "-" prefix for descending order.
    Example: "name" (ascending), "-created_at" (descending)

    Attributes:
        sort: Raw sort string from query
        field: The field name (without prefix)
        direction: The sort direction (asc or desc)
    """

    def __init__(
        self,
        sort: str = Query(
            default="created_at",
            description="Sort field. Prefix with - for descending (e.g., '-created_at')",
        ),
    ):
        self.sort = sort
        self.direction = SortDirection.ASC if not sort.startswith("-") else SortDirection.DESC
        self.field = sort.lstrip("+-")


# Search parameters
class SearchParams:
    """
    Search parameter for list endpoints.

    Attributes:
        search: Search query string (None if not provided)
    """

    def __init__(
        self,
        search: str | None = Query(
            default=None, description="Search query for text fields"
        ),
    ):
        self.search = search



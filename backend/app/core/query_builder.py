from sqlalchemy.ext.asyncio import AsyncSession
from app.core.schemas import SortDirection
from typing import Any, Generic, TypeVar
from sqlmodel import asc, desc, func, select, col, or_
from sqlmodel import SQLModel
from typing_extensions import Self
from pydantic import BaseModel

from app.core.schemas import PaginationParams, SortParams


# Query builder
T = TypeVar("T")

class QueryResult(BaseModel, Generic[T]):
    data: list[T]
    count: int

class QueryBuilder(Generic[T]):
    """
    Fluent query builder for list endpoints with automatic pagination, sorting, and counting.

    Usage:
        @router.get("/items")
        def list_items(
            session: SessionDep,
            pagination: PaginationParams = Depends(),
            sorting: SortParams = Depends(),
            search: str | None = Query(default=None),
            category: str | None = Query(default=None),
        ):
            builder = QueryBuilder(Item, session, pagination, sorting)

            # Add search (searches multiple fields)
            if search:
                builder.search(search, [Item.name, Item.description])

            # Add filters
            if category:
                builder.filter(Item.category == category)

            # Execute and return
            return builder.execute()  # Returns {"data": [...], "count": N}
    """

    def __init__(
        self,
        model: type[T],
        session: AsyncSession,
        pagination: PaginationParams | None = None,
        sorting: SortParams | None = None,
    ) -> None:
        """
        Initialize the query builder.

        Args:
            model: The SQLModel class to query
            session: Database session
            pagination: PaginationParams instance (optional, can be set via .paginate())
            sorting: SortParams instance (optional, can be set via .sort())
        """
        from sqlmodel import select

        self.model: type[T] = model
        self.session: AsyncSession = session
        self.pagination: PaginationParams | None = pagination
        self.sorting: SortParams | None = sorting
        self.sort_columns: dict[str, Any] = {}
        self.default_sort_column: Any = None
        self._query: Any = select(model)
        self._filters: list[Any] = []

    def paginate(self, pagination: PaginationParams) -> Self:
        """Set pagination parameters."""
        self.pagination = pagination
        return self

    def sort(
        self,
        sorting: SortParams,
        sort_columns: dict[str, Any] | list[Any] | None = None,
        default_sort_column: Any = None,
    ) -> Self:
        """
        Set sorting parameters.
        
        Args:
            sorting: SortParams instance
            sort_columns: Dict mapping name to column OR list of sortable column names
            default_sort_column: Column to use if sort field not found
        """
        self.sorting = sorting
        self.default_sort_column = default_sort_column

        if isinstance(sort_columns, dict):
            self.sort_columns = sort_columns
        elif isinstance(sort_columns, list):
            # Auto-generate dict from list of model fields or strings
            self.sort_columns = {}
            for col in sort_columns:
                if hasattr(col, "key"):  # SQLAlchemy Column/InstrumentedAttribute
                    self.sort_columns[col.key] = col
                elif isinstance(col, str) and hasattr(self.model, col):
                    self.sort_columns[col] = getattr(self.model, col)

        # If no sort columns provided, allow sorting by any model field that matches
        if not self.sort_columns and not sort_columns:
             pass # Logic handled in execute/get_sort_column

        return self

    def filter(self, *conditions: Any) -> Self:
        """Add filter conditions to the query."""
        for condition in conditions:
            self._query = self._query.where(condition)
        return self

    def search(self, term: str | None, columns: list[Any]) -> Self:
        """Add search across multiple columns using ILIKE."""

        if term:
            search_term = f"%{term}%"
            conditions = [col(column).ilike(search_term) for column in columns]
            self._query = self._query.where(or_(*conditions))
        return self

    async def execute(self) -> QueryResult[T]:
        """
        Execute the query with pagination and sorting.

        Returns:
            Dict with 'data' (list of results) and 'count' (total matching records)
        """

        if not self.pagination:
            raise ValueError("Pagination parameters must be set before execution")

        # Count total matching records (before pagination)
        count_query = select(func.count()).select_from(self._query.subquery())
        count_result = await self.session.execute(count_query)
        count = count_result.scalar_one()

        # Apply sorting
        if self.sorting:
            sort_column = self.sort_columns.get(
                self.sorting.field,
                self.default_sort_column
            )

            # Fallback: if no specific map, try to find field on model
            if sort_column is None and not self.sort_columns and hasattr(self.model, self.sorting.field):
                 sort_column = getattr(self.model, self.sorting.field)

            # Final fallback to created_at if exists
            if sort_column is None:
                 sort_column = getattr(self.model, "created_at", None)

            if sort_column is not None:
                if self.sorting.direction == SortDirection.DESC:
                    self._query = self._query.order_by(desc(sort_column))
                else:
                    self._query = self._query.order_by(asc(sort_column))

        # Apply pagination
        self._query = self._query.offset(self.pagination.skip).limit(
            self.pagination.limit
        )

        # Execute
        data_result = await self.session.execute(self._query)
        data = list(data_result.scalars().all())

        return QueryResult[T](data=data, count=count)

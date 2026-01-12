from typing import TypeVar

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.constants import DEFAULT_PAGE, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters for API requests."""

    page: int = DEFAULT_PAGE
    page_size: int = DEFAULT_PAGE_SIZE

    @property
    def offset(self) -> int:
        """Calculate offset for database query."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get limit for database query."""
        return self.page_size


class PageResponse[T](BaseModel):
    """Generic paginated response."""

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    @property
    def has_next(self) -> bool:
        """Check if there is a next page."""
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        """Check if there is a previous page."""
        return self.page > 1


def get_pagination_params(
    page: int = Query(DEFAULT_PAGE, ge=1, description="Page number"),
    page_size: int = Query(
        DEFAULT_PAGE_SIZE,
        ge=1,
        le=MAX_PAGE_SIZE,
        description="Items per page",
    ),
) -> PaginationParams:
    """FastAPI dependency for pagination parameters.

    Args:
        page: Page number (starts from 1)
        page_size: Number of items per page

    Returns:
        PaginationParams object
    """
    return PaginationParams(page=page, page_size=page_size)


async def paginate(
    db: AsyncSession,
    query: Select,
    params: PaginationParams,
) -> tuple[list, int]:
    """Execute paginated query and return results with total count.

    Args:
        db: Database session
        query: SQLAlchemy select query (without offset/limit)
        params: Pagination parameters

    Returns:
        Tuple of (items, total_count)
    """
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Get paginated items
    paginated_query = query.offset(params.offset).limit(params.limit)
    result = await db.execute(paginated_query)
    items = result.scalars().all()

    return list(items), total


def create_page_response[T](
    items: list[T],
    total: int,
    params: PaginationParams,
) -> PageResponse[T]:
    """Create a paginated response.

    Args:
        items: List of items for current page
        total: Total number of items
        params: Pagination parameters

    Returns:
        PageResponse object
    """
    total_pages = (total + params.page_size - 1) // params.page_size  # Ceiling division

    return PageResponse(
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size,
        total_pages=total_pages,
    )

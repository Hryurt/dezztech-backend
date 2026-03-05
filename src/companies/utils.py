# Company module utilities

from src.companies.config import DEFAULT_COMPANY_PAGE_SIZE, MAX_COMPANY_PAGE_SIZE


def normalize_pagination(page: int, limit: int) -> tuple[int, int]:
    """Normalize page and limit to valid ranges."""
    if page < 1:
        page = 1
    if limit < 1:
        limit = DEFAULT_COMPANY_PAGE_SIZE
    if limit > MAX_COMPANY_PAGE_SIZE:
        limit = MAX_COMPANY_PAGE_SIZE
    return page, limit


def normalize_iban(iban: str | None) -> str | None:
    """Normalize IBAN by removing spaces and converting to uppercase."""
    if not iban:
        return None
    return iban.replace(" ", "").upper()


def normalize_mersis(mersis: str) -> str:
    """Normalize MERSIS number by stripping whitespace."""
    return mersis.strip()


def normalize_search(search: str | None) -> str | None:
    """Normalize search string for query use."""
    if not search:
        return None
    return search.strip()

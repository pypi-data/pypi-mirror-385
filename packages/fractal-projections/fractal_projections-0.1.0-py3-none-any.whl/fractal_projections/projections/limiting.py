"""
Limiting Projections

Defines pagination and result limiting (LIMIT/OFFSET in SQL, limit/skip in MongoDB).
"""

from dataclasses import dataclass


@dataclass
class LimitProjection:
    """
    Defines result limiting and pagination

    Examples:
        LimitProjection(10)  # First 10 results
        LimitProjection(20, offset=40)  # Results 41-60 (page 3 of size 20)
    """

    limit: int
    offset: int = 0

    def __post_init__(self):
        """Validate limit and offset values"""
        if self.limit <= 0:
            raise ValueError("Limit must be greater than 0")
        if self.offset < 0:
            raise ValueError("Offset must be non-negative")

    @property
    def page_size(self) -> int:
        """Alias for limit (more intuitive for pagination)"""
        return self.limit

    @property
    def skip(self) -> int:
        """Alias for offset (matches MongoDB terminology)"""
        return self.offset

    def page_number(self, one_based: bool = True) -> int:
        """
        Calculate page number based on offset and limit

        Args:
            one_based: If True, return 1-based page numbers (default).
                      If False, return 0-based page numbers.
        """
        page = self.offset // self.limit
        return page + 1 if one_based else page

    def next_page(self) -> "LimitProjection":
        """Return a LimitProjection for the next page"""
        return LimitProjection(self.limit, self.offset + self.limit)

    def previous_page(self) -> "LimitProjection":
        """Return a LimitProjection for the previous page"""
        new_offset = max(0, self.offset - self.limit)
        return LimitProjection(self.limit, new_offset)

    def __str__(self) -> str:
        """String representation for debugging"""
        if self.offset > 0:
            return f"LIMIT {self.limit} OFFSET {self.offset}"
        return f"LIMIT {self.limit}"

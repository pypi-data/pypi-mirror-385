"""
Ordering Projections

Defines how to sort results (ORDER BY in SQL, sort stages in MongoDB aggregation).
"""

from dataclasses import dataclass
from typing import List


@dataclass
class OrderingProjection:
    """
    Defines how to sort results by a single field

    Examples:
        OrderingProjection("created_at")  # Ascending by default
        OrderingProjection("created_at", ascending=False)  # Descending
        OrderingProjection("name", ascending=True)
    """

    field: str
    ascending: bool = True

    @property
    def direction(self) -> str:
        """Return human-readable direction"""
        return "ASC" if self.ascending else "DESC"

    def __str__(self) -> str:
        """String representation for debugging"""
        direction = "↑" if self.ascending else "↓"
        return f"{self.field} {direction}"


class OrderingList:
    """
    A list of ordering projections for multi-field sorting

    Examples:
        OrderingList([
            OrderingProjection("department"),
            OrderingProjection("salary", ascending=False)
        ])
    """

    def __init__(self, orderings: List[OrderingProjection]):
        self.orderings = orderings or []

    def add(self, field: str, ascending: bool = True) -> "OrderingList":
        """Add an ordering projection"""
        self.orderings.append(OrderingProjection(field, ascending))
        return self

    def add_desc(self, field: str) -> "OrderingList":
        """Add a descending ordering projection"""
        return self.add(field, ascending=False)

    def __iter__(self):
        """Allow iteration over orderings"""
        return iter(self.orderings)

    def __len__(self) -> int:
        """Return the number of ordering fields"""
        return len(self.orderings)

    def __bool__(self) -> bool:
        """Return True if there are any orderings"""
        return len(self.orderings) > 0

    def __str__(self) -> str:
        """String representation for debugging"""
        return ", ".join(str(ordering) for ordering in self.orderings)

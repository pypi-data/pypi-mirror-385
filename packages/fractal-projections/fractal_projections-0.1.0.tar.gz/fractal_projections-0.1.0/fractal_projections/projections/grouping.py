"""
Grouping Projections

Defines how to group results (GROUP BY in SQL, grouping stages in MongoDB aggregation).
"""

from dataclasses import dataclass
from typing import List


@dataclass
class GroupingProjection:
    """
    Defines how to group results by one or more fields

    Examples:
        GroupingProjection(["category"])
        GroupingProjection(["department", "role"])
    """

    fields: List[str]

    def __post_init__(self):
        """Validate that we have at least one field to group by"""
        if not self.fields:
            raise ValueError("GroupingProjection must have at least one field")

    def __len__(self) -> int:
        """Return the number of grouping fields"""
        return len(self.fields)

    def __iter__(self):
        """Allow iteration over grouping fields"""
        return iter(self.fields)

    def __contains__(self, field: str) -> bool:
        """Check if a field is in the grouping"""
        return field in self.fields

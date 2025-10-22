"""
Query Projections

Combines all projection types into a complete query projection that can be
used with database-specific builders to generate optimized queries.
"""

from dataclasses import dataclass
from typing import List, Optional

from fractal_specifications.generic.specification import Specification

from .fields import (
    AggregateFunction,
    AggregateProjection,
    FieldProjection,
    ProjectionList,
)
from .grouping import GroupingProjection
from .limiting import LimitProjection
from .ordering import OrderingList


@dataclass
class QueryProjection:
    """
    Complete query projection combining filtering, field selection,
    grouping, ordering, and limiting

    Examples:
        # Simple field selection
        QueryProjection(
            filter=EqualsSpecification("active", True),
            projection=ProjectionList([FieldProjection("name")])
        )

        # Complex aggregation with grouping
        QueryProjection(
            filter=EqualsSpecification("status", "active"),
            projection=ProjectionList([
                FieldProjection("department"),
                AggregateProjection(AggregateFunction.COUNT, alias="count"),
                AggregateProjection(AggregateFunction.AVG, "salary", "avg_salary")
            ]),
            grouping=GroupingProjection(["department"]),
            ordering=OrderingList([OrderingProjection("count", ascending=False)]),
            limiting=LimitProjection(10)
        )
    """

    filter: Optional[Specification] = None
    projection: Optional[ProjectionList] = None
    grouping: Optional[GroupingProjection] = None
    ordering: Optional[OrderingList] = None
    limiting: Optional[LimitProjection] = None

    def has_aggregates(self) -> bool:
        """Check if query contains aggregate functions"""
        if not self.projection:
            return False
        return self.projection.has_aggregates()

    def requires_grouping(self) -> bool:
        """Check if query requires grouping (has aggregates + non-aggregate fields)"""
        if not self.projection or not self.has_aggregates():
            return False

        has_regular_fields = any(
            isinstance(f, FieldProjection) for f in self.projection.fields
        )
        return has_regular_fields

    def validate(self) -> List[str]:
        """Validate query projection and return any errors"""
        errors = []

        if self.requires_grouping() and not self.grouping:
            errors.append("Query with aggregates and regular fields requires grouping")

        if self.grouping and not self.has_aggregates():
            errors.append("Grouping requires at least one aggregate function")

        return errors


class QueryProjectionBuilder:
    """Builder pattern for constructing query projections"""

    def __init__(self):
        self._filter = None
        self._projection = None
        self._grouping = None
        self._ordering = OrderingList([])
        self._limiting = None

    def filter(self, specification: Specification) -> "QueryProjectionBuilder":
        """Add filter specification"""
        self._filter = specification
        return self

    def select(self, *fields) -> "QueryProjectionBuilder":
        """Add field projections"""
        from typing import List as TypingList
        from typing import Union

        projections: TypingList[Union[FieldProjection, AggregateProjection]] = []
        for field_def in fields:
            if isinstance(field_def, str):
                projections.append(FieldProjection(field_def))
            elif isinstance(field_def, (FieldProjection, AggregateProjection)):
                projections.append(field_def)
            else:
                raise ValueError(f"Invalid field definition: {field_def}")

        self._projection = ProjectionList(projections)
        return self

    def select_distinct(self, *fields) -> "QueryProjectionBuilder":
        """Add distinct field projections"""
        self.select(*fields)
        if self._projection:
            self._projection.distinct = True
        return self

    def count(
        self, field: Optional[str] = None, alias: Optional[str] = None
    ) -> "QueryProjectionBuilder":
        """Add COUNT aggregate"""
        agg = AggregateProjection(AggregateFunction.COUNT, field, alias)

        if not self._projection:
            self._projection = ProjectionList([])
        self._projection.fields.append(agg)
        return self

    def sum(self, field: str, alias: Optional[str] = None) -> "QueryProjectionBuilder":
        """Add SUM aggregate"""
        agg = AggregateProjection(AggregateFunction.SUM, field, alias)

        if not self._projection:
            self._projection = ProjectionList([])
        self._projection.fields.append(agg)
        return self

    def avg(self, field: str, alias: Optional[str] = None) -> "QueryProjectionBuilder":
        """Add AVG aggregate"""
        agg = AggregateProjection(AggregateFunction.AVG, field, alias)

        if not self._projection:
            self._projection = ProjectionList([])
        self._projection.fields.append(agg)
        return self

    def min(self, field: str, alias: Optional[str] = None) -> "QueryProjectionBuilder":
        """Add MIN aggregate"""
        agg = AggregateProjection(AggregateFunction.MIN, field, alias)

        if not self._projection:
            self._projection = ProjectionList([])
        self._projection.fields.append(agg)
        return self

    def max(self, field: str, alias: Optional[str] = None) -> "QueryProjectionBuilder":
        """Add MAX aggregate"""
        agg = AggregateProjection(AggregateFunction.MAX, field, alias)

        if not self._projection:
            self._projection = ProjectionList([])
        self._projection.fields.append(agg)
        return self

    def count_distinct(
        self, field: str, alias: Optional[str] = None
    ) -> "QueryProjectionBuilder":
        """Add COUNT DISTINCT aggregate"""
        agg = AggregateProjection(AggregateFunction.COUNT_DISTINCT, field, alias)

        if not self._projection:
            self._projection = ProjectionList([])
        self._projection.fields.append(agg)
        return self

    def group_by(self, *fields: str) -> "QueryProjectionBuilder":
        """Add grouping"""
        self._grouping = GroupingProjection(list(fields))
        return self

    def order_by(self, field: str, ascending: bool = True) -> "QueryProjectionBuilder":
        """Add ordering"""
        self._ordering.add(field, ascending)
        return self

    def order_by_desc(self, field: str) -> "QueryProjectionBuilder":
        """Add descending ordering"""
        return self.order_by(field, ascending=False)

    def limit(self, limit: int, offset: int = 0) -> "QueryProjectionBuilder":
        """Add limiting"""
        self._limiting = LimitProjection(limit, offset)
        return self

    def build(self) -> QueryProjection:
        """Build the final query projection"""
        query_projection = QueryProjection(
            filter=self._filter,
            projection=self._projection,
            grouping=self._grouping,
            ordering=self._ordering if self._ordering else None,
            limiting=self._limiting,
        )

        # Validate the query
        errors = query_projection.validate()
        if errors:
            raise ValueError(f"Invalid query projection: {'; '.join(errors)}")

        return query_projection


# Convenience functions for common query patterns
def select(*fields) -> QueryProjectionBuilder:
    """Start building a SELECT query"""
    return QueryProjectionBuilder().select(*fields)


def select_distinct(*fields) -> QueryProjectionBuilder:
    """Start building a SELECT DISTINCT query"""
    return QueryProjectionBuilder().select_distinct(*fields)


def count(field: Optional[str] = None) -> QueryProjectionBuilder:
    """Start building a COUNT query"""
    return QueryProjectionBuilder().count(field)

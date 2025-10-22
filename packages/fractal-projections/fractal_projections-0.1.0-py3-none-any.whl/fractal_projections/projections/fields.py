"""
Field Projections

Defines what fields to select and how to aggregate them.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterator, List, Optional, Union


class AggregateFunction(Enum):
    """Supported aggregate functions across different database backends"""

    COUNT = "COUNT"
    SUM = "SUM"
    AVG = "AVG"
    MIN = "MIN"
    MAX = "MAX"
    COUNT_DISTINCT = "COUNT DISTINCT"


@dataclass
class FieldProjection:
    """
    Represents a simple field projection like 'name', 'email', etc.

    Examples:
        FieldProjection("name")
        FieldProjection("email", alias="user_email")
    """

    field: str
    alias: Optional[str] = None


@dataclass
class AggregateProjection:
    """
    Represents an aggregate function projection like COUNT(*), SUM(field), etc.

    Examples:
        AggregateProjection(AggregateFunction.COUNT)  # COUNT(*)
        AggregateProjection(AggregateFunction.SUM, "amount", "total_amount")
        AggregateProjection(AggregateFunction.COUNT_DISTINCT, "user_id", "unique_users")
    """

    function: AggregateFunction
    field: Optional[str] = None  # None for COUNT(*)
    alias: Optional[str] = None

    def apply_to_results(self, results: List[Any]) -> Any:
        """
        Apply aggregate function to in-memory results

        This is used as a fallback when the database doesn't support
        server-side aggregation for this function.
        """
        if not results:
            return (
                0
                if self.function
                in [AggregateFunction.COUNT, AggregateFunction.COUNT_DISTINCT]
                else None
            )

        if self.function == AggregateFunction.COUNT:
            return len(results)
        elif self.function == AggregateFunction.COUNT_DISTINCT:
            if self.field:
                return len(set(getattr(item, self.field) for item in results))
            return len(set(results))
        elif self.function == AggregateFunction.SUM:
            return sum(getattr(item, self.field) for item in results)
        elif self.function == AggregateFunction.AVG:
            values = [getattr(item, self.field) for item in results]
            return sum(values) / len(values) if values else None
        elif self.function == AggregateFunction.MIN:
            return min(getattr(item, self.field) for item in results)
        elif self.function == AggregateFunction.MAX:
            return max(getattr(item, self.field) for item in results)


@dataclass
class ProjectionList:
    """
    A list of field and aggregate projections with optional DISTINCT

    Examples:
        ProjectionList([FieldProjection("name"), FieldProjection("email")])
        ProjectionList([FieldProjection("category")], distinct=True)
        ProjectionList([
            FieldProjection("category"),
            AggregateProjection(AggregateFunction.COUNT, alias="count")
        ])
    """

    fields: List[Union[FieldProjection, AggregateProjection]]
    distinct: bool = False

    def apply_to_results(self, results: List[Any]) -> Iterator[Any]:
        """
        Apply projection to in-memory results

        This is used as a fallback when the database doesn't support
        server-side projection.
        """
        if not self.fields:
            yield from results
            return

        # Handle aggregates
        aggregate_fields = [
            f for f in self.fields if isinstance(f, AggregateProjection)
        ]
        if aggregate_fields:
            # If we have aggregates, return a single result with aggregate values
            result = {}
            for agg in aggregate_fields:
                key = agg.alias or f"{agg.function.value}_{agg.field or 'all'}"
                result[key] = agg.apply_to_results(results)
            yield result
            return

        # Handle regular field projections
        seen = set() if self.distinct else None

        for item in results:
            if len(self.fields) == 1:
                # Single field - return scalar value
                field_proj = self.fields[0]
                value = getattr(item, field_proj.field)

                if self.distinct:
                    if value in seen:
                        continue
                    seen.add(value)

                yield value
            else:
                # Multiple fields - return dict
                result = {}
                for field_proj in self.fields:
                    if isinstance(field_proj, FieldProjection):
                        key = field_proj.alias or field_proj.field
                        result[key] = getattr(item, field_proj.field)

                if self.distinct:
                    result_tuple = tuple(result.values())
                    if result_tuple in seen:
                        continue
                    seen.add(result_tuple)

                yield result

    def has_aggregates(self) -> bool:
        """Check if this projection contains any aggregate functions"""
        return any(isinstance(f, AggregateProjection) for f in self.fields)

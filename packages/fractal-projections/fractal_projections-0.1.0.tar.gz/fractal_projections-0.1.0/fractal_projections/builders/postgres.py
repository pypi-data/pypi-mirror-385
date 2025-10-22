"""
PostgreSQL Projection Builder

Converts generic projections to PostgreSQL-specific SQL syntax.
"""

from ..projections.fields import (
    AggregateFunction,
    AggregateProjection,
    FieldProjection,
    ProjectionList,
)
from ..projections.grouping import GroupingProjection
from ..projections.limiting import LimitProjection
from ..projections.ordering import OrderingList


class PostgresProjectionBuilder:
    """Builds PostgreSQL-specific SQL from projection objects"""

    @staticmethod
    def build_select(projection: ProjectionList) -> str:
        """Convert ProjectionList to PostgreSQL SELECT clause"""
        if not projection.fields:
            return "*"

        field_exprs = []
        for field_spec in projection.fields:
            if isinstance(field_spec, FieldProjection):
                expr = PostgresProjectionBuilder._build_field_projection(field_spec)
            elif isinstance(field_spec, AggregateProjection):
                expr = PostgresProjectionBuilder._build_aggregate_projection(field_spec)
            else:
                raise ValueError(f"Unknown projection type: {type(field_spec)}")

            field_exprs.append(expr)

        select_clause = ", ".join(field_exprs)

        if projection.distinct:
            select_clause = f"DISTINCT {select_clause}"

        return select_clause

    @staticmethod
    def _build_field_projection(field: FieldProjection) -> str:
        """Convert FieldProjection to PostgreSQL field expression"""
        expr = field.field
        if field.alias:
            expr += f" AS {field.alias}"
        return expr

    @staticmethod
    def _build_aggregate_projection(agg: AggregateProjection) -> str:
        """Convert AggregateProjection to PostgreSQL aggregate expression"""
        if agg.function == AggregateFunction.COUNT and agg.field is None:
            expr = "COUNT(*)"
        elif agg.function == AggregateFunction.COUNT_DISTINCT:
            expr = f"COUNT(DISTINCT {agg.field})"
        else:
            expr = f"{agg.function.value}({agg.field})"

        if agg.alias:
            expr += f" AS {agg.alias}"
        return expr

    @staticmethod
    def build_group_by(grouping: GroupingProjection) -> str:
        """Convert GroupingProjection to PostgreSQL GROUP BY clause"""
        return ", ".join(grouping.fields)

    @staticmethod
    def build_order_by(ordering: OrderingList) -> str:
        """Convert OrderingList to PostgreSQL ORDER BY clause"""
        if not ordering:
            return ""

        order_exprs = []
        for order_proj in ordering:
            direction = "ASC" if order_proj.ascending else "DESC"
            expr = f"{order_proj.field} {direction}"
            order_exprs.append(expr)

        return ", ".join(order_exprs)

    @staticmethod
    def build_limit(limit: LimitProjection) -> str:
        """Convert LimitProjection to PostgreSQL LIMIT/OFFSET clause"""
        sql = f"LIMIT {limit.limit}"
        if limit.offset > 0:
            sql += f" OFFSET {limit.offset}"
        return sql

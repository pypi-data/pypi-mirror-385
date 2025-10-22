"""
Tests for PostgreSQL projection builder
"""

import pytest

from fractal_projections.builders.postgres import PostgresProjectionBuilder
from fractal_projections.projections.fields import (
    AggregateFunction,
    AggregateProjection,
    FieldProjection,
    ProjectionList,
)
from fractal_projections.projections.grouping import GroupingProjection
from fractal_projections.projections.limiting import LimitProjection
from fractal_projections.projections.ordering import OrderingList, OrderingProjection


class TestPostgresProjectionBuilder:
    """Tests for PostgreSQL projection builder"""

    def test_build_select_empty_fields(self):
        """Test building SELECT with no fields returns *"""
        projection = ProjectionList([])
        result = PostgresProjectionBuilder.build_select(projection)
        assert result == "*"

    def test_build_select_single_field(self):
        """Test building SELECT with single field"""
        projection = ProjectionList([FieldProjection("name")])
        result = PostgresProjectionBuilder.build_select(projection)
        assert result == "name"

    def test_build_select_multiple_fields(self):
        """Test building SELECT with multiple fields"""
        projection = ProjectionList(
            [FieldProjection("name"), FieldProjection("email"), FieldProjection("age")]
        )
        result = PostgresProjectionBuilder.build_select(projection)
        assert result == "name, email, age"

    def test_build_select_field_with_alias(self):
        """Test building SELECT with field alias"""
        projection = ProjectionList([FieldProjection("name", alias="full_name")])
        result = PostgresProjectionBuilder.build_select(projection)
        assert result == "name AS full_name"

    def test_build_select_distinct(self):
        """Test building SELECT DISTINCT"""
        projection = ProjectionList([FieldProjection("category")], distinct=True)
        result = PostgresProjectionBuilder.build_select(projection)
        assert result == "DISTINCT category"

    def test_build_select_distinct_multiple_fields(self):
        """Test building SELECT DISTINCT with multiple fields"""
        projection = ProjectionList(
            [FieldProjection("category"), FieldProjection("status")], distinct=True
        )
        result = PostgresProjectionBuilder.build_select(projection)
        assert result == "DISTINCT category, status"

    def test_build_aggregate_count_all(self):
        """Test building COUNT(*) aggregate"""
        projection = ProjectionList([AggregateProjection(AggregateFunction.COUNT)])
        result = PostgresProjectionBuilder.build_select(projection)
        assert result == "COUNT(*)"

    def test_build_aggregate_count_with_field(self):
        """Test building COUNT with field"""
        projection = ProjectionList(
            [AggregateProjection(AggregateFunction.COUNT, "user_id")]
        )
        result = PostgresProjectionBuilder.build_select(projection)
        assert result == "COUNT(user_id)"

    def test_build_aggregate_count_with_alias(self):
        """Test building COUNT with alias"""
        projection = ProjectionList(
            [AggregateProjection(AggregateFunction.COUNT, alias="total")]
        )
        result = PostgresProjectionBuilder.build_select(projection)
        assert result == "COUNT(*) AS total"

    def test_build_aggregate_sum(self):
        """Test building SUM aggregate"""
        projection = ProjectionList(
            [AggregateProjection(AggregateFunction.SUM, "amount", "total_amount")]
        )
        result = PostgresProjectionBuilder.build_select(projection)
        assert result == "SUM(amount) AS total_amount"

    def test_build_aggregate_avg(self):
        """Test building AVG aggregate"""
        projection = ProjectionList(
            [AggregateProjection(AggregateFunction.AVG, "salary", "avg_salary")]
        )
        result = PostgresProjectionBuilder.build_select(projection)
        assert result == "AVG(salary) AS avg_salary"

    def test_build_aggregate_min(self):
        """Test building MIN aggregate"""
        projection = ProjectionList(
            [AggregateProjection(AggregateFunction.MIN, "price")]
        )
        result = PostgresProjectionBuilder.build_select(projection)
        assert result == "MIN(price)"

    def test_build_aggregate_max(self):
        """Test building MAX aggregate"""
        projection = ProjectionList(
            [AggregateProjection(AggregateFunction.MAX, "price")]
        )
        result = PostgresProjectionBuilder.build_select(projection)
        assert result == "MAX(price)"

    def test_build_aggregate_count_distinct(self):
        """Test building COUNT DISTINCT aggregate"""
        projection = ProjectionList(
            [
                AggregateProjection(
                    AggregateFunction.COUNT_DISTINCT, "user_id", "unique_users"
                )
            ]
        )
        result = PostgresProjectionBuilder.build_select(projection)
        assert result == "COUNT(DISTINCT user_id) AS unique_users"

    def test_build_select_mixed_fields_and_aggregates(self):
        """Test building SELECT with mixed field and aggregate projections"""
        projection = ProjectionList(
            [
                FieldProjection("department"),
                AggregateProjection(AggregateFunction.COUNT, alias="employee_count"),
                AggregateProjection(AggregateFunction.AVG, "salary", "avg_salary"),
            ]
        )
        result = PostgresProjectionBuilder.build_select(projection)
        expected = "department, COUNT(*) AS employee_count, AVG(salary) AS avg_salary"
        assert result == expected

    def test_build_group_by_single_field(self):
        """Test building GROUP BY with single field"""
        grouping = GroupingProjection(["department"])
        result = PostgresProjectionBuilder.build_group_by(grouping)
        assert result == "department"

    def test_build_group_by_multiple_fields(self):
        """Test building GROUP BY with multiple fields"""
        grouping = GroupingProjection(["department", "role", "location"])
        result = PostgresProjectionBuilder.build_group_by(grouping)
        assert result == "department, role, location"

    def test_build_order_by_empty(self):
        """Test building ORDER BY with empty list"""
        ordering = OrderingList([])
        result = PostgresProjectionBuilder.build_order_by(ordering)
        assert result == ""

    def test_build_order_by_single_ascending(self):
        """Test building ORDER BY with single ascending field"""
        ordering = OrderingList([OrderingProjection("name", ascending=True)])
        result = PostgresProjectionBuilder.build_order_by(ordering)
        assert result == "name ASC"

    def test_build_order_by_single_descending(self):
        """Test building ORDER BY with single descending field"""
        ordering = OrderingList([OrderingProjection("created_at", ascending=False)])
        result = PostgresProjectionBuilder.build_order_by(ordering)
        assert result == "created_at DESC"

    def test_build_order_by_multiple_fields(self):
        """Test building ORDER BY with multiple fields"""
        ordering = OrderingList(
            [
                OrderingProjection("department", ascending=True),
                OrderingProjection("salary", ascending=False),
                OrderingProjection("name", ascending=True),
            ]
        )
        result = PostgresProjectionBuilder.build_order_by(ordering)
        assert result == "department ASC, salary DESC, name ASC"

    def test_build_limit_only(self):
        """Test building LIMIT without offset"""
        limit = LimitProjection(10)
        result = PostgresProjectionBuilder.build_limit(limit)
        assert result == "LIMIT 10"

    def test_build_limit_with_offset(self):
        """Test building LIMIT with offset"""
        limit = LimitProjection(20, offset=40)
        result = PostgresProjectionBuilder.build_limit(limit)
        assert result == "LIMIT 20 OFFSET 40"

    def test_build_limit_large_values(self):
        """Test building LIMIT with large values"""
        limit = LimitProjection(1000, offset=5000)
        result = PostgresProjectionBuilder.build_limit(limit)
        assert result == "LIMIT 1000 OFFSET 5000"

    def test_build_field_projection_without_alias(self):
        """Test _build_field_projection without alias"""
        field = FieldProjection("email")
        result = PostgresProjectionBuilder._build_field_projection(field)
        assert result == "email"

    def test_build_field_projection_with_alias(self):
        """Test _build_field_projection with alias"""
        field = FieldProjection("email", alias="user_email")
        result = PostgresProjectionBuilder._build_field_projection(field)
        assert result == "email AS user_email"

    def test_build_aggregate_projection_count_all(self):
        """Test _build_aggregate_projection for COUNT(*)"""
        agg = AggregateProjection(AggregateFunction.COUNT)
        result = PostgresProjectionBuilder._build_aggregate_projection(agg)
        assert result == "COUNT(*)"

    def test_build_aggregate_projection_count_distinct(self):
        """Test _build_aggregate_projection for COUNT DISTINCT"""
        agg = AggregateProjection(AggregateFunction.COUNT_DISTINCT, "user_id")
        result = PostgresProjectionBuilder._build_aggregate_projection(agg)
        assert result == "COUNT(DISTINCT user_id)"

    def test_build_aggregate_projection_sum(self):
        """Test _build_aggregate_projection for SUM"""
        agg = AggregateProjection(AggregateFunction.SUM, "amount")
        result = PostgresProjectionBuilder._build_aggregate_projection(agg)
        assert result == "SUM(amount)"

    def test_build_aggregate_projection_with_alias(self):
        """Test _build_aggregate_projection with alias"""
        agg = AggregateProjection(AggregateFunction.AVG, "salary", "avg_salary")
        result = PostgresProjectionBuilder._build_aggregate_projection(agg)
        assert result == "AVG(salary) AS avg_salary"

    def test_build_select_invalid_projection_type_raises_error(self):
        """Test that invalid projection type raises ValueError"""

        class InvalidProjection:
            pass

        projection = ProjectionList([InvalidProjection()])

        with pytest.raises(ValueError, match="Unknown projection type"):
            PostgresProjectionBuilder.build_select(projection)

    def test_integration_complex_query_parts(self):
        """Test building all parts of a complex query"""
        # SELECT department, COUNT(*) as employee_count, AVG(salary) as avg_salary
        select_projection = ProjectionList(
            [
                FieldProjection("department"),
                AggregateProjection(AggregateFunction.COUNT, alias="employee_count"),
                AggregateProjection(AggregateFunction.AVG, "salary", "avg_salary"),
            ]
        )

        # GROUP BY department
        grouping = GroupingProjection(["department"])

        # ORDER BY employee_count DESC, avg_salary DESC
        ordering = OrderingList(
            [
                OrderingProjection("employee_count", ascending=False),
                OrderingProjection("avg_salary", ascending=False),
            ]
        )

        # LIMIT 10
        limiting = LimitProjection(10)

        select_clause = PostgresProjectionBuilder.build_select(select_projection)
        group_by_clause = PostgresProjectionBuilder.build_group_by(grouping)
        order_by_clause = PostgresProjectionBuilder.build_order_by(ordering)
        limit_clause = PostgresProjectionBuilder.build_limit(limiting)

        # Verify each part
        assert "department" in select_clause
        assert "COUNT(*) AS employee_count" in select_clause
        assert "AVG(salary) AS avg_salary" in select_clause

        assert group_by_clause == "department"

        assert "employee_count DESC" in order_by_clause
        assert "avg_salary DESC" in order_by_clause

        assert limit_clause == "LIMIT 10"

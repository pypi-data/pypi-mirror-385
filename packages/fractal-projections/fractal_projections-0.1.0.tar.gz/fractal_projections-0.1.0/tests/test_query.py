"""
Tests for query projection classes
"""

import pytest

from fractal_projections.projections.fields import (
    AggregateFunction,
    AggregateProjection,
    FieldProjection,
    ProjectionList,
)
from fractal_projections.projections.grouping import GroupingProjection
from fractal_projections.projections.limiting import LimitProjection
from fractal_projections.projections.ordering import OrderingList, OrderingProjection
from fractal_projections.projections.query import (
    QueryProjection,
    QueryProjectionBuilder,
    count,
    select,
    select_distinct,
)


# Mock specification for testing
class MockSpecification:
    """Mock specification for testing"""

    def __init__(self, field, value):
        self.field = field
        self.value = value


class TestQueryProjection:
    """Tests for QueryProjection class"""

    def test_empty_query_projection(self):
        """Test creating an empty query projection"""
        query = QueryProjection()
        assert query.filter is None
        assert query.projection is None
        assert query.grouping is None
        assert query.ordering is None
        assert query.limiting is None

    def test_simple_query_with_filter(self):
        """Test query with just a filter"""
        spec = MockSpecification("active", True)
        query = QueryProjection(filter=spec)
        assert query.filter == spec

    def test_query_with_projection(self):
        """Test query with field projection"""
        proj = ProjectionList([FieldProjection("name")])
        query = QueryProjection(projection=proj)
        assert query.projection == proj

    def test_has_aggregates_without_projection(self):
        """Test has_aggregates returns False when no projection"""
        query = QueryProjection()
        assert query.has_aggregates() is False

    def test_has_aggregates_with_regular_fields(self):
        """Test has_aggregates with only regular fields"""
        proj = ProjectionList([FieldProjection("name")])
        query = QueryProjection(projection=proj)
        assert query.has_aggregates() is False

    def test_has_aggregates_with_aggregates(self):
        """Test has_aggregates with aggregate functions"""
        proj = ProjectionList(
            [AggregateProjection(AggregateFunction.COUNT, alias="total")]
        )
        query = QueryProjection(projection=proj)
        assert query.has_aggregates() is True

    def test_requires_grouping_without_projection(self):
        """Test requires_grouping without projection"""
        query = QueryProjection()
        assert query.requires_grouping() is False

    def test_requires_grouping_only_aggregates(self):
        """Test requires_grouping with only aggregates"""
        proj = ProjectionList(
            [AggregateProjection(AggregateFunction.COUNT, alias="total")]
        )
        query = QueryProjection(projection=proj)
        assert query.requires_grouping() is False

    def test_requires_grouping_mixed_fields(self):
        """Test requires_grouping with mixed fields and aggregates"""
        proj = ProjectionList(
            [
                FieldProjection("department"),
                AggregateProjection(AggregateFunction.COUNT, alias="total"),
            ]
        )
        query = QueryProjection(projection=proj)
        assert query.requires_grouping() is True

    def test_validate_no_errors_simple_query(self):
        """Test validate returns no errors for simple query"""
        query = QueryProjection(projection=ProjectionList([FieldProjection("name")]))
        errors = query.validate()
        assert errors == []

    def test_validate_error_missing_grouping(self):
        """Test validate error when grouping is required but missing"""
        proj = ProjectionList(
            [
                FieldProjection("department"),
                AggregateProjection(AggregateFunction.COUNT, alias="total"),
            ]
        )
        query = QueryProjection(projection=proj)
        errors = query.validate()

        assert len(errors) == 1
        assert "requires grouping" in errors[0]

    def test_validate_error_grouping_without_aggregates(self):
        """Test validate error when grouping without aggregates"""
        query = QueryProjection(
            projection=ProjectionList([FieldProjection("department")]),
            grouping=GroupingProjection(["department"]),
        )
        errors = query.validate()

        assert len(errors) == 1
        assert "requires at least one aggregate" in errors[0]

    def test_validate_no_errors_with_proper_grouping(self):
        """Test validate with proper grouping and aggregates"""
        query = QueryProjection(
            projection=ProjectionList(
                [
                    FieldProjection("department"),
                    AggregateProjection(AggregateFunction.COUNT, alias="total"),
                ]
            ),
            grouping=GroupingProjection(["department"]),
        )
        errors = query.validate()
        assert errors == []

    def test_complete_query(self):
        """Test creating a complete query with all components"""
        spec = MockSpecification("active", True)
        proj = ProjectionList(
            [
                FieldProjection("department"),
                AggregateProjection(AggregateFunction.COUNT, alias="total"),
            ]
        )
        grouping = GroupingProjection(["department"])
        ordering = OrderingList([OrderingProjection("total", ascending=False)])
        limiting = LimitProjection(10)

        query = QueryProjection(
            filter=spec,
            projection=proj,
            grouping=grouping,
            ordering=ordering,
            limiting=limiting,
        )

        assert query.filter == spec
        assert query.projection == proj
        assert query.grouping == grouping
        assert query.ordering == ordering
        assert query.limiting == limiting


class TestQueryProjectionBuilder:
    """Tests for QueryProjectionBuilder class"""

    def test_empty_builder(self):
        """Test creating empty builder"""
        builder = QueryProjectionBuilder()
        assert builder._filter is None
        assert builder._projection is None

    def test_select_single_field_string(self):
        """Test select with single string field"""
        builder = QueryProjectionBuilder()
        result = builder.select("name")

        assert result is builder  # Test chaining
        assert builder._projection is not None
        assert len(builder._projection.fields) == 1
        assert builder._projection.fields[0].field == "name"

    def test_select_multiple_fields(self):
        """Test select with multiple fields"""
        builder = QueryProjectionBuilder()
        builder.select("name", "email", "age")

        assert len(builder._projection.fields) == 3
        assert builder._projection.fields[0].field == "name"
        assert builder._projection.fields[1].field == "email"
        assert builder._projection.fields[2].field == "age"

    def test_select_with_field_projection(self):
        """Test select with FieldProjection objects"""
        builder = QueryProjectionBuilder()
        builder.select(FieldProjection("name", alias="full_name"))

        assert len(builder._projection.fields) == 1
        assert builder._projection.fields[0].alias == "full_name"

    def test_select_distinct(self):
        """Test select_distinct sets distinct flag"""
        builder = QueryProjectionBuilder()
        builder.select_distinct("category")

        assert builder._projection.distinct is True
        assert len(builder._projection.fields) == 1

    def test_count_aggregate(self):
        """Test adding COUNT aggregate"""
        builder = QueryProjectionBuilder()
        builder.count(alias="total")

        assert len(builder._projection.fields) == 1
        agg = builder._projection.fields[0]
        assert isinstance(agg, AggregateProjection)
        assert agg.function == AggregateFunction.COUNT
        assert agg.alias == "total"

    def test_sum_aggregate(self):
        """Test adding SUM aggregate"""
        builder = QueryProjectionBuilder()
        builder.sum("amount", alias="total_amount")

        agg = builder._projection.fields[0]
        assert agg.function == AggregateFunction.SUM
        assert agg.field == "amount"
        assert agg.alias == "total_amount"

    def test_avg_aggregate(self):
        """Test adding AVG aggregate"""
        builder = QueryProjectionBuilder()
        builder.avg("salary", alias="avg_salary")

        agg = builder._projection.fields[0]
        assert agg.function == AggregateFunction.AVG
        assert agg.field == "salary"

    def test_min_aggregate(self):
        """Test adding MIN aggregate"""
        builder = QueryProjectionBuilder()
        builder.min("price", alias="min_price")

        agg = builder._projection.fields[0]
        assert agg.function == AggregateFunction.MIN

    def test_max_aggregate(self):
        """Test adding MAX aggregate"""
        builder = QueryProjectionBuilder()
        builder.max("price", alias="max_price")

        agg = builder._projection.fields[0]
        assert agg.function == AggregateFunction.MAX

    def test_count_distinct_aggregate(self):
        """Test adding COUNT DISTINCT aggregate"""
        builder = QueryProjectionBuilder()
        builder.count_distinct("user_id", alias="unique_users")

        agg = builder._projection.fields[0]
        assert agg.function == AggregateFunction.COUNT_DISTINCT
        assert agg.field == "user_id"

    def test_group_by_single_field(self):
        """Test group_by with single field"""
        builder = QueryProjectionBuilder()
        builder.group_by("department")

        assert builder._grouping is not None
        assert len(builder._grouping.fields) == 1
        assert builder._grouping.fields[0] == "department"

    def test_group_by_multiple_fields(self):
        """Test group_by with multiple fields"""
        builder = QueryProjectionBuilder()
        builder.group_by("department", "role")

        assert len(builder._grouping.fields) == 2

    def test_order_by_ascending(self):
        """Test order_by ascending"""
        builder = QueryProjectionBuilder()
        builder.order_by("name")

        assert len(builder._ordering) == 1
        assert builder._ordering.orderings[0].field == "name"
        assert builder._ordering.orderings[0].ascending is True

    def test_order_by_descending(self):
        """Test order_by with descending"""
        builder = QueryProjectionBuilder()
        builder.order_by("created_at", ascending=False)

        assert builder._ordering.orderings[0].ascending is False

    def test_order_by_desc_shorthand(self):
        """Test order_by_desc shorthand"""
        builder = QueryProjectionBuilder()
        builder.order_by_desc("created_at")

        assert builder._ordering.orderings[0].ascending is False

    def test_limit(self):
        """Test adding limit"""
        builder = QueryProjectionBuilder()
        builder.limit(10)

        assert builder._limiting is not None
        assert builder._limiting.limit == 10
        assert builder._limiting.offset == 0

    def test_limit_with_offset(self):
        """Test adding limit with offset"""
        builder = QueryProjectionBuilder()
        builder.limit(20, offset=40)

        assert builder._limiting.limit == 20
        assert builder._limiting.offset == 40

    def test_filter(self):
        """Test adding filter"""
        spec = MockSpecification("active", True)
        builder = QueryProjectionBuilder()
        builder.filter(spec)

        assert builder._filter == spec

    def test_chaining(self):
        """Test method chaining"""
        spec = MockSpecification("active", True)
        builder = QueryProjectionBuilder()

        result = (
            builder.filter(spec)
            .select("department")
            .count(alias="total")
            .group_by("department")
            .order_by_desc("total")
            .limit(10)
        )

        assert result is builder  # All methods return self

    def test_build_simple_query(self):
        """Test building simple query"""
        builder = QueryProjectionBuilder()
        query = builder.select("name", "email").build()

        assert isinstance(query, QueryProjection)
        assert query.projection is not None
        assert len(query.projection.fields) == 2

    def test_build_complex_query(self):
        """Test building complex query with all components"""
        spec = MockSpecification("active", True)
        builder = QueryProjectionBuilder()

        query = (
            builder.filter(spec)
            .select("department")
            .count(alias="total")
            .group_by("department")
            .order_by_desc("total")
            .limit(10)
            .build()
        )

        assert query.filter == spec
        assert query.projection is not None
        assert query.grouping is not None
        assert query.ordering is not None
        assert query.limiting is not None

    def test_build_invalid_query_raises_error(self):
        """Test that building invalid query raises ValueError"""
        builder = QueryProjectionBuilder()

        # This is invalid: aggregates + regular fields without grouping
        builder.select("department").count(alias="total")

        with pytest.raises(ValueError, match="Invalid query projection"):
            builder.build()

    def test_select_invalid_field_type_raises_error(self):
        """Test that invalid field type raises ValueError"""
        builder = QueryProjectionBuilder()

        with pytest.raises(ValueError, match="Invalid field definition"):
            builder.select(123)  # Invalid type


class TestConvenienceFunctions:
    """Tests for convenience functions"""

    def test_select_function(self):
        """Test select convenience function"""
        builder = select("name", "email")

        assert isinstance(builder, QueryProjectionBuilder)
        assert builder._projection is not None
        assert len(builder._projection.fields) == 2

    def test_select_distinct_function(self):
        """Test select_distinct convenience function"""
        builder = select_distinct("category")

        assert isinstance(builder, QueryProjectionBuilder)
        assert builder._projection.distinct is True

    def test_count_function(self):
        """Test count convenience function"""
        builder = count()

        assert isinstance(builder, QueryProjectionBuilder)
        assert len(builder._projection.fields) == 1
        agg = builder._projection.fields[0]
        assert agg.function == AggregateFunction.COUNT

    def test_count_function_with_field(self):
        """Test count convenience function with field"""
        builder = count("user_id")

        agg = builder._projection.fields[0]
        assert agg.field == "user_id"

    def test_select_chaining_with_convenience_function(self):
        """Test that convenience functions support chaining"""
        spec = MockSpecification("active", True)
        query = select("name", "email").filter(spec).order_by("name").limit(10).build()

        assert isinstance(query, QueryProjection)
        assert query.filter == spec

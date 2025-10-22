"""
Tests for field projection classes
"""

from fractal_projections.projections.fields import (
    AggregateFunction,
    AggregateProjection,
    FieldProjection,
    ProjectionList,
)


class TestFieldProjection:
    """Tests for FieldProjection class"""

    def test_simple_field(self):
        """Test basic field projection without alias"""
        field = FieldProjection("name")
        assert field.field == "name"
        assert field.alias is None

    def test_field_with_alias(self):
        """Test field projection with alias"""
        field = FieldProjection("email", alias="user_email")
        assert field.field == "email"
        assert field.alias == "user_email"


class TestAggregateFunction:
    """Tests for AggregateFunction enum"""

    def test_all_functions_exist(self):
        """Test that all expected aggregate functions are defined"""
        expected_functions = ["COUNT", "SUM", "AVG", "MIN", "MAX", "COUNT_DISTINCT"]
        for func_name in expected_functions:
            assert hasattr(AggregateFunction, func_name)

    def test_function_values(self):
        """Test that function values are strings"""
        assert AggregateFunction.COUNT.value == "COUNT"
        assert AggregateFunction.SUM.value == "SUM"
        assert AggregateFunction.COUNT_DISTINCT.value == "COUNT DISTINCT"


class TestAggregateProjection:
    """Tests for AggregateProjection class"""

    def test_count_all(self):
        """Test COUNT(*) aggregate"""
        agg = AggregateProjection(AggregateFunction.COUNT)
        assert agg.function == AggregateFunction.COUNT
        assert agg.field is None
        assert agg.alias is None

    def test_count_with_field(self):
        """Test COUNT with specific field"""
        agg = AggregateProjection(AggregateFunction.COUNT, "user_id", "total_users")
        assert agg.function == AggregateFunction.COUNT
        assert agg.field == "user_id"
        assert agg.alias == "total_users"

    def test_sum_aggregate(self):
        """Test SUM aggregate"""
        agg = AggregateProjection(AggregateFunction.SUM, "amount", "total_amount")
        assert agg.function == AggregateFunction.SUM
        assert agg.field == "amount"
        assert agg.alias == "total_amount"

    def test_apply_count_empty_results(self):
        """Test COUNT on empty results returns 0"""
        agg = AggregateProjection(AggregateFunction.COUNT)
        assert agg.apply_to_results([]) == 0

    def test_apply_count_results(self):
        """Test COUNT on results"""
        agg = AggregateProjection(AggregateFunction.COUNT)

        class Item:
            pass

        results = [Item(), Item(), Item()]
        assert agg.apply_to_results(results) == 3

    def test_apply_sum(self):
        """Test SUM aggregate on results"""
        agg = AggregateProjection(AggregateFunction.SUM, "amount")

        class Item:
            def __init__(self, amount):
                self.amount = amount

        results = [Item(10), Item(20), Item(30)]
        assert agg.apply_to_results(results) == 60

    def test_apply_avg(self):
        """Test AVG aggregate on results"""
        agg = AggregateProjection(AggregateFunction.AVG, "amount")

        class Item:
            def __init__(self, amount):
                self.amount = amount

        results = [Item(10), Item(20), Item(30)]
        assert agg.apply_to_results(results) == 20.0

    def test_apply_min(self):
        """Test MIN aggregate on results"""
        agg = AggregateProjection(AggregateFunction.MIN, "amount")

        class Item:
            def __init__(self, amount):
                self.amount = amount

        results = [Item(30), Item(10), Item(20)]
        assert agg.apply_to_results(results) == 10

    def test_apply_max(self):
        """Test MAX aggregate on results"""
        agg = AggregateProjection(AggregateFunction.MAX, "amount")

        class Item:
            def __init__(self, amount):
                self.amount = amount

        results = [Item(30), Item(10), Item(20)]
        assert agg.apply_to_results(results) == 30

    def test_apply_count_distinct(self):
        """Test COUNT DISTINCT aggregate"""
        agg = AggregateProjection(AggregateFunction.COUNT_DISTINCT, "category")

        class Item:
            def __init__(self, category):
                self.category = category

        results = [Item("A"), Item("B"), Item("A"), Item("C"), Item("B")]
        assert agg.apply_to_results(results) == 3


class TestProjectionList:
    """Tests for ProjectionList class"""

    def test_simple_projection_list(self):
        """Test projection list with simple fields"""
        proj_list = ProjectionList([FieldProjection("name"), FieldProjection("email")])
        assert len(proj_list.fields) == 2
        assert proj_list.distinct is False

    def test_projection_list_with_distinct(self):
        """Test projection list with DISTINCT flag"""
        proj_list = ProjectionList([FieldProjection("category")], distinct=True)
        assert proj_list.distinct is True

    def test_projection_list_with_aggregates(self):
        """Test projection list with aggregate functions"""
        proj_list = ProjectionList(
            [
                FieldProjection("category"),
                AggregateProjection(AggregateFunction.COUNT, alias="count"),
            ]
        )
        assert len(proj_list.fields) == 2
        assert proj_list.has_aggregates() is True

    def test_projection_list_without_aggregates(self):
        """Test has_aggregates returns False when no aggregates present"""
        proj_list = ProjectionList([FieldProjection("name"), FieldProjection("email")])
        assert proj_list.has_aggregates() is False

    def test_apply_to_results_single_field(self):
        """Test applying projection with single field to results"""
        proj_list = ProjectionList([FieldProjection("name")])

        class Item:
            def __init__(self, name):
                self.name = name

        results = [Item("Alice"), Item("Bob"), Item("Charlie")]
        projected = list(proj_list.apply_to_results(results))

        assert projected == ["Alice", "Bob", "Charlie"]

    def test_apply_to_results_multiple_fields(self):
        """Test applying projection with multiple fields to results"""
        proj_list = ProjectionList([FieldProjection("name"), FieldProjection("age")])

        class Item:
            def __init__(self, name, age):
                self.name = name
                self.age = age

        results = [Item("Alice", 30), Item("Bob", 25)]
        projected = list(proj_list.apply_to_results(results))

        assert projected == [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]

    def test_apply_to_results_with_alias(self):
        """Test applying projection with field aliases"""
        proj_list = ProjectionList(
            [FieldProjection("name", alias="full_name"), FieldProjection("age")]
        )

        class Item:
            def __init__(self, name, age):
                self.name = name
                self.age = age

        results = [Item("Alice", 30)]
        projected = list(proj_list.apply_to_results(results))

        assert projected == [{"full_name": "Alice", "age": 30}]

    def test_apply_to_results_distinct(self):
        """Test applying projection with DISTINCT"""
        proj_list = ProjectionList([FieldProjection("category")], distinct=True)

        class Item:
            def __init__(self, category):
                self.category = category

        results = [Item("A"), Item("B"), Item("A"), Item("C"), Item("B")]
        projected = list(proj_list.apply_to_results(results))

        assert set(projected) == {"A", "B", "C"}
        assert len(projected) == 3

    def test_apply_to_results_with_aggregates(self):
        """Test applying projection with aggregate functions"""
        proj_list = ProjectionList(
            [
                AggregateProjection(AggregateFunction.COUNT, alias="total"),
                AggregateProjection(AggregateFunction.SUM, "amount", "total_amount"),
            ]
        )

        class Item:
            def __init__(self, amount):
                self.amount = amount

        results = [Item(10), Item(20), Item(30)]
        projected = list(proj_list.apply_to_results(results))

        assert len(projected) == 1
        assert projected[0]["total"] == 3
        assert projected[0]["total_amount"] == 60

    def test_apply_to_results_no_fields(self):
        """Test applying empty projection returns all results"""
        proj_list = ProjectionList([])

        class Item:
            def __init__(self, value):
                self.value = value

        results = [Item(1), Item(2)]
        projected = list(proj_list.apply_to_results(results))

        assert len(projected) == 2
        assert projected[0].value == 1

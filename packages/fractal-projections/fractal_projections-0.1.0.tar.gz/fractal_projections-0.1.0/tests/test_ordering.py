"""
Tests for ordering projection classes
"""

from fractal_projections.projections.ordering import OrderingList, OrderingProjection


class TestOrderingProjection:
    """Tests for OrderingProjection class"""

    def test_ascending_by_default(self):
        """Test that ordering is ascending by default"""
        ordering = OrderingProjection("created_at")
        assert ordering.field == "created_at"
        assert ordering.ascending is True

    def test_explicit_ascending(self):
        """Test explicitly setting ascending order"""
        ordering = OrderingProjection("name", ascending=True)
        assert ordering.field == "name"
        assert ordering.ascending is True

    def test_descending_order(self):
        """Test descending order"""
        ordering = OrderingProjection("created_at", ascending=False)
        assert ordering.field == "created_at"
        assert ordering.ascending is False

    def test_direction_property_ascending(self):
        """Test direction property for ascending order"""
        ordering = OrderingProjection("name", ascending=True)
        assert ordering.direction == "ASC"

    def test_direction_property_descending(self):
        """Test direction property for descending order"""
        ordering = OrderingProjection("name", ascending=False)
        assert ordering.direction == "DESC"

    def test_str_representation_ascending(self):
        """Test string representation for ascending order"""
        ordering = OrderingProjection("name", ascending=True)
        result = str(ordering)
        assert "name" in result
        assert "↑" in result

    def test_str_representation_descending(self):
        """Test string representation for descending order"""
        ordering = OrderingProjection("created_at", ascending=False)
        result = str(ordering)
        assert "created_at" in result
        assert "↓" in result


class TestOrderingList:
    """Tests for OrderingList class"""

    def test_empty_ordering_list(self):
        """Test creating empty ordering list"""
        ordering_list = OrderingList([])
        assert len(ordering_list) == 0
        assert bool(ordering_list) is False

    def test_single_ordering(self):
        """Test ordering list with single ordering"""
        ordering_list = OrderingList([OrderingProjection("name")])
        assert len(ordering_list) == 1

    def test_multiple_orderings(self):
        """Test ordering list with multiple orderings"""
        ordering_list = OrderingList(
            [
                OrderingProjection("department"),
                OrderingProjection("salary", ascending=False),
                OrderingProjection("name"),
            ]
        )
        assert len(ordering_list) == 3

    def test_add_method(self):
        """Test adding ordering via add method"""
        ordering_list = OrderingList([])
        ordering_list.add("name")

        assert len(ordering_list) == 1
        assert ordering_list.orderings[0].field == "name"
        assert ordering_list.orderings[0].ascending is True

    def test_add_method_with_ascending_false(self):
        """Test adding descending ordering via add method"""
        ordering_list = OrderingList([])
        ordering_list.add("created_at", ascending=False)

        assert len(ordering_list) == 1
        assert ordering_list.orderings[0].field == "created_at"
        assert ordering_list.orderings[0].ascending is False

    def test_add_method_chaining(self):
        """Test that add method returns self for chaining"""
        ordering_list = OrderingList([])
        result = ordering_list.add("field1").add("field2")

        assert result is ordering_list
        assert len(ordering_list) == 2

    def test_add_desc_method(self):
        """Test adding descending ordering via add_desc method"""
        ordering_list = OrderingList([])
        ordering_list.add_desc("created_at")

        assert len(ordering_list) == 1
        assert ordering_list.orderings[0].field == "created_at"
        assert ordering_list.orderings[0].ascending is False

    def test_add_desc_method_chaining(self):
        """Test that add_desc method supports chaining"""
        ordering_list = OrderingList([])
        result = ordering_list.add("name").add_desc("created_at")

        assert result is ordering_list
        assert len(ordering_list) == 2
        assert ordering_list.orderings[0].ascending is True
        assert ordering_list.orderings[1].ascending is False

    def test_iteration(self):
        """Test iterating over ordering list"""
        orderings = [
            OrderingProjection("field1"),
            OrderingProjection("field2"),
        ]
        ordering_list = OrderingList(orderings)

        result = list(ordering_list)
        assert result == orderings

    def test_bool_operator_with_items(self):
        """Test bool operator returns True when list has items"""
        ordering_list = OrderingList([OrderingProjection("name")])
        assert bool(ordering_list) is True

    def test_bool_operator_empty(self):
        """Test bool operator returns False when list is empty"""
        ordering_list = OrderingList([])
        assert bool(ordering_list) is False

    def test_str_representation_single(self):
        """Test string representation with single ordering"""
        ordering_list = OrderingList([OrderingProjection("name")])
        result = str(ordering_list)
        assert "name" in result

    def test_str_representation_multiple(self):
        """Test string representation with multiple orderings"""
        ordering_list = OrderingList(
            [
                OrderingProjection("name"),
                OrderingProjection("created_at", ascending=False),
            ]
        )
        result = str(ordering_list)
        assert "name" in result
        assert "created_at" in result
        assert "," in result

    def test_iteration_with_for_loop(self):
        """Test that ordering list can be used in for loops"""
        ordering_list = OrderingList(
            [
                OrderingProjection("field1"),
                OrderingProjection("field2"),
                OrderingProjection("field3"),
            ]
        )

        fields = []
        for ordering in ordering_list:
            fields.append(ordering.field)

        assert fields == ["field1", "field2", "field3"]

    def test_none_orderings_becomes_empty_list(self):
        """Test that None orderings becomes empty list"""
        ordering_list = OrderingList(None)
        assert len(ordering_list) == 0

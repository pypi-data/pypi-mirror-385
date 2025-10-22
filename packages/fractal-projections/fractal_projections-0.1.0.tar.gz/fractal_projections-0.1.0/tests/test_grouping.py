"""
Tests for grouping projection classes
"""

import pytest

from fractal_projections.projections.grouping import GroupingProjection


class TestGroupingProjection:
    """Tests for GroupingProjection class"""

    def test_single_field_grouping(self):
        """Test grouping by a single field"""
        grouping = GroupingProjection(["category"])
        assert len(grouping.fields) == 1
        assert grouping.fields[0] == "category"

    def test_multiple_field_grouping(self):
        """Test grouping by multiple fields"""
        grouping = GroupingProjection(["department", "role", "location"])
        assert len(grouping.fields) == 3
        assert grouping.fields == ["department", "role", "location"]

    def test_empty_fields_raises_error(self):
        """Test that empty fields list raises ValueError"""
        with pytest.raises(ValueError, match="must have at least one field"):
            GroupingProjection([])

    def test_len_operator(self):
        """Test len() operator returns number of grouping fields"""
        grouping = GroupingProjection(["field1", "field2"])
        assert len(grouping) == 2

    def test_iteration(self):
        """Test iterating over grouping fields"""
        fields = ["category", "status"]
        grouping = GroupingProjection(fields)

        result = list(grouping)
        assert result == fields

    def test_contains_operator(self):
        """Test 'in' operator for checking if field is in grouping"""
        grouping = GroupingProjection(["category", "status"])

        assert "category" in grouping
        assert "status" in grouping
        assert "other_field" not in grouping

    def test_iteration_with_for_loop(self):
        """Test that grouping can be used in for loops"""
        fields = ["field1", "field2", "field3"]
        grouping = GroupingProjection(fields)

        collected = []
        for field in grouping:
            collected.append(field)

        assert collected == fields

"""
Tests for limiting projection classes
"""

import pytest

from fractal_projections.projections.limiting import LimitProjection


class TestLimitProjection:
    """Tests for LimitProjection class"""

    def test_simple_limit(self):
        """Test basic limit without offset"""
        limit = LimitProjection(10)
        assert limit.limit == 10
        assert limit.offset == 0

    def test_limit_with_offset(self):
        """Test limit with offset"""
        limit = LimitProjection(20, offset=40)
        assert limit.limit == 20
        assert limit.offset == 40

    def test_zero_limit_raises_error(self):
        """Test that zero limit raises ValueError"""
        with pytest.raises(ValueError, match="Limit must be greater than 0"):
            LimitProjection(0)

    def test_negative_limit_raises_error(self):
        """Test that negative limit raises ValueError"""
        with pytest.raises(ValueError, match="Limit must be greater than 0"):
            LimitProjection(-5)

    def test_negative_offset_raises_error(self):
        """Test that negative offset raises ValueError"""
        with pytest.raises(ValueError, match="Offset must be non-negative"):
            LimitProjection(10, offset=-1)

    def test_page_size_property(self):
        """Test page_size property is alias for limit"""
        limit = LimitProjection(25)
        assert limit.page_size == 25
        assert limit.page_size == limit.limit

    def test_skip_property(self):
        """Test skip property is alias for offset"""
        limit = LimitProjection(10, offset=50)
        assert limit.skip == 50
        assert limit.skip == limit.offset

    def test_page_number_one_based_first_page(self):
        """Test page_number for first page (1-based)"""
        limit = LimitProjection(10, offset=0)
        assert limit.page_number(one_based=True) == 1

    def test_page_number_one_based_second_page(self):
        """Test page_number for second page (1-based)"""
        limit = LimitProjection(10, offset=10)
        assert limit.page_number(one_based=True) == 2

    def test_page_number_one_based_third_page(self):
        """Test page_number for third page (1-based)"""
        limit = LimitProjection(20, offset=40)
        assert limit.page_number(one_based=True) == 3

    def test_page_number_zero_based_first_page(self):
        """Test page_number for first page (0-based)"""
        limit = LimitProjection(10, offset=0)
        assert limit.page_number(one_based=False) == 0

    def test_page_number_zero_based_second_page(self):
        """Test page_number for second page (0-based)"""
        limit = LimitProjection(10, offset=10)
        assert limit.page_number(one_based=False) == 1

    def test_page_number_default_is_one_based(self):
        """Test that page_number defaults to 1-based"""
        limit = LimitProjection(10, offset=20)
        assert limit.page_number() == 3

    def test_next_page(self):
        """Test next_page returns limit for next page"""
        limit = LimitProjection(10, offset=20)
        next_limit = limit.next_page()

        assert next_limit.limit == 10
        assert next_limit.offset == 30

    def test_next_page_from_first_page(self):
        """Test next_page from first page"""
        limit = LimitProjection(25, offset=0)
        next_limit = limit.next_page()

        assert next_limit.limit == 25
        assert next_limit.offset == 25

    def test_previous_page(self):
        """Test previous_page returns limit for previous page"""
        limit = LimitProjection(10, offset=30)
        prev_limit = limit.previous_page()

        assert prev_limit.limit == 10
        assert prev_limit.offset == 20

    def test_previous_page_from_second_page(self):
        """Test previous_page from second page goes to first"""
        limit = LimitProjection(15, offset=15)
        prev_limit = limit.previous_page()

        assert prev_limit.limit == 15
        assert prev_limit.offset == 0

    def test_previous_page_from_first_page(self):
        """Test previous_page from first page stays at zero"""
        limit = LimitProjection(10, offset=0)
        prev_limit = limit.previous_page()

        assert prev_limit.limit == 10
        assert prev_limit.offset == 0

    def test_str_representation_without_offset(self):
        """Test string representation without offset"""
        limit = LimitProjection(10)
        result = str(limit)

        assert "LIMIT 10" in result
        assert "OFFSET" not in result

    def test_str_representation_with_offset(self):
        """Test string representation with offset"""
        limit = LimitProjection(20, offset=40)
        result = str(limit)

        assert "LIMIT 20" in result
        assert "OFFSET 40" in result

    def test_page_navigation_sequence(self):
        """Test navigating through multiple pages"""
        # Start at page 1
        page1 = LimitProjection(10, offset=0)
        assert page1.page_number() == 1

        # Go to page 2
        page2 = page1.next_page()
        assert page2.page_number() == 2
        assert page2.offset == 10

        # Go to page 3
        page3 = page2.next_page()
        assert page3.page_number() == 3
        assert page3.offset == 20

        # Go back to page 2
        back_to_page2 = page3.previous_page()
        assert back_to_page2.page_number() == 2
        assert back_to_page2.offset == 10

    def test_partial_page_number(self):
        """Test page number calculation with non-aligned offset"""
        # Offset doesn't align perfectly with page size
        limit = LimitProjection(10, offset=15)
        # Should be page 2 (offset 15 / limit 10 = 1, +1 for 1-based = 2)
        assert limit.page_number() == 2

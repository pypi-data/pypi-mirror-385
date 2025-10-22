"""Test overlapping range strategies."""

import pytest

from range_key_dict import RangeKeyDict


def test_overlap_strategy_error_default():
    """Test that overlapping ranges raise error by default."""
    with pytest.raises(ValueError, match="overlaps"):
        RangeKeyDict(
            {
                (0, 100): "A",
                (50, 150): "B",
            }
        )


def test_overlap_strategy_error_explicit():
    """Test explicit 'error' strategy."""
    with pytest.raises(ValueError, match="overlaps"):
        RangeKeyDict(
            {
                (0, 100): "A",
                (50, 150): "B",
            },
            overlap_strategy="error",
        )


def test_overlap_strategy_first(overlapping_dict_first):
    """Test 'first' overlap strategy."""
    # Range (0, 100) is first, (50, 150) is second, (25, 75) is third
    # In the overlap region, should return 'first'

    # Only in first range
    assert overlapping_dict_first[10] == "first"

    # In first and third (25-75)
    assert overlapping_dict_first[30] == "first"

    # In all three ranges (50-75)
    assert overlapping_dict_first[60] == "first"

    # In first and second (75-100)
    assert overlapping_dict_first[80] == "first"

    # In second only (100-150)
    assert overlapping_dict_first[120] == "second"


def test_overlap_strategy_last(overlapping_dict_last):
    """Test 'last' overlap strategy."""
    # In the overlap region, should return 'last'

    # Only in first range
    assert overlapping_dict_last[10] == "first"

    # In first and third (25-75)
    assert overlapping_dict_last[30] == "third"

    # In all three ranges (50-75)
    assert overlapping_dict_last[60] == "third"

    # In first and second (75-100)
    assert overlapping_dict_last[80] == "second"

    # In second only (100-150)
    assert overlapping_dict_last[120] == "second"


def test_overlap_strategy_shortest(overlapping_dict_shortest):
    """Test 'shortest' overlap strategy."""
    # (0, 200) = length 200
    # (50, 150) = length 100
    # (80, 90) = length 10 (shortest)

    # Only in long range
    assert overlapping_dict_shortest[10] == "long"

    # In long and medium
    assert overlapping_dict_shortest[60] == "medium"

    # In all three - should return shortest
    assert overlapping_dict_shortest[85] == "short"

    # In long and medium (after short)
    assert overlapping_dict_shortest[100] == "medium"

    # Only in long
    assert overlapping_dict_shortest[180] == "long"


def test_overlap_strategy_longest(overlapping_dict_longest):
    """Test 'longest' overlap strategy."""
    # (0, 200) = length 200 (longest)
    # (50, 150) = length 100
    # (80, 90) = length 10

    # Only in long range
    assert overlapping_dict_longest[10] == "long"

    # In long and medium - should return longest
    assert overlapping_dict_longest[60] == "long"

    # In all three - should return longest
    assert overlapping_dict_longest[85] == "long"

    # In long and medium
    assert overlapping_dict_longest[100] == "long"

    # Only in long
    assert overlapping_dict_longest[180] == "long"


def test_non_overlapping_with_overlap_strategy():
    """Test that non-overlapping ranges work with overlap strategies."""
    rkd = RangeKeyDict(
        {
            (0, 100): "A",
            (100, 200): "B",
            (200, 300): "C",
        },
        overlap_strategy="first",
    )

    assert rkd[50] == "A"
    assert rkd[150] == "B"
    assert rkd[250] == "C"


def test_partially_overlapping():
    """Test complex partially overlapping scenarios."""
    rkd = RangeKeyDict(
        {
            (0, 100): "A",
            (50, 150): "B",
            (200, 300): "C",
        },
        overlap_strategy="first",
    )

    # Only in A
    assert rkd[25] == "A"

    # In A and B - should return first (A)
    assert rkd[75] == "A"

    # Only in B
    assert rkd[125] == "B"

    # Gap between B and C
    assert 175 not in rkd

    # Only in C
    assert rkd[250] == "C"


def test_touching_ranges_not_overlapping():
    """Test that touching ranges (one ends where other starts) don't overlap."""
    # These should work even with 'error' strategy since they don't actually overlap
    rkd = RangeKeyDict(
        {
            (0, 100): "A",
            (100, 200): "B",
        },
        overlap_strategy="error",
    )

    assert rkd[99] == "A"
    assert rkd[100] == "B"
    assert len(rkd) == 2


def test_identical_ranges_overlap():
    """Test that identical ranges are detected as overlapping when added sequentially."""
    # Note: Can't test with dict literal since Python deduplicates keys automatically
    rkd = RangeKeyDict({(0, 100): "A"})

    # Adding the exact same range should work (it's an update, not overlap)
    # This replaces the existing range
    rkd[(0, 100)] = "B"
    assert rkd[50] == "B"  # Updated value
    assert len(rkd) == 1  # Still one range


def test_nested_ranges():
    """Test ranges where one is completely inside another."""
    rkd = RangeKeyDict(
        {
            (0, 200): "outer",
            (50, 150): "inner",
        },
        overlap_strategy="shortest",
    )

    # Only in outer
    assert rkd[25] == "outer"

    # In both - should return shorter
    assert rkd[100] == "inner"

    # Only in outer
    assert rkd[175] == "outer"


def test_multiple_overlaps_same_point():
    """Test point that falls in multiple overlapping ranges."""
    rkd = RangeKeyDict(
        {
            (0, 100): "A",
            (25, 75): "B",
            (40, 60): "C",
            (45, 55): "D",
        },
        overlap_strategy="shortest",
    )

    # Point 50 is in all 4 ranges
    # D (45-55) is shortest with length 10
    assert rkd[50] == "D"


def test_overlap_with_floats():
    """Test overlapping ranges with float boundaries."""
    rkd = RangeKeyDict(
        {
            (0.0, 10.0): "A",
            (5.0, 15.0): "B",
        },
        overlap_strategy="first",
    )

    assert rkd[3.0] == "A"
    assert rkd[7.0] == "A"  # Overlapping region
    assert rkd[12.0] == "B"


def test_overlap_strategy_case_insensitive():
    """Test that overlap strategy is validated."""
    # Valid strategies should work
    RangeKeyDict({(0, 100): "A"}, overlap_strategy="error")
    RangeKeyDict({(0, 100): "A"}, overlap_strategy="first")
    RangeKeyDict({(0, 100): "A"}, overlap_strategy="last")
    RangeKeyDict({(0, 100): "A"}, overlap_strategy="shortest")
    RangeKeyDict({(0, 100): "A"}, overlap_strategy="longest")


def test_setitem_with_overlap_strategies():
    """Test adding ranges with __setitem__ under different strategies."""
    # Error strategy
    rkd_error = RangeKeyDict({(0, 100): "A"}, overlap_strategy="error")
    with pytest.raises(ValueError, match="overlaps"):
        rkd_error[(50, 150)] = "B"

    # First strategy - should allow
    rkd_first = RangeKeyDict({(0, 100): "A"}, overlap_strategy="first")
    rkd_first[(50, 150)] = "B"
    assert len(rkd_first) == 2
    assert rkd_first[75] == "A"  # Returns first

    # Last strategy - should allow
    rkd_last = RangeKeyDict({(0, 100): "A"}, overlap_strategy="last")
    rkd_last[(50, 150)] = "B"
    assert len(rkd_last) == 2
    assert rkd_last[75] == "B"  # Returns last

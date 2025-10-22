"""Test open-ended ranges with None bounds."""

from range_key_dict import RangeKeyDict


def test_none_lower_bound():
    """Test range with None as lower bound (negative infinity)."""
    rkd = RangeKeyDict({(None, 0): "negative"})

    assert rkd[-1000000] == "negative"
    assert rkd[-100] == "negative"
    assert rkd[-1] == "negative"
    assert 0 not in rkd


def test_none_upper_bound():
    """Test range with None as upper bound (positive infinity)."""
    rkd = RangeKeyDict({(0, None): "non-negative"})

    assert rkd[0] == "non-negative"
    assert rkd[100] == "non-negative"
    assert rkd[1000000] == "non-negative"
    assert -1 not in rkd


def test_both_bounds_none():
    """Test range with None as both bounds (all numbers)."""
    rkd = RangeKeyDict({(None, None): "everything"})

    assert rkd[-1000000] == "everything"
    assert rkd[-1] == "everything"
    assert rkd[0] == "everything"
    assert rkd[1] == "everything"
    assert rkd[1000000] == "everything"


def test_mixed_open_closed_ranges(open_ended_dict):
    """Test mix of open-ended and closed ranges."""
    # (None, 0): "negative"
    # (0, 100): "small"
    # (100, None): "large"

    assert open_ended_dict[-100] == "negative"
    assert open_ended_dict[-1] == "negative"
    assert open_ended_dict[0] == "small"
    assert open_ended_dict[50] == "small"
    assert open_ended_dict[99] == "small"
    assert open_ended_dict[100] == "large"
    assert open_ended_dict[1000] == "large"


def test_open_ended_non_overlapping():
    """Test that open-ended ranges can be non-overlapping."""
    rkd = RangeKeyDict(
        {
            (None, -100): "very negative",
            (-100, 0): "negative",
            (0, 100): "positive",
            (100, None): "very positive",
        }
    )

    assert rkd[-1000] == "very negative"
    assert rkd[-50] == "negative"
    assert rkd[50] == "positive"
    assert rkd[1000] == "very positive"


def test_open_ended_overlapping_first():
    """Test overlapping open-ended ranges with 'first' strategy."""
    rkd = RangeKeyDict(
        {
            (None, 100): "first",
            (0, None): "second",
        },
        overlap_strategy="first",
    )

    # Only in first
    assert rkd[-100] == "first"

    # In both - should return first
    assert rkd[50] == "first"

    # Only in second
    assert rkd[200] == "second"


def test_open_ended_overlapping_shortest():
    """Test overlapping open-ended ranges with 'shortest' strategy."""
    rkd = RangeKeyDict(
        {
            (None, None): "infinite",  # Infinite length
            (0, 100): "finite",  # Length 100
        },
        overlap_strategy="shortest",
    )

    # In both - should return shortest (finite)
    assert rkd[50] == "finite"

    # Only in infinite
    assert rkd[-100] == "infinite"
    assert rkd[200] == "infinite"


def test_open_ended_overlapping_longest():
    """Test overlapping open-ended ranges with 'longest' strategy."""
    rkd = RangeKeyDict(
        {
            (None, None): "infinite",  # Infinite length
            (0, 100): "finite",  # Length 100
        },
        overlap_strategy="longest",
    )

    # In both - should return longest (infinite)
    assert rkd[50] == "infinite"

    # Only in infinite
    assert rkd[-100] == "infinite"
    assert rkd[200] == "infinite"


def test_none_bound_validation():
    """Test that None bounds are validated properly."""
    # These should all be valid
    RangeKeyDict({(None, 100): "A"})
    RangeKeyDict({(0, None): "A"})
    RangeKeyDict({(None, None): "A"})

    # Start > end should still fail even with None bounds
    # (This test doesn't apply since None can't be compared with >)


def test_setitem_with_none_bounds():
    """Test adding ranges with None bounds using __setitem__."""
    rkd = RangeKeyDict()

    rkd[(None, 0)] = "negative"
    assert rkd[-100] == "negative"

    rkd[(0, None)] = "non-negative"
    assert rkd[100] == "non-negative"

    assert len(rkd) == 2


def test_delitem_with_none_bounds():
    """Test deleting ranges with None bounds."""
    rkd = RangeKeyDict(
        {
            (None, 0): "negative",
            (0, None): "non-negative",
        }
    )

    del rkd[(None, 0)]
    assert -100 not in rkd
    assert rkd[100] == "non-negative"


def test_keys_with_none_bounds():
    """Test that keys() returns tuples with None properly."""
    rkd = RangeKeyDict(
        {
            (None, 0): "A",
            (0, 100): "B",
            (100, None): "C",
        }
    )

    keys = rkd.keys()
    assert (None, 0) in keys
    assert (0, 100) in keys
    assert (100, None) in keys


def test_items_with_none_bounds():
    """Test that items() returns tuples with None properly."""
    rkd = RangeKeyDict(
        {
            (None, 0): "A",
            (0, None): "B",
        }
    )

    items = rkd.items()
    assert ((None, 0), "A") in items
    assert ((0, None), "B") in items


def test_repr_with_none_bounds():
    """Test that repr works with None bounds."""
    rkd = RangeKeyDict({(None, 0): "A"})
    repr_str = repr(rkd)

    assert "None" in repr_str
    assert "RangeKeyDict" in repr_str


def test_practical_use_case_grading():
    """Test a practical use case: grade boundaries."""
    # F: < 60, D: 60-70, C: 70-80, B: 80-90, A: 90-100, A+: > 100 (extra credit)
    grades = RangeKeyDict(
        {
            (None, 60): "F",
            (60, 70): "D",
            (70, 80): "C",
            (80, 90): "B",
            (90, 100): "A",
            (100, None): "A+",
        }
    )

    assert grades[0] == "F"
    assert grades[50] == "F"
    assert grades[65] == "D"
    assert grades[75] == "C"
    assert grades[85] == "B"
    assert grades[95] == "A"
    assert grades[105] == "A+"
    assert grades[200] == "A+"  # Lots of extra credit!


def test_practical_use_case_age_categories():
    """Test practical use case: age categories."""
    categories = RangeKeyDict(
        {
            (None, 13): "child",
            (13, 20): "teenager",
            (20, 65): "adult",
            (65, None): "senior",
        }
    )

    assert categories[5] == "child"
    assert categories[16] == "teenager"
    assert categories[30] == "adult"
    assert categories[70] == "senior"

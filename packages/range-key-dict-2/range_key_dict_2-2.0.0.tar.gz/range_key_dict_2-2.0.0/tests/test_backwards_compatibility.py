"""Test backwards compatibility with range-key-dict v1."""

import pytest

from range_key_dict import RangeKeyDict


def test_original_example():
    """Test the exact example from the original range-key-dict."""
    range_key_dict = RangeKeyDict(
        {
            (0, 100): "A",
            (100, 200): "B",
            (200, 300): "C",
        }
    )

    # test normal case
    assert range_key_dict[70] == "A"
    assert range_key_dict[170] == "B"
    assert range_key_dict[270] == "C"

    # test case when the number is float
    assert range_key_dict[70.5] == "A"

    # test case not in the range, with default value
    assert range_key_dict.get(1000, "D") == "D"


def test_get_method_with_default():
    """Test the get method with default values."""
    rkd = RangeKeyDict({(0, 100): "value"})

    assert rkd.get(50) == "value"
    assert rkd.get(150) is None
    assert rkd.get(150, "default") == "default"
    assert rkd.get(150, 42) == 42


def test_getitem_raises_keyerror():
    """Test that __getitem__ raises KeyError for out-of-range values."""
    rkd = RangeKeyDict({(0, 100): "value"})

    with pytest.raises(KeyError):
        _ = rkd[150]

    with pytest.raises(KeyError):
        _ = rkd[-50]


def test_tuple_key_initialization():
    """Test initialization with tuple keys."""
    rkd = RangeKeyDict(
        {
            (0, 10): "first",
            (10, 20): "second",
        }
    )

    assert rkd[5] == "first"
    assert rkd[15] == "second"


def test_integer_ranges():
    """Test with integer range boundaries."""
    rkd = RangeKeyDict(
        {
            (0, 100): "A",
            (100, 200): "B",
        }
    )

    assert rkd[0] == "A"
    assert rkd[99] == "A"
    assert rkd[100] == "B"
    assert rkd[199] == "B"

    with pytest.raises(KeyError):
        _ = rkd[200]


def test_float_ranges():
    """Test with float range boundaries and lookups."""
    rkd = RangeKeyDict(
        {
            (0.0, 10.5): "A",
            (10.5, 20.0): "B",
        }
    )

    assert rkd[0.0] == "A"
    assert rkd[5.25] == "A"
    assert rkd[10.4] == "A"
    assert rkd[10.5] == "B"
    assert rkd[15.0] == "B"


def test_negative_ranges():
    """Test with negative number ranges."""
    rkd = RangeKeyDict(
        {
            (-100, 0): "negative",
            (0, 100): "positive",
        }
    )

    assert rkd[-50] == "negative"
    assert rkd[-1] == "negative"
    assert rkd[0] == "positive"
    assert rkd[50] == "positive"


def test_empty_initialization():
    """Test creating an empty RangeKeyDict."""
    rkd = RangeKeyDict()
    assert len(rkd) == 0

    with pytest.raises(KeyError):
        _ = rkd[0]


def test_single_range():
    """Test with a single range."""
    rkd = RangeKeyDict({(0, 100): "only"})

    assert rkd[0] == "only"
    assert rkd[50] == "only"
    assert rkd[99] == "only"
    assert rkd.get(100) is None


def test_non_overlapping_ranges():
    """Test that non-overlapping ranges work correctly."""
    rkd = RangeKeyDict(
        {
            (0, 10): "A",
            (20, 30): "B",
            (40, 50): "C",
        }
    )

    assert rkd[5] == "A"
    assert rkd[25] == "B"
    assert rkd[45] == "C"
    assert rkd.get(15) is None
    assert rkd.get(35) is None


def test_invalid_range_order():
    """Test that ranges with start > end raise ValueError."""
    with pytest.raises(ValueError, match="start.*must be.*end"):
        RangeKeyDict({(100, 50): "invalid"})


def test_invalid_key_type():
    """Test that non-tuple keys raise TypeError."""
    with pytest.raises(TypeError, match="must be a 2-tuple"):
        RangeKeyDict({100: "invalid"})  # type: ignore

    with pytest.raises(TypeError, match="must be a 2-tuple"):
        RangeKeyDict({(100,): "invalid"})  # type: ignore

    with pytest.raises(TypeError, match="must be a 2-tuple"):
        RangeKeyDict({(100, 200, 300): "invalid"})  # type: ignore

"""Test edge cases and boundary conditions."""

import pytest

from range_key_dict import RangeKeyDict


def test_empty_dict_operations():
    """Test operations on an empty dictionary."""
    rkd = RangeKeyDict()

    assert len(rkd) == 0
    assert list(rkd) == []
    assert rkd.keys() == []
    assert rkd.values() == []
    assert rkd.items() == []
    assert 0 not in rkd
    assert 100 not in rkd
    assert rkd.get(0) is None
    assert rkd.get(0, "default") == "default"

    with pytest.raises(KeyError):
        _ = rkd[0]


def test_single_range_boundaries():
    """Test exact boundaries of a single range."""
    rkd = RangeKeyDict({(10, 20): "value"})

    # Just inside
    assert rkd[10] == "value"
    assert rkd[19.999] == "value"

    # Just outside
    assert 9.999 not in rkd
    assert 20 not in rkd
    assert 20.001 not in rkd


def test_zero_length_range():
    """Test range with same start and end."""
    # This should be valid but contain no numbers
    rkd = RangeKeyDict({(10, 10): "empty"})

    assert 9 not in rkd
    assert 10 not in rkd  # Range is [10, 10) so 10 is not included
    assert 11 not in rkd


def test_very_small_range():
    """Test very small floating point range."""
    rkd = RangeKeyDict({(0.0, 0.001): "tiny"})

    assert rkd[0.0] == "tiny"
    assert rkd[0.0005] == "tiny"
    assert 0.001 not in rkd


def test_very_large_numbers():
    """Test with very large numbers."""
    rkd = RangeKeyDict(
        {
            (1e10, 1e11): "large",
        }
    )

    assert rkd[5e10] == "large"
    assert 1e9 not in rkd
    assert 1e12 not in rkd


def test_very_negative_numbers():
    """Test with very negative numbers."""
    rkd = RangeKeyDict(
        {
            (-1e11, -1e10): "very negative",
        }
    )

    assert rkd[-5e10] == "very negative"
    assert -1e9 not in rkd
    assert -1e12 not in rkd


def test_many_ranges():
    """Test with many ranges."""
    ranges = {(i * 10, (i + 1) * 10): f"range_{i}" for i in range(100)}
    rkd = RangeKeyDict(ranges)

    assert len(rkd) == 100
    assert rkd[5] == "range_0"
    assert rkd[155] == "range_15"
    assert rkd[995] == "range_99"


def test_adjacent_ranges_no_gaps():
    """Test adjacent ranges with no gaps."""
    rkd = RangeKeyDict(
        {
            (0, 10): "A",
            (10, 20): "B",
            (20, 30): "C",
        }
    )

    # Test boundaries
    assert rkd[0] == "A"
    assert rkd[9.999] == "A"
    assert rkd[10] == "B"
    assert rkd[19.999] == "B"
    assert rkd[20] == "C"
    assert rkd[29.999] == "C"

    # No gaps
    assert 30 not in rkd


def test_ranges_with_gaps():
    """Test ranges with intentional gaps."""
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

    # Gaps
    assert 15 not in rkd
    assert 35 not in rkd
    assert 55 not in rkd


def test_unicode_values():
    """Test with unicode string values."""
    rkd = RangeKeyDict(
        {
            (0, 100): "😀",
            (100, 200): "日本語",
            (200, 300): "العربية",
        }
    )

    assert rkd[50] == "😀"
    assert rkd[150] == "日本語"
    assert rkd[250] == "العربية"


def test_complex_object_values():
    """Test with complex objects as values."""
    obj1 = {"key": "value1", "list": [1, 2, 3]}
    obj2 = ["a", "b", "c"]
    obj3 = (1, 2, 3)

    rkd = RangeKeyDict(
        {
            (0, 100): obj1,
            (100, 200): obj2,
            (200, 300): obj3,
        }
    )

    assert rkd[50] == obj1
    assert rkd[150] == obj2
    assert rkd[250] == obj3


def test_none_as_value():
    """Test with None as a value (different from None as bound)."""
    rkd = RangeKeyDict(
        {
            (0, 100): None,
            (100, 200): "not none",
        }
    )

    assert rkd[50] is None
    assert rkd[150] == "not none"
    assert rkd.get(50) is None
    assert rkd.get(250) is None  # Different: not in range


def test_boolean_values():
    """Test with boolean values."""
    rkd = RangeKeyDict(
        {
            (0, 100): True,
            (100, 200): False,
        }
    )

    assert rkd[50] is True
    assert rkd[150] is False


def test_function_values():
    """Test with functions as values."""

    def func1():
        return "A"

    def func2():
        return "B"

    rkd = RangeKeyDict(
        {
            (0, 100): func1,
            (100, 200): func2,
        }
    )

    assert rkd[50]() == "A"
    assert rkd[150]() == "B"


def test_class_instance_values():
    """Test with class instances as values."""

    class MyClass:
        def __init__(self, value):
            self.value = value

    obj1 = MyClass("A")
    obj2 = MyClass("B")

    rkd = RangeKeyDict(
        {
            (0, 100): obj1,
            (100, 200): obj2,
        }
    )

    assert rkd[50].value == "A"
    assert rkd[150].value == "B"


def test_negative_to_positive_range():
    """Test range spanning negative to positive."""
    rkd = RangeKeyDict({(-50, 50): "around zero"})

    assert rkd[-25] == "around zero"
    assert rkd[0] == "around zero"
    assert rkd[25] == "around zero"


def test_float_precision():
    """Test floating point precision edge cases."""
    rkd = RangeKeyDict(
        {
            (0.1, 0.2): "A",
            (0.2, 0.3): "B",
        }
    )

    assert rkd[0.15] == "A"
    assert rkd[0.25] == "B"

    # Exact boundary
    assert rkd[0.2] == "B"


def test_scientific_notation():
    """Test with numbers in scientific notation."""
    rkd = RangeKeyDict(
        {
            (1e-10, 1e-5): "very small",
            (1e5, 1e10): "very large",
        }
    )

    assert rkd[1e-8] == "very small"
    assert rkd[1e7] == "very large"


def test_update_then_query():
    """Test updating a range and then querying."""
    rkd = RangeKeyDict({(0, 100): "original"})
    assert rkd[50] == "original"

    rkd[(0, 100)] = "updated"
    assert rkd[50] == "updated"

    # Should still be same number of ranges
    assert len(rkd) == 1


def test_delete_and_readd():
    """Test deleting and re-adding a range."""
    rkd = RangeKeyDict({(0, 100): "value1"})
    assert rkd[50] == "value1"

    del rkd[(0, 100)]
    assert 50 not in rkd

    rkd[(0, 100)] = "value2"
    assert rkd[50] == "value2"


def test_mixed_int_float_boundaries():
    """Test mixing int and float boundaries."""
    rkd = RangeKeyDict(
        {
            (0, 100.5): "A",
            (100.5, 200): "B",
        }
    )

    assert rkd[50] == "A"
    assert rkd[100] == "A"
    assert rkd[100.5] == "B"
    assert rkd[150] == "B"


def test_equality_with_same_content_different_order():
    """Test equality when ranges added in different order."""
    rkd1 = RangeKeyDict(
        {
            (0, 100): "A",
            (100, 200): "B",
        }
    )

    rkd2 = RangeKeyDict(
        {
            (100, 200): "B",
            (0, 100): "A",
        }
    )

    # Should be equal since they contain the same ranges
    assert rkd1 == rkd2


def test_get_with_various_defaults():
    """Test get method with various default values."""
    rkd = RangeKeyDict({(0, 100): "value"})

    assert rkd.get(150) is None
    assert rkd.get(150, "default") == "default"
    assert rkd.get(150, 0) == 0
    assert rkd.get(150, []) == []
    assert rkd.get(150, {"key": "value"}) == {"key": "value"}


def test_iteration_order():
    """Test that iteration maintains sorted order."""
    rkd = RangeKeyDict(
        {
            (200, 300): "C",
            (0, 100): "A",
            (100, 200): "B",
        }
    )

    keys = list(rkd.keys())
    assert keys == [(0, 100), (100, 200), (200, 300)]


def test_contains_with_different_types():
    """Test __contains__ with int and float."""
    rkd = RangeKeyDict({(0, 100): "value"})

    assert 50 in rkd
    assert 50.0 in rkd
    assert 50.5 in rkd

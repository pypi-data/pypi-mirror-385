"""Test dict-like interface methods."""

import pytest

from range_key_dict import RangeKeyDict


def test_len(simple_dict):
    """Test __len__ method."""
    assert len(simple_dict) == 3

    empty = RangeKeyDict()
    assert len(empty) == 0

    single = RangeKeyDict({(0, 100): "value"})
    assert len(single) == 1


def test_contains(simple_dict):
    """Test __contains__ method."""
    assert 50 in simple_dict
    assert 150 in simple_dict
    assert 250 in simple_dict

    assert 0 in simple_dict
    assert 100 in simple_dict
    assert 200 in simple_dict

    assert -1 not in simple_dict
    assert 300 not in simple_dict
    assert 999 not in simple_dict


def test_keys(simple_dict):
    """Test keys method."""
    keys = simple_dict.keys()
    assert len(keys) == 3
    assert (0, 100) in keys
    assert (100, 200) in keys
    assert (200, 300) in keys


def test_values(simple_dict):
    """Test values method."""
    values = simple_dict.values()
    assert len(values) == 3
    assert "A" in values
    assert "B" in values
    assert "C" in values


def test_items(simple_dict):
    """Test items method."""
    items = simple_dict.items()
    assert len(items) == 3
    assert ((0, 100), "A") in items
    assert ((100, 200), "B") in items
    assert ((200, 300), "C") in items


def test_iter(simple_dict):
    """Test __iter__ method."""
    keys = list(simple_dict)
    assert len(keys) == 3
    assert (0, 100) in keys
    assert (100, 200) in keys
    assert (200, 300) in keys


def test_setitem_new_range():
    """Test adding a new range with __setitem__."""
    rkd = RangeKeyDict()
    rkd[(0, 100)] = "A"

    assert len(rkd) == 1
    assert rkd[50] == "A"


def test_setitem_update_existing():
    """Test updating an existing range with __setitem__."""
    rkd = RangeKeyDict({(0, 100): "A"})
    assert rkd[50] == "A"

    rkd[(0, 100)] = "B"
    assert rkd[50] == "B"
    assert len(rkd) == 1  # Should still be 1 range


def test_setitem_multiple_ranges():
    """Test adding multiple ranges."""
    rkd = RangeKeyDict()
    rkd[(0, 100)] = "A"
    rkd[(100, 200)] = "B"
    rkd[(200, 300)] = "C"

    assert len(rkd) == 3
    assert rkd[50] == "A"
    assert rkd[150] == "B"
    assert rkd[250] == "C"


def test_setitem_invalid_key():
    """Test that __setitem__ validates keys."""
    rkd = RangeKeyDict()

    with pytest.raises(TypeError):
        rkd[100] = "invalid"  # type: ignore

    with pytest.raises(ValueError):
        rkd[(100, 50)] = "invalid"  # start > end


def test_setitem_overlapping_error():
    """Test that __setitem__ raises error for overlapping ranges by default."""
    rkd = RangeKeyDict({(0, 100): "A"})

    with pytest.raises(ValueError, match="overlaps"):
        rkd[(50, 150)] = "B"


def test_delitem():
    """Test deleting a range with __delitem__."""
    rkd = RangeKeyDict(
        {
            (0, 100): "A",
            (100, 200): "B",
            (200, 300): "C",
        }
    )

    assert len(rkd) == 3
    del rkd[(100, 200)]
    assert len(rkd) == 2

    assert rkd[50] == "A"
    assert 150 not in rkd
    assert rkd[250] == "C"


def test_delitem_nonexistent():
    """Test that deleting a nonexistent range raises KeyError."""
    rkd = RangeKeyDict({(0, 100): "A"})

    with pytest.raises(KeyError):
        del rkd[(100, 200)]


def test_repr():
    """Test __repr__ method."""
    rkd = RangeKeyDict({(0, 100): "A"})
    repr_str = repr(rkd)

    assert "RangeKeyDict" in repr_str
    assert "(0, 100)" in repr_str
    assert "'A'" in repr_str


def test_str():
    """Test __str__ method."""
    rkd = RangeKeyDict({(0, 100): "A"})
    str_repr = str(rkd)

    assert "RangeKeyDict" in str_repr
    assert "(0, 100)" in str_repr


def test_eq():
    """Test equality comparison."""
    rkd1 = RangeKeyDict({(0, 100): "A", (100, 200): "B"})
    rkd2 = RangeKeyDict({(0, 100): "A", (100, 200): "B"})
    rkd3 = RangeKeyDict({(0, 100): "A"})

    assert rkd1 == rkd2
    assert rkd1 != rkd3
    assert rkd1 != "not a dict"
    assert rkd1 != 42


def test_empty_dict_operations(empty_dict):
    """Test operations on empty dict."""
    assert len(empty_dict) == 0
    assert list(empty_dict) == []
    assert empty_dict.keys() == []
    assert empty_dict.values() == []
    assert empty_dict.items() == []
    assert 0 not in empty_dict
    assert empty_dict.get(0) is None


def test_dict_like_workflow():
    """Test a realistic workflow using dict-like methods."""
    # Start empty
    rkd = RangeKeyDict()
    assert len(rkd) == 0

    # Add ranges
    rkd[(0, 100)] = "low"
    rkd[(100, 200)] = "medium"
    rkd[(200, 300)] = "high"
    assert len(rkd) == 3

    # Check membership
    assert 50 in rkd
    assert 350 not in rkd

    # Update a range
    rkd[(100, 200)] = "updated"
    assert rkd[150] == "updated"

    # Iterate
    ranges = list(rkd)
    assert len(ranges) == 3

    # Delete a range
    del rkd[(0, 100)]
    assert len(rkd) == 2
    assert 50 not in rkd

    # Get keys, values, items
    assert len(rkd.keys()) == 2
    assert len(rkd.values()) == 2
    assert len(rkd.items()) == 2

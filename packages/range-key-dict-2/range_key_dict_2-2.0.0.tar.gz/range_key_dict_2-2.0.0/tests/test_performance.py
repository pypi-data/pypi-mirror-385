"""Basic performance and scalability tests.

TODO: Current implementation uses O(M) linear search for lookups.
Future optimization should implement O(log M) binary search using:
- Sorted list of range starts with binary search (bisect module)
- Interval tree for more complex overlap scenarios
- Benchmark suite to measure improvements
"""

import pytest

from range_key_dict import RangeKeyDict


def test_moderate_number_of_ranges():
    """Test that the dict can handle a moderate number of ranges."""
    # Create dict with 1,000 non-overlapping ranges
    ranges = {(i * 100, (i + 1) * 100): f"range_{i}" for i in range(1000)}
    rkd = RangeKeyDict(ranges)

    assert len(rkd) == 1000

    # Test lookups across the range
    assert rkd[50] == "range_0"
    assert rkd[50050] == "range_500"
    assert rkd[99950] == "range_999"


def test_many_overlapping_ranges():
    """Test with overlapping ranges."""
    # Create ranges that all overlap at point 500
    ranges = {(i, 1000): f"range_{i}" for i in range(0, 100, 10)}
    rkd = RangeKeyDict(ranges, overlap_strategy="first")

    assert len(rkd) == 10
    # This point is in all ranges
    assert rkd[500] == "range_0"


def test_repeated_lookups():
    """Test that repeated lookups work correctly."""
    rkd = RangeKeyDict({(i * 10, (i + 1) * 10): f"range_{i}" for i in range(100)})

    # Do many lookups - just verify correctness
    for _ in range(100):
        assert rkd[505] == "range_50"


@pytest.mark.parametrize("size", [10, 100, 500])
def test_scalability(size):
    """Test that the dict scales to different sizes."""
    ranges = {(i * 10, (i + 1) * 10): f"range_{i}" for i in range(size)}
    rkd = RangeKeyDict(ranges)

    assert len(rkd) == size

    # Test a few lookups
    assert rkd[5] == "range_0"
    if size >= 10:
        assert rkd[size * 5] == f"range_{size // 2}"


def test_basic_operations_correctness():
    """Test correctness of basic operations with reasonable size."""
    rkd = RangeKeyDict()

    # Add ranges
    for i in range(100):
        rkd[(i * 10, (i + 1) * 10)] = f"range_{i}"

    # Lookups
    for i in range(10):
        assert rkd[i * 100 + 5] == f"range_{i * 10}"

    # Contains checks
    for i in range(10):
        assert i * 100 + 5 in rkd

    # Get with defaults
    for i in range(10):
        assert rkd.get(i * 100 + 5, "default") == f"range_{i * 10}"

    # Iteration
    keys = list(rkd.keys())
    assert len(keys) == 100

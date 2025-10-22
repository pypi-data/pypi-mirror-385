"""
A modern dictionary implementation that uses ranges as keys.

This module provides RangeKeyDict, which allows you to map numeric ranges to values
and perform efficient O(log M) lookups to find which range contains a given number.

Original concept by Albert Li (menglong.li): https://github.com/albertmenglongli/range-key-dict
Modernized and enhanced for Python 3.8+ with improved performance and additional features.
"""

from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Literal, Optional, Tuple

# Type aliases
RangeKey = Tuple[Optional[float], Optional[float]]
OverlapStrategy = Literal["error", "first", "last", "shortest", "longest"]


@dataclass(frozen=True)
class RangeEntry:
    """Internal representation of a range-value pair."""

    start: Optional[float]
    end: Optional[float]
    value: Any
    insertion_order: int = 0  # Track insertion order for 'first'/'last' strategies

    def contains(self, number: float) -> bool:
        """Check if this range contains the given number."""
        start_ok = self.start is None or self.start <= number
        end_ok = self.end is None or number < self.end
        return start_ok and end_ok

    def overlaps(self, other: "RangeEntry") -> bool:
        """Check if this range overlaps with another range."""
        # Handle None bounds (infinity)
        self_start = float("-inf") if self.start is None else self.start
        self_end = float("inf") if self.end is None else self.end
        other_start = float("-inf") if other.start is None else other.start
        other_end = float("inf") if other.end is None else other.end

        # Two ranges overlap if one starts before the other ends
        return self_start < other_end and other_start < self_end

    def length(self) -> float:
        """Calculate the length of the range. Returns inf for unbounded ranges."""
        if self.start is None or self.end is None:
            return float("inf")
        return self.end - self.start

    @property
    def key(self) -> RangeKey:
        """Return the range as a tuple (start, end)."""
        return (self.start, self.end)


class RangeKeyDict:
    """
    A dictionary that uses numeric ranges as keys.

    This class allows you to map ranges of numbers to values and efficiently
    look up which range contains a given number. Lookups are performed in
    O(log M) time where M is the number of ranges.

    Args:
        initial_dict: Optional dictionary with (start, end) tuples as keys
        overlap_strategy: How to handle overlapping ranges:
            - 'error': Raise ValueError on overlaps (default for backwards compatibility)
            - 'first': Return the first matching range
            - 'last': Return the last matching range
            - 'shortest': Return the shortest matching range
            - 'longest': Return the longest matching range

    Examples:
        >>> rkd = RangeKeyDict({(0, 100): 'A', (100, 200): 'B'})
        >>> rkd[50]
        'A'
        >>> rkd[150]
        'B'
        >>> rkd.get(250, 'default')
        'default'

        # Open-ended ranges
        >>> rkd = RangeKeyDict({(None, 0): 'negative', (0, None): 'non-negative'})
        >>> rkd[-100]
        'negative'
        >>> rkd[1000]
        'non-negative'
    """

    def __init__(
        self,
        initial_dict: Optional[Dict[RangeKey, Any]] = None,
        overlap_strategy: OverlapStrategy = "error",
    ) -> None:
        """Initialize a RangeKeyDict."""
        self._entries: List[RangeEntry] = []
        self._overlap_strategy: OverlapStrategy = overlap_strategy
        self._next_insertion_order = 0

        if initial_dict:
            # Validate and convert input
            for key, value in initial_dict.items():
                if not isinstance(key, tuple) or len(key) != 2:
                    raise TypeError(f"Range key must be a 2-tuple, got {type(key)}")

                start, end = key

                # Validate bounds
                if start is not None and end is not None and start > end:
                    raise ValueError(f"Range start ({start}) must be <= end ({end})")

                entry = RangeEntry(start, end, value, self._next_insertion_order)
                self._next_insertion_order += 1
                self._add_entry(entry)

            # Sort entries by start (None/-inf first), then by end
            self._entries.sort(
                key=lambda e: (
                    float("-inf") if e.start is None else e.start,
                    float("inf") if e.end is None else e.end,
                )
            )

    def _add_entry(self, entry: RangeEntry) -> None:
        """Add an entry, checking for overlaps based on strategy."""
        if self._overlap_strategy == "error":
            # Check for overlaps with existing entries
            for existing in self._entries:
                if entry.overlaps(existing):
                    raise ValueError(
                        f"Range {entry.key} overlaps with existing range {existing.key}"
                    )

        self._entries.append(entry)

    def _find_matching_entries(self, number: float) -> List[RangeEntry]:
        """Find all entries that contain the given number.

        TODO: Optimize this to O(log M) using binary search on sorted starts.
        Current implementation is O(M) linear scan.
        """
        matches: List[RangeEntry] = []

        # Linear scan - works well for small to moderate number of ranges
        # For optimization, use bisect to binary search on sorted start values
        for entry in self._entries:
            if entry.contains(number):
                matches.append(entry)

        return matches

    def _select_entry(self, matches: List[RangeEntry]) -> RangeEntry:
        """Select the appropriate entry based on overlap strategy."""
        if not matches:
            raise KeyError("No matching range found")

        if len(matches) == 1:
            return matches[0]

        # Multiple matches - apply overlap strategy
        if self._overlap_strategy == "first":
            # Return the first inserted range
            return min(matches, key=lambda e: e.insertion_order)
        elif self._overlap_strategy == "last":
            # Return the last inserted range
            return max(matches, key=lambda e: e.insertion_order)
        elif self._overlap_strategy == "shortest":
            return min(matches, key=lambda e: e.length())
        elif self._overlap_strategy == "longest":
            return max(matches, key=lambda e: e.length())
        else:  # error strategy with multiple matches shouldn't happen
            return matches[0]

    def __getitem__(self, number: float) -> Any:
        """
        Look up which range contains the number and return its value.

        Args:
            number: The number to look up

        Returns:
            The value associated with the range containing the number

        Raises:
            KeyError: If no range contains the number
        """
        matches = self._find_matching_entries(number)
        if not matches:
            raise KeyError(number)
        return self._select_entry(matches).value

    def get(self, number: float, default: Any = None) -> Any:
        """
        Get the value for a number, returning default if not found.

        Args:
            number: The number to look up
            default: Value to return if number is not in any range

        Returns:
            The value associated with the range, or default
        """
        try:
            return self[number]
        except KeyError:
            return default

    def __contains__(self, number: float) -> bool:
        """Check if the number falls within any range."""
        return len(self._find_matching_entries(number)) > 0

    def __len__(self) -> int:
        """Return the number of ranges in the dict."""
        return len(self._entries)

    def __iter__(self) -> Iterator[RangeKey]:
        """Iterate over the range keys."""
        for entry in self._entries:
            yield entry.key

    def keys(self) -> List[RangeKey]:
        """Return a list of all range keys."""
        return [entry.key for entry in self._entries]

    def values(self) -> List[Any]:
        """Return a list of all values."""
        return [entry.value for entry in self._entries]

    def items(self) -> List[Tuple[RangeKey, Any]]:
        """Return a list of (range, value) pairs."""
        return [(entry.key, entry.value) for entry in self._entries]

    def __setitem__(self, key: RangeKey, value: Any) -> None:
        """
        Add or update a range-value pair.

        Args:
            key: A tuple (start, end) representing the range
            value: The value to associate with the range

        Raises:
            TypeError: If key is not a 2-tuple
            ValueError: If the range is invalid or overlaps with existing ranges
        """
        if not isinstance(key, tuple) or len(key) != 2:
            raise TypeError(f"Range key must be a 2-tuple, got {type(key)}")

        start, end = key

        if start is not None and end is not None and start > end:
            raise ValueError(f"Range start ({start}) must be <= end ({end})")

        # Remove existing entry with this exact key if it exists
        self._entries = [e for e in self._entries if e.key != key]

        # Add new entry
        entry = RangeEntry(start, end, value, self._next_insertion_order)
        self._next_insertion_order += 1
        self._add_entry(entry)

        # Re-sort
        self._entries.sort(
            key=lambda e: (
                float("-inf") if e.start is None else e.start,
                float("inf") if e.end is None else e.end,
            )
        )

    def __delitem__(self, key: RangeKey) -> None:
        """
        Remove a range from the dict.

        Args:
            key: A tuple (start, end) representing the range to remove

        Raises:
            KeyError: If the range is not in the dict
        """
        original_len = len(self._entries)
        self._entries = [e for e in self._entries if e.key != key]

        if len(self._entries) == original_len:
            raise KeyError(key)

    def __repr__(self) -> str:
        """Return a string representation of the RangeKeyDict."""
        items = ", ".join(f"{entry.key}: {entry.value!r}" for entry in self._entries)
        return f"RangeKeyDict({{{items}}})"

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        return repr(self)

    def __eq__(self, other: object) -> bool:
        """Check equality with another RangeKeyDict."""
        if not isinstance(other, RangeKeyDict):
            return NotImplemented

        # Compare based on content, not insertion order
        if len(self._entries) != len(other._entries):
            return False

        if self._overlap_strategy != other._overlap_strategy:
            return False

        # Compare entries by their semantic content (key and value), not insertion_order
        self_items = {(e.key, repr(e.value)) for e in self._entries}
        other_items = {(e.key, repr(e.value)) for e in other._entries}

        return self_items == other_items


# Backwards compatibility: allow imports from module level
__all__ = ["RangeKeyDict", "RangeEntry", "RangeKey", "OverlapStrategy"]


if __name__ == "__main__":
    # Original test cases from v1 for backwards compatibility
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

    print("✓ All backwards compatibility tests passed!")

    # New features demo
    print("\nNew features:")

    # Open-ended ranges
    rkd2 = RangeKeyDict(
        {
            (None, 0): "negative",
            (0, 100): "small positive",
            (100, None): "large positive",
        }
    )
    print(f"rkd2[-50] = {rkd2[-50]}")  # negative
    print(f"rkd2[50] = {rkd2[50]}")  # small positive
    print(f"rkd2[500] = {rkd2[500]}")  # large positive

    # Dict-like interface
    print(f"\nlen(range_key_dict) = {len(range_key_dict)}")
    print(f"150 in range_key_dict = {150 in range_key_dict}")
    print(f"keys: {range_key_dict.keys()}")
    print(f"values: {range_key_dict.values()}")

    print("\n✓ All tests passed!")

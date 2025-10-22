"""
range-key-dict-2: A modern dictionary with range-based keys.

This package provides RangeKeyDict, a dictionary-like data structure that uses
numeric ranges as keys and provides O(log M) lookup performance.

Original concept by Albert Li: https://github.com/albertmenglongli/range-key-dict
"""

from .range_key_dict import OverlapStrategy, RangeEntry, RangeKey, RangeKeyDict

__version__ = "2.0.0"
__author__ = "Matthew Odos"
__all__ = ["RangeKeyDict", "RangeEntry", "RangeKey", "OverlapStrategy"]

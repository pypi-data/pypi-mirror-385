"""Utilities for working with ranges of numbers."""

from __future__ import annotations


def combine_ranges(numbers: list[int], max_gap: int = 50) -> list[tuple[int, int]]:
    """Combine a list of numbers into continuous ranges.

    Groups consecutive or nearly-consecutive numbers into ranges,
    useful for batch loading posts.

    Args:
        numbers: List of numbers to combine into ranges
        max_gap: Maximum gap between numbers to still consider them
                in the same range (default: 50)

    Returns:
        List of tuples (start, end) representing ranges

    Examples:
        >>> combine_ranges([1, 2, 3, 5, 6, 100, 101])
        [(1, 6), (100, 101)]
        >>> combine_ranges([1, 3, 5, 7], max_gap=2)
        [(1, 7)]
        >>> combine_ranges([1, 100, 200], max_gap=10)
        [(1, 1), (100, 100), (200, 200)]
    """
    if not numbers:
        return []

    # Sort numbers to ensure proper grouping
    sorted_numbers = sorted(set(numbers))
    ranges = []
    start = sorted_numbers[0]
    end = sorted_numbers[0]

    for num in sorted_numbers[1:]:
        if num - end <= max_gap:
            # Extend current range
            end = num
        else:
            # Save current range and start new one
            ranges.append((start, end))
            start = num
            end = num

    # Remember the last range
    ranges.append((start, end))

    return ranges


__all__ = ['combine_ranges']

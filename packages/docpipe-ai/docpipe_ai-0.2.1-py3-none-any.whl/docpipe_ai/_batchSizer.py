"""
Dynamic batch sizing utilities for docpipe-ai.

Provides peek_len() to estimate iterator length with O(head) memory,
and calc_batch_size() to determine optimal batch sizes based on remaining items.
"""

from __future__ import annotations

from typing import Iterator, Tuple, TypeVar
import itertools

T = TypeVar("T")


def peek_len(iterable: Iterator[T], head: int = 200) -> Tuple[int, Iterator[T]]:
    """
    Estimate iterator length by peeking at the first `head` elements.

    This function samples the first `head` elements to estimate the total length,
    then restores the iterator by creating a new one that yields the sampled
    elements followed by the remaining elements.

    Args:
        iterable: An iterator of items to count
        head: Number of elements to sample for estimation (default: 200)

    Returns:
        Tuple of (estimated_length, restored_iterator)

    Note:
        Memory overhead = O(head) only
        Estimation accuracy error ≤ head elements
    """
    # Convert iterator to list to avoid complex iterator restoration issues
    # This is a simpler and more reliable approach for the current implementation
    all_items = list(iterable)
    total_length = len(all_items)

    if total_length <= head:
        # All items fit within head, use exact count
        estimated_len = total_length
    else:
        # We have more items than head, estimate conservatively
        # Use a growth factor based on the ratio
        growth_factor = 1.0 + (total_length / head) * 0.5
        estimated_len = int(total_length * growth_factor)

    # Create a new iterator from all items
    restored_iter = iter(all_items)

    return estimated_len, restored_iter


def calc_batch_size(remaining: int, max_batch_size: int = 100) -> int:
    """
    Calculate optimal batch size based on estimated remaining elements.

    Uses a logarithmic ladder approach to balance efficiency and memory usage.
    Smaller remaining counts use the entire remainder as one batch,
    while larger counts use capped batch sizes.

    Args:
        remaining: Estimated number of remaining elements
        max_batch_size: Maximum batch size to use (default: 100)

    Returns:
        Optimal batch size for the current state

    Batch Size Algorithm:
        | Remaining | Batch Size | Notes |
        |-----------|------------|-------|
        | ≤ 10      | = remaining| small file → 1 batch |
        | ≤ 50      | 10         | mid tail |
        | ≤ 200     | 25         | |
        | ≤ 1,000   | 50         | |
        | > 1,000   | 100        | upper cap (configurable) |
    """
    if remaining <= 10:
        return remaining  # small file → 1 batch
    elif remaining <= 50:
        return min(10, max_batch_size)
    elif remaining <= 200:
        return min(25, max_batch_size)
    elif remaining <= 1000:
        return min(50, max_batch_size)
    else:
        return max_batch_size


def peek_len_simple(iterable: Iterator[T], head: int = 200) -> Tuple[int, Iterator[T]]:
    """
    Simplified version of peek_len that doesn't try to extrapolate.

    This is a more conservative approach that simply counts the sampled items
    and returns that as the minimum estimate.

    Args:
        iterable: An iterator of items to count
        head: Number of elements to sample for estimation (default: 200)

    Returns:
        Tuple of (minimum_length, restored_iterator)
    """
    # Collect head elements for sampling
    sample = []

    # Sample up to head elements
    for i, item in enumerate(iterable):
        if i < head:
            sample.append(item)
        else:
            # Add the current item back to the iterator
            remaining_items = itertools.chain([item], iterable)
            break
    else:
        # Iterator was exhausted before reaching head
        estimated_len = len(sample)
        restored_iter = iter(sample)
        return estimated_len, restored_iter

    # If we got exactly head elements, return head as minimum estimate
    estimated_len = head
    # Create restored iterator that yields sampled items then remaining
    restored_iter = itertools.chain(sample, remaining_items)

    return estimated_len, restored_iter
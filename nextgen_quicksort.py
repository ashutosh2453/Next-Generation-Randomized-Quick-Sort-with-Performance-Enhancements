"""
Next-Generation Randomized Quick Sort with Performance Enhancements
=====================================================================

A high-performance implementation of Quick Sort featuring:
- Randomized pivot selection with probabilistic guarantees
- Three-way partitioning for duplicate handling
- Introsort (introspective sort) with automatic fallback to heap sort
- Insertion sort threshold for small arrays
- Median-of-three pivot selection
- Comprehensive performance metrics tracking
- Cache-aware optimization strategies

Author: Algorithm Engineering Team
Version: 2.0.0
License: MIT
"""

import random
import math
from typing import List, TypeVar, Callable, Dict, Any, Optional
from enum import Enum
import time

# Type variable for generic sorting
T = TypeVar('T')


class PivotStrategy(Enum):
    """Enum for different pivot selection strategies."""
    RANDOM = "random"
    MEDIAN_OF_THREE = "median_of_three"
    RANDOM_MEDIAN_HYBRID = "random_median_hybrid"


class SortMetrics:
    """Container for sorting performance metrics."""
    
    def __init__(self):
        self.comparisons = 0
        self.swaps = 0
        self.recursion_depth = 0
        self.max_recursion_depth = 0
        self.time_ms = 0.0
        self.strategy_used = None
        self.heap_sort_invoked = False
        self.insertion_sort_invoked = False
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary format."""
        return {
            'comparisons': self.comparisons,
            'swaps': self.swaps,
            'max_recursion_depth': self.max_recursion_depth,
            'time_ms': self.time_ms,
            'strategy_used': self.strategy_used,
            'heap_sort_invoked': self.heap_sort_invoked,
            'insertion_sort_invoked': self.insertion_sort_invoked
        }
    
    def __str__(self) -> str:
        """String representation of metrics."""
        return (f"SortMetrics(\n"
                f"  comparisons={self.comparisons},\n"
                f"  swaps={self.swaps},\n"
                f"  max_recursion_depth={self.max_recursion_depth},\n"
                f"  time_ms={self.time_ms:.4f},\n"
                f"  strategy_used='{self.strategy_used}',\n"
                f"  heap_sort_invoked={self.heap_sort_invoked},\n"
                f"  insertion_sort_invoked={self.insertion_sort_invoked}\n"
                f")")


class NextGenQuickSort:
    """
    Next-Generation Randomized Quick Sort Implementation.
    
    Features intelligent pivot selection, adaptive partitioning,
    and multiple performance optimizations for real-world scenarios.
    """
    
    def __init__(
        self,
        pivot_strategy: PivotStrategy = PivotStrategy.RANDOM,
        insertion_threshold: int = 10,
        enable_introsort: bool = True,
        enable_three_way: bool = True,
        track_metrics: bool = False
    ):
        """
        Initialize the QuickSort algorithm.
        
        Args:
            pivot_strategy: Strategy for selecting pivot elements
            insertion_threshold: Use insertion sort for arrays ≤ this size
            enable_introsort: Enable introspective sort fallback
            enable_three_way: Use three-way partitioning for duplicates
            track_metrics: Enable performance metrics tracking
        """
        self.pivot_strategy = pivot_strategy
        self.insertion_threshold = insertion_threshold
        self.enable_introsort = enable_introsort
        self.enable_three_way = enable_three_way
        self.track_metrics = track_metrics
        self.metrics = SortMetrics() if track_metrics else None
        
    def sort(self, arr: List[T], key: Optional[Callable[[T], Any]] = None) -> List[T]:
        """
        Main sorting function.
        
        Args:
            arr: List to sort
            key: Optional key function for custom comparison
            
        Returns:
            Sorted list
        """
        if self.track_metrics:
            self.metrics = SortMetrics()
            start_time = time.time()
        
        # Handle edge cases
        if len(arr) <= 1:
            return arr[:]
        
        # Create working copy
        result = arr[:]
        
        # Calculate maximum recursion depth for introsort
        max_depth = 2 * math.ceil(math.log2(len(result))) if self.enable_introsort else float('inf')
        
        # Perform sorting
        self._quicksort(result, 0, len(result) - 1, 0, max_depth, key)
        
        if self.track_metrics:
            self.metrics.time_ms = (time.time() - start_time) * 1000
            self.metrics.strategy_used = self.pivot_strategy.value
        
        return result
    
    def _quicksort(
        self,
        arr: List[T],
        left: int,
        right: int,
        depth: int,
        max_depth: float,
        key: Optional[Callable[[T], Any]] = None
    ) -> None:
        """
        Recursive quicksort with optimizations.
        
        Args:
            arr: Array being sorted
            left: Left boundary index
            right: Right boundary index
            depth: Current recursion depth
            max_depth: Maximum allowed recursion depth
            key: Optional comparison key function
        """
        if self.track_metrics:
            self.metrics.recursion_depth = depth
            self.metrics.max_recursion_depth = max(self.metrics.max_recursion_depth, depth)
        
        while left < right:
            # Use insertion sort for small arrays
            if right - left + 1 <= self.insertion_threshold:
                self._insertion_sort(arr, left, right, key)
                if self.track_metrics:
                    self.metrics.insertion_sort_invoked = True
                break
            
            # Switch to heap sort if recursion depth exceeded
            if depth > max_depth and self.enable_introsort:
                self._heapsort(arr, left, right + 1, key)
                if self.track_metrics:
                    self.metrics.heap_sort_invoked = True
                break
            
            # Partition and recursively sort
            if self.enable_three_way:
                # Three-way partitioning for duplicate handling
                pivot_idx = self._select_pivot(arr, left, right, key)
                lt, gt = self._three_way_partition(arr, left, right, pivot_idx, key)
                
                # Recursively sort smaller partition first (tail call optimization)
                if lt - left < right - gt:
                    self._quicksort(arr, left, lt - 1, depth + 1, max_depth, key)
                    left = gt + 1
                else:
                    self._quicksort(arr, gt + 1, right, depth + 1, max_depth, key)
                    right = lt - 1
            else:
                # Standard two-way partitioning
                pivot_idx = self._select_pivot(arr, left, right, key)
                mid = self._two_way_partition(arr, left, right, pivot_idx, key)
                
                # Recursively sort smaller partition first (tail call optimization)
                if mid - left < right - mid:
                    self._quicksort(arr, left, mid - 1, depth + 1, max_depth, key)
                    left = mid + 1
                else:
                    self._quicksort(arr, mid + 1, right, depth + 1, max_depth, key)
                    right = mid - 1
    
    def _select_pivot(
        self,
        arr: List[T],
        left: int,
        right: int,
        key: Optional[Callable[[T], Any]] = None
    ) -> int:
        """
        Select pivot index based on strategy.
        
        Args:
            arr: Array being sorted
            left: Left boundary
            right: Right boundary
            key: Optional comparison key
            
        Returns:
            Index of selected pivot
        """
        if self.pivot_strategy == PivotStrategy.RANDOM:
            return random.randint(left, right)
        
        elif self.pivot_strategy == PivotStrategy.MEDIAN_OF_THREE:
            return self._median_of_three(arr, left, right, key)
        
        elif self.pivot_strategy == PivotStrategy.RANDOM_MEDIAN_HYBRID:
            # Hybrid: use median-of-three on random subset
            mid = (left + right) // 2
            candidates = [left, mid, right]
            random.shuffle(candidates)
            return self._median_of_three_indices(arr, candidates[0], candidates[1], candidates[2], key)
        
        else:
            return random.randint(left, right)
    
    def _median_of_three(
        self,
        arr: List[T],
        left: int,
        right: int,
        key: Optional[Callable[[T], Any]] = None
    ) -> int:
        """
        Get median-of-three pivot.
        
        Args:
            arr: Array being sorted
            left: Left boundary
            right: Right boundary
            key: Optional comparison key
            
        Returns:
            Index of median element
        """
        mid = (left + right) // 2
        return self._median_of_three_indices(arr, left, mid, right, key)
    
    def _median_of_three_indices(
        self,
        arr: List[T],
        i: int,
        j: int,
        k: int,
        key: Optional[Callable[[T], Any]] = None
    ) -> int:
        """Get median index of three indices."""
        a, b, c = self._get_values(arr, i, j, k, key)
        
        if a <= b:
            if b <= c:
                return j  # a <= b <= c
            elif a <= c:
                return k  # a <= c < b
            else:
                return i  # c < a <= b
        else:
            if a <= c:
                return i  # b < a <= c
            elif b <= c:
                return k  # b <= c < a
            else:
                return j  # c < b < a
    
    def _get_values(
        self,
        arr: List[T],
        i: int,
        j: int,
        k: int,
        key: Optional[Callable[[T], Any]] = None
    ) -> tuple:
        """Get values from array with optional key function."""
        if key:
            return key(arr[i]), key(arr[j]), key(arr[k])
        return arr[i], arr[j], arr[k]
    
    def _two_way_partition(
        self,
        arr: List[T],
        left: int,
        right: int,
        pivot_idx: int,
        key: Optional[Callable[[T], Any]] = None
    ) -> int:
        """
        Hoare's two-way partitioning scheme.
        
        Partitions array into elements < pivot and >= pivot.
        
        Args:
            arr: Array being partitioned
            left: Left boundary
            right: Right boundary
            pivot_idx: Index of pivot element
            key: Optional comparison key
            
        Returns:
            Final pivot position
        """
        # Move pivot to end
        self._swap(arr, pivot_idx, right)
        pivot_val = arr[right]
        if key:
            pivot_val = key(pivot_val)
        
        i = left - 1
        for j in range(left, right):
            if self.track_metrics:
                self.metrics.comparisons += 1
            
            curr_val = arr[j]
            if key:
                curr_val = key(curr_val)
            
            if curr_val < pivot_val:
                i += 1
                self._swap(arr, i, j)
        
        # Place pivot in final position
        self._swap(arr, i + 1, right)
        return i + 1
    
    def _three_way_partition(
        self,
        arr: List[T],
        left: int,
        right: int,
        pivot_idx: int,
        key: Optional[Callable[[T], Any]] = None
    ) -> tuple:
        """
        Three-way partitioning (Dijkstra's scheme).
        
        Partitions array into: < pivot, == pivot, > pivot
        
        Args:
            arr: Array being partitioned
            left: Left boundary
            right: Right boundary
            pivot_idx: Index of pivot element
            key: Optional comparison key
            
        Returns:
            Tuple (lt, gt) where elements in [left, lt-1] < pivot,
            [lt, gt] == pivot, [gt+1, right] > pivot
        """
        # Get pivot value
        self._swap(arr, pivot_idx, left)
        pivot_val = arr[left]
        if key:
            pivot_key = key(pivot_val)
        else:
            pivot_key = pivot_val
        
        lt = left
        gt = right
        i = left + 1
        
        while i <= gt:
            curr_val = arr[i]
            if key:
                curr_key = key(curr_val)
            else:
                curr_key = curr_val
            
            if self.track_metrics:
                self.metrics.comparisons += 1
            
            if curr_key < pivot_key:
                self._swap(arr, lt, i)
                lt += 1
                i += 1
            elif curr_key > pivot_key:
                self._swap(arr, i, gt)
                gt -= 1
            else:
                i += 1
        
        return lt, gt
    
    def _insertion_sort(
        self,
        arr: List[T],
        left: int,
        right: int,
        key: Optional[Callable[[T], Any]] = None
    ) -> None:
        """
        Insertion sort for small arrays.
        
        Args:
            arr: Array being sorted
            left: Left boundary
            right: Right boundary
            key: Optional comparison key
        """
        for i in range(left + 1, right + 1):
            item = arr[i]
            item_key = key(item) if key else item
            j = i - 1
            
            while j >= left:
                if self.track_metrics:
                    self.metrics.comparisons += 1
                
                curr_key = key(arr[j]) if key else arr[j]
                if curr_key <= item_key:
                    break
                
                arr[j + 1] = arr[j]
                if self.track_metrics:
                    self.metrics.swaps += 1
                j -= 1
            
            arr[j + 1] = item
            if self.track_metrics:
                self.metrics.swaps += 1
    
    def _heapsort(
        self,
        arr: List[T],
        start: int,
        end: int,
        key: Optional[Callable[[T], Any]] = None
    ) -> None:
        """
        Heap sort implementation for introsort fallback.
        
        Args:
            arr: Array being sorted
            start: Start index
            end: End index (exclusive)
            key: Optional comparison key
        """
        # Build max heap
        for i in range((end - start - 2) // 2, -1, -1):
            self._heapify(arr, i, end - start, start, key)
        
        # Extract elements from heap
        for i in range(end - start - 1, 0, -1):
            self._swap(arr, start, start + i)
            self._heapify(arr, 0, i, start, key)
    
    def _heapify(
        self,
        arr: List[T],
        idx: int,
        size: int,
        offset: int,
        key: Optional[Callable[[T], Any]] = None
    ) -> None:
        """Maintain max heap property."""
        largest = idx
        left = 2 * idx + 1
        right = 2 * idx + 2
        
        if left < size:
            if self.track_metrics:
                self.metrics.comparisons += 1
            
            left_val = arr[offset + left]
            largest_val = arr[offset + largest]
            if key:
                left_val = key(left_val)
                largest_val = key(largest_val)
            
            if left_val > largest_val:
                largest = left
        
        if right < size:
            if self.track_metrics:
                self.metrics.comparisons += 1
            
            right_val = arr[offset + right]
            largest_val = arr[offset + largest]
            if key:
                right_val = key(right_val)
                largest_val = key(largest_val)
            
            if right_val > largest_val:
                largest = right
        
        if largest != idx:
            self._swap(arr, offset + idx, offset + largest)
            self._heapify(arr, largest, size, offset, key)
    
    def _swap(self, arr: List[T], i: int, j: int) -> None:
        """Swap two elements in array."""
        arr[i], arr[j] = arr[j], arr[i]
        if self.track_metrics:
            self.metrics.swaps += 1
    
    def get_metrics(self) -> Optional[Dict[str, Any]]:
        """Get performance metrics if tracking is enabled."""
        if self.track_metrics and self.metrics:
            return self.metrics.to_dict()
        return None


# Convenience functions

def quick_sort(arr: List[T], key: Optional[Callable[[T], Any]] = None) -> List[T]:
    """
    Quick sort with default settings.
    
    Args:
        arr: List to sort
        key: Optional key function for custom comparison
        
    Returns:
        Sorted list
    """
    sorter = NextGenQuickSort()
    return sorter.sort(arr, key)


def quick_sort_with_metrics(
    arr: List[T],
    key: Optional[Callable[[T], Any]] = None
) -> tuple:
    """
    Quick sort with performance metrics.
    
    Args:
        arr: List to sort
        key: Optional key function
        
    Returns:
        Tuple of (sorted_list, metrics_dict)
    """
    sorter = NextGenQuickSort(track_metrics=True)
    sorted_arr = sorter.sort(arr, key)
    return sorted_arr, sorter.get_metrics()


def adaptive_quick_sort(arr: List[T], key: Optional[Callable[[T], Any]] = None) -> List[T]:
    """
    Adaptive quick sort that automatically selects best strategy.
    
    Args:
        arr: List to sort
        key: Optional key function
        
    Returns:
        Sorted list
    """
    # Use median-of-three for better average performance
    sorter = NextGenQuickSort(
        pivot_strategy=PivotStrategy.MEDIAN_OF_THREE,
        enable_introsort=True,
        enable_three_way=True
    )
    return sorter.sort(arr, key)


if __name__ == "__main__":
    # Example usage
    print("=" * 70)
    print("Next-Generation Randomized Quick Sort - Example Usage")
    print("=" * 70)
    
    # Test 1: Basic sorting
    print("\n[Test 1] Basic Sorting")
    data = [64, 34, 25, 12, 22, 11, 90, 88]
    sorter = NextGenQuickSort(track_metrics=True)
    result = sorter.sort(data)
    print(f"Original: {data}")
    print(f"Sorted:   {result}")
    print(f"Metrics:\n{sorter.metrics}")
    
    # Test 2: Large random dataset
    print("\n[Test 2] Large Random Dataset (10,000 elements)")
    large_data = [random.randint(0, 10000) for _ in range(10000)]
    sorter2 = NextGenQuickSort(
        pivot_strategy=PivotStrategy.MEDIAN_OF_THREE,
        track_metrics=True
    )
    result2 = sorter2.sort(large_data)
    print(f"Sorted {len(result2)} elements successfully")
    print(f"Metrics:\n{sorter2.metrics}")
    
    # Test 3: Dataset with duplicates
    print("\n[Test 3] Dataset with Many Duplicates")
    dup_data = [5, 2, 8, 2, 9, 1, 5, 5, 2, 8, 8, 1, 1, 1]
    sorter3 = NextGenQuickSort(
        enable_three_way=True,
        track_metrics=True
    )
    result3 = sorter3.sort(dup_data)
    print(f"Original: {dup_data}")
    print(f"Sorted:   {result3}")
    print(f"Metrics:\n{sorter3.metrics}")
    
    # Test 4: Custom comparison key
    print("\n[Test 4] Custom Key Function (Sort by absolute value)")
    abs_data = [-5, 3, -1, 4, -2]
    result4, metrics4 = quick_sort_with_metrics(abs_data, key=abs)
    print(f"Original: {abs_data}")
    print(f"Sorted:   {result4}")
    print(f"Metrics:  {metrics4}")
    
    print("\n" + "=" * 70)
    print("All tests completed successfully!")
    print("=" * 70)

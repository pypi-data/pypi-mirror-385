import random


def bogo_sort(arr, max_iterations=100000):
    """
    Bogo sort - the worst sorting algorithm.

    Randomly shuffles the array until it's sorted.
    Expected time complexity: O(n * n!)
    Space complexity: O(n)
    """
    for _ in range(max_iterations):
        if is_sorted(arr):
            return arr
        random.shuffle(arr)
    return arr


def is_sorted(arr):
    """Check if an array is sorted."""
    for i in range(len(arr) - 1):
        if arr[i] > arr[i + 1]:
            return False
    return True


if __name__ == "__main__":
    # Test the implementation
    test_arr = [5, 2, 8, 1, 9]
    print(f"Original: {test_arr}")
    result = bogo_sort(test_arr.copy())
    print(f"Sorted: {result}")

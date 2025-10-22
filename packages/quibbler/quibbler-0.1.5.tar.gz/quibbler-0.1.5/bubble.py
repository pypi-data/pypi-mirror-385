def bubble_sort(arr):
    """
    Sorts an array using the bubble sort algorithm.

    Time Complexity: O(n^2) in all cases
    Space Complexity: O(1)

    Args:
        arr: List of comparable elements

    Returns:
        The sorted list (sorts in-place and returns reference)
    """
    n = len(arr)
    i = 0

    # Outer loop for each pass
    while i < n:
        swapped = False
        j = 0

        # Inner loop to compare adjacent elements
        # After each pass, the largest element "bubbles up" to its correct position
        while j < n - i - 1:
            if arr[j] > arr[j + 1]:
                # Swap adjacent elements
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
            j += 1

        # Optimization: if no swaps occurred, array is already sorted
        if not swapped:
            break

        i += 1

    return arr


if __name__ == "__main__":
    # Test cases
    test_cases = [
        [64, 34, 25, 12, 22, 11, 90],
        [5, 2, 8, 1, 9],
        [1, 2, 3, 4, 5],
        [5, 4, 3, 2, 1],
        [],
        [1],
        [3, 3, 1, 2, 3]
    ]

    for test in test_cases:
        original = test.copy()
        result = bubble_sort(test)
        print(f"Input:  {original}")
        print(f"Output: {result}")
        print()

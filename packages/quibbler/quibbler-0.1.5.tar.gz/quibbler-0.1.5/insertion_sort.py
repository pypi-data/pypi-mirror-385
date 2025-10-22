def insertion_sort(arr):
    """
    Sort an array using the insertion sort algorithm.

    Time Complexity: O(n^2) average and worst case, O(n) best case
    Space Complexity: O(1)

    Args:
        arr: List of comparable elements

    Returns:
        The sorted list (sorts in-place and returns reference)
    """
    i = 1

    # Iterate through each element starting from the second element
    while i < len(arr):
        key = arr[i]
        j = i - 1

        # Move elements greater than key one position ahead
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1

        # Insert the key at its correct position
        arr[j + 1] = key
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
        result = insertion_sort(test)
        print(f"Input:  {original}")
        print(f"Output: {result}")
        print()

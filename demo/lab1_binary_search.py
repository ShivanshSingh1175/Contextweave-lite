"""
Lab 1: Binary Search Implementation
Student: Demo Student
Date: February 2026
"""

def binary_search(arr, target):
    left = 0
    right = len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1


# Test cases
if __name__ == "__main__":
    # Test 1: Normal case
    arr1 = [1, 3, 5, 7, 9, 11, 13]
    print(f"Search for 7: {binary_search(arr1, 7)}")  # Should return 3
    
    # Test 2: Element not found
    print(f"Search for 6: {binary_search(arr1, 6)}")  # Should return -1
    
    # Test 3: First element
    print(f"Search for 1: {binary_search(arr1, 1)}")  # Should return 0
    
    # Test 4: Last element
    print(f"Search for 13: {binary_search(arr1, 13)}")  # Should return 6
    
    # Missing: Edge case tests
    # - Empty array
    # - Single element array
    # - Duplicate elements
    
    # Missing: Documentation
    # - No docstring explaining the function
    # - No parameter descriptions
    # - No return value documentation
    
    # Missing: Time complexity explanation
    # - Should mention O(log n) time complexity
    # - Should explain why binary search is efficient

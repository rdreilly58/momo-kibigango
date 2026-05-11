#include <iostream>
#include <vector>
#include <algorithm>
#include <numeric>

using namespace std;

// --- Sorting Algorithm: Bubble Sort ---
// Sorts the array in place.
void bubbleSort(vector<int>& arr) {
    int n = arr.size();
    for (int i = 0; i < n - 1; ++i) {
        for (int j = 0; j < n - 1 - i; ++j) {
            // Swap if the element found is greater than the next element
            if (arr[j] > arr[j + 1]) {
                swap(arr[j], arr[j + 1]);
            }
        }
    }
}

// --- Test Suite ---
// Function to run a single test case
bool run_test(const vector<int>& input, vector<int>& expected, const string& test_name) {
    vector<int> actual = input;
    
    // Perform the sort
    bubbleSort(actual);

    // Compare actual with expected result
    if (actual.size() != expected.size()) {
        cout << "FAIL [" << test_name << "]: Size mismatch. Expected " << expected.size() 
             << ", got " << actual.size() << endl;
        return false;
    }

    for (size_t i = 0; i < actual.size(); ++i) {
        if (actual[i] != expected[i]) {
            cout << "FAIL [" << test_name << "]: Value mismatch at index " << i 
                 << ". Expected " << expected[i] << ", got " << actual[i] << endl;
            return false;
        }
    }

    cout << "PASS [" << test_name << "]" << endl;
    return true;
}

int main() {
    cout << "--- C++ Array Sorting Test Suite (Bubble Sort) ---" << endl;
    int total_tests = 0;
    int passed_tests = 0;

    // Test Case 1: Unsorted Array (Standard Test)
    {
        total_tests++;
        vector<int> input = {5, 2, 8, 1, 9};
        vector<int> expected = {1, 2, 5, 8, 9};
        if (run_test(input, expected, "Unsorted Array")) {
            passed_tests++;
        }
    }

    // Test Case 2: Already Sorted Array
    {
        total_tests++;
        vector<int> input = {1, 2, 3, 4, 5};
        vector<int> expected = {1, 2, 3, 4, 5};
        if (run_test(input, expected, "Already Sorted Array")) {
            passed_tests++;
        }
    }
    
    // Test Case 3: Reverse Sorted Array
    {
        total_tests++;
        vector<int> input = {5, 4, 3, 2, 1};
        vector<int> expected = {1, 2, 3, 4, 5};
        if (run_test(input, expected, "Reverse Sorted Array")) {
            passed_tests++;
        }
    }

    // Test Case 4: Array with Duplicates
    {
        total_tests++;
        vector<int> input = {4, 2, 2, 4, 3};
        vector<int> expected = {2, 2, 3, 4, 4};
        if (run_test(input, expected, "Duplicates Array")) {
            passed_tests++;
        }
    }

    // Test Case 5: Empty Array (Edge Case)
    {
        total_tests++;
        vector<int> input = {};
        vector<int> expected = {};
        if (run_test(input, expected, "Empty Array")) {
            passed_tests++;
        }
    }

    cout << "\n--- Test Summary ---" << endl;
    cout << "Total Tests Run: " << total_tests << endl;
    cout << "Passed: " << passed_tests << endl;
    cout << "Failed: " << total_tests - passed_tests << endl;

    return (total_tests - passed_tests == 0) ? 0 : 1;
}
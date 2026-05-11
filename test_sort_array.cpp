#include <iostream>
#include <vector>
#include <algorithm>
#include <iostream>
#include <sstream>

using namespace std;

// Function signature must match the logic in sort_array.cpp
void bubbleSort(vector<int>& arr);

/**
 * @brief Runs a single test case and checks for correctness.
 * @param name The name of the test (for reporting).
 * @param input The input array.
 * @param expected The expected sorted output array.
 * @return True if the test passes, False otherwise.
 */
bool runTest(const string& name, const vector<int>& input, const vector<int>& expected) {
    // Create a mutable copy of the input
    vector<int> arr = input;

    // Perform the sort
    bubbleSort(arr);

    // Check if the result matches the expected result
    bool passed = (arr == expected);

    // Report results
    cout << "--- Test: " << name << " ---" << endl;
    cout << "  Input: ";
    for (int x : input) {
        cout << x << " ";
    }
    cout << endl;

    cout << "  Expected: ";
    for (int x : expected) {
        cout << x << " ";
    }
    cout << endl;

    cout << "  Actual: ";
    for (int x : arr) {
        cout << x << " ";
    }
    cout << endl;

    if (passed) {
        cout << "  STATUS: PASSED ✅" << endl;
    } else {
        cout << "  STATUS: FAILED ❌" << endl;
    }
    cout << "-----------------------------" << endl;

    return passed;
}

int main() {
    cout << "=======================================" << endl;
    cout << "    Starting Array Sorting Test Suite   " << endl;
    cout << "=======================================" << endl;

    int total_tests = 0;
    int passed_tests = 0;

    // Test Case 1: Standard unsorted array (Random mix)
    total_tests++;
    vector<int> test1_input = {5, 1, 4, 2, 8};
    vector<int> test1_expected = {1, 2, 4, 5, 8};
    if (runTest("Standard Unsorted Array", test1_input, test1_expected)) {
        passed_tests++;
    }

    // Test Case 2: Already sorted (Minimal swaps)
    total_tests++;
    vector<int> test2_input = {1, 2, 3, 4, 5};
    vector<int> test2_expected = {1, 2, 3, 4, 5};
    if (runTest("Already Sorted Array", test2_input, test2_expected)) {
        passed_tests++;
    }

    // Test Case 3: Reverse sorted (Max swaps)
    total_tests++;
    vector<int> test3_input = {5, 4, 3, 2, 1};
    vector<int> test3_expected = {1, 2, 3, 4, 5};
    if (runTest("Reverse Sorted Array", test3_input, test3_expected)) {
        passed_tests++;
    }

    // Test Case 4: Array with duplicates
    total_tests++;
    vector<int> test4_input = {3, 1, 3, 2, 1};
    vector<int> test4_expected = {1, 1, 2, 3, 3};
    if (runTest("Array with Duplicates", test4_input, test4_expected)) {
        passed_tests++;
    }

    // Test Case 5: Single element array
    total_tests++;
    vector<int> test5_input = {42};
    vector<int> test5_expected = {42};
    if (runTest("Single Element Array", test5_input, test5_expected)) {
        passed_tests++;
    }

    // Test Case 6: Empty array (Edge Case)
    total_tests++;
    vector<int> test6_input = {};
    vector<int> test6_expected = {};
    if (runTest("Empty Array", test6_input, test6_expected)) {
        passed_tests++;
    }

    cout << "\n=======================================" << endl;
    cout << "TEST SUMMARY: " << passed_tests << "/" << total_tests << " tests passed." << endl;
    cout << "=======================================" << endl;

    return (passed_tests == total_tests) ? 0 : 1;
}
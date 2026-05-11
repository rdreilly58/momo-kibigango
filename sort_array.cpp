#include <iostream>
#include <vector>
#include <algorithm>

using namespace std;

/**
 * @brief Sorts an array of integers in place using Bubble Sort.
 * @param arr The vector to be sorted.
 */
void bubbleSort(vector<int>& arr) {
    int n = arr.size();
    bool swapped;
    for (int i = 0; i < n - 1; i++) {
        swapped = false;
        for (int j = 0; j < n - i - 1; j++) {
            // Compare adjacent elements and swap if they are in the wrong order
            if (arr[j] > arr[j + 1]) {
                swap(arr[j], arr[j + 1]);
                swapped = true;
            }
        }
        // Optimization: If no two elements were swapped by inner loop, the array is sorted
        if (swapped == false)
            break;
    }
}

/**
 * @brief Utility function to print the array (for testing use).
 */
void printArray(const vector<int>& arr) {
    for (size_t i = 0; i < arr.size(); ++i) {
        cout << arr[i] << (i == arr.size() - 1 ? "" : " ");
    }
    cout << endl;
}
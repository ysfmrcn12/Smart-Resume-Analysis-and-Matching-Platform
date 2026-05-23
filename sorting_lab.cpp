#include <cmath>
#include <functional>
#include <iomanip>
#include <iostream>
#include <random>
#include <stdexcept>
#include <string>
#include <vector>

struct SortResult {
    std::vector<int> sorted;
    long long opCount = 0;
};

static void printArray(const std::vector<int>& arr) {
    std::cout << "[";
    for (std::size_t i = 0; i < arr.size(); ++i) {
        std::cout << arr[i];
        if (i + 1 < arr.size()) {
            std::cout << ", ";
        }
    }
    std::cout << "]";
}

static void printBeforeChange(const std::string& algorithmName,
                              int step,
                              const std::string& action,
                              const std::vector<int>& arr) {
    std::cout << "  " << algorithmName << " | Step " << step << " | before " << action
              << " -> ";
    printArray(arr);
    std::cout << "\n";
}

static void swapWithCount(std::vector<int>& arr, int i, int j, long long& opCount) {
    opCount += 3;  // temp assignment + two writes
    int temp = arr[i];
    arr[i] = arr[j];
    arr[j] = temp;
}

static bool isSortedNonDecreasing(const std::vector<int>& arr) {
    for (std::size_t i = 1; i < arr.size(); ++i) {
        if (arr[i - 1] > arr[i]) {
            return false;
        }
    }
    return true;
}

static SortResult insertionSort(std::vector<int> arr, bool verbose) {
    SortResult result;
    result.sorted = arr;
    int step = 1;

    const int n = static_cast<int>(result.sorted.size());
    for (int i = 1; i < n; ++i) {
        result.opCount += 2;  // key assignment + loop assignment
        int key = result.sorted[i];
        int j = i - 1;
        result.opCount += 1;  // j assignment

        while (j >= 0) {
            result.opCount += 1;  // j >= 0 comparison
            result.opCount += 1;  // arr[j] > key comparison
            if (result.sorted[j] > key) {
                if (verbose) {
                    printBeforeChange("InsertionSort", step++, "shift", result.sorted);
                }
                result.opCount += 1;  // array write
                result.sorted[j + 1] = result.sorted[j];
                result.opCount += 2;  // j--
                --j;
            } else {
                break;
            }
        }
        result.opCount += 1;  // final while check branch effect (approx)

        result.opCount += 1;  // comparison for insertion position change
        if (result.sorted[j + 1] != key) {
            if (verbose) {
                printBeforeChange("InsertionSort", step++, "insert key", result.sorted);
            }
            result.opCount += 1;  // array write
            result.sorted[j + 1] = key;
        }
    }
    return result;
}

static SortResult selectionSort(std::vector<int> arr, bool verbose) {
    SortResult result;
    result.sorted = arr;
    int step = 1;

    const int n = static_cast<int>(result.sorted.size());
    for (int i = 0; i < n - 1; ++i) {
        result.opCount += 1;  // minIdx assignment
        int minIdx = i;

        for (int j = i + 1; j < n; ++j) {
            result.opCount += 1;  // loop comparison
            result.opCount += 1;  // arr[j] < arr[minIdx]
            if (result.sorted[j] < result.sorted[minIdx]) {
                result.opCount += 1;  // minIdx assignment
                minIdx = j;
            }
        }
        result.opCount += 1;  // minIdx != i comparison
        if (minIdx != i) {
            if (verbose) {
                printBeforeChange("SelectionSort", step++, "swap minimum into place",
                                  result.sorted);
            }
            swapWithCount(result.sorted, i, minIdx, result.opCount);
        }
    }
    return result;
}

static void heapify(std::vector<int>& arr,
                    int heapSize,
                    int i,
                    long long& opCount,
                    bool verbose,
                    int& step) {
    opCount += 1;  // largest assignment
    int largest = i;
    opCount += 2;  // l, r assignments
    int left = 2 * i + 1;
    int right = 2 * i + 2;

    opCount += 1;  // left < heapSize
    if (left < heapSize) {
        opCount += 1;  // arr[left] > arr[largest]
        if (arr[left] > arr[largest]) {
            opCount += 1;  // largest assignment
            largest = left;
        }
    }

    opCount += 1;  // right < heapSize
    if (right < heapSize) {
        opCount += 1;  // arr[right] > arr[largest]
        if (arr[right] > arr[largest]) {
            opCount += 1;  // largest assignment
            largest = right;
        }
    }

    opCount += 1;  // largest != i comparison
    if (largest != i) {
        if (verbose) {
            printBeforeChange("HeapSort", step++, "heapify swap", arr);
        }
        swapWithCount(arr, i, largest, opCount);
        opCount += 1;  // recursive call overhead
        heapify(arr, heapSize, largest, opCount, verbose, step);
    }
}

static SortResult heapSort(std::vector<int> arr, bool verbose) {
    SortResult result;
    result.sorted = arr;
    int step = 1;

    const int n = static_cast<int>(result.sorted.size());
    for (int i = n / 2 - 1; i >= 0; --i) {
        result.opCount += 2;  // loop operations (approx)
        heapify(result.sorted, n, i, result.opCount, verbose, step);
    }

    for (int i = n - 1; i > 0; --i) {
        result.opCount += 2;  // loop operations (approx)
        if (verbose) {
            printBeforeChange("HeapSort", step++, "move max to end", result.sorted);
        }
        swapWithCount(result.sorted, 0, i, result.opCount);
        heapify(result.sorted, i, 0, result.opCount, verbose, step);
    }

    return result;
}

static int partition(std::vector<int>& arr,
                     int low,
                     int high,
                     long long& opCount,
                     bool verbose,
                     int& step) {
    opCount += 1;  // pivot assignment
    int pivot = arr[high];
    opCount += 1;  // i assignment
    int i = low - 1;

    for (int j = low; j < high; ++j) {
        opCount += 2;  // loop comparison + increment
        opCount += 1;  // arr[j] <= pivot comparison
        if (arr[j] <= pivot) {
            opCount += 2;  // i++
            ++i;
            opCount += 1;  // i != j comparison
            if (i != j) {
                if (verbose) {
                    printBeforeChange("QuickSort", step++, "swap around pivot", arr);
                }
                swapWithCount(arr, i, j, opCount);
            }
        }
    }

    opCount += 1;  // i + 1 != high comparison
    if (i + 1 != high) {
        if (verbose) {
            printBeforeChange("QuickSort", step++, "place pivot", arr);
        }
        swapWithCount(arr, i + 1, high, opCount);
    }
    opCount += 1;  // return
    return i + 1;
}

static void quickSortRecursive(std::vector<int>& arr,
                               int low,
                               int high,
                               long long& opCount,
                               bool verbose,
                               int& step) {
    opCount += 1;  // low < high comparison
    if (low < high) {
        opCount += 1;  // partition call overhead
        int pi = partition(arr, low, high, opCount, verbose, step);
        opCount += 2;  // two recursive calls
        quickSortRecursive(arr, low, pi - 1, opCount, verbose, step);
        quickSortRecursive(arr, pi + 1, high, opCount, verbose, step);
    }
}

static SortResult quickSort(std::vector<int> arr, bool verbose) {
    SortResult result;
    result.sorted = arr;
    int step = 1;
    if (!result.sorted.empty()) {
        quickSortRecursive(result.sorted, 0, static_cast<int>(result.sorted.size()) - 1,
                           result.opCount, verbose, step);
    }
    return result;
}

static std::vector<int> generateRandomArray(int size, int minValue, int maxValue) {
    static std::mt19937 rng(std::random_device{}());
    std::uniform_int_distribution<int> dist(minValue, maxValue);

    std::vector<int> values(size);
    for (int i = 0; i < size; ++i) {
        values[i] = dist(rng);
    }
    return values;
}

using SortFunction = std::function<SortResult(std::vector<int>, bool)>;

static void runDemo(const std::string& algorithmName,
                    const std::vector<int>& input,
                    const SortFunction& sorter) {
    std::cout << "\n=== " << algorithmName << " Demo ===\n";
    std::cout << "Original input: ";
    printArray(input);
    std::cout << "\n";

    SortResult result = sorter(input, true);

    std::cout << "Sorted output : ";
    printArray(result.sorted);
    std::cout << "\n";
    std::cout << "Operation count (demo run): " << result.opCount << "\n";
}

static void printTableHeader() {
    std::cout << std::left << std::setw(10) << "n" << std::setw(10) << "batch"
              << std::setw(18) << "T(avg opCount)" << std::setw(14) << "T/n"
              << std::setw(14) << "T/n^2" << std::setw(14) << "T/log2(n)"
              << std::setw(16) << "T/(n*log2n)" << "\n";
    std::cout << std::string(96, '-') << "\n";
}

static void runBatchAnalysis(const std::string& algorithmName,
                             const SortFunction& sorter,
                             const std::vector<int>& sizes,
                             int batchRepeats) {
    std::cout << "\n=== " << algorithmName << " Randomized Batch Analysis ===\n";
    printTableHeader();

    for (int n : sizes) {
        long long totalCost = 0;
        for (int run = 0; run < batchRepeats; ++run) {
            std::vector<int> input = generateRandomArray(n, 1, n * 10);
            SortResult result = sorter(input, false);
            if (!isSortedNonDecreasing(result.sorted)) {
                throw std::runtime_error("Sorting validation failed for " + algorithmName);
            }
            totalCost += result.opCount;
        }

        double avgCost = static_cast<double>(totalCost) / static_cast<double>(batchRepeats);
        double nAsDouble = static_cast<double>(n);
        double log2n = std::log2(nAsDouble);

        std::cout << std::left << std::setw(10) << n << std::setw(10) << batchRepeats
                  << std::setw(18) << std::fixed << std::setprecision(2) << avgCost
                  << std::setw(14) << avgCost / nAsDouble
                  << std::setw(14) << avgCost / (nAsDouble * nAsDouble)
                  << std::setw(14) << avgCost / log2n
                  << std::setw(16) << avgCost / (nAsDouble * log2n) << "\n";
    }
}

int main() {
    std::vector<int> demoInput = {34, 8, 64, 51, 32, 21, 5, 13};
    std::vector<int> testSizes = {100, 200, 500, 1000};
    int batchRepeats = 20;

    std::cout << "Task 1 + Task 2: Sorting demos with before-change array status\n";
    runDemo("QuickSort", demoInput, quickSort);
    runDemo("InsertionSort", demoInput, insertionSort);
    runDemo("HeapSort", demoInput, heapSort);
    runDemo("SelectionSort", demoInput, selectionSort);

    std::cout << "\nTask 3: Randomized input performance analysis\n";
    runBatchAnalysis("QuickSort", quickSort, testSizes, batchRepeats);
    runBatchAnalysis("InsertionSort", insertionSort, testSizes, batchRepeats);
    runBatchAnalysis("HeapSort", heapSort, testSizes, batchRepeats);
    runBatchAnalysis("SelectionSort", selectionSort, testSizes, batchRepeats);

    return 0;
}

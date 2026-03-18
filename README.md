# Simple Hash Table Implementation in Java

This is a comprehensive, production-quality implementation of a hash table data structure in Java, designed for both educational purposes and practical use.

## Overview

A hash table (also called hash map) is a data structure that implements an associative array abstract data type, a structure that can map keys to values. It uses a hash function to compute an index into an array of buckets or slots, from which the desired value can be found.

### Key Concepts Demonstrated

1. **Hashing**: Converting keys into array indices using a hash function
2. **Collision Resolution**: Using separate chaining (linked lists) to handle multiple keys hashing to the same index
3. **Dynamic Resizing**: Automatically growing the table when the load factor exceeds a threshold
4. **Generic Implementation**: Works with any key-value types using Java generics
5. **Performance Analysis**: O(1) average-case time complexity for basic operations

## Files

- **`SimpleHashTable.java`**: The main hash table implementation
- **`HashTableExample.java`**: Comprehensive examples showing various use cases
- **`README.md`**: This documentation file

## How to Compile and Run

```bash
# Compile both files
javac SimpleHashTable.java HashTableExample.java

# Run the examples
java HashTableExample
```

## Implementation Details

### Internal Structure

The hash table uses an array of linked lists (chains) to store key-value pairs:

```
buckets[] array:
[0] -> null
[1] -> [key1:value1] -> [key5:value5] -> null
[2] -> [key2:value2] -> null
[3] -> null
[4] -> [key3:value3] -> [key4:value4] -> [key6:value6] -> null
```

### Hash Function

The implementation uses a two-step hashing process:
1. Get the key's `hashCode()`
2. Improve distribution by XORing high bits with low bits
3. Map to bucket index using bitwise AND with (capacity - 1)

```java
int h = key.hashCode();
h ^= (h >>> 16);  // Mix high and low bits
return h & (buckets.length - 1);  // Fast modulo for power-of-2 sizes
```

### Load Factor and Resizing

- **Load Factor**: The ratio of size to capacity (number of elements / number of buckets)
- **Default Load Factor**: 0.75 (resize when table is 75% full)
- **Resizing**: When load factor is exceeded, the table doubles in size and all elements are rehashed

### Time Complexity

| Operation | Average Case | Worst Case |
|-----------|--------------|------------|
| put()     | O(1)         | O(n)       |
| get()     | O(1)         | O(n)       |
| remove()  | O(1)         | O(n)       |

The worst case occurs when all keys hash to the same bucket, creating a single long chain.

## API Reference

### Constructor

```java
SimpleHashTable()  // Default capacity: 16, load factor: 0.75
SimpleHashTable(int initialCapacity, float loadFactor)
```

### Core Methods

```java
V put(K key, V value)      // Insert or update key-value pair
V get(K key)               // Retrieve value for key
V remove(K key)            // Remove key-value pair
boolean containsKey(K key) // Check if key exists
int size()                 // Number of key-value pairs
boolean isEmpty()          // Check if table is empty
void clear()               // Remove all entries
```

### Utility Methods

```java
List<K> keys()             // Get all keys
List<V> values()           // Get all values
int getCapacity()          // Current bucket array size
float getCurrentLoadFactor() // Current load factor
void printBucketStructure() // Visual representation of internal structure
```

## Usage Examples

### Basic Usage

```java
SimpleHashTable<String, Integer> ages = new SimpleHashTable<>();
ages.put("Alice", 25);
ages.put("Bob", 30);

Integer aliceAge = ages.get("Alice");  // Returns 25
ages.remove("Bob");                     // Removes Bob's entry
```

### Custom Objects as Keys

Keys must properly implement `equals()` and `hashCode()`:

```java
class Point {
    int x, y;
    
    @Override
    public boolean equals(Object obj) {
        if (!(obj instanceof Point)) return false;
        Point other = (Point) obj;
        return x == other.x && y == other.y;
    }
    
    @Override
    public int hashCode() {
        return 31 * x + y;
    }
}

SimpleHashTable<Point, String> map = new SimpleHashTable<>();
map.put(new Point(1, 2), "Location A");
```

### Word Frequency Counter

```java
SimpleHashTable<String, Integer> wordCount = new SimpleHashTable<>();
for (String word : text.split(" ")) {
    Integer count = wordCount.get(word);
    wordCount.put(word, count == null ? 1 : count + 1);
}
```

## Performance Considerations

1. **Initial Capacity**: Choose based on expected size to minimize resizing
2. **Load Factor**: Lower values = more memory but better performance
3. **Hash Function Quality**: Poor hash functions lead to clustering and degraded performance
4. **Key equals() and hashCode()**: Must be properly implemented for custom key types

## Educational Value

This implementation teaches:
- How hash tables achieve O(1) average performance
- The importance of good hash functions
- Trade-offs between memory usage and performance
- How dynamic data structures handle growth
- Real-world applications of hash tables

## Comparison with Java's HashMap

This implementation is simpler than `java.util.HashMap` but demonstrates the same core concepts:
- Both use separate chaining for collisions
- Both use power-of-2 sizing for fast modulo operations
- Both implement dynamic resizing
- Java's HashMap has additional optimizations (tree-based buckets for long chains, better hash spreading)

## Further Learning

To extend this implementation, consider:
1. Implementing other collision resolution methods (open addressing, Robin Hood hashing)
2. Adding iterator support
3. Thread-safety with synchronization
4. Implementing the full Java Map interface
5. Performance optimizations (caching hash codes, tree-based buckets)
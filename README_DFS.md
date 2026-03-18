# Depth-First Search (DFS) Java Implementation

This repository contains a comprehensive, production-quality implementation of the Depth-First Search (DFS) algorithm in Java, including both educational examples and practical applications.

## Files Overview

### 1. `DFSExample.java`
Core DFS implementations with detailed documentation:
- **Recursive DFS**: Classic implementation using recursion
- **Iterative DFS**: Stack-based implementation for large graphs
- **Connected Components**: Finding disconnected graph components
- **Path Finding**: Checking if path exists between vertices
- Complete examples for both directed and undirected graphs

### 2. `DFSApplications.java`
Real-world applications and interview problems:
- **Cycle Detection**: Detect cycles in undirected graphs
- **Topological Sort**: Order vertices in directed acyclic graphs (DAGs)
- **All Paths**: Find all possible paths between two vertices
- **Maze Solver**: Solve 2D grid mazes using DFS

### 3. `README_DFS.md` (this file)
Documentation and usage guide

## How to Compile and Run

```bash
# Compile the files
javac DFSExample.java
javac DFSApplications.java

# Run the examples
java DFSExample
java DFSApplications
```

## Key Concepts

### What is DFS?
Depth-First Search is a graph traversal algorithm that explores as far as possible along each branch before backtracking. Think of it like exploring a maze by always taking the first unexplored path until you hit a dead end, then backing up to try the next path.

### When to Use DFS vs BFS?

**Use DFS when:**
- You need to explore all possible paths (backtracking problems)
- Finding connected components
- Detecting cycles
- Topological sorting
- The solution is likely deep in the tree/graph
- Memory is a constraint (DFS uses less memory than BFS)

**Use BFS when:**
- Finding shortest path in unweighted graphs
- Level-order traversal
- Finding nodes within a certain distance
- The solution is likely close to the starting point

### Time and Space Complexity

- **Time Complexity**: O(V + E)
  - V = number of vertices
  - E = number of edges
  - We visit each vertex once and explore all edges

- **Space Complexity**: 
  - Recursive: O(V) for the recursion stack
  - Iterative: O(V) for the explicit stack
  - Both need O(V) for the visited array

## Implementation Details

### Graph Representation
Both examples use an **adjacency list** representation:
```java
List<List<Integer>> adjacencyList;
```
- More space-efficient than adjacency matrix for sparse graphs
- Faster iteration over neighbors
- Easy to add/remove edges

### Key Implementation Patterns

1. **Visited Array**: Prevents infinite loops in cyclic graphs
   ```java
   boolean[] visited = new boolean[vertices];
   ```

2. **Backtracking**: For exploring all possibilities
   ```java
   // Add to path
   path.add(vertex);
   // Explore
   dfs(adjacent);
   // Remove from path (backtrack)
   path.remove(path.size() - 1);
   ```

3. **Stack vs Recursion**:
   - Recursion: Cleaner code, implicit stack
   - Iteration: No stack overflow risk, explicit control

## Common Interview Questions

1. **Number of Islands**: Count connected components in a 2D grid
2. **Word Search**: Find if word exists in 2D board
3. **Course Schedule**: Topological sort with prerequisites
4. **Clone Graph**: Deep copy a graph structure
5. **Longest Path in DAG**: DFS with memoization

## Production Considerations

### Error Handling
In production code, add:
- Null checks for graph/vertex parameters
- Bounds checking for vertex indices
- Cycle detection for algorithms that require DAGs

### Optimizations
- Use BitSet instead of boolean[] for very large graphs
- Consider parallel DFS for independent components
- Implement iterative deepening for memory-constrained environments

### Testing
Always test with:
- Empty graphs
- Single vertex graphs
- Disconnected graphs
- Graphs with cycles
- Complete graphs (every vertex connected to every other)

## Example Usage in Real Applications

### 1. File System Traversal
```java
// Similar to DFS - exploring directory tree
void exploreDirectory(File dir) {
    for (File file : dir.listFiles()) {
        if (file.isDirectory()) {
            exploreDirectory(file);  // Recursive DFS
        }
        processFile(file);
    }
}
```

### 2. Web Crawler
```java
// DFS to crawl website
void crawlWebsite(String url, Set<String> visited) {
    if (visited.contains(url)) return;
    visited.add(url);
    
    List<String> links = extractLinks(url);
    for (String link : links) {
        crawlWebsite(link, visited);
    }
}
```

### 3. Dependency Resolution
```java
// Topological sort for build dependencies
List<String> getBuildOrder(Map<String, List<String>> dependencies) {
    // Use DFS-based topological sort
}
```

## Further Reading

- [Introduction to Algorithms (CLRS)](https://mitpress.mit.edu/books/introduction-algorithms) - Chapter 22
- [Algorithms by Sedgewick](https://algs4.cs.princeton.edu/home/) - Graph algorithms section
- [LeetCode Graph Problems](https://leetcode.com/tag/depth-first-search/) - Practice problems

## License

This code is provided for educational purposes. Feel free to use and modify for your learning and projects.
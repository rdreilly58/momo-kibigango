import java.util.*;

/**
 * Depth-First Search (DFS) Implementation in Java
 * 
 * This class demonstrates both recursive and iterative approaches to DFS
 * on an undirected graph using an adjacency list representation.
 * 
 * Time Complexity: O(V + E) where V is vertices and E is edges
 * Space Complexity: O(V) for the visited array and recursion/stack
 */
public class DFSExample {
    
    /**
     * Graph class using adjacency list representation
     */
    static class Graph {
        private final int vertices;
        private final List<List<Integer>> adjacencyList;
        
        /**
         * Constructor to initialize graph with given number of vertices
         * @param vertices Number of vertices in the graph
         */
        public Graph(int vertices) {
            this.vertices = vertices;
            this.adjacencyList = new ArrayList<>(vertices);
            
            // Initialize adjacency list for each vertex
            for (int i = 0; i < vertices; i++) {
                adjacencyList.add(new ArrayList<>());
            }
        }
        
        /**
         * Adds an undirected edge between two vertices
         * @param source Source vertex
         * @param destination Destination vertex
         */
        public void addEdge(int source, int destination) {
            // For undirected graph, add edge in both directions
            adjacencyList.get(source).add(destination);
            adjacencyList.get(destination).add(source);
        }
        
        /**
         * Adds a directed edge from source to destination
         * @param source Source vertex
         * @param destination Destination vertex
         */
        public void addDirectedEdge(int source, int destination) {
            adjacencyList.get(source).add(destination);
        }
        
        /**
         * RECURSIVE DFS Implementation
         * 
         * This method performs DFS starting from a given vertex using recursion.
         * It explores as far as possible along each branch before backtracking.
         * 
         * @param startVertex The vertex to start DFS from
         * @return List of vertices in the order they were visited
         */
        public List<Integer> dfsRecursive(int startVertex) {
            // Track visited vertices to avoid cycles
            boolean[] visited = new boolean[vertices];
            List<Integer> dfsTraversal = new ArrayList<>();
            
            // Perform DFS starting from the given vertex
            dfsRecursiveUtil(startVertex, visited, dfsTraversal);
            
            return dfsTraversal;
        }
        
        /**
         * Utility method for recursive DFS
         * @param vertex Current vertex being visited
         * @param visited Array to track visited vertices
         * @param dfsTraversal List to store the DFS traversal order
         */
        private void dfsRecursiveUtil(int vertex, boolean[] visited, List<Integer> dfsTraversal) {
            // Mark current vertex as visited and add to traversal
            visited[vertex] = true;
            dfsTraversal.add(vertex);
            
            // Recursively visit all unvisited adjacent vertices
            for (int adjacentVertex : adjacencyList.get(vertex)) {
                if (!visited[adjacentVertex]) {
                    dfsRecursiveUtil(adjacentVertex, visited, dfsTraversal);
                }
            }
        }
        
        /**
         * ITERATIVE DFS Implementation
         * 
         * This method performs DFS using an explicit stack instead of recursion.
         * Useful when dealing with large graphs to avoid stack overflow.
         * 
         * @param startVertex The vertex to start DFS from
         * @return List of vertices in the order they were visited
         */
        public List<Integer> dfsIterative(int startVertex) {
            // Track visited vertices
            boolean[] visited = new boolean[vertices];
            List<Integer> dfsTraversal = new ArrayList<>();
            
            // Use explicit stack for iterative approach
            Stack<Integer> stack = new Stack<>();
            
            // Push start vertex to stack
            stack.push(startVertex);
            
            while (!stack.isEmpty()) {
                // Pop vertex from stack
                int vertex = stack.pop();
                
                // If not visited, process it
                if (!visited[vertex]) {
                    visited[vertex] = true;
                    dfsTraversal.add(vertex);
                    
                    // Add all unvisited adjacent vertices to stack
                    // Note: Adding in reverse order to maintain similar traversal order as recursive
                    List<Integer> neighbors = adjacencyList.get(vertex);
                    for (int i = neighbors.size() - 1; i >= 0; i--) {
                        int adjacentVertex = neighbors.get(i);
                        if (!visited[adjacentVertex]) {
                            stack.push(adjacentVertex);
                        }
                    }
                }
            }
            
            return dfsTraversal;
        }
        
        /**
         * DFS for finding all connected components in an undirected graph
         * @return List of connected components, each component is a list of vertices
         */
        public List<List<Integer>> findConnectedComponents() {
            boolean[] visited = new boolean[vertices];
            List<List<Integer>> components = new ArrayList<>();
            
            // Check each vertex
            for (int vertex = 0; vertex < vertices; vertex++) {
                if (!visited[vertex]) {
                    List<Integer> component = new ArrayList<>();
                    dfsRecursiveUtil(vertex, visited, component);
                    components.add(component);
                }
            }
            
            return components;
        }
        
        /**
         * DFS application: Check if path exists between two vertices
         * @param source Starting vertex
         * @param destination Target vertex
         * @return true if path exists, false otherwise
         */
        public boolean hasPath(int source, int destination) {
            if (source == destination) return true;
            
            boolean[] visited = new boolean[vertices];
            return hasPathDFS(source, destination, visited);
        }
        
        private boolean hasPathDFS(int current, int destination, boolean[] visited) {
            visited[current] = true;
            
            // Check all adjacent vertices
            for (int adjacent : adjacencyList.get(current)) {
                if (adjacent == destination) {
                    return true;
                }
                if (!visited[adjacent] && hasPathDFS(adjacent, destination, visited)) {
                    return true;
                }
            }
            
            return false;
        }
        
        /**
         * Prints the graph's adjacency list representation
         */
        public void printGraph() {
            for (int vertex = 0; vertex < vertices; vertex++) {
                System.out.print("Vertex " + vertex + ": ");
                for (int adjacent : adjacencyList.get(vertex)) {
                    System.out.print(adjacent + " ");
                }
                System.out.println();
            }
        }
    }
    
    /**
     * Main method demonstrating DFS usage with examples
     */
    public static void main(String[] args) {
        System.out.println("=== Depth-First Search (DFS) Examples ===\n");
        
        // Example 1: Basic DFS on a simple graph
        System.out.println("Example 1: Basic DFS Traversal");
        System.out.println("Creating a graph with 6 vertices (0-5):");
        
        Graph graph1 = new Graph(6);
        
        // Adding edges to create the graph:
        //     0 --- 1
        //     |     |
        //     2 --- 3
        //     |
        //     4 --- 5
        
        graph1.addEdge(0, 1);
        graph1.addEdge(0, 2);
        graph1.addEdge(1, 3);
        graph1.addEdge(2, 3);
        graph1.addEdge(2, 4);
        graph1.addEdge(4, 5);
        
        System.out.println("\nGraph structure:");
        graph1.printGraph();
        
        System.out.println("\nDFS Recursive starting from vertex 0: " + 
                         graph1.dfsRecursive(0));
        System.out.println("DFS Iterative starting from vertex 0: " + 
                         graph1.dfsIterative(0));
        
        // Example 2: DFS on a disconnected graph
        System.out.println("\n\nExample 2: DFS on Disconnected Graph");
        Graph graph2 = new Graph(7);
        
        // Creating two separate components:
        // Component 1: 0-1-2
        // Component 2: 3-4
        // Isolated vertices: 5, 6
        
        graph2.addEdge(0, 1);
        graph2.addEdge(1, 2);
        graph2.addEdge(3, 4);
        
        System.out.println("Connected components: " + 
                         graph2.findConnectedComponents());
        
        // Example 3: Path finding using DFS
        System.out.println("\n\nExample 3: Path Finding");
        System.out.println("Using graph from Example 1:");
        System.out.println("Path from 0 to 5 exists? " + graph1.hasPath(0, 5));
        System.out.println("Path from 1 to 4 exists? " + graph1.hasPath(1, 4));
        System.out.println("Path from 1 to 5 exists? " + graph1.hasPath(1, 5));
        
        // Example 4: DFS on a directed graph
        System.out.println("\n\nExample 4: DFS on Directed Graph");
        Graph directedGraph = new Graph(4);
        
        // Creating directed edges:
        // 0 -> 1 -> 2
        // |         ^
        // v         |
        // 3 --------+
        
        directedGraph.addDirectedEdge(0, 1);
        directedGraph.addDirectedEdge(0, 3);
        directedGraph.addDirectedEdge(1, 2);
        directedGraph.addDirectedEdge(3, 2);
        
        System.out.println("Directed graph structure:");
        directedGraph.printGraph();
        
        System.out.println("\nDFS from vertex 0: " + directedGraph.dfsRecursive(0));
        System.out.println("DFS from vertex 1: " + directedGraph.dfsRecursive(1));
        
        // Performance comparison example
        System.out.println("\n\nPerformance Note:");
        System.out.println("- Recursive DFS: Cleaner code, but limited by stack size");
        System.out.println("- Iterative DFS: Can handle larger graphs without stack overflow");
        System.out.println("- Both have O(V + E) time complexity");
    }
}
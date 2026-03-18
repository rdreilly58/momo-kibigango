#include <iostream>
#include <vector>
#include <queue>
#include <unordered_map>
#include <unordered_set>
#include <algorithm>
#include <sstream>

/**
 * @brief Graph class representing an undirected graph using adjacency list
 * 
 * This implementation uses an unordered_map to allow flexible vertex naming
 * (not limited to sequential integers). Each vertex maps to a vector of its neighbors.
 */
class Graph {
private:
    // Adjacency list representation: vertex -> list of adjacent vertices
    std::unordered_map<int, std::vector<int>> adjacencyList;
    
public:
    /**
     * @brief Add a vertex to the graph
     * @param vertex The vertex to add
     */
    void addVertex(int vertex) {
        if (adjacencyList.find(vertex) == adjacencyList.end()) {
            adjacencyList[vertex] = std::vector<int>();
        }
    }
    
    /**
     * @brief Add an undirected edge between two vertices
     * @param v1 First vertex
     * @param v2 Second vertex
     */
    void addEdge(int v1, int v2) {
        // Ensure both vertices exist
        addVertex(v1);
        addVertex(v2);
        
        // Add edge in both directions (undirected graph)
        adjacencyList[v1].push_back(v2);
        adjacencyList[v2].push_back(v1);
    }
    
    /**
     * @brief Get the neighbors of a vertex
     * @param vertex The vertex to get neighbors for
     * @return Vector of neighboring vertices
     */
    std::vector<int> getNeighbors(int vertex) const {
        auto it = adjacencyList.find(vertex);
        if (it != adjacencyList.end()) {
            return it->second;
        }
        return std::vector<int>();
    }
    
    /**
     * @brief Check if a vertex exists in the graph
     * @param vertex The vertex to check
     * @return true if vertex exists, false otherwise
     */
    bool hasVertex(int vertex) const {
        return adjacencyList.find(vertex) != adjacencyList.end();
    }
    
    /**
     * @brief Get all vertices in the graph
     * @return Vector of all vertices
     */
    std::vector<int> getAllVertices() const {
        std::vector<int> vertices;
        for (const auto& pair : adjacencyList) {
            vertices.push_back(pair.first);
        }
        return vertices;
    }
    
    /**
     * @brief Print the graph structure
     */
    void printGraph() const {
        std::cout << "Graph Structure (Adjacency List):\n";
        for (const auto& pair : adjacencyList) {
            std::cout << pair.first << " -> ";
            for (size_t i = 0; i < pair.second.size(); ++i) {
                std::cout << pair.second[i];
                if (i < pair.second.size() - 1) std::cout << ", ";
            }
            std::cout << "\n";
        }
        std::cout << "\n";
    }
};

/**
 * @brief Breadth-First Search (BFS) Algorithm Implementation
 * 
 * BFS explores a graph level by level, visiting all neighbors of a vertex
 * before moving to the next level. It uses a queue to maintain the order
 * of vertices to visit.
 * 
 * Time Complexity: O(V + E) where V is vertices and E is edges
 * Space Complexity: O(V) for the visited set and queue
 * 
 * @param graph The graph to traverse
 * @param startVertex The starting vertex for traversal
 * @return Vector containing the order of visited vertices
 */
std::vector<int> breadthFirstSearch(const Graph& graph, int startVertex) {
    std::vector<int> traversalOrder;
    
    // Check if start vertex exists
    if (!graph.hasVertex(startVertex)) {
        std::cout << "Error: Start vertex " << startVertex << " not found in graph.\n";
        return traversalOrder;
    }
    
    // Queue to store vertices to visit (FIFO - First In First Out)
    std::queue<int> vertexQueue;
    
    // Set to keep track of visited vertices (prevents cycles)
    std::unordered_set<int> visited;
    
    // Step 1: Add the starting vertex to the queue and mark as visited
    vertexQueue.push(startVertex);
    visited.insert(startVertex);
    
    std::cout << "BFS Traversal Steps:\n";
    std::cout << "Starting from vertex: " << startVertex << "\n\n";
    
    // Step 2: Continue until all reachable vertices are visited
    while (!vertexQueue.empty()) {
        // Step 3: Dequeue a vertex from the front of the queue
        int currentVertex = vertexQueue.front();
        vertexQueue.pop();
        
        // Step 4: Process the current vertex (add to traversal order)
        traversalOrder.push_back(currentVertex);
        
        // Debug output showing current state
        std::cout << "Visiting vertex: " << currentVertex << "\n";
        std::cout << "  Queue state: [";
        std::queue<int> tempQueue = vertexQueue; // Copy for display
        bool first = true;
        while (!tempQueue.empty()) {
            if (!first) std::cout << ", ";
            std::cout << tempQueue.front();
            tempQueue.pop();
            first = false;
        }
        std::cout << "]\n";
        
        // Step 5: Get all neighbors of the current vertex
        std::vector<int> neighbors = graph.getNeighbors(currentVertex);
        std::cout << "  Neighbors: [";
        for (size_t i = 0; i < neighbors.size(); ++i) {
            std::cout << neighbors[i];
            if (i < neighbors.size() - 1) std::cout << ", ";
        }
        std::cout << "]\n";
        
        // Step 6: For each unvisited neighbor, mark as visited and enqueue
        for (int neighbor : neighbors) {
            if (visited.find(neighbor) == visited.end()) {
                visited.insert(neighbor);
                vertexQueue.push(neighbor);
                std::cout << "    Enqueuing unvisited neighbor: " << neighbor << "\n";
            } else {
                std::cout << "    Neighbor " << neighbor << " already visited, skipping\n";
            }
        }
        std::cout << "\n";
    }
    
    return traversalOrder;
}

/**
 * @brief Find the shortest path between two vertices using BFS
 * 
 * BFS naturally finds the shortest path in unweighted graphs
 * 
 * @param graph The graph to search
 * @param start Starting vertex
 * @param end Target vertex
 * @return Vector representing the shortest path, empty if no path exists
 */
std::vector<int> findShortestPath(const Graph& graph, int start, int end) {
    std::vector<int> path;
    
    if (!graph.hasVertex(start) || !graph.hasVertex(end)) {
        return path;
    }
    
    std::queue<int> queue;
    std::unordered_set<int> visited;
    std::unordered_map<int, int> parent; // To reconstruct the path
    
    queue.push(start);
    visited.insert(start);
    parent[start] = -1; // Start has no parent
    
    bool found = false;
    
    while (!queue.empty() && !found) {
        int current = queue.front();
        queue.pop();
        
        if (current == end) {
            found = true;
            break;
        }
        
        for (int neighbor : graph.getNeighbors(current)) {
            if (visited.find(neighbor) == visited.end()) {
                visited.insert(neighbor);
                parent[neighbor] = current;
                queue.push(neighbor);
            }
        }
    }
    
    // Reconstruct path if found
    if (found) {
        int current = end;
        while (current != -1) {
            path.push_back(current);
            current = parent[current];
        }
        std::reverse(path.begin(), path.end());
    }
    
    return path;
}

/**
 * @brief Check if the graph is connected using BFS
 * 
 * A graph is connected if there's a path between every pair of vertices
 * 
 * @param graph The graph to check
 * @return true if connected, false otherwise
 */
bool isConnected(const Graph& graph) {
    std::vector<int> vertices = graph.getAllVertices();
    if (vertices.empty()) return true;
    
    // Perform BFS from the first vertex
    std::vector<int> reachable = breadthFirstSearch(graph, vertices[0]);
    
    // If BFS visited all vertices, the graph is connected
    return reachable.size() == vertices.size();
}

// Helper function to print a vector
void printVector(const std::vector<int>& vec, const std::string& label) {
    std::cout << label << ": [";
    for (size_t i = 0; i < vec.size(); ++i) {
        std::cout << vec[i];
        if (i < vec.size() - 1) std::cout << ", ";
    }
    std::cout << "]\n";
}

int main() {
    std::cout << "=== Breadth-First Search (BFS) Comprehensive Example ===\n\n";
    
    // Create a sample graph
    Graph graph;
    
    // Adding edges to create the following graph:
    //       1 --- 2
    //      / \     \
    //     3   4     5
    //      \ / \   /
    //       6   7-8
    
    graph.addEdge(1, 2);
    graph.addEdge(1, 3);
    graph.addEdge(1, 4);
    graph.addEdge(2, 5);
    graph.addEdge(3, 6);
    graph.addEdge(4, 6);
    graph.addEdge(4, 7);
    graph.addEdge(5, 8);
    graph.addEdge(7, 8);
    
    // Print the graph structure
    graph.printGraph();
    
    // Perform BFS from vertex 1
    std::cout << "=== BFS Traversal from vertex 1 ===\n";
    std::vector<int> bfsResult = breadthFirstSearch(graph, 1);
    printVector(bfsResult, "\nFinal BFS Traversal Order");
    
    std::cout << "\n=== Shortest Path Examples ===\n";
    
    // Find shortest paths between various vertices
    std::vector<std::pair<int, int>> pathQueries = {{1, 8}, {3, 5}, {6, 2}};
    
    for (const auto& query : pathQueries) {
        std::vector<int> path = findShortestPath(graph, query.first, query.second);
        std::cout << "Shortest path from " << query.first << " to " << query.second << ": ";
        if (path.empty()) {
            std::cout << "No path exists\n";
        } else {
            printVector(path, "");
            std::cout << "  Path length: " << path.size() - 1 << " edges\n";
        }
    }
    
    std::cout << "\n=== Graph Connectivity Test ===\n";
    std::cout << "Is the graph connected? " << (isConnected(graph) ? "Yes" : "No") << "\n";
    
    // Create a disconnected graph for demonstration
    std::cout << "\n=== Testing Disconnected Graph ===\n";
    Graph disconnectedGraph;
    disconnectedGraph.addEdge(1, 2);
    disconnectedGraph.addEdge(3, 4);  // Separate component
    
    disconnectedGraph.printGraph();
    std::cout << "Is this graph connected? " << (isConnected(disconnectedGraph) ? "Yes" : "No") << "\n";
    
    // BFS on disconnected graph
    std::cout << "\nBFS on disconnected graph starting from vertex 1:\n";
    std::vector<int> disconnectedBFS = breadthFirstSearch(disconnectedGraph, 1);
    printVector(disconnectedBFS, "Vertices reached");
    std::cout << "Note: Vertices 3 and 4 are unreachable from vertex 1\n";
    
    return 0;
}
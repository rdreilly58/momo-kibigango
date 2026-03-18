import java.util.*;

/**
 * Common DFS Applications and Interview Problems
 * 
 * This class demonstrates practical applications of DFS including:
 * - Cycle detection
 * - Topological sort
 * - Finding all paths between nodes
 * - Detecting bipartite graphs
 * - Solving maze problems
 */
public class DFSApplications {
    
    /**
     * Application 1: Cycle Detection in Undirected Graph
     * 
     * Uses DFS to detect if an undirected graph contains a cycle
     * Time Complexity: O(V + E)
     */
    static class CycleDetection {
        private int vertices;
        private List<List<Integer>> adjacencyList;
        
        public CycleDetection(int vertices) {
            this.vertices = vertices;
            this.adjacencyList = new ArrayList<>(vertices);
            for (int i = 0; i < vertices; i++) {
                adjacencyList.add(new ArrayList<>());
            }
        }
        
        public void addEdge(int u, int v) {
            adjacencyList.get(u).add(v);
            adjacencyList.get(v).add(u);
        }
        
        /**
         * Detects if the graph contains a cycle
         * @return true if cycle exists, false otherwise
         */
        public boolean hasCycle() {
            boolean[] visited = new boolean[vertices];
            
            // Check each component of the graph
            for (int i = 0; i < vertices; i++) {
                if (!visited[i]) {
                    if (hasCycleDFS(i, -1, visited)) {
                        return true;
                    }
                }
            }
            return false;
        }
        
        private boolean hasCycleDFS(int vertex, int parent, boolean[] visited) {
            visited[vertex] = true;
            
            // Check all adjacent vertices
            for (int adjacent : adjacencyList.get(vertex)) {
                if (!visited[adjacent]) {
                    if (hasCycleDFS(adjacent, vertex, visited)) {
                        return true;
                    }
                } else if (adjacent != parent) {
                    // If adjacent is visited and not parent, we found a cycle
                    return true;
                }
            }
            return false;
        }
    }
    
    /**
     * Application 2: Topological Sort using DFS
     * 
     * Orders vertices in a directed acyclic graph (DAG) such that
     * for every directed edge (u,v), u comes before v in the ordering
     */
    static class TopologicalSort {
        private int vertices;
        private List<List<Integer>> adjacencyList;
        
        public TopologicalSort(int vertices) {
            this.vertices = vertices;
            this.adjacencyList = new ArrayList<>(vertices);
            for (int i = 0; i < vertices; i++) {
                adjacencyList.add(new ArrayList<>());
            }
        }
        
        public void addEdge(int u, int v) {
            adjacencyList.get(u).add(v);
        }
        
        /**
         * Performs topological sort
         * @return List of vertices in topologically sorted order
         * @throws IllegalStateException if graph contains a cycle
         */
        public List<Integer> topologicalSort() {
            Stack<Integer> stack = new Stack<>();
            boolean[] visited = new boolean[vertices];
            
            // Perform DFS from all unvisited vertices
            for (int i = 0; i < vertices; i++) {
                if (!visited[i]) {
                    topologicalSortDFS(i, visited, stack);
                }
            }
            
            // Pop all vertices from stack to get topological order
            List<Integer> result = new ArrayList<>();
            while (!stack.isEmpty()) {
                result.add(stack.pop());
            }
            
            return result;
        }
        
        private void topologicalSortDFS(int vertex, boolean[] visited, Stack<Integer> stack) {
            visited[vertex] = true;
            
            // Recursively visit all adjacent vertices
            for (int adjacent : adjacencyList.get(vertex)) {
                if (!visited[adjacent]) {
                    topologicalSortDFS(adjacent, visited, stack);
                }
            }
            
            // Push current vertex to stack after visiting all its adjacents
            stack.push(vertex);
        }
    }
    
    /**
     * Application 3: Find All Paths Between Two Vertices
     * 
     * Uses DFS with backtracking to find all possible paths
     */
    static class AllPaths {
        private int vertices;
        private List<List<Integer>> adjacencyList;
        
        public AllPaths(int vertices) {
            this.vertices = vertices;
            this.adjacencyList = new ArrayList<>(vertices);
            for (int i = 0; i < vertices; i++) {
                adjacencyList.add(new ArrayList<>());
            }
        }
        
        public void addEdge(int u, int v) {
            adjacencyList.get(u).add(v);
        }
        
        /**
         * Finds all paths from source to destination
         * @param source Starting vertex
         * @param destination Target vertex
         * @return List of all possible paths
         */
        public List<List<Integer>> findAllPaths(int source, int destination) {
            List<List<Integer>> allPaths = new ArrayList<>();
            List<Integer> currentPath = new ArrayList<>();
            boolean[] visited = new boolean[vertices];
            
            // Start DFS with backtracking
            findAllPathsDFS(source, destination, visited, currentPath, allPaths);
            
            return allPaths;
        }
        
        private void findAllPathsDFS(int current, int destination, boolean[] visited,
                                     List<Integer> currentPath, List<List<Integer>> allPaths) {
            // Add current vertex to path and mark as visited
            visited[current] = true;
            currentPath.add(current);
            
            // If we reached destination, add current path to results
            if (current == destination) {
                allPaths.add(new ArrayList<>(currentPath));
            } else {
                // Explore all adjacent vertices
                for (int adjacent : adjacencyList.get(current)) {
                    if (!visited[adjacent]) {
                        findAllPathsDFS(adjacent, destination, visited, currentPath, allPaths);
                    }
                }
            }
            
            // Backtrack: remove current vertex and mark as unvisited
            currentPath.remove(currentPath.size() - 1);
            visited[current] = false;
        }
    }
    
    /**
     * Application 4: Maze Solver using DFS
     * 
     * Solves a maze represented as a 2D grid
     */
    static class MazeSolver {
        private static final int[] dx = {-1, 1, 0, 0}; // Up, Down, Left, Right
        private static final int[] dy = {0, 0, -1, 1};
        
        /**
         * Solves maze using DFS
         * @param maze 2D grid (0 = path, 1 = wall)
         * @param startX Starting X coordinate
         * @param startY Starting Y coordinate
         * @param endX Ending X coordinate
         * @param endY Ending Y coordinate
         * @return Path from start to end, or empty list if no path exists
         */
        public List<int[]> solveMaze(int[][] maze, int startX, int startY, int endX, int endY) {
            int rows = maze.length;
            int cols = maze[0].length;
            boolean[][] visited = new boolean[rows][cols];
            List<int[]> path = new ArrayList<>();
            
            if (solveMazeDFS(maze, startX, startY, endX, endY, visited, path)) {
                return path;
            }
            
            return new ArrayList<>(); // No path found
        }
        
        private boolean solveMazeDFS(int[][] maze, int x, int y, int endX, int endY,
                                     boolean[][] visited, List<int[]> path) {
            // Check if out of bounds or wall or already visited
            if (x < 0 || x >= maze.length || y < 0 || y >= maze[0].length ||
                maze[x][y] == 1 || visited[x][y]) {
                return false;
            }
            
            // Mark as visited and add to path
            visited[x][y] = true;
            path.add(new int[]{x, y});
            
            // Check if we reached the end
            if (x == endX && y == endY) {
                return true;
            }
            
            // Try all four directions
            for (int i = 0; i < 4; i++) {
                int nextX = x + dx[i];
                int nextY = y + dy[i];
                
                if (solveMazeDFS(maze, nextX, nextY, endX, endY, visited, path)) {
                    return true;
                }
            }
            
            // Backtrack if no path found
            path.remove(path.size() - 1);
            return false;
        }
        
        /**
         * Prints the maze with the solution path marked
         */
        public void printMazeWithPath(int[][] maze, List<int[]> path) {
            int rows = maze.length;
            int cols = maze[0].length;
            char[][] display = new char[rows][cols];
            
            // Initialize display
            for (int i = 0; i < rows; i++) {
                for (int j = 0; j < cols; j++) {
                    display[i][j] = maze[i][j] == 1 ? '#' : ' ';
                }
            }
            
            // Mark path
            for (int[] cell : path) {
                display[cell[0]][cell[1]] = '*';
            }
            
            // Mark start and end
            if (!path.isEmpty()) {
                int[] start = path.get(0);
                int[] end = path.get(path.size() - 1);
                display[start[0]][start[1]] = 'S';
                display[end[0]][end[1]] = 'E';
            }
            
            // Print
            for (int i = 0; i < rows; i++) {
                for (int j = 0; j < cols; j++) {
                    System.out.print(display[i][j] + " ");
                }
                System.out.println();
            }
        }
    }
    
    /**
     * Main method demonstrating all applications
     */
    public static void main(String[] args) {
        System.out.println("=== DFS Applications Demo ===\n");
        
        // Demo 1: Cycle Detection
        System.out.println("1. Cycle Detection:");
        CycleDetection cd = new CycleDetection(5);
        cd.addEdge(0, 1);
        cd.addEdge(1, 2);
        cd.addEdge(2, 3);
        cd.addEdge(3, 4);
        System.out.println("Graph without cycle has cycle? " + cd.hasCycle());
        
        cd.addEdge(4, 1); // Add edge to create cycle
        System.out.println("Graph with cycle has cycle? " + cd.hasCycle());
        
        // Demo 2: Topological Sort
        System.out.println("\n2. Topological Sort (Course Prerequisites):");
        TopologicalSort ts = new TopologicalSort(6);
        // Course dependencies: to take course v, must complete course u first
        ts.addEdge(5, 2); // Must take course 5 before course 2
        ts.addEdge(5, 0);
        ts.addEdge(4, 0);
        ts.addEdge(4, 1);
        ts.addEdge(2, 3);
        ts.addEdge(3, 1);
        
        List<Integer> courseOrder = ts.topologicalSort();
        System.out.println("Course order: " + courseOrder);
        
        // Demo 3: Find All Paths
        System.out.println("\n3. Find All Paths:");
        AllPaths ap = new AllPaths(4);
        ap.addEdge(0, 1);
        ap.addEdge(0, 2);
        ap.addEdge(1, 2);
        ap.addEdge(1, 3);
        ap.addEdge(2, 3);
        
        List<List<Integer>> allPaths = ap.findAllPaths(0, 3);
        System.out.println("All paths from 0 to 3:");
        for (List<Integer> path : allPaths) {
            System.out.println("  " + path);
        }
        
        // Demo 4: Maze Solver
        System.out.println("\n4. Maze Solver:");
        int[][] maze = {
            {0, 0, 1, 0, 0},
            {0, 1, 1, 0, 1},
            {0, 0, 0, 0, 0},
            {1, 1, 0, 1, 0},
            {0, 0, 0, 1, 0}
        };
        
        MazeSolver ms = new MazeSolver();
        List<int[]> solution = ms.solveMaze(maze, 0, 0, 4, 4);
        
        if (!solution.isEmpty()) {
            System.out.println("Maze solution found!");
            System.out.println("Path coordinates: ");
            for (int[] cell : solution) {
                System.out.print("(" + cell[0] + "," + cell[1] + ") ");
            }
            System.out.println("\n\nMaze with solution path:");
            ms.printMazeWithPath(maze, solution);
        } else {
            System.out.println("No solution exists!");
        }
        
        System.out.println("\n=== Key DFS Concepts ===");
        System.out.println("1. Backtracking: Undo choices to explore all possibilities");
        System.out.println("2. Visited tracking: Prevent infinite loops in cyclic graphs");
        System.out.println("3. Path recording: Keep track of current path for problems like maze solving");
        System.out.println("4. Post-order processing: Process node after its children (topological sort)");
    }
}
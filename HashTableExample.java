import java.util.Random;

/**
 * Comprehensive example demonstrating the SimpleHashTable implementation.
 * This example shows:
 * 1. Basic operations (put, get, remove)
 * 2. Different data types as keys and values
 * 3. Collision handling and resolution
 * 4. Dynamic resizing behavior
 * 5. Performance characteristics
 * 6. Real-world usage scenarios
 */
public class HashTableExample {
    
    public static void main(String[] args) {
        System.out.println("=== Simple Hash Table Example ===\n");
        
        // Example 1: Basic Usage
        basicUsageExample();
        
        // Example 2: Different Data Types
        differentDataTypesExample();
        
        // Example 3: Collision Demonstration
        collisionExample();
        
        // Example 4: Dynamic Resizing
        resizingExample();
        
        // Example 5: Performance Test
        performanceTest();
        
        // Example 6: Real-world Use Case - Word Frequency Counter
        wordFrequencyExample();
    }
    
    /**
     * Example 1: Basic operations - put, get, remove, containsKey
     */
    private static void basicUsageExample() {
        System.out.println("1. BASIC USAGE EXAMPLE");
        System.out.println("----------------------");
        
        SimpleHashTable<String, Integer> ages = new SimpleHashTable<>();
        
        // Adding key-value pairs
        ages.put("Alice", 25);
        ages.put("Bob", 30);
        ages.put("Charlie", 35);
        ages.put("Diana", 28);
        
        System.out.println("Added 4 people to hash table");
        System.out.println("Size: " + ages.size());
        
        // Retrieving values
        System.out.println("\nRetrieving values:");
        System.out.println("Alice's age: " + ages.get("Alice"));
        System.out.println("Bob's age: " + ages.get("Bob"));
        System.out.println("Unknown person: " + ages.get("Eve")); // Returns null
        
        // Checking if key exists
        System.out.println("\nChecking existence:");
        System.out.println("Contains 'Charlie': " + ages.containsKey("Charlie"));
        System.out.println("Contains 'Eve': " + ages.containsKey("Eve"));
        
        // Updating existing value
        Integer oldAge = ages.put("Alice", 26);
        System.out.println("\nUpdated Alice's age from " + oldAge + " to " + ages.get("Alice"));
        
        // Removing entries
        Integer removedAge = ages.remove("Bob");
        System.out.println("Removed Bob (age " + removedAge + ")");
        System.out.println("Size after removal: " + ages.size());
        
        // Print all keys
        System.out.println("\nAll people in hash table: " + ages.keys());
        
        ages.printBucketStructure();
    }
    
    /**
     * Example 2: Using different data types as keys and values
     */
    private static void differentDataTypesExample() {
        System.out.println("\n2. DIFFERENT DATA TYPES EXAMPLE");
        System.out.println("--------------------------------");
        
        // Integer keys, String values
        SimpleHashTable<Integer, String> studentNames = new SimpleHashTable<>();
        studentNames.put(101, "John Doe");
        studentNames.put(102, "Jane Smith");
        studentNames.put(103, "Mike Johnson");
        
        System.out.println("Student ID 102: " + studentNames.get(102));
        
        // Custom objects as keys (must properly implement equals() and hashCode())
        class Point {
            final int x, y;
            
            Point(int x, int y) {
                this.x = x;
                this.y = y;
            }
            
            @Override
            public boolean equals(Object obj) {
                if (this == obj) return true;
                if (!(obj instanceof Point)) return false;
                Point other = (Point) obj;
                return x == other.x && y == other.y;
            }
            
            @Override
            public int hashCode() {
                return 31 * x + y;
            }
            
            @Override
            public String toString() {
                return "(" + x + "," + y + ")";
            }
        }
        
        SimpleHashTable<Point, String> locationNames = new SimpleHashTable<>();
        locationNames.put(new Point(0, 0), "Origin");
        locationNames.put(new Point(1, 0), "East");
        locationNames.put(new Point(0, 1), "North");
        
        System.out.println("Location at (0,0): " + locationNames.get(new Point(0, 0)));
        System.out.println("Location at (1,0): " + locationNames.get(new Point(1, 0)));
        
        // Null key handling
        SimpleHashTable<String, String> nullKeyTable = new SimpleHashTable<>();
        nullKeyTable.put(null, "This is a null key");
        nullKeyTable.put("regular", "This is a regular key");
        
        System.out.println("\nNull key value: " + nullKeyTable.get(null));
        System.out.println("Regular key value: " + nullKeyTable.get("regular"));
    }
    
    /**
     * Example 3: Demonstrating collision handling with keys that hash to same bucket
     */
    private static void collisionExample() {
        System.out.println("\n3. COLLISION HANDLING EXAMPLE");
        System.out.println("-----------------------------");
        
        // Create a small hash table to force collisions
        SimpleHashTable<String, Integer> collisionTable = new SimpleHashTable<>(4, 0.75f);
        
        // These strings are chosen to potentially collide in a small table
        String[] keys = {"AA", "BB", "CC", "DD", "EE", "FF", "GG", "HH"};
        
        System.out.println("Adding 8 keys to a small hash table (initial capacity: 4)");
        System.out.println("This will cause collisions and demonstrate chaining...\n");
        
        for (int i = 0; i < keys.length; i++) {
            collisionTable.put(keys[i], i);
            System.out.println("Added key '" + keys[i] + "' with value " + i);
        }
        
        System.out.println("\nAll keys successfully stored despite collisions:");
        for (String key : keys) {
            System.out.println(key + " -> " + collisionTable.get(key));
        }
        
        collisionTable.printBucketStructure();
    }
    
    /**
     * Example 4: Demonstrating dynamic resizing behavior
     */
    private static void resizingExample() {
        System.out.println("\n4. DYNAMIC RESIZING EXAMPLE");
        System.out.println("---------------------------");
        
        // Start with a very small table
        SimpleHashTable<Integer, String> resizingTable = new SimpleHashTable<>(2, 0.75f);
        
        System.out.println("Initial capacity: " + resizingTable.getCapacity());
        System.out.println("Load factor threshold: 0.75");
        System.out.println("\nAdding elements and watching resize behavior...\n");
        
        for (int i = 1; i <= 10; i++) {
            resizingTable.put(i, "Value" + i);
            System.out.println("Added element " + i + 
                             " | Size: " + resizingTable.size() + 
                             " | Capacity: " + resizingTable.getCapacity() +
                             " | Load: " + String.format("%.2f", resizingTable.getCurrentLoadFactor()));
            
            // Check if resize occurred
            if (i > 1 && resizingTable.getCapacity() > Math.pow(2, Math.floor(Math.log(i-1)/Math.log(2)))) {
                System.out.println("  >>> RESIZE OCCURRED! Capacity doubled.");
            }
        }
        
        resizingTable.printBucketStructure();
    }
    
    /**
     * Example 5: Performance comparison with different load factors
     */
    private static void performanceTest() {
        System.out.println("\n5. PERFORMANCE TEST");
        System.out.println("-------------------");
        
        int numOperations = 100000;
        Random rand = new Random(42); // Fixed seed for reproducibility
        
        // Test with different load factors
        float[] loadFactors = {0.5f, 0.75f, 1.0f, 2.0f};
        
        for (float lf : loadFactors) {
            SimpleHashTable<Integer, Integer> table = new SimpleHashTable<>(16, lf);
            
            // Insert operations
            long startTime = System.nanoTime();
            for (int i = 0; i < numOperations; i++) {
                table.put(i, rand.nextInt());
            }
            long insertTime = System.nanoTime() - startTime;
            
            // Get operations
            startTime = System.nanoTime();
            for (int i = 0; i < numOperations; i++) {
                table.get(rand.nextInt(numOperations));
            }
            long getTime = System.nanoTime() - startTime;
            
            System.out.println("\nLoad Factor: " + lf);
            System.out.println("Final capacity: " + table.getCapacity());
            System.out.println("Insert time: " + (insertTime / 1_000_000) + " ms");
            System.out.println("Get time: " + (getTime / 1_000_000) + " ms");
            System.out.println("Avg insert: " + (insertTime / numOperations) + " ns/op");
            System.out.println("Avg get: " + (getTime / numOperations) + " ns/op");
        }
    }
    
    /**
     * Example 6: Real-world use case - Word frequency counter
     */
    private static void wordFrequencyExample() {
        System.out.println("\n6. REAL-WORLD EXAMPLE: WORD FREQUENCY COUNTER");
        System.out.println("----------------------------------------------");
        
        String text = "The quick brown fox jumps over the lazy dog. " +
                     "The dog was really lazy. The fox was very quick and brown. " +
                     "Quick brown foxes are common in the forest.";
        
        // Convert to lowercase and split into words
        String[] words = text.toLowerCase().replaceAll("[^a-z\\s]", "").split("\\s+");
        
        // Count word frequencies using our hash table
        SimpleHashTable<String, Integer> wordCount = new SimpleHashTable<>();
        
        for (String word : words) {
            Integer count = wordCount.get(word);
            if (count == null) {
                wordCount.put(word, 1);
            } else {
                wordCount.put(word, count + 1);
            }
        }
        
        System.out.println("Word frequencies from the text:");
        System.out.println("-------------------------------");
        
        // Sort by frequency for better display
        wordCount.keys().stream()
            .sorted((a, b) -> wordCount.get(b).compareTo(wordCount.get(a)))
            .forEach(word -> System.out.println(word + ": " + wordCount.get(word)));
        
        System.out.println("\nTotal unique words: " + wordCount.size());
        
        // Show internal structure
        wordCount.printBucketStructure();
        
        // Demonstrate some queries
        System.out.println("Frequency of 'the': " + wordCount.get("the"));
        System.out.println("Frequency of 'quick': " + wordCount.get("quick"));
        System.out.println("Frequency of 'elephant': " + wordCount.get("elephant"));
    }
}
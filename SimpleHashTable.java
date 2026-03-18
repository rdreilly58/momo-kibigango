import java.util.ArrayList;
import java.util.List;

/**
 * A simple hash table implementation using separate chaining for collision resolution.
 * 
 * Hash tables provide O(1) average-case time complexity for basic operations (put, get, remove).
 * This implementation demonstrates the core concepts of hash tables:
 * - Hashing: Converting keys into array indices
 * - Collision handling: Using linked lists (chaining) when multiple keys hash to same index
 * - Dynamic resizing: Growing the table when load factor exceeds threshold
 * 
 * @param <K> The type of keys maintained by this hash table
 * @param <V> The type of mapped values
 */
public class SimpleHashTable<K, V> {
    
    /**
     * Node class represents a key-value pair in the hash table.
     * Each bucket contains a linked list of nodes to handle collisions.
     */
    private static class Node<K, V> {
        final K key;
        V value;
        Node<K, V> next;
        
        Node(K key, V value, Node<K, V> next) {
            this.key = key;
            this.value = value;
            this.next = next;
        }
    }
    
    // The underlying array of buckets
    private Node<K, V>[] buckets;
    
    // Number of key-value pairs in the hash table
    private int size;
    
    // Default initial capacity (must be power of 2 for optimal performance)
    private static final int DEFAULT_CAPACITY = 16;
    
    // Load factor threshold - resize when size exceeds capacity * load factor
    private static final float DEFAULT_LOAD_FACTOR = 0.75f;
    
    // Current load factor threshold
    private final float loadFactor;
    
    /**
     * Constructs an empty hash table with default initial capacity and load factor.
     */
    @SuppressWarnings("unchecked")
    public SimpleHashTable() {
        this.buckets = (Node<K, V>[]) new Node[DEFAULT_CAPACITY];
        this.loadFactor = DEFAULT_LOAD_FACTOR;
        this.size = 0;
    }
    
    /**
     * Constructs an empty hash table with specified initial capacity and load factor.
     * 
     * @param initialCapacity the initial capacity
     * @param loadFactor the load factor threshold for resizing
     */
    @SuppressWarnings("unchecked")
    public SimpleHashTable(int initialCapacity, float loadFactor) {
        if (initialCapacity <= 0) {
            throw new IllegalArgumentException("Initial capacity must be positive");
        }
        if (loadFactor <= 0 || Float.isNaN(loadFactor)) {
            throw new IllegalArgumentException("Load factor must be positive");
        }
        
        // Round up to nearest power of 2
        int capacity = 1;
        while (capacity < initialCapacity) {
            capacity <<= 1;
        }
        
        this.buckets = (Node<K, V>[]) new Node[capacity];
        this.loadFactor = loadFactor;
        this.size = 0;
    }
    
    /**
     * Computes the hash code for a given key and maps it to a bucket index.
     * Uses bitwise AND with (capacity - 1) for fast modulo operation.
     * This works because capacity is always a power of 2.
     * 
     * @param key the key to hash
     * @return the bucket index for this key
     */
    private int hash(K key) {
        if (key == null) {
            return 0; // null keys always go to bucket 0
        }
        
        // Use Object's hashCode and improve distribution with bit manipulation
        int h = key.hashCode();
        // XOR higher bits with lower bits for better distribution
        h ^= (h >>> 16);
        
        // Map to bucket index using bitwise AND (equivalent to h % buckets.length)
        return h & (buckets.length - 1);
    }
    
    /**
     * Associates the specified value with the specified key in this hash table.
     * If the table previously contained a mapping for the key, the old value is replaced.
     * 
     * Time Complexity: O(1) average case, O(n) worst case (all keys hash to same bucket)
     * 
     * @param key key with which the specified value is to be associated
     * @param value value to be associated with the specified key
     * @return the previous value associated with key, or null if there was no mapping
     */
    public V put(K key, V value) {
        int bucketIndex = hash(key);
        Node<K, V> head = buckets[bucketIndex];
        
        // Search for existing key in the chain
        Node<K, V> current = head;
        while (current != null) {
            if (keysEqual(current.key, key)) {
                // Key exists, update value
                V oldValue = current.value;
                current.value = value;
                return oldValue;
            }
            current = current.next;
        }
        
        // Key doesn't exist, add new node at beginning of chain
        Node<K, V> newNode = new Node<>(key, value, head);
        buckets[bucketIndex] = newNode;
        size++;
        
        // Check if resize is needed
        if (size > buckets.length * loadFactor) {
            resize();
        }
        
        return null;
    }
    
    /**
     * Returns the value to which the specified key is mapped,
     * or null if this map contains no mapping for the key.
     * 
     * Time Complexity: O(1) average case, O(n) worst case
     * 
     * @param key the key whose associated value is to be returned
     * @return the value to which the specified key is mapped, or null
     */
    public V get(K key) {
        int bucketIndex = hash(key);
        Node<K, V> current = buckets[bucketIndex];
        
        // Search through the chain
        while (current != null) {
            if (keysEqual(current.key, key)) {
                return current.value;
            }
            current = current.next;
        }
        
        return null; // Key not found
    }
    
    /**
     * Removes the mapping for the specified key from this hash table if present.
     * 
     * Time Complexity: O(1) average case, O(n) worst case
     * 
     * @param key key whose mapping is to be removed from the map
     * @return the previous value associated with key, or null if there was no mapping
     */
    public V remove(K key) {
        int bucketIndex = hash(key);
        Node<K, V> head = buckets[bucketIndex];
        Node<K, V> prev = null;
        Node<K, V> current = head;
        
        // Search through the chain
        while (current != null) {
            if (keysEqual(current.key, key)) {
                // Found the key, remove node from chain
                if (prev == null) {
                    // Removing head of chain
                    buckets[bucketIndex] = current.next;
                } else {
                    // Removing from middle or end
                    prev.next = current.next;
                }
                size--;
                return current.value;
            }
            prev = current;
            current = current.next;
        }
        
        return null; // Key not found
    }
    
    /**
     * Returns true if this hash table contains a mapping for the specified key.
     * 
     * @param key key whose presence in this map is to be tested
     * @return true if this map contains a mapping for the specified key
     */
    public boolean containsKey(K key) {
        return get(key) != null;
    }
    
    /**
     * Returns the number of key-value mappings in this hash table.
     * 
     * @return the number of key-value mappings
     */
    public int size() {
        return size;
    }
    
    /**
     * Returns true if this hash table contains no key-value mappings.
     * 
     * @return true if this hash table contains no key-value mappings
     */
    public boolean isEmpty() {
        return size == 0;
    }
    
    /**
     * Removes all of the mappings from this hash table.
     */
    @SuppressWarnings("unchecked")
    public void clear() {
        buckets = (Node<K, V>[]) new Node[buckets.length];
        size = 0;
    }
    
    /**
     * Helper method to check if two keys are equal.
     * Handles null keys safely.
     */
    private boolean keysEqual(K key1, K key2) {
        if (key1 == key2) return true;
        if (key1 == null || key2 == null) return false;
        return key1.equals(key2);
    }
    
    /**
     * Resizes the hash table when load factor is exceeded.
     * Creates a new array with double the capacity and rehashes all entries.
     * 
     * This is an expensive operation (O(n)) but happens infrequently.
     * Amortized cost of put operations remains O(1).
     */
    @SuppressWarnings("unchecked")
    private void resize() {
        int newCapacity = buckets.length * 2;
        Node<K, V>[] oldBuckets = buckets;
        buckets = (Node<K, V>[]) new Node[newCapacity];
        size = 0;
        
        // Rehash all existing entries
        for (Node<K, V> head : oldBuckets) {
            while (head != null) {
                put(head.key, head.value);
                head = head.next;
            }
        }
    }
    
    /**
     * Returns a list of all keys in the hash table.
     * Useful for iteration and debugging.
     * 
     * @return a list containing all keys
     */
    public List<K> keys() {
        List<K> keys = new ArrayList<>(size);
        for (Node<K, V> head : buckets) {
            Node<K, V> current = head;
            while (current != null) {
                keys.add(current.key);
                current = current.next;
            }
        }
        return keys;
    }
    
    /**
     * Returns a list of all values in the hash table.
     * 
     * @return a list containing all values
     */
    public List<V> values() {
        List<V> values = new ArrayList<>(size);
        for (Node<K, V> head : buckets) {
            Node<K, V> current = head;
            while (current != null) {
                values.add(current.value);
                current = current.next;
            }
        }
        return values;
    }
    
    /**
     * Prints a visual representation of the internal bucket structure.
     * Shows how keys are distributed across buckets and chain lengths.
     * 
     * This helps understand load distribution and collision patterns.
     */
    public void printBucketStructure() {
        System.out.println("\n=== Hash Table Internal Structure ===");
        System.out.println("Capacity: " + buckets.length);
        System.out.println("Size: " + size);
        System.out.println("Load Factor: " + String.format("%.2f", (float) size / buckets.length));
        System.out.println("\nBucket Distribution:");
        
        int emptyBuckets = 0;
        int maxChainLength = 0;
        
        for (int i = 0; i < buckets.length; i++) {
            Node<K, V> current = buckets[i];
            if (current == null) {
                emptyBuckets++;
                continue;
            }
            
            System.out.print("Bucket[" + i + "]: ");
            int chainLength = 0;
            
            while (current != null) {
                System.out.print("[" + current.key + ":" + current.value + "]");
                if (current.next != null) {
                    System.out.print(" -> ");
                }
                current = current.next;
                chainLength++;
            }
            
            System.out.println(" (chain length: " + chainLength + ")");
            maxChainLength = Math.max(maxChainLength, chainLength);
        }
        
        System.out.println("\nStatistics:");
        System.out.println("Empty buckets: " + emptyBuckets + "/" + buckets.length);
        System.out.println("Max chain length: " + maxChainLength);
        System.out.println("Average chain length: " + 
            String.format("%.2f", (float) size / (buckets.length - emptyBuckets)));
        System.out.println("=====================================\n");
    }
    
    /**
     * Returns current capacity of the hash table.
     * 
     * @return the current capacity (number of buckets)
     */
    public int getCapacity() {
        return buckets.length;
    }
    
    /**
     * Returns the current load factor (size / capacity).
     * 
     * @return the current load factor
     */
    public float getCurrentLoadFactor() {
        return (float) size / buckets.length;
    }
}
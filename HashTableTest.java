/**
 * Test class to verify the correctness of SimpleHashTable implementation.
 * This demonstrates various test cases and edge conditions.
 */
public class HashTableTest {
    
    private static int testsPassed = 0;
    private static int totalTests = 0;
    
    public static void main(String[] args) {
        System.out.println("=== Hash Table Test Suite ===\n");
        
        // Run all tests
        testBasicOperations();
        testNullKeyValue();
        testCollisions();
        testResizing();
        testEdgeCases();
        testLargeScale();
        
        // Print summary
        System.out.println("\n=== Test Summary ===");
        System.out.println("Tests passed: " + testsPassed + "/" + totalTests);
        if (testsPassed == totalTests) {
            System.out.println("All tests PASSED! ✓");
        } else {
            System.out.println("Some tests FAILED! ✗");
        }
    }
    
    private static void testBasicOperations() {
        System.out.println("Testing basic operations...");
        SimpleHashTable<String, Integer> table = new SimpleHashTable<>();
        
        // Test empty table
        assertTrue("Empty table size should be 0", table.size() == 0);
        assertTrue("Empty table should be empty", table.isEmpty());
        assertNull("Get from empty table should return null", table.get("key"));
        
        // Test put and get
        assertNull("First put should return null", table.put("one", 1));
        assertEquals("Get should return inserted value", 1, table.get("one"));
        assertEquals("Size should be 1", 1, table.size());
        assertFalse("Table should not be empty", table.isEmpty());
        
        // Test update
        assertEquals("Update should return old value", 1, table.put("one", 100));
        assertEquals("Get should return updated value", 100, table.get("one"));
        assertEquals("Size should still be 1", 1, table.size());
        
        // Test multiple entries
        table.put("two", 2);
        table.put("three", 3);
        assertEquals("Size should be 3", 3, table.size());
        assertTrue("Should contain key 'two'", table.containsKey("two"));
        assertFalse("Should not contain key 'four'", table.containsKey("four"));
        
        // Test remove
        assertEquals("Remove should return value", 2, table.remove("two"));
        assertNull("Second remove should return null", table.remove("two"));
        assertEquals("Size should be 2", 2, table.size());
        assertFalse("Should not contain removed key", table.containsKey("two"));
        
        // Test clear
        table.clear();
        assertEquals("Size after clear should be 0", 0, table.size());
        assertTrue("Table should be empty after clear", table.isEmpty());
        
        System.out.println("Basic operations tests completed.\n");
    }
    
    private static void testNullKeyValue() {
        System.out.println("Testing null keys and values...");
        SimpleHashTable<String, String> table = new SimpleHashTable<>();
        
        // Test null key
        assertNull("Put null key should return null", table.put(null, "null-key-value"));
        assertEquals("Get null key should work", "null-key-value", table.get(null));
        assertTrue("Should contain null key", table.containsKey(null));
        
        // Test null value
        assertNull("Put null value should work", table.put("null-value-key", null));
        assertNull("Get should return null value", table.get("null-value-key"));
        
        // Update null key
        assertEquals("Update null key should return old value", 
                    "null-key-value", table.put(null, "new-null-value"));
        
        // Remove null key
        assertEquals("Remove null key should work", 
                    "new-null-value", table.remove(null));
        assertFalse("Should not contain removed null key", table.containsKey(null));
        
        System.out.println("Null key/value tests completed.\n");
    }
    
    private static void testCollisions() {
        System.out.println("Testing collision handling...");
        
        // Create keys that will collide in a small table
        class CollisionKey {
            String value;
            
            CollisionKey(String value) {
                this.value = value;
            }
            
            @Override
            public int hashCode() {
                // Force collision - all keys hash to same value
                return 42;
            }
            
            @Override
            public boolean equals(Object obj) {
                if (!(obj instanceof CollisionKey)) return false;
                return value.equals(((CollisionKey) obj).value);
            }
        }
        
        SimpleHashTable<CollisionKey, String> table = new SimpleHashTable<>(4, 2.0f);
        
        // Add multiple colliding keys
        CollisionKey k1 = new CollisionKey("A");
        CollisionKey k2 = new CollisionKey("B");
        CollisionKey k3 = new CollisionKey("C");
        
        table.put(k1, "Value A");
        table.put(k2, "Value B");
        table.put(k3, "Value C");
        
        // Verify all values are retrievable despite collisions
        assertEquals("Should get value A", "Value A", table.get(k1));
        assertEquals("Should get value B", "Value B", table.get(k2));
        assertEquals("Should get value C", "Value C", table.get(k3));
        
        // Remove middle element in chain
        assertEquals("Remove should work in chain", "Value B", table.remove(k2));
        assertNull("Should not find removed key", table.get(k2));
        assertEquals("Should still get value A", "Value A", table.get(k1));
        assertEquals("Should still get value C", "Value C", table.get(k3));
        
        System.out.println("Collision handling tests completed.\n");
    }
    
    private static void testResizing() {
        System.out.println("Testing dynamic resizing...");
        SimpleHashTable<Integer, String> table = new SimpleHashTable<>(2, 0.75f);
        
        int initialCapacity = table.getCapacity();
        assertEquals("Initial capacity should be 2", 2, initialCapacity);
        
        // Add elements to trigger resize
        table.put(1, "one");
        assertEquals("Capacity should still be 2", 2, table.getCapacity());
        
        table.put(2, "two"); // This should trigger resize (2 * 0.75 = 1.5)
        assertEquals("Capacity should double to 4", 4, table.getCapacity());
        
        // Verify data integrity after resize
        assertEquals("Should still have value 'one'", "one", table.get(1));
        assertEquals("Should still have value 'two'", "two", table.get(2));
        
        // Add more to trigger another resize
        table.put(3, "three");
        table.put(4, "four"); // Should trigger resize (4 * 0.75 = 3)
        assertEquals("Capacity should double to 8", 8, table.getCapacity());
        
        // Verify all data
        for (int i = 1; i <= 4; i++) {
            assertTrue("Should contain key " + i, table.containsKey(i));
        }
        
        System.out.println("Resizing tests completed.\n");
    }
    
    private static void testEdgeCases() {
        System.out.println("Testing edge cases...");
        
        // Test with single bucket
        SimpleHashTable<Integer, String> singleBucket = new SimpleHashTable<>(1, 10.0f);
        for (int i = 0; i < 5; i++) {
            singleBucket.put(i, "value" + i);
        }
        assertEquals("All elements should be in one chain", 5, singleBucket.size());
        assertEquals("Should still find elements", "value3", singleBucket.get(3));
        
        // Test remove non-existent key
        SimpleHashTable<String, String> table = new SimpleHashTable<>();
        assertNull("Remove non-existent should return null", table.remove("ghost"));
        
        // Test repeated puts
        table.put("key", "value1");
        table.put("key", "value2");
        table.put("key", "value3");
        assertEquals("Should have latest value", "value3", table.get("key"));
        assertEquals("Size should be 1", 1, table.size());
        
        System.out.println("Edge case tests completed.\n");
    }
    
    private static void testLargeScale() {
        System.out.println("Testing large-scale operations...");
        SimpleHashTable<Integer, Integer> table = new SimpleHashTable<>();
        
        int n = 10000;
        
        // Insert many elements
        for (int i = 0; i < n; i++) {
            table.put(i, i * i);
        }
        assertEquals("Size should be " + n, n, table.size());
        
        // Verify random samples
        for (int i = 0; i < 100; i++) {
            int key = (int) (Math.random() * n);
            assertEquals("Value should be square of key", key * key, (int) table.get(key));
        }
        
        // Remove half the elements
        for (int i = 0; i < n; i += 2) {
            table.remove(i);
        }
        assertEquals("Size should be " + (n/2), n/2, table.size());
        
        // Verify remaining elements
        for (int i = 1; i < n; i += 2) {
            assertEquals("Odd keys should remain", i * i, (int) table.get(i));
        }
        for (int i = 0; i < n; i += 2) {
            assertNull("Even keys should be removed", table.get(i));
        }
        
        System.out.println("Large-scale tests completed.\n");
    }
    
    // Helper assertion methods
    private static void assertTrue(String message, boolean condition) {
        totalTests++;
        if (condition) {
            testsPassed++;
            System.out.println("✓ " + message);
        } else {
            System.out.println("✗ " + message + " (FAILED)");
        }
    }
    
    private static void assertFalse(String message, boolean condition) {
        assertTrue(message, !condition);
    }
    
    private static void assertEquals(String message, Object expected, Object actual) {
        totalTests++;
        if ((expected == null && actual == null) || 
            (expected != null && expected.equals(actual))) {
            testsPassed++;
            System.out.println("✓ " + message);
        } else {
            System.out.println("✗ " + message + " (expected: " + expected + 
                             ", actual: " + actual + ")");
        }
    }
    
    private static void assertNull(String message, Object value) {
        assertEquals(message, null, value);
    }
}
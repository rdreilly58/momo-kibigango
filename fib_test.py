def fibonacci(n):
    """Generates the Fibonacci sequence up to n terms."""
    a, b = 0, 1
    sequence = []
    for i in range(n):
        sequence.append(a)
        a, b = b, a + b
    return sequence

if __name__ == "__main__":
    terms = 10
    result = fibonacci(terms)
    print(f"Fibonacci sequence up to {terms} terms: {result}")
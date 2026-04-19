# Makefile for BFS C++ Example
CXX = g++
CXXFLAGS = -std=c++11 -Wall -Wextra -pedantic -O2
TARGET = bfs_example

# Default target
all: $(TARGET)

# Build the executable
$(TARGET): bfs_example.cpp
	$(CXX) $(CXXFLAGS) -o $(TARGET) bfs_example.cpp

# Run the program
run: $(TARGET)
	./$(TARGET)

# Clean build artifacts
clean:
	rm -f $(TARGET)

# Compile with debug symbols
debug: CXXFLAGS += -g -DDEBUG
debug: clean $(TARGET)

.PHONY: all run clean debug
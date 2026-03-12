// Tests/PeachViewModelTests.swift
// Unit tests for PeachViewModel

import XCTest
@testable import Momotaro

class PeachViewModelTests: XCTestCase {
    var sut: PeachViewModel!
    var mockNetworkService: MockNetworkService!
    
    override func setUp() {
        super.setUp()
        mockNetworkService = MockNetworkService()
        sut = PeachViewModel(networkService: mockNetworkService)
    }
    
    override func tearDown() {
        sut = nil
        mockNetworkService = nil
        super.tearDown()
    }
    
    // MARK: - Loading Tests
    
    func testLoadPeachesSuccess() {
        // Arrange
        let testPeaches = [
            Peach(id: "1", name: "Golden", ripeness: 85, color: "orange"),
            Peach(id: "2", name: "Crimson", ripeness: 90, color: "red")
        ]
        mockNetworkService.peaches = testPeaches
        
        // Act
        sut.loadPeaches()
        
        // Assert
        XCTAssertEqual(sut.peaches.count, 2)
        XCTAssertEqual(sut.peaches[0].name, "Golden")
        XCTAssertNil(sut.errorMessage)
    }
    
    // MARK: - Sorting Tests
    
    func testSortPeachesByName() {
        // Arrange
        sut.peaches = [
            Peach(id: "1", name: "Zebra", ripeness: 85, color: "orange"),
            Peach(id: "2", name: "Apple", ripeness: 90, color: "red")
        ]
        
        // Act
        sut.sortByName()
        
        // Assert
        XCTAssertEqual(sut.peaches[0].name, "Apple")
        XCTAssertEqual(sut.peaches[1].name, "Zebra")
    }
    
    func testSortPeachesByRipeness() {
        // Arrange
        sut.peaches = [
            Peach(id: "1", name: "Golden", ripeness: 50, color: "orange"),
            Peach(id: "2", name: "Crimson", ripeness: 90, color: "red")
        ]
        
        // Act
        sut.sortByRipeness()
        
        // Assert
        XCTAssertEqual(sut.peaches[0].ripeness, 90)
        XCTAssertEqual(sut.peaches[1].ripeness, 50)
    }
    
    // MARK: - Filtering Tests
    
    func testFilterPeachesByName() {
        // Arrange
        sut.peaches = [
            Peach(id: "1", name: "Golden Delicious", ripeness: 85, color: "orange"),
            Peach(id: "2", name: "Crimson Peach", ripeness: 90, color: "red"),
            Peach(id: "3", name: "Yellow Sweet", ripeness: 75, color: "yellow")
        ]
        
        // Act
        sut.filterPeaches(with: "Golden")
        
        // Assert
        XCTAssertEqual(sut.filteredPeaches.count, 1)
        XCTAssertEqual(sut.filteredPeaches[0].name, "Golden Delicious")
    }
    
    func testFilterPeachesByColor() {
        // Arrange
        sut.peaches = [
            Peach(id: "1", name: "Golden", ripeness: 85, color: "orange"),
            Peach(id: "2", name: "Crimson", ripeness: 90, color: "red"),
            Peach(id: "3", name: "Sunny", ripeness: 75, color: "orange")
        ]
        
        // Act
        sut.filterPeaches(byColor: "orange")
        
        // Assert
        XCTAssertEqual(sut.filteredPeaches.count, 2)
        XCTAssertTrue(sut.filteredPeaches.allSatisfy { $0.color == "orange" })
    }
    
    func testFilterPeachesByRipenessRange() {
        // Arrange
        sut.peaches = [
            Peach(id: "1", name: "Golden", ripeness: 50, color: "orange"),
            Peach(id: "2", name: "Crimson", ripeness: 80, color: "red"),
            Peach(id: "3", name: "Ripe", ripeness: 95, color: "red")
        ]
        
        // Act
        sut.filterPeaches(minRipeness: 75, maxRipeness: 90)
        
        // Assert
        XCTAssertEqual(sut.filteredPeaches.count, 1)
        XCTAssertEqual(sut.filteredPeaches[0].name, "Crimson")
    }
    
    // MARK: - Statistics Tests
    
    func testAverageRipeness() {
        // Arrange
        sut.peaches = [
            Peach(id: "1", name: "Golden", ripeness: 60, color: "orange"),
            Peach(id: "2", name: "Crimson", ripeness: 80, color: "red"),
            Peach(id: "3", name: "Ripe", ripeness: 100, color: "red")
        ]
        
        // Act
        let average = sut.averageRipeness
        
        // Assert
        XCTAssertEqual(average, 80)
    }
    
    func testRipePeaches() {
        // Arrange
        sut.peaches = [
            Peach(id: "1", name: "Golden", ripeness: 60, color: "orange"),
            Peach(id: "2", name: "Crimson", ripeness: 80, color: "red"),
            Peach(id: "3", name: "Ripe", ripeness: 95, color: "red")
        ]
        
        // Act
        let ripePeaches = sut.ripePeaches(minRipeness: 80)
        
        // Assert
        XCTAssertEqual(ripePeaches.count, 2)
        XCTAssertTrue(ripePeaches.allSatisfy { $0.ripeness >= 80 })
    }
    
    func testCountByColor() {
        // Arrange
        sut.peaches = [
            Peach(id: "1", name: "Golden", ripeness: 85, color: "orange"),
            Peach(id: "2", name: "Crimson", ripeness: 90, color: "red"),
            Peach(id: "3", name: "Sunny", ripeness: 75, color: "orange")
        ]
        
        // Act
        let colorCount = sut.countByColor()
        
        // Assert
        XCTAssertEqual(colorCount["orange"], 2)
        XCTAssertEqual(colorCount["red"], 1)
    }
}

// MARK: - Mock NetworkService

class MockNetworkService: NetworkService {
    var peaches: [Peach] = []
    
    override func fetchPeaches(completion: @escaping (Result<[Peach], NetworkError>) -> Void) {
        DispatchQueue.main.async {
            completion(.success(self.peaches))
        }
    }
}

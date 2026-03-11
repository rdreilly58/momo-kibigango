// Tests/NetworkServiceTests.swift
// Unit tests for NetworkService with mock URLSession

import XCTest
@testable import Momotaro

class NetworkServiceTests: XCTestCase {
    var sut: NetworkService!
    var mockSession: MockURLSession!
    
    override func setUp() {
        super.setUp()
        mockSession = MockURLSession()
        sut = NetworkService(session: mockSession)
    }
    
    override func tearDown() {
        sut = nil
        mockSession = nil
        super.tearDown()
    }
    
    // MARK: - Success Cases
    
    func testFetchPeachesSuccess() {
        // Arrange
        let peaches = [
            Peach(id: "1", name: "Golden", ripeness: 85, color: "orange"),
            Peach(id: "2", name: "Crimson", ripeness: 90, color: "red")
        ]
        let data = try! JSONEncoder().encode(peaches)
        mockSession.data = data
        mockSession.response = HTTPURLResponse(url: URL(string: "https://api.peaches.com")!, statusCode: 200, httpVersion: nil, headerFields: nil)
        
        let expectation = self.expectation(description: "Fetch peaches")
        
        // Act
        sut.fetchPeaches { result in
            // Assert
            switch result {
            case .success(let fetchedPeaches):
                XCTAssertEqual(fetchedPeaches.count, 2)
                XCTAssertEqual(fetchedPeaches[0].name, "Golden")
                expectation.fulfill()
            case .failure:
                XCTFail("Expected success")
            }
        }
        
        waitForExpectations(timeout: 1.0)
    }
    
    // MARK: - Error Cases
    
    func testFetchPeachesNetworkError() {
        // Arrange
        mockSession.error = URLError(.networkConnectionLost)
        let expectation = self.expectation(description: "Network error")
        
        // Act
        sut.fetchPeaches { result in
            // Assert
            switch result {
            case .failure(let error):
                if case .requestFailed = error {
                    expectation.fulfill()
                } else {
                    XCTFail("Expected requestFailed error")
                }
            case .success:
                XCTFail("Expected failure")
            }
        }
        
        waitForExpectations(timeout: 1.0)
    }
    
    func testFetchPeachesServerError() {
        // Arrange
        mockSession.response = HTTPURLResponse(url: URL(string: "https://api.peaches.com")!, statusCode: 500, httpVersion: nil, headerFields: nil)
        let expectation = self.expectation(description: "Server error")
        
        // Act
        sut.fetchPeaches { result in
            // Assert
            switch result {
            case .failure(let error):
                if case .serverError(let code) = error {
                    XCTAssertEqual(code, 500)
                    expectation.fulfill()
                } else {
                    XCTFail("Expected serverError")
                }
            case .success:
                XCTFail("Expected failure")
            }
        }
        
        waitForExpectations(timeout: 1.0)
    }
    
    func testFetchPeachesDecodingError() {
        // Arrange
        mockSession.data = Data("{invalid json}".utf8)
        mockSession.response = HTTPURLResponse(url: URL(string: "https://api.peaches.com")!, statusCode: 200, httpVersion: nil, headerFields: nil)
        let expectation = self.expectation(description: "Decoding error")
        
        // Act
        sut.fetchPeaches { result in
            // Assert
            switch result {
            case .failure(let error):
                if case .decodingError = error {
                    expectation.fulfill()
                } else {
                    XCTFail("Expected decodingError")
                }
            case .success:
                XCTFail("Expected failure")
            }
        }
        
        waitForExpectations(timeout: 1.0)
    }
    
    func testFetchPeachesNoData() {
        // Arrange
        mockSession.data = nil
        mockSession.response = HTTPURLResponse(url: URL(string: "https://api.peaches.com")!, statusCode: 200, httpVersion: nil, headerFields: nil)
        let expectation = self.expectation(description: "No data error")
        
        // Act
        sut.fetchPeaches { result in
            // Assert
            switch result {
            case .failure(let error):
                if case .noData = error {
                    expectation.fulfill()
                } else {
                    XCTFail("Expected noData error")
                }
            case .success:
                XCTFail("Expected failure")
            }
        }
        
        waitForExpectations(timeout: 1.0)
    }
}

// MARK: - Mock URLSession

class MockURLSession: URLSession {
    var data: Data?
    var response: URLResponse?
    var error: URLError?
    
    override func dataTask(with request: URLRequest, completionHandler: @escaping (Data?, URLResponse?, Error?) -> Void) -> URLSessionDataTask {
        let task = MockURLSessionDataTask {
            completionHandler(self.data, self.response, self.error)
        }
        return task
    }
}

class MockURLSessionDataTask: URLSessionDataTask {
    private let closure: () -> Void
    
    init(closure: @escaping () -> Void) {
        self.closure = closure
    }
    
    override func resume() {
        closure()
    }
}

// Services/NetworkService.swift
// Centralized network service with proper error handling and Result type

import Foundation

/// Enumeration for network-related errors
enum NetworkError: Error, LocalizedError {
    case badURL
    case requestFailed(URLError)
    case decodingError(DecodingError)
    case serverError(statusCode: Int)
    case noData
    
    var errorDescription: String? {
        switch self {
        case .badURL:
            return "The URL is invalid or malformed."
        case .requestFailed(let error):
            return "Network request failed: \(error.localizedDescription)"
        case .decodingError:
            return "Failed to decode response data."
        case .serverError(let code):
            return "Server error: HTTP \(code)"
        case .noData:
            return "No data received from server."
        }
    }
}

/// Service responsible for network requests
struct NetworkService {
    private let baseURL: String
    private let session: URLSession
    
    init(baseURL: String = "https://api.peaches.com", session: URLSession = URLSession.shared) {
        self.baseURL = baseURL
        self.session = session
    }
    
    /// Fetch peaches from the server
    /// - Parameter completion: Closure called with Result<[Peach], NetworkError>
    func fetchPeaches(completion: @escaping (Result<[Peach], NetworkError>) -> Void) {
        let endpoint = "/peaches"
        guard let url = URL(string: baseURL + endpoint) else {
            completion(.failure(.badURL))
            return
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        session.dataTask(with: request) { data, response, error in
            // Handle network errors
            if let error = error as? URLError {
                completion(.failure(.requestFailed(error)))
                return
            }
            
            // Check HTTP status
            if let httpResponse = response as? HTTPURLResponse {
                guard (200...299).contains(httpResponse.statusCode) else {
                    completion(.failure(.serverError(statusCode: httpResponse.statusCode)))
                    return
                }
            }
            
            // Verify data exists
            guard let data = data else {
                completion(.failure(.noData))
                return
            }
            
            // Decode JSON
            do {
                let decoder = JSONDecoder()
                decoder.dateDecodingStrategy = .iso8601
                let peaches = try decoder.decode([Peach].self, from: data)
                completion(.success(peaches))
            } catch let error as DecodingError {
                completion(.failure(.decodingError(error)))
            } catch {
                completion(.failure(.decodingError(DecodingError.dataCorrupted(.init(codingPath: [], debugDescription: error.localizedDescription)))))
            }
        }.resume()
    }
    
    /// Fetch a single peach by ID
    func fetchPeach(id: String, completion: @escaping (Result<Peach, NetworkError>) -> Void) {
        let endpoint = "/peaches/\(id)"
        guard let url = URL(string: baseURL + endpoint) else {
            completion(.failure(.badURL))
            return
        }
        
        session.dataTask(with: url) { data, response, error in
            if let error = error as? URLError {
                completion(.failure(.requestFailed(error)))
                return
            }
            
            guard let data = data else {
                completion(.failure(.noData))
                return
            }
            
            do {
                let peach = try JSONDecoder().decode(Peach.self, from: data)
                completion(.success(peach))
            } catch let error as DecodingError {
                completion(.failure(.decodingError(error)))
            } catch {
                completion(.failure(.decodingError(DecodingError.dataCorrupted(.init(codingPath: [], debugDescription: error.localizedDescription)))))
            }
        }.resume()
    }
}

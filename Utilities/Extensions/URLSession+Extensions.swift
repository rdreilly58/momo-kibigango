// Utilities/Extensions/URLSession+Extensions.swift
// URLSession utility extensions

import Foundation

extension URLSession {
    /// Execute a data task with result type
    func dataTask<T: Decodable>(
        with url: URL,
        completionHandler: @escaping (Result<T, Error>) -> Void
    ) -> URLSessionDataTask {
        return dataTask(with: url) { data, response, error in
            if let error = error {
                completionHandler(.failure(error))
                return
            }
            
            guard let data = data else {
                completionHandler(.failure(URLError(.badServerResponse)))
                return
            }
            
            do {
                let decoded = try JSONDecoder().decode(T.self, from: data)
                completionHandler(.success(decoded))
            } catch {
                completionHandler(.failure(error))
            }
        }
    }
    
    /// Execute a request with result type
    func request<T: Decodable>(
        _ request: URLRequest,
        completionHandler: @escaping (Result<T, Error>) -> Void
    ) -> URLSessionDataTask {
        return dataTask(with: request) { data, response, error in
            if let error = error {
                completionHandler(.failure(error))
                return
            }
            
            guard let data = data else {
                completionHandler(.failure(URLError(.badServerResponse)))
                return
            }
            
            do {
                let decoded = try JSONDecoder().decode(T.self, from: data)
                completionHandler(.success(decoded))
            } catch {
                completionHandler(.failure(error))
            }
        }
    }
}

import Foundation

class APIManager {
    static let shared = APIManager()
    
    private var baseURL: String = "https://api.onigashima.app"
    
    func setBaseURL(_ url: String) {
        baseURL = url
    }
    
    func registerDevice(name: String, type: String, pairingCode: String) async throws -> DeviceRegistration {
        guard let url = URL(string: "\(baseURL)/devices/register") else {
            throw APIError.invalidURL
        }
        
        let payload = RegisterDeviceRequest(
            deviceName: name,
            deviceType: type,
            pairingCode: pairingCode
        )
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(payload)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw APIError.invalidResponse
        }
        
        return try JSONDecoder().decode(DeviceRegistration.self, from: data)
    }
    
    func verifyPairing(deviceID: String, token: String) async throws -> Bool {
        guard let url = URL(string: "\(baseURL)/devices/\(deviceID)/verify-pairing") else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        let (_, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw APIError.invalidResponse
        }
        
        return true
    }
}

struct RegisterDeviceRequest: Codable {
    let deviceName: String
    let deviceType: String
    let pairingCode: String
}

struct DeviceRegistration: Codable {
    let deviceID: String
    let token: String
    let apiEndpoint: String
}

enum APIError: Error {
    case invalidURL
    case invalidResponse
    case decodingError
    case networkError(Error)
}


import Foundation

class GatewayClient: ObservableObject {
    @Published var isConnected: Bool = false
    @Published var errorMessage: String? = nil
    
    private var webSocketTask: URLSessionWebSocketTask?
    private var backoffAttempts: Int = 0
    private let maxBackoffAttempts = 5
    private let url: URL
    
    init(url: URL) {
        self.url = url
        connect()
    }
    
    func connect() {
        let session = URLSession(configuration: .default)
        webSocketTask = session.webSocketTask(with: url)
        webSocketTask?.resume()
        isConnected = true
        listenForMessages()
    }
    
    func disconnect() {
        webSocketTask?.cancel(with: .goingAway, reason: nil)
        isConnected = false
    }
    
    func listenForMessages() {
        webSocketTask?.receive { [weak self] result in
            switch result {
            case .success(let message):
                switch message {
                case .data(let data):
                    self?.handleData(data)
                case .string(let text):
                    print("Received string: \(text)")
                @unknown default:
                    break
                }
                self?.listenForMessages()
            case .failure(let error):
                self?.errorMessage = "Connection error: \(error)"
                self?.isConnected = false
                self?.attemptReconnect()
            }
        }
    }
    
    private func handleData(_ data: Data) {
        // Handle incoming data
    }
    
    private func attemptReconnect() {
        guard backoffAttempts < maxBackoffAttempts else { return }
        backoffAttempts += 1
        let delay = Double(backoffAttempts * backoffAttempts)
        DispatchQueue.main.asyncAfter(deadline: .now() + delay) { [weak self] in
            self?.connect()
        }
    }
    
    func send(message: String) {
        let message = URLSessionWebSocketTask.Message.string(message)
        webSocketTask?.send(message) { [weak self] error in
            if let error = error {
                self?.errorMessage = "Send error: \(error)"
            }
        }
    }
}

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
        log.info("GatewayClient initialized", ["url": url.absoluteString])
        connect()
    }
    
    func connect() {
        log.info("Attempting WebSocket connection", [
            "url": url.absoluteString,
            "attempt": backoffAttempts
        ])
        
        let session = URLSession(configuration: .default)
        webSocketTask = session.webSocketTask(with: url)
        webSocketTask?.resume()
        isConnected = true
        
        log.info("✅ WebSocket connected")
        listenForMessages()
    }
    
    func disconnect() {
        log.info("Disconnecting from WebSocket")
        webSocketTask?.cancel(with: .goingAway, reason: nil)
        isConnected = false
    }
    
    func listenForMessages() {
        webSocketTask?.receive { [weak self] result in
            switch result {
            case .success(let message):
                switch message {
                case .data(let data):
                    self?.log.info("Received data", ["bytes": data.count])
                    self?.handleData(data)
                case .string(let text):
                    self?.log.info("Received string", ["length": text.count])
                @unknown default:
                    break
                }
                self?.listenForMessages()
            case .failure(let error):
                let errorMsg = "❌ Connection error: \(error.localizedDescription)"
                self?.log.error(errorMsg, error)
                self?.errorMessage = errorMsg
                self?.isConnected = false
                self?.attemptReconnect()
            }
        }
    }
    
    private func handleData(_ data: Data) {
        // Handle incoming data
    }
    
    private func attemptReconnect() {
        guard backoffAttempts < maxBackoffAttempts else {
            log.warning("Max reconnection attempts reached")
            return
        }
        backoffAttempts += 1
        let delay = Double(backoffAttempts * backoffAttempts)
        log.warning("Attempting reconnect", [
            "attempt": backoffAttempts,
            "delay_seconds": delay
        ])
        
        DispatchQueue.main.asyncAfter(deadline: .now() + delay) { [weak self] in
            self?.connect()
        }
    }
    
    func send(message: String) {
        guard isConnected else {
            log.warning("Send attempted while disconnected", ["message_length": message.count])
            return
        }
        
        let wsMessage = URLSessionWebSocketTask.Message.string(message)
        webSocketTask?.send(wsMessage) { [weak self] error in
            if let error = error {
                self?.log.error("Send failed", error)
                self?.errorMessage = "Send error: \(error.localizedDescription)"
            } else {
                self?.log.info("Message sent", ["length": message.count])
            }
        }
    }
}

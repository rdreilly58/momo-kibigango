// Services/WebSocketManager.swift
// WebSocket connection manager for OpenClaw gateway with automatic reconnection

import Foundation

/// Connection state for WebSocket
enum ConnectionState: Equatable {
    case disconnected
    case connecting
    case connected
    case error(String)
    case reconnecting(attempt: Int)
}

/// Manages WebSocket connections to OpenClaw gateway
class WebSocketManager: NSObject, ObservableObject, URLSessionWebSocketDelegate {
    @Published var connectionState: ConnectionState = .disconnected
    @Published var lastMessage: GatewayMessage?
    
    private var webSocketTask: URLSessionWebSocketTask?
    private var reconnectAttempts = 0
    private let maxReconnectAttempts = 5
    private let baseReconnectDelay: TimeInterval = 2.0
    private var reconnectTimer: Timer?
    private let queue = DispatchQueue(label: "com.momotaro.websocket", attributes: .concurrent)
    
    private let gatewayURL: URL
    
    init(gatewayURL: URL = URL(string: "wss://gateway.openclaw.local/ws")!) {
        self.gatewayURL = gatewayURL
        super.init()
    }
    
    /// Connect to the WebSocket gateway
    func connect() {
        queue.async(flags: .barrier) { [weak self] in
            guard self?.webSocketTask == nil else { return }
            
            DispatchQueue.main.async { [weak self] in
                self?.connectionState = .connecting
            }
            
            let session = URLSession(configuration: .default, delegate: self, delegateQueue: OperationQueue())
            let task = session.webSocketTask(with: self.gatewayURL)
            self?.webSocketTask = task
            task.resume()
            
            self?.resetReconnectCounter()
            self?.receiveMessage()
        }
    }
    
    /// Disconnect from the WebSocket gateway
    func disconnect() {
        queue.async(flags: .barrier) { [weak self] in
            self?.reconnectTimer?.invalidate()
            self?.reconnectTimer = nil
            self?.webSocketTask?.cancel(with: .goingAway, reason: nil)
            self?.webSocketTask = nil
            
            DispatchQueue.main.async { [weak self] in
                self?.connectionState = .disconnected
            }
        }
    }
    
    /// Send a message through the WebSocket
    func send(_ message: GatewayMessage) {
        queue.async { [weak self] in
            guard let self = self, self.webSocketTask != nil else { return }
            
            do {
                let encoder = JSONEncoder()
                encoder.dateEncodingStrategy = .iso8601
                let data = try encoder.encode(message)
                let message = URLSessionWebSocketTask.Message.data(data)
                
                self.webSocketTask?.send(message) { [weak self] error in
                    if let error = error {
                        self?.handleError("Failed to send message: \(error.localizedDescription)")
                    }
                }
            } catch {
                self.handleError("Failed to encode message: \(error.localizedDescription)")
            }
        }
    }
    
    /// Receive messages from the WebSocket
    private func receiveMessage() {
        queue.async { [weak self] in
            guard let self = self, let task = self.webSocketTask else { return }
            
            task.receive { [weak self] result in
                switch result {
                case .success(let message):
                    self?.handleMessage(message)
                    self?.receiveMessage() // Continue listening
                    
                case .failure(let error):
                    self?.handleError("WebSocket error: \(error.localizedDescription)")
                }
            }
        }
    }
    
    /// Handle incoming WebSocket message
    private func handleMessage(_ message: URLSessionWebSocketTask.Message) {
        switch message {
        case .data(let data):
            do {
                let decoder = JSONDecoder()
                decoder.dateDecodingStrategy = .iso8601
                let gatewayMessage = try decoder.decode(GatewayMessage.self, from: data)
                
                DispatchQueue.main.async { [weak self] in
                    self?.lastMessage = gatewayMessage
                }
            } catch {
                handleError("Failed to decode message: \(error.localizedDescription)")
            }
            
        case .string(let text):
            print("Received text message: \(text)")
            
        @unknown default:
            break
        }
    }
    
    /// Handle connection errors with automatic reconnection
    private func handleError(_ errorMessage: String) {
        DispatchQueue.main.async { [weak self] in
            self?.connectionState = .error(errorMessage)
            self?.attemptReconnection()
        }
    }
    
    /// Attempt to reconnect with exponential backoff
    private func attemptReconnection() {
        guard reconnectAttempts < maxReconnectAttempts else {
            DispatchQueue.main.async { [weak self] in
                self?.connectionState = .error("Max reconnection attempts reached")
            }
            return
        }
        
        reconnectAttempts += 1
        let delay = baseReconnectDelay * pow(2.0, Double(reconnectAttempts - 1))
        
        DispatchQueue.main.async { [weak self] in
            self?.connectionState = .reconnecting(attempt: self?.reconnectAttempts ?? 0)
        }
        
        reconnectTimer = Timer.scheduledTimer(withTimeInterval: delay, repeats: false) { [weak self] _ in
            self?.connect()
        }
    }
    
    /// Reset the reconnection counter
    private func resetReconnectCounter() {
        queue.async(flags: .barrier) { [weak self] in
            self?.reconnectAttempts = 0
        }
    }
    
    // MARK: - URLSessionWebSocketDelegate
    
    func urlSession(_ session: URLSession, webSocketTask: URLSessionWebSocketTask, didOpenWithProtocol protocol: String?) {
        DispatchQueue.main.async { [weak self] in
            self?.connectionState = .connected
        }
    }
    
    func urlSession(_ session: URLSession, webSocketTask: URLSessionWebSocketTask, didCloseWith closeCode: URLSessionWebSocketTask.CloseCode, reason: Data?) {
        DispatchQueue.main.async { [weak self] in
            self?.connectionState = .disconnected
        }
    }
}

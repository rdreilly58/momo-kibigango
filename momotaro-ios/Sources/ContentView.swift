import SwiftUI

struct ContentView: View {
    @StateObject private var gatewayClient = GatewayClient(url: URL(string: "ws://localhost:8080")!)
    @State private var messageToSend: String = ""
    
    var body: some View {
        VStack {
            connectionStatus
            messageInput
            Spacer()
            if let error = gatewayClient.errorMessage {
                Text("Error: \(error)").foregroundColor(.red)
            }
        }
        .padding()
    }
    
    private var connectionStatus: some View {
        HStack {
            Text(gatewayClient.isConnected ? "Connected" : "Disconnected")
                .foregroundColor(gatewayClient.isConnected ? .green : .red)
            Button(action: {
                if gatewayClient.isConnected {
                    gatewayClient.disconnect()
                } else {
                    gatewayClient.connect()
                }
            }) {
                Text(gatewayClient.isConnected ? "Disconnect" : "Connect")
            }
            .padding(.leading)
        }
    }
    
    private var messageInput: some View {
        HStack {
            TextField("Message", text: $messageToSend)
            Button("Send") {
                gatewayClient.send(message: messageToSend)
                messageToSend = ""
            }
            .padding(.leading)
        }
    }
}

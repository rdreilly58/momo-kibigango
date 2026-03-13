import SwiftUI

struct PairingView: View {
    @State private var currentStep: PairingStep = .scanner
    @State private var scannedCode = ""
    @State private var showError = false
    @State private var errorMessage = ""
    @State private var isLoading = false
    
    enum PairingStep {
        case scanner
        case registering
        case success
        case error
    }
    
    var body: some View {
        ZStack {
            switch currentStep {
            case .scanner:
                ScannerView(onScanned: handleScannedCode)
                
            case .registering:
                VStack(spacing: 20) {
                    ProgressView()
                    Text("Registering device...")
                        .foregroundColor(.gray)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(Color(.systemBackground))
                
            case .success:
                VStack(spacing: 20) {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 60))
                        .foregroundColor(.green)
                    
                    Text("Pairing Successful!")
                        .font(.headline)
                    
                    Text("Your iPhone is now paired with your Mac.")
                        .foregroundColor(.gray)
                    
                    Button(action: { currentStep = .scanner }) {
                        Text("Done")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                }
                .padding(40)
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(Color(.systemBackground))
                
            case .error:
                VStack(spacing: 20) {
                    Image(systemName: "exclamationmark.circle.fill")
                        .font(.system(size: 60))
                        .foregroundColor(.red)
                    
                    Text("Pairing Failed")
                        .font(.headline)
                    
                    Text(errorMessage)
                        .foregroundColor(.gray)
                        .multilineTextAlignment(.center)
                    
                    Button(action: { currentStep = .scanner }) {
                        Text("Try Again")
                            .frame(maxWidth: .infinity)
                    }
                    .buttonStyle(.borderedProminent)
                }
                .padding(40)
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(Color(.systemBackground))
            }
        }
        .alert("Error", isPresented: $showError) {
            Button("OK") { showError = false }
        } message: {
            Text(errorMessage)
        }
    }
    
    private func handleScannedCode(_ code: String) {
        scannedCode = code
        currentStep = .registering
        performPairing(with: code)
    }
    
    private func performPairing(with code: String) {
        Task {
            do {
                let registration = try await APIManager.shared.registerDevice(
                    name: UIDevice.current.name,
                    type: "iphone",
                    pairingCode: code
                )
                
                // Save credentials securely
                KeychainManager.shared.saveToken(registration.token, forKey: "jwtToken")
                KeychainManager.shared.saveToken(registration.deviceID, forKey: "deviceID")
                KeychainManager.shared.saveToken(registration.apiEndpoint, forKey: "apiEndpoint")
                
                // Verify pairing
                let verified = try await APIManager.shared.verifyPairing(
                    deviceID: registration.deviceID,
                    token: registration.token
                )
                
                if verified {
                    currentStep = .success
                } else {
                    throw APIError.invalidResponse
                }
            } catch {
                errorMessage = error.localizedDescription
                currentStep = .error
            }
        }
    }
}

#Preview {
    PairingView()
}

import SwiftUI
import AVFoundation

struct ScannerView: View {
    @StateObject private var scanner = QRCodeScanner()
    @State private var scannedCode: String = ""
    @State private var showError = false
    @State private var errorMessage = ""
    @State private var isProcessing = false
    
    var onScanned: (String) -> Void
    
    var body: some View {
        ZStack {
            // Camera preview
            ScannerPreview(session: scanner.session)
                .ignoresSafeArea()
            
            // Scanning overlay
            VStack {
                Text("Scan QR Code")
                    .font(.headline)
                    .foregroundColor(.white)
                    .padding()
                
                Spacer()
                
                // Scanning frame
                RoundedRectangle(cornerRadius: 12)
                    .stroke(Color.green, lineWidth: 2)
                    .frame(width: 250, height: 250)
                
                Spacer()
                
                Text("Position QR code in frame")
                    .font(.caption)
                    .foregroundColor(.white.opacity(0.7))
                    .padding()
            }
            .padding()
            
            // Loading indicator
            if isProcessing {
                ProgressView()
                    .tint(.white)
            }
        }
        .onAppear {
            scanner.startScanning()
        }
        .onDisappear {
            scanner.stopScanning()
        }
        .onChange(of: scanner.scannedCode) { newCode in
            if !newCode.isEmpty {
                isProcessing = true
                scannedCode = newCode
                onScanned(newCode)
            }
        }
        .alert("Error", isPresented: $showError) {
            Button("OK") { 
                showError = false
                scanner.startScanning()
            }
        } message: {
            Text(errorMessage)
        }
    }
}

struct ScannerPreview: UIViewRepresentable {
    var session: AVCaptureSession
    
    func makeUIView(context: Context) -> UIView {
        let view = UIView(frame: .zero)
        let previewLayer = AVCaptureVideoPreviewLayer(session: session)
        previewLayer.frame = view.bounds
        previewLayer.videoGravity = .resizeAspectFill
        view.layer.addSublayer(previewLayer)
        return view
    }
    
    func updateUIView(_ uiView: UIView, context: Context) {}
}

class QRCodeScanner: NSObject, ObservableObject, AVCaptureMetadataOutputObjectsDelegate {
    @Published var scannedCode = ""
    let session = AVCaptureSession()
    
    override init() {
        super.init()
        setupCamera()
    }
    
    func setupCamera() {
        guard let videoCaptureDevice = AVCaptureDevice.default(for: .video) else { return }
        
        do {
            let videoInput = try AVCaptureDeviceInput(device: videoCaptureDevice)
            if session.canAddInput(videoInput) {
                session.addInput(videoInput)
            }
            
            let metadataOutput = AVCaptureMetadataOutput()
            if session.canAddOutput(metadataOutput) {
                session.addOutput(metadataOutput)
                metadataOutput.setMetadataObjectsDelegate(self, queue: DispatchQueue.main)
                metadataOutput.metadataObjectTypes = [.qr]
            }
        } catch {
            print("Camera setup error: \(error)")
        }
    }
    
    func startScanning() {
        DispatchQueue.global(qos: .userInitiated).async {
            self.session.startRunning()
        }
    }
    
    func stopScanning() {
        session.stopRunning()
    }
    
    func metadataOutput(_ output: AVCaptureMetadataOutput, 
                       didOutput metadataObjects: [AVMetadataObject], 
                       from connection: AVCaptureConnection) {
        for metadata in metadataObjects {
            if let machineReadableCode = metadata as? AVMetadataMachineReadableCodeObject,
               machineReadableCode.type == .qr,
               let stringValue = machineReadableCode.stringValue {
                scannedCode = stringValue
            }
        }
    }
}

#Preview {
    ScannerView(onScanned: { _ in })
}

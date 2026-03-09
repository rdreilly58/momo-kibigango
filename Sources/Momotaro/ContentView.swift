import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack {
            Text("🍑")
                .font(.system(size: 60))
            
            Text("Momotaro")
                .font(.title)
            
            Text("OpenClaw iOS Client")
                .font(.caption)
                .foregroundStyle(.secondary)
            
            Spacer()
            
            Button(action: {}) {
                Text("Connect to Gateway")
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(.blue)
                    .foregroundStyle(.white)
                    .cornerRadius(8)
            }
            .padding()
        }
        .padding()
    }
}

#Preview {
    ContentView()
}

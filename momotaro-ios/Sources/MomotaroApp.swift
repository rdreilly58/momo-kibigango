import SwiftUI

@main
struct MomotaroApp: App {
    init() {
        log.info("🍑 Momotaro-iOS launching")
        FirebaseConfig.configure()
    }
    
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

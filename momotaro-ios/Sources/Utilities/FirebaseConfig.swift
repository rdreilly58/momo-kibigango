import Foundation

#if os(iOS)
import FirebaseCore
import FirebaseCrashlytics

class FirebaseConfig {
  static func configure() {
    log.info("🔥 Initializing Firebase")
    
    // Firebase will auto-initialize using GoogleService-Info.plist
    FirebaseApp.configure()
    
    log.info("✅ Firebase configured successfully")
    
    // Set user ID for Crashlytics (optional - for better crash grouping)
    // Crashlytics.crashlytics().setUserID("user_id")
  }
}

// Initialize on app launch via MomotaroApp.swift
#endif

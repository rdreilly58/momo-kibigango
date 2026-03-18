import Foundation
import os

class AppLogger {
  static let shared = AppLogger()

  private let logger = Logger(subsystem: "com.momotaro.ios", category: "App")

  enum LogLevel {
    case debug
    case info
    case warning
    case error
  }

  func log(
    level: LogLevel,
    _ message: String,
    context: [String: Any] = [:]
  ) {
    let contextStr = context.isEmpty ? "" : " | \(context)"
    let timestamp = ISO8601DateFormatter().string(from: Date())
    let logMessage = "[\(timestamp)] [\(level)] \(message)\(contextStr)"

    switch level {
    case .debug:
      logger.debug("\(logMessage)")
    case .info:
      logger.info("\(logMessage)")
    case .warning:
      logger.warning("\(logMessage)")
    case .error:
      logger.error("\(logMessage)")
    }
  }

  func debug(_ message: String, _ context: [String: Any] = [:]) {
    log(level: .debug, message, context: context)
  }

  func info(_ message: String, _ context: [String: Any] = [:]) {
    log(level: .info, message, context: context)
  }

  func warning(_ message: String, _ context: [String: Any] = [:]) {
    log(level: .warning, message, context: context)
  }

  func error(_ message: String, _ error: Error? = nil, _ context: [String: Any] = [:]) {
    var fullContext = context
    if let error = error {
      fullContext["error"] = error.localizedDescription
    }
    log(level: .error, message, context: fullContext)
  }
}

let log = AppLogger.shared

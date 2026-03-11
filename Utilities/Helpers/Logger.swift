// Utilities/Helpers/Logger.swift
// Centralized logging utility

import Foundation
import os.log

/// Centralized logging service
class Logger {
    static let shared = Logger()
    
    private let osLog = OSLog(subsystem: "com.momotaro.app", category: "General")
    
    // MARK: - Log Levels
    
    enum LogLevel: String {
        case debug = "🔍 DEBUG"
        case info = "ℹ️ INFO"
        case warning = "⚠️ WARNING"
        case error = "❌ ERROR"
    }
    
    // MARK: - Logging Methods
    
    /// Log debug message
    static func debug(_ message: String, file: String = #file, function: String = #function, line: Int = #line) {
        log(message, level: .debug, file: file, function: function, line: line)
    }
    
    /// Log info message
    static func info(_ message: String, file: String = #file, function: String = #function, line: Int = #line) {
        log(message, level: .info, file: file, function: function, line: line)
    }
    
    /// Log warning message
    static func warning(_ message: String, file: String = #file, function: String = #function, line: Int = #line) {
        log(message, level: .warning, file: file, function: function, line: line)
    }
    
    /// Log error message
    static func error(_ message: String, file: String = #file, function: String = #function, line: Int = #line) {
        log(message, level: .error, file: file, function: function, line: line)
    }
    
    /// Log with custom level
    private static func log(
        _ message: String,
        level: LogLevel,
        file: String,
        function: String,
        line: Int
    ) {
        let fileName = URL(fileURLWithPath: file).lastPathComponent
        let logMessage = "[\(level.rawValue)] \(fileName):\(line) \(function) - \(message)"
        
        #if DEBUG
        print(logMessage)
        #endif
        
        os_log("%@", log: Logger.shared.osLog, type: mapLogType(level), logMessage as NSString)
    }
    
    /// Map logger level to OSLogType
    private static func mapLogType(_ level: LogLevel) -> OSLogType {
        switch level {
        case .debug:
            return .debug
        case .info:
            return .info
        case .warning:
            return .default
        case .error:
            return .error
        }
    }
}

// MARK: - Convenience Functions

func logDebug(_ message: String) {
    Logger.debug(message)
}

func logInfo(_ message: String) {
    Logger.info(message)
}

func logWarning(_ message: String) {
    Logger.warning(message)
}

func logError(_ message: String) {
    Logger.error(message)
}

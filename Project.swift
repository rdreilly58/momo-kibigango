// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "Momotaro",
    platforms: [
        .iOS(.v17)
    ],
    products: [
        .library(
            name: "Momotaro",
            targets: ["Momotaro"]
        )
    ],
    dependencies: [
        // Essential dependencies for OpenClaw integration
        .package(url: "https://github.com/daltoniam/Starscream.git", from: "4.0.0"), // WebSocket
        .package(url: "https://github.com/apple/swift-crypto.git", from: "3.0.0"), // Ed25519 auth
        .package(url: "https://github.com/stephencelis/SQLite.swift.git", from: "0.14.1") // Local storage
    ],
    targets: [
        .target(
            name: "Momotaro",
            dependencies: [
                "Starscream",
                .product(name: "Crypto", package: "swift-crypto"),
                .product(name: "SQLite", package: "SQLite.swift")
            ],
            path: "Sources"
        ),
        .testTarget(
            name: "MomotaroTests",
            dependencies: ["Momotaro"],
            path: "Tests"
        )
    ]
)
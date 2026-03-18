import ProjectDescription

let project = Project(
    name: "Momotaro-iOS",
    targets: [
        .target(
            name: "Momotaro-iOS",
            destinations: .iOS,
            product: .app,
            bundleId: "com.momotaro.ios",
            deploymentTargets: .iOS("17.0"),
            infoPlist: .file(path: "Info.plist"),
            sources: ["Sources/**"],
            resources: ["Resources/**", "Assets.xcassets/**", "GoogleService-Info.plist"]
        ),
        .target(
            name: "Momotaro-iOSTests",
            destinations: .iOS,
            product: .unitTests,
            bundleId: "com.momotaro.ios.tests",
            infoPlist: .default,
            sources: ["Tests/**"],
            dependencies: [
                .target(name: "Momotaro-iOS")
            ]
        ),
    ]
)

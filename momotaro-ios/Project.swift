import ProjectDescription

let project = Project(
    name: "Momotaro-iOS",
    targets: [
        .init(
            name: "Momotaro-iOS",
            platform: .iOS,
            product: .app,
            bundleId: "com.momotaro.ios",
            deploymentTarget: .iOS(targetVersion: "17.0", devices: .iphone),
            infoPlist: "Info.plist",
            sources: ["Sources/**"],
            resources: ["Resources/**"],
            dependencies: []
        ),
        .init(
            name: "Momotaro-iOSTests",
            platform: .iOS,
            product: .unitTests,
            bundleId: "com.momotaro.ios.tests",
            deploymentTarget: .iOS(targetVersion: "17.0", devices: .iphone),
            infoPlist: .default,
            sources: ["Tests/**"],
            dependencies: [
                .target(name: "Momotaro-iOS")
            ]
        ),
    ]
)

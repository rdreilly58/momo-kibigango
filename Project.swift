import ProjectDescription

let project = Project(
    name: "Momotaro",
    targets: [
        .target(
            name: "Momotaro",
            destinations: .iOS,
            product: .app,
            bundleId: "com.reillydesign.momotaro",
            infoPlist: .extendingDefault(with: [
                "UIMainStoryboardFile": "",
                "UILaunchScreen": [:]
            ]),
            sources: ["Sources/**"],
            resources: ["Resources/**"]
        ),
        .target(
            name: "MomotaroTests",
            destinations: .iOS,
            product: .unitTests,
            bundleId: "com.reillydesign.momotaro.tests",
            infoPlist: .default,
            sources: ["Tests/**"],
            dependencies: [
                .target(name: "Momotaro")
            ]
        )
    ]
)

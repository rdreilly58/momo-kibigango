#!/bin/bash
# xcode-build.sh — Build and manage iOS projects with Xcode
#
# Usage:
#   xcode-build.sh [PROJECT_PATH] [OPTIONS]
#   xcode-build.sh --list                    # List available schemes
#   xcode-build.sh build [--scheme NAME]     # Build for iOS
#   xcode-build.sh archive [--scheme NAME]   # Create iOS archive for export
#   xcode-build.sh test [--scheme NAME]      # Run unit tests
#   xcode-build.sh clean                     # Clean build folder
#   xcode-build.sh open                      # Open in Xcode
#   xcode-build.sh simulator [--device NAME] # Build and run on simulator
#   xcode-build.sh help

set -euo pipefail

PROJECT_PATH="${1:-.}"
COMMAND="${2:-help}"
SCHEME=""
DEVICE="iPhone 16"
CONFIGURATION="Debug"
SDK="iphoneos"

while [[ $# -gt 0 ]]; do
  case $1 in
    --scheme)
      SCHEME="$2"
      shift 2
      ;;
    --device)
      DEVICE="$2"
      shift 2
      ;;
    --config)
      CONFIGURATION="$2"
      shift 2
      ;;
    --release)
      CONFIGURATION="Release"
      shift
      ;;
    -h|--help)
      COMMAND="help"
      shift
      ;;
    *)
      shift
      ;;
  esac
done

# Find Xcode project
if [[ -f "$PROJECT_PATH"/*.xcodeproj/project.pbxproj ]]; then
  PROJECT_FILE=$(ls -d "$PROJECT_PATH"/*.xcodeproj | head -1)
elif [[ -d "$PROJECT_PATH" ]]; then
  PROJECT_FILE=$(find "$PROJECT_PATH" -name "*.xcodeproj" -type d | head -1)
fi

if [[ -z "$PROJECT_FILE" ]]; then
  echo "[xcode] Error: No Xcode project found in $PROJECT_PATH" >&2
  exit 1
fi

PROJECT_NAME=$(basename "$PROJECT_FILE" .xcodeproj)

# Auto-detect scheme if not provided
if [[ -z "$SCHEME" ]]; then
  SCHEME=$(xcodebuild -project "$PROJECT_FILE" -list -json 2>/dev/null | \
    grep -o '"schemes" : \[' | head -1 | sed 's/.*"\([^"]*\)".*/\1/' || echo "$PROJECT_NAME")
fi

case "$COMMAND" in
  list)
    echo "[xcode] Available schemes for: $PROJECT_NAME"
    xcodebuild -project "$PROJECT_FILE" -list
    ;;
  
  build)
    echo "[xcode] Building: $SCHEME (Configuration: $CONFIGURATION)"
    xcodebuild -project "$PROJECT_FILE" \
      -scheme "$SCHEME" \
      -configuration "$CONFIGURATION" \
      -sdk iphoneos \
      build
    echo "[xcode] ✓ Build complete"
    ;;
  
  archive)
    echo "[xcode] Creating archive: $SCHEME"
    ARCHIVE_PATH="./build/${PROJECT_NAME}.xcarchive"
    xcodebuild -project "$PROJECT_FILE" \
      -scheme "$SCHEME" \
      -configuration Release \
      -sdk iphoneos \
      -archivePath "$ARCHIVE_PATH" \
      archive
    echo "[xcode] ✓ Archive created: $ARCHIVE_PATH"
    ;;
  
  test)
    echo "[xcode] Running tests for: $SCHEME"
    xcodebuild -project "$PROJECT_FILE" \
      -scheme "$SCHEME" \
      -configuration Debug \
      test
    echo "[xcode] ✓ Tests complete"
    ;;
  
  clean)
    echo "[xcode] Cleaning build folder..."
    xcodebuild -project "$PROJECT_FILE" \
      -scheme "$SCHEME" \
      clean
    echo "[xcode] ✓ Clean complete"
    ;;
  
  open)
    echo "[xcode] Opening in Xcode: $PROJECT_FILE"
    open "$PROJECT_FILE"
    ;;
  
  simulator)
    echo "[xcode] Building for simulator: $DEVICE"
    xcodebuild -project "$PROJECT_FILE" \
      -scheme "$SCHEME" \
      -configuration Debug \
      -sdk iphonesimulator \
      -derivedDataPath ./build/simulator \
      build
    
    # Find and launch simulator build
    echo "[xcode] Launching simulator..."
    SIMULATOR_BUILD=$(find ./build/simulator -name "*.app" -type d | head -1)
    if [[ -n "$SIMULATOR_BUILD" ]]; then
      xcrun simctl boot "$DEVICE" 2>/dev/null || true
      xcrun simctl install "$DEVICE" "$SIMULATOR_BUILD"
      echo "[xcode] ✓ App installed on $DEVICE"
    fi
    ;;
  
  help|*)
    echo "Usage: xcode-build.sh [PROJECT_PATH] <COMMAND> [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  list                -- List available schemes"
    echo "  build               -- Build for iOS device"
    echo "  archive             -- Create iOS archive (.xcarchive)"
    echo "  test                -- Run unit tests"
    echo "  clean               -- Clean build folder"
    echo "  open                -- Open project in Xcode"
    echo "  simulator           -- Build and run on simulator"
    echo ""
    echo "Options:"
    echo "  --scheme NAME       -- Xcode scheme to use"
    echo "  --device NAME       -- Simulator device (default: iPhone 16)"
    echo "  --config DEBUG|Release  -- Build configuration"
    echo "  --release           -- Build as Release"
    echo ""
    echo "Examples:"
    echo "  xcode-build.sh . list"
    echo "  xcode-build.sh ~/MyApp build --scheme MyApp"
    echo "  xcode-build.sh ~/MyApp archive --release"
    echo "  xcode-build.sh ~/MyApp simulator --device 'iPhone 15 Pro'"
    exit 0
    ;;
esac

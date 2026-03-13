# Momotaro-iOS Integration Guide

## Step-by-Step Integration into Xcode Project

### Step 1: Prepare Your Project Structure

1. Open your Momotaro-iOS project in Xcode
2. Create the following folder groups in Xcode (File → New → Group):
   - `Models`
   - `ViewModels`
   - `Views`
   - `Services`
   - `Utilities` (with sub-groups `Extensions` and `Helpers`)
   - `Tests`

### Step 2: Create Model Files

1. **Peach.swift**
   - Right-click on Models → New File → Swift File
   - Name: `Peach.swift`
   - Copy content from Models/Peach.swift
   - Make sure `Codable` and `Identifiable` are implemented

2. **User.swift**
   - New File in Models group
   - Copy User.swift content

3. **GatewayMessage.swift**
   - New File in Models group
   - Copy GatewayMessage.swift content
   - Includes validation errors

4. **SortCriteria.swift**
   - New File in Models group
   - Copy SortCriteria.swift content

### Step 3: Create Service Files

1. **NetworkService.swift**
   - Right-click on Services → New File
   - Copy NetworkService.swift content
   - Replace base URL with your actual API endpoint
   - Update endpoints as needed

2. **WebSocketManager.swift**
   - New File in Services group
   - Copy WebSocketManager.swift content
   - Update gateway URL: `wss://your-gateway-url/ws`
   - Implement URLSessionWebSocketDelegate methods

3. **StorageService.swift**
   - New File in Services group
   - Copy StorageService.swift content
   - Provides UserDefaults and file system persistence

4. **GatewayService.swift**
   - New File in Services group
   - Copy GatewayService.swift content

### Step 4: Create ViewModel Files

1. **AppState.swift**
   - Right-click on ViewModels → New File
   - Copy AppState.swift content
   - This is your centralized state holder
   - Add to `@main` app file with `@StateObject`

2. **PeachViewModel.swift**
   - New File in ViewModels group
   - Copy PeachViewModel.swift content
   - Handles peach list, filtering, sorting

3. **UserViewModel.swift**
   - New File in ViewModels group
   - Copy UserViewModel.swift content
   - Handles authentication

### Step 5: Create View Files

1. **PeachListView.swift**
   - Right-click on Views → New File
   - Copy PeachListView.swift content
   - This is your main list view

2. **SettingsView.swift** (Create new)
   - New File in Views group
   - Template for settings screen using @EnvironmentObject

3. **ContentView.swift**
   - Update existing ContentView.swift
   - Use NavigationView with PeachListView

### Step 6: Create Extensions & Utilities

**Utilities/Extensions:**

1. **String+Extensions.swift**
   - New File in Utilities/Extensions
   - Copy String+Extensions.swift

2. **URLSession+Extensions.swift** (Create new)
   - New File in Utilities/Extensions
   - Add custom URLSession helpers if needed

3. **View+Extensions.swift** (Create new)
   - New File in Utilities/Extensions
   - Add custom SwiftUI modifiers

**Utilities/Helpers:**

1. **Logger.swift**
   - New File in Utilities/Helpers
   - Basic logging utility

2. **Constants.swift**
   - New File in Utilities/Helpers
   - Define API endpoints:
   ```swift
   struct Constants {
       static let apiBaseURL = "https://api.peaches.com"
       static let gatewayURL = "wss://gateway.openclaw.local/ws"
   }
   ```

### Step 7: Update App File

Update your main app file (e.g., `MomotaroApp.swift`):

```swift
import SwiftUI

@main
struct MomotaroApp: App {
    @StateObject var appState = AppState()
    @StateObject var peachViewModel = PeachViewModel()
    @StateObject var userViewModel = UserViewModel()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .environmentObject(peachViewModel)
                .environmentObject(userViewModel)
        }
    }
}
```

### Step 8: Create Test Files

1. **NetworkServiceTests.swift**
   - Right-click on Tests group → New File
   - Copy NetworkServiceTests.swift
   - Includes mock URLSession

2. **PeachViewModelTests.swift**
   - New File in Tests group
   - Copy PeachViewModelTests.swift
   - Tests filtering, sorting, statistics

3. **AppStateTests.swift** (Create new)
   - Tests state updates and persistence

4. **UserViewModelTests.swift** (Create new)
   - Tests authentication flow

### Step 9: Build & Test

1. **Build the project**
   - Cmd + B to build
   - Fix any import or syntax errors

2. **Run tests**
   - Cmd + U to run unit tests
   - Verify all tests pass

3. **Run the app**
   - Cmd + R to run on simulator
   - Test basic functionality

### Step 10: Configuration

1. **Update API endpoints**
   - In NetworkService.swift: Update base URL
   - In Constants.swift: Set correct endpoints
   - In WebSocketManager: Update gateway URL

2. **Set up authentication**
   - Implement real auth in UserViewModel
   - Store tokens securely
   - Handle token refresh

3. **Configure storage**
   - Decide on UserDefaults vs file system
   - Implement caching strategy
   - Set up data migrations if needed

## File Checklist

### Models (4 files)
- [ ] Peach.swift
- [ ] User.swift
- [ ] GatewayMessage.swift
- [ ] SortCriteria.swift

### Services (4 files)
- [ ] NetworkService.swift
- [ ] WebSocketManager.swift
- [ ] StorageService.swift
- [ ] GatewayService.swift

### ViewModels (3 files)
- [ ] AppState.swift
- [ ] PeachViewModel.swift
- [ ] UserViewModel.swift

### Views (3+ files)
- [ ] PeachListView.swift
- [ ] SettingsView.swift (or your screens)
- [ ] ContentView.swift (updated)

### Utilities (5+ files)
- [ ] String+Extensions.swift
- [ ] URLSession+Extensions.swift (optional)
- [ ] View+Extensions.swift (optional)
- [ ] Logger.swift
- [ ] Constants.swift

### Tests (4+ files)
- [ ] NetworkServiceTests.swift
- [ ] PeachViewModelTests.swift
- [ ] AppStateTests.swift
- [ ] UserViewModelTests.swift

## Common Issues & Solutions

### Import Errors
```
Error: No such module 'Momotaro'
```
**Solution:** Update @testable import to your actual module name

### Build Fails
- Check for missing files
- Verify all imports are correct
- Ensure target membership is set

### Tests Won't Run
- Verify test files are in the Tests group
- Check that @testable import uses correct module name
- Make sure test target includes source files

### Missing Dependencies
- If using Combine/async-await, check iOS deployment target
- WebSocket requires iOS 13+

## Next Steps

1. **Implement real API calls**
   - Update NetworkService endpoints
   - Test with actual backend

2. **Add authentication**
   - Implement OAuth or JWT
   - Secure token storage

3. **Enable WebSocket**
   - Test gateway connection
   - Implement message handlers

4. **Add more views**
   - Detail screens
   - Edit/create screens
   - Settings screens

5. **Enhance testing**
   - Add UI tests with XCUITest
   - Implement integration tests
   - Add snapshot tests

## Support & Debugging

### Enable Debug Logging
```swift
import os.log

let logger = Logger()
logger.info("Debug message")
```

### Monitor Network Calls
- Use Xcode Network Link Conditioner
- Check Charles Proxy for requests
- Enable URLSession logging

### Debug State Changes
- Print @Published changes
- Use Xcode breakpoints
- Check AppState in debugger

## Performance Tips

1. Lazy load images
2. Paginate list data
3. Cache responses
4. Use weak self in closures
5. Profile with Instruments

## Documentation Files

Place these in your project root:
- [ ] ARCHITECTURE.md (overview)
- [ ] INTEGRATION.md (this file)
- [ ] TESTING.md (test guide)
- [ ] WEBSOCKET.md (WebSocket setup)
- [ ] README.md (project overview)

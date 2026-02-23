# Mobile Dev Agent Memory

## SwiftUI / iOS Patterns

### Observable Pattern (iOS 17+)
- Use `@Observable` + `@MainActor` on ViewModels (NOT ObservableObject)
- Singletons: `static let shared = MyClass()` with private `init()`
- Environment injection: `.environment(storeManager)` in App, `@Environment(StoreManager.self)` in Views

### StoreKit 2 Pattern
- `Product.products(for: productIDs)` to load
- `product.purchase()` returns `PurchaseResult` enum
- Always call `transaction.finish()` after handling
- `Transaction.updates` async sequence for background transaction listening
- `Transaction.currentEntitlements` for restore

### Sign in with Apple
- Import `AuthenticationServices`
- Use `ASAuthorizationAppleIDButton` SwiftUI button
- Extract `identityToken` from `ASAuthorizationAppleIDCredential`
- Token is `Data`, convert to `String` with `.utf8`

### Google OAuth (no SDK)
- Use `ASWebAuthenticationSession` for browser OAuth flow
- `callbackURLScheme` must match URL scheme in project
- Extract `code` from callback URL query params

### Keychain Pattern
- `KeychainHelper.shared.save/read/delete` - existing singleton in project
- Constants in `AppConstants.Keychain`

## Project-Specific Notes

### Exercise Plan App
- Auth: JWT stored in Keychain via `AppConstants.Keychain.jwtToken`
- Backend: `AppConstants.API.baseURL` = `http://localhost:8000`
- `APIClient.shared` auto-attaches JWT Bearer token
- `AuthManager.shared.isAuthenticated` gates app access (replaces API key check)
- `LLMServiceFactory.createFromSettings()` prefers `BackendLLMService` when authenticated
- `StoreManager` injected via `.environment()` from App entry point

### project.yml (XcodeGen)
- Entitlements go under `targets.<name>.entitlements.properties`
- URL schemes go under `targets.<name>.info.properties.CFBundleURLTypes`
- `CODE_SIGN_ENTITLEMENTS` must reference path relative to project root

## Common Pitfalls
- `ASWebAuthenticationSession` needs `presentationContextProvider` set before `start()`
- `@Observable` classes must NOT use `@Published` - just plain stored properties
- StoreKit `Transaction.updates` task should be stored and cancelled in `deinit`
- `VerificationResult.unverified` should throw, not silently pass

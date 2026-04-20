# Native Authentik Login (Flow Executor API)

This document explains how the ChatFort override replaces the default WebView-based proxy authentication with a native SwiftUI login form that talks directly to Authentik's headless Flow Executor API.

---

## What This Replaces

**Before (upstream):** When the app detects an Authentik-protected server, it opens `ProxyAuthView` — a full `WKWebView` showing the Authentik web portal. The user logs in through the web interface, and session cookies are captured when the flow completes.

**After (override):** The app shows a native SwiftUI form with username and password fields. The form posts credentials to Authentik's Flow Executor API, which returns the same session cookies without ever showing a web view. After the proxy login succeeds, the app automatically completes the OpenWebUI OAuth login programmatically — the user goes straight from the native login form to the chat interface with no intermediate screens.

The `ProxyAuthView` is **not deleted** — it remains as a fallback for non-Authentik proxies (Authelia, Keycloak, etc.) or if the Flow Executor returns an unexpected response.

---

## Authentik Flow Executor API

The Flow Executor is Authentik's headless (browserless) authentication API. It supports a challenge-response pattern where each stage of the authentication flow returns a challenge, and the client responds with the appropriate data.

### Endpoint

```
https://auth.chatfort.ai/api/v3/flows/executor/default-authentication-flow/
```

### Flow Slug

The flow slug `default-authentication-flow` comes from the standard Authentik setup. It was confirmed from the `eigenloom/` configuration in this repository. This flow includes:

1. **`default-authentication-identification`** — username/email identification stage
2. **Password stage** — password verification
3. **Optional MFA/authenticator validation** — TOTP or other second factor

### Authentication Sequence

```
1. GET  /api/v3/flows/executor/default-authentication-flow/
   Response: { "component": "ak-stage-identification", ... }

2. POST /api/v3/flows/executor/default-authentication-flow/
   Body:  { "component": "ak-stage-identification", "uid_field": "username" }
   Response: { "component": "ak-stage-password", ... }

3. POST /api/v3/flows/executor/default-authentication-flow/
   Body:  { "component": "ak-stage-password", "password": "..." }
   Response: { "component": "xak-flow-redirect", ... }  (success)
          OR { "component": "ak-stage-access-denied", "message": "..." }  (failure)
          OR { "component": "ak-stage-authenticator-validate", ... }  (MFA required)
```

### Important: Cookie Persistence

The Flow Executor uses HTTP cookies to track flow state between requests. All requests in a single authentication attempt **must** share the same `URLSession` cookie jar. The override creates a dedicated `URLSession` with `httpCookieStorage = HTTPCookieStorage.shared` for this purpose.

---

## Auth Domain Convention

The override derives the Authentik auth domain from the server URL:

```
chat.chatfort.ai  →  auth.chatfort.ai
```

This follows the convention where the first subdomain component is replaced with `auth`. If the server URL doesn't follow this pattern, the override falls back to the WebView.

---

## MFA (TOTP) Handling

If Authentik returns `ak-stage-authenticator-validate` after the password stage, the app:

1. Sets `nativeProxyNeedsMFA = true`
2. Shows a TOTP input field in the login form
3. On submission, sends:

```json
{
  "component": "ak-stage-authenticator-validate",
  "code": "123456"
}
```

4. If the TOTP is correct, the flow completes with `xak-flow-redirect`
5. If incorrect, the error message from Authentik is displayed

---

## Fallback Behavior

The native login falls back to the `ProxyAuthView` WebView in these cases:

- The Flow Executor returns an unrecognized `component` value
- The auth domain cannot be derived from the server URL
- A network error occurs during the flow that suggests the endpoint doesn't exist

This ensures compatibility with non-Authentik proxies (Authelia, Keycloak, oauth2-proxy) that don't have a Flow Executor API.

---

## Auto-Connect + Auto-OAuth Flow

The complete streamlined login flow works as follows:

```
App Launch (first time)
    |
    v
[ServerConnectionView] -- .task auto-triggers connect()
    |                      (no "Connect" button press needed)
    v
Health check detects proxy auth required
    |
    v
[NativeProxyLoginView] -- user enters username + password
    |
    v
Authentik Flow Executor authenticates (session cookies captured)
    |
    v
connectSkippingProxyCheck() -- fetches OpenWebUI config
    |
    v
Auto-detects OAuth provider (e.g. "oidc")
    |
    v
performAutoOAuthLogin() -- follows /oauth/oidc/login redirect
    |                       chain via URLSession (has Authentik
    |                       session cookies, auto-completes)
    v
Captures OpenWebUI JWT token from cookie
    |
    v
loginWithSSOToken() --> [Authenticated] --> Chat interface
```

**Key insight:** `performAutoOAuthLogin` uses URLSession (not WKWebView) to follow the OAuth redirect chain. Since URLSession shares `HTTPCookieStorage.shared` with the Flow Executor session, Authentik recognizes the existing session and auto-authorizes without user interaction. The JWT token cookie set by OpenWebUI's callback is captured and used to complete authentication.

**Fallback:** If no OAuth provider is detected or the programmatic OAuth fails, the app falls back to showing the auth method selection screen.

---

## Override Configs

### `configs/01_server_prefill.json`

| File | Change |
|------|--------|
| `ServerConnectionView.swift` | Adds `hasAutoConnected` state variable |
| `ServerConnectionView.swift` | Adds `.task` modifier that auto-triggers `connect()` when URL is pre-filled |

### `configs/02_auth_native_login.json`

| File | Change |
|------|--------|
| `AuthViewModel.swift` | Adds `.nativeProxyLogin` to `AuthPhase` enum |
| `AuthViewModel.swift` | Adds state variables for native login (username, password, TOTP, loading state) |
| `AuthViewModel.swift` | Replaces `.proxyAuthRequired` case to use native login instead of WebView |
| `AuthViewModel.swift` | Adds `authenticateViaFlowExecutor()`, `submitNativeProxyMFA()`, and `captureFlowCookiesAndResume()` methods |
| `AuthViewModel.swift` | Adds `performAutoOAuthLogin()` — programmatic OAuth via URLSession after proxy auth |
| `AuthViewModel.swift` | Modifies `connectSkippingProxyCheck()` to auto-trigger OAuth instead of showing auth method selection |

---

## Testing Checklist

- [ ] App launches and auto-connects to `chat.chatfort.ai` (no "Connect" button press)
- [ ] Native login form appears (username + password fields, no WebView)
- [ ] Correct credentials → auto-OAuth completes → chat loads (no auth method selection screen)
- [ ] Incorrect password → error message from Authentik is displayed
- [ ] Non-existent username → error message is displayed
- [ ] MFA-enabled account → TOTP field appears after password
- [ ] Correct TOTP → auto-OAuth completes → chat loads
- [ ] Incorrect TOTP → error message is displayed
- [ ] Network error during login → appropriate error message
- [ ] After successful login, session cookies are persisted (app restart maintains session)
- [ ] If OAuth auto-complete fails, falls back to auth method selection screen
- [ ] ProxyAuthView still works if manually triggered (fallback path)

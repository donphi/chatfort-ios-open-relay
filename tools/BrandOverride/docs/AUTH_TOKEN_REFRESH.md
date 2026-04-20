# Persistent Sessions via OAuth2 Refresh Tokens

This document explains how the ChatFort override adds OAuth2 refresh token support to keep users logged in indefinitely, replacing the upstream behavior where sessions expire after 1-2 days.

---

## The Problem

The upstream app stores a single JWT in the Keychain. Its "refresh" mechanism (`refreshToken()`) simply calls `getCurrentUser()` every 45 minutes to validate the token — it never actually rotates or renews the token. When Authentik's token lifetime expires, the app silently stops working: conversations don't load, and there's no error message.

---

## The Solution

A dedicated **OAuth2 provider** in Authentik (`chatfort-mobile`) issues:
- **Access tokens** with a 15-minute lifetime (short-lived for security)
- **Refresh tokens** with a 365-day lifetime (long-lived for persistence)

The app refreshes the access token every 10 minutes using the refresh token, so the user never experiences a session expiry.

---

## Token Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│                    FIRST LOGIN                          │
├─────────────────────────────────────────────────────────┤
│ 1. Native Authentik login succeeds (Flow Executor)      │
│ 2. Session cookies captured                             │
│ 3. App does OAuth2 PKCE flow:                           │
│    GET  /application/o/authorize/?...                    │
│    POST /application/o/token/                           │
│ 4. Receives: access_token + refresh_token               │
│ 5. Both stored in iOS Keychain                          │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              ONGOING (every 10 minutes)                  │
├─────────────────────────────────────────────────────────┤
│ 1. refreshToken() fires                                 │
│ 2. POST /application/o/token/                           │
│    grant_type=refresh_token                             │
│ 3. New access_token + refresh_token returned            │
│ 4. Both stored in Keychain (rotation)                   │
│ 5. App continues seamlessly                             │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│         APP FOREGROUNDED AFTER HOURS/DAYS               │
├─────────────────────────────────────────────────────────┤
│ 1. validateSessionInBackground() runs                   │
│ 2. Access token expired → 401 from Open WebUI           │
│ 3. Automatic refresh via stored refresh token           │
│ 4. New tokens stored, user sees no interruption         │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│     REFRESH TOKEN EXPIRED (after 365 days)              │
├─────────────────────────────────────────────────────────┤
│ 1. Refresh attempt fails (400/401 from Authentik)       │
│ 2. Refresh token cleared from Keychain                  │
│ 3. Native login form shown                              │
│ 4. User re-authenticates once, gets new token pair      │
└─────────────────────────────────────────────────────────┘
```

---

## KeychainService Changes

The override adds three new methods to `KeychainService`:

| Method | Purpose |
|--------|---------|
| `saveRefreshToken(_:forServer:)` | Stores the refresh token in Keychain |
| `getRefreshToken(forServer:)` | Retrieves the refresh token |
| `deleteRefreshToken(forServer:)` | Removes the refresh token |
| `hasRefreshToken(forServer:)` | Checks if a refresh token exists |

Refresh tokens use the key format `refresh_token:{normalized_url}` to avoid collisions with access tokens (`token:{normalized_url}`).

---

## AuthViewModel Changes

| Change | Detail |
|--------|--------|
| `startTokenRefreshTimer()` | Interval changed from 45 min to 10 min |
| `refreshToken()` | Attempts OAuth2 refresh grant first, falls back to `getCurrentUser()` |
| Session expiry | Redirects to `.nativeProxyLogin` instead of `.authMethodSelection` |

### Refresh Flow in `refreshToken()`

```
1. Check if refresh token exists in Keychain
2. If yes: POST to token endpoint with grant_type=refresh_token
3. If 200: store new access_token and refresh_token
4. If error: delete expired refresh token, fall through
5. Fall back: call getCurrentUser() to validate session
6. If 401: show native login form
```

---

## ServerConfig Changes

Three new optional fields added to `ServerConfig`:

| Field | Type | Purpose |
|-------|------|---------|
| `oauth2ClientID` | `String?` | OAuth2 client ID (`chatfort-mobile`) |
| `oauth2TokenEndpoint` | `String?` | Token endpoint URL |
| `oauth2AuthEndpoint` | `String?` | Authorization endpoint URL |

These are included in `CodingKeys` and decoded with graceful defaults so existing saved configs don't break.

---

## Override Config

The override is defined in `configs/03_auth_token_refresh.json`. It modifies:

| File | Change |
|------|--------|
| `KeychainService.swift` | Adds refresh token storage methods |
| `AuthViewModel.swift` | Replaces `refreshToken()` and `startTokenRefreshTimer()` |
| `ServerConfig.swift` | Adds OAuth2 metadata fields |

---

## Android Compatibility Notes

The same OAuth2 PKCE flow works on Android:
- Use **Android Keystore** instead of iOS Keychain for token storage
- Use `net.openid.appauth` library for the OAuth2 flow
- Same client ID (`chatfort-mobile`), same endpoints, same scopes
- The redirect URI scheme would be different (e.g., `com.chatfort.android://oauth/callback`) — register it as an additional Redirect URI on the Authentik provider

---

## Troubleshooting

### App still loses session after a day

1. Verify the `chatfort-mobile` provider exists in Authentik (see [AUTHENTIK_MOBILE_PROVIDER.md](AUTHENTIK_MOBILE_PROVIDER.md))
2. Check that `offline_access` scope is selected on the provider
3. Check that the refresh token validity is `days=365`
4. Verify the override was applied: search for `grant_type=refresh_token` in `AuthViewModel.swift`

### "Invalid grant" error during refresh

- The refresh token may have been revoked by an admin. The user needs to log in again.
- Check Authentik's **Events** log for token revocation events.

### Tokens not persisting across app restarts

- Verify Keychain access: the tokens use `kSecAttrAccessibleAfterFirstUnlock` which should persist across restarts.
- Check that the server URL normalization is consistent (trailing slashes can cause key mismatches).

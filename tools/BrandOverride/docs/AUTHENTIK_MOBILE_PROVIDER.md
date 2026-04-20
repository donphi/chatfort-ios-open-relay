# Setting Up the Authentik Mobile OAuth2 Provider

This guide walks through creating a dedicated OAuth2 provider in Authentik for the ChatFort iOS app. This provider is **separate** from the existing `open-webui` provider used for browser-based SSO — it does not affect web login at all.

The mobile provider enables:
- **Refresh tokens** with a 365-day lifetime so the app stays logged in
- **PKCE (Proof Key for Code Exchange)** for secure mobile OAuth2 flows
- **`offline_access` scope** which tells Authentik to issue refresh tokens

---

## Prerequisites

- Admin access to your Authentik instance at `https://auth.chatfort.ai`
- The existing `default-provider-authorization-implicit-consent` flow (comes with Authentik by default)

---

## Step 1: Log into Authentik Admin

1. Open your browser and go to `https://auth.chatfort.ai/if/admin/`
2. Log in with your **admin** account
3. You should see the Authentik Admin Interface dashboard

---

## Step 2: Create a New OAuth2/OpenID Provider

1. In the left sidebar, click **Applications** → **Providers**
2. Click the **Create** button (top right)
3. Select **OAuth2/OpenID Provider** from the list and click **Next**

### Fill in the Provider Details

| Field | Value | Why |
|-------|-------|-----|
| **Name** | `ChatFort Mobile` | Descriptive name for the admin UI |
| **Authentication flow** | `default-provider-authorization-implicit-consent` | This is the only option in the dropdown. It controls how Authentik handles the OAuth authorization step — "implicit consent" means the user won't see a separate "Allow this app?" screen after logging in. |
| **Authorization flow** | `default-provider-authorization-implicit-consent` | Same flow — auto-approves the OAuth consent screen since the user just authenticated |
| **Client type** | **Public** | Mobile apps cannot securely store a client secret |
| **Client ID** | `chatfort-mobile` | **Write this down** — the iOS app needs this exact value |
| **Client Secret** | *(leave empty)* | Not needed for public clients |
| **Redirect URIs/Origins (Regex)** | `openui://oauth/callback` | The iOS app's custom URL scheme for receiving the auth code |
| **Signing Key** | *(select your existing signing key)* | Same key used for the `open-webui` provider |

> **Note about "Authentication flow"**: In Authentik's provider settings, this field controls which flow runs when the OAuth provider needs to authenticate a user. The dropdown only shows authorization/consent flows, not login flows. The actual login flow (`default-authentication-flow`) is configured at the Authentik tenant level and runs automatically before the provider's authorization flow. You do not need to set the login flow here — Authentik handles that globally.

### Token Lifetimes

| Field | Value | Why |
|-------|-------|-----|
| **Access token validity** | `minutes=15` | Short-lived for security; the app refreshes every 10 minutes |
| **Refresh token validity** | `days=365` | Long-lived so users don't need to re-login for a year |

### Advanced Protocol Settings

Scroll down to the **Advanced protocol settings** section:

| Field | Value | Why |
|-------|-------|-----|
| **Scopes** | Select: `openid`, `profile`, `email`, **`offline_access`** | `offline_access` is **critical** — without it, Authentik will NOT issue a refresh token (changed in Authentik 2024.2) |
| **Subject mode** | `Based on the User's hashed ID` | Standard; matches the existing provider |
| **Include claims in id_token** | `Yes` (checked) | Includes user info in the ID token |

4. Click **Finish** to create the provider

---

## Step 3: Create an Application for the Provider

1. In the left sidebar, click **Applications** → **Applications**
2. Click the **Create** button
3. Fill in:

| Field | Value |
|-------|-------|
| **Name** | `ChatFort Mobile` |
| **Slug** | `chatfort-mobile` |
| **Provider** | Select `ChatFort Mobile` (the provider you just created) |
| **Launch URL** | `openui://` *(optional — for Authentik's app launcher)* |

4. *(Optional)* Under **Policy / Group / User Bindings**, bind to the `openwebui` group if you want to restrict which users can log in via the mobile app
5. Click **Create**

---

## Step 4: Verify the Discovery Endpoint

Open this URL in your browser to confirm the provider is working:

```
https://auth.chatfort.ai/application/o/chatfort-mobile/.well-known/openid-configuration
```

You should see a JSON response containing:
- `token_endpoint` — should be `https://auth.chatfort.ai/application/o/token/`
- `authorization_endpoint` — should be `https://auth.chatfort.ai/application/o/authorize/`
- `issuer` — should be `https://auth.chatfort.ai/application/o/chatfort-mobile/`
- `scopes_supported` — should include `offline_access`

If you get a 404, double-check that the Application slug is `chatfort-mobile` and the Provider is correctly linked.

---

## Step 5: Open WebUI Environment Variables

**No changes needed.** The existing Open WebUI OIDC configuration (`OAUTH_CLIENT_ID`, `OPENID_PROVIDER_URL`, etc.) stays as-is — it uses the `open-webui` provider for browser-based SSO.

The new `chatfort-mobile` provider is used **only** by the iOS app. Open WebUI does not need to know about it because:
1. The iOS app uses the refresh token to get a fresh access token from Authentik
2. The app then uses that access token as a Bearer token against Open WebUI's API
3. Open WebUI validates the JWT signature (not the provider), so any valid Authentik-signed token works

### Optional: Increase Max Sessions

If you have many mobile devices per user, you may want to increase the maximum concurrent OAuth sessions:

```env
OAUTH_MAX_SESSIONS_PER_USER=20
```

The default is 10, which is usually sufficient.

---

## Values the iOS App Needs

These values are hardcoded in the override config files (`configs/03_auth_token_refresh.json`):

| Value | Setting |
|-------|---------|
| **Auth domain** | `auth.chatfort.ai` |
| **Client ID** | `chatfort-mobile` |
| **Token endpoint** | `https://auth.chatfort.ai/application/o/token/` |
| **Authorization endpoint** | `https://auth.chatfort.ai/application/o/authorize/` |
| **Flow slug** | `default-authentication-flow` |
| **Redirect URI** | `openui://oauth/callback` |

---

## Troubleshooting

### No refresh token is returned

- **Most common cause**: The `offline_access` scope is not selected on the provider. Go to **Providers** → **ChatFort Mobile** → **Edit** → **Advanced protocol settings** → ensure `offline_access` is in the selected scopes.
- Verify by checking the token response: it should contain a `refresh_token` field alongside `access_token`.

### Token expires too quickly

- Check the **Refresh token validity** on the provider. It should be `days=365`.
- The **Access token validity** should be `minutes=15` (the app refreshes every 10 minutes).

### "Invalid redirect URI" error

- Ensure the Redirect URI on the provider is exactly `openui://oauth/callback` (no trailing slash).
- The iOS app's URL scheme must be registered in `Info.plist` as `openui`.

### Users can't log in via mobile but can via web

- Check that the Application has the correct group bindings. If the `open-webui` application has a group binding, the `chatfort-mobile` application needs the same binding.

### Discovery endpoint returns 404

- Verify the Application slug is `chatfort-mobile` (not `ChatFort Mobile` or similar).
- Ensure the Application is linked to the `ChatFort Mobile` provider.

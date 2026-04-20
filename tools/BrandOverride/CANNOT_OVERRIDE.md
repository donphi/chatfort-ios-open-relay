# CANNOT_OVERRIDE.md — Brand Strings That Require Upstream File Edits

> **What is this file?**
> This is a complete, line-by-line inventory of every place the upstream repo says
> "Open Relay", "Open UI", "Ask Open Relay", or links to the original author's GitHub.
> These strings live inside upstream source files that **cannot** be changed by simply
> adding new files to the repo — the scripts in `scripts/` handle them automatically.
>
> **When do I need this?**
> - After pulling upstream updates, run `./scripts/override.sh --dry-run` to see if
>   any of these lines moved or changed. This file is your reference for what *should*
>   be different.
> - If you ever need to make changes manually (without the scripts), this is your checklist.

---

## How to Read This Table

| Column | Meaning |
|--------|---------|
| **File** | Path from the repo root |
| **Line** | Line number in the current version (v2.4 build 1) |
| **Current Value** | The exact string as it appears in upstream |
| **Desired Value** | What it should say for the ChatFort brand |
| **Type** | `UI` = user sees it, `Build` = Xcode build setting, `Intent` = Siri/Shortcuts, `Doc` = documentation |
| **Risk** | How likely this line changes in an upstream update: `Low` / `Medium` / `High` |
| **Impact** | What happens if this is NOT changed |

---

## project.pbxproj — Xcode Build Settings

This file controls the app's display name on the home screen and all iOS permission prompts.
It has Debug and Release sections that duplicate every setting, so each change appears twice.

| File | Line | Current Value | Desired Value | Type | Risk | Impact |
|------|------|---------------|---------------|------|------|--------|
| `Open UI.xcodeproj/project.pbxproj` | 543 | `INFOPLIST_KEY_CFBundleDisplayName = "Open Relay";` | `"ChatFort"` | Build | Medium | App name on home screen says "Open Relay" |
| `Open UI.xcodeproj/project.pbxproj` | 587 | `INFOPLIST_KEY_CFBundleDisplayName = "Open Relay";` | `"ChatFort"` | Build | Medium | Same (Release config) |
| `Open UI.xcodeproj/project.pbxproj` | 546 | `"Open Relay needs camera access to capture photos and documents for chat attachments."` | `"ChatFort needs camera..."` | Build | Low | Camera permission popup says "Open Relay" |
| `Open UI.xcodeproj/project.pbxproj` | 590 | (same as 546) | (same) | Build | Low | Same (Release) |
| `Open UI.xcodeproj/project.pbxproj` | 547 | `"Open Relay uses Face ID to protect your account and conversations."` | `"ChatFort uses Face ID..."` | Build | Low | Face ID prompt says "Open Relay" |
| `Open UI.xcodeproj/project.pbxproj` | 591 | (same as 547) | (same) | Build | Low | Same (Release) |
| `Open UI.xcodeproj/project.pbxproj` | 548 | `"Open Relay needs microphone access for voice input and voice calls."` | `"ChatFort needs microphone..."` | Build | Low | Mic permission says "Open Relay" |
| `Open UI.xcodeproj/project.pbxproj` | 592 | (same as 548) | (same) | Build | Low | Same (Release) |
| `Open UI.xcodeproj/project.pbxproj` | 549 | `"Open Relay needs permission to save images generated in conversations to your photo library."` | `"ChatFort needs permission..."` | Build | Low | Save-to-photos prompt says "Open Relay" |
| `Open UI.xcodeproj/project.pbxproj` | 593 | (same as 549) | (same) | Build | Low | Same (Release) |
| `Open UI.xcodeproj/project.pbxproj` | 550 | `"Open Relay needs photo library access to attach images to your conversations."` | `"ChatFort needs photo library..."` | Build | Low | Photo picker prompt says "Open Relay" |
| `Open UI.xcodeproj/project.pbxproj` | 594 | (same as 550) | (same) | Build | Low | Same (Release) |
| `Open UI.xcodeproj/project.pbxproj` | 551 | `"Open Relay uses speech recognition to convert your voice input to text."` | `"ChatFort uses speech..."` | Build | Low | Speech recognition prompt says "Open Relay" |
| `Open UI.xcodeproj/project.pbxproj` | 595 | (same as 551) | (same) | Build | Low | Same (Release) |

**Total: 14 changes in this file.**

---

## AboutView.swift — About Screen

This is the "About" page in Settings. It shows the app name, tagline, credits, and links.

| File | Line | Current Value | Desired Value | Type | Risk | Impact |
|------|------|---------------|---------------|------|------|--------|
| `Open UI/Features/Settings/Views/AboutView.swift` | 122 | `Text("Open Relay")` | `Text("ChatFort")` | UI | Medium | About screen title says "Open Relay" |
| `Open UI/Features/Settings/Views/AboutView.swift` | 103 | `Text("Made with ❤️ for Open WebUI")` | `Text("Designed by donphi")` | UI | Low | Credits line at bottom |
| `Open UI/Features/Settings/Views/AboutView.swift` | 52 | `url: "https://github.com/Ichigo3766/Open-Relay"` | `url: "https://github.com/donphi/chatfort-ios-chat-relay"` | UI | Medium | Source code link |
| `Open UI/Features/Settings/Views/AboutView.swift` | 57 | `url: "https://github.com/Ichigo3766/Open-Relay/blob/main/PRIVACY.md"` | `url: "https://github.com/donphi/chatfort-ios-chat-relay/blob/main/PRIVACY.md"` | UI | Low | Privacy policy link |
| `Open UI/Features/Settings/Views/AboutView.swift` | 69 | `url: "https://github.com/Ichigo3766/Open-Relay/issues/new?template=bug_report.yml"` | `url: "https://github.com/donphi/chatfort-ios-chat-relay/issues/new?template=bug_report.yml"` | UI | Low | Bug report link |
| `Open UI/Features/Settings/Views/AboutView.swift` | 76 | `url: "https://github.com/Ichigo3766/Open-Relay/issues/new?template=feature_request.yml"` | `url: "https://github.com/donphi/chatfort-ios-chat-relay/issues/new?template=branding.yml"` | UI | Low | Feature request -> branding link |
| `Open UI/Features/Settings/Views/AboutView.swift` | 83 | `url: "https://github.com/Ichigo3766/Open-Relay/issues/new?template=ui_ux.yml"` | `url: "https://github.com/donphi/chatfort-ios-chat-relay/issues/new?template=branding.yml"` | UI | Low | UI/UX -> branding link |
| `Open UI/Features/Settings/Views/AboutView.swift` | 90 | `url: "https://github.com/Ichigo3766/Open-Relay/issues/new?template=performance.yml"` | `url: "https://github.com/donphi/chatfort-ios-chat-relay/issues/new?template=bug_report.yml"` | UI | Low | Performance -> bug report link |
| `Open UI/Features/Settings/Views/AboutView.swift` | 96 | `url: "https://github.com/Ichigo3766/Open-Relay/issues/new?template=question.yml"` | `url: "https://github.com/donphi/chatfort-ios-chat-relay/issues/new?template=bug_report.yml"` | UI | Low | Question -> bug report link |

**Total: 9 changes in this file.**

---

## SettingsView.swift — Settings Screen

| File | Line | Current Value | Desired Value | Type | Risk | Impact |
|------|------|---------------|---------------|------|------|--------|
| `Open UI/Features/Settings/Views/SettingsView.swift` | 223 | `title: "About Open Relay"` | `title: "About ChatFort"` | UI | Medium | Settings row label |
| `Open UI/Features/Settings/Views/SettingsView.swift` | 1938 | `"...iOS Settings → Open Relay → Notifications."` | `"...iOS Settings → ChatFort → Notifications."` | UI | Low | Notification help text |

**Total: 2 changes in this file.**

---

## AppearanceSettingsView.swift — Appearance Settings

| File | Line | Current Value | Desired Value | Type | Risk | Impact |
|------|------|---------------|---------------|------|------|--------|
| `Open UI/Features/Settings/Views/AppearanceSettingsView.swift` | 23 | `"Choose how Open Relay looks. System follows your device settings."` | `"Choose how ChatFort looks..."` | UI | Low | Footer text under appearance picker |

**Total: 1 change in this file.**

---

## ServerConnectionView.swift — Login/Connection Screen

| File | Line | Current Value | Desired Value | Type | Risk | Impact |
|------|------|---------------|---------------|------|------|--------|
| `Open UI/Features/Auth/Views/ServerConnectionView.swift` | 234 | `Text("Open UI")` | `Text("ChatFort")` | UI | Medium | Large title on the server connection screen |

**Total: 1 change in this file.**

---

## AppIntentsService.swift — Siri Shortcuts

| File | Line | Current Value | Desired Value | Type | Risk | Impact |
|------|------|---------------|---------------|------|------|--------|
| `Open UI/Core/Services/AppIntentsService.swift` | 104 | `IntentDescription("Open the create-channel sheet in Open Relay.")` | `"...in ChatFort."` | Intent | Low | Siri Shortcuts description |

**Total: 1 change in this file.**

---

## OpenUIWidgets.swift — Widget Extension

| File | Line | Current Value | Desired Value | Type | Risk | Impact |
|------|------|---------------|---------------|------|------|--------|
| `OpenUIWidgets/OpenUIWidgets.swift` | 54 | `.configurationDisplayName("Open Relay")` | `"ChatFort"` | UI | Medium | Widget name in widget gallery |
| `OpenUIWidgets/OpenUIWidgets.swift` | 208 | `Text("Ask Open Relay")` | `Text("Ask ChatFort")` | UI | Medium | Search bar text in medium widget |
| `OpenUIWidgets/OpenUIWidgets.swift` | 297 | `.configurationDisplayName("Open Relay")` | `"ChatFort"` | UI | Medium | Lock screen widget name |
| `OpenUIWidgets/OpenUIWidgets.swift` | 298 | `.description("Quick access to Open Relay from your lock screen.")` | `"...ChatFort..."` | UI | Low | Lock screen widget description |
| `OpenUIWidgets/OpenUIWidgets.swift` | 324 | `Text("Open Relay")` | `Text("ChatFort")` | UI | Medium | Rectangular lock screen widget title |
| `OpenUIWidgets/OpenUIWidgets.swift` | 335 | `Label("Ask Open Relay", systemImage: ...)` | `"Ask ChatFort"` | UI | Low | Inline lock screen widget label |

**Total: 6 changes in this file.**

---

## OpenUIWidgetsControl.swift — Widget Control Intent

| File | Line | Current Value | Desired Value | Type | Risk | Impact |
|------|------|---------------|---------------|------|------|--------|
| `OpenUIWidgets/OpenUIWidgetsControl.swift` | 32 | `IntentDescription("Open a new chat in Open Relay.")` | `"...in ChatFort."` | Intent | Low | Control Center widget intent description |

**Total: 1 change in this file.**

---

## Info.plist — App Configuration

| File | Line | Current Value | Desired Value | Type | Risk | Impact |
|------|------|---------------|---------------|------|------|--------|
| `Open UI/Info.plist` | 112 | `<string>Open Relay Chat Item</string>` | `<string>ChatFort Chat Item</string>` | Build | Low | UTType description (shown in share sheets) |

**Total: 1 change in this file.**

---

## PRIVACY.md — Privacy Policy

| File | Line | Current Value | Desired Value | Type | Risk | Impact |
|------|------|---------------|---------------|------|------|--------|
| `PRIVACY.md` | 1 | `# Open UI Privacy Policy` | `# ChatFort Privacy Policy` | Doc | Low | Privacy page title |
| `PRIVACY.md` | 5 | `Open UI is an open‑source mobile client for Open WebUI.` | `ChatFort is an open‑source...` | Doc | Low | First paragraph |
| `PRIVACY.md` | 23 | `Depending on how you use Open UI,` | `...use ChatFort,` | Doc | Low | Permissions section |
| `PRIVACY.md` | 46 | `Open UI is not directed to children` | `ChatFort is not directed...` | Doc | Low | Children's privacy section |
| `PRIVACY.md` | 52 | `https://github.com/Ichigo3766/Open-UI` | `https://github.com/donphi/chatfort-ios-chat-relay` | Doc | Low | Contact link |

**Total: 5 changes in this file.**

---

## Icon Files (Bundle + Preview PNG)

The app icon uses an Icon Composer `.icon` bundle (Liquid Glass format). The
override script copies the bundle into the project and a preview PNG for in-app
display.

| File | Type | Impact if not changed |
|------|------|-----------------------|
| `Open UI/AppIcon.icon` | Icon Composer bundle (home screen, App Store, all appearances) | Shows original Open Relay icon |
| `OpenUIWidgets/AppIcon.icon` | Icon Composer bundle (widget icon) | Widget shows original icon |
| `Open UI/Assets.xcassets/AppIconImage.imageset/IMG_0816.png` | In-app preview (About, Onboarding, Login screens) | Shows original icon in UI |
| `OpenUIWidgets/Assets.xcassets/AppIconImage.imageset/IMG_0816.png` | Widget in-app preview | Widget shows original icon |

---

## Custom Font Overrides (`configs/07_custom_fonts.json`)

These are font-related string replacements and file operations applied by the
`07_custom_fonts.json` modular config. They are NOT brand-string changes — they
replace system font calls with custom font references.

### Font File Copies

| Source | Target | Purpose |
|--------|--------|---------|
| `Assets/Fonts/main/*.otf` (6 files) | `Open UI/Resources/Fonts/` | Main app body fonts |
| `Assets/Fonts/round/*.otf` (3 files) | `Open UI/Resources/Fonts/` | Rounded (input field) fonts |
| `Assets/Fonts/mono/*.otf` (3 files) | `Open UI/Resources/Fonts/` | Monospaced (code/terminal) fonts |
| `Assets/Fonts/main/StyreneB-{Regular,Bold}.otf` | `OpenUIWidgets/Fonts/` | Widget text fonts |

### Info.plist Font Registration

| File | Change | Type |
|------|--------|------|
| `Open UI/Info.plist` | Inject `UIAppFonts` array with 12 font filenames | Build |
| `OpenUIWidgets/Info.plist` | Inject `UIAppFonts` array with 2 font filenames | Build |

### Typography.swift Rewrites

| File | Change | Type |
|------|--------|------|
| `Typography.swift` | Add `customFont(size:weight:design:)` helper | Code |
| `Typography.swift` | Rewrite 15 static font constants to use `customFont()` | Code |
| `Typography.swift` | Rewrite both `scaled()` factories to use `customFont()` | Code |
| `Typography.swift` | Rewrite `ScaledFontModifier` body to use `AppTypography.customFont()` | Code |

### UIKit Font Replacements

| File | Change | Type |
|------|--------|------|
| `ChatInputField.swift` | `UIFont.systemFont` + `.rounded` → `UIFont(name: "CircularStd-Book")` | Code |
| `ChannelInputField.swift` | Same as ChatInputField | Code |
| `TerminalBrowserView.swift` | `.monospacedSystemFont` → `UIFont(name: "ApercuMonoPro-Regular")` | Code |

### CSS Font Replacements

| File | Change | Type |
|------|--------|------|
| `HTMLPreviewView.swift` | Body `font-family` prepended with `'Styrene B'` | Code |
| `HTMLPreviewView.swift` | Code `font-family` prepended with `'Apercu Mono Pro'` | Code |

### Direct `.font(.system())` Replacements

| File | Calls Changed | Notes |
|------|---------------|-------|
| `UsageInfoPopover.swift` | 4 | Text labels and values; SF Symbol icon kept as system |
| `VoiceCallPillView.swift` | 1 | Monospaced timer; phone icon kept as system |
| `AccessibilitySettingsView.swift` | 7 | Preview card text; SF Symbol icons and dynamic-weight expressions kept as system |
| `ChannelDetailView.swift` | 1 | Reaction emoji text |
| `OpenUIWidgets.swift` | 4 | Widget text labels; 7 SF Symbol icon calls kept as system |

### NOT Changed (Font-Related)

| Item | Why it stays as system font |
|------|----------------------------|
| SF Symbol `Image(systemName:)` font calls | SF Symbols only render correctly with system fonts |
| `.fontWeight()` modifier calls | These modify existing fonts, not set new ones |
| Semantic font styles (`.headline`, `.caption`, `.title3`, `.body`, `.footnote`) | Used in edge cases (loading screens, error sheets); acceptable as system |
| `MessageReactionOverlay` emoji font | Emoji rendering depends on Apple's system emoji font |
| `StreamingMarkdownView` / `MarkdownView` library | Uses `MarkdownTheme.default` which applies system body font; custom theme is a follow-up |
| Dynamic weight expressions (`isSelected ? .semibold : .medium`) | Too complex for static find/replace |

---

## Grand Total

| Category | Files | Changes |
|----------|-------|---------|
| Build settings (pbxproj) | 1 | 14 |
| Swift UI views | 4 | 13 |
| Widget Swift files | 2 | 7 |
| Siri Intents | 1 | 1 |
| Info.plist | 1 | 1 |
| Privacy policy | 1 | 5 |
| Icon Composer bundles | 2 | 2 (bundle copies) |
| Icon preview PNGs | 2 | 2 (file replacements) |
| Custom font copies | 14 | 14 (file copies) |
| Font registration (Info.plist) | 2 | 2 (UIAppFonts injection) |
| Typography rewrites | 1 | 3 (helper + constants + modifier) |
| UIKit font replacements | 3 | 3 |
| CSS font replacements | 1 | 2 |
| Direct .font() replacements | 5 | 17 |
| **TOTAL** | **26+ files** | **86+ changes** |

---

## NOW Overridden (Bundle ID and App Group)

These identifiers were previously left alone but are **now overridden** by the
`brand_config.json` override system. This is required because the upstream
`com.openui.openui` bundle ID is registered to a different Apple Developer team
and cannot be used by this fork.

| Item | Upstream Value | Overridden Value |
|------|---------------|-----------------|
| Bundle ID (main app) | `com.openui.openui` | `com.chatfort.chatfort` |
| Bundle ID (widget) | `com.openui.openui.OpenUIWidget` | `com.chatfort.chatfort.OpenUIWidget` |
| App group | `group.com.openui.openui` | `group.com.chatfort.chatfort` |
| Shortcut types | `com.openui.openui.new-chat` etc. | `com.chatfort.chatfort.new-chat` etc. |
| Widget control kind | `com.openui.openui.OpenUINewChatControl` | `com.chatfort.chatfort.OpenUINewChatControl` |
| Fastlane bundle IDs | `MAIN_BUNDLE_ID = "com.openui.openui"` | `MAIN_BUNDLE_ID = "com.chatfort.chatfort"` |

These overrides are applied automatically by all GitHub Actions workflows
(via `python3 tools/BrandOverride/scripts/override.py --apply`).

---

## NOT Changed (Intentionally Left Alone)

These contain "openui" or "Open UI" but are **internal identifiers** that should NOT be
changed to avoid breaking functionality:

| Item | Why it stays |
|------|-------------|
| URL scheme `openui://` | Widgets and shortcuts use this scheme; changing it breaks deep links |
| Notification names `.openUINewChatWithFocus` etc. | Internal Swift notification names; not user-visible |
| Logger subsystem `com.openui` | Internal logging; not user-visible |
| Keychain service `com.openui.auth` | Changing this loses stored credentials |
| Background task IDs `com.openui.streaming` etc. | Registered with iOS; changing breaks background tasks |
| UTType identifier `com.openui.chat-item` | Registered type; description is changed but ID stays |
| Target name "Open UI" in Xcode | Renaming the Xcode target causes massive pbxproj changes |
| `Localizable.xcstrings` | ~168 lines with "Open Relay"/"Open UI" across all locales — these are localization keys and translated values. Changing them is possible but high-risk for merge conflicts. The override script does not touch this file. |

---

## Auth Override Files (ChatFort-Specific)

These files are modified by the modular override configs in `configs/` to implement
native Authentik login and persistent sessions. They are NOT brand-string changes —
they are functional code injections.

### Server Pre-fill (`configs/01_server_prefill.json`)

| File | Change | Type | Impact if not applied |
|------|--------|------|----------------------|
| `AuthViewModel.swift` | Pre-fill `serverURL` with `https://chat.chatfort.ai` | Code | User must type server URL manually |
| `ServerConnectionView.swift` | Hide server URL field, change subtitle text | UI | User sees URL field on first launch |

### Native Authentik Login (`configs/02_auth_native_login.json`)

| File | Change | Type | Impact if not applied |
|------|--------|------|----------------------|
| `AuthViewModel.swift` | Add `.nativeProxyLogin` to `AuthPhase` enum | Code | No native login phase available |
| `AuthViewModel.swift` | Add native login state variables (username, password, TOTP) | Code | No state for native login form |
| `AuthViewModel.swift` | Replace `.proxyAuthRequired` case to use native login | Code | WebView opens instead of native form |
| `AuthViewModel.swift` | Add Flow Executor client methods | Code | No headless Authentik API calls |

### OAuth2 Token Refresh (`configs/03_auth_token_refresh.json`)

| File | Change | Type | Impact if not applied |
|------|--------|------|----------------------|
| `KeychainService.swift` | Add refresh token storage methods | Code | No secure refresh token storage |
| `AuthViewModel.swift` | Replace `refreshToken()` with OAuth2 grant | Code | Token never actually refreshes |
| `AuthViewModel.swift` | Change refresh interval from 45 min to 10 min | Code | Token may expire between refreshes |
| `ServerConfig.swift` | Add OAuth2 metadata fields | Code | No OAuth2 config persistence |

---

## Tooling Location: `tools/BrandOverride`

The brand tooling now lives at `tools/BrandOverride/`, outside the synchronized
`Open UI/` source tree. That keeps the `backups/`, `scripts/`, assets, and config
files out of the app target and avoids the old "Multiple commands produce" issue
without relying on any special Xcode exclusion in `project.pbxproj`.

If you see old commands or docs pointing to the previous in-tree location, treat them as
stale. The supported workflow is to run `backup.sh`, `restore.sh`, and
`override.sh` from `tools/BrandOverride/`.

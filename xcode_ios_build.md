# Building ChatFort Locally with Xcode — Complete Guide

Build and run ChatFort directly on your iPhone or iPad using Xcode on your Mac.
This guide assumes you have never used Xcode before. You need a paid Apple
Developer account ($99/year).

---

## Table of Contents

1. [What You Need](#1-what-you-need)
2. [Install Xcode](#2-install-xcode)
3. [Get the Code onto Your Mac](#3-get-the-code-onto-your-mac)
4. [Open the Project in Xcode](#4-open-the-project-in-xcode)
5. [Wait for Dependencies to Download](#5-wait-for-dependencies-to-download)
6. [Set Up Signing (Your Developer Identity)](#6-set-up-signing-your-developer-identity)
7. [Connect Your iPhone](#7-connect-your-iphone)
8. [Build and Run](#8-build-and-run)
9. [Distribute to Others](#9-distribute-to-others)
10. [Updating When Upstream Changes](#10-updating-when-upstream-changes)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. What You Need

| Requirement | Details |
|---|---|
| **A Mac** | Any Mac that can run macOS 14 Sonoma or later (MacBook, iMac, Mac Mini, etc.) |
| **Xcode 16 or later** | Free from the Mac App Store (~35 GB download) |
| **Apple Developer Account** | $99/year — [developer.apple.com](https://developer.apple.com). The app installs permanently and you can distribute via TestFlight or Ad Hoc (UDID). |
| **An iPhone or iPad** | Running iOS 18.0 or later |
| **A USB cable** | To connect your iPhone to your Mac (Lightning or USB-C depending on your iPhone model) |
| **An Open WebUI server** | The app connects to your self-hosted Open WebUI instance. You need the server URL to use the app after building. |

---

## 2. Install Xcode

If you already have Xcode 16+ installed, skip to [Step 3](#3-get-the-code-onto-your-mac).

### Option A: Mac App Store (Easiest)

1. Open the **App Store** on your Mac
2. Search for **Xcode**
3. Click **Get** then **Install**
4. Wait for the download (~35 GB — this takes a while on slow connections)
5. Once installed, open Xcode once to let it finish setting up

### Option B: Apple Developer Website (Faster Download)

1. Go to [developer.apple.com/xcode](https://developer.apple.com/xcode/)
2. Click **Download**
3. Sign in with your Apple ID
4. Download the `.xip` file
5. Double-click the `.xip` file to extract it
6. Drag **Xcode.app** into your **Applications** folder
7. Open Xcode and let it install additional components when prompted

### First Launch

The first time you open Xcode, it will:
- Ask you to agree to the license agreement — click **Agree**
- Ask to install additional components — click **Install**
- Ask for your Mac password — enter it

This takes a few minutes. Once you see the "Welcome to Xcode" window, you are ready.

---

## 3. Get the Code onto Your Mac

You have two options: clone directly from Xcode, or use Terminal.

### Option A: Clone from Xcode (No Terminal Needed)

1. Open Xcode
2. On the Welcome screen, click **Clone Git Repository**
   (If you do not see the Welcome screen, go to **Window → Welcome to Xcode**)
3. In the search/URL field, paste:
   ```
   https://github.com/donphi/chatfort-ios-open-relay.git
   ```
4. Click **Clone**
5. Choose where to save it on your Mac (e.g., your Desktop or Documents folder)
6. Click **Clone** again
7. Xcode will download the code and open the project automatically

### Option B: Clone from Terminal

1. Open **Terminal** (search for it in Spotlight with Cmd+Space)
2. Navigate to where you want the project:
   ```bash
   cd ~/Desktop
   ```
3. Clone the repository:
   ```bash
   git clone https://github.com/donphi/chatfort-ios-open-relay.git
   ```
4. Open the project in Xcode:
   ```bash
   cd chatfort-ios-open-relay
   open "Open UI.xcodeproj"
   ```

---

## 4. Open the Project in Xcode

If you used Option A above, the project is already open. If you used Option B,
Xcode should have opened automatically.

If you need to open it later:

1. Open **Finder**
2. Navigate to the `chatfort-ios-open-relay` folder
3. Double-click **`Open UI.xcodeproj`** (it has a blue Xcode icon)

You should see the Xcode window with:
- A **file navigator** on the left (list of folders and files)
- The **editor area** in the center
- A **toolbar** at the top with a Play button, a device selector, and status indicators

---

## 5. Wait for Dependencies to Download

This project uses **Swift Package Manager (SPM)** for its dependencies. Xcode
downloads them automatically when you first open the project.

**Look at the status bar** at the top of the Xcode window. You will see messages like:
- "Resolving package graph..."
- "Fetching package: beautiful-mermaid-swift..."
- "Fetching package: mlx-audio-swift..."

**Wait until all packages are resolved.** This typically takes 1-3 minutes depending
on your internet speed. The status bar will go quiet when it is done.

If you see an error about packages, go to **File → Packages → Resolve Package Versions**.

---

## 6. Set Up Signing (Your Developer Identity)

This is the most important step. Xcode needs to know who you are so it can sign
the app for your device.

### 6a. Add Your Apple ID to Xcode

1. In the menu bar, go to **Xcode → Settings** (or press **Cmd + ,**)
2. Click the **Accounts** tab
3. Click the **+** button in the bottom-left corner
4. Select **Apple ID**
5. Sign in with the Apple ID linked to your paid Developer account
6. Close the Settings window

### 6b. Select Your Team and Change the Bundle Identifier for the Main App

The default Bundle Identifier (`com.openui.openui`) and App Group
(`group.com.openui.openui`) are registered to the upstream developer's Apple
account. **If you are building via GitHub Actions, the override script handles
this automatically** (changing to `com.chatfort.chatfort` and
`group.com.chatfort.chatfort`). **For local Xcode builds, you must change them
manually** to something unique to your own account, otherwise Xcode cannot
create provisioning profiles and you will see errors like
"Communication with Apple failed" or "No profiles found."

1. In the left sidebar (Project Navigator), click on **Open UI** at the very top
   (the blue project icon, not a folder)
2. In the center panel, you will see a list of **Targets**. Click on **Open UI**
   (the first target — this is the main app)
3. Click the **Signing & Capabilities** tab
4. Make sure **Automatically manage signing** is checked (it should be by default)
5. Click the **Team** dropdown and select your team name (e.g., "John Smith")
6. **Change the Bundle Identifier** from `com.openui.openui` to something unique
   to you, for example `com.yourname.chatfort` (replace `yourname` with your own
   name or domain — it just needs to be globally unique)
7. **Update the App Group:**
   - Under **Signing & Capabilities**, find the **App Groups** section
   - Click the existing group `group.com.openui.openui`
   - Click the **−** (minus) button to remove it
   - Click the **+** (plus) button to add a new App Group
   - Enter a matching identifier, e.g., `group.com.yourname.chatfort`
   - Click **OK** — Xcode will register it with your Apple Developer account

### 6c. Select Your Team and Change the Bundle Identifier for the Widget Extension

1. Still in the project editor, click on the **OpenUIWidgetsExtension** target
   (the second target in the list)
2. Click the **Signing & Capabilities** tab
3. Select the same **Team** you chose for the main app
4. **Change the Bundle Identifier** from `com.openui.openui.OpenUIWidget` to
   match your main app's identifier with `.OpenUIWidget` appended, e.g.,
   `com.yourname.chatfort.OpenUIWidget`
5. **Update the App Group** to the same value you used in 6b (e.g.,
   `group.com.yourname.chatfort`) — follow the same remove/add steps

### 6d. Update the App Group in Source Code

The App Group identifier is also hardcoded in one Swift file. It must match the
value you chose above or the widget will not be able to share data with the main
app.

1. In the left sidebar, navigate to **Open UI → Core → Services →
   SharedDataService.swift**
2. Find the line:
   ```swift
   static let appGroupId = "group.com.openui.openui"
   ```
3. Change it to match your App Group, e.g.:
   ```swift
   static let appGroupId = "group.com.yourname.chatfort"
   ```
4. Save the file (**Cmd + S**)

### What "Signing" Means

Every iOS app must be digitally signed to run on a real device. This proves the
app came from a known developer and has not been tampered with. When you select
your Team and set a unique Bundle Identifier, Xcode automatically:
- Creates a signing certificate for you
- Creates a provisioning profile that ties your certificate to the app and your device
- Registers your App Group with Apple
- Signs the app when you build it

You do not need to do any of this manually. Xcode handles it all.

---

## 7. Connect Your iPhone

1. Plug your iPhone into your Mac with a USB cable
2. If your iPhone asks **"Trust This Computer?"** — tap **Trust** and enter your passcode
3. In Xcode, look at the **device selector** in the toolbar (next to the Play button)
4. Click it and select your iPhone from the list
   - It will appear under **iOS Devices** with your iPhone's name
   - If you do not see it, try unplugging and replugging the cable
5. The first time you connect, Xcode may need to prepare your device for development.
   This can take a few minutes. The status bar will show "Preparing device..."

### Enable Developer Mode on Your iPhone (iOS 16+)

If this is your first time using your iPhone for development:

1. On your iPhone, go to **Settings → Privacy & Security**
2. Scroll down and tap **Developer Mode**
3. Toggle it **On**
4. Your iPhone will ask to restart — tap **Restart**
5. After restarting, confirm by tapping **Turn On** when prompted

> If you do not see "Developer Mode" in Settings, connect your iPhone to Xcode
> first. The option appears after Xcode detects the device.

---

## 8. Build and Run

1. Make sure your iPhone is selected in the device selector (top toolbar)
2. Press **Cmd + R** (or click the **Play** button in the top-left)
3. Xcode will:
   - Compile all the Swift code
   - Download and compile the SPM dependencies (first build only — takes longer)
   - Sign the app
   - Install it on your iPhone
   - Launch it

**First build time:** 5-15 minutes depending on your Mac's speed. The SPM
dependencies (especially `mlx-audio-swift`) take a while to compile.

**Subsequent builds:** 30 seconds to 2 minutes (only changed files recompile).

### What to Expect

- The status bar at the top shows build progress
- If the build succeeds, the app launches on your iPhone automatically
- On first launch, the app will ask for your **Open WebUI server URL** — enter it
  and sign in
- The app stays installed permanently on your device (paid developer account)

---

## 9. Distribute to Others

With a paid developer account, you have two ways to get the app onto other
people's devices without them needing a Mac or Xcode.

### Option A: TestFlight (Recommended)

TestFlight lets you distribute the app to up to 10,000 testers. They install it
from the TestFlight app on their iPhone. Builds expire after 90 days but you can
rebuild at any time.

For TestFlight distribution, use the [GitHub Actions build](github_ios_build.md)
instead of Xcode — it handles the entire upload process automatically.

### Option B: Ad Hoc Distribution (UDID-Based, No 90-Day Expiry)

Ad Hoc lets you build an IPA file that can be installed directly on specific
devices. The IPA is valid for 1 year. Each device must have its UDID registered
in your Apple Developer account (up to 100 devices per year).

#### Step 1: Register the Device UDID

Find the UDID of the device you want to install on:

**On the iPhone itself (no computer needed):**
1. Open **Safari** on the iPhone (must be Safari, not Chrome)
2. Go to [udid.tech](https://udid.tech)
3. Tap **Get UDID** and allow the profile download
4. Go to **Settings → General → VPN & Device Management** and install the profile
5. Copy the UDID shown on the website
6. **Delete the profile afterward:** Settings → General → VPN & Device Management → tap the profile → Remove

**Register it in Apple Developer:**
1. Go to [developer.apple.com/account/resources/devices/list](https://developer.apple.com/account/resources/devices/list)
2. Click the **+** button
3. Enter a **Device Name** (e.g., "Sarah's iPhone 15")
4. Enter the **Device ID (UDID)**
5. Click **Continue** → **Register**

#### Step 2: Create an Ad Hoc Provisioning Profile

1. Go to [developer.apple.com/account/resources/profiles/list](https://developer.apple.com/account/resources/profiles/list)
2. Click the **+** button
3. Under **Distribution**, select **Ad Hoc** → click **Continue**
4. Select your app's Bundle Identifier (the one you set in Step 6b, e.g.,
   `com.yourname.chatfort`) → click **Continue**
5. Select your distribution certificate → click **Continue**
6. Select all the devices you want to install on → click **Continue**
7. Name it `ChatFort Ad Hoc` → click **Generate** → **Download**
8. Repeat for the widget: create another Ad Hoc profile for your widget's Bundle
   Identifier (e.g., `com.yourname.chatfort.OpenUIWidget`)

#### Step 3: Archive and Export the IPA from Xcode

1. In Xcode, change the device selector to **Any iOS Device (arm64)**
   (not a specific iPhone or simulator)
2. Go to **Product → Archive**
3. Wait for the archive to complete (5-15 minutes)
4. The **Organizer** window opens showing your archive
5. Click **Distribute App**
6. Select **Ad Hoc** → click **Next**
7. Select your Ad Hoc provisioning profiles when prompted
8. Click **Export**
9. Choose where to save — Xcode creates a folder containing `ChatFort.ipa`

#### Step 4: Install the IPA on the Device

**Using Finder (Mac):**
1. Connect the target iPhone to your Mac via USB
2. Open Finder, click the iPhone in the sidebar
3. Drag the `ChatFort.ipa` file onto the iPhone in Finder

**Using Apple Configurator 2 (Mac):**
1. Download Apple Configurator 2 from the Mac App Store (free)
2. Connect the iPhone, select it in Apple Configurator
3. Click **Add** → **Apps** → select the IPA file

**Using Diawi (no computer needed):**
1. Go to [diawi.com](https://diawi.com) on your computer
2. Drag the IPA onto the upload area
3. You get a link and QR code
4. Open the link on the target iPhone in Safari, or scan the QR code
5. Tap **Install**

---

## 10. Updating When Upstream Changes

When the original Open Relay repo has updates you want to pull in:

### In Terminal

```bash
cd /path/to/chatfort-ios-open-relay

# 1. Restore original branding
cd "tools/BrandOverride"
./scripts/restore.sh
cd ../..

# 2. Pull the latest from upstream
git pull upstream main

# 3. Create a fresh backup
cd "tools/BrandOverride"
./scripts/backup.sh

# 4. Preview changes
./scripts/override.sh --dry-run

# 5. Apply ChatFort branding
./scripts/override.sh --apply
cd ../..
```

### In Xcode

6. Xcode may prompt you to resolve updated packages — click **Resolve** if asked
7. Press **Cmd + R** to build and run with the latest changes

### Setting Up the Upstream Remote (One Time)

If you have not done this before, you need to tell Git where the original repo is:

```bash
cd /path/to/chatfort-ios-open-relay
git remote add upstream https://github.com/Ichigo3766/Open-Relay.git
```

You only need to do this once. After that, `git pull upstream main` will work.

---

## 11. Troubleshooting

### "No such module" or "Missing package product" errors

SPM dependencies did not download properly.

1. Go to **File → Packages → Reset Package Caches**
2. Then **File → Packages → Resolve Package Versions**
3. Wait for all packages to download
4. Try building again (Cmd + R)

### "Signing requires a development team" or "No profiles found" or "Communication with Apple failed"

You either did not select a Team, or the Bundle Identifier / App Group still
uses the upstream defaults that belong to a different Apple Developer account.

1. Click on the **Open UI** project in the left sidebar
2. Select the target that has the error
3. Go to **Signing & Capabilities**
4. Select your Team from the dropdown
5. Make sure the **Bundle Identifier** is unique to your account (not
   `com.openui.openui` — see Step 6b)
6. Make sure the **App Group** matches what you set in Step 6b (not
   `group.com.openui.openui`)
7. If you changed the App Group, also update `SharedDataService.swift` (Step 6d)

### "Could not launch — device not available" or "device is busy"

1. Make sure your iPhone is unlocked
2. Make sure you tapped "Trust This Computer" on your iPhone
3. Try unplugging and replugging the USB cable
4. Try restarting Xcode (Cmd + Q, then reopen)

### Build succeeds but app crashes on launch

1. Check the **Console** output at the bottom of Xcode for error messages
2. Make sure your iPhone is running iOS 18.0 or later
3. Try **Product → Clean Build Folder** (Shift + Cmd + K), then build again

### "Developer Mode" does not appear in iPhone Settings

1. Connect your iPhone to your Mac via USB
2. Open Xcode
3. The option should appear in Settings → Privacy & Security after Xcode detects the device
4. If it still does not appear, restart your iPhone

### Build takes extremely long (30+ minutes)

The first build compiles all SPM dependencies from source. This is normal and only
happens once. Subsequent builds are much faster.

If it is consistently slow:
- Close other apps to free up RAM
- Make sure your Mac has at least 8 GB of free disk space
- Check that you are not running on battery with Low Power Mode enabled

### Xcode says "Unable to install" or "iPhone is not available"

1. Make sure your iPhone's iOS version is 18.0 or later
2. Make sure your Xcode version is 16.0 or later
3. Go to **Xcode → Settings → Platforms** and check that the iOS platform is installed
4. If needed, click the **+** button to download the iOS 18 platform

### "Multiple commands produce" errors for Info.plist, PRIVACY.md, or Swift files

The supported layout keeps `BrandOverride` at `tools/BrandOverride/`, outside the
synchronized `Open UI/` source tree. That prevents Xcode 16 from discovering the
backup copies of Swift files, plists, and docs during the app build.

If you still see this error, you probably have an old in-tree BrandOverride copy
or stale build artifacts. Fix it with:

1. Make sure the only supported tooling folder is `tools/BrandOverride/`
2. Remove any leftover in-tree BrandOverride copy from the source tree
3. In Xcode, run **Product → Clean Build Folder** (Shift + Cmd + K)
4. If needed, delete DerivedData for this project and build again

### The app still shows "Open Relay" somewhere

The brand override scripts may not have been applied. Run:

```bash
cd "tools/BrandOverride"
./scripts/override.sh --dry-run   # preview
./scripts/override.sh --apply     # apply
```

Then rebuild in Xcode.

---

## Quick Reference

| Action | How |
|---|---|
| Open the project | Double-click `Open UI.xcodeproj` |
| Build and run | Cmd + R |
| Stop the app | Cmd + . |
| Clean build folder | Shift + Cmd + K |
| Archive for distribution | Product → Archive |
| Resolve packages | File → Packages → Resolve Package Versions |
| Reset package cache | File → Packages → Reset Package Caches |
| Select device | Click the device name in the top toolbar |
| View console output | View → Debug Area → Activate Console |
| Xcode settings | Cmd + , |
| Add Apple ID | Xcode → Settings → Accounts → + |

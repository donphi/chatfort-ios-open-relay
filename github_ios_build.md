# Building ChatFort with GitHub Actions — Complete Guide

Build ChatFort entirely in the cloud using GitHub Actions and Fastlane. No Mac
required. No Xcode required. This is the same approach used by **LoopKit/Loop**
and **nightscout/Trio** — battle-tested by thousands of non-developer users
building insulin delivery apps from forks.

---

## Table of Contents

1. [How It Works](#1-how-it-works)
2. [What You Need Before Starting](#2-what-you-need-before-starting)
3. [Step 1: Collect the Four Apple Secrets](#3-step-1-collect-the-four-apple-secrets)
4. [Step 2: Collect the GitHub Secret (GH_PAT)](#4-step-2-collect-the-github-secret-gh_pat)
5. [Step 3: Make Up a Password (MATCH_PASSWORD)](#5-step-3-make-up-a-password-match_password)
6. [Step 4: Create the Match-Secrets Repository](#6-step-4-create-the-match-secrets-repository)
7. [Step 5: Add Secrets to Your Repository](#7-step-5-add-secrets-to-your-repository)
8. [Step 6: Add the ENABLE_NUKE_CERTS Variable](#8-step-6-add-the-enable_nuke_certs-variable)
9. [Step 7: Run "Add Identifiers" Workflow](#9-step-7-run-add-identifiers-workflow)
10. [Step 8: Create the App in App Store Connect](#10-step-8-create-the-app-in-app-store-connect)
11. [Step 9: Run "Build ChatFort" Workflow](#11-step-9-run-build-chatfort-workflow)
12. [Step 10: Install on Your iPhone via TestFlight](#12-step-10-install-on-your-iphone-via-testflight)
13. [Ad Hoc Builds (UDID-Based, No 90-Day Expiry)](#13-ad-hoc-builds-udid-based-no-90-day-expiry)
14. [The Update Loop (When Upstream Changes)](#14-the-update-loop-when-upstream-changes)
15. [Automatic Builds and Sync](#15-automatic-builds-and-sync)
16. [Secrets Reference Template](#16-secrets-reference-template)
17. [Troubleshooting](#17-troubleshooting)

---

## 1. How It Works

```
You only need 6 secrets. Fastlane handles everything else automatically.

┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│   Apple Developer Account ──► 4 secrets (TEAMID, API key info)   │
│   GitHub Account ──────────► 1 secret  (GH_PAT)                  │
│   You make one up ─────────► 1 secret  (MATCH_PASSWORD)          │
│                                                                  │
│   Add them to GitHub ──► Run workflow ──► App on TestFlight      │
│                                                                  │
│   Fastlane Match automatically:                                  │
│     • Creates signing certificates                               │
│     • Creates provisioning profiles                              │
│     • Stores them encrypted in a private Git repo                │
│     • Renews them when they expire                               │
│     • Increments build numbers                                   │
│     • Uploads to TestFlight                                      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Two distribution options:**

| | TestFlight (Primary) | Ad Hoc (Optional) |
|---|---|---|
| **How testers install** | TestFlight app (auto-updates) | Manual IPA install |
| **Build expiry** | 90 days (auto-rebuild keeps it fresh) | 1 year |
| **Device registration** | Not needed | Must register each UDID |
| **Max testers** | 10,000 | 100 devices/year |
| **Apple review** | First external build only | None |
| **Triggered by** | Manual or automatic schedule | Manual only |

---

## 2. What You Need Before Starting

| Requirement | Cost | Notes |
|---|---|---|
| Apple Developer Account | $99/year | [developer.apple.com](https://developer.apple.com) — if you just signed up, wait until the account is fully active (can take 1-2 days) |
| GitHub Account | Free | [github.com/signup](https://github.com/signup) |
| A web browser | Free | Any browser on any device — no Mac or Xcode needed |
| A plain text editor | Free | TextEdit (Mac), Notepad (Windows), or any code editor. Do NOT use Word or Google Docs — they change characters silently |

**Save your secrets as you go.** Create a file called `MySecrets.txt` in a safe
place and paste each secret into it as you collect them. You will need to copy
and paste these values later. See the [template](#16-secrets-reference-template)
at the end of this guide.

---

## 3. Step 1: Collect the Four Apple Secrets

You need four values from your Apple Developer account. Log in at
[developer.apple.com/account](https://developer.apple.com/account).

### Secret 1: TEAMID

1. Go to [developer.apple.com/account](https://developer.apple.com/account)
2. Click **Membership Details** in the left sidebar (or on the main page)
3. Find **Team ID** — it is a 10-character alphanumeric code like `A1B2C3D4E5`
4. Click it or select it and **copy** it (do NOT type it by hand — an `8` looks like a `B`)
5. Paste it into your secrets file as `TEAMID`

> If you see a prompt to accept a new agreement, accept it before continuing.

### Secrets 2, 3, 4: The API Key (FASTLANE_ISSUER_ID, FASTLANE_KEY_ID, FASTLANE_KEY)

These three secrets come from creating a single API key in App Store Connect.

1. Open [appstoreconnect.apple.com/access/integrations/api](https://appstoreconnect.apple.com/access/integrations/api) in a new tab
2. Click the **Integrations** tab at the top
3. If this is your first time, you will see "Permission is required to access the App Store Connect API" — click **Request Access** and wait for it to be granted
4. Click **Generate API Key** (or the blue **+** button)
5. For the name, enter: **`FastLane API Key`**
6. For access, select: **Admin**
7. Click **Generate**

Now save three values from this screen:

**FASTLANE_ISSUER_ID:**
- Above the key list, you will see **Issuer ID** with a **Copy** button next to it
- Click **Copy**
- Paste into your secrets file as `FASTLANE_ISSUER_ID`
- It looks like: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

**FASTLANE_KEY_ID:**
- Hover over your key row — a **Copy Key ID** button appears
- Click it
- Paste into your secrets file as `FASTLANE_KEY_ID`
- It looks like: `AAAAAAAAAA` (10 characters)

**FASTLANE_KEY:**
- Click **Download API Key** — you will be warned you can only download this **once**
- Save the file (it will be named `AuthKey_XXXXXXXXXX.p8`)
- Open the file in a text editor (on Mac: right-click → Open With → TextEdit)
- Select **all** the text (Cmd+A on Mac, Ctrl+A on Windows) and **copy** it
- Paste into your secrets file as `FASTLANE_KEY`
- It looks like:
  ```
  -----BEGIN PRIVATE KEY-----
  MIGTAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQg...
  ...several lines of random characters...
  -----END PRIVATE KEY-----
  ```
- You MUST include the `-----BEGIN PRIVATE KEY-----` and `-----END PRIVATE KEY-----` lines

> **CRITICAL:** You can only download the `.p8` file **once**. If you lose it, you
> must delete the key and create a new one. Save it immediately and keep a backup.

---

## 4. Step 2: Collect the GitHub Secret (GH_PAT)

1. Log into [github.com](https://github.com)
2. Open this link in a new tab: [github.com/settings/tokens/new](https://github.com/settings/tokens/new)
3. You may be asked to confirm your password
4. Fill in:
   - **Note:** `ChatFort Build`
   - **Expiration:** Select **No expiration** (a yellow warning will appear — ignore it)
5. Under **Select scopes**, check these two boxes:
   - ✅ **repo** (this will auto-check several sub-items — that is correct)
   - ✅ **workflow**
6. Scroll all the way to the bottom and click **Generate token**
7. **Copy the token immediately** — you will never see it again after leaving this page
8. Paste into your secrets file as `GH_PAT`
9. It looks like: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

> If you lose this token, you can create a new one at the same link. But then you
> must update the `GH_PAT` secret in every repository that uses it.

---

## 5. Step 3: Make Up a Password (MATCH_PASSWORD)

Make up a password and save it as `MATCH_PASSWORD` in your secrets file.

This password encrypts your signing certificates when Fastlane stores them in
your Match-Secrets repository. It can be anything you want.

**Suggestions:**
- At least 15 characters
- Mix uppercase, lowercase, numbers, and symbols
- Do not use your name or birthday
- Example: `Kj8#mP2$vL9@nQ4!`

> Use the same `MATCH_PASSWORD` for every app you build. If you change it later,
> you will need to nuke and recreate your certificates.

---

## 6. Step 4: Create the Match-Secrets Repository

Fastlane Match stores your encrypted certificates and provisioning profiles in a
private Git repository. You need to create this repository.

1. Go to [github.com/new](https://github.com/new)
2. Fill in:
   - **Repository name:** `Match-Secrets`
   - **Description:** (leave blank or enter anything)
   - **Visibility:** Select **Private** (this is critical — your certificates are stored here)
3. Do NOT check "Add a README file" — leave the repo completely empty
4. Click **Create repository**

That is it. Fastlane will populate this repository automatically during the first
build. You do not need to add anything to it.

---

## 7. Step 5: Add Secrets to Your Repository

Now add all 6 secrets to your ChatFort fork on GitHub.

1. Go to your ChatFort repository: `https://github.com/YOUR_USERNAME/chatfort-ios-open-relay`
2. Click **Settings** (tab at the top of the repo page)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. For each secret below, click **New repository secret**, enter the exact **Name** and paste the **Value**, then click **Add secret**

| # | Secret Name | What to Paste |
|---|---|---|
| 1 | `TEAMID` | Your 10-character Apple Team ID |
| 2 | `FASTLANE_ISSUER_ID` | The Issuer ID (UUID format) |
| 3 | `FASTLANE_KEY_ID` | The Key ID (10 characters) |
| 4 | `FASTLANE_KEY` | The entire contents of the `.p8` file (including BEGIN/END lines) |
| 5 | `GH_PAT` | Your GitHub Personal Access Token |
| 6 | `MATCH_PASSWORD` | The password you made up |

After adding all 6, your repository's **Actions secrets** page should show exactly
these 6 names. If any are missing, the build will fail.

> **Using a GitHub Organization?** If you plan to build multiple apps (like Loop
> users do), create a free GitHub Organization and add the secrets there instead.
> Then every repo in the organization can use the same secrets. See
> [GitHub's docs on organization secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets#creating-encrypted-secrets-for-an-organization).

---

## 8. Step 6: Add the ENABLE_NUKE_CERTS Variable

This variable tells the workflow to automatically renew certificates when they
expire (after 1 year). Without it, you would have to manually intervene.

1. On the same **Settings → Secrets and variables → Actions** page
2. Click the **Variables** tab (next to the Secrets tab)
3. Click **New repository variable**
4. Name: `ENABLE_NUKE_CERTS`
5. Value: `true`
6. Click **Add variable**

---

## 9. Step 7: Run "Add Identifiers" Workflow

This workflow creates the App IDs (identifiers) in your Apple Developer account
automatically. You only need to run this once.

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. In the left sidebar, click **1. Add Identifiers**
4. Click the **Run workflow** dropdown (right side)
5. Make sure the branch is **main**
6. Click the green **Run workflow** button
7. Wait for it to complete (usually 1-2 minutes)

**What this does behind the scenes:**
- Creates the App ID `com.openui.openui` with Push Notifications and App Groups capabilities
- Creates the App ID `com.openui.openui.OpenUIWidget` with App Groups capability
- These appear in your Apple Developer account under Certificates, Identifiers & Profiles → Identifiers

> If this fails, check that your `TEAMID`, `FASTLANE_KEY_ID`, `FASTLANE_ISSUER_ID`,
> and `FASTLANE_KEY` are correct. The most common error is a wrong Team ID or an
> API key without Admin access.

---

## 10. Step 8: Create the App in App Store Connect

This is the one step that must be done manually in a browser. You are creating the
app record that TestFlight will use.

1. Go to [appstoreconnect.apple.com/apps](https://appstoreconnect.apple.com/apps)
2. Click the **+** (plus) button → select **New App**
3. Fill in:

| Field | What to Enter |
|---|---|
| **Platforms** | Check **iOS** |
| **Name** | `ChatFort` |
| **Primary Language** | English (U.S.) — or your preferred language |
| **Bundle ID** | Select `com.openui.openui` from the dropdown (created in Step 7) |
| **SKU** | `chatfort` (any unique string — this is internal, not shown to users) |
| **User Access** | **Full Access** |

4. Click **Create**

> **If you do not see `com.openui.openui` in the Bundle ID dropdown:**
> - Go back and make sure the "Add Identifiers" workflow completed successfully
> - It can take a few minutes for new identifiers to appear
> - Try refreshing the page

### Set Up TestFlight Internal Testing

1. Click on your **ChatFort** app in App Store Connect
2. Click the **TestFlight** tab
3. In the left sidebar under **Internal Testing**, click the **+** button
4. Enter a group name: `Internal Testers`
5. Check **Enable automatic distribution** (new builds go to testers automatically)
6. Click **Create**
7. Click **Add Testers** → select yourself (and anyone else on your team)
8. Click **Add**

---

## 11. Step 9: Run "Build ChatFort" Workflow

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. In the left sidebar, click **4. Build ChatFort**
4. Click the **Run workflow** dropdown
5. For **Distribution method**, select **testflight** (the default)
6. Click the green **Run workflow** button

The build takes approximately **15-30 minutes**. You can watch progress by clicking
on the running workflow.

**What happens during the build:**

| Step | What It Does | Time |
|---|---|---|
| Check status | Validates secrets, checks for upstream updates | ~1 min |
| Check certificates | Validates/creates signing certificates via Fastlane Match | ~2 min |
| Select Xcode | Picks the right Xcode version on the macOS runner | ~5 sec |
| Install dependencies | Installs Fastlane via Bundler | ~1 min |
| Build & Archive | Compiles the app, signs it, creates the IPA | 10-20 min |
| Upload to TestFlight | Sends the signed IPA to App Store Connect | 2-5 min |

---

## 12. Step 10: Install on Your iPhone via TestFlight

1. On your iPhone, download **TestFlight** from the App Store (it is free)
2. Open TestFlight
3. You should see **ChatFort** listed
4. Tap **Install**
5. The app appears on your home screen

> **First build:** It can take 10-30 minutes after the GitHub Actions upload
> completes for the build to appear in TestFlight. Apple processes it on their end.

> **"Missing Compliance" warning:** If you see this in App Store Connect, click
> **Manage** on the build and answer the encryption questions. Most apps that only
> use HTTPS can select "No" for custom encryption.

---

## 13. Ad Hoc Builds (UDID-Based, No 90-Day Expiry)

If you want an IPA that does not expire after 90 days, use the Ad Hoc distribution
option. The IPA is valid for 1 year (until the provisioning profile expires).

**Limitation:** Every device that will install the app must have its UDID registered
in your Apple Developer account. You can register up to 100 devices per year.

### Register Device UDIDs

**Find the UDID — Method 1 (on the iPhone itself, no computer needed):**

1. Open **Safari** on the iPhone (must be Safari, not Chrome)
2. Go to [udid.tech](https://udid.tech)
3. Tap **Get UDID**
4. Allow the profile download when prompted
5. Go to **Settings → General → VPN & Device Management** and install the profile
6. Your UDID appears on the website — copy it
7. **Delete the profile afterward:** Settings → General → VPN & Device Management → tap the profile → Remove

**Find the UDID — Method 2 (using Finder on macOS Catalina+):**

1. Connect the iPhone to your Mac with a USB cable
2. Open **Finder** and click the iPhone in the sidebar
3. Click the text below the device name repeatedly until **UDID** appears
4. Right-click the UDID → **Copy**

**Register the UDID in Apple Developer:**

1. Go to [developer.apple.com/account/resources/devices/list](https://developer.apple.com/account/resources/devices/list)
2. Click the **+** button
3. Enter a **Device Name** (e.g., `Donald's iPhone 15`)
4. Enter the **Device ID (UDID)** you copied
5. Click **Continue** → **Register**

### Build Ad Hoc

1. Go to **Actions** → **4. Build ChatFort** → **Run workflow**
2. For **Distribution method**, select **adhoc**
3. Click **Run workflow**
4. When the build completes, go to the workflow run page
5. Scroll to the bottom — under **Artifacts**, download **build-artifacts**
6. Inside the zip you will find `ChatFort.ipa`

### Install the IPA

**Option A — Using Finder (Mac):**
1. Connect the iPhone to your Mac
2. Open Finder, click the iPhone in the sidebar
3. Drag the `ChatFort.ipa` file onto the iPhone in Finder

**Option B — Using Apple Configurator 2 (Mac):**
1. Download Apple Configurator 2 from the Mac App Store (free)
2. Connect the iPhone, select it in Apple Configurator
3. Click **Add** → **Apps** → select the IPA file

**Option C — Using Diawi (no computer needed):**
1. Go to [diawi.com](https://diawi.com) on your computer
2. Drag the IPA onto the upload area
3. You get a link and QR code
4. Open the link on the iPhone in Safari, or scan the QR code
5. Tap **Install**

---

## 14. The Update Loop (When Upstream Changes)

When the original Open Relay repo has updates you want:

### On Your Computer (Terminal)

```bash
cd /path/to/chatfort-ios-open-relay

# 1. Restore original branding (undo ChatFort changes)
cd "tools/BrandOverride"
./scripts/restore.sh
cd ../..

# 2. Pull the latest from upstream
git pull upstream main

# 3. Create a fresh backup of the new upstream files
cd "tools/BrandOverride"
./scripts/backup.sh

# 4. Preview the branding changes
./scripts/override.sh --dry-run

# 5. Apply ChatFort branding
./scripts/override.sh --apply
cd ../..

# 6. Commit and push
git add -A
git commit -m "Apply ChatFort branding to upstream update"
git push origin main
```

### Then on GitHub

7. Go to **Actions** → **4. Build ChatFort** → **Run workflow** → **testflight**
8. Wait for the build to complete (~15-30 min)
9. Open TestFlight on your iPhone — the update appears automatically

> **Or let the automation handle it:** The workflow checks for upstream changes
> every Sunday. If it finds new commits, it syncs and builds automatically. See
> the next section.

---

## 15. Automatic Builds and Sync

The workflow is configured to run automatically:

| Schedule | What Happens |
|---|---|
| **Every Sunday at 07:33 UTC** | Checks if the upstream repo has new commits. If yes, syncs your fork and triggers a build. |
| **2nd Sunday of each month** | Builds regardless of whether there are new commits. This keeps your TestFlight build fresh (prevents the 90-day expiry). |

**To disable automatic builds:** Add a repository variable `SCHEDULED_BUILD` with
value `false`.

**To disable automatic sync:** Add a repository variable `SCHEDULED_SYNC` with
value `false`.

**To re-enable:** Delete the variable or set it to `true`.

> **Important:** GitHub disables scheduled workflows on repositories with no
> activity for 60 days. If this happens, go to the Actions tab and re-enable
> the workflow. The monthly build keeps the repo active enough to prevent this
> in most cases.

---

## 16. Secrets Reference Template

Save this in a plain text file. Fill in each value as you complete the steps.

```
ChatFort Build Secrets — KEEP THIS FILE SECURE
================================================

Last updated: _______________

APPLE DEVELOPER ACCOUNT
  Email: _______________
  (use your password manager for the password)

## SECRETS (add these to GitHub):

TEAMID
(10 characters, e.g., A1B2C3D4E5)
_______________

FASTLANE_ISSUER_ID
(UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)
_______________

FASTLANE_KEY_ID
(10 characters)
_______________

FASTLANE_KEY
(full contents of the .p8 file)
-----BEGIN PRIVATE KEY-----
_______________
_______________
_______________
-----END PRIVATE KEY-----

GH_PAT
(starts with ghp_)
_______________

MATCH_PASSWORD
(password you made up)
_______________

## VARIABLE (add to GitHub Variables tab):

ENABLE_NUKE_CERTS = true

## GITHUB ACCOUNT:

Username: _______________
Repository: https://github.com/_______________/chatfort-ios-open-relay
Match-Secrets: https://github.com/_______________/Match-Secrets (PRIVATE)

## BUNDLE IDS (for reference, do not change):

Main app: com.openui.openui
Widget:   com.openui.openui.OpenUIWidget
```

---

## 17. Troubleshooting

### "Add Identifiers" workflow fails

**Most likely cause:** One of your Apple secrets is wrong.

- Verify `TEAMID` is exactly 10 characters — copy it from
  [developer.apple.com/account](https://developer.apple.com/account) → Membership Details
- Verify the API key has **Admin** access in App Store Connect
- Verify `FASTLANE_KEY` includes the `-----BEGIN PRIVATE KEY-----` and
  `-----END PRIVATE KEY-----` lines
- Verify `FASTLANE_ISSUER_ID` and `FASTLANE_KEY_ID` match what App Store Connect shows

### "Create Certificates" workflow fails

**Most likely cause:** The `Match-Secrets` repo does not exist or `GH_PAT` cannot
access it.

- Verify you created a **private** repo called `Match-Secrets` under your GitHub account
- Verify `GH_PAT` has `repo` and `workflow` scopes
- Verify `GH_PAT` has not expired (if you set an expiration)

### Build fails with signing errors

**Most likely cause:** Certificates or profiles are not set up yet.

- Run the **3. Create Certificates** workflow manually first
- If that fails, check that the `Match-Secrets` repo exists and is accessible
- If certificates are corrupted, set the `ENABLE_NUKE_CERTS` variable to `true`
  and run **3. Create Certificates** again — it will delete and recreate everything

### Build succeeds but TestFlight upload fails

- Verify you created the app record in App Store Connect (Step 8)
- Verify the Bundle ID is `com.openui.openui`
- Verify the API key has **Admin** access

### Build succeeds but app does not appear in TestFlight

- Apple processes builds after upload — wait 10-30 minutes
- Check App Store Connect → your app → TestFlight tab for processing status
- Check your email for any messages from Apple about the build

### "Missing Compliance" in TestFlight

- In App Store Connect → your app → TestFlight → click the build
- Under "Missing Compliance", click **Manage**
- Answer the encryption questions (most apps using only HTTPS select "No")
- To avoid this on future builds, add the key `ITSAppUsesNonExemptEncryption`
  with value `NO` to your app's Info.plist

### Provisioning profiles or certificates expire

- If you added the `ENABLE_NUKE_CERTS` variable (Step 6), renewal is automatic
- If not, run **3. Create Certificates** manually
- Certificates expire after 1 year; the workflow checks and renews automatically

### Adding a new device for Ad Hoc builds

1. Find the device UDID (see [Ad Hoc section](#13-ad-hoc-builds-udid-based-no-90-day-expiry))
2. Register it at [developer.apple.com/account/resources/devices/list](https://developer.apple.com/account/resources/devices/list)
3. Run **3. Create Certificates** to regenerate profiles that include the new device
4. Run **4. Build ChatFort** with **adhoc** distribution

### The app still shows "Open Relay" somewhere

- Check `tools/BrandOverride/CANNOT_OVERRIDE.md` for items the scripts skip
- The `Localizable.xcstrings` file (translations) is not modified to avoid merge conflicts

### Scheduled builds stopped running

- GitHub disables workflows on repos with no activity for 60 days
- Go to the **Actions** tab and click the banner to re-enable
- Push any commit to reset the inactivity timer

---

## Quick Reference

| What | Where |
|---|---|
| Your secrets | GitHub repo → Settings → Secrets and variables → Actions |
| Your variable | GitHub repo → Settings → Secrets and variables → Actions → Variables tab |
| Run a build | GitHub repo → Actions → 4. Build ChatFort → Run workflow |
| Download Ad Hoc IPA | GitHub repo → Actions → (completed run) → Artifacts → build-artifacts |
| TestFlight builds | [appstoreconnect.apple.com](https://appstoreconnect.apple.com) → your app → TestFlight |
| Registered devices | [developer.apple.com/account/resources/devices/list](https://developer.apple.com/account/resources/devices/list) |
| App identifiers | [developer.apple.com/account/resources/identifiers/list](https://developer.apple.com/account/resources/identifiers/list) |
| Match-Secrets repo | `https://github.com/YOUR_USERNAME/Match-Secrets` (private) |
| Upstream repo | [github.com/Ichigo3766/Open-Relay](https://github.com/Ichigo3766/Open-Relay) |

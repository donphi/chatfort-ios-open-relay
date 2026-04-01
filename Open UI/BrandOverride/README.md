# ChatFort Brand Override

This folder contains everything you need to rebrand the Open Relay iOS app as **ChatFort**
by **donphi**. It includes scripts that automatically swap out the old branding and put it
back when you need to pull updates from the original repo.

---

## The Golden Rule

**You never edit the app's original files by hand.**

The Python scripts in `scripts/` do all the editing for you. They can also undo everything
so you can safely pull updates from the original GitHub repo without conflicts.

This `BrandOverride/` folder is the only place you work directly.

---

## Quick Start (5 Minutes)

### Step 1: Place Your Icon

Put your ChatFort app icon in the `Assets/` folder:

```
Open UI/BrandOverride/Assets/AppIcon.png
```

Requirements:
- **Size:** 1024 x 1024 pixels
- **Format:** PNG
- **Shape:** Square (iOS rounds the corners automatically)
- **No transparency** (iOS does not allow transparent app icons)

### Step 2: Create a Backup

Open Terminal, navigate to the repo, and run:

```bash
cd "Open UI/BrandOverride"
./scripts/backup.sh
```

This saves a copy of every file the scripts will change. You can always get back to this
exact state later.

### Step 3: Preview the Changes

```bash
./scripts/override.sh --dry-run
```

This shows you every single change that will be made, in color:
- **Red** lines = what gets removed (old "Open Relay" text)
- **Green** lines = what gets added (new "ChatFort" text)

Nothing is written to disk. It is just a preview.

### Step 4: Apply the Changes

```bash
./scripts/override.sh --apply
```

This writes all the ChatFort branding into the app files and copies your icon into the
right places.

### Step 5: Build in Xcode

Open the project in Xcode and build. Your app should now say "ChatFort" everywhere.

---

## When the Original Repo Updates

When the upstream Open Relay repo has new features or fixes you want:

```bash
# 1. Put everything back to the original state
./scripts/restore.sh

# 2. Pull the latest from the original repo
git pull upstream main

# 3. Create a fresh backup of the updated files
./scripts/backup.sh

# 4. Preview what the override will do (check for any surprises)
./scripts/override.sh --dry-run

# 5. Apply ChatFort branding again
./scripts/override.sh --apply

# 6. Build in Xcode and verify
```

---

## What is in This Folder

| File/Folder | What It Is |
|-------------|-----------|
| `README.md` | This file. The guide you are reading now. |
| `MANIFEST.md` | Technical reference for AI assistants working on this repo. |
| `CANNOT_OVERRIDE.md` | Line-by-line list of every brand string the scripts change. |
| `brand_config.json` | The single file that controls ALL brand values and replacements. |
| `Assets/` | Where you put your ChatFort icon and any future brand images. |
| `scripts/` | The three Python scripts (backup, restore, override) and their shell wrappers. |
| `backups/` | Created automatically by the backup script. Contains versioned snapshots. |

---

## Master Table: Every Brandable Element

This table lists every single thing in the app that carries branding. The "Handled by Scripts?"
column tells you whether the override script changes it automatically.

### App Identity

| Element | What You See | File | Line | File Type | Current Value | ChatFort Value | Handled by Scripts? |
|---------|-------------|------|------|-----------|---------------|----------------|-------------------|
| Home screen name | The name under the app icon | `project.pbxproj` | 543, 587 | Xcode project | `Open Relay` | `ChatFort` | Yes |
| App icon | The icon on the home screen | `AppIcon.appiconset/IMG_0816.png` | — | PNG image | Open Relay icon | Your icon | Yes (if you place `Assets/AppIcon.png`) |
| In-app icon | Icon shown on About, Login, Onboarding screens | `AppIconImage.imageset/IMG_0816.png` | — | PNG image | Open Relay icon | Your icon | Yes (same source file) |
| Widget icon | Icon in widget gallery and widgets | `OpenUIWidgets/.../IMG_0816.png` | — | PNG image | Open Relay icon | Your icon | Yes (same source file) |

### Screens and UI Text

| Element | What You See | File | Line | File Type | Current Value | ChatFort Value | Handled by Scripts? |
|---------|-------------|------|------|-----------|---------------|----------------|-------------------|
| Login screen title | Big text on the server connection page | `ServerConnectionView.swift` | 234 | Swift | `Open UI` | `ChatFort` | Yes |
| About screen title | Title on the About page | `AboutView.swift` | 122 | Swift | `Open Relay` | `ChatFort` | Yes |
| About screen credits | Small text at the bottom of About | `AboutView.swift` | 103 | Swift | `Made with ❤️ for Open WebUI` | `Designed by donphi` | Yes |
| Settings row label | The "About" row in Settings | `SettingsView.swift` | 223 | Swift | `About Open Relay` | `About ChatFort` | Yes |
| Notification help text | Help text about enabling notifications | `SettingsView.swift` | 1938 | Swift | `...Open Relay → Notifications` | `...ChatFort → Notifications` | Yes |
| Appearance footer | Text under the theme picker | `AppearanceSettingsView.swift` | 23 | Swift | `Choose how Open Relay looks...` | `Choose how ChatFort looks...` | Yes |

### Widgets

| Element | What You See | File | Line | File Type | Current Value | ChatFort Value | Handled by Scripts? |
|---------|-------------|------|------|-----------|---------------|----------------|-------------------|
| Widget gallery name | Name when adding widget | `OpenUIWidgets.swift` | 54, 297 | Swift | `Open Relay` | `ChatFort` | Yes |
| Widget search bar text | "Ask Open Relay" pill in medium widget | `OpenUIWidgets.swift` | 208 | Swift | `Ask Open Relay` | `Ask ChatFort` | Yes |
| Lock screen widget title | Title in rectangular lock screen widget | `OpenUIWidgets.swift` | 324 | Swift | `Open Relay` | `ChatFort` | Yes |
| Lock screen widget description | Description in widget gallery | `OpenUIWidgets.swift` | 298 | Swift | `Quick access to Open Relay...` | `Quick access to ChatFort...` | Yes |
| Lock screen inline label | Inline lock screen widget text | `OpenUIWidgets.swift` | 335 | Swift | `Ask Open Relay` | `Ask ChatFort` | Yes |
| Widget control intent | Siri/Control Center description | `OpenUIWidgetsControl.swift` | 32 | Swift | `...in Open Relay.` | `...in ChatFort.` | Yes |

### Siri and Shortcuts

| Element | What You See | File | Line | File Type | Current Value | ChatFort Value | Handled by Scripts? |
|---------|-------------|------|------|-----------|---------------|----------------|-------------------|
| Channel intent description | Shown in Shortcuts app | `AppIntentsService.swift` | 104 | Swift | `...in Open Relay.` | `...in ChatFort.` | Yes |

### iOS Permission Prompts

These are the popup messages iOS shows when the app asks for camera, microphone, etc.

| Element | What You See | File | Line | File Type | Current Value | ChatFort Value | Handled by Scripts? |
|---------|-------------|------|------|-----------|---------------|----------------|-------------------|
| Camera prompt | "ChatFort needs camera access..." | `project.pbxproj` | 546, 590 | Xcode project | `Open Relay needs camera...` | `ChatFort needs camera...` | Yes |
| Face ID prompt | "ChatFort uses Face ID..." | `project.pbxproj` | 547, 591 | Xcode project | `Open Relay uses Face ID...` | `ChatFort uses Face ID...` | Yes |
| Microphone prompt | "ChatFort needs microphone..." | `project.pbxproj` | 548, 592 | Xcode project | `Open Relay needs microphone...` | `ChatFort needs microphone...` | Yes |
| Save photos prompt | "ChatFort needs permission to save..." | `project.pbxproj` | 549, 593 | Xcode project | `Open Relay needs permission...` | `ChatFort needs permission...` | Yes |
| Photo library prompt | "ChatFort needs photo library..." | `project.pbxproj` | 550, 594 | Xcode project | `Open Relay needs photo library...` | `ChatFort needs photo library...` | Yes |
| Speech recognition prompt | "ChatFort uses speech recognition..." | `project.pbxproj` | 551, 595 | Xcode project | `Open Relay uses speech...` | `ChatFort uses speech...` | Yes |

### About Screen Links

| Element | Where It Goes | File | Line | Current URL | ChatFort URL | Handled by Scripts? |
|---------|--------------|------|------|-------------|-------------|-------------------|
| Source code link | GitHub repo | `AboutView.swift` | 52 | `Ichigo3766/Open-Relay` | `donphi/chatfort-ios-chat-relay` | Yes |
| Privacy policy link | Privacy doc | `AboutView.swift` | 57 | `Ichigo3766/Open-Relay/.../PRIVACY.md` | `donphi/chatfort-ios-chat-relay/.../PRIVACY.md` | Yes |
| Bug report link | Issue template | `AboutView.swift` | 69 | `Ichigo3766/.../bug_report.yml` | `donphi/.../bug_report.yml` | Yes |
| Feature request link | Issue template | `AboutView.swift` | 76 | `Ichigo3766/.../feature_request.yml` | `donphi/.../branding.yml` | Yes |
| UI/UX link | Issue template | `AboutView.swift` | 83 | `Ichigo3766/.../ui_ux.yml` | `donphi/.../branding.yml` | Yes |
| Performance link | Issue template | `AboutView.swift` | 90 | `Ichigo3766/.../performance.yml` | `donphi/.../bug_report.yml` | Yes |
| Question link | Issue template | `AboutView.swift` | 96 | `Ichigo3766/.../question.yml` | `donphi/.../bug_report.yml` | Yes |

### Documentation

| Element | What It Is | File | Line | Current Value | ChatFort Value | Handled by Scripts? |
|---------|-----------|------|------|---------------|----------------|-------------------|
| Privacy policy title | Title of the privacy doc | `PRIVACY.md` | 1 | `Open UI Privacy Policy` | `ChatFort Privacy Policy` | Yes |
| Privacy policy body | References to app name | `PRIVACY.md` | 5, 23, 46 | `Open UI` | `ChatFort` | Yes |
| Privacy policy contact | GitHub link | `PRIVACY.md` | 52 | `Ichigo3766/Open-UI` | `donphi/chatfort-ios-chat-relay` | Yes |
| Info.plist UTType | Share sheet label | `Info.plist` | 112 | `Open Relay Chat Item` | `ChatFort Chat Item` | Yes |

### Theme and Visual Design (NOT Changed by Scripts)

These control colors, spacing, fonts, and animations. They are not "brand strings" but
you can customize them by editing the upstream files directly if desired.

| Element | What It Controls | File | File Type |
|---------|-----------------|------|-----------|
| Color palette (light) | All light mode colors | `Open UI/Shared/Theme/ColorTokens.swift` | Swift |
| Color palette (dark) | All dark mode colors | `Open UI/Shared/Theme/ColorTokens.swift` | Swift |
| Accent color presets | The 12 accent colors in Settings | `Open UI/Core/Services/AppearanceManager.swift` | Swift |
| Spacing grid | Padding, margins, gaps | `Open UI/Shared/Theme/DesignTokens.swift` | Swift |
| Corner radii | How rounded things are | `Open UI/Shared/Theme/DesignTokens.swift` | Swift |
| Typography scale | Font sizes and weights | `Open UI/Shared/Theme/Typography.swift` | Swift |
| Animations | Motion timing and curves | `Open UI/Shared/Theme/Animations.swift` | Swift |
| View styles | Reusable component styles | `Open UI/Shared/Theme/ViewStyles.swift` | Swift |

### Localized Strings (NOT Changed by Scripts)

The file `Open UI/Localizable.xcstrings` contains ~168 lines with "Open Relay" or "Open UI"
across all supported languages. The scripts do not touch this file because:
- It is very large (JSON format, thousands of lines)
- Changes here cause frequent merge conflicts with upstream
- The strings are duplicated across ~30 languages

If you want to change these, see `CANNOT_OVERRIDE.md` for details.

---

## How Each Script Works

### `backup.sh` — Create a Safety Net

**What it does:** Copies every file that the override script will change into a
timestamped folder inside `backups/`. Creates two copies:
- `pristine/` — the untouched originals (used by restore)
- `override/` — identical copies for reference

**When to run:** Before your first override, and after every `git pull` from upstream.

**Example output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  BACKUP: v2.4_build1_2026-04-01_f49448d
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  OK  Open UI.xcodeproj/project.pbxproj  (34,185 bytes)
  OK  Open UI/Features/Settings/Views/AboutView.swift  (6,725 bytes)
  ...
  14 files backed up
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### `restore.sh` — Undo Everything

**What it does:** Copies the `pristine/` files back to their original locations,
undoing all brand changes. After running this, the repo looks exactly like upstream.

**When to run:** Before `git pull upstream main`.

**Options:**
- `./scripts/restore.sh` — uses the most recent backup
- `./scripts/restore.sh --version v2.4_build1_2026-04-01_f49448d` — uses a specific backup

### `override.sh` — Apply ChatFort Branding

**What it does:** Reads `brand_config.json` and makes every string replacement and
icon copy defined there.

**Two modes:**
- `./scripts/override.sh --dry-run` — shows all changes without writing anything (default)
- `./scripts/override.sh --apply` — shows all changes AND writes them to disk

**The dry-run output** shows each change with color coding:
```
━━━━ FILE: Open UI/Features/Settings/Views/AboutView.swift ━━━━
  Line 122:
  - Text("Open Relay")          ← red (being removed)
  + Text("ChatFort")            ← green (being added)
```

---

## Editing brand_config.json

The `brand_config.json` file is the single source of truth. If you want to change any
brand value, edit it here and re-run the override script.

### Changing the App Name

Find the `"brand"` section at the top:

```json
{
  "brand": {
    "app_name": "ChatFort",        ← change this
```

Then update the `"string_replacements"` section to match. Each entry has a `"find"` (the
old text) and `"replace"` (the new text).

### Changing the Icon

Just replace the file at `Assets/AppIcon.png`. The scripts handle copying it to all four
locations in the app.

### Adding a New Replacement

Add a new entry to the appropriate file's `"replacements"` array:

```json
{
  "find": "the exact text to find",
  "replace": "the text to put in its place"
}
```

---

## Troubleshooting

### "Icon source missing" warning

You have not placed your icon yet. Put a 1024x1024 PNG at:
```
Open UI/BrandOverride/Assets/AppIcon.png
```

### "File not found" warning

The upstream file has been moved or renamed in a new version. Check `CANNOT_OVERRIDE.md`
for the expected file paths and update `brand_config.json` if needed.

### Merge conflicts after git pull

You forgot to run `restore.sh` before pulling. Fix it:
```bash
git checkout --theirs .    # accept upstream versions
./scripts/backup.sh        # create new backup
./scripts/override.sh --apply  # re-apply brand
```

### The app still says "Open Relay" somewhere

Check `CANNOT_OVERRIDE.md` — there are some places (like `Localizable.xcstrings`) that
the scripts intentionally skip to avoid merge conflicts. The "NOT Changed" section at the
bottom of that file lists everything left alone and why.

---

## File Types Explained (for Non-Developers)

| Extension | What It Is | How to Open It |
|-----------|-----------|----------------|
| `.swift` | Swift source code (the app's programming language) | Any text editor, or Xcode |
| `.pbxproj` | Xcode project file (settings, targets, build config) | Any text editor (carefully!) |
| `.plist` | Property list (XML config file for iOS apps) | Any text editor, or Xcode |
| `.xcstrings` | String catalog (translations for all languages) | Xcode (has a visual editor) |
| `.xcassets` | Asset catalog folder (contains images, colors) | Xcode (drag and drop images) |
| `.png` | Image file | Any image viewer |
| `.json` | Data file (the brand config) | Any text editor |
| `.py` | Python script | Runs in Terminal with `python3` |
| `.sh` | Shell script | Runs in Terminal with `./filename.sh` |
| `.md` | Markdown document (like this file) | Any text editor, or GitHub |

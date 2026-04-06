# ChatFort Brand Assets

Place your brand assets in this folder. The override script copies them to the
correct locations in the app automatically.

---

## App Icon — Icon Composer (`.icon` Bundle)

The app icon uses Apple's **Icon Composer** format (`.icon`), which supports
Liquid Glass effects, layered depth, and automatic generation of all icon
variants (light, dark, mono/tinted) from a single source file.

### Required File

| Path | What It Is |
|------|-----------|
| `AppIcon.icon/` | Icon Composer bundle — contains `icon.json` + SVG/PNG layers in `Assets/` |

### How to Create or Edit the Icon

1. Open **Icon Composer** (Xcode → Open Developer Tool → Icon Composer)
2. Design your icon with up to 4 layer groups, applying Liquid Glass effects
3. Configure light, dark, and mono appearances inside Icon Composer
4. **Save** as `AppIcon.icon` (File → Save) into this `Assets/` folder

The `.icon` bundle is a folder containing:

```
AppIcon.icon/
  ├── icon.json          # Layer definitions, colors, Liquid Glass settings
  └── Assets/
      ├── layer1.svg     # Individual layer artwork
      ├── layer2.svg
      └── ...
```

### What the Override Script Does

When you run `./scripts/override.sh --apply`, it:

1. Copies `AppIcon.icon/` into `Open UI/AppIcon.icon` and
   `OpenUIWidgets/AppIcon.icon` (Xcode picks these up via filesystem sync)
2. Copies `AppIcon-preview.png` to the two `AppIconImage.imageset/` locations
   (for in-app display on About, Login, Onboarding, and Widget screens)

Xcode generates all home-screen icon sizes, App Store icons, and
backward-compatible flat icons for iOS 18 automatically at build time from the
`.icon` file. You do not need separate PNGs for light, dark, or tinted.

---

## In-App Preview Icon (`AppIcon-preview.png`)

SwiftUI `Image("AppIconImage")` cannot read `.icon` files directly. The app
uses a regular `AppIconImage.imageset` (PNG) to display the icon inside the
app (About screen, Login, Onboarding, Widgets).

### Required File

| Path | What It Is |
|------|-----------|
| `AppIcon-preview.png` | 1024x1024 PNG exported from Icon Composer for in-app display |

### How to Export

**Option A — Manual export (recommended for local builds):**

1. Open your `AppIcon.icon` in Icon Composer
2. Select **iOS** platform and **Default** (light) appearance
3. Choose **File → Export**
4. Save as `AppIcon-preview.png` in this `Assets/` folder

**Option B — Automatic via `ictool` (used by CI):**

If `AppIcon-preview.png` is missing when you run the override script, it will
attempt to generate it automatically using `ictool` (bundled with Xcode 26+).
This is how the GitHub Actions CI build works — no manual export needed.

### Specifications

| Property | Requirement |
|----------|-------------|
| Size | 1024 x 1024 pixels |
| Format | PNG |
| Color space | sRGB or Display P3 |

---

## Tips for Creating Icons in Icon Composer

- Start with the Apple Design Resources template (1024x1024 canvas)
- Use SVG layers for maximum scalability (PNG layers also work)
- Separate your design into up to 4 groups for depth effects
- Apply Liquid Glass effects (specular, blur, translucency) in Icon Composer,
  not in your design tool
- Preview all three appearances (Default, Dark, Mono) before saving
- Test at small sizes using the preview size selector in Icon Composer
- Apple's Human Interface Guidelines:
  https://developer.apple.com/design/human-interface-guidelines/app-icons

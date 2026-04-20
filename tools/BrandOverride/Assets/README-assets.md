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

---

## Custom Fonts (`Fonts/`)

Three font families replace the system fonts (SF Pro, SF Pro Rounded, SF Mono):

```
Fonts/
  main/                         Replaces SF Pro (.default design)
    StyreneB-Thin.otf           PostScript: StyreneB-Thin
    StyreneB-Light.otf          PostScript: StyreneB-Light
    StyreneB-Regular.otf        PostScript: StyreneB-Regular
    StyreneB-Medium.otf         PostScript: StyreneB-Medium
    StyreneB-Bold.otf           PostScript: StyreneB-Bold
    StyreneB-Black.otf          PostScript: StyreneB-Black
  round/                        Replaces SF Pro Rounded (.rounded design)
    CircularStd-Book.otf        PostScript: CircularStd-Book
    CircularStd-Medium.otf      PostScript: CircularStd-Medium
    CircularStd-Bold.otf        PostScript: CircularStd-Bold
  mono/                         Replaces SF Mono (.monospaced design)
    ApercuMonoProRegular.otf    PostScript: ApercuMonoPro-Regular
    ApercuMonoProMedium.otf     PostScript: ApercuMonoPro-Medium
    ApercuMonoProBold.otf       PostScript: ApercuMonoPro-Bold
```

### Weight Mapping

Styrene B has no `.semibold` variant. Both `.semibold` and `.bold` map to `StyreneB-Bold`.

| SwiftUI Weight | Styrene B | Circular Std | Apercu Mono Pro |
|----------------|-----------|--------------|-----------------|
| `.thin` / `.ultraLight` / `.light` | StyreneB-Light | CircularStd-Book | ApercuMonoPro-Regular |
| `.regular` | StyreneB-Regular | CircularStd-Book | ApercuMonoPro-Regular |
| `.medium` | StyreneB-Medium | CircularStd-Medium | ApercuMonoPro-Medium |
| `.semibold` | StyreneB-Bold | CircularStd-Medium | ApercuMonoPro-Bold |
| `.bold` | StyreneB-Bold | CircularStd-Bold | ApercuMonoPro-Bold |
| `.heavy` / `.black` | StyreneB-Black | CircularStd-Bold | ApercuMonoPro-Bold |

### What the Override Script Does

The `07_custom_fonts.json` config:

1. **Copies** all 12 `.otf` files to `Open UI/Resources/Fonts/` (Xcode's filesystem
   sync automatically bundles them — no `project.pbxproj` changes needed)
2. **Copies** 2 widget-used fonts to `OpenUIWidgets/Fonts/`
3. **Injects** `UIAppFonts` arrays into both `Info.plist` files (required for iOS to
   load the fonts)
4. **Rewrites** `Typography.swift` with a `customFont()` helper that maps
   `Font.Weight` × `Font.Design` to PostScript names
5. **Replaces** all direct `.font(.system(...))` text calls in 8+ Swift files
6. **Prepends** custom font names to CSS `font-family` stacks in `HTMLPreviewView`

### Swapping to a Different Custom Font

To use different fonts:

1. Replace the `.otf` files in `Fonts/main/`, `Fonts/round/`, and `Fonts/mono/`
2. Run `fc-scan --format '%{postscriptname}\n' YourFont.otf` to get PostScript names
3. Update all PostScript name strings in `07_custom_fonts.json`
4. Run `./scripts/override.sh --dry-run` to verify

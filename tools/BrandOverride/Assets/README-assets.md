# ChatFort Brand Assets

Place your brand image files in this folder. The override script will copy them
to the correct locations in the app and update the asset catalog JSON automatically.

## App Icon — Three Variants

iOS 18+ supports three icon appearances: light (default), dark, and tinted.
Export all three from Icon Composer and place them here.

### Required Files

| Filename | Appearance | What iOS Uses It For |
|----------|------------|---------------------|
| `AppIcon-light.png` | Light (default) | Home screen on light wallpapers, App Store, in-app display |
| `AppIcon-dark.png` | Dark | Home screen on dark wallpapers (iOS 18+) |
| `AppIcon-tinted.png` | Tinted | Monochrome tinted icon colored by user's tint (iOS 18+) |

### Specifications (All Three)

| Property | Requirement |
|----------|-------------|
| Size | 1024 x 1024 pixels |
| Format | PNG |
| Color space | sRGB |
| Shape | Square (iOS adds rounded corners automatically) |

### Per-Variant Notes

**Light (`AppIcon-light.png`):**
- Your full-color default icon
- No transparency (iOS rejects transparent app icons)
- This is also used for in-app display (About screen, Onboarding, Login, Widgets)

**Dark (`AppIcon-dark.png`):**
- Your dark mode variant — typically darker background, lighter/brighter elements
- No transparency
- If you skip this file, iOS uses the light icon on dark wallpapers

**Tinted (`AppIcon-tinted.png`):**
- A grayscale silhouette/shape that iOS will colorize with the user's chosen tint
- White areas become the tint color, black areas stay dark
- Design it as a single-layer grayscale shape
- If you skip this file, iOS uses the light icon for tinted mode

### What the Override Script Does

When you run `./scripts/override.sh --apply`, it:

1. Copies `AppIcon-light.png` to all four `IMG_0816.png` locations (main app + widget, icon + in-app image)
2. Copies `AppIcon-dark.png` into the two `AppIcon.appiconset/` folders (main app + widget)
3. Copies `AppIcon-tinted.png` into the two `AppIcon.appiconset/` folders (main app + widget)
4. Updates `Contents.json` in both `AppIcon.appiconset/` folders to reference the dark and tinted filenames

You only need to provide the PNGs — the script handles all the wiring.

### Partial Support

You do not need all three variants. The script handles whatever you provide:

- **Light only:** Just place `AppIcon-light.png`. Dark and tinted slots stay empty (iOS uses light for everything).
- **Light + Dark:** Place both. Tinted slot stays empty.
- **All three:** Place all three for full iOS 18+ icon support.

### Legacy Fallback

If you have a single icon and don't want variants, you can also just name it
`AppIcon-light.png` and skip the other two. The result is identical to the
old single-icon behavior.

## Tips for Creating Icons

- Design at 1024x1024 but check how it looks at small sizes (60x60, 40x40, 29x29)
- Avoid fine text — it becomes unreadable at small sizes
- Use bold, simple shapes with good contrast
- Test on both light and dark wallpapers
- Apple's Human Interface Guidelines: https://developer.apple.com/design/human-interface-guidelines/app-icons

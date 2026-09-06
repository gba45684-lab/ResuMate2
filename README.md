# ResuMate2

ResuMate2 is a Capacitor Android app whose UI runs from a web bundle. The project is intentionally kept simple: **one canonical UI source, one web build command, one OTA workflow, and one native APK workflow**.

## Architecture

```text
www/app-source.html       <- ONLY canonical UI/feature source
        |
        v
scripts/build-web.py      <- ONE deterministic web build entry point
        |
        +-- patch-web.py
        +-- patch-ota-whats-new.py
        +-- finalize-export-ui.py
        +-- bundle-runtime-libs.py
        +-- patch-theme-preview.py
        |
        v
www/index.html            <- generated web bundle; do not edit manually
        |
        +--> OTA branch    <- installed app updates web layer without APK reinstall
        |
        +--> Capacitor     <- packaged by native APK build

scripts/patch-android.py
scripts/patch-android-ui.py
scripts/patch-android-icon.py
        |
        v
Android native layer      <- only needed for native/device behavior
```

## Golden rules

1. **Edit `www/app-source.html` for normal UI, features, navigation and business logic.**
2. **Never manually edit generated `www/index.html`.** Run `npm run build:web` instead.
3. Keep native Android changes in the three `patch-android*.py` scripts; do not mix native fixes into the web source.
4. OTA changes are web-layer changes and normally do **not** require a new APK.
5. Changes to Android/native behavior require a new APK.
6. Do not use global `pointer-events` or mutation-observer hacks to repair touch behavior. Fix the actual component/event logic.
7. Keep the approved `ResuMate_Final_Aligned_Functional.html` visual design locked; refactoring must not redesign the UI.

## Commands

```bash
npm ci
npm run build:web       # build and validate the web bundle
npm test                # same deterministic web validation
npm run android:debug   # package the current web app into a debug APK
```

## OTA flow

A push to `main` runs `.github/workflows/main.yml`. It builds the bundle from `www/app-source.html`, validates it, generates the OTA manifest, and publishes the web bundle to the `ota` branch.

Installed apps poll the OTA manifest and can receive web UI/feature fixes without reinstalling the APK.

## Native flow

`.github/workflows/native-apk.yml` creates the Android platform when needed, syncs Capacitor, applies only the native patches, and builds a signed debug APK for testing. Native changes require installing the new APK.

## Important files

| Purpose | File |
|---|---|
| Canonical app | `www/app-source.html` |
| Generated web bundle | `www/index.html` |
| Offline fallback | `www/fallback.html` |
| OTA bootstrap | `www/ota-loader.html` |
| Web build entry point | `scripts/build-web.py` |
| Web workflow | `.github/workflows/main.yml` |
| Native workflow | `.github/workflows/native-apk.yml` |
| Native bridge patch | `scripts/patch-android.py` |
| Native status-bar patch | `scripts/patch-android-ui.py` |
| Native icon patch | `scripts/patch-android-icon.py` |

## Updating ResuMate

For a normal UI or feature fix:

```bash
# edit only this file
www/app-source.html

# validate/build
npm run build:web

# commit and push to main
```

The OTA workflow handles publication automatically. **Do not create a new APK for web-only fixes.**

For a native Android fix, run the native workflow and install the resulting APK.

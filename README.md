# ResuMate — Android APK

ResuMate is a lightweight Capacitor Android app that packages the web app in `www/index.html` into an installable APK.

## Clean project structure

`www/index.html` is the **single canonical app entry point**. The duplicate root `index.html` has been removed so the app cannot accidentally build from two different HTML copies.

Core files:

- `www/index.html` — current ResuMate UI/app
- `capacitor.config.json` — app ID/name configuration
- `package.json` / `package-lock.json` — Capacitor dependencies and build scripts
- `.github/workflows/main.yml` — automatic GitHub Actions APK build
- `settings.gradle` / `proguard-rules.pro` — Android build configuration

The repository currently contains one HTML app source: `www/index.html`.

## Build APK automatically

Every push to `main` starts the **Build ResuMate APK** GitHub Actions workflow. It:

1. Installs Node.js 24 and Java 21.
2. Runs `npm ci`.
3. Verifies the clean project structure.
4. Creates the Android platform when `android/` is not present.
5. Runs `npx cap sync android` so the latest `www/index.html` is packaged.
6. Runs `./gradlew assembleDebug`.
7. Uploads `resumate-debug-apk` as a downloadable workflow artifact.

## Download the APK

1. Open the repository's **Actions** tab.
2. Open the latest **Build ResuMate APK** run.
3. Wait until the build job is green.
4. Scroll to **Artifacts**.
5. Download **resumate-debug-apk**.
6. Unzip it and install `app-debug.apk` on an Android phone.

## Local/Codespace build

```bash
npm ci
npx cap sync android
cd android
./gradlew assembleDebug --no-daemon
```

APK output:

```text
android/app/build/outputs/apk/debug/app-debug.apk
```

## Updating the app

Replace only the canonical file:

```text
www/index.html
```

Then commit/push to `main`. GitHub Actions will automatically build a fresh APK from that version.

## Release build

The debug APK is intended for testing/personal installation. A Play Store release should use a properly configured signing keystore and Android App Bundle/release signing process; never commit the keystore or signing credentials to this repository.

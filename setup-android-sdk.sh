#!/usr/bin/env bash
# Installs a minimal Android SDK (cmdline-tools + platform 34 + build-tools)
# into the Codespace so `./gradlew assembleDebug` works straight from the
# integrated terminal. Runs once automatically when the Codespace is created.
set -e

export ANDROID_HOME="$HOME/android-sdk"
mkdir -p "$ANDROID_HOME/cmdline-tools"
cd "$ANDROID_HOME/cmdline-tools"

if [ ! -d "latest" ]; then
  echo "Downloading Android command-line tools..."
  curl -fsSL -o cmdline-tools.zip \
    "https://dl.google.com/android/repository/commandlinetools-linux-15859902_latest.zip"
  unzip -q cmdline-tools.zip
  mv cmdline-tools latest
  rm cmdline-tools.zip
fi

export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"

echo "Accepting SDK licenses and installing platform 34 + build-tools..."
yes | sdkmanager --licenses > /dev/null
sdkmanager --install "platform-tools" "platforms;android-34" "build-tools;34.0.0" > /dev/null

# Persist environment for every future terminal in this Codespace
{
  echo "export ANDROID_HOME=\"$ANDROID_HOME\""
  echo "export ANDROID_SDK_ROOT=\"$ANDROID_HOME\""
  echo "export PATH=\"\$ANDROID_HOME/cmdline-tools/latest/bin:\$ANDROID_HOME/platform-tools:\$PATH\""
} >> ~/.bashrc

echo "sdk.dir=$ANDROID_HOME" > "$(dirname "$0")/../android/local.properties"

echo "Installing npm dependencies..."
cd "$(dirname "$0")/.."
npm install

echo ""
echo "Android SDK ready. Open a NEW terminal (or run 'source ~/.bashrc'),"
echo "then run:  cd android && ./gradlew assembleDebug"

#!/usr/bin/env bash
# Re-applies the release signing config to the generated Android project.
#
# `expo prebuild` regenerates android/ from scratch and deletes anything added
# to it by hand, so the keystore lives in signing/ (untracked) and this script
# wires it back in. Run it after every prebuild, before ./gradlew assembleRelease.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROPS="$ROOT/signing/keystore.properties"
GRADLE_APP="$ROOT/android/app/build.gradle"
GRADLE_PROPS="$ROOT/android/gradle.properties"

if [ ! -f "$PROPS" ]; then
  echo "No $PROPS. Create a keystore first:" >&2
  echo "  keytool -genkeypair -v -storetype PKCS12 \\" >&2
  echo "    -keystore signing/tur-release.keystore -alias tur-watering \\" >&2
  echo "    -keyalg RSA -keysize 2048 -validity 10000" >&2
  exit 1
fi

if [ ! -f "$GRADLE_APP" ]; then
  echo "No android/ project. Run: npx expo prebuild --platform android" >&2
  exit 1
fi

# shellcheck disable=SC1090
source "$PROPS"

python3 - "$GRADLE_APP" "$GRADLE_PROPS" "$storeFile" "$keyAlias" "$storePassword" "$keyPassword" <<'PY'
import pathlib, sys

app_gradle, gradle_props, store_file, key_alias, store_pw, key_pw = sys.argv[1:7]

p = pathlib.Path(app_gradle)
s = p.read_text()
if 'signingConfigs.release' not in s:
    s = s.replace("""            keyAlias 'androiddebugkey'
            keyPassword 'android'
        }
    }""", """            keyAlias 'androiddebugkey'
            keyPassword 'android'
        }
        release {
            storeFile file(TUR_RELEASE_STORE_FILE)
            storePassword TUR_RELEASE_STORE_PASSWORD
            keyAlias TUR_RELEASE_KEY_ALIAS
            keyPassword TUR_RELEASE_KEY_PASSWORD
        }
    }""")
    s = s.replace("""            // Caution! In production, you need to generate your own keystore file.
            // see https://reactnative.dev/docs/signed-apk-android.
            signingConfig signingConfigs.debug""",
                  """            signingConfig signingConfigs.release""")
    p.write_text(s)
    print('signing config added to app/build.gradle')
else:
    print('signing config already present')

p = pathlib.Path(gradle_props)
s = p.read_text()
# Emulator-only architectures roughly double the build with no use on a phone.
s = s.replace('reactNativeArchitectures=armeabi-v7a,arm64-v8a,x86,x86_64',
              'reactNativeArchitectures=armeabi-v7a,arm64-v8a')
if 'TUR_RELEASE_STORE_FILE' not in s:
    s += (f"\nTUR_RELEASE_STORE_FILE={store_file}\n"
          f"TUR_RELEASE_KEY_ALIAS={key_alias}\n"
          f"TUR_RELEASE_STORE_PASSWORD={store_pw}\n"
          f"TUR_RELEASE_KEY_PASSWORD={key_pw}\n")
p.write_text(s)
print('gradle.properties updated')
PY

if [ -n "${ANDROID_HOME:-}" ]; then
  echo "sdk.dir=$ANDROID_HOME" > "$ROOT/android/local.properties"
  echo "local.properties points at $ANDROID_HOME"
fi

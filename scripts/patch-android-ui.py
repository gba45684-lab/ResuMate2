#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANDROID = ROOT / 'android'
main_files = list((ANDROID / 'app' / 'src' / 'main' / 'java').rglob('MainActivity.java'))
if not main_files:
    raise SystemExit('MainActivity.java not found')

main = main_files[0]
text = main.read_text(encoding='utf-8')

# Keep the native Android status-bar region visible and black so it joins
# the app's black top pad. The WebView must start below the status bar.
imports = 'import android.os.Bundle;\n'
needed = (
    'import android.view.View;\n'
    'import android.view.Window;\n'
    'import android.view.WindowInsets;\n'
    'import android.view.WindowInsetsController;\n'
)
if 'import android.view.Window;' not in text:
    text = text.replace(imports, imports + needed, 1)

marker = '        ResuMateNativeBridge.install(this);'
if marker in text:
    text = text.replace(
        marker,
        marker + '\n        configureTopStatusBar();',
        1,
    )

# Remove the old fullscreen/hide-status-bar implementation if present.
start = text.find('    private void hideSystemStatusBar() {')
if start >= 0:
    end = text.find('\n    }', start)
    if end >= 0:
        end += len('\n    }')
        text = text[:start] + text[end:]

if 'private void configureTopStatusBar()' not in text:
    insert = '''
    private void configureTopStatusBar() {
        Window window = getWindow();
        window.setStatusBarColor(android.graphics.Color.BLACK);

        if (android.os.Build.VERSION.SDK_INT >= 23) {
            int flags = window.getDecorView().getSystemUiVisibility();
            flags &= ~View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR;
            flags &= ~View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN;
            flags |= View.SYSTEM_UI_FLAG_LAYOUT_STABLE;
            window.getDecorView().setSystemUiVisibility(flags);
        }

        if (android.os.Build.VERSION.SDK_INT >= 29) {
            window.setNavigationBarColor(android.graphics.Color.BLACK);
        }

        if (android.os.Build.VERSION.SDK_INT >= 30) {
            WindowInsetsController controller = window.getInsetsController();
            if (controller != null) {
                controller.show(WindowInsets.Type.statusBars());
                controller.setSystemBarsAppearance(
                    0,
                    WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS
                );
            }
        }
    }
'''
    pos = text.rfind('}')
    text = text[:pos] + insert + text[pos:]

main.write_text(text, encoding='utf-8')
print('Patched Android top area: black status bar visible, WebView below it, no fullscreen overlap')

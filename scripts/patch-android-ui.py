#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANDROID = ROOT / 'android'
main_files = list((ANDROID / 'app' / 'src' / 'main' / 'java').rglob('MainActivity.java'))
if not main_files:
    raise SystemExit('MainActivity.java not found')
main = main_files[0]
text = main.read_text(encoding='utf-8')

# Keep the native Android status-bar region visible and black so it physically
# joins the app's black top pad. Do not draw the WebView underneath the status
# bar: the Home UI must begin below the black region and its separator line.
imports = 'import android.os.Bundle;\n'
needed = (
    'import android.view.View;\n'
    'import android.view.Window;\n'
    'import android.view.WindowInsets;\n'
    'import android.view.WindowInsetsController;\n'
')
if 'import android.view.Window;' not in text:
    text = text.replace(imports, imports + needed, 1)

marker = '        ResuMateNativeBridge.install(this);'
method = '''        ResuMateNativeBridge.install(this);\n        configureTopStatusBar();'''
text = text.replace(marker, method, 1)

# Replace any previous hideSystemStatusBar implementation from older builds.
start = text.find('    private void hideSystemStatusBar() {')
if start >= 0:
    end = text.find('\n    }', start)
    if end >= 0:
        end += len('\n    }')
        text = text[:start] + text[end:]

if 'private void configureTopStatusBar()' not in text:
    insert = '''\n    private void configureTopStatusBar() {\n        Window window = getWindow();\n        // The real Android status-bar area is part of the black top strip.\n        window.setStatusBarColor(android.graphics.Color.BLACK);\n        if (android.os.Build.VERSION.SDK_INT >= 23) {\n            int flags = window.getDecorView().getSystemUiVisibility();\n            flags &= ~View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR;\n            flags &= ~View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN;\n            flags |= View.SYSTEM_UI_FLAG_LAYOUT_STABLE;\n            window.getDecorView().setSystemUiVisibility(flags);\n        }\n        if (android.os.Build.VERSION.SDK_INT >= 29) {\n            window.setNavigationBarColor(android.graphics.Color.BLACK);\n        }\n        if (android.os.Build.VERSION.SDK_INT >= 30) {\n            WindowInsetsController controller = window.getInsetsController();\n            if (controller != null) {\n                controller.show(WindowInsets.Type.statusBars());\n                controller.setSystemBarsAppearance(0, WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS);\n            }\n        }\n    }\n'''
    pos = text.rfind('}')
    text = text[:pos] + insert + text[pos:]

main.write_text(text, encoding='utf-8')
print('Patched Android top area: black status bar visible, WebView below it, no fullscreen overlap')

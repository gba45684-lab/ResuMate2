#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANDROID = ROOT / 'android'
main_files = list((ANDROID / 'app' / 'src' / 'main' / 'java').rglob('MainActivity.java'))
if not main_files:
    raise SystemExit('MainActivity.java not found')
main = main_files[0]
text = main.read_text(encoding='utf-8')

if 'WindowInsetsController' not in text:
    text = text.replace('import android.os.Bundle;\n', 'import android.os.Bundle;\nimport android.view.View;\nimport android.view.WindowInsets;\nimport android.view.WindowInsetsController;\n', 1)

marker = '        ResuMateNativeBridge.install(this);'
method = '''        ResuMateNativeBridge.install(this);
        hideSystemStatusBar();'''
text = text.replace(marker, method, 1)

if 'private void hideSystemStatusBar()' not in text:
    insert = '''
    private void hideSystemStatusBar() {
        if (android.os.Build.VERSION.SDK_INT >= 30) {
            getWindow().setStatusBarColor(android.graphics.Color.TRANSPARENT);
            WindowInsetsController controller = getWindow().getInsetsController();
            if (controller != null) controller.hide(WindowInsets.Type.statusBars());
        } else {
            getWindow().setFlags(android.view.WindowManager.LayoutParams.FLAG_FULLSCREEN,
                    android.view.WindowManager.LayoutParams.FLAG_FULLSCREEN);
            getWindow().getDecorView().setSystemUiVisibility(
                    View.SYSTEM_UI_FLAG_FULLSCREEN | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN |
                    View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
        }
    }
'''
    pos = text.rfind('}')
    text = text[:pos] + insert + text[pos:]

main.write_text(text, encoding='utf-8')
print('Patched Android system status bar: time/signal/battery bar hidden')

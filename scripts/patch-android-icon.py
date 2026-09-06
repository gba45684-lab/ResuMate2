#!/usr/bin/env python3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
ANDROID = ROOT / 'android'
RES = ANDROID / 'app' / 'src' / 'main' / 'res'
if not RES.exists(): raise SystemExit('Android resources not found')
(RES / 'drawable').mkdir(parents=True, exist_ok=True)
(RES / 'mipmap-anydpi-v26').mkdir(parents=True, exist_ok=True)
vector = '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="108dp" android:height="108dp" android:viewportWidth="108" android:viewportHeight="108">
<path android:fillColor="#F7F4EC" android:pathData="M0,0h108v108h-108z"/>
<path android:fillColor="#1D3450" android:pathData="M27,20h30c14.4,0 24,8.2 24,20.5 0,8.4 -5.1,14.7 -13.6,18l15.5,28.5h-15.8l-13.7,-25.6h-12.4v25.6h-14zM41,31.5v18.4h14.5c6.8,0 11.3,-3.3 11.3,-9.2 0,-5.9 -4.5,-9.2 -11.3,-9.2z"/>
<path android:fillColor="#1D3450" android:pathData="M28,91h52v5h-52z"/>
</vector>
'''
(RES / 'drawable' / 'resumate_launcher.xml').write_text(vector, encoding='utf-8')
adaptive = '''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
<background android:drawable="@drawable/resumate_launcher"/>
<foreground android:drawable="@drawable/resumate_launcher"/>
</adaptive-icon>
'''
(RES / 'mipmap-anydpi-v26' / 'ic_launcher_resumate.xml').write_text(adaptive, encoding='utf-8')
manifest = ANDROID / 'app' / 'src' / 'main' / 'AndroidManifest.xml'
text = manifest.read_text(encoding='utf-8')
text = text.replace('android:icon="@mipmap/ic_launcher"', 'android:icon="@mipmap/ic_launcher_resumate"')
text = text.replace('android:roundIcon="@mipmap/ic_launcher_round"', 'android:roundIcon="@mipmap/ic_launcher_resumate"')
manifest.write_text(text, encoding='utf-8')
print('Applied ResuMate navy/cream launcher icon')

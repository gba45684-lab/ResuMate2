from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'www' / 'index.html'
VENDOR = ROOT / 'www' / 'vendor'
VENDOR.mkdir(parents=True, exist_ok=True)

# docx is installed from package.json during the APK build. Copy the browser bundle into
# www so the APK does not depend on the public CDN at runtime.
src = ROOT / 'node_modules' / 'docx' / 'build' / 'index.js'
dst = VENDOR / 'docx.js'
if not src.exists():
    raise SystemExit(f'DOCX browser bundle missing: {src}')
dst.write_bytes(src.read_bytes())

text = INDEX.read_text(encoding='utf-8')
text = text.replace(
    '<script src="https://cdn.jsdelivr.net/npm/docx@8.5.0/build/index.min.js" onerror="window.__docxLoadFailed=true"></script>',
    '<script src="vendor/docx.js" onerror="window.__docxLoadFailed=true"></script>',
    1,
)
INDEX.write_text(text, encoding='utf-8')
print('Bundled DOCX runtime locally into www/vendor/docx.js')

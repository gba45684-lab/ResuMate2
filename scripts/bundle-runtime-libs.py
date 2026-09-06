from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'www' / 'index.html'
VENDOR = ROOT / 'www' / 'vendor'
VENDOR.mkdir(parents=True, exist_ok=True)

text = INDEX.read_text(encoding='utf-8')

# Some approved ResuMate builds already contain the complete docx.js UMD
# runtime inline in index.html. In that case there is no external DOCX
# <script src=...> tag to replace, so the old exact-string check incorrectly
# failed the Android build. Treat an embedded runtime as already bundled.
embedded_markers = (
    'DOCX runtime (docx.js, embedded inline)',
    'factory(global2.docx = {})',
)
if any(marker in text for marker in embedded_markers):
    print('DOCX runtime already embedded in www/index.html; no external bundle needed')
    raise SystemExit(0)

# docx 8.x publishes multiple builds. The plain index.js is an ES module and
# cannot be loaded by a normal <script> tag, so prefer the UMD browser bundle.
docx_build = ROOT / 'node_modules' / 'docx' / 'build'
candidates = [
    docx_build / 'index.umd.js',
    docx_build / 'index.umd.cjs',
]
src = next((p for p in candidates if p.exists()), None)
if src is None:
    available = ', '.join(p.name for p in sorted(docx_build.glob('index*'))) if docx_build.exists() else 'build directory missing'
    raise SystemExit(f'DOCX browser UMD bundle missing in {docx_build}. Available: {available}')

dst = VENDOR / 'docx.js'
dst.write_bytes(src.read_bytes())

old_urls = [
    '<script src="https://cdn.jsdelivr.net/npm/docx@8.5.0/build/index.min.js" onerror="window.__docxLoadFailed=true"></script>',
    '<script src="vendor/docx.js" onerror="window.__docxLoadFailed=true"></script>',
]
for old in old_urls:
    if old in text:
        text = text.replace(old, '<script src="vendor/docx.js" onerror="window.__docxLoadFailed=true"></script>', 1)
        break
else:
    raise SystemExit('DOCX script tag not found in www/index.html')

INDEX.write_text(text, encoding='utf-8')
print(f'Bundled DOCX browser UMD runtime locally from {src.name} into www/vendor/docx.js')

#!/usr/bin/env python3
"""Fast regression gate for source/build safety; never mutates the app."""
from pathlib import Path
import py_compile
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SOURCE = ROOT / "www" / "app-source.html"

REQUIRED = [
    "build-web.py", "patch-web.py", "patch-ota-whats-new.py",
    "patch-error-engine.py", "patch-data-protection.py",
    "finalize-export-ui.py", "bundle-runtime-libs.py", "patch-theme-preview.py",
    "health-check.py",
]
FORBIDDEN = (
    r"MutationObserver\([^\n]*\)\.observe\([^\n]*style",
    r"MutationObserver\([^\n]*\)\.observe\([^\n]*class",
    r"\.view\.active[^\n]*pointer-events\s*:\s*none",
    r"\.view:not\([^\n]*pointer-events\s*:\s*none",
)

def fail(msg):
    print(f"REGRESSION CHECK FAILED: {msg}", file=sys.stderr)
    raise SystemExit(1)


def main():
    if not SOURCE.is_file(): fail("canonical app source is missing")
    for name in REQUIRED:
        p=SCRIPTS/name
        if not p.is_file(): fail(f"required script missing: {name}")
        try: py_compile.compile(str(p), doraise=True)
        except py_compile.PyCompileError as e: fail(f"Python syntax error in {name}: {e}")

    text=SOURCE.read_text(encoding="utf-8")
    if len(text) < 10000: fail("canonical app source unexpectedly small")
    for pattern in FORBIDDEN:
        if re.search(pattern, text, re.I): fail(f"unsafe touch interception in source: {pattern}")

    print("REGRESSION CHECK PASSED: build scripts compile and locked-source touch safety is intact")

if __name__ == "__main__":
    main()

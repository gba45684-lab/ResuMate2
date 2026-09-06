#!/usr/bin/env python3
"""Static health gate for the generated ResuMate web bundle.

This intentionally checks only safe, deterministic invariants. It never edits
application source or generated HTML, so a failed check cannot introduce a new
runtime regression. CI runs it after the single build pipeline.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "www" / "index.html"
SOURCE = ROOT / "www" / "app-source.html"

REQUIRED_MARKERS = (
    "<!DOCTYPE html>",
    "<html",
    "</html>",
    "resumate-ota-status",
    "VERSION_URL",
    "ResuMateNativeBridge",
)
FORBIDDEN_PATTERNS = (
    r"MutationObserver\([^\n]*\)\.observe\([^\n]*style",
    r"\.view\.active[^\n]*pointer-events\s*:\s*none",
    r"\.view:not\([^\n]*pointer-events\s*:\s*none",
)


def fail(message: str) -> None:
    print(f"HEALTH CHECK FAILED: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if not SOURCE.is_file():
        fail("canonical source www/app-source.html is missing")
    if not INDEX.is_file():
        fail("generated bundle www/index.html is missing")

    text = INDEX.read_text(encoding="utf-8")
    if not text.strip():
        fail("generated bundle is empty")

    for marker in REQUIRED_MARKERS:
        if marker not in text:
            fail(f"required marker missing: {marker}")

    if text.count("id=\"resumate-ota-status\"") > 1:
        fail("duplicate OTA status control detected")

    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text, re.I):
            fail(f"unsafe touch-interception pattern detected: {pattern}")

    # Basic HTML structure sanity. This is deliberately lightweight because
    # the app contains large embedded third-party JavaScript runtimes.
    if text.count("<html") != 1 or text.count("</html>") != 1:
        fail("invalid top-level HTML document structure")
    if text.count("<body") != 1 or text.count("</body>") != 1:
        fail("invalid body structure")

    # Ensure the source itself has not accidentally acquired generated output.
    source = SOURCE.read_text(encoding="utf-8")
    if "Built www/index.html from www/app-source.html" in source:
        fail("generated build output leaked into canonical source")

    print("HEALTH CHECK PASSED: structure, OTA controls, touch safety and build invariants are valid")


if __name__ == "__main__":
    main()

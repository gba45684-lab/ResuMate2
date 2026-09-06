#!/usr/bin/env python3
"""Static smoke gate for the generated ResuMate web bundle.

This intentionally avoids a browser dependency in CI. It verifies that the
published bundle contains the critical runtime surfaces and that known unsafe
patterns have not returned. Native OTA rollback is validated by the native
loader/workflow and manifest, not by this generated web bundle check.
"""
from pathlib import Path
from html.parser import HTMLParser
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "www" / "index.html"


def fail(message: str) -> None:
    print(f"POST-BUILD SMOKE FAILED: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        fail(f"missing {label}: {needle}")


class ScriptTagParser(HTMLParser):
    """Count actual HTML script elements, ignoring strings inside JavaScript."""
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.open_count = 0
        self.close_count = 0

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "script":
            self.open_count += 1

    def handle_startendtag(self, tag, attrs):
        if tag.lower() == "script":
            self.open_count += 1
            self.close_count += 1

    def handle_endtag(self, tag):
        if tag.lower() == "script":
            self.close_count += 1


def main() -> None:
    if not BUNDLE.is_file() or BUNDLE.stat().st_size < 10000:
        fail("generated www/index.html is missing or unexpectedly small")

    text = BUNDLE.read_text(encoding="utf-8", errors="strict")

    for needle, label in [
        ("resumate-ota-status", "OTA status control"),
        ("VERSION_URL", "OTA manifest URL"),
        ("ResuMateErrorEngine", "runtime error engine"),
        ("ResuMateDataProtection", "resume data protection"),
        ("html2pdf", "PDF export runtime"),
        ("docx", "DOCX runtime"),
        ("localStorage", "local persistence"),
        ("whatsNew", "OTA What’s New data"),
    ]:
        require(text, needle, label)

    if not re.search(r"<!DOCTYPE html>", text, re.I):
        fail("generated bundle has no HTML doctype")

    # Raw text.count() is unsafe because JavaScript/templates may contain
    # literal <script or </script> strings. Parse the HTML structure instead.
    parser = ScriptTagParser()
    try:
        parser.feed(text)
        parser.close()
    except Exception as exc:
        fail(f"HTML parser rejected generated bundle: {exc}")
    if parser.open_count != parser.close_count:
        fail(f"script elements are unbalanced ({parser.open_count} open, {parser.close_count} close)")

    forbidden = [
        r"MutationObserver\([^\n]*\)\.observe\([^\n]*style",
        r"MutationObserver\([^\n]*\)\.observe\([^\n]*class",
        r"\.view\.active[^\n]*pointer-events\s*:\s*none",
        r"\.view:not\([^\n]*pointer-events\s*:\s*none",
    ]
    for pattern in forbidden:
        if re.search(pattern, text, re.I):
            fail(f"unsafe touch interception detected: {pattern}")

    print("POST-BUILD SMOKE PASSED: core export, persistence, OTA, error/recovery and touch-safety surfaces present")


if __name__ == "__main__":
    main()

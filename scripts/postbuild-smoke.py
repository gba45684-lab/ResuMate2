#!/usr/bin/env python3
"""Static smoke gate for the generated ResuMate web bundle.

This intentionally avoids a browser dependency in CI. It verifies that the
published bundle contains the critical runtime surfaces and that known unsafe
patterns have not returned. Native OTA rollback is validated by the native
loader/workflow and manifest, not by this generated web bundle check.
"""
from pathlib import Path
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


def main() -> None:
    if not BUNDLE.is_file() or BUNDLE.stat().st_size < 10000:
        fail("generated www/index.html is missing or unexpectedly small")

    text = BUNDLE.read_text(encoding="utf-8", errors="strict")

    # Runtime surfaces that must be present in the generated app bundle.
    # ResuMateHealth is intentionally NOT checked here: health-check.py is a
    # build-time validation gate and reports success during build; it is not a
    # browser runtime object embedded in the published bundle.
    # Native OTA rollback is also intentionally NOT checked here because its
    # recovery logic lives in the native OTA loader/workflow, not the web bundle.
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

    # Basic document/script integrity.
    if not re.search(r"<!DOCTYPE html>", text, re.I):
        fail("generated bundle has no HTML doctype")
    if text.count("<script") != text.count("</script>"):
        fail("script tag count is unbalanced")

    # Never allow the historical global touch-blocking patterns back in.
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

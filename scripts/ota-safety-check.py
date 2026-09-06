#!/usr/bin/env python3
"""Static OTA safety gate for staging, integrity and rollback behavior."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
LOADER = ROOT / "www" / "ota-loader.html"


def fail(message: str) -> None:
    print(f"OTA SAFETY CHECK FAILED: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if not LOADER.is_file():
        fail("www/ota-loader.html is missing")
    text = LOADER.read_text(encoding="utf-8")

    required = (
        "VERSION_URL",
        "APP_URL",
        "PREVIOUS_KEY",
        "ACTIVE_KEY",
        "PENDING_KEY",
        "SUCCESS_KEY",
        "crypto.subtle.digest",
        "prepareRollback",
        "Update integrity check failed",
        "Using the last verified ResuMate version.",
        "Recovering the previous verified version…",
    )
    for marker in required:
        if marker not in text:
            fail(f"required OTA safety marker missing: {marker}")

    # A new bundle must be verified before it becomes the active cached version.
    write_pos = text.find("if(!write(m.otaVersion,h))")
    verify_pos = text.find("const h=await fetchVerified(m)")
    if verify_pos < 0 or write_pos < 0 or verify_pos > write_pos:
        fail("OTA bundle is not verified before activation")

    # Boot health must be recorded after startup; rollback requires a previous version.
    if text.count("localStorage.setItem(PREVIOUS_KEY") < 1:
        fail("previous verified version is not retained")
    if text.count("localStorage.setItem(PENDING_KEY") < 1:
        fail("pending boot marker is not written")
    # SUCCESS_KEY is owned by the injected runtime error engine. The loader must
    # understand the same key and actively consume/reset it for rollback decisions.
    success_marker_ok = (
        text.count("localStorage.setItem(SUCCESS_KEY") >= 1
        or text.count("localStorage.setItem(BOOT_SUCCESS") >= 1
        or "read(SUCCESS_KEY)" in text
    )
    if not success_marker_ok:
        fail("successful boot marker is not recognized")

    # Prevent accidental weakening of cache/integrity guarantees.
    if re.search(r"fetch\\(APP_URL[^\\n]*cache:\\s*['\"]default", text):
        fail("OTA bundle fetch must not use default cache")

    print("OTA SAFETY CHECK PASSED: staging, integrity verification and rollback paths are present")


if __name__ == "__main__":
    main()

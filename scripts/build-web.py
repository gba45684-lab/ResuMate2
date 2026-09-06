#!/usr/bin/env python3
"""Build the ResuMate web bundle from the single canonical app source.

Design rule: app-source.html is the only file edited for normal UI/features.
All generated/compatibility patches are applied here in one deterministic order.
"""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
WWW = ROOT / "www"
SOURCE = WWW / "app-source.html"
OUTPUT = WWW / "index.html"
REQUIRED = [
    SOURCE,
    WWW / "ota-loader.html",
    WWW / "fallback.html",
    ROOT / "scripts" / "patch-web.py",
    ROOT / "scripts" / "patch-ota-whats-new.py",
    ROOT / "scripts" / "patch-error-engine.py",
    ROOT / "scripts" / "patch-data-protection.py",
    ROOT / "scripts" / "patch-diagnostics.py",
    ROOT / "scripts" / "patch-interaction-recovery.py",
    ROOT / "scripts" / "finalize-export-ui.py",
    ROOT / "scripts" / "bundle-runtime-libs.py",
    ROOT / "scripts" / "patch-theme-preview.py",
    ROOT / "scripts" / "health-check.py",
]


def run(script: str) -> None:
    print(f"==> {script}")
    subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT, check=True)


def main() -> None:
    missing = [str(p.relative_to(ROOT)) for p in REQUIRED if not p.is_file()]
    if missing:
        raise SystemExit("Missing build inputs:\n" + "\n".join(missing))

    OUTPUT.write_text(SOURCE.read_text(encoding="utf-8"), encoding="utf-8")

    for script in (
        "patch-web.py",
        "patch-ota-whats-new.py",
        "patch-error-engine.py",
        "patch-data-protection.py",
        "patch-diagnostics.py",
        "patch-interaction-recovery.py",
        "finalize-export-ui.py",
        "bundle-runtime-libs.py",
        "patch-theme-preview.py",
    ):
        run(script)

    text = OUTPUT.read_text(encoding="utf-8")
    if not text.strip():
        raise SystemExit("Generated www/index.html is empty")
    if "resumate-ota-status" not in text:
        raise SystemExit("Generated bundle is missing the OTA status control")
    if "ResuMateDiagnostics" not in text:
        raise SystemExit("Generated bundle is missing diagnostics")
    if "ResuMate interaction recovery" not in text:
        raise SystemExit("Generated bundle is missing interaction recovery")
    run("health-check.py")

    print(f"Built {OUTPUT.relative_to(ROOT)} from {SOURCE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

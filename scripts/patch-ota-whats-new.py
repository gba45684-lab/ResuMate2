#!/usr/bin/env python3
"""Patch the OTA update toggle and What's New modal into the generated bundle."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "www" / "index.html"

text = OUT.read_text(encoding="utf-8")

# Keep the OTA control visible, compact, and directly beside the ResuMate branding.
patch = r'''
<style id="resumate-ota-position-fix">
#resumate-ota-status {
  position: fixed !important;
  top: 8px !important;
  right: auto !important;
  left: 50% !important;
  transform: translateX(72px) !important;
  z-index: 2147483647 !important;
  pointer-events: auto !important;
  touch-action: manipulation !important;
}
</style>
'''
if "resumate-ota-position-fix" not in text:
    text = text.replace("</head>", patch + "</head>", 1)

OUT.write_text(text, encoding="utf-8")
print("OTA update toggle positioned beside ResuMate branding")

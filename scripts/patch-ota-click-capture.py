#!/usr/bin/env python3
"""Install a capture-phase OTA update button handler.

The OTA dialog is deliberately outside the app's normal event flow. Capture the
button click before any document-level app handler can cancel or swallow it.
No global pointer-events override is used.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "www" / "index.html"
text = INDEX.read_text(encoding="utf-8")

MARKER = "ResuMate OTA capture handler v2"
SCRIPT = r'''
<script>
(function(){
  'use strict';
  if(window.__resumateOtaCaptureV2) return;
  window.__resumateOtaCaptureV2=true;
  let busy=false;
  async function run(e){
    const b=e.target && e.target.closest ? e.target.closest('#resumate-ota-apply') : null;
    if(!b || busy) return;
    e.preventDefault();
    e.stopPropagation();
    if(e.stopImmediatePropagation) e.stopImmediatePropagation();
    busy=true;
    b.disabled=true;
    b.textContent='Downloading…';
    b.style.opacity='0.75';
    try{
      let ok=false;
      if(typeof window.ResuMateOTAUpdateCheck==='function') ok=await window.ResuMateOTAUpdateCheck();
      else if(window.ResuMateOTA && typeof window.ResuMateOTA.check==='function') ok=await window.ResuMateOTA.check();
      if(!ok) throw new Error('OTA updater could not start');
    }catch(err){
      busy=false;
      b.disabled=false;
      b.textContent='Download and install now';
      b.style.opacity='1';
      if(typeof window.toast==='function') window.toast('Update failed: '+String(err && err.message || err));
      else console.error('ResuMate OTA update failed:',err);
    }
  }
  document.addEventListener('click',run,true);
  document.addEventListener('keydown',function(e){
    if((e.key==='Enter'||e.key===' ') && e.target && e.target.closest && e.target.closest('#resumate-ota-apply')) run(e);
  },true);
})();
</script>
'''.replace("'use strict';", "'use strict'; /* " + MARKER + " */", 1)

if MARKER not in text:
    text = text.replace('</body>', SCRIPT + '\n</body>', 1)
    INDEX.write_text(text, encoding='utf-8')
    print('Applied capture-phase OTA Download and install handler')
else:
    print('OTA capture handler already present')

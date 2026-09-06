#!/usr/bin/env python3
"""Install robust capture-phase OTA update button handling."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "www" / "index.html"
text = INDEX.read_text(encoding="utf-8")

MARKER = "ResuMate OTA capture handler v3"
SCRIPT = r'''
<script>
(function(){
  'use strict';
  if(window.__resumateOtaCaptureV3) return;
  window.__resumateOtaCaptureV3=true;
  let busy=false;
  let lastRun=0;
  async function run(e){
    const b=e.target && e.target.closest ? e.target.closest('#resumate-ota-apply') : null;
    if(!b || busy) return;
    const now=Date.now();
    if(now-lastRun<500) return;
    lastRun=now;
    if(e.cancelable) e.preventDefault();
    e.stopPropagation();
    if(e.stopImmediatePropagation) e.stopImmediatePropagation();
    busy=true;
    b.disabled=true;
    b.setAttribute('aria-busy','true');
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
      b.removeAttribute('aria-busy');
      b.textContent='Download and install now';
      b.style.opacity='1';
      if(typeof window.toast==='function') window.toast('Update failed: '+String(err && err.message || err));
      else console.error('ResuMate OTA update failed:',err);
    }
  }
  document.addEventListener('pointerup',run,true);
  document.addEventListener('click',run,true);
  document.addEventListener('touchend',run,true);
  document.addEventListener('keydown',function(e){
    if((e.key==='Enter'||e.key===' ') && e.target && e.target.closest && e.target.closest('#resumate-ota-apply')) run(e);
  },true);
})();
</script>
'''.replace("'use strict';", "'use strict'; /* " + MARKER + " */", 1)

if "ResuMate OTA capture handler v3" not in text:
    text = text.replace('</body>', SCRIPT + '\n</body>', 1)
    INDEX.write_text(text, encoding='utf-8')
    print('Applied robust capture-phase OTA install handler')
else:
    print('OTA capture handler v3 already present')

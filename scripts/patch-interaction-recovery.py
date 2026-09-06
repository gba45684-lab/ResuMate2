#!/usr/bin/env python3
"""Repair stale UI layers that can intercept all component taps.

This is intentionally component-state based: hidden overlays are made non-rendering
and the active view remains interactive. No global pointer-events override is used.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "www" / "index.html"
text = INDEX.read_text(encoding="utf-8")

STYLE = r'''
/* ResuMate interaction recovery: prevent stale hidden modal layers from covering UI. */
.overlay:not(.show),
.modal:not(.show),
.dialog:not(.show),
.drawer:not(.show),
.sheet:not(.show) {
  display: none !important;
  visibility: hidden !important;
}
'''

SCRIPT = r'''
<script>
(function(){
  'use strict';
  function hideStaleLayers(root){
    (root || document).querySelectorAll('.overlay,.modal,.dialog,.drawer,.sheet').forEach(function(el){
      if(el.classList.contains('show')) return;
      var s=getComputedStyle(el);
      var r=el.getBoundingClientRect();
      /* Only repair layers that are actually capable of covering the app. */
      if(s.position==='fixed' && r.width >= window.innerWidth*0.85 && r.height >= window.innerHeight*0.85){
        el.style.display='none';
        el.style.visibility='hidden';
      }
    });
  }
  function start(){
    hideStaleLayers(document);
    var observer=new MutationObserver(function(){ hideStaleLayers(document); });
    observer.observe(document.body,{childList:true,subtree:true});
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',start,{once:true});
  else start();
})();
</script>
'''

if '/* ResuMate interaction recovery: prevent stale hidden modal layers from covering UI. */' not in text:
    text = text.replace('</style>', STYLE + '\n</style>', 1)
if 'ResuMate interaction recovery' not in text:
    text = text.replace('</body>', SCRIPT + '\n</body>', 1)

INDEX.write_text(text, encoding='utf-8')
print('Applied stale overlay interaction recovery without global pointer-events hacks')

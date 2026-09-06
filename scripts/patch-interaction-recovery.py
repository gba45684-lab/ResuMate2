#!/usr/bin/env python3
"""Repair stale UI layers that can intercept component taps.

This is intentionally component-state based: hidden overlays are made non-rendering
and the active view remains interactive. No global pointer-events override is used.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "www" / "index.html"
text = INDEX.read_text(encoding="utf-8")

STYLE_MARKER = "/* ResuMate interaction recovery: prevent stale hidden modal layers from covering UI. */"
SCRIPT_MARKER = "window.__ResuMateInteractionRecoveryInstalled"

STYLE = r'''
/* ResuMate interaction recovery: prevent stale hidden modal layers from covering UI. */
.overlay:not(.show),
.modal:not(.show),
.dialog:not(.show),
.drawer:not(.show),
.sheet:not(.show),
.overlay[aria-hidden="true"],
.modal[aria-hidden="true"],
.dialog[aria-hidden="true"],
.drawer[aria-hidden="true"],
.sheet[aria-hidden="true"] {
  display: none !important;
  visibility: hidden !important;
}
'''

SCRIPT = r'''
<script>
(function(){
  'use strict';
  if(window.__ResuMateInteractionRecoveryInstalled) return;
  window.__ResuMateInteractionRecoveryInstalled=true;

  const selectors='.overlay,.modal,.dialog,.drawer,.sheet';
  function hideStaleLayers(root){
    (root || document).querySelectorAll(selectors).forEach(function(el){
      if(el.classList.contains('show') && el.getAttribute('aria-hidden') !== 'true') return;
      if(el.id === 'welcome' && el.classList.contains('show')) return;
      var s=getComputedStyle(el);
      var r=el.getBoundingClientRect();
      var large=r.width >= window.innerWidth*0.85 && r.height >= window.innerHeight*0.65;
      var overlayLike=s.position==='fixed' || s.position==='absolute' || s.position==='sticky';
      if(overlayLike && large){
        el.style.display='none';
        el.style.visibility='hidden';
      }
    });
  }
  function start(){
    hideStaleLayers(document);
    var observer=new MutationObserver(function(records){
      for(var i=0;i<records.length;i++){
        if(records[i].type==='childList') { hideStaleLayers(document); break; }
      }
    });
    observer.observe(document.body,{childList:true,subtree:true});
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',start,{once:true});
  else start();
})();
</script>
'''

if STYLE_MARKER not in text:
    text = text.replace('</style>', STYLE + '\n</style>', 1)
if SCRIPT_MARKER not in text:
    text = text.replace('</body>', SCRIPT + '\n</body>', 1)

INDEX.write_text(text, encoding='utf-8')
print('Applied stale overlay interaction recovery without global pointer-events hacks')

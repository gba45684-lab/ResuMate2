#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'www' / 'index.html'
text = INDEX.read_text(encoding='utf-8')

STYLE = r'''
/* ResuMate theme/icon + Preview export layering fix */
:root {
  --resumate-brand: #1D3450;
  --resumate-brand-strong: #162A40;
  --resumate-surface: #F7F4EC;
  --resumate-ink: #181A1F;
}
html, body, button, input, textarea, select {
  font-family: Inter, "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
}
.resumate-preview-export-fix,
.resumate-preview-export-fix * {
  box-sizing: border-box;
}
.resumate-preview-menu-fix {
  position: relative !important;
  z-index: 12000 !important;
}
.resumate-preview-export-layer-fix {
  position: relative !important;
  z-index: 11000 !important;
  isolation: isolate;
}
.resumate-preview-export-layer-fix,
.resumate-preview-export-layer-fix * {
  pointer-events: auto;
}
.resumate-preview-overflow-fix,
.resumate-preview-overflow-fix > * {
  overflow: visible !important;
}
'''

SCRIPT = r'''
<script>
(function(){
  'use strict';
  function norm(v){return String(v||'').replace(/\s+/g,' ').trim().toLowerCase();}
  function visible(el){
    if(!el) return false;
    const s=getComputedStyle(el), r=el.getBoundingClientRect();
    return s.display!=='none' && s.visibility!=='hidden' && r.width>0 && r.height>0;
  }
  function mark(){
    const controls=Array.from(document.querySelectorAll('button,[role="button"]'));
    const menu=controls.find(el=>norm(el.textContent)==='menu' || norm(el.getAttribute('aria-label'))==='menu');
    if(menu){
      menu.classList.add('resumate-preview-menu-fix');
      const p=menu.parentElement;
      if(p) p.classList.add('resumate-preview-menu-fix');
    }
    const exportButton=controls.find(el=>norm(el.textContent)==='export' || norm(el.getAttribute('aria-label'))==='export');
    if(!exportButton) return;
    exportButton.classList.add('resumate-preview-export-fix');
    let panel=exportButton.parentElement;
    for(let i=0;i<5 && panel;i++,panel=panel.parentElement){
      const t=norm(panel.textContent);
      if(t.includes('pdf') || t.includes('docx') || t.includes('download')){
        panel.classList.add('resumate-preview-export-layer-fix','resumate-preview-overflow-fix');
        if(panel.parentElement) panel.parentElement.classList.add('resumate-preview-overflow-fix');
        break;
      }
    }
    document.querySelectorAll('[class*="export"],[id*="export"]').forEach(el=>{
      if(visible(el) && (norm(el.textContent).includes('pdf') || norm(el.textContent).includes('docx'))){
        el.classList.add('resumate-preview-export-layer-fix');
        if(el.parentElement) el.parentElement.classList.add('resumate-preview-overflow-fix');
      }
    });
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',mark,{once:true}); else mark();
  new MutationObserver(mark).observe(document.documentElement,{subtree:true,childList:true});
})();
</script>
'''

if '/* ResuMate theme/icon + Preview export layering fix */' not in text:
    text = text.replace('</style>', STYLE + '\n</style>', 1)
if 'ResuMate preview export layering fix' not in text:
    text = text.replace('</body>', SCRIPT + '\n</body>', 1)

INDEX.write_text(text, encoding='utf-8')
print('Applied ResuMate theme typography and Preview Export/menu layering fix')

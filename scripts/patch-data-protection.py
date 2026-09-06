#!/usr/bin/env python3
"""Install a small, non-invasive local data safety layer in the generated app."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "www" / "index.html"

ENGINE = r'''<script>
/* ResuMate Data Protection: versioned local snapshots, no UI changes. */
(function(){
  'use strict';
  const SNAP='resumate.data.snapshot.v1';
  const MAX=3;
  const MAX_BYTES=250000;
  const EXCLUDE=/^(resumate\.ota\.|resumate\.error-engine)/i;
  function collect(){
    const data={};
    try{
      for(let i=0;i<localStorage.length;i++){
        const k=localStorage.key(i);
        if(!k || EXCLUDE.test(k)) continue;
        const v=localStorage.getItem(k);
        if(v!=null) data[k]=v;
      }
    }catch(_){ return null; }
    return data;
  }
  function saveSnapshot(reason){
    const data=collect(); if(!data) return false;
    let payload;
    try{payload=JSON.stringify({schema:1,time:new Date().toISOString(),reason:reason||'periodic',data});}catch(_){return false;}
    if(payload.length>MAX_BYTES) return false;
    try{
      const old=JSON.parse(localStorage.getItem(SNAP)||'[]');
      const list=Array.isArray(old)?old:[];
      list.push(JSON.parse(payload));
      while(list.length>MAX) list.shift();
      localStorage.setItem(SNAP,JSON.stringify(list));
      return true;
    }catch(_){return false;}
  }
  function latest(){
    try{const x=JSON.parse(localStorage.getItem(SNAP)||'[]');return Array.isArray(x)&&x.length?x[x.length-1]:null;}catch(_){return null;}
  }
  function restore(snapshot){
    const s=snapshot||latest(); if(!s||!s.data||typeof s.data!=='object') return false;
    try{Object.keys(s.data).forEach(k=>localStorage.setItem(k,String(s.data[k])));return true;}catch(_){return false;}
  }
  window.ResuMateDataProtection={snapshot:saveSnapshot,latest:latest,restore:restore};
  setTimeout(function(){saveSnapshot('startup');},3000);
  setInterval(function(){saveSnapshot('periodic');},30000);
  window.addEventListener('pagehide',function(){saveSnapshot('pagehide');});
})();
</script>
'''
text=INDEX.read_text(encoding='utf-8')
if 'ResuMateDataProtection' not in text:
    text=text.replace('</body>',ENGINE+'</body>',1)
INDEX.write_text(text,encoding='utf-8')
print('Installed ResuMate local data protection snapshots')

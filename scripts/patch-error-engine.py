#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "www" / "index.html"

ENGINE = r'''<script>
/* ResuMate Error Engine: observe -> classify -> persist -> safely recover. */
(function(){
  'use strict';
  const KEY='resumate.error-engine.v1';
  const MAX=40;
  const recent=[];
  let reloading=false;

  function normalize(value){
    if(value instanceof Error) return {name:value.name||'Error',message:value.message||String(value),stack:value.stack||''};
    if(value && typeof value==='object') return {name:String(value.name||'Error'),message:String(value.message||value.reason||JSON.stringify(value)),stack:String(value.stack||'')};
    return {name:'Error',message:String(value),stack:''};
  }
  function classify(e){
    const s=(e.name+' '+e.message).toLowerCase();
    if(/network|fetch|http|offline|failed to fetch/.test(s)) return 'network';
    if(/quota|storage|localstorage|indexeddb/.test(s)) return 'storage';
    if(/permission|denied|security/.test(s)) return 'permission';
    if(/syntax|unexpected token|parse/.test(s)) return 'syntax';
    if(/typeerror|referenceerror|rangeerror/.test(s)) return 'runtime';
    return 'unknown';
  }
  function persist(entry){
    recent.push(entry); while(recent.length>MAX) recent.shift();
    try{ localStorage.setItem(KEY,JSON.stringify(recent)); }catch(_){ /* storage itself may be broken */ }
  }
  function toast(message){
    try{
      if(typeof window.toast==='function') window.toast(message);
      else if(typeof window.showToast==='function') window.showToast(message);
    }catch(_){ }
  }
  function analyze(error, context){
    const e=normalize(error);
    const entry={time:new Date().toISOString(),type:classify(e),context:context||'runtime',name:e.name,message:e.message,stack:e.stack};
    persist(entry);
    return entry;
  }
  function safeRecover(entry){
    /* Only reversible, low-risk recovery actions are automatic. */
    if(entry.type==='storage'){
      try{
        ['resumate.ota.active.v3','resumate.ota.bundle.v7','resumate.ota.bundle.v3'].forEach(k=>{
          const v=localStorage.getItem(k); if(v) JSON.parse(v);
        });
      }catch(_){ /* do not delete user resume data */ }
    }
    if(entry.type==='network' && !navigator.onLine) toast('ResuMate is offline. Your local work is safe; retry when online.');
    if(entry.type==='runtime' || entry.type==='syntax') toast('ResuMate detected an app error. Please retry the action.');
  }
  window.ResuMateErrorEngine={
    capture:function(error,context){const e=analyze(error,context); safeRecover(e); return e;},
    getRecent:function(){return recent.slice();},
    clear:function(){recent.length=0;try{localStorage.removeItem(KEY);}catch(_){}}
  };
  window.addEventListener('error',function(ev){
    const e=analyze(ev.error||ev.message||'Unknown error','window.error'); safeRecover(e);
  });
  window.addEventListener('unhandledrejection',function(ev){
    const e=analyze(ev.reason||'Unhandled promise rejection','unhandledrejection'); safeRecover(e);
  });
  window.addEventListener('online',function(){
    try{ if(typeof window.ResuMateOTAUpdateCheck==='function') window.ResuMateOTAUpdateCheck(); }catch(_){ }
  });
  window.addEventListener('offline',function(){toast('ResuMate is offline. Local features remain available.');});
  try{
    const old=localStorage.getItem(KEY); if(old){const parsed=JSON.parse(old); if(Array.isArray(parsed)) parsed.slice(-MAX).forEach(x=>recent.push(x));}
  }catch(_){ }
})();
</script>
'''

text=INDEX.read_text(encoding='utf-8')
if 'ResuMateErrorEngine' not in text:
    text=text.replace('</body>',ENGINE+'</body>',1)
INDEX.write_text(text,encoding='utf-8')
print('Installed ResuMate runtime error analysis/recovery engine')

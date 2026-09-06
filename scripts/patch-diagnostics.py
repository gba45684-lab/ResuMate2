#!/usr/bin/env python3
"""Install an opt-in diagnostics dashboard without changing the locked UI."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "www" / "index.html"

DASHBOARD = r'''<script>
/* ResuMate Diagnostics: opt-in developer dashboard; normal UI remains unchanged. */
(function(){
  'use strict';
  const PANEL_ID='resumate-diagnostics-panel';
  const ERROR_KEY='resumate.error-engine.v1';
  const SNAP_KEY='resumate.data.snapshot.v1';
  const ACTIVE_KEY='resumate.ota.active.v3';
  const PENDING_KEY='resumate.ota.boot.pending.v1';
  const SUCCESS_KEY='resumate.ota.boot.success.v1';
  function read(key, fallback){try{const v=localStorage.getItem(key);return v?JSON.parse(v):fallback;}catch(_){return fallback;}}
  function esc(v){return String(v==null?'':v).replace(/[&<>\"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','\\':'&#92;','"':'&quot;'}[c];});}
  function diagnostics(){
    const errors=read(ERROR_KEY,[]);
    const snapshots=read(SNAP_KEY,[]);
    const active=read(ACTIVE_KEY,null);
    const pending=read(PENDING_KEY,null);
    const success=read(SUCCESS_KEY,null);
    const counts={network:0,storage:0,permission:0,syntax:0,runtime:0,unknown:0};
    (Array.isArray(errors)?errors:[]).forEach(e=>{if(counts[e.type]!=null)counts[e.type]++;});
    return {generatedAt:new Date().toISOString(),online:navigator.onLine,errors:Array.isArray(errors)?errors:[],counts,snapshots:Array.isArray(snapshots)?snapshots:[],ota:{active,pending,success}};
  }
  function exportDiagnostics(){
    const payload=JSON.stringify(diagnostics(),null,2);
    const blob=new Blob([payload],{type:'application/json'});
    const url=URL.createObjectURL(blob); const a=document.createElement('a');
    a.href=url; a.download='resumate-diagnostics-'+new Date().toISOString().replace(/[:.]/g,'-')+'.json';
    document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
  }
  function render(){
    let p=document.getElementById(PANEL_ID);
    if(!p){p=document.createElement('section');p.id=PANEL_ID;document.body.appendChild(p);}
    const d=diagnostics(); const last=d.errors.slice(-12).reverse();
    p.innerHTML='<div class="rdiag-head"><div><strong>ResuMate Diagnostics</strong><small>Developer-only local diagnostics</small></div><button id="rdiag-close">Close</button></div>'+
      '<div class="rdiag-grid"><div><b>'+d.errors.length+'</b><span>Errors stored</span></div><div><b>'+d.snapshots.length+'</b><span>Data snapshots</span></div><div><b>'+ (d.online?'ONLINE':'OFFLINE') +'</b><span>Network</span></div><div><b>'+esc(d.ota.active&&d.ota.active.version||'none')+'</b><span>Active OTA</span></div></div>'+
      '<div class="rdiag-actions"><button id="rdiag-export">Export JSON</button><button id="rdiag-snapshot">Create snapshot</button><button id="rdiag-clear">Clear errors</button></div>'+
      '<h4>Error classification</h4><div class="rdiag-types">'+Object.keys(d.counts).map(k=>'<span><b>'+d.counts[k]+'</b> '+k+'</span>').join('')+'</div>'+
      '<h4>Recent errors</h4><div class="rdiag-list">'+(last.length?last.map(e=>'<article><b>'+esc(e.type)+' · '+esc(e.name)+'</b><time>'+esc(e.time)+'</time><p>'+esc(e.message)+'</p><small>'+esc(e.context)+'</small></article>').join(''):'<p>No errors recorded.</p>')+'</div>'+
      '<h4>OTA health</h4><pre>'+esc(JSON.stringify(d.ota,null,2))+'</pre>'+
      '<h4>Recovery</h4><p>Local snapshots: '+d.snapshots.length+'. Safe restore is available through <code>ResuMateDataProtection.restore()</code>; OTA activation remains integrity-verified and rollback-protected.</p>';
    p.querySelector('#rdiag-close').onclick=function(){p.remove();history.replaceState(null,'',location.pathname+location.search);};
    p.querySelector('#rdiag-export').onclick=exportDiagnostics;
    p.querySelector('#rdiag-snapshot').onclick=function(){try{window.ResuMateDataProtection&&window.ResuMateDataProtection.snapshot('diagnostics');}catch(_){}render();};
    p.querySelector('#rdiag-clear').onclick=function(){try{localStorage.removeItem(ERROR_KEY);}catch(_){}render();};
  }
  function injectStyles(){
    if(document.getElementById('resumate-diagnostics-style'))return;
    const s=document.createElement('style');s.id='resumate-diagnostics-style';s.textContent='#'+PANEL_ID+'{position:fixed;inset:0;z-index:2147483646;background:#fff;color:#111;overflow:auto;padding:20px;font:14px/1.45 system-ui,sans-serif}#'+PANEL_ID+' .rdiag-head{display:flex;justify-content:space-between;align-items:center;gap:12px;position:sticky;top:0;background:#fff;padding-bottom:12px;border-bottom:1px solid #ddd}#'+PANEL_ID+' .rdiag-head small{display:block;color:#666}#'+PANEL_ID+' button{border:1px solid #bbb;background:#f6f6f6;border-radius:8px;padding:8px 12px;margin:4px;cursor:pointer}#'+PANEL_ID+' .rdiag-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin:14px 0}#'+PANEL_ID+' .rdiag-grid>div{border:1px solid #ddd;border-radius:10px;padding:12px}#'+PANEL_ID+' .rdiag-grid b{display:block;font-size:18px}#'+PANEL_ID+' .rdiag-grid span{color:#666;font-size:12px}#'+PANEL_ID+' .rdiag-types{display:flex;flex-wrap:wrap;gap:8px}#'+PANEL_ID+' .rdiag-types span{border:1px solid #ddd;border-radius:999px;padding:6px 9px}#'+PANEL_ID+' article{border-bottom:1px solid #eee;padding:8px 0}#'+PANEL_ID+' article time{float:right;color:#777;font-size:11px}#'+PANEL_ID+' article p{margin:3px 0}#'+PANEL_ID+' pre{white-space:pre-wrap;background:#f6f6f6;padding:10px;border-radius:8px;overflow:auto}@media(max-width:600px){#'+PANEL_ID+'{padding:12px}#'+PANEL_ID+' .rdiag-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}';document.head.appendChild(s);
  }
  window.ResuMateDiagnostics={get:diagnostics,open:function(){injectStyles();render();},export:exportDiagnostics};
  function shouldOpen(){return location.hash==='#diagnostics'||/[?&]diagnostics=1(?:&|$)/.test(location.search);}
  if(shouldOpen())setTimeout(function(){window.ResuMateDiagnostics.open();},0);
})();
</script>
'''

text=INDEX.read_text(encoding='utf-8')
if 'window.ResuMateDiagnostics' not in text:
    text=text.replace('</body>',DASHBOARD+'</body>',1)
INDEX.write_text(text,encoding='utf-8')
print('Installed opt-in ResuMate diagnostics dashboard')

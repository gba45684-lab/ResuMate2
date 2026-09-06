#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'www' / 'index.html'
text = INDEX.read_text(encoding='utf-8')

script = r'''
<script>
(function(){
  'use strict';
  const VERSION_URL='https://raw.githubusercontent.com/gba45684-lab/ResuMate2/ota/version.json';
  const id='resumate-ota-status';
  const styleId='resumate-ota-whats-new-style';
  let manifest=null;
  let applying=false;

  function escapeHtml(value){
    return String(value).replace(/[&<>\"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c];});
  }

  function ensureStyle(){
    if(document.getElementById(styleId)) return;
    const s=document.createElement('style');
    s.id=styleId;
    s.textContent='@keyframes resumateOtaBlink{0%,100%{filter:brightness(1);box-shadow:0 2px 10px rgba(0,0,0,.22)}50%{filter:brightness(1.15);box-shadow:0 0 0 4px rgba(34,197,94,.18),0 0 18px rgba(34,197,94,.65)}}'
      +'#resumate-ota-status{display:block!important;position:fixed!important;top:8px!important;right:10px!important;z-index:2147483647!important;pointer-events:auto!important;touch-action:manipulation!important;}'
      +'#resumate-ota-status.resumate-update-ready{background:#22c55e!important;color:#fff!important;border-color:#16a34a!important;animation:resumateOtaBlink 1.1s ease-in-out infinite!important}'
      +'html,body{margin-top:0!important;padding-top:0!important;}'
      +'button,a,input,select,textarea,[role="button"]{touch-action:manipulation;}';
    document.head.appendChild(s);
  }

  function activeVersion(){
    const keys=['resumate.ota.active.v3','resumate.ota.bundle.v7','resumate.ota.bundle.v3'];
    for(const key of keys){
      try{
        const raw=localStorage.getItem(key);
        if(!raw) continue;
        const value=JSON.parse(raw);
        const v=typeof value==='string' ? value : (value && (value.version||value.otaVersion||value.bundleVersion));
        if(v) return String(v);
      }catch(e){
        const raw=localStorage.getItem(key);
        if(raw) return raw;
      }
    }
    return '';
  }

  async function checkUpdate(){
    const b=document.getElementById(id);
    if(!b) return;
    b.style.display='block';
    b.textContent='Update';
    b.classList.remove('resumate-update-ready');
    try{
      const r=await fetch(VERSION_URL+'?whatsnew='+Date.now(),{cache:'no-store'});
      if(!r.ok) return;
      manifest=await r.json();
      const published=String(manifest.version||manifest.otaVersion||manifest.bundleVersion||'');
      const installed=activeVersion();
      if(published && installed && published!==installed){
        b.classList.add('resumate-update-ready');
        b.textContent='NEW • Update';
        b.title='New update available — tap to see What\'s New';
      }else{
        b.title='ResuMate update status';
      }
    }catch(e){
      // Keep the neutral toggle visible when the manifest cannot be checked.
    }
  }

  function close(){
    const m=document.getElementById('resumate-ota-whats-new');
    if(m) m.remove();
  }

  function show(){
    close();
    const notes=Array.isArray(manifest && manifest.whatsNew) ? manifest.whatsNew.filter(Boolean) : [];
    const items=(notes.length ? notes : ['Latest ResuMate improvements and fixes.']).slice(0,8);
    const version=String((manifest && (manifest.appVersion||manifest.version)) || '');
    const wrap=document.createElement('div');
    wrap.id='resumate-ota-whats-new';
    wrap.style.cssText='position:fixed;inset:0;z-index:2147483646;background:rgba(0,0,0,.48);display:flex;align-items:flex-start;justify-content:center;padding:64px 14px 20px;box-sizing:border-box;font-family:system-ui,-apple-system,Segoe UI,sans-serif;pointer-events:auto;';
    wrap.innerHTML='<div role="dialog" aria-modal="true" style="width:min(420px,100%);max-height:80vh;overflow:auto;background:#fff;color:#181A1F;border-radius:16px;box-shadow:0 12px 40px rgba(0,0,0,.35);padding:20px;box-sizing:border-box;pointer-events:auto;">'
      +'<div style="display:flex;align-items:center;justify-content:space-between;gap:12px;"><strong style="font-size:18px;">What\'s New</strong><button id="resumate-ota-close" type="button" aria-label="Close" style="border:0;background:transparent;font-size:24px;line-height:1;cursor:pointer;">×</button></div>'
      +(version?'<div style="font-size:12px;color:#777;margin-top:5px;">ResuMate '+escapeHtml(version.slice(0,12))+'</div>':'')
      +'<ul style="margin:16px 0 20px;padding-left:20px;line-height:1.55;">'+items.map(function(x){return '<li style="margin:7px 0;">'+escapeHtml(x)+'</li>';}).join('')+'</ul>'
      +'<button id="resumate-ota-apply" type="button" style="width:100%;border:0;border-radius:10px;background:#181A1F;color:#fff;padding:11px 14px;font:700 14px system-ui,-apple-system,Segoe UI,sans-serif;cursor:pointer;">Update now</button>'
      +'</div>';
    document.body.appendChild(wrap);
    document.getElementById('resumate-ota-close').onclick=close;
    wrap.addEventListener('click',function(e){ if(e.target===wrap) close(); });
    document.getElementById('resumate-ota-apply').onclick=function(){
      close();
      const b=document.getElementById(id);
      if(b){ applying=true; b.click(); }
    };
  }

  function bind(){
    const b=document.getElementById(id);
    if(!b || b.dataset.whatsNewBound) return;
    b.dataset.whatsNewBound='1';
    b.addEventListener('click',function(e){
      if(applying){ applying=false; return; }
      e.preventDefault();
      e.stopImmediatePropagation();
      show();
    },true);
    checkUpdate();
  }

  function start(){
    ensureStyle();
    bind();
    // Observe only DOM additions. Do not observe style/class mutations: the
    // previous implementation changed pointer-events from inside its own
    // MutationObserver, which could create a mutation loop and block touches.
    const observer=new MutationObserver(function(){ bind(); });
    observer.observe(document.body,{childList:true,subtree:true});
    setInterval(checkUpdate,30000);
    document.addEventListener('visibilitychange',function(){if(!document.hidden) checkUpdate();});
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',start,{once:true});
  else start();
})();
</script>
'''

if 'resumate-ota-whats-new-style' not in text:
    text = text.replace('</body>', script + '</body>', 1)

INDEX.write_text(text, encoding='utf-8')
print('Fixed global touch blocking regression; preserved OTA toggle and removed only unsafe touch-layer interception logic')

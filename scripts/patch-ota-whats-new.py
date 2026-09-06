#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'www' / 'index.html'
text = INDEX.read_text(encoding='utf-8')

# Add a capture-phase click handler so tapping the OTA badge first shows the
# release notes instead of immediately reloading. The existing updater remains
# the final action after the user confirms.
script = r'''
<script>
(function(){
  'use strict';
  const VERSION_URL='https://raw.githubusercontent.com/gba45684-lab/ResuMate2/ota/version.json';
  const id='resumate-ota-status';
  let manifest=null;
  function escapeHtml(value){
    return String(value).replace(/[&<>\"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c];});
  }
  function close(){
    const m=document.getElementById('resumate-ota-whats-new');
    if(m) m.remove();
  }
  function show(){
    close();
    const notes=Array.isArray(manifest && manifest.whatsNew) ? manifest.whatsNew.filter(Boolean) : [];
    const items=(notes.length ? notes : ['Latest ResuMate improvements and fixes.']).slice(0,8);
    const version=String((manifest&& (manifest.appVersion||manifest.version)) || '');
    const wrap=document.createElement('div');
    wrap.id='resumate-ota-whats-new';
    wrap.style.cssText='position:fixed;inset:0;z-index:2147483646;background:rgba(0,0,0,.48);display:flex;align-items:flex-start;justify-content:center;padding:64px 14px 20px;box-sizing:border-box;font-family:system-ui,-apple-system,Segoe UI,sans-serif;';
    wrap.innerHTML='<div role="dialog" aria-modal="true" style="width:min(420px,100%);max-height:80vh;overflow:auto;background:#fff;color:#181A1F;border-radius:16px;box-shadow:0 12px 40px rgba(0,0,0,.35);padding:20px;box-sizing:border-box;">'
      +'<div style="display:flex;align-items:center;justify-content:space-between;gap:12px;"><strong style="font-size:18px;">What\'s New</strong><button id="resumate-ota-close" type="button" aria-label="Close" style="border:0;background:transparent;font-size:24px;line-height:1;cursor:pointer;">×</button></div>'
      +(version?'<div style="font-size:12px;color:#777;margin-top:5px;">ResuMate '+escapeHtml(version.slice(0,12))+'</div>':'')
      +'<ul style="margin:16px 0 20px;padding-left:20px;line-height:1.55;">'+items.map(function(x){return '<li style="margin:7px 0;">'+escapeHtml(x)+'</li>';}).join('')+'</ul>'
      +'<button id="resumate-ota-apply" type="button" style="width:100%;border:0;border-radius:10px;background:#181A1F;color:#fff;padding:11px 14px;font:700 14px system-ui,-apple-system,Segoe UI,sans-serif;cursor:pointer;">Update now</button>'
      +'</div>';
    document.body.appendChild(wrap);
    document.getElementById('resumate-ota-close').onclick=close;
    wrap.addEventListener('click',function(e){ if(e.target===wrap) close(); });
    document.getElementById('resumate-ota-apply').onclick=function(){
      const b=document.getElementById(id);
      close();
      if(b) b.click();
    };
  }
  async function load(){
    try{
      const r=await fetch(VERSION_URL+'?whatsnew='+Date.now(),{cache:'no-store'});
      if(r.ok) manifest=await r.json();
    }catch(e){}
  }
  function bind(){
    const b=document.getElementById(id);
    if(!b || b.dataset.whatsNewBound) return;
    b.dataset.whatsNewBound='1';
    b.addEventListener('click',function(e){
      e.preventDefault();
      e.stopImmediatePropagation();
      show();
    },true);
    load();
  }
  const observer=new MutationObserver(bind);
  function start(){
    bind();
    observer.observe(document.body,{childList:true});
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',start,{once:true});
  else start();
})();
</script>
'''
if 'resumate-ota-whats-new' not in text:
    text = text.replace('</body>', script + '</body>', 1)
INDEX.write_text(text, encoding='utf-8')
print('Added OTA What\'s New dialog with update confirmation')

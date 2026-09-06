#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'www' / 'index.html'
text = INDEX.read_text(encoding='utf-8')

ota_toggle = r'''
<script>
(function(){
  'use strict';
  const VERSION_URL='https://raw.githubusercontent.com/gba45684-lab/ResuMate2/ota/version.json';
  const id='resumate-ota-status';
  const styleId='resumate-ota-toggle-style';
  const scriptId='resumate-ota-toggle-controller';

  const points = [
    'New OTA update indicator is now always visible.',
    'Green blinking indicator clearly shows when a fresh update is available.',
    'Tap Update to see the What\'s New points before applying the update.',
    'OTA updates continue without reinstalling the APK.'
  ];

  function ensureStyle(){
    if(document.getElementById(styleId)) return;
    const s=document.createElement('style');
    s.id=styleId;
    s.textContent='@keyframes resumateOtaBlink{0%,100%{filter:brightness(1);box-shadow:0 2px 10px rgba(0,0,0,.22)}50%{filter:brightness(1.12);box-shadow:0 0 0 4px rgba(34,197,94,.18),0 0 18px rgba(34,197,94,.65)}}#resumate-ota-status.resumate-update-ready{background:#22c55e!important;color:#fff!important;border-color:#16a34a!important;animation:resumateOtaBlink 1.1s ease-in-out infinite!important}#resumate-ota-whats-new{position:fixed;inset:0;z-index:2147483646;background:rgba(0,0,0,.58);display:flex;align-items:center;justify-content:center;padding:18px;box-sizing:border-box}#resumate-ota-whats-new .ota-card{width:min(92vw,380px);background:#fff;color:#181A1F;border-radius:18px;padding:20px;box-shadow:0 18px 50px rgba(0,0,0,.35);font-family:system-ui,-apple-system,Segoe UI,sans-serif}#resumate-ota-whats-new h3{margin:0 0 12px;font-size:19px}#resumate-ota-whats-new ul{margin:0 0 18px;padding-left:20px}#resumate-ota-whats-new li{margin:8px 0;font-size:14px;line-height:1.4}#resumate-ota-whats-new .ota-actions{display:flex;gap:8px;justify-content:flex-end}#resumate-ota-whats-new button{border:0;border-radius:10px;padding:9px 14px;font-weight:700;cursor:pointer}#resumate-ota-whats-new .ota-cancel{background:#eee;color:#222}#resumate-ota-whats-new .ota-apply{background:#16a34a;color:#fff}';
    document.head.appendChild(s);
  }

  function ensureButton(){
    const b=document.getElementById(id);
    if(!b) return null;
    b.style.display='block';
    b.textContent='Update';
    b.setAttribute('aria-label','ResuMate updates');
    return b;
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
        if(localStorage.getItem(key)) return localStorage.getItem(key);
      }
    }
    return '';
  }

  async function hasUpdate(){
    try{
      const r=await fetch(VERSION_URL+'?toggle='+Date.now(),{cache:'no-store'});
      if(!r.ok) return false;
      const m=await r.json();
      const published=String(m.version||m.otaVersion||m.bundleVersion||'');
      const installed=activeVersion();
      return !!(published && installed && published!==installed);
    }catch(e){ return false; }
  }

  function showWhatsNew(){
    document.getElementById('resumate-ota-whats-new')?.remove();
    const wrap=document.createElement('div');
    wrap.id='resumate-ota-whats-new';
    wrap.innerHTML='<div class="ota-card" role="dialog" aria-modal="true" aria-labelledby="resumate-ota-title"><h3 id="resumate-ota-title">What\'s New</h3><ul>'+points.map(p=>'<li>'+p+'</li>').join('')+'</ul><div class="ota-actions"><button class="ota-cancel" type="button">Later</button><button class="ota-apply" type="button">Update now</button></div></div>';
    document.body.appendChild(wrap);
    wrap.querySelector('.ota-cancel').onclick=()=>wrap.remove();
    wrap.querySelector('.ota-apply').onclick=()=>{
      const btn=wrap.querySelector('.ota-apply');
      btn.disabled=true; btn.textContent='Updating…';
      ['resumate.ota.active.v3','resumate.ota.bundle.v7','resumate.ota.bundle.v3'].forEach(k=>localStorage.removeItem(k));
      const done=()=>window.location.reload();
      if('caches' in window){
        caches.keys().then(keys=>Promise.all(keys.filter(k=>/resumate\.ota/i.test(k)).map(k=>caches.delete(k)))).then(done).catch(done);
      }else done();
    };
  }

  async function updateState(){
    const b=ensureButton();
    if(!b) return;
    const available=await hasUpdate();
    b.classList.toggle('resumate-update-ready',available);
    b.title=available?'New update available — tap to see What\'s New':'ResuMate update status';
  }

  function start(){
    ensureStyle();
    ensureButton();
    document.addEventListener('click',function(e){
      const b=e.target.closest && e.target.closest('#'+id);
      if(!b) return;
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      showWhatsNew();
    },true);
    updateState();
    setInterval(updateState,30000);
    document.addEventListener('visibilitychange',()=>{if(!document.hidden) updateState();});
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',start,{once:true});
  else start();
})();
</script>
'''

if 'resumate-ota-toggle-controller' not in text:
    text=text.replace('</body>',ota_toggle+'</body>',1)
INDEX.write_text(text,encoding='utf-8')
print('Added persistent OTA update toggle, green blinking state, and What\'s New popup')

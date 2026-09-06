#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'www' / 'index.html'
text = INDEX.read_text(encoding='utf-8')

# Keep the approved visual system; remove the simulated device chrome and normalize navigation.
css = '''
        /* ResuMate Android/browser navigation + export fixes */
        .status-bar { display:none !important; }
        .header-actions { display:flex; align-items:center; justify-content:flex-end; gap:6px; margin-left:auto; min-width:0; }
        .back-btn { flex:none; min-height:28px; white-space:nowrap; }
        .header-tag { max-width:120px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
'''
if '/* ResuMate Android/browser navigation + export fixes */' not in text:
    text = text.replace('</style>', css + '    </style>', 1)

# Visible OTA status control. It reports whether the installed app has the
# currently published OTA bundle and lets the user force a fresh check.
ota_ui = r'''
<script>
(function(){
  'use strict';
  const VERSION_URL='https://raw.githubusercontent.com/gba45684-lab/ResuMate2/ota/version.json';
  const CACHE_KEY='resumate.ota.bundle.v3';
  const id='resumate-ota-status';
  function ensure(){
    if(document.getElementById(id)) return document.getElementById(id);
    const b=document.createElement('button');
    b.id=id;
    b.type='button';
    b.setAttribute('aria-label','ResuMate update status');
    b.style.cssText='position:fixed;right:10px;bottom:10px;z-index:2147483647;border:1px solid #d7dbe0;border-radius:999px;background:#fff;color:#333;box-shadow:0 2px 10px rgba(0,0,0,.12);padding:7px 11px;font:600 11px system-ui,-apple-system,Segoe UI,sans-serif;cursor:pointer;display:none;max-width:190px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;';
    document.body.appendChild(b);
    b.addEventListener('click',function(){
      b.textContent='↻ Checking update…';
      b.style.display='block';
      window.location.reload();
    });
    return b;
  }
  function set(text,title){
    const b=ensure();
    b.textContent=text;
    b.title=title||text;
    b.style.display='block';
  }
  async function check(){
    try{
      const cached=JSON.parse(localStorage.getItem(CACHE_KEY)||'null');
      const r=await fetch(VERSION_URL+'?status='+Date.now(),{cache:'no-store'});
      if(!r.ok) throw new Error('HTTP '+r.status);
      const m=await r.json();
      const published=String(m.version||m.otaVersion||'');
      const installed=String(cached&&cached.version||'');
      if(published && installed && published===installed){
        set('✓ Fresh update','Installed version is up to date: '+published.slice(0,12));
      }else if(published){
        set('↻ Update available','New update '+published.slice(0,12)+' is available. Tap to refresh.');
      }else{
        set('? Update check','Could not read the published version. Tap to retry.');
      }
    }catch(e){
      set('⚠ Update check failed','Tap to retry the OTA update check.');
    }
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',check,{once:true});
  else check();
})();
</script>
'''
if 'resumate-ota-status' not in text:
    text = text.replace('</body>', ota_ui + '</body>', 1)

old_back = '''            function smartBack() {
                if (state.navHistory.length > 1) {
                    state.navHistory.pop();
                    go(state.navHistory[state.navHistory.length - 1] || 'home', true);
                } else go('home', true);
            }'''
new_back = '''            function smartBack() {
                const overlays = Array.from(document.querySelectorAll('.overlay.show')).filter(x => x.id !== 'welcome');
                if (overlays.length) {
                    overlays[overlays.length - 1].classList.remove('show');
                    return;
                }
                if (mode === 'preview' && document.querySelector('.view.active')?.id === 'builder') {
                    mode = 'edit';
                    renderBuilder();
                    return;
                }
                if (state.navHistory.length > 1) {
                    state.navHistory.pop();
                    go(state.navHistory[state.navHistory.length - 1] || 'home', true);
                } else go('home', true);
            }'''
if old_back in text:
    text = text.replace(old_back, new_back, 1)

helper = '''
            async function saveBlobToNative(blob, filename, mimeType) {
                if (!window.ResuMateNative) return false;
                const base64 = await new Promise((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onloadend = () => resolve(String(reader.result).split(',')[1] || '');
                    reader.onerror = reject;
                    reader.readAsDataURL(blob);
                });
                const result = window.ResuMateNative.saveBase64File(filename, mimeType, base64);
                if (!String(result).startsWith('OK:')) throw new Error(String(result));
                if (typeof window.ResuMateNative.notifyDownload === 'function') {
                    window.ResuMateNative.notifyDownload(filename, mimeType, String(result).slice(3));
                }
                return true;
            }
'''
if 'async function saveBlobToNative' not in text:
    marker = '            // ─── PDF ─────────────────────────────────────────────────────\n'
    text = text.replace(marker, marker + helper, 1)

# DOCX library: fail clearly if CDN is unavailable; do not silently claim a download.
text = text.replace("<script src=\"https://cdn.jsdelivr.net/npm/docx@8.5.0/build/index.min.js\"></script>", "<script src=\"https://cdn.jsdelivr.net/npm/docx@8.5.0/build/index.min.js\" onerror=\"window.__docxLoadFailed=true\"></script>", 1)

start = text.find('            function performPremiumPDFExport() {')
end_marker = '            window.performPremiumPDFExport = performPremiumPDFExport;'
end = text.find(end_marker, start)
if start != -1 and end != -1:
    end += len(end_marker)
    new_pdf = '''            async function performPremiumPDFExport() {
                closeOverlay('pdfExport');
                toast('Generating PDF...');
                const filename = (state.profile.name || 'Resume').replace(/[^a-zA-Z0-9_\-]/g, '_') + '.pdf';
                let temp = null;
                try {
                    if (typeof html2pdf === 'undefined') throw new Error('PDF library not loaded');
                    temp = document.createElement('div');
                    temp.style.width = '800px';
                    temp.style.padding = '20px';
                    temp.style.background = '#ffffff';
                    temp.style.color = '#181A1F';
                    temp.innerHTML = resumeHTML();
                    document.body.appendChild(temp);
                    const opt = {
                        margin: 10,
                        filename,
                        image: { type: 'jpeg', quality: 0.98 },
                        html2canvas: { scale: 2, useCORS: true, logging: false },
                        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
                    };
                    const pdfBlob = await html2pdf().set(opt).from(temp).outputPdf('blob');
                    if (window.ResuMateNative) {
                        await saveBlobToNative(pdfBlob, filename, 'application/pdf');
                        toast('PDF saved to Downloads/ResuMate/Resumes');
                    } else {
                        const url = URL.createObjectURL(pdfBlob);
                        const link = document.createElement('a');
                        link.href = url;
                        link.download = filename;
                        document.body.appendChild(link);
                        link.click();
                        link.remove();
                        setTimeout(() => URL.revokeObjectURL(url), 2000);
                        toast('PDF exported successfully!');
                    }
                } catch (err) {
                    toast('PDF export error: ' + err.message);
                    console.error(err);
                } finally {
                    if (temp && temp.parentNode) temp.parentNode.removeChild(temp);
                }
            }
            window.performPremiumPDFExport = performPremiumPDFExport;'''
    text = text[:start] + new_pdf + text[end:]

start = text.find('            function exportDOCX() {')
end_marker = '            window.exportDOCX = exportDOCX;'
end = text.find(end_marker, start)
if start != -1 and end != -1:
    end += len(end_marker)
    new_docx = '''            async function exportDOCX() {
                if (typeof docx === 'undefined' || window.__docxLoadFailed) {
                    toast('DOCX library not loaded. Check internet connection and retry.');
                    return;
                }
                try {
                    const { Document, Packer, Paragraph, TextRun, HeadingLevel } = docx;
                    const doc = new Document({ sections: [{ properties: {}, children: [
                        new Paragraph({ children: [new TextRun({ text: state.profile.name, bold: true, size: 28 })], heading: HeadingLevel.HEADING_1 }),
                        new Paragraph({ children: [new TextRun({ text: state.profile.role, size: 22, color: '1D3450' })] }),
                        new Paragraph({ children: [new TextRun({ text: [state.profile.email, state.profile.phone, state.profile.location].filter(Boolean).join(' · '), size: 18, color: '888888' })] }),
                        ...(state.summary ? [new Paragraph({ children: [new TextRun({ text: 'SUMMARY', bold: true, size: 20 })], heading: HeadingLevel.HEADING_2 }), new Paragraph({ children: [new TextRun({ text: state.summary, size: 20 })] })] : []),
                        ...state.experience.flatMap(exp => [new Paragraph({ children: [new TextRun({ text: exp.company, bold: true, size: 20 }), new TextRun({ text: ' — ' + exp.role, size: 18 }), new TextRun({ text: ' (' + (exp.from || '') + '-' + (exp.to || '') + ')', size: 16, color: '888888' })] }), ...exp.bullets.filter(Boolean).map(b => new Paragraph({ children: [new TextRun({ text: '• ' + b, size: 18 })], bullet: { level: 0 } }))]),
                        ...(state.skills.length ? [new Paragraph({ children: [new TextRun({ text: 'SKILLS', bold: true, size: 20 })], heading: HeadingLevel.HEADING_2 }), new Paragraph({ children: [new TextRun({ text: state.skills.join(' · '), size: 18 })] })] : []),
                        ...(state.education.length ? [new Paragraph({ children: [new TextRun({ text: 'EDUCATION', bold: true, size: 20 })], heading: HeadingLevel.HEADING_2 }), ...state.education.map(edu => new Paragraph({ children: [new TextRun({ text: edu.school + ' — ' + edu.degree, size: 18 })] }))] : [])
                    ] }] });
                    const blob = await Packer.toBlob(doc);
                    const filename = (state.profile.name || 'Resume').replace(/[^a-zA-Z0-9_\-]/g, '_') + '.docx';
                    if (window.ResuMateNative) {
                        await saveBlobToNative(blob, filename, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document');
                        toast('DOCX saved to Downloads/ResuMate/Resumes');
                    } else {
                        const url = URL.createObjectURL(blob);
                        const link = document.createElement('a');
                        link.href = url;
                        link.download = filename;
                        document.body.appendChild(link);
                        link.click();
                        link.remove();
                        setTimeout(() => URL.revokeObjectURL(url), 2000);
                        toast('DOCX downloaded');
                    }
                } catch (e) {
                    toast('DOCX export error: ' + e.message);
                    console.error(e);
                }
            }
            window.exportDOCX = exportDOCX;'''
    text = text[:start] + new_docx + text[end:]

INDEX.write_text(text, encoding='utf-8')
print('Patched web UI: hidden simulated device status bar, navigation/back, PDF export, DOCX export, native download notifications, visible OTA update status toggle')

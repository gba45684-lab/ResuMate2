#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'www' / 'index.html'
text = INDEX.read_text(encoding='utf-8')

# Never invoke Android/browser print UI for resume export.
text = text.replace('window.print();', '/* ResuMate print export disabled */')

# Replace the export handlers after the baseline patch so PDF always downloads directly
# and DOCX uses exactly the same visible resume text as the PDF source.
def replace_function(source, name, replacement, assignment):
    start = source.find(f'            function {name}(')
    if start == -1:
        start = source.find(f'            async function {name}(')
    if start == -1:
        raise SystemExit(f'{name} not found')
    end = source.find(assignment, start)
    if end == -1:
        raise SystemExit(f'{assignment} not found')
    end += len(assignment)
    return source[:start] + replacement + source[end:]

pdf = '''            async function performPremiumPDFExport() {
                closeOverlay('pdfExport');
                toast('Generating high-quality PDF...');
                const filename = (state.profile.name || 'Resume').replace(/[^a-zA-Z0-9_-]/g, '_') + '.pdf';
                let temp = null;
                try {
                    if (typeof html2pdf === 'undefined') throw new Error('PDF library not loaded');

                    // Export the same rendered resume, but use a true A4 page canvas with
                    // controlled page margins. The previous JPEG/scale-2 pipeline softened
                    // small text; PNG at high DPI keeps characters and thin rules crisp.
                    temp = document.createElement('div');
                    temp.className = 'resumate-pdf-export-root';
                    temp.style.width = '210mm';
                    temp.style.minHeight = '297mm';
                    temp.style.boxSizing = 'border-box';
                    temp.style.margin = '0';
                    temp.style.padding = '0';
                    temp.style.background = '#ffffff';
                    temp.style.color = '#181A1F';
                    temp.style.overflow = 'visible';
                    temp.innerHTML = resumeHTML();

                    const printStyle = document.createElement('style');
                    printStyle.textContent = `
                        @page { size: A4 portrait; margin: 0; }
                        .resumate-pdf-export-root { width: 210mm !important; min-height: 297mm !important; }
                        .resumate-pdf-export-root * { box-sizing: border-box; }
                        .resumate-pdf-export-root img { max-width: 100%; }
                        .resumate-pdf-export-root .page-break,
                        .resumate-pdf-export-root .avoid-break { break-inside: avoid; page-break-inside: avoid; }
                    `;
                    temp.prepend(printStyle);
                    document.body.appendChild(temp);

                    // Reference-page margin target: restrained, even whitespace on all four
                    // sides instead of the old 10mm margin + 20px wrapper double-padding.
                    const opt = {
                        margin: [14, 14, 16, 14],
                        filename,
                        image: { type: 'png', quality: 1 },
                        pagebreak: { mode: ['css', 'legacy'], avoid: ['.avoid-break'] },
                        html2canvas: {
                            scale: 4,
                            useCORS: true,
                            allowTaint: false,
                            backgroundColor: '#ffffff',
                            logging: false,
                            imageTimeout: 15000,
                            windowWidth: 794,
                            scrollX: 0,
                            scrollY: 0
                        },
                        jsPDF: {
                            unit: 'mm',
                            format: 'a4',
                            orientation: 'portrait',
                            compress: true,
                            putOnlyUsedFonts: true,
                            precision: 12
                        }
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
                        toast('PDF downloaded');
                    }
                } catch (err) {
                    toast('PDF export error: ' + err.message);
                    console.error(err);
                } finally {
                    if (temp && temp.parentNode) temp.parentNode.removeChild(temp);
                }
            }
            window.performPremiumPDFExport = performPremiumPDFExport;'''
text = replace_function(text, 'performPremiumPDFExport', pdf, 'window.performPremiumPDFExport = performPremiumPDFExport;')

docx = '''            async function exportDOCX() {
                if (typeof docx === 'undefined' || window.__docxLoadFailed) {
                    toast('DOCX library not loaded.');
                    return;
                }
                let source = null;
                try {
                    const { Document, Packer, Paragraph, TextRun } = docx;
                    // Use the exact same rendered resumeHTML() source as PDF, then export
                    // its visible text line-for-line. This keeps DOCX text identical to PDF.
                    source = document.createElement('div');
                    source.style.position = 'fixed';
                    source.style.left = '-100000px';
                    source.style.width = '210mm';
                    source.innerHTML = resumeHTML();
                    document.body.appendChild(source);
                    const lines = String(source.innerText || source.textContent || '')
                        .replace(/\\u00a0/g, ' ')
                        .split(/\\r?\\n/)
                        .map(s => s.replace(/[ \\t]+/g, ' ').trim())
                        .filter(Boolean);
                    const children = lines.map(line => new Paragraph({
                        children: [new TextRun({ text: line, size: 20 })],
                        spacing: { after: 80 }
                    }));
                    const doc = new Document({ sections: [{ properties: {}, children }] });
                    const blob = await Packer.toBlob(doc);
                    const filename = (state.profile.name || 'Resume').replace(/[^a-zA-Z0-9_-]/g, '_') + '.docx';
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
                } finally {
                    if (source && source.parentNode) source.parentNode.removeChild(source);
                }
            }
            window.exportDOCX = exportDOCX;'''
text = replace_function(text, 'exportDOCX', docx, 'window.exportDOCX = exportDOCX;')

INDEX.write_text(text, encoding='utf-8')
print('Finalized high-quality A4 PDF export: PNG/high-DPI rendering, controlled full-page margins, and no print dialog')

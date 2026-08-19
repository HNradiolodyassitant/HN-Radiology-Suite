#!/usr/bin/env python3
from pathlib import Path

p = Path('index.html')
text = p.read_text(encoding='utf-8')
module_marker = '/* module: src/components/Common/ReportOutput.jsx */'
start = text.find(module_marker)
if start < 0:
    raise SystemExit('ReportOutput module marker not found')
end = text.find('/* module:', start + len(module_marker))
if end < 0:
    end = text.find('</script>', start)
if end < 0:
    raise SystemExit('ReportOutput module end not found')
module = text[start:end]

marker = '/* HN_INSURANCE_A5_CURRENT_V1 */'
if marker in module:
    print('Current-report A5 insurance patch already present; no-op')
    raise SystemExit(0)

copy_anchor = '''    const copyForCMS = async () => {
        if (!validate()) return;
        await copyText(normalizeForCMS(editorText()));
        flash("نسخه سازگار با CMS کپی شد");
    };'''
if module.count(copy_anchor) != 1:
    raise SystemExit(f'copyForCMS anchor count={module.count(copy_anchor)}')

insurance_fn = r'''
    /* HN_INSURANCE_A5_CURRENT_V1 */
    const printInsuranceCurrent = () => {
        if (!validate()) return;
        const text = editorText();
        if (!text) return flash("متن گزارش هنوز خالی است");
        const win = window.open("", "_blank", "width=760,height=980");
        if (!win) return flash("پنجره چاپ توسط مرورگر مسدود شد");
        const reportHtml = editorRef.current ? editorRef.current.innerHTML : editableHtml;
        const safePatientName = escapeHtml(patientName.trim() || "—");
        const safePatientId = escapeHtml(patientId.trim() || "—");
        const safeReportTitle = escapeHtml(reportTitle.trim() || examTitle || "گزارش سونوگرافی");
        const printDate = escapeHtml(new Date().toLocaleDateString("fa-IR"));
        const headerAsset = window.HNPrintAssets && window.HNPrintAssets.letterheadHeader ? window.HNPrintAssets.letterheadHeader : "";
        const peyda = window.HNPrintAssets && window.HNPrintAssets.peydaVariable ? window.HNPrintAssets.peydaVariable : "";
        const fontFace = peyda ? `@font-face{font-family:"Peyda";src:url("${peyda}") format("woff2");font-style:normal;font-weight:100 900;font-display:swap}` : "";
        const headerHtml = headerAsset ? `<div class="insurance-letterhead"><img src="${headerAsset}" alt="سربرگ درمانگاه ولیعصر"></div>` : `<div class="insurance-letterhead-fallback"><strong>درمانگاه ولیعصر</strong><span>بخش رادیولوژی و سونوگرافی</span></div>`;
        win.document.write(`<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>چاپ بیمه A5</title><style>${fontFace}
@page{size:A5 portrait;margin:5mm}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#fff;color:#111}
body{font-family:"Peyda",Arial,Tahoma,sans-serif;direction:rtl}
.insurance-sheet{width:100%;min-height:200mm;display:flex;flex-direction:column;position:relative}
.insurance-letterhead{width:100%;margin:0 0 2mm;overflow:hidden}
.insurance-letterhead img{display:block;width:100%;height:auto}
.insurance-letterhead-fallback{height:28mm;border-bottom:.3mm solid #333;display:flex;flex-direction:column;align-items:center;justify-content:center;margin-bottom:3mm}
.insurance-letterhead-fallback strong{font-size:17pt}.insurance-letterhead-fallback span{font-size:9pt;color:#555}
.patient-row{display:grid;grid-template-columns:1.45fr 1fr .85fr;gap:2.5mm;align-items:center;border-top:.25mm solid #aaa;border-bottom:.25mm solid #aaa;padding:2.1mm 1mm;margin:0 0 3mm;font-size:8.7pt;line-height:1.5}
.patient-row b{font-weight:800}.patient-row .value{font-weight:650}
.report-title{text-align:right;font-size:12.2pt;font-weight:850;margin:0 0 3mm;padding:0 1mm}
.report{font-size:9.4pt;line-height:1.72;text-align:right;overflow-wrap:anywhere;word-break:normal;padding:0 1mm;flex:1}
.report p,.report div{margin-top:0;margin-bottom:1.15mm}.report h1,.report h2,.report h3{margin:2mm 0 1mm;font-size:10.4pt}.report ul,.report ol{margin:1mm 0;padding-right:5mm}
.signature{width:42mm;margin-top:5mm;margin-right:auto;margin-left:1mm;text-align:center;font-size:8.3pt;color:#444;padding-top:2mm;border-top:.25mm solid #999;min-height:13mm}
@media screen{body{background:#e5e7eb;padding:12px}.insurance-sheet{width:138mm;min-height:200mm;margin:0 auto;background:#fff;padding:0;box-shadow:0 3px 18px #0002}}
@media print{body{background:#fff}.insurance-sheet{min-height:200mm}.insurance-sheet:last-child{page-break-after:auto}}
</style></head><body><section class="insurance-sheet">${headerHtml}<div class="patient-row"><div><b>نام و نام خانوادگی بیمار:</b> <span class="value">${safePatientName}</span></div><div><b>Patient ID:</b> <span class="value" dir="ltr">${safePatientId}</span></div><div><b>تاریخ:</b> <span class="value">${printDate}</span></div></div><div class="report-title">${safeReportTitle}</div><div class="report">${reportHtml}</div><div class="signature">مهر و امضای پزشک</div></section><script>window.onload=()=>{setTimeout(()=>{window.focus();window.print();},120)}<\/script></body></html>`);
        win.document.close();
        flash("نسخه A5 برای چاپ بیمه آماده شد");
    };'''
module = module.replace(copy_anchor, copy_anchor + insurance_fn, 1)

button_anchor = '            h("button", { type: "button", onClick: copyForCMS, style: Object.assign({}, actionStyle, { background: "#0f766e", color: "white", border: "1px solid #5eead4" }) }, "کپی برای CMS"),'
if module.count(button_anchor) != 1:
    raise SystemExit(f'CMS button anchor count={module.count(button_anchor)}')
insurance_button = button_anchor + '\n            h("button", { type: "button", onClick: printInsuranceCurrent, style: Object.assign({}, actionStyle, { background: "#15803d", color: "white", border: "1px solid #86efac" }) }, "چاپ بیمه"),'
module = module.replace(button_anchor, insurance_button, 1)

new_text = text[:start] + module + text[end:]

# Safety invariants: only one current-report insurance feature, CMS/PDF untouched.
if new_text.count(marker) != 1:
    raise SystemExit('Insurance marker count invalid')
if new_text.count('onClick: printInsuranceCurrent') != 1:
    raise SystemExit('Insurance button count invalid')
if new_text.count('"کپی برای CMS"') != text.count('"کپی برای CMS"'):
    raise SystemExit('CMS button unexpectedly changed')
if new_text.count('onClick: printReport') != text.count('onClick: printReport'):
    raise SystemExit('Normal PDF/print button unexpectedly changed')
if '@page{size:A5 portrait;margin:5mm}' not in new_text:
    raise SystemExit('A5 print CSS missing')
if 'نام و نام خانوادگی بیمار:' not in new_text or 'Patient ID:' not in new_text:
    raise SystemExit('Patient identity fields missing')
if len(new_text) - len(text) > 9000:
    raise SystemExit('Patch unexpectedly large')

p.write_text(new_text, encoding='utf-8')
print('Applied current-report A5 insurance print button and template')

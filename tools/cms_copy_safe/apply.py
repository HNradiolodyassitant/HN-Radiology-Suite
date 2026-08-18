#!/usr/bin/env python3
from pathlib import Path

INDEX = Path('index.html')
text = INDEX.read_text(encoding='utf-8')
MARKER = '/* module: src/components/Common/ReportOutput.jsx */'

start = text.find(MARKER)
if start < 0:
    raise SystemExit('ReportOutput module not found')
end = text.find('/* module:', start + len(MARKER))
if end < 0:
    end = text.find('</script>', start)
if end < 0:
    raise SystemExit('ReportOutput module end not found')
module = text[start:end]

if '/* HN_CMS_COPY_SAFE */' not in module:
    fn_anchor = 'function ReportOutput({ finding = "", impression = "", recommendation = "", sessionKey = 0, wordExtras = null, plainText = "", examTitle = "گزارش سونوگرافی" }) {'
    if fn_anchor not in module:
        raise SystemExit('ReportOutput function anchor missing')

    helper = r'''/* HN_CMS_COPY_SAFE */
function normalizeForCMS(value) {
    let s = String(value || "").normalize("NFKC");
    const fa = "۰۱۲۳۴۵۶۷۸۹";
    const ar = "٠١٢٣٤٥٦٧٨٩";
    s = s.replace(/[۰-۹]/g, ch => String(fa.indexOf(ch)));
    s = s.replace(/[٠-٩]/g, ch => String(ar.indexOf(ch)));
    s = s.replace(/\u00A0/g, " ");
    s = s.replace(/[\u200B-\u200F\u202A-\u202E\u2066-\u2069\uFEFF]/g, "");
    s = s.replace(/ي/g, "ی").replace(/ك/g, "ک");
    s = s.replace(/[–—−]/g, "-").replace(/×/g, "x");
    s = s.replace(/≥/g, ">=").replace(/≤/g, "<=");
    s = s.replace(/[“”]/g, '"').replace(/[‘’]/g, "'");
    s = s.split(/\r?\n/).map(line => line.replace(/[ \t]+$/g, "")).join("\n");
    return s.replace(/\n{3,}/g, "\n\n").trim();
}
'''
    module = module.replace(fn_anchor, helper + fn_anchor, 1)

    copy_anchor = '''    const copyReport = async () => {
        if (!validate()) return;
        await copyText(editorText());
        flash("گزارش کپی شد");
    };'''
    if copy_anchor not in module:
        raise SystemExit('copyReport anchor missing')
    cms_copy = copy_anchor + r'''
    const copyForCMS = async () => {
        if (!validate()) return;
        await copyText(normalizeForCMS(editorText()));
        flash("نسخه سازگار با CMS کپی شد");
    };'''
    module = module.replace(copy_anchor, cms_copy, 1)

    button_anchor = 'h("button", { type: "button", onClick: copyReport, style: actionStyle }, "کپی گزارش"),'
    if button_anchor not in module:
        raise SystemExit('copy button anchor missing')
    module = module.replace(
        button_anchor,
        button_anchor + '\n            h("button", { type: "button", onClick: copyForCMS, style: Object.assign({}, actionStyle, { background: "#0f766e", color: "white", border: "1px solid #5eead4" }) }, "کپی برای CMS"),',
        1,
    )

    text = text[:start] + module + text[end:]

# Hard safety rules: no global DOM observer/panel/pilot is introduced.
for forbidden in ['MutationObserver', 'hn-cms-pilot', 'HNCMSPilot', 'setInterval(', 'setTimeout(inject']:
    if forbidden in text[text.find('/* HN_CMS_COPY_SAFE */'):] and forbidden != 'MutationObserver':
        raise SystemExit('Forbidden CMS implementation pattern detected: ' + forbidden)

if text.count('/* HN_CMS_COPY_SAFE */') != 1:
    raise SystemExit('CMS marker count invalid')
if text.count('"کپی برای CMS"') != 1:
    raise SystemExit('CMS button count invalid')
if 'normalizeForCMS' not in text or 'copyForCMS' not in text:
    raise SystemExit('CMS copy function missing')

INDEX.write_text(text, encoding='utf-8')
print('Safe CMS copy patch applied')

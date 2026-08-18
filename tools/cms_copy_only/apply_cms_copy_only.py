#!/usr/bin/env python3
from pathlib import Path
import re

INDEX = Path('index.html')
text = INDEX.read_text(encoding='utf-8')

# 1) Remove the entire previous experimental CMS Pilot layer.
text = re.sub(
    r'\s*<!-- HN_CMS_PILOT_START -->.*?<!-- HN_CMS_PILOT_END -->\s*',
    '\n',
    text,
    flags=re.S,
)

MARKER = '/* module: src/components/Common/ReportOutput.jsx */'
start = text.find(MARKER)
if start < 0:
    raise SystemExit('ReportOutput module marker not found')
end = text.find('/* module:', start + len(MARKER))
if end < 0:
    end = text.find('</script>', start)
if end < 0:
    raise SystemExit('ReportOutput module end not found')
module = text[start:end]

# Idempotent: if the minimal native patch already exists, do not duplicate it.
if '/* HN_CMS_COPY_ONLY */' not in module:
    fn_anchor = 'function ReportOutput({ finding = "", impression = "", recommendation = "", sessionKey = 0, wordExtras = null, plainText = "", examTitle = "گزارش سونوگرافی" }) {'
    if fn_anchor not in module:
        raise SystemExit('ReportOutput function anchor not found')

    helper = r'''/* HN_CMS_COPY_ONLY */
function normalizeTextForCMS(value) {
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
        raise SystemExit('copyReport anchor not found')

    cms_copy = copy_anchor + r'''
    const copyForCMS = async () => {
        if (!validate()) return;
        const normalized = normalizeTextForCMS(editorText());
        await copyText(normalized);
        flash("نسخه سازگار با CMS کپی شد");
    };'''
    module = module.replace(copy_anchor, cms_copy, 1)

    button_anchor = 'h("button", { type: "button", onClick: copyReport, style: actionStyle }, "کپی گزارش"),'
    if button_anchor not in module:
        raise SystemExit('Copy button anchor not found')
    button_replacement = button_anchor + '\n            h("button", { type: "button", onClick: copyForCMS, style: Object.assign({}, actionStyle, { background: "#0f766e", color: "white", border: "1px solid #5eead4" }) }, "کپی برای CMS"),'
    module = module.replace(button_anchor, button_replacement, 1)

    text = text[:start] + module + text[end:]

# Safety validation: previous pilot must be gone; only copy-only marker should remain.
for forbidden in ['HN_CMS_PILOT_START', 'hn-cms-pilot-fab', 'MutationObserver(records=>', 'HNCMSPilot']:
    if forbidden in text:
        raise SystemExit('Old CMS pilot residue remains: ' + forbidden)
for required in ['/* HN_CMS_COPY_ONLY */', 'normalizeTextForCMS', 'copyForCMS', 'کپی برای CMS']:
    if required not in text:
        raise SystemExit('CMS copy-only validation failed: ' + required)

INDEX.write_text(text, encoding='utf-8')
print('CMS Pilot removed; minimal Copy for CMS installed.')

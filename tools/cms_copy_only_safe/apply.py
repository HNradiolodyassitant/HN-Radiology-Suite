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

marker = '/* HN_CMS_COPY_ONLY_SAFE */'
if marker in module:
    print('CMS copy patch already present; no-op')
    raise SystemExit(0)

fn_anchor = 'function ReportOutput({ finding = "", impression = "", recommendation = "", sessionKey = 0, wordExtras = null, plainText = "", examTitle = "گزارش سونوگرافی" }) {'
if module.count(fn_anchor) != 1:
    raise SystemExit(f'ReportOutput function anchor count={module.count(fn_anchor)}')

helper = r'''/* HN_CMS_COPY_ONLY_SAFE */
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
if module.count(copy_anchor) != 1:
    raise SystemExit(f'copyReport anchor count={module.count(copy_anchor)}')
copy_block = copy_anchor + r'''
    const copyForCMS = async () => {
        if (!validate()) return;
        await copyText(normalizeForCMS(editorText()));
        flash("نسخه سازگار با CMS کپی شد");
    };'''
module = module.replace(copy_anchor, copy_block, 1)

button_anchor = '            h("button", { type: "button", onClick: copyReport, style: actionStyle }, "کپی گزارش"),'
if module.count(button_anchor) != 1:
    raise SystemExit(f'copy button anchor count={module.count(button_anchor)}')
button = button_anchor + '\n            h("button", { type: "button", onClick: copyForCMS, style: Object.assign({}, actionStyle, { background: "#0f766e", color: "white", border: "1px solid #5eead4" }) }, "کپی برای CMS"),'
module = module.replace(button_anchor, button, 1)

new_text = text[:start] + module + text[end:]

# Safety invariants
if new_text.count(marker) != 1:
    raise SystemExit('CMS marker count invalid')
if new_text.count('"کپی برای CMS"') != 1:
    raise SystemExit('CMS button count invalid')
if 'MutationObserver' in module or 'setInterval(' in module or 'hn-cms-pilot' in module or 'HNCMSPilot' in module:
    raise SystemExit('Forbidden global/pilot pattern detected in patched module')
if len(new_text) - len(text) > 5000:
    raise SystemExit('Patch unexpectedly large')

p.write_text(new_text, encoding='utf-8')
print('Applied minimal CMS copy button patch')

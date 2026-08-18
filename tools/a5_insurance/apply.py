from pathlib import Path

PATH = Path("index.html")
MARKER = "HN_A5_INSURANCE_V1"
text = PATH.read_text(encoding="utf-8")

module_marker = '/* module: src/components/MyReports.jsx */'
module_start = text.find(module_marker)
if module_start < 0:
    raise SystemExit("MyReports module marker not found")
module_end = text.find('exports.default = MyReports;', module_start)
if module_end < 0:
    raise SystemExit("MyReports module end not found")

segment = text[module_start:module_end]
if MARKER in segment:
    required = ["چاپ بیمه A5", "چاپ A5 گزارش‌های فیلترشده", "چاپ A5 گزارش‌های امروز"]
    missing = [x for x in required if x not in segment]
    if missing:
        raise SystemExit(f"Existing A5 marker is incomplete: {missing}")
    print("A5 insurance patch already present and valid")
    raise SystemExit(0)

helpers_anchor = 'function MyReports({ goBack }) {'
if segment.count(helpers_anchor) != 1:
    raise SystemExit("Unexpected MyReports function anchor count")

helpers = r'''/* HN_A5_INSURANCE_V1 */
function escapeInsuranceHtml(value) {
    return String(value == null ? "" : value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}
function insuranceReportText(item) {
    if (String(item && item.fullReport || "").trim()) return String(item.fullReport).trim();
    const sections = [];
    if (String(item && item.finding || "").trim()) sections.push(`یافته‌ها:\n${String(item.finding).trim()}`);
    if (String(item && item.impression || "").trim()) sections.push(`نتیجه‌گیری:\n${String(item.impression).trim()}`);
    if (String(item && item.recommendation || "").trim()) sections.push(`پیشنهاد:\n${String(item.recommendation).trim()}`);
    return sections.join("\n\n");
}
function sameLocalDay(iso, reference = new Date()) {
    const date = new Date(iso);
    return !Number.isNaN(date.getTime()) &&
        date.getFullYear() === reference.getFullYear() &&
        date.getMonth() === reference.getMonth() &&
        date.getDate() === reference.getDate();
}
function printInsuranceA5(items) {
    const rows = (Array.isArray(items) ? items : []).filter(Boolean);
    if (!rows.length) return false;
    const pages = rows.map(item => {
        const patientId = escapeInsuranceHtml(item.patientId || "------");
        const title = escapeInsuranceHtml(item.examTitle || "گزارش سونوگرافی");
        const date = escapeInsuranceHtml(formatDate(item.createdAt || new Date().toISOString()));
        const report = escapeInsuranceHtml(insuranceReportText(item));
        return `<section class="page"><div class="header"><strong>گزارش جهت ارائه به بیمه</strong></div><div class="meta"><div><b>Patient ID:</b> ${patientId}</div><div><b>تاریخ:</b> ${date}</div><div class="wide"><b>نوع بررسی:</b> ${title}</div></div><div class="report">${report}</div><div class="signature">مهر و امضای پزشک</div></section>`;
    }).join("");
    const win = window.open("", "_blank", "width=800,height=1000");
    if (!win) return false;
    const peyda = window.HNPrintAssets && window.HNPrintAssets.peydaVariable ? window.HNPrintAssets.peydaVariable : "";
    const fontFace = peyda ? `@font-face{font-family:"Peyda";src:url("${peyda}") format("woff2");font-style:normal;font-weight:100 900;font-display:swap}` : "";
    win.document.write(`<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><title>چاپ بیمه A5</title><style>${fontFace}@page{size:A5 portrait;margin:10mm}html,body{margin:0;padding:0;background:#fff;color:#111}body{font-family:"Peyda",Arial,Tahoma,sans-serif;direction:rtl}.page{page-break-after:always;min-height:190mm;box-sizing:border-box;position:relative;padding-bottom:18mm}.page:last-child{page-break-after:auto}.header{border-bottom:1px solid #111;padding-bottom:3mm;margin-bottom:4mm;text-align:center;font-size:13pt}.meta{display:grid;grid-template-columns:1fr 1fr;gap:2mm 5mm;font-size:10pt;margin-bottom:5mm}.meta .wide{grid-column:1/-1}.report{white-space:pre-wrap;line-height:1.85;font-size:10.5pt;text-align:right;overflow-wrap:anywhere}.signature{position:absolute;left:0;bottom:2mm;width:42mm;text-align:center;border-top:1px solid #aaa;padding-top:2mm;font-size:9pt;color:#444}@media screen{body{background:#e5e7eb;padding:12px}.page{width:148mm;margin:0 auto 12px;background:white;padding:10mm;box-shadow:0 3px 18px #0002}.signature{left:10mm;bottom:10mm}}@media print{.page{padding:0}}</style></head><body>${pages}<script>window.onload=()=>{window.focus();window.print();}<\/script></body></html>`);
    win.document.close();
    return true;
}
'''
segment = segment.replace(helpers_anchor, helpers + helpers_anchor, 1)

filtered_anchor = '    const filtered = reports.filter(item => !search.trim() || String(item.patientId || "").includes(search.trim()) || String(item.examTitle || "").includes(search.trim()));'
if segment.count(filtered_anchor) != 1:
    raise SystemExit("Filtered reports anchor not found exactly once")
segment = segment.replace(filtered_anchor, filtered_anchor + '\n    const todayReports = reports.filter(item => sameLocalDay(item.createdAt));', 1)

print_anchor = '    const downloadWord = item => {'
if segment.count(print_anchor) != 1:
    raise SystemExit("downloadWord anchor not found exactly once")
print_handler = '''    const printA5 = items => {
        if (!printInsuranceA5(items)) {
            flash("پنجره چاپ باز نشد؛ اجازه Pop-up مرورگر را بررسی کنید.", 3500);
            return;
        }
        flash("نسخه A5 برای چاپ بیمه آماده شد");
    };
'''
segment = segment.replace(print_anchor, print_handler + print_anchor, 1)

count_anchor = '        h("div", { style: { marginTop: "15px", color: "#7dd3fc" } }, `${filtered.length} گزارش از ${reports.length} گزارش ذخیره‌شده`),'
if segment.count(count_anchor) != 1:
    raise SystemExit("Report count UI anchor not found exactly once")
batch_ui = '''        h("div", { style: { display: "flex", gap: "8px", flexWrap: "wrap", marginTop: "12px" } },
            h("button", { type: "button", disabled: !filtered.length, onClick: () => printA5(filtered), style: { background: "#7c3aed", color: "white", border: "1px solid #c4b5fd" } }, `چاپ A5 گزارش‌های فیلترشده (${filtered.length})`),
            h("button", { type: "button", disabled: !todayReports.length, onClick: () => printA5(todayReports), style: { background: "#6d28d9", color: "white", border: "1px solid #c4b5fd" } }, `چاپ A5 گزارش‌های امروز (${todayReports.length})`)
        ),'''
segment = segment.replace(count_anchor, count_anchor + '\n' + batch_ui, 1)

copy_button_anchor = '                h("button", { type: "button", onClick: () => copy(item.fullReport || "") }, "کپی گزارش"),'
if segment.count(copy_button_anchor) != 1:
    raise SystemExit("Per-report copy button anchor not found exactly once")
a5_button = '                h("button", { type: "button", onClick: () => printA5([item]), style: { background: "#7c3aed", color: "white", border: "1px solid #c4b5fd" } }, "چاپ بیمه A5"),'
segment = segment.replace(copy_button_anchor, copy_button_anchor + '\n' + a5_button, 1)

patched = text[:module_start] + segment + text[module_end:]

checks = {
    MARKER: 1,
    '"چاپ بیمه A5"': 1,
    'چاپ A5 گزارش‌های فیلترشده': 1,
    'چاپ A5 گزارش‌های امروز': 1,
}
for token, expected in checks.items():
    count = patched.count(token)
    if count != expected:
        raise SystemExit(f"Validation failed for {token!r}: expected {expected}, got {count}")

for token in ["HN_V2162_NATIVE_RENAL", "HN_V2162_NATIVE_IUD", "HN_V2162_NATIVE_TWIN", "کپی برای CMS"]:
    if token not in patched:
        raise SystemExit(f"Required existing feature missing after patch: {token}")

if "HN CMS Pilot" in patched:
    raise SystemExit("Unsafe CMS Pilot marker detected")

PATH.write_text(patched, encoding="utf-8")
print("Applied HN A5 Insurance v1 safely to MyReports")

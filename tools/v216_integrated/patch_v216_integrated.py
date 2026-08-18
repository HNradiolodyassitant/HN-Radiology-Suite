#!/usr/bin/env python3
from pathlib import Path
import re

INDEX = Path('index.html')
START = '<!-- HN_V216_NATIVE_PLACEMENT_START -->'
END = '<!-- HN_V216_NATIVE_PLACEMENT_END -->'

text = INDEX.read_text(encoding='utf-8')
required = ['hnTwinV215Button', 'hnv216-launch', 'HNClinicalAddonsV216']
missing = [x for x in required if x not in text]
if missing:
    raise SystemExit('Required v2.16 UI hooks missing: ' + ', '.join(missing))


def module_slice(source, marker):
    start = source.find(marker)
    if start < 0:
        raise SystemExit('Module marker not found: ' + marker)
    end = source.find('/* module:', start + len(marker))
    if end < 0:
        end = source.find('</script>', start)
    if end < 0:
        raise SystemExit('Could not find module end: ' + marker)
    return start, end, source[start:end]


def replace_module(source, marker, updated):
    start, end, _ = module_slice(source, marker)
    return source[:start] + updated + source[end:]


# -----------------------------------------------------------------------------
# 1) Kidney: real native repeatable Renal Scar section + automatic report output
# -----------------------------------------------------------------------------
KIDNEY_MARKER = '/* module: src/components/Kidney/KidneyCard.jsx */'
_, _, kidney = module_slice(text, KIDNEY_MARKER)
if '/* HN_V2162_NATIVE_RENAL */' not in kidney:
    helper_anchor = 'function KidneyCard({ onReportChange, showPreview = true }) {'
    if helper_anchor not in kidney:
        raise SystemExit('KidneyCard helper anchor not found')

    renal_helper = r'''/* HN_V2162_NATIVE_RENAL */
const makeRenalScarNative = (index = 1) => ({
    id: `renal-scar-${Date.now()}-${index}-${Math.random().toString(36).slice(2, 6)}`,
    side: "راست",
    pole: "قطب فوقانی",
    length: "",
    minParenchyma: "",
    contour: "depressed",
    echogenicity: "increased",
    calyx: "none",
    note: "",
});
function RenalScarSectionNative({ value, onChange }) {
    const scars = Array.isArray(value) ? value : [];
    const update = (id, key, nextValue) => onChange(scars.map((x) => x.id === id ? { ...x, [key]: nextValue } : x));
    const add = () => onChange([...scars, makeRenalScarNative(scars.length + 1)]);
    const remove = (id) => onChange(scars.filter((x) => x.id !== id));
    const labelStyle = { display: "grid", gap: "6px" };
    return ((0, jsx_runtime_1.jsxs)("div", { id: "hn-v216-inline-renal", style: groupStyle, children: [
        (0, jsx_runtime_1.jsx)("h3", { children: "اسکار پارانشیم کلیه" }),
        (0, jsx_runtime_1.jsx)("p", { style: { color: "#94a3b8", marginTop: 0 }, children: "در صورت مشاهده کاهش موضعی ضخامت پارانشیم/نامنظمی کورتیکال، هر اسکار را جداگانه ثبت کنید." }),
        scars.map((scar, index) => ((0, jsx_runtime_1.jsxs)("div", { style: subCardStyle, children: [
            (0, jsx_runtime_1.jsxs)("div", { style: { display: "flex", alignItems: "center", justifyContent: "space-between", gap: "8px", flexWrap: "wrap" }, children: [
                (0, jsx_runtime_1.jsxs)("strong", { children: ["اسکار ", index + 1] }),
                (0, jsx_runtime_1.jsx)("button", { type: "button", onClick: () => remove(scar.id), children: "حذف" })
            ] }),
            (0, jsx_runtime_1.jsxs)("div", { style: gridStyle, children: [
                (0, jsx_runtime_1.jsxs)("label", { style: labelStyle, children: ["سمت", (0, jsx_runtime_1.jsx)("select", { style: fieldStyle, value: scar.side, onChange: (e) => update(scar.id, "side", e.target.value), children: ["راست", "چپ"].map((x) => (0, jsx_runtime_1.jsx)("option", { value: x, children: x }, x)) })] }),
                (0, jsx_runtime_1.jsxs)("label", { style: labelStyle, children: ["محل", (0, jsx_runtime_1.jsx)("select", { style: fieldStyle, value: scar.pole, onChange: (e) => update(scar.id, "pole", e.target.value), children: ["قطب فوقانی", "قسمت میانی", "قطب تحتانی", "چندکانونی"].map((x) => (0, jsx_runtime_1.jsx)("option", { value: x, children: x }, x)) })] }),
                (0, jsx_runtime_1.jsxs)("label", { style: labelStyle, children: ["طول تقریبی ناحیه (mm)", (0, jsx_runtime_1.jsx)("input", { style: fieldStyle, type: "number", value: scar.length, onChange: (e) => update(scar.id, "length", e.target.value) })] }),
                (0, jsx_runtime_1.jsxs)("label", { style: labelStyle, children: ["حداقل ضخامت پارانشیم (mm)", (0, jsx_runtime_1.jsx)("input", { style: fieldStyle, type: "number", value: scar.minParenchyma, onChange: (e) => update(scar.id, "minParenchyma", e.target.value) })] }),
                (0, jsx_runtime_1.jsxs)("label", { style: labelStyle, children: ["Contour", (0, jsx_runtime_1.jsxs)("select", { style: fieldStyle, value: scar.contour, onChange: (e) => update(scar.id, "contour", e.target.value), children: [(0, jsx_runtime_1.jsx)("option", { value: "depressed", children: "فرورفتگی/نامنظمی کورتیکال" }), (0, jsx_runtime_1.jsx)("option", { value: "smooth", children: "صاف" })] })] }),
                (0, jsx_runtime_1.jsxs)("label", { style: labelStyle, children: ["Echogenicity", (0, jsx_runtime_1.jsxs)("select", { style: fieldStyle, value: scar.echogenicity, onChange: (e) => update(scar.id, "echogenicity", e.target.value), children: [(0, jsx_runtime_1.jsx)("option", { value: "increased", children: "افزایش اکوژنیسیته" }), (0, jsx_runtime_1.jsx)("option", { value: "normal", children: "اکوژنیسیته طبیعی" })] })] }),
                (0, jsx_runtime_1.jsxs)("label", { style: labelStyle, children: ["کالیس مجاور", (0, jsx_runtime_1.jsxs)("select", { style: fieldStyle, value: scar.calyx, onChange: (e) => update(scar.id, "calyx", e.target.value), children: [(0, jsx_runtime_1.jsx)("option", { value: "none", children: "بدون تغییر واضح" }), (0, jsx_runtime_1.jsx)("option", { value: "deformed", children: "Clubbed / deformed" })] })] }),
                (0, jsx_runtime_1.jsxs)("label", { style: labelStyle, children: ["توضیح اضافی", (0, jsx_runtime_1.jsx)("textarea", { style: { ...fieldStyle, minHeight: "64px" }, value: scar.note, onChange: (e) => update(scar.id, "note", e.target.value) })] })
            ] })
        ] }, scar.id))),
        (0, jsx_runtime_1.jsx)("button", { type: "button", onClick: add, style: { marginTop: "12px" }, children: "+ افزودن اسکار کلیه" })
    ] }));
}

'''
    kidney = kidney.replace(helper_anchor, renal_helper + helper_anchor, 1)

    state_anchor = '    leftPelvisAP: "",\n    fullnessSide: "none",'
    if state_anchor not in kidney:
        raise SystemExit('Kidney renalScars state anchor not found')
    kidney = kidney.replace(state_anchor, '    leftPelvisAP: "",\n    renalScars: [],\n    fullnessSide: "none",', 1)

    report_anchor = '        if (state.fullnessSide !== "none") {'
    if report_anchor not in kidney:
        raise SystemExit('Kidney report anchor not found')
    renal_report = r'''        (state.renalScars || []).forEach((scar) => {
            const lines = [];
            let sentence = `در ${scar.pole} کلیه ${scar.side}`;
            if (scar.length) sentence += ` ناحیه‌ای به طول تقریبی ${scar.length} میلی‌متر`;
            sentence += " همراه با کاهش موضعی ضخامت پارانشیم، مطرح‌کننده اسکار پارانشیمی مشاهده شد.";
            lines.push(sentence);
            if (scar.minParenchyma) lines.push(`حداقل ضخامت پارانشیم در این ناحیه حدود ${scar.minParenchyma} میلی‌متر است.`);
            if (scar.contour === "depressed") lines.push("فرورفتگی/نامنظمی کورتیکال در محل مذکور مشاهده شد.");
            if (scar.echogenicity === "increased") lines.push("افزایش اکوژنیسیته پارانشیم در ناحیه مذکور مشاهده شد.");
            if (scar.calyx === "deformed") lines.push("کالیس مجاور دارای نمای clubbed/deformed است.");
            if (String(scar.note || "").trim()) lines.push(String(scar.note).trim());
            cards.push({ finding: lines.join("\n"), impression: `اسکار پارانشیمی کلیه ${scar.side}.`, recommendation: "" });
        });
'''
    kidney = kidney.replace(report_anchor, renal_report + report_anchor, 1)

    preview_anchor = 'showPreview && (0, jsx_runtime_1.jsx)(ReportOutput_jsx_1.default, { ...report })'
    if preview_anchor not in kidney:
        raise SystemExit('Kidney UI preview anchor not found')
    kidney = kidney.replace(preview_anchor, '(0, jsx_runtime_1.jsx)(RenalScarSectionNative, { value: state.renalScars, onChange: (renalScars) => set("renalScars", renalScars) }), ' + preview_anchor, 1)
    text = replace_module(text, KIDNEY_MARKER, kidney)


# -----------------------------------------------------------------------------
# 2) Female Pelvis: native IUD fields + automatic report integration
# -----------------------------------------------------------------------------
PELVIS_MARKER = '/* module: src/components/Workflow/ExamCards.jsx */'
_, _, pelvis = module_slice(text, PELVIS_MARKER)
if '/* HN_V2162_NATIVE_IUD */' not in pelvis:
    state_anchor = '  cysts:[],\n  freeFluid:"none"\n};'
    if state_anchor not in pelvis:
        raise SystemExit('FemalePelvis IUD state anchor not found')
    iud_state = '''  cysts:[],\n  /* HN_V2162_NATIVE_IUD */\n  iudEnabled:false,\n  iudType:"copper",\n  iudPosition:"fundal",\n  iudFundalDistance:"",\n  iudOrientation:"normal",\n  iudEmbedment:"none",\n  iudPerforation:"none",\n  iudNote:"",\n  freeFluid:"none"\n};'''
    pelvis = pelvis.replace(state_anchor, iud_state, 1)

    report_anchor = '  if(examId!=="femaleAbdomenPelvis"){' 
    if report_anchor not in pelvis:
        raise SystemExit('FemalePelvis IUD report anchor not found')
    iud_report = r'''  if(s.iudEnabled){
    const typeFa={copper:"Copper IUD",lng:"LNG-IUS",other:"IUD"}[s.iudType]||"IUD";
    const posFa={
      fundal:"IUD در موقعیت فوندال مناسب داخل حفره رحم مشاهده شد.",
      low:"Low-lying IUD در قسمت تحتانی حفره رحم مشاهده شد.",
      cervical:"IUD در کانال سرویکس مشاهده شد.",
      partial:"قسمتی از IUD در کانال سرویکس قرار گرفته و نمای partial expulsion مطرح است.",
      embedded:"شواهدی از embedment قسمتی از IUD در میومتر مشاهده شد.",
      perforation:"موقعیت IUD مشکوک به perforation است.",
      notseen:"IUD در بررسی انجام‌شده مشاهده نشد."
    };
    f.push(`نوع وسیله داخل رحمی: ${typeFa}.`);
    if(posFa[s.iudPosition]) f.push(posFa[s.iudPosition]);
    if(s.iudPosition!=="notseen" && s.iudFundalDistance) f.push(`فاصله انتهای فوقانی IUD از فوندوس حفره رحم حدود ${s.iudFundalDistance} میلی‌متر است.`);
    if(s.iudPosition!=="notseen" && s.iudOrientation!=="normal") f.push(`Orientation وسیله: ${{rotated:"چرخیده",oblique:"مایل",inverted:"معکوس"}[s.iudOrientation]||s.iudOrientation}.`);
    if(s.iudEmbedment!=="none") f.push(`Embedment: ${{arm:"درگیری arm",stem:"درگیری stem",uncertain:"مشکوک/نامشخص"}[s.iudEmbedment]||s.iudEmbedment}.`);
    if(s.iudPerforation!=="none") f.push(`Perforation: ${{suspected:"مشکوک",partial:"partial",complete:"complete"}[s.iudPerforation]||s.iudPerforation}.`);
    if(String(s.iudNote||"").trim()) f.push(String(s.iudNote).trim());
    const abnormal=["low","cervical","partial","embedded","perforation"].includes(s.iudPosition)||s.iudEmbedment!=="none"||s.iudPerforation!=="none";
    if(abnormal) i.push("موقعیت/وضعیت IUD غیرطبیعی است.");
    if(s.iudPosition==="notseen") i.push("IUD در بررسی سونوگرافیک مشاهده نشد.");
    if(s.iudPosition==="cervical"||s.iudPosition==="partial") r.push("ارزیابی متخصص زنان از نظر malposition/expulsion توصیه می‌شود.");
    if(s.iudPosition==="perforation"||s.iudPerforation!=="none") r.push("ارزیابی تخصصی زنان و تطبیق با معاینه/تصویربرداری تکمیلی جهت رد perforation توصیه می‌شود.");
  }
'''
    pelvis = pelvis.replace(report_anchor, iud_report + report_anchor, 1)

    ui_anchor = '    details("مایع آزاد لگنی",h("div",{style:gridStyle},label("میزان مایع آزاد",select(s.freeFluid,v=>set("freeFluid",v),[["none","مشاهده نشد"],["mild","مختصر"],["moderate","متوسط"],["large","زیاد"]]))),false)'
    if ui_anchor not in pelvis:
        raise SystemExit('FemalePelvis IUD UI anchor not found')
    iud_ui = r'''    details("IUD — موقعیت و وضعیت",h("div",{id:"hn-v216-inline-iud"},
      h("div",{style:gridStyle},
        label("بررسی IUD",select(s.iudEnabled?"yes":"no",v=>set("iudEnabled",v==="yes"),[["no","گزارش نشود"],["yes","IUD بررسی شود"]])),
        s.iudEnabled?label("نوع IUD",select(s.iudType,v=>set("iudType",v),[["copper","Copper IUD"],["lng","LNG-IUS"],["other","سایر"]])):null,
        s.iudEnabled?label("موقعیت",select(s.iudPosition,v=>set("iudPosition",v),[["fundal","Fundal / مناسب"],["low","Low-lying"],["cervical","داخل کانال سرویکس"],["partial","Partial expulsion"],["embedded","Embedded"],["perforation","مشکوک به perforation"],["notseen","مشاهده نشد"]])):null,
        s.iudEnabled&&s.iudPosition!=="notseen"?label("فاصله انتهای فوقانی از فوندوس (mm)",h("input",{style:fieldStyle,type:"number",value:s.iudFundalDistance,onChange:e=>set("iudFundalDistance",e.target.value)})):null,
        s.iudEnabled&&s.iudPosition!=="notseen"?label("Orientation",select(s.iudOrientation,v=>set("iudOrientation",v),[["normal","طبیعی"],["rotated","چرخیده"],["oblique","مایل"],["inverted","معکوس"]])):null,
        s.iudEnabled?label("Embedment",select(s.iudEmbedment,v=>set("iudEmbedment",v),[["none","مشاهده نشد"],["arm","Arm"],["stem","Stem"],["uncertain","مشکوک/نامشخص"]])):null,
        s.iudEnabled?label("Perforation",select(s.iudPerforation,v=>set("iudPerforation",v),[["none","شواهدی ندارد"],["suspected","مشکوک"],["partial","Partial"],["complete","Complete"]])):null,
        s.iudEnabled?label("توضیح اضافی",h("input",{style:fieldStyle,value:s.iudNote,onChange:e=>set("iudNote",e.target.value)})):null
      )
    ),false),
'''
    pelvis = pelvis.replace(ui_anchor, iud_ui + ui_anchor, 1)
    text = replace_module(text, PELVIS_MARKER, pelvis)


# -----------------------------------------------------------------------------
# 3) Women & Pregnancy: Twin becomes a real native engine card.
#    Existing native RPOC/PAS/Hadlock remain untouched and are not duplicated.
# -----------------------------------------------------------------------------
WOMEN_MARKER = '/* module: src/components/ObGyn/WomenPregnancyCore.jsx */'
_, _, women = module_slice(text, WOMEN_MARKER)
if '/* HN_V2162_NATIVE_TWIN */' not in women:
    engines_anchor = 'const engines=['
    if engines_anchor not in women:
        raise SystemExit('WomenPregnancy engines anchor not found')
    twin_engine = r'''/* HN_V2162_NATIVE_TWIN */
function TwinPregnancyEngine(){
 return h("div",{id:"hn-v216-inline-pregnancy"},
  h("section",{style:panel},h("h2",{style:{marginTop:0}},"بارداری دوقلویی"),h("p",{style:muted},"این زیرماژول در همان هسته زنان و بارداری اجرا می‌شود و از پنجره یا دکمه شناور جداگانه استفاده نمی‌کند.")),
  h("iframe",{id:"hn-v216-inline-twin",src:"twin-pregnancy.html",title:"Twin Pregnancy Module",style:{display:"block",width:"100%",height:"82vh",minHeight:"760px",border:"1px solid #475569",borderRadius:"14px",background:"#0b1220"}})
 );
}

'''
    women = women.replace(engines_anchor, twin_engine + engines_anchor, 1)

    bpp_anchor = ' {id:"bpp",title:"بیوفیزیکال پروفایل",en:"Biophysical profile",icon:"✓",keywords:"bpp biophysical profile tone movement breathing fluid nst"}'
    if bpp_anchor not in women:
        raise SystemExit('WomenPregnancy BPP engine anchor not found')
    twin_card = ' {id:"twin",title:"بارداری دوقلویی",en:"Twin pregnancy",icon:"◉◉",keywords:"twin twins multiple pregnancy chorionicity amnionicity dichorionic monochorionic diamniotic دوقلویی دو قلویی چندقلویی"},\n'
    women = women.replace(bpp_anchor, twin_card + bpp_anchor, 1)

    render_old = 'active==="early"?h(EarlyPregnancyEngine):active==="nt"?h(NtEngine):active==="anomaly"?h(AnomalyEngine):active==="fgr"?h(FgrEngine):active==="rpoc"?h(RpocEngine):active==="pas"?h(PasEngine):h(BppEngine)'
    render_new = 'active==="early"?h(EarlyPregnancyEngine):active==="nt"?h(NtEngine):active==="anomaly"?h(AnomalyEngine):active==="fgr"?h(FgrEngine):active==="rpoc"?h(RpocEngine):active==="pas"?h(PasEngine):active==="twin"?h(TwinPregnancyEngine):h(BppEngine)'
    if render_old not in women:
        raise SystemExit('WomenPregnancy render chain anchor not found')
    women = women.replace(render_old, render_new, 1)
    women = women.replace('HN Women & Pregnancy Core — هفت موتور تخصصی + Pregnancy Dating', 'HN Women & Pregnancy Core — هشت موتور تخصصی + Pregnancy Dating', 1)
    text = replace_module(text, WOMEN_MARKER, women)


# Remove the old placement/button layer. Keep legacy clinical code in the file only
# as a rollback source; it is no longer visible in normal UI.
text = re.sub(re.escape(START) + r'.*?' + re.escape(END), '', text, flags=re.S)
placement = r'''<!-- HN_V216_NATIVE_PLACEMENT_START -->
<style id="hn-v216-native-placement-style">
/* v2.16.2: original-form integration. Legacy launchers/modals are rollback-only. */
#hnTwinV215Button,#hnTwinV215Modal,#hnv216-launch,#hnv216-modal,.hn-v216-native-row{display:none!important}
@media print{#hnTwinV215Button,#hnTwinV215Modal,#hnv216-launch,#hnv216-modal,.hn-v216-native-row{display:none!important}}
</style>
<!-- HN_V216_NATIVE_PLACEMENT_END -->'''

pos = text.lower().rfind('</body>')
if pos < 0:
    raise SystemExit('index.html has no </body>')
text = text[:pos] + '\n' + placement + '\n' + text[pos:]

# Safety validation before writing.
checks = [
    '/* HN_V2162_NATIVE_RENAL */',
    '/* HN_V2162_NATIVE_IUD */',
    '/* HN_V2162_NATIVE_TWIN */',
    'hn-v216-inline-renal',
    'hn-v216-inline-iud',
    'hn-v216-inline-pregnancy',
    'hn-v216-inline-twin',
    'active==="twin"?h(TwinPregnancyEngine)',
    'renalScars: []',
    'iudEnabled:false',
]
for needle in checks:
    if needle not in text:
        raise SystemExit('Native integration validation failed: ' + needle)
if text.count(START) != 1 or text.count(END) != 1:
    raise SystemExit('Placement marker count invalid')

INDEX.write_text(text, encoding='utf-8')
print('v2.16.2 native inline integration applied:', INDEX.stat().st_size, 'bytes')

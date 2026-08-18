#!/usr/bin/env python3
from pathlib import Path
import re

INDEX = Path('index.html')
START = '<!-- HN_CMS_PILOT_START -->'
END = '<!-- HN_CMS_PILOT_END -->'

text = INDEX.read_text(encoding='utf-8')
required = ['aria-label="گزارش نهایی"', 'Patient ID — اختیاری', 'نام بیمار — اختیاری']
missing = [x for x in required if x not in text]
if missing:
    raise SystemExit('Required report output hooks missing: ' + ', '.join(missing))

text = re.sub(re.escape(START) + r'.*?' + re.escape(END), '', text, flags=re.S)

payload = r'''<!-- HN_CMS_PILOT_START -->
<style id="hn-cms-pilot-style">
#hn-cms-pilot-fab{position:fixed;right:14px;bottom:14px;z-index:2147483001;background:#0f766e;color:#fff;border:1px solid #5eead4;border-radius:999px;padding:9px 14px;font:700 13px Arial,Tahoma,sans-serif;box-shadow:0 8px 28px #0008;cursor:pointer}
#hn-cms-pilot-panel{position:fixed;right:16px;bottom:64px;width:min(430px,calc(100vw - 32px));max-height:78vh;overflow:auto;z-index:2147483002;background:#111827;color:#f8fafc;border:1px solid #475569;border-radius:16px;padding:16px;box-shadow:0 24px 70px #000b;direction:rtl;font-family:Arial,Tahoma,sans-serif}
#hn-cms-pilot-panel[hidden]{display:none!important}
#hn-cms-pilot-panel h3{margin:0 0 8px}
#hn-cms-pilot-panel p{font-size:12px;line-height:1.8;color:#cbd5e1}
#hn-cms-pilot-panel input{width:100%;padding:9px 10px;border-radius:8px;border:1px solid #64748b;background:#f8fafc;color:#0f172a;margin-top:6px}
#hn-cms-pilot-panel .hn-cms-row{display:flex;gap:8px;flex-wrap:wrap;margin-top:9px}
#hn-cms-pilot-panel button,.hn-cms-inline-btn{cursor:pointer;border-radius:8px;padding:8px 11px;border:1px solid #64748b;background:#1e293b;color:#fff;font:700 12px Arial,Tahoma,sans-serif}
#hn-cms-pilot-panel button.primary,.hn-cms-inline-btn{background:#0f766e;border-color:#5eead4}
#hn-cms-pilot-status{margin-top:10px;padding:9px;border-radius:8px;background:#0b2230;border:1px solid #33536c;font-size:12px;line-height:1.8}
.hn-cms-locked{outline:2px solid #22c55e!important;outline-offset:1px!important;background:#ecfdf5!important;color:#14532d!important}
.hn-cms-inline-btn{margin-right:4px}
.hn-cms-badge{display:inline-flex;align-items:center;gap:6px;border:1px solid #22c55e;background:#052e16;color:#bbf7d0;border-radius:999px;padding:5px 9px;font-size:11px;font-weight:700}
#hn-cms-toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);z-index:2147483647;background:#020617;color:#fff;border:1px solid #64748b;border-radius:10px;padding:10px 14px;box-shadow:0 10px 35px #000a;font:13px Arial,Tahoma,sans-serif;direction:rtl;max-width:min(520px,90vw);text-align:center}
@media print{#hn-cms-pilot-fab,#hn-cms-pilot-panel,#hn-cms-toast,.hn-cms-inline-btn,.hn-cms-badge{display:none!important}}
</style>
<script id="hn-cms-pilot-script">
(()=>{
'use strict';
if(window.HNCMSPilot)return;
const state={locked:false,patientId:'',patientName:'',rows:[],lastPacket:null};
const asciiDigits=s=>String(s||'').replace(/[۰-۹]/g,ch=>'۰۱۲۳۴۵۶۷۸۹'.indexOf(ch)).replace(/[٠-٩]/g,ch=>'٠١٢٣٤٥٦٧٨٩'.indexOf(ch));
function cmsSafe(value){
 let s=String(value||'').normalize('NFKC');
 s=asciiDigits(s).replace(/\u00a0/g,' ').replace(/[\u200b-\u200f\u202a-\u202e\u2066-\u2069\ufeff]/g,'');
 s=s.replace(/ي/g,'ی').replace(/ك/g,'ک').replace(/[–—−]/g,'-').replace(/×/g,'x').replace(/≥/g,'>=').replace(/≤/g,'<=').replace(/[“”]/g,'"').replace(/[‘’]/g,"'");
 s=s.split(/\r?\n/).map(x=>x.replace(/[ \t]+$/g,'')).join('\n').replace(/\n{3,}/g,'\n\n').trim();
 return s;
}
function visible(el){return !!(el&&el.isConnected&&el.getClientRects().length);}
function allVisible(selector){return Array.from(document.querySelectorAll(selector)).filter(visible);}
function patientFields(){
 const names=allVisible('input[placeholder*="نام بیمار"]');
 const ids=allVisible('input[placeholder*="Patient ID"]');
 return {name:names[names.length-1]||null,id:ids[ids.length-1]||null};
}
function reportEditor(){
 const rich=allVisible('[contenteditable="true"][aria-label="گزارش نهایی"]');
 if(rich.length)return rich[rich.length-1];
 const areas=allVisible('textarea');
 return areas.reverse().find(x=>(x.value||'').trim().length>20)||null;
}
function reportText(){const e=reportEditor();return e?(e.isContentEditable?String(e.innerText||''):String(e.value||'')):'';}
function examTitle(){
 const labels=allVisible('label');
 for(const l of labels){if((l.textContent||'').includes('عنوان سونوگرافی')){const s=l.querySelector('select');if(s&&s.value&&s.value!=='__custom__')return s.value;}}
 return 'گزارش سونوگرافی';
}
function setNativeValue(el,value){
 if(!el)return;
 const setter=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;
 setter.call(el,String(value||''));
 el.dispatchEvent(new Event('input',{bubbles:true}));
 el.dispatchEvent(new Event('change',{bubbles:true}));
}
function toast(msg){let t=document.getElementById('hn-cms-toast');if(!t){t=document.createElement('div');t.id='hn-cms-toast';document.body.appendChild(t);}t.textContent=msg;clearTimeout(toast._timer);toast._timer=setTimeout(()=>t.remove(),2600);}
async function copyPlain(text){
 const safe=cmsSafe(text);
 if(!safe)throw new Error('متن گزارش خالی است');
 try{await navigator.clipboard.writeText(safe);}catch(_){const ta=document.createElement('textarea');ta.value=safe;ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.focus();ta.select();document.execCommand('copy');ta.remove();}
 return safe;
}
function currentIdentity(){const f=patientFields();return {patientId:String(f.id&&f.id.value||'').trim(),patientName:String(f.name&&f.name.value||'').trim()};}
function verifyLocked(){
 if(!state.locked)return true;
 const now=currentIdentity();
 if(now.patientId!==state.patientId||now.patientName!==state.patientName){toast('هشدار: اطلاعات بیمار با بیمار قفل‌شده تطابق ندارد. ارسال متوقف شد.');return false;}
 return true;
}
function applyLockVisual(){
 const f=patientFields();
 [f.id,f.name].forEach(el=>{if(!el)return;el.readOnly=!!state.locked;el.classList.toggle('hn-cms-locked',!!state.locked);});
 let badge=document.getElementById('hn-cms-identity-badge');
 if(state.locked&&f.id){if(!badge){badge=document.createElement('span');badge.id='hn-cms-identity-badge';badge.className='hn-cms-badge';f.id.insertAdjacentElement('afterend',badge);}badge.textContent=`🔒 ${state.patientName} | ${state.patientId}`;}else if(badge)badge.remove();
 renderStatus();
}
function lockPatient(){
 const now=currentIdentity();
 if(!now.patientId||!now.patientName){toast('برای قفل بیمار، نام بیمار و Patient ID را کامل کنید.');return false;}
 state.locked=true;state.patientId=now.patientId;state.patientName=now.patientName;applyLockVisual();toast('هویت بیمار قفل شد ✓');return true;
}
function unlockPatient(){if(!state.locked)return; if(!confirm('قفل هویت بیمار باز شود؟'))return;state.locked=false;state.patientId='';state.patientName='';applyLockVisual();toast('قفل بیمار باز شد');}
async function copyForCMS(){if(!verifyLocked())return;try{await copyPlain(reportText());toast('نسخه CMS-safe کپی شد ✓');}catch(e){toast(e.message||'کپی انجام نشد');}}
function downloadPacket(){
 if(!state.locked){toast('قبل از ارسال Bridge، هویت بیمار را قفل کنید.');return;}
 if(!verifyLocked())return;
 const reportCms=cmsSafe(reportText());if(!reportCms){toast('متن گزارش خالی است');return;}
 const packet={schema:'hn-cms-pilot/v1',createdAt:new Date().toISOString(),patientId:state.patientId,patientName:state.patientName,examTitle:examTitle(),reportCms,source:'HN Radiology Suite'};
 const blob=new Blob([JSON.stringify(packet,null,2)],{type:'application/json;charset=utf-8'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=`HN_CMS_${asciiDigits(state.patientId).replace(/[^0-9A-Za-z_-]/g,'_')}_${Date.now()}.hncms.json`;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);state.lastPacket=packet;toast('بسته CMS Bridge ساخته شد ✓');
}
function parseLine(line,delim){const out=[];let cur='',q=false;for(let i=0;i<line.length;i++){const ch=line[i];if(ch==='"'){if(q&&line[i+1]==='"'){cur+='"';i++;}else q=!q;}else if(ch===delim&&!q){out.push(cur.trim());cur='';}else cur+=ch;}out.push(cur.trim());return out;}
function importRows(text){
 const lines=String(text||'').replace(/^\ufeff/,'').split(/\r?\n/).filter(x=>x.trim());if(!lines.length)return [];
 const first=lines[0];const delims=[',',';','\t'];const delim=delims.sort((a,b)=>(first.split(b).length-first.split(a).length))[0];
 const matrix=lines.map(x=>parseLine(x,delim));const headers=matrix[0].map(x=>x.toLowerCase().replace(/[_-]+/g,' ').replace(/\s+/g,' ').trim());
 const idKeys=['patient id','patientid','id','شماره پرونده','کد بیمار','کد پذیرش','شماره پذیرش','پذیرش'];const nameKeys=['patient name','name','نام بیمار','نام و نام خانوادگی','نام'];
 let idIdx=headers.findIndex(h=>idKeys.some(k=>h===k||h.includes(k)));let nameIdx=headers.findIndex(h=>nameKeys.some(k=>h===k||h.includes(k)));
 const hasHeader=idIdx>=0||nameIdx>=0;if(idIdx<0)idIdx=0;if(nameIdx<0)nameIdx=Math.min(1,(matrix[0]||[]).length-1);
 const data=hasHeader?matrix.slice(1):matrix;
 return data.map(r=>({patientId:String(r[idIdx]||'').trim(),patientName:String(r[nameIdx]||'').trim()})).filter(x=>x.patientId||x.patientName);
}
function lookup(q){
 q=String(q||'').trim();if(!q)return null;const aq=asciiDigits(q).toLowerCase();return state.rows.find(x=>asciiDigits(x.patientId).toLowerCase()===aq)||state.rows.find(x=>String(x.patientName||'').toLowerCase().includes(q.toLowerCase()))||null;
}
function applyPatient(p){if(state.locked){toast('ابتدا قفل بیمار قبلی را باز کنید.');return;}const f=patientFields();if(!f.id||!f.name){toast('ابتدا وارد صفحه گزارش نهایی شوید.');return;}setNativeValue(f.id,p.patientId);setNativeValue(f.name,p.patientName);toast(`بیمار بارگذاری شد: ${p.patientName}`);}
function renderStatus(){const el=document.getElementById('hn-cms-pilot-status');if(!el)return;el.innerHTML=state.locked?`<b style="color:#86efac">بیمار قفل است ✓</b><br>${escapeHtml(state.patientName)}<br>Patient ID: <span dir="ltr">${escapeHtml(state.patientId)}</span>`:`بیمار هنوز قفل نشده است. پس از تطبیق نام و Patient ID، «قفل بیمار» را بزنید.`;}
function escapeHtml(s){return String(s||'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function createPanel(){
 if(document.getElementById('hn-cms-pilot-fab'))return;
 const fab=document.createElement('button');fab.id='hn-cms-pilot-fab';fab.type='button';fab.textContent='CMS ولیعصر';
 const panel=document.createElement('section');panel.id='hn-cms-pilot-panel';panel.hidden=true;panel.innerHTML=`<h3>CMS Pilot — ولیعصر</h3><p>مرحله آزمایشی: کپی سازگار با CMS، قفل هویت بیمار، ورود لیست پذیرش و ساخت بسته Bridge. هیچ اطلاعاتی به اینترنت یا CMS ارسال نمی‌شود.</p><div id="hn-cms-pilot-status"></div><div class="hn-cms-row"><button class="primary" id="hn-cms-lock" type="button">🔒 قفل بیمار</button><button id="hn-cms-unlock" type="button">باز کردن قفل</button><button class="primary" id="hn-cms-copy" type="button">کپی برای CMS</button></div><hr style="border-color:#334155;margin:14px 0"><b>لیست پذیرش / بارکدخوان</b><input id="hn-cms-search" placeholder="Patient ID یا نام بیمار — سپس Enter"><div class="hn-cms-row"><button id="hn-cms-import" type="button">ورود CSV/TXT پذیرش</button><input id="hn-cms-file" type="file" accept=".csv,.txt,text/csv,text/plain" hidden><span id="hn-cms-count" style="font-size:11px;color:#93c5fd"></span></div><hr style="border-color:#334155;margin:14px 0"><b>Bridge Test</b><p>برای تست مسیر HN → کامپیوتر کلینیک. در نسخه Pilot فقط بسته را به Bridge می‌دهد؛ نوشتن مستقیم در CMS بعد از شناسایی CMS فعال می‌شود.</p><button class="primary" id="hn-cms-packet" type="button">ساخت بسته برای CMS Bridge</button><div class="hn-cms-row"><button id="hn-cms-close" type="button">بستن</button></div>`;
 document.body.append(panel,fab);fab.addEventListener('click',()=>{panel.hidden=!panel.hidden;renderStatus();});document.getElementById('hn-cms-close').onclick=()=>panel.hidden=true;document.getElementById('hn-cms-lock').onclick=lockPatient;document.getElementById('hn-cms-unlock').onclick=unlockPatient;document.getElementById('hn-cms-copy').onclick=copyForCMS;document.getElementById('hn-cms-packet').onclick=downloadPacket;
 const fi=document.getElementById('hn-cms-file');document.getElementById('hn-cms-import').onclick=()=>fi.click();fi.onchange=async()=>{const file=fi.files&&fi.files[0];if(!file)return;try{state.rows=importRows(await file.text());document.getElementById('hn-cms-count').textContent=`${state.rows.length} بیمار بارگذاری شد`;toast(`${state.rows.length} بیمار از فایل پذیرش خوانده شد`);}catch(e){toast('فایل پذیرش قابل خواندن نبود');}fi.value='';};
 const search=document.getElementById('hn-cms-search');search.addEventListener('keydown',e=>{if(e.key!=='Enter')return;e.preventDefault();const p=lookup(search.value);if(p)applyPatient(p);else if(search.value.trim()){const f=patientFields();if(f.id&&!state.locked){setNativeValue(f.id,asciiDigits(search.value.trim()));toast('Patient ID ثبت شد؛ نام بیمار را تطبیق دهید.');}else toast('بیمار در لیست واردشده پیدا نشد.');}});
}
function injectInlineButtons(){
 const copyButtons=allVisible('button').filter(b=>(b.textContent||'').trim()==='کپی گزارش');
 copyButtons.forEach(b=>{const parent=b.parentElement;if(!parent||parent.querySelector('.hn-cms-inline-btn'))return;const x=document.createElement('button');x.type='button';x.className='hn-cms-inline-btn';x.textContent='کپی برای CMS';x.onclick=copyForCMS;b.insertAdjacentElement('afterend',x);});
 applyLockVisual();
}
document.addEventListener('click',e=>{const t=e.target&&e.target.closest&&e.target.closest('button');if(t&&(t.textContent||'').includes('بیمار جدید')){state.locked=false;state.patientId='';state.patientName='';setTimeout(applyLockVisual,80);}},true);
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>{createPanel();injectInlineButtons();},{once:true});else{createPanel();injectInlineButtons();}
const observer=new MutationObserver(()=>injectInlineButtons());observer.observe(document.documentElement,{childList:true,subtree:true});
window.HNCMSPilot={version:'2.16.3-pilot',cmsSafe,copyForCMS,lockPatient,unlockPatient,downloadPacket,state};
})();
</script>
<!-- HN_CMS_PILOT_END -->'''

pos = text.lower().rfind('</body>')
if pos < 0:
    raise SystemExit('index.html has no </body>')
text = text[:pos] + '\n' + payload + '\n' + text[pos:]

for needle in ['HN_CMS_PILOT_START','HNCMSPilot','کپی برای CMS','قفل بیمار','hn-cms-packet','hn-cms-search']:
    if needle not in text:
        raise SystemExit('CMS pilot validation failed: ' + needle)
if text.count(START) != 1 or text.count(END) != 1:
    raise SystemExit('CMS pilot marker count invalid')
INDEX.write_text(text, encoding='utf-8')
print('CMS pilot installed:', INDEX.stat().st_size, 'bytes')

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

# Idempotent: remove an older placement layer, if present.
text = re.sub(re.escape(START) + r'.*?' + re.escape(END), '', text, flags=re.S)

placement = r'''<!-- HN_V216_NATIVE_PLACEMENT_START -->
<style id="hn-v216-native-placement-style">
/* v2.16.1 UI placement only: keep module logic untouched, remove floating launchers. */
#hnTwinV215Button,#hnv216-launch{display:none!important}
.hn-v216-native-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin:10px 0;padding:0}
.hn-v216-native-btn{appearance:none;border:1px solid #0f766e;border-radius:9px;background:#f0fdfa;color:#115e59;padding:8px 12px;font-family:"Peyda",Arial,Tahoma,sans-serif;font-weight:750;font-size:13px;line-height:1.5;cursor:pointer;box-shadow:none}
.hn-v216-native-btn:hover{background:#ccfbf1;border-color:#0d9488}
.hn-v216-native-btn:focus-visible{outline:2px solid #14b8a6;outline-offset:2px}
@media print{.hn-v216-native-row{display:none!important}}
</style>
<script id="hn-v216-native-placement-script">
(()=>{
  const byId=id=>document.getElementById(id);
  const modalSelector='#hnv216-modal,#hnTwinV215Modal';

  function anchorFor(ids){
    for(const id of ids){const el=byId(id);if(el)return el;}
    return null;
  }

  function textAnchor(words){
    const nodes=document.querySelectorAll('h1,h2,h3,h4,h5,legend,.section-title,.accordion-header,label');
    for(const el of nodes){
      if(el.closest(modalSelector))continue;
      const t=(el.textContent||'').trim().toLowerCase();
      if(words.some(w=>t.includes(w.toLowerCase())))return el;
    }
    return null;
  }

  function placementPoint(ids,words){
    const anchor=anchorFor(ids)||textAnchor(words);
    if(!anchor)return null;
    const group=anchor.closest('.form-group,.result-group,.option-group,.input-group');
    if(group&&group.parentElement)return {host:group.parentElement,after:group};
    const section=anchor.closest('section,.accordion-content,.organ-section,.module-section,.card');
    if(section)return {host:section,after:null};
    const host=anchor.parentElement||document.body;
    return {host,after:anchor};
  }

  function button(label,action,title){
    const b=document.createElement('button');
    b.type='button';b.className='hn-v216-native-btn';b.textContent=label;
    if(title)b.title=title;
    b.addEventListener('click',action);
    return b;
  }

  function openTwin(){
    const original=byId('hnTwinV215Button');
    if(original)original.click();
  }

  function openAddon(tab){
    const tabButton=document.querySelector('#hnv216-tabs button[data-tab="'+tab+'"]');
    if(tabButton)tabButton.click();
    const api=window.HNClinicalAddonsV216;
    if(api&&typeof api.open==='function')api.open();
    else {const original=byId('hnv216-launch');if(original)original.click();}
  }

  function ensureRow(id,point,buttons){
    if(!point||byId(id))return !!byId(id);
    const row=document.createElement('div');row.id=id;row.className='hn-v216-native-row';
    buttons.forEach(b=>row.appendChild(b));
    if(point.after&&point.after.parentElement===point.host)point.after.insertAdjacentElement('afterend',row);
    else point.host.appendChild(row);
    return true;
  }

  function place(){
    ensureRow('hn-v216-native-pregnancy',
      placementPoint(['pregnancy_result','fetus_result','crl_result','gs_result','fhr_result'],['بارداری','pregnancy','obstetric']),
      [
        button('👶👶 بارداری دوقلویی',openTwin,'Twin Pregnancy'),
        button('ابزارهای تکمیلی بارداری',()=>openAddon('preg'),'GA / RPOC / PAS')
      ]);

    ensureRow('hn-v216-native-renal',
      placementPoint(['kidney_parenchyma_result','kidney_size_result','kidney_stone_result','hydronephrosis_result'],['کلیه','kidney','renal']),
      [button('Renal Scar — اسکار کلیه',()=>openAddon('renal'),'Renal Scar')]);

    ensureRow('hn-v216-native-iud',
      placementPoint(['uterus_result','endometrium_result','adenomyosis_result','cervix_result'],['رحم','uterus','endometrium']),
      [button('IUD — موقعیت IUD',()=>openAddon('iud'),'IUD position / malposition')]);
  }

  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',place,{once:true});
  else place();
  const observer=new MutationObserver(()=>place());
  observer.observe(document.documentElement,{childList:true,subtree:true});
  document.addEventListener('click',()=>setTimeout(place,80),true);
})();
</script>
<!-- HN_V216_NATIVE_PLACEMENT_END -->'''

pos = text.lower().rfind('</body>')
if pos < 0:
    raise SystemExit('index.html has no </body>')
text = text[:pos] + '\n' + placement + '\n' + text[pos:]
INDEX.write_text(text, encoding='utf-8')

# Safety checks: one placement layer; existing clinical modules remain present.
out = INDEX.read_text(encoding='utf-8')
assert out.count(START) == 1 and out.count(END) == 1
for needle in required + ['hn-v216-native-pregnancy','hn-v216-native-renal','hn-v216-native-iud']:
    assert needle in out, needle
print('Native v2.16 placement applied:', INDEX.stat().st_size, 'bytes')

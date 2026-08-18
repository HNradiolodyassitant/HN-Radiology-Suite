#!/usr/bin/env python3
from pathlib import Path

p = Path('index.html')
text = p.read_text(encoding='utf-8')
old = "const observer=new MutationObserver(()=>injectInlineButtons());observer.observe(document.documentElement,{childList:true,subtree:true});"
new = """let cmsInjectTimer=null;
const observer=new MutationObserver(records=>{
 const onlyCmsMutations=records.length&&records.every(r=>{
   const t=r.target;
   return !!(t&&t.nodeType===1&&t.closest&&t.closest('#hn-cms-pilot-panel,#hn-cms-identity-badge,#hn-cms-toast'));
 });
 if(onlyCmsMutations)return;
 clearTimeout(cmsInjectTimer);
 cmsInjectTimer=setTimeout(injectInlineButtons,80);
});
observer.observe(document.documentElement,{childList:true,subtree:true});"""
if old not in text:
    if 'let cmsInjectTimer=null;' in text:
        print('CMS observer hotfix already present')
    else:
        raise SystemExit('Expected CMS observer anchor not found')
else:
    text = text.replace(old, new, 1)
    p.write_text(text, encoding='utf-8')
    print('CMS observer hotfix applied')

for marker in ['HN_CMS_PILOT_START','HNCMSPilot','let cmsInjectTimer=null;']:
    if marker not in p.read_text(encoding='utf-8'):
        raise SystemExit('Validation failed: ' + marker)

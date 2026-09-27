#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0927 语种页口径体检：EN/FR 页 description/title 是否含中文残留 + 是否旧IP口径"""
import re, os, json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)
FILES = ['en/index.html', 'fr/index.html', 'en/mili/index.html', 'fr/mili/index.html',
         'en/najie/index.html', 'fr/najie/index.html', 'en/aipunajie/index.html',
         'fr/aipunajie/index.html']

def meta(t, pat):
    m = re.search(pat, t, re.S)
    return m.group(1).strip() if m else ''

rows = []
for f in FILES:
    if not os.path.exists(f):
        print('%-24s MISSING' % f); continue
    t = open(f, encoding='utf-8').read()
    d = meta(t, r'<meta name="description" content="([^"]*)"')
    ti = meta(t, r'<title>(.*?)</title>')
    cjk_d = len(re.findall(r'[\u4e00-\u9fff]', d))
    cjk_t = len(re.findall(r'[\u4e00-\u9fff]', ti))
    old = ('IP Legal Protection' in t) or ('Protection Juridique PI' in t)
    rows.append(dict(file=f, desc_len=len(d), desc_cjk=cjk_d, title_cjk=cjk_t, old_ip_only=old))
    print('%-24s desc=%3d 中文字=%3d  title中文字=%2d  旧IP口径=%s' % (f, len(d), cjk_d, cjk_t, old))
    print('      title: %s' % ti[:110])
    print('      desc : %s' % d[:130])
json.dump(rows, open('site-inbox/i18n-audit-0927.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

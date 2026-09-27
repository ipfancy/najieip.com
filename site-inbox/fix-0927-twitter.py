#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0927 顺带补：4 个 EN/FR 页缺 twitter:title → 复用自身 og:title 值（不另编文案）"""
import os, re, sys, shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)
APPLY = '--apply' in sys.argv

FILES = ['en/mili/index.html', 'fr/mili/index.html',
         'en/aipunajie/index.html', 'fr/aipunajie/index.html']

ok = True
for f in FILES:
    t = open(f, encoding='utf-8').read()
    if 'twitter:title' in t:
        print('skip %s (已有 twitter:title)' % f); continue
    m = re.search(r'<meta property="og:title" content="([^"]*)">', t)
    if not m:
        print('❌ %s 无 og:title' % f); ok = False; continue
    val = m.group(1)
    anchor = '<meta name="twitter:card" content="summary_large_image">'
    if t.count(anchor) != 1:
        print('❌ %s twitter:card 锚点 %d 次' % (f, t.count(anchor))); ok = False; continue
    add = anchor + '\n<meta name="twitter:title" content="%s">' % val
    t = t.replace(anchor, add, 1)
    # 断言 twitter:title 值与 og:title 一致
    v2 = re.search(r'<meta name="twitter:title" content="([^"]*)">', t).group(1)
    assert v2 == val, f
    if APPLY:
        shutil.copy2(f, f + '.bak-20260927b')
        open(f, 'w', encoding='utf-8').write(t)
        print('✅ %s 补 twitter:title = %s' % (f, val[:60]))
    else:
        print('… %s 将补 twitter:title = %s [dry-run]' % (f, val[:60]))
print('OK=%s APPLY=%s' % (ok, APPLY))

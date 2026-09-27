#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0927 修复后终验：JSON-LD 解析 + og/twitter 完整 + 中文残留 + 双房屋 + hreflang + div 配平"""
import os, re, json, html

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)
FILES = ['mili/index.html', 'en/mili/index.html', 'fr/mili/index.html',
         'en/aipunajie/index.html', 'fr/aipunajie/index.html', 'llms.txt']
fails = []

for f in FILES:
    t = open(f, encoding='utf-8').read()
    print('=== %s (%d B) ===' % (f, len(t.encode('utf-8'))))
    if f.endswith('llms.txt'):
        print('   facts.html=%d  llms 行数=%d' % (t.count('facts.html'), t.count('\n') + 1))
        continue
    # JSON-LD
    lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)
    print('   ld+json 块=%d' % len(lds))
    for i, blk in enumerate(lds):
        try:
            o = json.loads(blk)
            print('     [%d] OK @type=%s name=%s' % (i, o.get('@type'), o.get('name')))
        except Exception as e:
            print('     [%d] ❌ JSON 非法: %s' % (i, e))
            fails.append('%s ld[%d] invalid' % (f, i))
    # og/twitter
    for tag in ['og:title', 'og:description', 'og:image', 'og:url',
                'twitter:card', 'twitter:title']:
        m = re.search(r'<meta (?:property|name)="%s" content="([^"]*)"' % tag, t)
        v = m.group(1) if m else None
        status = 'OK' if v else 'MISSING'
        if not v:
            fails.append('%s %s missing' % (f, tag))
        print('     %-18s %s  %s' % (tag, status, (v[:80] + '…') if v and len(v) > 80 else (v or '')))
    # 中文残留（仅 EN/FR 页的 meta 字段）
    if f.startswith(('en/', 'fr/')):
        cjk_meta = 0
        for tag in ['description', 'og:description', 'og:title', 'twitter:title']:
            m = re.search(r'<meta (?:property|name)="(?:og:)?%s" content="([^"]*)"' % tag, t)
            if m:
                cjk_meta += len(re.findall(r'[\u4e00-\u9fff]', m.group(1)))
        print('     meta 中文字=%d' % cjk_meta)
        if cjk_meta:
            fails.append('%s meta CJK=%d' % (f, cjk_meta))
    # hreflang
    hl = re.findall(r'hreflang="([^"]+)"', t)
    print('     hreflang=%s' % (hl if hl else 'NONE'))
    # 双房屋 + div 配平
    style = ('<style' in t) or (('/style.css' in t) and os.path.exists('style.css'))
    opens = len(re.findall(r'<div\b', t)); closes = t.count('</div>')
    schema = t.count('https://schema.org'); bad = t.count('https://***')
    print('     style=%s  div开=%d 闭=%d  diff=%d  schema.org=%d  "***"=%d' %
          (style, opens, closes, opens - closes, schema, bad))
    if not style:
        fails.append('%s NO-STYLE' % f)
    if schema == 0 or bad:
        fails.append('%s schema.org=%d bad=%d' % (f, schema, bad))

print('\n================ 终验结论 ================')
print('FAILS: %d' % len(fails))
for x in fails:
    print('  ❌', x)
if not fails:
    print('  全部 PASS')

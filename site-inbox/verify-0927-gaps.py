#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0927 缺口复核：对 44 non_article_page + 1 stub 逐条判定是否真缺口
判据 (a) 文件名是否出现在主索引全文 (b) 文件是否有 JSON-LD/日期/og:image (c) 首次入库日 (d) 是否被 sitemap 收录
"""
import os, re, json, subprocess

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)
main = open('blog/index.html', encoding='utf-8').read()
sm = open('sitemap.xml', encoding='utf-8').read()
rows = json.load(open('site-inbox/missing-cards-0927.json', encoding='utf-8'))

real_gaps, legacy, stub = [], [], []
for r in rows:
    f = r['file']
    fname = f.rsplit('/', 1)[-1]
    in_main = fname in main
    in_sm = fname in sm
    body = open(f, encoding='utf-8').read()
    ld = body.count('application/ld+json')
    ogi = 'og:image' in body
    h1 = body.count('<h1')
    size = len(body.encode('utf-8'))
    try:
        d = subprocess.run(['git', 'log', '--diff-filter=A', '--date=short',
                            '--format=%ad', '--', f], capture_output=True, text=True).stdout.split()
        first = d[-1] if d else '?'
    except Exception:
        first = '?'
    rec = dict(file=f, in_main=in_main, in_sitemap=in_sm, ld=ld, og_image=ogi,
               h1=h1, size=size, first_commit=first, reason=r['reason'])
    if size < 1500 or 'http-equiv="refresh"' in body:
        stub.append(rec)
    elif in_main:
        legacy.append(rec)          # 已在主索引，扫描误报
    else:
        real_gaps.append(rec)

print('已在主索引（误报）: %d' % len(legacy))
print('stub/跳转壳      : %d' % len(stub))
for r in stub:
    print('   ', r['file'], r['size'], 'B', r['first_commit'])
print('\n=== 真缺口 %d ===' % len(real_gaps))
for r in real_gaps:
    print('  %-72s ld=%d og:image=%s h1=%d %6dB 首次=%s sitemap=%s' %
          (r['file'], r['ld'], r['og_image'], r['h1'], r['size'], r['first_commit'], r['in_sitemap']))
json.dump(dict(real_gaps=real_gaps, legacy=legacy, stub=stub),
          open('site-inbox/gap-verify-0927.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

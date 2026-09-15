#!/usr/bin/env python3
"""SiteOps 0915 补卡 v3（幂等）：把 2026-09-01~09-14 缺失的 15 张文章卡片按日期降序插回主 blog/index.html。

演进：
 v1 按偏移插入，插入后未更新既有卡片偏移 → 落点撕开标签（div +29/+30）。
 v2 整体重建容器区，但卡片间分隔符不统一（'\n  ' vs '\n\n  '）→ 重建不等于原文件，断言拦下。
 v3 每次插入后重新扫描当前字符串取卡片位置（无过期偏移）；插入串 = 卡块 + '\n  '，
    落在目标卡 `<div class="article-card">` 之前 —— 目标卡原有的缩进分隔符天然成为新卡前缀。
用法：python3 gen-0915-index-cards-v3.py [--apply]
"""
import re
import sys
import json

IDX = 'blog/index.html'
APPLY = '--apply' in sys.argv
CARD = '<div class="article-card">'

MISSING = json.load(open('site-inbox/missing-cards-0915.json', encoding='utf-8'))
BRAND_LABEL = {'mili': '觅理律师事务所', 'najie': '纳杰知识产权', 'aipunajie': '爱普纳杰专利代理'}


def clean(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or '')).strip()


def excerpt_for(slug, path):
    for m in MISSING:
        if m['slug'] == slug and m['desc']:
            return m['desc']
    t = open(path.lstrip('/'), encoding='utf-8').read()
    for pat in (r'<meta property="og:description" content="([^"]*)"',
                r'<meta name="description" content="([^"]*)"'):
        m = re.search(pat, t)
        if m and len(clean(m.group(1))) >= 20:
            return clean(m.group(1))[:400]
    for m in re.finditer(r'<p[^>]*>(.*?)</p>', t, flags=re.S):
        c = clean(m.group(1))
        if len(c) >= 60 and '版权' not in c[:10]:
            return c[:400]
    return ''


def markers(t):
    """[(pos, date_or_None)] for every card, positions fresh."""
    out = []
    for m in re.finditer(re.escape(CARD), t):
        w = t[m.start():m.start() + 900]
        d = re.search(r'(\d{4}-\d{2}-\d{2})', w)
        out.append((m.start(), d.group(1) if d else None))
    return out


t = open(IDX, encoding='utf-8').read()
base_cards = len(markers(t))
print('existing cards:', base_cards)

todo = []
for m in MISSING:
    path = m['path']
    if f'href="{path}"' in t:
        print('SKIP (present):', path)
        continue
    tags = ''.join(f'<span class="tag">{k}</span>'
                   for k in [x.strip() for x in (m['kw'] or '').split(',') if x.strip()][:3])
    ex = excerpt_for(m['slug'], path)
    assert len(ex) >= 30, f'excerpt too short: {path}'
    blk = ('<div class="article-card">\n'
           f'    <h2><a href="{path}">{m["h1"] or m["ogtitle"]}</a></h2>\n'
           f'    <div class="meta">{tags} {m["date"]} · {BRAND_LABEL[m["brand"]]}</div>\n'
           f'    <p>{ex}</p>\n'
           '  </div>')
    todo.append((m['date'], path, blk))
print('to insert:', len(todo))
if not APPLY:
    for d, p, _ in todo:
        print('  ', d, p)
    print('[DRY RUN]')
    sys.exit(0)

for date, path, blk in sorted(todo, key=lambda x: x[0], reverse=True):
    ms = markers(t)
    pos = None
    for p, d in ms:
        if d and d < date:
            pos = p
            break
    if pos is None:  # older than every dated card -> first undated card
        for p, d in ms:
            if d is None:
                pos = p
                break
    assert pos is not None, f'no anchor for {path}'
    t = t[:pos] + blk + '\n  ' + t[pos:]
    print('inserted', date, path, 'at', pos)

open(IDX, 'w', encoding='utf-8').write(t)

print('\n=== VERIFY ===')
t2 = open(IDX, encoding='utf-8').read()
print('cards:', t2.count(CARD), 'expected', base_cards + len(todo))
print('<div:', t2.count('<div'), '</div>:', t2.count('</div>'),
      'balanced:', t2.count('<div') == t2.count('</div>'))
for _, p, _ in todo:
    c = t2.count(f'href="{p}"')
    print(('OK ' if c == 1 else 'DUP'), f'x{c}', p)
print('stray **:', t2.count('**'), '| corrupt schema:', t2.count('https://***'))
bad = [b[:60] for b in re.findall(r'<div class="article-card">(.*?)\n  </div>', t2, flags=re.S)
       if not ('<h2><a href=' in b and '<div class="meta">' in b and '<p>' in b)]
print('malformed cards:', len(bad), bad[:3])
ms = markers(t2)
ds = [d for _, d in ms if d]
print('dated cards:', len(ds), 'monotonic desc:', all(a >= b for a, b in zip(ds, ds[1:])),
      '| range', ds[0], '→', ds[-1])

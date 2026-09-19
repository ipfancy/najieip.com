#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-09-19 主索引缺口采集（v5：品牌索引 body 卡 vs 主索引 body 卡，href 精确比对）
输出 site-inbox/missing-cards-20260919.json
"""
import re, os, json, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(ROOT, 'blog/index.html')
BRANDS = [
    ('mili', os.path.join(ROOT, 'mili/blog/index.html')),
    ('najie', os.path.join(ROOT, 'najie/blog/index.html')),
]

CARD_RE = re.compile(
    r'<div class="article-card">\s*<h2><a href="([^"]+)">(.*?)</a></h2>\s*'
    r'<div class="meta">(.*?)</div>\s*<p>(.*?)</p>\s*</div>', re.S)


def body(t):
    i = t.find('<body')
    return t[i:] if i >= 0 else t


def cards(t):
    return [(m.group(1), m.group(2).strip(), m.group(3).strip(), m.group(4).strip())
            for m in CARD_RE.finditer(body(t))]


def norm(href, base='/'):
    h = href.strip()
    if h.startswith('http'):
        h = '/' + h.split('//', 1)[1].split('/', 1)[1] if '//' in h else h
    if h.startswith('./'):
        h = base.rstrip('/') + '/' + h[2:]
    elif not h.startswith('/'):
        h = base.rstrip('/') + '/' + h
    return h


def main():
    main_t = open(MAIN, encoding='utf-8').read()
    main_cards = cards(main_t)
    main_hrefs = set(norm(c[0]) for c in main_cards)
    print('MAIN cards =', len(main_cards), 'unique hrefs =', len(main_hrefs))

    gaps = []
    skipped = []
    for brand, path in BRANDS:
        base = '/' + brand + '/blog'
        t = open(path, encoding='utf-8').read()
        cs = cards(t)
        print('BRAND', brand, 'cards =', len(cs))
        for href, title, meta, desc in cs:
            n = norm(href, base)
            if n in main_hrefs:
                continue
            fpath = os.path.join(ROOT, n.lstrip('/'))
            if not os.path.isfile(fpath):
                skipped.append({'brand': brand, 'href': n, 'reason': 'file_not_found'})
                continue
            size = os.path.getsize(fpath)
            ft = open(fpath, encoding='utf-8', errors='replace').read()
            if size < 1500 or 'http-equiv="refresh"' in ft or ft.count('<p') < 2:
                skipped.append({'brand': brand, 'href': n, 'reason': 'stub', 'size': size})
                continue
            m = re.search(r'(\d{4}-\d{2}-\d{2})', meta)
            date = m.group(1) if m else ''
            tags = re.findall(r'<span class="tag">([^<]*)</span>', meta)
            gaps.append({'brand': brand, 'href': n, 'title': title,
                         'tags': tags, 'date': date, 'desc': desc, 'size': size})
            main_hrefs.add(n)

    gaps.sort(key=lambda x: x['date'], reverse=True)
    out = os.path.join(ROOT, 'site-inbox/missing-cards-20260919.json')
    json.dump({'gaps': gaps, 'skipped': skipped}, open(out, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print('GAPS =', len(gaps))
    for g in gaps:
        print('  ', g['date'], g['brand'], g['href'], g['size'])
    print('SKIPPED =', len(skipped))
    for s in skipped:
        print('  ', s)
    print('wrote', out)


main()

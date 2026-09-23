#!/usr/bin/env python3
# 0923 gather: brand index href (normalized) vs main index -> real gaps
import os, re, json, subprocess

ROOT = os.path.expanduser('~/wiki/najieip-verify')
os.chdir(ROOT)

def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()

MAIN = read('blog/index.html')
main_hrefs = set(re.findall(r'<h2><a href="([^"]+)"', MAIN))
print("main index cards:", len(main_hrefs))

brands = ['mili', 'najie', 'aipunajie']
rows = []
for b in brands:
    ip = f'{b}/blog/index.html'
    t = read(ip)
    cards = re.findall(r'<div class="article-card">(.*?)</div>\s*(?=<div class="article-card">|<div class="container"|$)', t, re.S)
    # simpler: split by article-card marker
    blocks = t.split('<div class="article-card">')[1:]
    print(f"\n{b}: raw card blocks {len(blocks)}")
    for blk in blocks:
        h = re.search(r'<h2><a href="([^"]+)"[^>]*>(.*?)</a></h2>', blk, re.S)
        if not h:
            continue
        href, title = h.group(1), re.sub(r'<[^>]+>', '', h.group(2)).strip()
        p = re.search(r'<p>(.*?)</p>', blk, re.S)
        desc = re.sub(r'<[^>]+>', '', p.group(1)).strip() if p else ''
        meta = re.search(r'<div class="meta">(.*?)</div>', blk, re.S)
        meta = re.sub(r'<[^>]+>', ' ', meta.group(1)).strip() if meta else ''
        date = re.search(r'(\d{4}-\d{2}-\d{2})', meta)
        date = date.group(1) if date else ''
        tags = re.findall(r'<span class="tag">([^<]*)</span>', blk)
        # normalize relative href
        if href.startswith('./'):
            norm = f'/{b}/blog/{href[2:]}'
        elif href.startswith('/'):
            norm = href
        else:
            norm = f'/{b}/blog/{href}'
        rows.append(dict(brand=b, href=href, norm=norm, title=title, desc=desc,
                         date=date, tags=tags, raw=blk))

json.dump(rows, open('site-inbox/gather-0923-all.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print("total brand cards:", len(rows))

# gaps relative to main
gap = [r for r in rows if r['norm'] not in main_hrefs]
print("\n=== GAPS (brand card not in main index) ===", len(gap))
for r in gap:
    f = r['norm'].lstrip('/')
    size = os.path.getsize(f) if os.path.exists(f) else -1
    t = read(f) if os.path.exists(f) else ''
    stub = size >= 0 and (size < 1500 or 'http-equiv="refresh"' in t)
    print(f"  {'STUB' if stub else 'REAL'} size={size} {r['norm']} | {r['date']} | {r['title'][:34]}")

# also show cards in main that are NOT in any brand index (info)
brand_norms = set(r['norm'] for r in rows)
only_main = [h for h in main_hrefs if h not in brand_norms]
print("\nmain-only cards:", len(only_main))
for h in sorted(only_main)[:10]:
    print("   ", h)

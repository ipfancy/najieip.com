#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 0925 每日巡检: 卡片计数 + 品牌/主索引缺口 + 畸形页四联判据 + articles.json 统计"""
import json, os, re, sys, subprocess

ROOT = os.path.expanduser('~/wiki/najieip-verify')
os.chdir(ROOT)

def read(p):
    with open(p, encoding='utf-8', errors='replace') as f:
        return f.read()

MAIN = read('blog/index.html')
BRANDS = {'mili': read('mili/blog/index.html'), 'najie': read('najie/blog/index.html')}

print('=== 卡片计数 ===')
print('main:', MAIN.count('class="article-card"'))
for b, t in BRANDS.items():
    print(b, ':', t.count('class="article-card"'))

# --- 缺口扫描: 品牌索引 href 归一 vs 主索引 ---
print('\n=== 缺口扫描 (href 归一) ===')
def cards(t, base):
    out = []
    for m in re.finditer(r'<h2><a href="([^"]+)"', t):
        href = m.group(1)
        if href.startswith('./'):
            href = base + href[1:]
        elif not href.startswith('/'):
            href = base + '/' + href
        out.append(href)
    return out

brand_cards = {}
for b, t in BRANDS.items():
    brand_cards[b] = cards(t, '/%s/blog' % b)
    print(b, 'cards:', len(brand_cards[b]))

gaps = []
for b, lst in brand_cards.items():
    for h in lst:
        if h not in MAIN:
            gaps.append((b, h))

SKIP_PAT = re.compile(r'(cnptes|architecture-diagram)')
real_gaps = []
for b, h in gaps:
    if SKIP_PAT.search(h):
        print('  skip(架构/内嵌页):', h)
        continue
    real_gaps.append((b, h))
print('候选缺口(未做stub过滤前):', len(real_gaps))
for b, h in real_gaps:
    print('  GAP', b, h)

# --- 畸形页四联判据 ---
print('\n=== 畸形页四联判据 ===')
def house_ok(t):
    inline = '<style>' in t
    ext = ('/style.css' in t) and os.path.exists('style.css')
    return inline or ext

def judge(path):
    t = read(path)
    h1 = len(re.findall(r'<h1', t))
    ld = len(re.findall(r'application/ld\+json', t))
    ogi = 'og:image' in t
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = m.group(1) if m else ''
    ti = re.search(r'<title>(.*?)</title>', t, re.S)
    title = ti.group(1).strip() if ti else ''
    bad = (h1 == 0 and ld == 0 and not ogi and desc and desc.strip() in title)
    return dict(size=os.path.getsize(path), h1=h1, ld=ld, og_img=ogi,
                style=house_ok(t), desc_len=len(desc), bad=bad,
                desc_repeat=(desc.strip() in title and bool(desc)))

# articles.json 首页 top6
with open('articles.json', encoding='utf-8') as f:
    d = json.load(f)
arts = d if isinstance(d, list) else d.get('articles', [])
print('articles.json 条目:', len(arts))
arts_sorted = sorted(arts, key=lambda a: a.get('date', ''), reverse=True)
print('\n--- 首页 slice(0,6) 房屋四件 ---')
for i, a in enumerate(arts_sorted[:6], 1):
    p = a.get('url') or a.get('path') or ''
    fp = p.lstrip('/')
    if not os.path.exists(fp):
        print('  %d MISSING-FILE %s' % (i, p)); continue
    r = judge(fp)
    print('  %d %s | style=%s h1=%d ld=%d og:image=%s desc=%d bad=%s' % (
        i, p, r['style'], r['h1'], r['ld'], r['og_img'], r['desc_len'], r['bad']))

print('\n--- 近 6 天新增文章页房屋四件 ---')
try:
    files = subprocess.run(['git', 'log', 'origin/main', '--diff-filter=A', '--name-only',
                            '--since=6 days ago', '--pretty=format:'],
                           capture_output=True, text=True).stdout.split('\n')
except Exception as e:
    files = []
seen = set()
for f in files:
    f = f.strip()
    if not f.endswith('.html') or 'index' in f or not f.startswith(('blog/', 'mili/blog/', 'najie/blog/')):
        continue
    if f in seen or not os.path.exists(f):
        continue
    seen.add(f)
    r = judge(f)
    flag = 'BAD' if r['bad'] else ('warn-desc-repeat' if r['desc_repeat'] else 'ok')
    print('  %-62s %6dB h1=%d ld=%d og=%s style=%s [%s]' % (
        f, r['size'], r['h1'], r['ld'], r['og_img'], r['style'], flag))

#!/usr/bin/env python3
# SiteOps 2026-09-23 诊断：新文主索引覆盖 + 房屋样式四件 + sitemap
import os, re, json, subprocess, sys

ROOT = os.path.expanduser('~/wiki/najieip-verify')
os.chdir(ROOT)

def read(p):
    with open(p, encoding='utf-8') as f:
        return f.read()

# ---- 1. 今日/昨日新增文章页（从 git 取最近提交新增的 html） ----
out = subprocess.run(['git','log','origin/main','--name-status','--diff-filter=A',
                      '--since=2026-09-22 00:00','--pretty=format:%h'],
                     capture_output=True, text=True).stdout
new_pages = []
for line in out.splitlines():
    if line.startswith('A\t') and line.endswith('.html'):
        p = line[2:]
        if p.startswith(('blog/','mili/blog/','najie/blog/','en/','fr/')) and 'index.html' not in p:
            new_pages.append(p)
new_pages = sorted(set(new_pages))
print("=== NEW PAGES (since 09-22) ===")
for p in new_pages:
    print("  ", p, os.path.getsize(p) if os.path.exists(p) else "MISSING")

# ---- 2. 房屋样式四件 ----
print("\n=== HOUSE STYLE 4-PIECE ===")
for p in new_pages:
    if not os.path.exists(p):
        continue
    t = read(p)
    has_inline = '<style>' in t
    has_ext = bool(re.search(r'<link[^>]+href="[^"]*style\.css', t)) and os.path.exists('style.css')
    h1 = len(re.findall(r'<h1[^>]*>', t))
    ld = t.count('application/ld+json')
    ogimg = 'og:image' in t
    desc = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = desc.group(1) if desc else ''
    title = re.search(r'<title>(.*?)</title>', t)
    title = title.group(1) if title else ''
    broken = not (has_inline or has_ext)
    status = 'OK'
    if broken or h1 != 1 or ld < 2 or not ogimg or len(desc) <= 80:
        status = 'SUSPECT'
    print(f"  [{status}] {p} style={'inline' if has_inline else ('ext' if has_ext else 'NONE')} h1={h1} ld={ld} og:img={ogimg} desc={len(desc)}B h2={len(re.findall(r'<h2',t))} `**`={t.count('**')}")
    if status == 'SUSPECT':
        print(f"      title={title[:60]}")
        print(f"      desc={desc[:80]}")

# ---- 3. 主索引覆盖 ----
print("\n=== MAIN INDEX COVERAGE ===")
main = read('blog/index.html')
for p in new_pages:
    if 'blog/' not in p:
        continue
    slug = os.path.basename(p)[:-5]
    hit = main.count(slug)
    print(f"  main-index refs {hit}: {p}")

# ---- 4. 品牌索引覆盖 ----
print("\n=== BRAND INDEX COUNTS ===")
for brand in ['mili','najie','aipunajie']:
    ip = f'{brand}/blog/index.html'
    if os.path.exists(ip):
        t = read(ip)
        print(f"  {ip}: cards={t.count('article-card')} blogPost={t.count('\"blogPost\"')} `**`={t.count('**')}")

# ---- 5. articles.json 前 6 条存在性（首页曝光位） ----
print("\n=== articles.json top6 exposure ===")
d = json.load(open('articles.json', encoding='utf-8'))
arr = d if isinstance(d, list) else d.get('articles', d)
print("  total entries:", len(arr))
for i, x in enumerate(arr[:6]):
    u = x.get('url') or x.get('path') or ''
    local = u.lstrip('/')
    ok = os.path.exists(local)
    print(f"  {i+1}. {'OK ' if ok else 'MISSING'} {u} | {(x.get('title') or '')[:35]}")

# ---- 6. articles.json 违例统计 ----
bad = []
for x in arr:
    u = (x.get('url') or x.get('path') or '').lstrip('/')
    if not u or not os.path.exists(u):
        bad.append(u)
print(f"\n=== articles.json violations: {len(bad)}/{len(arr)} ===")
for b in bad[:15]:
    print("   !", b)

# ---- 7. sitemap ----
print("\n=== SITEMAP ===")
sm = read('sitemap.xml')
locs = re.findall(r'<loc>(.*?)</loc>', sm)
blocks = re.findall(r'<url>(.*?)</url>', sm, re.S)
nolast = [b for b in blocks if '<lastmod>' not in b]
print(f"  locs={len(locs)} no-lastmod={len(nolast)}")
for p in new_pages:
    url = '/' + p if not p.startswith('/') else p
    found = any(url in l for l in locs)
    print(f"  sitemap {'HIT ' if found else 'MISS'} {url}")

# ---- 8. mili 系列主索引覆盖 ----
print("\n=== MILI SERIES in main index ===")
series = [p for p in new_pages if 'caichan-shouhu' in p]
for p in series:
    slug = os.path.basename(p)[:-5]
    print(f"  main refs {main.count(slug)} | mili refs {read('mili/blog/index.html').count(slug)}: {slug}")

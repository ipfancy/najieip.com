#!/usr/bin/env python3
# 0923 线上验证：字节一致 + 卡片在线 + sitemap loc + 结构
import os, re, subprocess, hashlib, time, urllib.request

os.chdir(os.path.expanduser('~/wiki/najieip-verify'))
TS = int(time.time())

def fetch(url):
    req = urllib.request.Request(url + ('&' if '?' in url else '?') + f'cb={TS}',
                                 headers={'User-Agent': 'SiteOps/1.0'})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()

def local(p):
    return open(p, 'rb').read()

print("=== A. BYTE CONSISTENCY (live vs local) ===")
for url, path in [('https://najieip.com/blog/', 'blog/index.html'),
                  ('https://najieip.com/mili/blog/', 'mili/blog/index.html'),
                  ('https://najieip.com/najie/blog/', 'najie/blog/index.html'),
                  ('https://najieip.com/sitemap.xml', 'sitemap.xml')]:
    live = fetch(url)
    loc = local(path)
    same = live == loc
    print(f"  {'IDENTICAL' if same else 'DIFF'}  {path}: live={len(live)}B local={len(loc)}B Δ={len(live)-len(loc)}")
    if not same and path.endswith('index.html'):
        import difflib
        a = live.decode('utf-8', 'ignore').splitlines()
        b = loc.decode('utf-8', 'ignore').splitlines()
        d = [l for l in difflib.unified_diff(b, a, lineterm='', n=0)][:12]
        print("     diff sample:", d)

print("\n=== B. NEW CARDS LIVE (blog index) ===")
live_main = fetch('https://najieip.com/blog/').decode('utf-8', 'ignore')
targets = ['/najie/blog/shangbiao-bohuifushen-2026.html',
           '/najie/blog/zhiming-shangbiao-pinpai-pingjia-2026.html'] + \
          [f'/mili/blog/20260922-caichan-shouhu-0{i}.html' for i in range(1, 8)]
for t in targets:
    print(f"  {'HIT ' if t in live_main else 'MISS'} {t}")
print("  live article-card count:", live_main.count('<div class="article-card">'))

print("\n=== C. SITEMAP LOCS LIVE ===")
live_sm = fetch('https://najieip.com/sitemap.xml').decode('utf-8', 'ignore')
print("  live locs:", live_sm.count('<loc>'))
for t in targets:
    print(f"  {'HIT ' if t in live_sm else 'MISS'} {t}")

print("\n=== D. ARTICLE PAGE SEO FIELDS (live) ===")
for u in ['https://najieip.com/mili/blog/20260922-caichan-shouhu-01.html',
          'https://najieip.com/najie/blog/shangbiao-bohuifushen-2026.html',
          'https://najieip.com/najie/blog/20260923-ai-opinion-article7-rights-holder-manual.html']:
    t = fetch(u).decode('utf-8', 'ignore')
    print(f"  {u.split('/')[-1]}: og:url={'og:url' in t} canonical={'canonical' in t} ld={t.count('application/ld+json')} schema_ok={t.count('https://schema.org')} star_leak={t.count('**')} h1={len(re.findall(r'<h1', t))}")

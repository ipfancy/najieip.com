#!/usr/bin/env python3
import os, re, subprocess
os.chdir(os.path.expanduser('~/wiki/najieip-verify'))
def read(p):
    return open(p, encoding='utf-8').read()

print("=== MAIN INDEX top 26 cards (date order) ===")
t = read('blog/index.html')
for m in list(re.finditer(r'<h2><a href="([^"]+)"[^>]*>(.*?)</a></h2>\s*<div class="meta">(.*?)</div>', t, re.S))[:26]:
    href = m.group(1)
    meta = re.sub(r'<[^>]+>', ' ', m.group(3))
    d = re.search(r'(\d{4}-\d{2}-\d{2})', meta)
    print(f"  {d.group(1) if d else '????-??-??'}  {href}")

print("\n=== SEPARATOR AUDIT (main) ===")
seps = re.findall(r'</div>(\s*)<div class="article-card">', t)
from collections import Counter
print(Counter(repr(s) for s in seps).most_common(5))
print("sep before first card:", repr(t[max(0,t.find('<div class=\"article-card\">')-8):t.find('<div class=\"article-card\">')]))

print("\n=== cnptes page inspect ===")
f = 'najie/blog/cnptes-three-layer-architecture-diagram.html'
c = read(f)
print("size", len(c))
print("title:", (re.search(r'<title>(.*?)</title>', c) or ['',''])[1][:80] if re.search(r'<title>(.*?)</title>', c) else '')
print("h1:", len(re.findall(r'<h1', c)), "h2:", len(re.findall(r'<h2', c)), "ld:", c.count('application/ld+json'))
print("in main index:", c.count(f) if False else ('/najie/blog/cnptes-three-layer-architecture-diagram.html' in read('blog/index.html')))
print("in sitemap:", 'cnptes-three-layer-architecture-diagram' in read('sitemap.xml'))
print("has style:", '<style>' in c, "| style.css link:", 'style.css' in c)
print("og:image:", 'og:image' in c)
print("first 400:", c[:400].replace('\n',' '))

print("\n=== sitemap tail & format ===")
sm = read('sitemap.xml')
print("locs:", len(re.findall(r'<loc>', sm)))
print(sm[:420])
print("...last 3 url blocks...")
blks = re.findall(r'<url>.*?</url>', sm, re.S)
for b in blks[-3:]:
    print(b.replace('\n',' '))

print("\n=== mili series git add dates ===")
for i in range(1,8):
    p = f'mili/blog/20260922-caichan-shouhu-0{i}.html'
    r = subprocess.run(['git','log','--diff-filter=A','--date=short','--pretty=format:%ad','--',''.join([]) or p], capture_output=True, text=True).stdout.splitlines()
    print(" ", p, r[-1] if r else 'N/A')

print("\n=== najie brand new pages git add dates ===")
for p in ['najie/blog/shangbiao-bohuifushen-2026.html','najie/blog/zhiming-shangbiao-pinpai-pingjia-2026.html']:
    r = subprocess.run(['git','log','--diff-filter=A','--date=short','--pretty=format:%ad','--',p], capture_output=True, text=True).stdout.splitlines()
    print(" ", p, r[-1] if r else 'N/A')

print("\n=== articles.json indent/base check ===")
raw = subprocess.run(['git','show','origin/main:articles.json'], capture_output=True, text=True).stdout
print("origin len", len(raw), "| local len", len(read('articles.json')), "| identical:", raw == read('articles.json'))
print("first 200:", raw[:200].replace('\n','\\n'))

#!/usr/bin/env python3
"""aipunajie 索引缺口（href 形如 ./x.html，不走 h2 包裹）"""
import re, os
os.chdir(os.path.expanduser("~/wiki/najieip-verify"))
main = open("blog/index.html", encoding="utf-8").read()
t = open("aipunajie/blog/index.html", encoding="utf-8").read()
hs = re.findall(r'<a href="(\./[^"]+\.html)"', t)
urls = []
for h in hs:
    p = "/aipunajie/blog/" + h[2:]
    if p not in urls: urls.append(p)
print("aipunajie 卡 URL:", len(urls))
gap = []
for p in urls:
    f = p.lstrip("/")
    if not os.path.exists(f):
        print("  DEAD", p); continue
    sz = os.path.getsize(f)
    body = open(f, encoding="utf-8", errors="replace").read()
    if sz < 1500 or 'http-equiv="refresh"' in body:
        continue
    if p in main: continue
    slug = os.path.basename(p)[:-5]
    if re.search(r'href="[^"]*' + re.escape(slug), main): continue
    gap.append(p)
print("真缺口:", len(gap))
for g in gap: print("  GAP", g)

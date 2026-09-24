#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0924 recon: style.css 规则 + mili og:image 取值 + 两索引卡日期序列"""
import os, re, collections

REPO = os.path.expanduser("~/wiki/najieip-verify")


def rd(p):
    with open(os.path.join(REPO, p), "r", encoding="utf-8", errors="replace") as f:
        return f.read()


print("=== style.css 相关规则 ===")
css = rd("style.css")
for kw in ["article h2", "h2 {", "h1 {", ".article-card", "article p"]:
    for m in re.finditer(re.escape(kw), css):
        s = css[m.start():m.start() + 200]
        print("  [%s] %s" % (kw, s.split("}")[0].replace("\n", " ")[:180]))
        break

print("\n=== mili/blog og:image 取值分布 ===")
c = collections.Counter()
for fn in os.listdir(os.path.join(REPO, "mili/blog")):
    if fn.endswith(".html") and fn != "index.html":
        t = open(os.path.join(REPO, "mili/blog", fn), encoding="utf-8", errors="replace").read()
        m = re.search(r'og:image" content="([^"]+)"', t)
        if m:
            c[m.group(1)] += 1
for u, n in c.most_common(8):
    print("  %dx %s" % (n, u))

print("\n=== mili/blog/index.html 卡片日期序列（前 16）===")
t = rd("mili/blog/index.html")
b = t[t.find('<div class="container"'):]
print("  total article-card:", b.count('<div class="article-card">'))
for m in list(re.finditer(r'<div class="article-card">', b))[:16]:
    seg = b[m.start():m.start() + 1200]
    d = re.search(r"(\d{4}-\d{2}-\d{2})", seg)
    h = re.search(r'<h2><a href="([^"]+)"', seg)
    print("  off=%d %s %s" % (m.start(), d.group(1) if d else "NODATE", h.group(1) if h else ""))

print("\n=== blog/index.html 卡片日期序列（前 16）===")
t2 = rd("blog/index.html")
b2 = t2[t2.find('<div class="container"'):]
print("  total article-card:", b2.count('<div class="article-card">'))
for m in list(re.finditer(r'<div class="article-card">', b2))[:16]:
    seg = b2[m.start():m.start() + 1600]
    d = re.search(r"(\d{4}-\d{2}-\d{2})", seg)
    h = re.search(r'<h2><a href="([^"]+)"', seg)
    print("  off=%d %s %s" % (m.start(), d.group(1) if d else "NODATE", h.group(1) if h else ""))

print("\n=== mili 索引卡：财产守护系列之前的分隔符形态 ===")
i = b.find('<div class="article-card">')
print(repr(b[max(0, i - 260):i + 60]))

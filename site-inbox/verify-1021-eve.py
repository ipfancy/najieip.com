#!/usr/bin/env python3
"""SiteOps 1021晚 结构终验"""
import re, subprocess
from collections import Counter

t = open("blog/index.html", encoding="utf-8").read()
base = subprocess.run(["git", "show", "origin/main:blog/index.html"],
                      capture_output=True, text=True).stdout

def analyze(s):
    c = Counter(); i = 0; d = 0; bad = 0
    while True:
        n = re.search(r'<div[ >]|</div>', s[i:])
        if not n: break
        j = i + n.start()
        if n.group().startswith('<div'):
            if s[j:j+28].startswith('<div class="article-card">'):
                c[d] += 1
            d += 1
        else:
            d -= 1
            if d < 0: bad += 1
        i = j + len(n.group())
    return c, d, bad

print("cards:", t.count('<div class="article-card">'), "(base", base.count('<div class="article-card">'), ")")
print("BASE depth:", dict(analyze(base)[0]), "final", analyze(base)[1], "bad", analyze(base)[2])
print("NEW  depth:", dict(analyze(t)[0]), "final", analyze(t)[1], "bad", analyze(t)[2])
blocks = re.findall(r'<div class="article-card">\n\s*(.{0,12})', t)
print("malformed cards:", len([b for b in blocks if not b.startswith('<h2><a href=')]))
print("stars:", t.count("**"), " h1:", len(re.findall(r"<h1[\s>]", t)))

print("\n--- 顶部 4 卡 ---")
for m in list(re.finditer(r'<div class="article-card">\n\s*<h2><a href="([^"]+)">', t))[:4]:
    seg = t[m.start():m.start()+800]
    d = re.search(r'(\d{4}-\d{2}-\d{2})', seg)
    print(" ", m.group(1), "|", d.group(1) if d else "?")

# 三条新卡 href 唯一性
print("\n--- 新卡 href 计数 ---")
from collections import Counter as C2
hrefs = C2(re.findall(r'<h2><a href="([^"]+)"', t))
for s in ["20261022-judge-liability-verdict-reversed", "20261021-3gpp-proposal-prior-art-date",
          "20261021-goods-names-acceptable-list-q4"]:
    hits = {h: n for h, n in hrefs.items() if s in h}
    print(" ", s, "->", hits)

# articles.json 自检
import json
arts = json.load(open("articles.json", encoding="utf-8"))
print("\narticles.json n =", len(arts), "| top1:", arts[0]["date"], arts[0]["url"])
bad_site = [a for a in arts if not a.get("site")]
print("缺 site 字段:", len(bad_site))

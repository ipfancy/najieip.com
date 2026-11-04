#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-04 终验：正文包含 + 索引结构（对比 origin/main 基线）+ 卡片计数"""
import os, re, subprocess, json

REPO = os.path.expanduser("~/wiki/najieip-verify")
ART = os.path.expanduser("~/wiki/digital-employees/articles")
FILES = ["blog/index.html", "mili/blog/index.html", "najie/blog/index.html"]

def norm(s):
    s = s.replace('"', "").replace("'", "").replace("“", "").replace("”", "")
    s = s.replace("何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰", "")
    s = s.replace("北京纳杰知识产权代理有限公司 何自刚", "")
    s = s.replace("|", "").replace("*", "").replace("#", "")
    s = re.sub(r"-{3,}", "", s)
    s = re.sub(r"\s+", "", s)
    return s

def mdtxt(p):
    t = open(p, encoding="utf-8").read()
    t = re.sub(r"^---.*?\n---\n", "", t, flags=re.S)
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    return norm(t)

def pagetxt(t):
    i = t.find("<h1")
    b = t[i:] if i > 0 else t[t.find("<body"):]
    b = re.sub(r"<script.*?</script>", " ", b, flags=re.S)
    b = re.sub(r"<style.*?</style>", " ", b, flags=re.S)
    b = re.sub(r"<fig.*?</figure>", " ", b, flags=re.S)
    b = re.sub(r"<[^>]+>", " ", b)
    b = b.replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<").replace("&quot;", '"').replace("&#x27;", "'")
    return norm(b)

print("=== A. 正文 md 完整包含 ===")
slug = "20261104-mili-anti-involution-low-price"
t = open(os.path.join(REPO, "mili/blog", slug + ".html"), encoding="utf-8").read()
m, p = mdtxt(os.path.join(ART, slug + ".md")), pagetxt(t)
print(f"md={len(m)} page={len(p)} contained={m in p}")
if m not in p:
    for i in range(min(len(m), len(p))):
        if m[i] != p[i]:
            print("  diff@", i, "md:", repr(m[max(0,i-30):i+50]), "page:", repr(p[max(0,i-30):i+50]))
            break
print("  ld blocks json.loads:", [json.loads(b).get("@type") for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)])
print("  tables:", t.count("<table"), "h2:", len(re.findall(r"<h2", t)), "size:", os.path.getsize(os.path.join(REPO, "mili/blog", slug + ".html")))

print("\n=== B. 索引结构 vs origin/main ===")
def analyze(t):
    hist = {}
    d = 0
    for m in re.finditer(r"<(/?)div\b", t):
        if m.group(1):
            d -= 1
        else:
            hist[d] = hist.get(d, 0) + 1
            d += 1
    return hist, t.count('<div class="article-card">'), len(re.findall(r"<h2><a href=", t))

for f in FILES:
    cur = open(os.path.join(REPO, f), encoding="utf-8").read()
    base = subprocess.run(["git", "-C", REPO, "show", "origin/main:" + f], capture_output=True, text=True).stdout
    hc, cc, h2c = analyze(cur)
    hb, cb, h2b = analyze(base)
    delta = {k: hc.get(k, 0) - hb.get(k, 0) for k in set(hc) | set(hb)}
    print(f"{f}: cards {cb}->{cc} (delta {cc-cb}) h2a {h2b}->{h2c} hist_delta={delta} sum={sum(delta.values())}")

# 每卡以 h2 起 + depth2 卡数
for f in FILES:
    t = open(os.path.join(REPO, f), encoding="utf-8").read()
    cards = re.findall(r'<div class="article-card">.{0,200}', t, re.S)
    mal = sum(1 for c in cards if "<h2><a href=" not in c)
    print(f"{f}: malformed={mal} stars={t.count('**')}")

print("\n=== C. 三篇卡命中 ===")
main = open(os.path.join(REPO, "blog/index.html"), encoding="utf-8").read()
for b, s in (("mili", "20261104-mili-anti-involution-low-price"),
             ("mili", "20261104-mili-provisional-protection-fee"),
             ("najie", "20261104-najie-priority-right-reform-agenda")):
    bi = open(os.path.join(REPO, b, "blog/index.html"), encoding="utf-8").read()
    print(f"{s}: main={len(re.findall(r'<h[23][^>]*><a href=\"[^\"]*'+re.escape(s), main))} brand={len(re.findall(r'<h[23][^>]*><a href=\"[^\"]*'+re.escape(s), bi))}")
print("\n=== D. 首卡日期序 ===")
dates = re.findall(r'(\d{4}-\d{2}-\d{2})', main[main.find("<body"):main.find("<body")+6000])[:8]
print(dates)

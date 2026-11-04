#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""诊断 2026-11-04 三篇新页六项 + 正文包含 + 最新 commit 涉及文件"""
import os, re, json

REPO = os.path.expanduser("~/wiki/najieip-verify")
ART = os.path.expanduser("~/wiki/digital-employees/articles")
PAGES = [
    ("mili", "20261104-mili-anti-involution-low-price", "20261104-mili-anti-involution-low-price.md"),
    ("mili", "20261104-mili-provisional-protection-fee", "20261104-mili-provisional-protection-fee.md"),
    ("najie", "20261104-najie-priority-right-reform-agenda", "20261104-najie-priority-right-reform-agenda.md"),
]

def norm(s):
    s = s.replace("“", "").replace("”", "").replace('"', "").replace("'", "").replace("’", "")
    s = s.replace("何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰", "")
    s = s.replace("北京纳杰知识产权代理有限公司 何自刚", "")
    s = re.sub(r"\s+", "", s)
    return s

def mdtxt(p):
    t = open(p, encoding="utf-8").read()
    t = re.sub(r"^---.*?\n---\n", "", t, flags=re.S)
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    t = t.replace("*", "").replace("#", "")
    return norm(t)

def pagetxt(t):
    b = t[t.find("<body"):]
    b = re.sub(r"<script.*?</script>", " ", b, flags=re.S)
    b = re.sub(r"<style.*?</style>", " ", b, flags=re.S)
    b = re.sub(r"<h1>.*?</h1>", " ", b, flags=re.S)
    b = re.sub(r"<fig.*?</figure>", " ", b, flags=re.S)
    b = re.sub(r"<[^>]+>", " ", b)
    b = b.replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<").replace("&quot;", '"').replace("&#x27;", "'")
    return norm(b)

for brand, slug, mdf in PAGES:
    path = os.path.join(REPO, brand, "blog", slug + ".html")
    t = open(path, encoding="utf-8").read()
    ld = len(re.findall(r'application/ld\+json', t))
    ogimg = len(re.findall(r'property="og:image"', t))
    desc = re.search(r'<meta name="description" content="([^"]*)"', t)
    title = re.search(r"<title>(.*?)</title>", t, re.S)
    h1 = len(re.findall(r"<h1", t))
    h2 = len(re.findall(r"<h2", t))
    stars = len(re.findall(r"(?<![0-9*])\*\*", re.sub(r"[0-9]\*{2,}[0-9.]*", "", t)))
    rawtbl = len(re.findall(r"<p>\|", t))
    style = ("<style>" in t) or ("/style.css" in t)
    d = desc.group(1) if desc else ""
    ti = title.group(1).strip() if title else ""
    print(f"\n### {brand}/{slug}")
    print(f"  size={os.path.getsize(path)} style={style} h1={h1} h2={h2} ld={ld} og:image={ogimg} stars={stars} rawtbl={rawtbl}")
    print(f"  title={ti[:70]}")
    print(f"  desc[{len(d)}]={d[:90]}")
    print(f"  desc==title复读? {d.strip() == ti.split(' — ')[0].strip()}")
    md = os.path.join(ART, mdf)
    if os.path.exists(md):
        m = mdtxt(md)
        p = pagetxt(t)
        print(f"  md_len={len(m)} page_len={len(p)} md_contained={m in p}")
        if m not in p:
            # 找出第一个差异位置
            for i in range(min(len(m), len(p))):
                if m[i] != p[i]:
                    print("   first diff at", i, "md:", repr(m[max(0,i-40):i+60]), "page:", repr(p[max(0,i-40):i+60]))
                    break
    else:
        print("  MD MISSING", md)

print("\n=== 最新 commit 文件 ===")
import subprocess
r = subprocess.run(["git", "-C", REPO, "show", "--stat", "--oneline", "5d05aec"], capture_output=True, text=True)
print(r.stdout[:1500])
print("\n=== articles.json ===")
aj = os.path.join(REPO, "articles.json")
d = json.load(open(aj))
print("len:", len(d))
missing = []
for i, e in enumerate(d):
    u = e.get("url") or e.get("path") or ""
    p = os.path.join(REPO, u.lstrip("/")) if u else None
    if not p or not os.path.exists(p):
        missing.append((i, u))
print("missing pages:", len(missing), missing[:10])
print("top6:", [(e.get("date"), (e.get("url") or "")[:60]) for e in d[:6]])

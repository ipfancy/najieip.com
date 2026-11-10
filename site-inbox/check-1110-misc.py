#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, os, json, subprocess
REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)

print("=== 专题页 mili/family-wealth.html ===")
p = "mili/family-wealth.html"
t = open(p, encoding="utf-8").read()
m = re.search(r'<meta name="description" content="([^"]*)"', t)
print(p, os.path.getsize(p), "h1", len(re.findall(r"<h1", t)),
      "ld", t.count("application/ld+json"), "og:image", t.count("og:image"),
      "canonical", bool(re.search(r'rel="canonical"', t)),
      "desc_len", len(m.group(1)) if m else 0)
print("title串:", re.search(r"<title>(.*?)</title>", t).group(1)[:50])

print("\n=== 85%胜诉率残留全站扫描 ===")
hits = []
for root, dirs, files in os.walk("."):
    if "/.git" in root or root.startswith("./.git"):
        continue
    for fn in files:
        if fn.endswith((".html", ".txt", ".xml", ".json")):
            fp = os.path.join(root, fn)
            try:
                c = open(fp, encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            if "85%" in c and ("胜诉" in c):
                hits.append(fp)
print("hits:", hits or "NONE")

print("\n=== articles.json 违例计数 ===")
r = subprocess.run(["python3", "site-inbox/guard-0918-articles-json.py", "--check"],
                   capture_output=True, text=True)
lines = (r.stdout + r.stderr).splitlines()
for ln in lines:
    if any(k in ln for k in ("违例", "总数", "TOTAL", "violations", "首页", "OK", "top6")):
        print(ln)
print("head:", lines[:4])

print("\n=== 今日文章页结构终验 ===")
pg = open("mili/blog/20261110-mili-will-partial-invalid.html", encoding="utf-8").read()
print("h1", len(re.findall(r"<h1", pg)), "h2", len(re.findall(r"<h2", pg)),
      "ld", pg.count("application/ld+json"), "og:image", pg.count("og:image"),
      "stars", pg.count("**"), "rawtable", len(re.findall(r"<p>\|", pg)),
      "masked", pg.count("https://***"), "bytes", len(pg.encode()))
for blk in re.findall(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', pg, re.S):
    json.loads(blk)
print("ld JSON all parse OK")
print("div open/close:", pg.count("<div"), pg.count("</div>"))

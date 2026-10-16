#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 2026-10-16 诊断 2：目标页 vs 房屋模板 vs md 源"""
import os, re, difflib

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)
TARGET = "najie/blog/customs-ip-filing-3-things-20261016.html"
MD = os.path.expanduser("~/wiki/digital-employees/articles/customs-ip-filing-3-things-20261016.md")

def rd(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()

t = rd(TARGET)
print("TARGET bytes =", os.path.getsize(TARGET), "chars =", len(t))
print("\n--- HEAD (first 2500) ---")
print(t[:2500])
print("\n--- count checks ---")
for k in ["<h1", "<h2", "application/ld+json", "og:image", "og:site_name", "twitter:title",
          "/style.css", "<style>", "keywords", "canonical"]:
    print(f"  {k:24s} = {t.count(k)}")
print("  ** =", t.count("**"))
print("  naked table =", len(re.findall(r"<p>\|.*\|</p>", t)))

m = re.search(r'<meta name="description" content="([^"]*)"', t)
print("\ndescription =", repr(m.group(1) if m else None))

print("\n--- paragraphs in <p> ---")
paras = re.findall(r"<p[^>]*>(.*?)</p>", t, re.S)
print("count =", len(paras))
for i, p in enumerate(paras[:60], 1):
    s = re.sub(r"<[^>]+>", "", p).strip()
    if s:
        print(f"  {i:2d}| {s[:110]}")

print("\n" + "=" * 60)
print("MD SOURCE paragraphs")
print("=" * 60)
md = rd(MD)
print("md bytes =", len(md))
for i, line in enumerate(md.splitlines(), 1):
    if line.strip():
        print(f"  {i:2d}| {line[:110]}")

print("\n" + "=" * 60)
print("HOUSE TEMPLATE: najie/blog/layout-design-originality-claim-322-2026.html")
print("=" * 60)
tpl = rd("najie/blog/layout-design-originality-claim-322-2026.html")
print("bytes =", os.path.getsize("najie/blog/layout-design-originality-claim-322-2026.html"))
print("--- head 3200 ---")
print(tpl[:3200])
print("\n--- ld+json blocks ---")
for i, blk in enumerate(re.findall(r'<script type="application/ld\+json">(.*?)</script>', tpl, re.S), 1):
    print(f"--- block {i} ---")
    print(blk.strip()[:1200])

print("\n" + "=" * 60)
print("site-inbox untracked file vs published page")
print("=" * 60)
si = rd("site-inbox/customs-ip-filing-3-things-20261016.html")
print("si bytes =", len(si), "target bytes =", len(t), "identical =", si == t)
print("--- si head 1500 ---")
print(si[:1500])

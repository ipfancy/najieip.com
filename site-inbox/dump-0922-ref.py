#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""参照页全文 + 图片约定调查"""
import os, re, json, glob

REPO = os.path.expanduser("~/wiki/najieip-verify")
def rd(p):
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

print("######## REF PAGE 0921 najie (full) ########")
print(rd(os.path.join(REPO, "najie/blog/20260921-us-trademark-sanction-defense-window.html")))

print("\n######## 图片资产目录 ########")
for d in ["images", "img", "assets", "blog/images", "static"]:
    fp = os.path.join(REPO, d)
    print("  %-14s exists=%s n=%s" % (d, os.path.isdir(fp), len(os.listdir(fp)) if os.path.isdir(fp) else 0))

print("\n######## najie blog 近期页 og:image 取值 ########")
for f in sorted(glob.glob(os.path.join(REPO, "najie/blog/*.html")))[-10:]:
    t = rd(f)
    m = re.search(r'<meta property="og:image" content="([^"]*)"', t)
    print("  %-56s %s" % (os.path.basename(f)[:54], (m.group(1)[:70] if m else "NONE")))

print("\n######## 落款三行（0921 参照页） ########")
t = rd(os.path.join(REPO, "najie/blog/20260921-us-trademark-sanction-defense-window.html"))
i = t.find("何自刚 |")
print(repr(t[i-400:i+600]))

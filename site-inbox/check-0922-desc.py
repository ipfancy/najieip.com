#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""09-20 mili 页 description 体检"""
import os, re
REPO = os.path.expanduser("~/wiki/najieip-verify")
f = os.path.join(REPO, "mili/blog/20260920-family-wealth-isolation-three-firewalls.html")
t = open(f, encoding="utf-8").read()
for pat in [r'<meta name="description" content="([^"]*)"',
            r'<meta property="og:description" content="([^"]*)"',
            r'<meta name="twitter:description" content="([^"]*)"']:
    m = re.search(pat, t)
    print("%-46s len=%s" % (pat[:44], len(m.group(1)) if m else "NONE"))
    if m:
        print("   ", m.group(1)[:220])
print("\n--- 用户可见正文首段 ---")
ps = re.findall(r"<p[^>]*>(.*?)</p>", t, re.S)
ps = [re.sub(r"<[^>]+>", "", x).strip() for x in ps]
for x in ps[:3]:
    print("   ", x[:180])
print("\n--- 索引卡里的 description ---")
for idx in ["mili/blog/index.html", "blog/index.html"]:
    ti = open(os.path.join(REPO, idx), encoding="utf-8").read()
    for m in re.finditer(r'<div class="article-card">(.*?)</div>\s*</div>', ti, re.S):
        if "family-wealth-isolation" in m.group(1):
            pm = re.search(r"<p>(.*?)</p>", m.group(1), re.S)
            print("  %-22s len=%d" % (idx, len(pm.group(1)) if pm else 0))
            print("     ", (pm.group(1)[:200] if pm else ""))

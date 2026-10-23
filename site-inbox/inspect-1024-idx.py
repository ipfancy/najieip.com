#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查看 EN/FR 索引现有卡片顺序（只读）"""
import re, os
REPO = os.path.expanduser("~/wiki/najieip-verify")
for p in ("en/blog/index.html", "fr/blog/index.html"):
    t = open(os.path.join(REPO, p), encoding="utf-8").read()
    body = t[t.find("<body"):]
    print("===", p, "cards:", body.count('<div class="article-card">'))
    for m in re.finditer(r'<div class="article-card">\s*<h2><a href="([^"]+)"', body):
        print("   ", m.group(1))
    for m in re.finditer(r'<div class="meta">(.*?)</div>', body[:4000], re.S):
        print("   meta:", re.sub(r"<[^>]+>", "", m.group(1)).strip()[:80])

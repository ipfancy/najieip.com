#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""查看 najie 索引 blogPost 数组结构 + 卡片日期序列"""
import os, re
REPO = os.path.expanduser("~/wiki/najieip-verify")
t = open(os.path.join(REPO, "najie/blog/index.html"), encoding="utf-8").read()
i = t.find('"blogPost"')
print("--- blogPost 锚点上下文 ---")
print(repr(t[i-200:i+900]))
print("\n--- 全部 ld+json 块 ---")
for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
    import json
    d = json.loads(m.group(1))
    print("  @type=", d.get("@type"), " keys=", list(d.keys())[:10], " blogPost n=", len(d.get("blogPost", [])))
print("\n--- 卡片日期序列(前12) 与位置 ---")
for m in list(re.finditer(r'<div class="article-card">\s*<h2><a href="([^"]+)"', t))[:12]:
    seg = t[m.start():m.start()+700]
    dm = re.search(r'<div class="meta">(.*?)</div>', seg, re.S)
    print("  @%-7d %-60s %s" % (m.start(), m.group(1)[:58], re.sub(r"<[^>]+>", "", dm.group(1)).strip()[-60:] if dm else "?"))

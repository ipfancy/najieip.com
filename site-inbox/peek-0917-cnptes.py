#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""peek-0917-cnptes.py — 打印 najie 索引里 cnptes 图页卡片（供主索引补卡取值）"""
import os, re

SITE = os.path.expanduser("~/wiki/najieip-verify")
CARD = re.compile(r'<div class="article-card">')
DATE = re.compile(r'(\d{4}-\d{2}-\d{2}) ·')

for rel in ["najie/blog/index.html", "blog/index.html"]:
    t = open(os.path.join(SITE, rel), encoding="utf-8").read()
    print("=====", rel, len(CARD.findall(t)), "cards")
    for m in CARD.finditer(t):
        seg = t[m.start():m.start() + 700]
        if "cnptes-three-layer-architecture-diagram" in seg:
            print(seg[:620])
            print("---")
    print(" 前 4 张：")
    for m in list(CARD.finditer(t))[:4]:
        seg = t[m.start():m.start() + 260]
        d = DATE.search(seg)
        h = re.search(r'href="([^"]+)"', seg)
        print("   ", d.group(1) if d else "-", h.group(1) if h else "?")

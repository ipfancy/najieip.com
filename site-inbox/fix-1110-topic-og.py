#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix-1110-topic-og.py — 专题页 mili/family-wealth.html 补 og:image + twitter 卡"""
import re, os, sys
P = os.path.expanduser("~/wiki/najieip-verify/mili/family-wealth.html")
t = open(P, encoding="utf-8").read()
IMG = "https://najieip.com/img/20261110-mili-will-partial-invalid.png"
m = re.search(r'<meta property="og:title" content="([^"]*)"', t)
title = m.group(1) if m else re.search(r"<title>(.*?)</title>", t).group(1).split(" — ")[0]
m = re.search(r'<meta name="description" content="([^"]*)"', t)
desc = m.group(1) if m else title

has = lambda s: s in t
add = []
if not has('property="og:image"'):
    add.append('<meta property="og:image" content="%s">' % IMG)
if not has('property="og:site_name"'):
    add.append('<meta property="og:site_name" content="北京觅理律师事务所">')
if not has('property="og:type"'):
    add.append('<meta property="og:type" content="website">')
if not has('name="twitter:card"'):
    add.append('<meta name="twitter:card" content="summary_large_image">')
    add.append('<meta name="twitter:title" content="%s">' % title)
    add.append('<meta name="twitter:description" content="%s">' % desc)
    add.append('<meta name="twitter:image" content="%s">' % IMG)
if not has('name="keywords"'):
    add.append('<meta name="keywords" content="家事法律,财富传承,遗嘱,继承纠纷,婚姻财产">')

assert add, "nothing to add"
anchor = '<link rel="canonical"'
assert anchor in t
t2 = t.replace(anchor, "\n".join(add) + "\n" + anchor, 1)
# 断言
assert t2.count("og:image") >= 1
assert t2.count("twitter:card") == 1
assert "https://***" not in t2
for blk in re.findall(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', t2, re.S):
    import json
    json.loads(blk)
print("add=%d bytes %d -> %d" % (len(add), len(t), len(t2)))
print("og:image", t2.count("og:image"), "twitter", t2.count("twitter:"), "h1", len(re.findall(r"<h1", t2)))
open(P, "w", encoding="utf-8").write(t2)
print("WROTE", P, os.path.getsize(P))

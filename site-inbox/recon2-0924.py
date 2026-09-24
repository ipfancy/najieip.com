#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""0924 索引卡插入前 recon：两索引 JSON-LD 结构 + 卡插入锚点"""
import os, re, json

REPO = os.path.expanduser("~/wiki/najieip-verify")


def rd(p):
    with open(os.path.join(REPO, p), encoding="utf-8") as f:
        return f.read()


for idx in ["mili/blog/index.html", "blog/index.html"]:
    t = rd(idx)
    print("=" * 20, idx, "(%d B)" % len(t.encode()))
    blocks = re.findall(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', t, re.S)
    print("  ld+json blocks:", len(blocks))
    for i, b in enumerate(blocks):
        try:
            j = json.loads(b)
        except Exception as e:
            print("  #%d PARSE FAIL %s" % (i, e))
            continue
        print("  #%d @type=%s keys=%s" % (i, j.get("@type"), list(j.keys())))
        if isinstance(j.get("blogPost"), list):
            print("     blogPost len=%d, first=%s" % (len(j["blogPost"]), json.dumps(j["blogPost"][0], ensure_ascii=False)[:160]))
            print("     anchor 'blogPost': [' at %d" % b.find('"blogPost"'))
    # 卡插入锚点
    ci = t.find('<div class="container"')
    print("  container at", ci)
    first_card = t.find('<div class="article-card">', ci)
    print("  first card at", first_card)
    print("  gap repr:", repr(t[ci:first_card]))
    if idx == "mili/blog/index.html":
        cm = t.find("<!-- 财产守护系列 -->")
        print("  财产守护 comment at", cm, "repr:", repr(t[cm - 30:cm + 40]))

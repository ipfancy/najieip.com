#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""索引卡格式 + 插入位诊断"""
import os, re

REPO = os.path.expanduser("~/wiki/najieip-verify")
def rd(p):
    with open(os.path.join(REPO, p), "r", encoding="utf-8", errors="replace") as f:
        return f.read()

for idx in ["najie/blog/index.html", "blog/index.html"]:
    t = rd(idx)
    print("=" * 70)
    print("### %s  (%d B / %d chars)" % (idx, os.path.getsize(os.path.join(REPO, idx)), len(t)))
    cards = [(m.start(), m.group(1), m.group(2), m.group(3)) for m in re.finditer(
        r'<div class="article-card">(.*?)<h2><a href="([^"]+)"[^>]*>(.*?)</a></h2>', t, re.S)]
    print("cards:", len(cards))
    for s, pre, href, title in cards[:5]:
        print("  @%d pre=%r" % (s, pre[:40]))
        print("     href=%s" % href)
        print("     title=%s" % re.sub(r"<[^>]+>", "", title)[:60])
    # raw block of first card
    i = t.find('<div class="article-card">')
    j = t.find('<div class="article-card">', i + 10)
    print("--- RAW FIRST CARD ---")
    print(repr(t[i:j]))
    print("--- CONTAINER ANCHOR ---")
    k = t.find('<div class="container">')
    print(repr(t[k:k+260]))
    # dates in order
    print("--- CARD DATES (first 14) ---")
    for m in list(re.finditer(r'<div class="meta">(.*?)</div>', t))[:14]:
        print("   ", re.sub(r"<[^>]+>", "|", m.group(1))[:80])
    print("--- JSON-LD blogPost count / 3-step presence ---")
    print("  blogPost:", t.count('"@type": "BlogPosting"'), " three-step:", t.count("three-step-selfcheck"))

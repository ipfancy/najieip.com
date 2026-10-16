#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-10-17 i18n 结构终验（本地）"""
import os, re, json, xml.etree.ElementTree as ET

REPO = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "20261009-mili-ai-short-drama-token-evidence"
FAILS = []


def chk(cond, label):
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        FAILS.append(label)


for lang in ("en", "fr"):
    p = f"{REPO}/{lang}/blog/{SLUG}-{lang}.html"
    t = open(p, encoding="utf-8").read()
    b = t[t.find("<body"):]
    sz = os.path.getsize(p)
    chk(t.count("<h1") == 1, f"{lang} h1==1")
    chk(t.count("<h2>") == 4, f"{lang} h2==4")
    chk(t.count("application/ld+json") == 1, f"{lang} ld==1")
    chk(t.count("https://schema.org") >= 1, f"{lang} schema.org ok")
    chk(t.count("https://***") == 0, f"{lang} no masked schema")
    chk("og:image" in t, f"{lang} og:image")
    chk(t.count("hreflang") == 4, f"{lang} hreflang==4")
    chk(t.count("**") == 0, f"{lang} no markdown leak")
    chk(t.count("<!--") == 0, f"{lang} no html comment")
    chk("<table" not in b, f"{lang} no table")
    chk('class="disclaimer"' in t, f"{lang} machine-translation disclaimer")
    # JSON-LD 可解析
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try:
            json.loads(m)
            chk(True, f"{lang} ld+json parses")
        except Exception as e:
            chk(False, f"{lang} ld+json parses ({e})")
    print(f"  {lang} size={sz} bytes")

for lang, path in (("en", f"{REPO}/en/blog/index.html"), ("fr", f"{REPO}/fr/blog/index.html")):
    t = open(path, encoding="utf-8").read()
    b = t[t.find("<body"):]
    chk(f"/{lang}/blog/{SLUG}-{lang}.html" in b, f"{lang} index card present")
    n = b.count('<div class="article-card">')
    chk(n == 21, f"{lang} index cards == 21 (got {n})")
    # div 深度归零
    depth = 0
    bad = False
    for m in re.finditer(r"<(/?)div\b", b):
        if m.group(1):
            depth -= 1
            if depth < 0:
                bad = True
        else:
            depth += 1
    chk(depth == 0 and not bad, f"{lang} index div depth balanced")

zp = f"{REPO}/mili/blog/{SLUG}.html"
z = open(zp, encoding="utf-8").read()
chk(z.count("hreflang") == 4, "zh page hreflang==4")
chk("</head>" in z, "zh page head closed")
chk(z.count("<h1") == 1, "zh page h1==1")

sm = f"{REPO}/sitemap.xml"
s = open(sm, encoding="utf-8").read()
ET.fromstring(s)
chk(s.count("<loc>") == 311, f"sitemap loc==311 (got {s.count('<loc>')})")
for lang in ("en", "fr"):
    u = f"https://najieip.com/{lang}/blog/{SLUG}-{lang}.html"
    chk(u in s, f"sitemap has {lang} loc")
    i = s.find(u)
    chk("<lastmod>" in s[i:i + 200], f"sitemap {lang} lastmod")

img = f"{REPO}/img/{SLUG}.png"
chk(os.path.exists(img) and os.path.getsize(img) > 100000, "cover image in repo img/")

print("\nFAILURES:", len(FAILS))
for f in FAILS:
    print(" -", f)

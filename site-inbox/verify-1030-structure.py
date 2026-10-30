#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""1030 结构终验：三索引 div 配平 + 卡片形态 + 跨品牌污染 + 覆盖矩阵。"""
import os, re, json

SITE = os.path.expanduser("~/wiki/najieip-verify")
IDX = {"mili": "mili/blog/index.html", "najie": "najie/blog/index.html", "main": "blog/index.html"}
TARGETS = [
    ("mili", "20261030-mili-ai-harm-outpaces-law"),
    ("najie", "20261030-najie-training-data-provenance"),
    ("najie", "20261030-najie-foreign-filing-confidentiality-review"),
    ("mili", "20261030-mili-trademark-renewal"),
    ("mili", "20261028-mili-social-insurance-subsidy"),
    ("mili", "20261021-mili-ai-creation-cost-evidence"),
]
FAIL = []

def rd(p):
    return open(p, encoding="utf-8").read()

def card_end(t, s):
    i, depth = s, 0
    while i < len(t):
        o = t.find("<div", i); c = t.find("</div>", i)
        if c == -1:
            return len(t)
        if o != -1 and o < c:
            depth += 1; i = o + 4
        else:
            depth -= 1; i = c + 6
            if depth == 0:
                return i
    return len(t)

print("=== INDEX STRUCTURE ===")
for name, rel in IDX.items():
    t = rd(os.path.join(SITE, rel))
    depth, bad = 0, 0
    for m in re.finditer(r"<(/?)div\b[^>]*>", t):
        depth += -1 if m.group(1) else 1
        if depth < 0:
            bad += 1
    n = t.count('<div class="article-card">')
    malformed = 0
    d2cards = 0
    for m in re.finditer(r'<div class="article-card">', t):
        blk = t[m.start():card_end(t, m.start())]
        if "<h2><a href=" not in blk.split("\n")[1] and not re.match(r'<div class="article-card">\s*<h2><a href=', blk):
            malformed += 1
    stars = t.count("**")
    print(f"{name:6} cards={n:4} depth_end={depth} underflow={bad} malformed={malformed} stars={stars} bytes={len(t.encode())}")
    if depth != 0 or bad or malformed or stars:
        FAIL.append(f"{name} structure")

print("\n=== COVERAGE ===")
main = rd(os.path.join(SITE, "blog/index.html"))
aj = rd(os.path.join(SITE, "articles.json"))
ajl = json.loads(aj)
aj_urls = {d.get("url", "") for d in ajl}
btext = {k: rd(os.path.join(SITE, v)) for k, v in IDX.items() if k != "main"}
bad_main = json.loads(aj)
urls = [d.get("url", "") for d in bad_main]
missing_page = [u for u in urls if u and not os.path.exists(os.path.join(SITE, u.lstrip("/")))]
for brand, slug in TARGETS:
    page = os.path.join(SITE, brand, "blog", slug + ".html")
    ok_page = os.path.exists(page) and os.path.getsize(page) > 1500
    in_b = btext[brand].count(slug)
    in_other = [k for k in btext if k != brand and slug in btext[k]]
    in_m = main.count(slug)
    in_aj = ("/%s/blog/%s.html" % (brand, slug)) in aj_urls
    print(f"{brand}/{slug[:48]:48} page={ok_page} brand={in_b} main={in_m} aj={in_aj} cross={in_other}")
    if not ok_page: FAIL.append(slug + " page")
    if in_b != 1: FAIL.append(slug + f" brand card count {in_b}")
    if in_m != 1: FAIL.append(slug + f" main card count {in_m}")
    if not in_aj: FAIL.append(slug + " articles.json")
    if in_other: FAIL.append(slug + " cross-brand " + str(in_other))

print(f"\narticles.json entries={len(ajl)} no-page={len(missing_page)}")
if missing_page:
    print("  NO-PAGE:", missing_page[:5])
    FAIL.append("articles.json no-page %d" % len(missing_page))

print("\n=== PAGE-LEVEL (six checks) ===")
for brand, slug in TARGETS:
    t = rd(os.path.join(SITE, brand, "blog", slug + ".html"))
    h1 = t.count("<h1")
    ld = t.count("application/ld+json")
    ogok = bool(re.search(r'property="og:image" content="https://najieip\.com/img/', t))
    desc = re.search(r'<meta name="description" content="([^"]*)"', t)
    title = re.search(r"<title>(.*?)</title>", t, re.S).group(1).split(" — ")[0]
    dup = desc and desc.group(1).strip() == title.strip()
    stars = len(re.findall(r"\*\*", re.sub(r"[0-9]\*{2,}[0-9.]*", "", t)))
    bare = len(re.findall(r"<p>\s*\|", t))
    sp = t.count("https://schema.org")
    print(f"{slug[:50]:50} h1={h1} ld={ld} og={ogok} duptitle={bool(dup)} stars={stars} baretbl={bare} schema={sp}")
    if not (h1 == 1 and ld == 2 and ogok and not dup and stars == 0 and bare == 0 and sp >= 2):
        FAIL.append(slug + " page checks")

print("\nFAILURES:", FAIL if FAIL else "NONE")

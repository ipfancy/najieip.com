#!/usr/bin/env python3
"""SiteOps 1009 诊断：近两日新文六联缺陷 + 索引卡在位核查"""
import os, re, json

BASE = os.path.expanduser("~/wiki/najieip-verify")

def load(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()

# 1. 逐目录列出 20261008/20261009 新文页
new_pages = []
for d in ["blog", "mili/blog", "najie/blog", "aipunajie/blog"]:
    dp = os.path.join(BASE, d)
    if not os.path.isdir(dp):
        continue
    for f in sorted(os.listdir(dp)):
        if f.startswith("20261008") or f.startswith("20261009"):
            if f.endswith(".html") and not f.startswith("index"):
                new_pages.append(os.path.join(dp, f))

print("=== NEW PAGES (1008-1009) ===")
for p in new_pages:
    t = load(p)
    sz = os.path.getsize(p)
    h1 = len(re.findall(r"<h1[ >]", t))
    ld = t.count("application/ld+json")
    ogimg = 'property="og:image"' in t
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = m.group(1) if m else ""
    tm = re.search(r"<title>(.*?)</title>", t, re.S)
    title = tm.group(1).strip() if tm else ""
    tcore = re.sub(r"\s*[—\-]\s*纳杰觅理.*$", "", title).strip()
    dup = (desc.strip() == title.strip()) or (desc.strip() == tcore)
    stars = t.count("**")
    baretable = len(re.findall(r"<p>\|.*\|</p>", t))
    defects = []
    if h1 == 0: defects.append("h1=0")
    if ld == 0: defects.append("ld=0")
    if not ogimg: defects.append("no-og:image")
    if dup: defects.append("desc=title")
    if stars: defects.append("stars=%d" % stars)
    if baretable: defects.append("baretable=%d" % baretable)
    rel = os.path.relpath(p, BASE)
    print("%-70s %6dB  %s" % (rel, sz, "OK" if not defects else "DEFECT: " + ", ".join(defects)))

# 2. 索引卡在位核查
print("\n=== INDEX CARD PRESENCE ===")
indexes = {
    "main": os.path.join(BASE, "blog/index.html"),
    "mili": os.path.join(BASE, "mili/blog/index.html"),
    "najie": os.path.join(BASE, "najie/blog/index.html"),
    "aipunajie": os.path.join(BASE, "aipunajie/blog/index.html"),
}
idx = {k: load(v) for k, v in indexes.items() if os.path.exists(v)}
print("indexes loaded:", list(idx.keys()))

for p in new_pages:
    rel = os.path.relpath(p, BASE)
    slug = os.path.basename(p)[:-5]
    brand = rel.split("/")[0] if "/" in rel else "main"
    main_href = "/" + rel
    in_main = (main_href in idx.get("main", "")) or (slug in idx.get("main", ""))
    bkey = brand if brand in ("mili", "najie", "aipunajie") else "mili"
    in_brand = (slug in idx.get(bkey, "")) if brand != "main" else True
    print("%-70s main=%s  %s=%s" % (rel, "Y" if in_main else "N", bkey, "Y" if in_brand else "N"))

for k in ("main", "mili", "najie", "aipunajie"):
    if k in idx:
        print("%s index article-card count: %d" % (k, idx[k].count('<div class="article-card">')))

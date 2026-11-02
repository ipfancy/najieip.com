#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps 11-02 诊断：页面六项 + 正文包含 + 索引卡计数"""
import os, re, json, glob, subprocess

REPO = os.path.expanduser("~/wiki/najieip-verify")
MD_DIR = os.path.expanduser("~/wiki/digital-employees/articles")

SLUGS = [
    ("najie", "20261102-najie-tech-export-catalog-48"),
    ("najie", "20261102-najie-ai-search-summary-pay"),
]

def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

def textify(s):
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<").replace("&quot;", '"')
    return re.sub(r"\s+", "", s)

for brand, slug in SLUGS:
    p = os.path.join(REPO, brand, "blog", slug + ".html")
    print("=" * 70)
    print(f"### {brand}/{slug}  exists={os.path.exists(p)} size={os.path.getsize(p)}")
    t = read(p)
    head = t[:t.find("</head>") + 7]
    h1 = len(re.findall(r"<h1[\s>]", t))
    ld = len(re.findall(r'application/ld\+json', t))
    ogimg = re.search(r'property="og:image"\s+content="([^"]*)"', t)
    desc = re.search(r'<meta name="description" content="([^"]*)"', t)
    title = re.search(r"<title>(.*?)</title>", t, re.S)
    can = re.search(r'rel="canonical" href="([^"]*)"', t)
    tw = len(re.findall(r'name="twitter:title"', t))
    site_name = len(re.findall(r'property="og:site_name"', t))
    kw = len(re.findall(r'name="keywords"', t))
    h2 = len(re.findall(r"<h2[\s>]", t))
    stars = len(re.findall(r"\*\*", re.sub(r"[0-9]\*{2,}[0-9.]*", "", t)))
    bare_tbl = len(re.findall(r"<p>\s*\|", t))
    print(f"h1={h1} ld={ld} h2={h2} og:image={'Y' if ogimg and ogimg.group(1) else 'N'} tw:title={tw} site_name={site_name} kw={kw}")
    print(f"desc_len={len(desc.group(1)) if desc else 0} desc==title? {desc and title and desc.group(1).strip()==title.group(1).strip()}")
    print(f"canonical={can.group(1) if can else None}")
    print(f"stars={stars} bare_table_rows={bare_tbl} style={'inline' if '<style>' in t else ('ext' if '/style.css' in t else 'NONE')}")
    # JSON-LD parse
    for i, blk in enumerate(re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S)):
        try:
            o = json.loads(blk)
            print(f"  ld[{i}] OK @type={o.get('@type')}")
        except Exception as e:
            print(f"  ld[{i}] FAIL {e}")
    # 正文包含 md
    md = os.path.join(MD_DIR, slug + ".md")
    if not os.path.exists(md):
        alt = glob.glob(os.path.join(MD_DIR, "*" + slug.split("-", 1)[1] + "*.md"))
        md = alt[0] if alt else None
    if md and os.path.exists(md):
        mraw = read(md)
        mraw = re.sub(r"^---.*?---", " ", mraw, count=1, flags=re.S)
        mraw = re.sub(r"<!--.*?-->", " ", mraw, flags=re.S)
        mtxt = textify(mraw.replace("#", " ").replace("*", " "))
        b = t[t.find("<body"):]
        btxt = textify(b)
        print(f"md={os.path.basename(md)} mdlen={len(mtxt)} contained={mtxt in btxt if mtxt else None}")
    else:
        print("md NOT FOUND")

print("\n=== INDEX CARD COUNTS ===")
for brand, slug in SLUGS:
    for idx in [os.path.join(REPO, "blog", "index.html"), os.path.join(REPO, brand, "blog", "index.html")]:
        s = read(idx)
        cards = len(re.findall(r'<div class="article-card">(?:(?!<div class="article-card">).)*?' + re.escape(slug), s, re.S))
        simple = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug), s))
        print(f"{os.path.relpath(idx, REPO)}  slug_hits={s.count(slug)}  href_cards={simple}")

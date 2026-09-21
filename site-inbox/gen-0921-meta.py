#!/usr/bin/env python3
# 0921 缺口文章元数据收集：品牌卡 + 文章页 og/h1/desc/keywords/JSON-LD datePublished
import os, re, json

REPO = os.path.expanduser("~/wiki/najieip-verify")
TARGETS = [
    ("najie", "20260921-us-trademark-sanction-defense-window"),
    ("mili", "querren-buqinquan-zhisu-2026"),
    ("najie", "xin-shangbiaofa-2027"),
]


def strip(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()


out = []
for brand, slug in TARGETS:
    idx = os.path.join(REPO, brand, "blog/index.html")
    t = open(idx, encoding="utf-8").read()
    body = t[t.find("<body"):]
    # 品牌索引卡片
    m = re.search(
        r'<div class="article-card">\s*<h2><a href="([^"]*' + re.escape(slug) + r'[^"]*)"[^>]*>(.*?)</a></h2>'
        r'(.*?)</div>\s*(?=<div class="article-card"|</div>)', body, re.S)
    card_title = card_desc = card_date = None
    if m:
        seg = m.group(0)
        card_title = strip(m.group(2))
        pd = re.search(r"<p>(.*?)</p>", seg, re.S)
        card_desc = strip(pd.group(1)) if pd else None
        dd = re.search(r"(\d{4}-\d{2}-\d{2})", seg)
        card_date = dd.group(1) if dd else None
    # 品牌索引内嵌 BlogPosting JSON-LD
    ld_date = None
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        if slug in blk:
            dm = re.search(r'"datePublished"\s*:\s*"([^"]+)"', blk)
            if dm:
                ld_date = dm.group(1)
    # 文章页
    f = os.path.join(REPO, brand, "blog", slug + ".html")
    size = os.path.getsize(f) if os.path.exists(f) else 0
    page = open(f, encoding="utf-8").read() if os.path.exists(f) else ""
    def meta(prop):
        mm = re.search(r'<meta[^>]+(?:property|name)="' + prop + r'"[^>]+content="([^"]*)"', page) or \
             re.search(r'<meta[^>]+content="([^"]*)"[^>]+(?:property|name)="' + prop + r'"', page)
        return mm.group(1) if mm else None
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S)
    pdate = None
    for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
        dm = re.search(r'"datePublished"\s*:\s*"([^"]+)"', blk)
        if dm:
            pdate = dm.group(1); break
    rec = {
        "brand": brand, "slug": slug, "file_size": size,
        "card_title": card_title, "card_desc": card_desc, "card_date": card_date,
        "ld_date_brand_index": ld_date, "page_datePublished": pdate,
        "og_title": meta("og:title"), "og_desc": meta("og:description"),
        "description": meta("description"), "keywords": meta("keywords"),
        "h1": strip(h1.group(1)) if h1 else None,
        "has_refresh": 'http-equiv="refresh"' in page,
    }
    out.append(rec)
    print(json.dumps(rec, ensure_ascii=False, indent=1))

json.dump(out, open(os.path.join(REPO, "site-inbox/meta-0921-gaps.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("wrote site-inbox/meta-0921-gaps.json")

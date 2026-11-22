#!/usr/bin/env python3
# 五段巡检：页面存在 → 页面六项+正文 → 品牌卡 → 主卡 → articles.json
import os, re, json, subprocess, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
BRANDS = ("mili", "najie", "aipunajie")

# 候选当日/近日 slug（content.db 近3日 + .published.json 近3日）
slugs = [
    "mili-food-oem-trademark-113-order-20261122",
    "20261121-mili-divorce-game-account-88w",
    "20261120-mili-device-procurement-firmware-checklist",
    "20261119-tv-box-backdoor-5x-penalty",
]

def find_page(slug):
    for b in BRANDS:
        p = os.path.join(REPO, b, "blog", slug + ".html")
        if os.path.exists(p):
            return b, p
    # 模糊匹配
    for b in BRANDS:
        d = os.path.join(REPO, b, "blog")
        for fn in os.listdir(d):
            if fn.endswith(".html") and slug[:14] in fn:
                return b, os.path.join(d, fn)
    return None, None

def textify(s):
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<").replace("&quot;", '"').replace("&#x27;", "'")
    return s

for slug in slugs:
    b, p = find_page(slug)
    if not p:
        print(f"== {slug}: PAGE_MISSING")
        continue
    t = open(p, encoding="utf-8").read()
    size = os.path.getsize(p)
    h1 = len(re.findall(r"<h1[\s>]", t))
    ld = t.count("application/ld+json")
    ogimg = "og:image" in t
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = m.group(1) if m else ""
    h1t = re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S)
    h1txt = re.sub(r"<[^>]+>", "", h1t.group(1)).strip() if h1t else ""
    dup = (desc.strip() == h1txt.strip()) or (len(desc) < 40)
    star = len(re.findall(r"\*\*", t))
    rawtbl = len(re.findall(r"<p>\s*\|", t))
    body = t[t.find("<body"):]
    art = re.search(r"<article.*?</article>", body, re.S)
    artlen = len(art.group(0)) if art else 0
    rel = False
    if art:
        byline_pat = re.compile(r"何自刚\s*\|\s*知识产权律师[^<]*")
        art_txt = textify(art.group(0))
        md = os.path.expanduser(f"~/wiki/digital-employees/articles/{slug}.md")
        if not os.path.exists(md):
            cands = [f for f in os.listdir(os.path.expanduser("~/wiki/digital-employees/articles")) if f.endswith(".md") and slug[:14] in f]
            md = os.path.expanduser("~/wiki/digital-employees/articles/" + cands[0]) if cands else md
        if os.path.exists(md):
            mdt = open(md, encoding="utf-8").read()
            mdt = re.sub(r"^---.*?---", "", mdt, flags=re.S)
            mdt = re.sub(r"(?m)^.*?<!--.*?-->.*$", "", mdt)
            mdt = "\n".join(l for l in mdt.split("\n") if not l.strip().startswith("#") and not l.strip().startswith("***") and not l.strip().startswith("---") and not l.strip().startswith(">"))
            mdt = re.sub(r"^\s*\d+\.\s*", "", mdt, flags=re.M)
            mdt = re.sub(r"[*`|\-:：\s「」『』【】\"“”'’]", "", mdt)
            pgt = re.sub(r"<h[1-6].*?</h[1-6]>", " ", art.group(0), flags=re.S)
            pgt = textify(pgt)
            pgt = pgt.replace("北京纳杰知识产权代理有限公司 何自刚", "")
            pgt = re.sub(r"[*`|\-:：\s「」『』【】\"“”'’]", "", pgt)
            rel = (mdt == pgt)
            if not rel:
                rel = f"MISMATCH md={len(mdt)} pg={len(pgt)}"
    # 索引卡
    def card_count(idx):
        if not os.path.exists(idx): return -1
        tt = open(idx, encoding="utf-8").read()
        return len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug[:20]), tt))
    brand_card = card_count(os.path.join(REPO, b, "blog", "index.html"))
    main_card = card_count(os.path.join(REPO, "blog", "index.html"))
    print(f"== {slug}")
    print(f"   brand={b} size={size} h1={h1} ld={ld} ogimg={ogimg} dupdesc={dup} star={star} rawtbl={rawtbl} artlen={artlen}")
    print(f"   md_contained={rel} brand_card={brand_card} main_card={main_card}")

# articles.json top6
aj = os.path.join(REPO, "articles.json")
if os.path.exists(aj):
    d = json.load(open(aj, encoding="utf-8"))
    print(f"== articles.json total={len(d)}")
    for it in d[:6]:
        u = it.get("url", "")
        fp = os.path.join(REPO, u.lstrip("/"))
        print(f"   top: {u} exists={os.path.exists(fp)} date={it.get('date')}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""11-18 夜班巡检：当日文五段判据 + 索引对账 + articles.json 前6位 + sitemap"""
import os, re, json, glob, subprocess

REPO = os.path.expanduser("~/wiki/najieip-verify")
BRANDS = ("mili", "najie", "aipunajie")

def rd(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

def textify(s):
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S)
    s = re.sub(r"<h1.*?</h1>", " ", s, flags=re.S)
    s = re.sub(r"<h2.*?</h2>", " ", s, flags=re.S)
    s = re.sub(r"<figure.*?</figure>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&amp;", "&").replace("&gt;", ">").replace("&lt;", "<").replace("&quot;", '"').replace("&#x27;", "'").replace("&nbsp;", " ")
    return s

def norm(s):
    s = re.sub(r"[“”‘’\"'「」『』【】]", "", s)
    s = re.sub(r"-{3,}", "", s)
    s = s.replace(":", "").replace("|", "")
    s = re.sub(r"\s+", "", s)
    return s

# 当日新增页面（按 mtime 判断）
today = "20261118"
pages = []
for b in BRANDS:
    for p in glob.glob(os.path.join(REPO, b, "blog", f"{today}-*.html")):
        pages.append((b, p))
pages.sort()

print("=== A. 当日页面清单 ===")
for b, p in pages:
    print(f"  {b}/{os.path.basename(p)} {os.path.getsize(p)}B")

idx = {b: rd(os.path.join(REPO, b, "blog", "index.html")) for b in BRANDS}
main_idx = rd(os.path.join(REPO, "blog", "index.html"))

print("\n=== B. 六项判据 + 索引卡 ===")
fails = []
for b, p in pages:
    t = rd(p)
    slug = os.path.basename(p)[:-5]
    h1 = len(re.findall(r"<h1[ >]", t))
    ld = len(re.findall(r'application/ld\+json', t))
    ogimg = bool(re.search(r'property="og:image"', t))
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = m.group(1) if m else ""
    tm = re.search(r"<title>(.*?)</title>", t, re.S)
    title = re.sub(r"\s*[—\-|]\s*(纳杰觅理|纳杰|觅理).*$", "", tm.group(1)).strip() if tm else ""
    descrep = (desc.strip() == title.strip()) or (len(desc) < 60)
    stars = len(re.findall(r"[0-9*]\*{2,}[0-9.]*", t))
    stars_all = t.count("**") - 2 * stars
    baretab = len(re.findall(r"<p>\s*\|", t))
    ctx = t[t.find("<body"):]
    # md containment
    md = os.path.expanduser(f"~/wiki/digital-employees/articles/{slug}.md")
    mdok = "NO_MD"
    if os.path.exists(md):
        mm = rd(md)
        mm = re.sub(r"^---.*?\n---\n", "", mm, flags=re.S)
        lines = []
        for ln in mm.split("\n"):
            s2 = ln.strip()
            if not s2: continue
            if s2.startswith("#"): continue
            if re.match(r"^\*\*[^*\n]{1,30}\*\*$", s2) and not s2.endswith(("。", "！", "？")): continue
            if re.match(r"^[一二三四五六七八九十]、", s2): continue
            if s2.startswith("<!--") or s2.endswith("-->"): continue
            s2 = re.sub(r"^\d+\.\s*", "", s2)
            s2 = s2.replace("何自刚 | 知识产权律师 | 爱普纳杰 · 觅理 · 纳杰", "")
            lines.append(s2)
        mdn = norm("".join(lines))
        art = re.search(r"<article.*?</article>", ctx, re.S)
        pg = art.group(0) if art else ctx
        pgn = norm(textify(pg))
        mdok = mdn in pgn
        if not mdok:
            for i in range(min(len(mdn), len(pgn))):
                if mdn[i] != pgn[i]:
                    print(f"    DIFF@{i}: md={mdn[i-20:i+20]!r} pg={pgn[i-20:i+20]!r}")
                    break
    bc = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug), idx[b]))
    mc = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug), main_idx))
    canon = re.search(r'rel="canonical" href="([^"]*)"', t)
    cok = canon and f"/{b}/blog/{slug}.html" in canon.group(1)
    stat = "OK" if (h1 == 1 and ld >= 2 and ogimg and not descrep and stars_all == 0 and baretab == 0 and mdok is True and cok and bc == 1 and mc == 1) else "DEFECT"
    if stat != "OK": fails.append(slug)
    print(f"  [{stat}] {b}/{slug}")
    print(f"     h1={h1} ld={ld} og:image={ogimg} desc_repeat={descrep}(len={len(desc)}) **={stars_all} baretab={baretab} md_contained={mdok} canon_ok={bool(cok)}")
    print(f"     brand_card={bc} main_card={mc}")

print("\n=== C. articles.json 前 6 位 + 总条数 ===")
aj = json.load(open(os.path.join(REPO, "articles.json"), encoding="utf-8"))
print(f"  total={len(aj)}")
for i, it in enumerate(aj[:6], 1):
    url = it.get("url", "")
    rel = url.lstrip("/")
    ok = os.path.exists(os.path.join(REPO, rel)) if rel else False
    print(f"  {i}. {'HIT' if ok else 'MISSING'} {url} | {it.get('title','')[:28]}")

print("\n=== D. sitemap loc 数 + 当日 loc ===")
sm = rd(os.path.join(REPO, "sitemap.xml"))
locs = re.findall(r"<loc>(.*?)</loc>", sm)
print(f"  locs={len(locs)}")
for b, p in pages:
    slug = os.path.basename(p)[:-5]
    hit = [l for l in locs if slug in l]
    print(f"  {slug}: {hit if hit else 'MISSING'}")

print("\n=== E. FAILS ===")
print("  " + (", ".join(fails) if fails else "NONE"))

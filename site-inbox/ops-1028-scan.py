#!/usr/bin/env python3
"""SiteOps 每日巡检扫描（只读）：近3日品牌页 × 六联判据 + 双索引缺口 + articles.json 守卫"""
import os, re, json, glob, sys

ROOT = "/Users/ziganghe/wiki/najieip-verify"
BRANDS = ["mili", "najie", "aipunajie"]
TODAY = "2026-10-28"
CUT = "20261026"  # 文件名日期前缀 >= 此值视为近3日

def load(p):
    with open(p, encoding="utf-8") as f:
        return f.read()

main_t = load(os.path.join(ROOT, "blog/index.html"))

def hrefs(t):
    return set(re.findall(r'<h[23][^>]*><a href="([^"]+)"', t))

main_hrefs = hrefs(main_t)

rows = []
for b in BRANDS:
    bidx = os.path.join(ROOT, b, "blog/index.html")
    bt = load(bidx) if os.path.exists(bidx) else ""
    bh = hrefs(bt)
    for f in sorted(glob.glob(os.path.join(ROOT, b, "blog/*.html"))):
        fn = os.path.basename(f)
        if fn == "index.html":
            continue
        m = re.match(r'^(\d{8})-', fn)
        if not m or m.group(1) < CUT:
            continue
        t = load(f)
        body = t[t.find("<body"):]
        h1 = len(re.findall(r'<h1[\s>]', t))
        ld = len(re.findall(r'<script type="application/ld\+json">', t))
        ogimg = 1 if 'property="og:image"' in t else 0
        desc = re.search(r'<meta name="description" content="([^"]*)"', t)
        title = re.search(r'<title>(.*?)</title>', t, re.S)
        desc_v = desc.group(1) if desc else ""
        title_v = re.sub(r'\s+—.*$', '', title.group(1)).strip() if title else ""
        repeat = 1 if desc_v and (desc_v.strip() == title_v.strip() or desc_v.strip() in title_v) else 0
        # markdown stars excluding masked patent numbers
        stars = len(re.findall(r'(?<![0-9*])\*\*', re.sub(r'[0-9]\*{2,}[0-9.X]*', '', body)))
        bare = len(re.findall(r'<p>\|.*?\|</p>', t))
        url_abs = "/%s/blog/%s" % (b, fn)
        in_main = 1 if url_abs in main_t else 0
        in_brand = 1 if any(h.endswith(fn) for h in bh) else 0
        size = os.path.getsize(f)
        defects = []
        if h1 == 0: defects.append("h1=0")
        if ld < 2: defects.append("ld=%d" % ld)
        if not ogimg: defects.append("no-og:image")
        if repeat: defects.append("desc=title")
        if stars: defects.append("**=%d" % stars)
        if bare: defects.append("bare-table=%d" % bare)
        rows.append(dict(brand=b, file=fn, size=size, h1=h1, ld=ld, og=ogimg,
                         stars=stars, bare=bare, repeat=repeat,
                         in_main=in_main, in_brand=in_brand, defects=defects))

print("== 近3日品牌页扫描 (%d 篇) ==" % len(rows))
for r in rows:
    flag = "OK " if not r["defects"] else "NG "
    print("%s%s %-62s %6dB h1=%d ld=%d og=%d main=%d brand=%d %s" % (
        flag, r["brand"], r["file"], r["size"], r["h1"], r["ld"], r["og"],
        r["in_main"], r["in_brand"], ",".join(r["defects"])))

print("\n== 缺口汇总 ==")
print("缺主索引:", [r["file"] for r in rows if not r["in_main"]])
print("缺品牌索引:", [r["file"] for r in rows if not r["in_brand"]])
print("有缺陷:", [(r["file"], r["defects"]) for r in rows if r["defects"]])

# articles.json 守卫
print("\n== articles.json ==")
aj = os.path.join(ROOT, "articles.json")
if os.path.exists(aj):
    d = json.load(open(aj, encoding="utf-8"))
    arr = d if isinstance(d, list) else d.get("articles", [])
    missing = [a for a in arr if not os.path.exists(os.path.join(ROOT, a.get("url", "").lstrip("/")))]
    print("total=%d missing_file=%d" % (len(arr), len(missing)))
    for a in missing[:6]:
        print("  -", a.get("url"), "|", a.get("title", "")[:30])

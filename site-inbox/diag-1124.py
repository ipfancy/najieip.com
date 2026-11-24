#!/usr/bin/env python3
# SiteOps 每日巡检诊断 2026-11-24 夜班
import os, re, json, glob, subprocess

REPO = "/Users/ziganghe/wiki/najieip-verify"
BRANDS = ("mili", "najie", "aipunajie")

def read(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()

# 1. 近 3 日文章页
pages = []
for b in BRANDS:
    for p in glob.glob(f"{REPO}/{b}/blog/*.html"):
        fn = os.path.basename(p)
        if fn == "index.html":
            continue
        if re.match(r"^202611(2[1-4])", fn):
            pages.append((b, p, fn, os.path.getsize(p)))

print("=== PAGES ===")
for b, p, fn, sz in sorted(pages):
    t = read(p)
    h1 = len(re.findall(r"<h1[ >]", t))
    h2 = len(re.findall(r"<h2[ >]", t))
    ld = t.count("application/ld+json")
    ogimg = 'property="og:image"' in t
    ttl = (re.search(r"<title>(.*?)</title>", t, re.S) or [None, ""])[1].strip()
    desc = (re.search(r'<meta name="description" content="(.*?)"', t, re.S) or [None, ""])[1].strip()
    dupdesc = desc[:20] in ttl or ttl[:20] in desc if desc else False
    stars = len(re.findall(r"\*\*", re.sub(r"[0-9]\*{2,}[0-9.]*", "", t)))
    pipes = len(re.findall(r"<p>\s*\|", t))
    schema = t.count("https://schema.org")
    fm = len(re.findall(r"<p>\s*(slug|title|date|brand|style|voice|end|tags|author)\s*[:：]", t)) + len(re.findall(r"<p>\s*-{3,}\s*</p>", t))
    print(f"{b:10s} {fn:52s} {sz:6d}B h1={h1} h2={h2} ld={ld} ogimg={int(ogimg)} stars={stars} pipep={pipes} schema={schema} fmlk={fm} descLen={len(desc)} dup={int(dupdesc)}")

# 2. 索引卡检查
main_idx = read(f"{REPO}/blog/index.html")
print("\n=== CARDS ===")
for b, p, fn, sz in sorted(pages):
    slug = fn[:-5]
    brand_idx = read(f"{REPO}/{b}/blog/index.html")
    bc = re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug), brand_idx)
    mc = re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug), main_idx)
    print(f"{slug:52s} brand={len(bc)} main={len(mc)}")

# 3. articles.json top6
aj = json.load(open(f"{REPO}/articles.json", encoding="utf-8"))
arr = aj if isinstance(aj, list) else aj.get("articles", [])
print(f"\n=== articles.json === n={len(arr)}")
miss = 0
for i, a in enumerate(arr[:6]):
    u = a.get("url", "")
    f = os.path.join(REPO, u.lstrip("/"))
    ok = os.path.exists(f)
    if not ok:
        miss += 1
    print(f"  top{i+1} {'OK ' if ok else '404'} {u[:70]}")
print("top6_missing=", miss)
slugs = {a.get("url", "") for a in arr}
for b, p, fn, sz in sorted(pages):
    u = f"/{b}/blog/{fn}"
    print(f"  aj_has {u} -> {u in slugs}")

# 4. feed 窗口
feed = read(f"{REPO}/feed.xml")
print("\n=== feed ===", "items=", feed.count("<item>"))
for b, p, fn, sz in sorted(pages):
    print("  ", fn[:-5], "in feed:", fn[:-5] in feed)

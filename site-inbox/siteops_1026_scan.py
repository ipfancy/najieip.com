#!/usr/bin/env python3
# SiteOps 每日缺口扫描 20261026
import os, re, json, sys, subprocess

BASE = "/Users/ziganghe/wiki/najieip-verify"
BRANDS = ["mili", "najie", "aipunajie"]
INDEXES = {
    "main": f"{BASE}/blog/index.html",
    "mili": f"{BASE}/mili/blog/index.html",
    "najie": f"{BASE}/najie/blog/index.html",
    "aipunajie": f"{BASE}/aipunajie/blog/index.html",
}

def rd(p):
    try:
        return open(p, encoding="utf-8").read()
    except Exception as e:
        return ""

idx = {k: rd(v) for k, v in INDEXES.items()}
sitemap = rd(f"{BASE}/sitemap.xml")
aj = json.load(open(f"{BASE}/articles.json", encoding="utf-8"))

# recent pages: files in brand blog dirs changed in last 4 days per git
out = subprocess.run(
    ["git", "-C", BASE, "log", "--since=5.days", "--name-only", "--diff-filter=AM", "--format="],
    capture_output=True, text=True).stdout
files = sorted({l.strip() for l in out.splitlines() if l.strip().endswith(".html")
                and re.match(r"^(mili|najie|aipunajie)/blog/[^/]+\.html$", l.strip())})

aj_paths = {a.get("url") or a.get("path") or "" for a in aj} if isinstance(aj, list) else set()
aj_all = json.dumps(aj, ensure_ascii=False)

print(f"[scan] recent article pages: {len(files)}  articles.json entries: {len(aj) if isinstance(aj,list) else '?'}")
print(f"{'file':0} | size | ld | h1 | ogimg | mainidx | brandidx | sitemap | aj")
rows = []
for f in files:
    p = os.path.join(BASE, f)
    if not os.path.exists(p):
        continue
    t = rd(p)
    size = os.path.getsize(p)
    slug = os.path.basename(f)[:-5]
    brand = f.split("/")[0]
    ld = len(re.findall(r'application/ld\+json', t))
    h1 = len(re.findall(r"<h1[ >]", t))
    ogimg = "og:image" in t
    in_main = f"/{brand}/blog/{slug}.html" in idx["main"]
    in_brand = (f'./{slug}.html' in idx[brand]) or (f"/{brand}/blog/{slug}.html" in idx[brand])
    in_sm = f"/{brand}/blog/{slug}.html" in sitemap
    in_aj = f"/{brand}/blog/{slug}.html" in aj_all
    rows.append(dict(file=f, slug=slug, brand=brand, size=size, ld=ld, h1=h1,
                     ogimg=ogimg, main=in_main, brandi=in_brand, sm=in_sm, aj=in_aj))
    flags = []
    if size < 1500: flags.append("STUB")
    if ld < 2: flags.append(f"LD={ld}")
    if h1 != 1: flags.append(f"H1={h1}")
    if not ogimg: flags.append("NO-OGIMG")
    if not in_main: flags.append("MAIN-MISS")
    if not in_brand: flags.append("BRAND-MISS")
    if not in_sm: flags.append("SM-MISS")
    if not in_aj: flags.append("AJ-MISS")
    print(f"{f} | {size} | {ld} | {h1} | {ogimg} | {in_main} | {in_brand} | {in_sm} | {in_aj} || {','.join(flags) or 'OK'}")

json.dump(rows, open("/tmp/siteops_1026_scan.json", "w"), ensure_ascii=False, indent=1)

# six-item: desc repeats title / markdown leak
print("\n[六联正文项]")
for r in rows:
    t = rd(os.path.join(BASE, r["file"]))
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = m.group(1) if m else ""
    h1m = re.search(r"<h1[^>]*>(.*?)</h1>", t, re.S)
    h1txt = re.sub(r"<[^>]+>", "", h1m.group(1)).strip() if h1m else ""
    rep = bool(desc) and (desc.strip()[:30] == h1txt[:30])
    body = t[t.find("<body"):]
    body_ns = re.sub(r"[0-9*]\*{2,}[0-9.]*", "", body)
    stars = body_ns.count("**")
    rawtbl = len(re.findall(r"<p>\s*\|", body))
    print(f"{r['slug']}: desc_len={len(desc)} repeat={rep} stars={stars} rawtable={rawtbl}")

# index card dup check
print("\n[主索引重复卡]")
from collections import Counter
c = Counter(re.findall(r'<h2><a href="(/[^"]+)"', idx["main"]))
print([k for k, v in c.items() if v > 1][:10] or "none")
print(f"main cards={idx['main'].count('article-card')} mili={idx['mili'].count('article-card')} najie={idx['najie'].count('article-card')}")

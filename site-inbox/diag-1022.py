#!/usr/bin/env python3
"""10-22 SiteOps daily: read-only diagnostics for new pages, indexes, articles.json."""
import re, os, json, subprocess, glob

REPO = "/Users/ziganghe/wiki/najieip-verify"
PAGES = [
    "mili/blog/20261021-3gpp-proposal-prior-art-date.html",
    "mili/blog/20261022-judge-liability-verdict-reversed.html",
    "mili/blog/20261022-safety-production-crimes.html",
    "najie/blog/20261021-goods-names-acceptable-list-q4.html",
    "najie/blog/20261022-najie-gaoqi-ip-30points.html",
]

def read(p):
    with open(os.path.join(REPO, p), encoding="utf-8") as f:
        return f.read()

def texts(t):
    b = t[t.find("<body"):]
    b = re.sub(r"<script.*?</script>", " ", b, flags=re.S)
    b = re.sub(r"<style.*?</style>", " ", b, flags=re.S)
    return re.sub(r"<[^>]+>", " ", b)

print("=== A. PAGE DEFECTS (six-item) ===")
for p in PAGES:
    t = read(p)
    h1 = t.count("<h1")
    ld = t.count("application/ld+json")
    ogimg = 'og:image' in t
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = m.group(1) if m else ""
    ti = re.search(r"<title>(.*?)</title>", t, re.S)
    title = ti.group(1).strip() if ti else ""
    title_core = title.split(" — ")[0].split(" | ")[0]
    dup = desc.strip()[:30] == title_core[:30] and len(desc) < 90
    body = texts(t)
    body_nomask = re.sub(r"[0-9]\*{2,}[0-9.]*", "", body)
    stars = body_nomask.count("**")
    bare_tbl = len(re.findall(r"<p>\s*\|[^<]*\|", t))
    style = ("<style>" in t) or ('/style.css"' in t)
    h2 = t.count("<h2")
    flags = []
    if h1 != 1: flags.append(f"h1={h1}")
    if ld < 2: flags.append(f"ld={ld}")
    if not ogimg: flags.append("no-og:image")
    if dup: flags.append("desc=title")
    if stars: flags.append(f"stars={stars}")
    if bare_tbl: flags.append(f"bareTable={bare_tbl}")
    if not style: flags.append("no-style")
    print(f"{os.path.basename(p):52s} {os.path.getsize(os.path.join(REPO,p)):7d}B h1={h1} ld={ld} h2={h2} desc={len(desc)} {'OK' if not flags else 'DEFECT '+','.join(flags)}")

print("\n=== B. INDEX PRESENCE ===")
main = read("blog/index.html")
for p in PAGES:
    brand, _, fn = p.split("/", 2)[2], None, os.path.basename(p)
    slug = fn[:-5]
    brandname = p.split("/")[0]
    bidx = read(f"{brandname}/blog/index.html")
    in_main = slug in main
    in_brand = slug in bidx
    print(f"{slug:50s} main={'Y' if in_main else 'N'} brand({brandname})={'Y' if in_brand else 'N'}")

print("\n=== C. articles.json ===")
aj = json.load(open(os.path.join(REPO, "articles.json"), encoding="utf-8"))
arts = aj if isinstance(aj, list) else aj.get("articles", [])
print("total entries:", len(arts))
missing = 0
for a in arts:
    u = a.get("url") or a.get("path") or ""
    loc = u.lstrip("/")
    if loc and not os.path.exists(os.path.join(REPO, loc)):
        missing += 1
print("entries without local file:", missing)
print("--- top6 homepage exposure ---")
for a in arts[:6]:
    u = (a.get("url") or a.get("path") or "").lstrip("/")
    fp = os.path.join(REPO, u)
    ex = os.path.exists(fp)
    st = ""
    if ex:
        tt = read(u)
        st = f"h1={tt.count('<h1')} ld={tt.count('application/ld+json')} ogimg={'og:image' in tt}"
        if tt.count("<h1") != 1 or tt.count("application/ld+json") < 2 or "og:image" not in tt:
            st += " DEFECT"
    else:
        st = "FILE-MISSING"
    print(f"  {a.get('date','')} {u[:55]:57s} {st}")

print("\n=== D. sitemap coverage ===")
sm = read("sitemap.xml")
locs = re.findall(r"<loc>(.*?)</loc>", sm)
print("sitemap loc count:", len(locs))
for p in PAGES:
    print(f"  {'/'+p:60s} {'IN' if ('https://najieip.com/'+p) in locs else 'MISSING'}")

print("\n=== E. published.json vs page existence ===")
pj = json.load(open("/Users/ziganghe/wiki/digital-employees/articles/.published.json", encoding="utf-8"))
rows = []
if isinstance(pj, dict):
    for k, v in pj.items():
        if isinstance(v, dict):
            rows.append((v.get("slug") or k, v.get("published_at", "")))
        else:
            rows.append((k, str(v)))
else:
    for v in pj:
        rows.append((v.get("slug"), v.get("published_at", "")))
for slug, at in rows[-6:]:
    hits = glob.glob(os.path.join(REPO, f"*/blog/{slug}.html")) + glob.glob(os.path.join(REPO, f"blog/{slug}.html"))
    print(f"  {at[:10]} {str(slug)[:55]:57s} {'page OK' if hits else 'NO-PAGE'}")

import re, json, os, sqlite3

REPO = "/Users/ziganghe/wiki/najieip-verify"
slugs = {
    "20261127-mili-pregnant-blood-smuggling": "mili",
    "20261127-mili-eu-trademark-real-cost": "mili",
}

def read(p):
    return open(p, encoding="utf-8").read()

for slug, brand in slugs.items():
    p = f"{REPO}/{brand}/blog/{slug}.html"
    t = read(p)
    h1 = len(re.findall(r"<h1[\s>]", t))
    h2 = len(re.findall(r"<h2[\s>]", t))
    ld = t.count('application/ld+json')
    types = re.findall(r'"@type"\s*:\s*"([^"]+)"', t)
    ogimg = 'og:image' in t
    desc = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = desc.group(1) if desc else ""
    title = re.search(r"<title>(.*?)</title>", t, re.S)
    title = title.group(1) if title else ""
    stars = t.count("**")
    baretable = len(re.findall(r"<p>\s*\|", t))
    canon = re.search(r'rel="canonical" href="([^"]*)"', t)
    canon = canon.group(1) if canon else ""
    # ld json parse
    bad = 0
    for blk in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', t, re.S):
        try:
            json.loads(blk)
        except Exception:
            bad += 1
    print(f"[{slug}] bytes={len(t.encode())} h1={h1} h2={h2} ld={ld} types={types} ogimg={ogimg} stars={stars} baretbl={baretable} ld_bad={bad}")
    print(f"   title={title[:50]!r}")
    print(f"   desc[{len(desc)}]={desc[:90]!r}")
    print(f"   canonical={canon}")

# index card checks
print("\n--- INDEX CARDS ---")
for idx in [f"{REPO}/mili/blog/index.html", f"{REPO}/blog/index.html"]:
    t = read(idx)
    lab = "mili_idx" if "mili/blog" in idx else "main_idx"
    for slug in slugs:
        cards = re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug) + r'[^"]*"', t)
        print(f"{lab}: {slug} -> cards={len(cards)}")
    print(f"{lab}: total article-card={t.count('article-card')}")

# articles.json
aj = json.load(open(f"{REPO}/articles.json", encoding="utf-8"))
items = aj if isinstance(aj, list) else aj.get("articles", [])
print(f"\narticles.json total={len(items)}")
for slug in slugs:
    hit = [i for i in items if slug in json.dumps(i, ensure_ascii=False)]
    print(f"  {slug}: {len(hit)} entry {hit}")
# top6 exposure
print("top6:", [(i.get("url", "")[-45:], i.get("date")) for i in items[:6]])

# sitemap
sm = read(f"{REPO}/sitemap.xml")
for slug in slugs:
    print(f"sitemap {slug}: {sm.count(slug)}")
print("sitemap loc=", sm.count("<loc>"))

#!/usr/bin/env python3
# SiteOps 1020 diag: page quality six-criteria + index presence + articles.json guard status
import os, re, json, glob

REPO = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(REPO)

TARGET = "mili/blog/customs-ip-detention-30-day-timeline-20261018.html"

def analyze(p):
    t = open(p, encoding="utf-8").read()
    body = t[t.find("<body"):] if "<body" in t else t
    h1 = len(re.findall(r"<h1[ >]", t))
    ld = t.count('application/ld+json')
    og_img = len(re.findall(r'property="og:image"', t))
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = m.group(1) if m else ""
    mt = re.search(r"<title>(.*?)</title>", t, re.S)
    title = mt.group(1).strip() if mt else ""
    rep = (desc.strip() and desc.strip()[:20] in title) or (title[:20] in desc)
    stars = t.count("**")
    table_rows = len(re.findall(r"<p>\|.*?\|</p>", t))
    style = ("<style>" in t) or ('/style.css' in t)
    return dict(path=p, size=len(t.encode()), bytes=os.path.getsize(p), h1=h1, ld=ld,
                og_image=og_img, desc_len=len(desc), desc=desc[:70], title=title[:50],
                desc_repeat=bool(rep), stars=stars, bare_table=table_rows,
                style=style, h2=len(re.findall(r"<h2[ >]", t)))

print("=== TARGET PAGE ===")
a = analyze(TARGET)
for k, v in a.items():
    print(f"  {k}: {v}")

print("\n=== INDEX PRESENCE ===")
slug = "customs-ip-detention-30-day-timeline-20261018"
for idx in ["blog/index.html", "mili/blog/index.html", "najie/blog/index.html", "aipunajie/blog/index.html"]:
    if not os.path.exists(idx):
        print(f"  {idx}: MISSING FILE"); continue
    t = open(idx, encoding="utf-8").read()
    print(f"  {idx}: count={t.count(slug)} cards={t.count('article-card')}")

print("\n=== articles.json ===")
j = json.load(open("articles.json", encoding="utf-8"))
arts = j if isinstance(j, list) else j.get("articles", [])
print(f"  total={len(arts)}")
bad = []
for i, e in enumerate(arts):
    u = e.get("url", "")
    fp = u.lstrip("/")
    if not os.path.exists(fp) or os.path.getsize(fp) < 1500:
        bad.append((i + 1, u))
print(f"  no-page-or-stub={len(bad)}")
for i, u in bad[:6]:
    print(f"    rank{i}: {u}")
# homepage exposure
print(f"  homepage slice(0,6) = {[e.get('url') for e in arts[:6]]}")

print("\n=== RECENT BLOG FILES (git, 4d) ===")
os.system("git log origin/main --since='4 days ago' --name-only --diff-filter=AM --pretty=format:'' | grep -E 'blog/.*\\.html$' | grep -v index.html | sort -u")

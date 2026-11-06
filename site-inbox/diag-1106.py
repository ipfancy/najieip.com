#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps daily diag 2026-11-06: new pages six-item check + index card presence."""
import os, re, json, subprocess, glob

REPO = os.path.expanduser("~/wiki/najieip-verify")
BRANDS = ["mili", "najie", "aipunajie"]
main_idx = os.path.join(REPO, "blog", "index.html")

def read(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()

# gather candidate pages: date prefix 2026110x or modified last 3 days via git
out = subprocess.run(["git", "-C", REPO, "log", "--since=3 days ago", "--name-only",
                      "--diff-filter=AM", "--format="], capture_output=True, text=True).stdout
files = sorted({l.strip() for l in out.splitlines() if l.strip().endswith(".html")})

rows = []
for rel in files:
    if not re.match(r"(mili|najie|aipunajie)/blog/[^/]+\.html$", rel):
        continue
    p = os.path.join(REPO, rel)
    if not os.path.exists(p):
        rows.append({"rel": rel, "exists": False}); continue
    t = read(p)
    size = os.path.getsize(p)
    h1 = len(re.findall(r"<h1[ >]", t))
    ld = len(re.findall(r'application/ld\+json', t))
    ogi = len(re.findall(r'property="og:image"', t))
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = m.group(1) if m else ""
    tm = re.search(r"<title>(.*?)</title>", t, re.S)
    title = tm.group(1) if tm else ""
    naked_tbl = len(re.findall(r"<p>\s*\|", t))
    stars = len(re.findall(r"(?<![0-9])\*\*", re.sub(r"[0-9]\*{2,}[0-9.]*", "", t)))
    slug = rel.split("/")[-1]
    brand = rel.split("/")[0]
    # index card presence
    bidx = read(os.path.join(REPO, brand, "blog", "index.html"))
    bcard = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug), bidx))
    mcard = len(re.findall(r'<h[23][^>]*><a href="[^"]*' + re.escape(slug), read(main_idx)))
    rows.append(dict(rel=rel, exists=True, size=size, h1=h1, ld=ld, og_image=ogi,
                     desc_len=len(desc), desc=desc[:60], title=title[:50],
                     desc_eq_title=(desc.strip() == title.split(" — ")[0].strip()),
                     naked_tbl=naked_tbl, stars=stars, bcard=bcard, mcard=mcard))

for r in rows:
    print(json.dumps(r, ensure_ascii=False))

print("----ARTICLES.JSON----")
aj = json.load(open(os.path.join(REPO, "articles.json")))
print("total", len(aj))
for i, a in enumerate(aj):
    d = a.get("date", "")
    if d >= "2026-11-03":
        u = a.get("url", "")
        f = os.path.join(REPO, u.lstrip("/"))
        print(i, d, u, "exists" if os.path.exists(f) else "MISSING")

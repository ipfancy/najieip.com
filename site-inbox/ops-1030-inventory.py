#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SiteOps daily inventory: recent article pages + six-item defect check + index coverage."""
import os, re, json, subprocess, sys, html

ROOT = os.path.expanduser("~/wiki/najieip-verify")
BRANDS = ["mili", "najie", "aipunajie"]

def rd(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()

def textify(t):
    t = re.sub(r"<script.*?</script>", " ", t, flags=re.S)
    t = re.sub(r"<style.*?</style>", " ", t, flags=re.S)
    t = re.sub(r"<[^>]+>", "", t)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()

files = []
for b in BRANDS:
    d = os.path.join(ROOT, b, "blog")
    if not os.path.isdir(d):
        continue
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".html") or fn == "index.html":
            continue
        p = os.path.join(d, fn)
        sz = os.path.getsize(p)
        files.append((b, fn, p, sz))

# recent by git: pages added/modified in last 3 days
try:
    out = subprocess.run(["git", "-C", ROOT, "log", "--since=3.days", "--name-only",
                          "--diff-filter=AM", "--pretty=format:"],
                         capture_output=True, text=True).stdout
    recent = {os.path.basename(x.strip()) for x in out.splitlines() if x.strip().endswith(".html")}
except Exception:
    recent = set()

main_idx = rd(os.path.join(ROOT, "blog", "index.html"))
aj = {}
try:
    aj = {a.get("url") or a.get("link") or "" for a in json.load(open(os.path.join(ROOT, "articles.json")))}
    ajtxt = " ".join(aj)
except Exception:
    ajtxt = ""

idx_by_brand = {}
for b in BRANDS:
    p = os.path.join(ROOT, b, "blog", "index.html")
    idx_by_brand[b] = rd(p) if os.path.exists(p) else ""

rows = []
for b, fn, p, sz in files:
    slug = fn[:-5]
    if sz < 1500:
        continue
    t = rd(p)
    if 'http-equiv="refresh"' in t or "http-equiv='refresh'" in t:
        continue
    if not (slug in recent or fn[:8] in ("20261029", "20261030")):
        continue
    h1 = t.count("<h1")
    ld = t.count("application/ld+json")
    ogimg = "og:image" in t
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = m.group(1) if m else ""
    ti = re.search(r"<title>(.*?)</title>", t, re.S)
    title = html.unescape(ti.group(1)).split(" — ")[0].strip() if ti else ""
    body = t[t.find("<body"):]
    stars = len(re.findall(r"\*\*", re.sub(r"[0-9]\*{2,}[0-9.]*", "", body)))
    bare_tbl = len(re.findall(r"<p>\s*\|", body))
    row = dict(brand=b, slug=slug, size=sz, h1=h1, ld=ld, ogimg=ogimg,
               desc_len=len(desc), desc_dup=(desc.strip() == title.strip()),
               stars=stars, bare_tbl=bare_tbl,
               in_main=fn in main_idx or slug in main_idx,
               in_brand=slug in idx_by_brand.get(b, ""),
               in_aj=slug in ajtxt)
    rows.append(row)

print(f"{'brand':10} {'slug':52} {'sz':>6} h1 ld og dsc dup ** tbl main brnd aj")
for r in rows:
    print(f"{r['brand']:10} {r['slug'][:52]:52} {r['size']:6} {r['h1']:2} {r['ld']:2} "
          f"{'Y' if r['ogimg'] else 'N':2} {r['desc_len']:3} {'DUP' if r['desc_dup'] else '   '} "
          f"{r['stars']:2} {r['bare_tbl']:3} {'Y' if r['in_main'] else 'N':4} "
          f"{'Y' if r['in_brand'] else 'N':4} {'Y' if r['in_aj'] else 'N'}")

print("\nDEFECTS:")
for r in rows:
    d = []
    if r["h1"] == 0: d.append("no-h1")
    if r["ld"] < 2: d.append(f"ld={r['ld']}")
    if not r["ogimg"]: d.append("no-og:image")
    if r["desc_dup"]: d.append("desc=title")
    if r["stars"] > 0: d.append(f"stars={r['stars']}")
    if r["bare_tbl"] > 0: d.append(f"baretable={r['bare_tbl']}")
    if not r["in_main"]: d.append("NOT-IN-MAIN")
    if not r["in_brand"]: d.append("NOT-IN-BRAND")
    if not r["in_aj"]: d.append("no-articles.json")
    if d:
        print(f"  {r['brand']}/{r['slug']}: {', '.join(d)}")
print(f"\nTOTAL recent pages: {len(rows)}")

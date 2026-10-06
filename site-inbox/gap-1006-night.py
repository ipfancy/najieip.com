#!/usr/bin/env python3
"""Nightly 1006: gap check main index vs brand indexes + malformed-page six-point check."""
import os, re, glob, json

ROOT = "/Users/ziganghe/wiki/najieip-verify"
SLUGS = {
    "mili": ["20261006-mili-gas-post-judgment-six-checklist",
             "20261005-mili-gas-supply-cutoff-justification",
             "20261004-mili-gas-deviation-settlement-account",
             "bambu-stratasys-fto-decision-tree-20261004",
             "20261006-nobel-icecube-patent-four-rules"],
    "najie": ["20261005-patent-annual-fee-ledger-5-signals",
              "20261005-trademark-law-2027-implementing-rules",
              "20261005-trademark-squatting-3-remedies",
              "20261003-trademark-invalidated-500w"],
}
files = {}
for d in ("blog", "mili/blog", "najie/blog"):
    p = os.path.join(ROOT, d, "index.html")
    files[d] = open(p, encoding="utf-8").read() if os.path.exists(p) else ""

print("=== INDEX CARD PRESENCE ===")
for brand, slugs in SLUGS.items():
    idx = files[f"{brand}/blog"]
    for s in slugs:
        fpath = os.path.join(ROOT, brand, "blog", s + ".html")
        exists = os.path.exists(fpath)
        in_brand = s in idx
        in_main = s in files["blog"]
        flag = "OK " if (exists and in_brand and in_main) else "GAP"
        print(f"{flag} {brand}/{s}  file={exists} brand_idx={in_brand} main_idx={in_main}")

print("\n=== SIX-POINT MALFORMED CHECK (recent pages) ===")
paths = []
for brand in SLUGS:
    for s in SLUGS[brand]:
        paths.append(os.path.join(ROOT, brand, "blog", s + ".html"))
paths.append(os.path.join(ROOT, "najie", "blog", "20261003-trademark-invalidated-500w.html"))
seen = set()
for p in paths:
    if p in seen or not os.path.exists(p):
        continue
    seen.add(p)
    t = open(p, encoding="utf-8").read()
    h1 = t.count("<h1")
    ld = t.count("application/ld+json")
    ogimg = "og:image" in t
    m = re.search(r'<meta name="description" content="([^"]*)"', t)
    desc = m.group(1) if m else ""
    title = re.search(r"<title>(.*?)</title>", t, re.S)
    title = title.group(1).strip() if title else ""
    dup = bool(desc) and (desc.strip().rstrip(" —|") in title or title.startswith(desc.strip()[:25]))
    rawtbl = len(re.findall(r"<p>\s*\|.*\|\s*</p>", t))
    star = t.count("**")
    style = ("<style>" in t) or ("/style.css" in t)
    bad = (h1 == 0) or (ld == 0) or (not ogimg) or dup or rawtbl > 0 or star > 0
    print(f"{'BAD' if bad else 'OK '} {os.path.relpath(p, ROOT)}  B={os.path.getsize(p)} style={style} h1={h1} ld={ld} ogimg={ogimg} dup={dup} rawrow={rawtbl} star={star}")

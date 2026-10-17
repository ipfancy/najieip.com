#!/usr/bin/env python3
"""Inspect an index page: card block structure + JSON-LD blogPost shape."""
import os, re, json, sys

REPO = os.path.expanduser("~/wiki/najieip-verify")
idx = sys.argv[1]
t = open(os.path.join(REPO, idx), encoding="utf-8").read()

# first card via div-depth pairing
start = t.find('<div class="article-card">')
i, depth = start, 0
while i < len(t):
    m = re.match(r'</?div\b[^>]*>', t[i:])
    if m:
        if m.group(0).startswith("</"):
            depth -= 1
        else:
            depth += 1
        i += m.end()
        if depth == 0:
            break
    else:
        i += 1
print("=== FIRST CARD (%d..%d) ===" % (start, i))
print(t[start:i])
print("\n=== FIRST 3 CARD DATES ===")
for m in list(re.finditer(r'<div class="meta">(.*?)</div>', t, re.S))[:3]:
    print(repr(m.group(1).strip()[:160]))
print("\n=== JSON-LD blogPost shape ===")
for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
    try:
        o = json.loads(blk)
    except Exception as e:
        print("ld parse fail", e, blk[:100]); continue
    if "blogPost" in o:
        bp = o["blogPost"]
        print("blogPost count:", len(bp))
        print(json.dumps(bp[0], ensure_ascii=False)[:500])
        print("anchor sample:", t[t.find('"blogPost": ['):t.find('"blogPost": [')+120])
    else:
        print("ld type:", o.get("@type"))

#!/usr/bin/env python3
import os, re, glob
REPO = os.path.expanduser("~/wiki/najieip-verify")
tgt = os.path.join(REPO, "najie/blog/mili-food-oem-trademark-113-order-20261122.html")
t = open(tgt, encoding="utf-8").read()
he = t.find("</head>") + 7
print("=== TARGET HEAD ===")
print(t[:he][:3000])
print("=== BODY START ===")
print(t[he:he+900])
print("=== TAIL ===")
print(t[-700:])
print("=== NAJIE 精修候选 (ld=2 且 og:image) ===")
cands = []
for p in sorted(glob.glob(os.path.join(REPO, "najie/blog/*.html")), key=os.path.getmtime, reverse=True):
    if p.endswith("index.html"): continue
    s = open(p, encoding="utf-8", errors="ignore").read()
    if s.count("application/ld+json") >= 2 and "og:image" in s:
        cands.append((os.path.basename(p), os.path.getsize(p)))
for c in cands[:6]: print("  ", c)
print("=== COVER ===")
for pat in ["cover-mili-food-oem-trademark-113-order-20261122.png", "cover-20261122-mili-food-oem-trademark-113-order.png", "*food-oem*"]:
    print(pat, "->", glob.glob(os.path.expanduser("~/wiki/digital-employees/articles/" + pat)))

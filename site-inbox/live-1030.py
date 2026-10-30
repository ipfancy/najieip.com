#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""1030 线上终验：页面 200 + 六项判据 + 索引卡 HIT + sitemap + 封面 + live articles.json。"""
import subprocess, re, time, json, sys

BASE = "https://najieip.com"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
FAIL = []

PAGES = [
    ("mili", "20261030-mili-ai-harm-outpaces-law"),
    ("najie", "20261030-najie-training-data-provenance"),
    ("najie", "20261030-najie-foreign-filing-confidentiality-review"),
    ("mili", "20261030-mili-trademark-renewal"),
    ("mili", "20261028-mili-social-insurance-subsidy"),
    ("mili", "20261021-mili-ai-creation-cost-evidence"),
]

def curl(url, head=False):
    for _ in range(3):
        cmd = ["curl", "-s", "--max-time", "25", "-A", UA]
        cmd += ["-I"] if head else []
        cmd += ["-w", "\n@@CODE:%{http_code}@@", url]
        r = subprocess.run(cmd, capture_output=True, text=True)
        out = r.stdout
        m = re.search(r"@@CODE:(\d+)@@", out)
        code = int(m.group(1)) if m else 0
        if code == 200:
            return code, out
        time.sleep(3)
    return code, out

def body(url):
    sep = "?cb=%d" % int(time.time())
    c, o = curl(url + sep)
    return c, o

print("=== PAGES ===")
for brand, slug in PAGES:
    url = f"{BASE}/{brand}/blog/{slug}.html"
    c, t = body(url)
    h1 = t.count("<h1")
    ld = t.count("application/ld+json")
    og = 'property="og:image"' in t and "/img/" in t
    canon = re.search(r'<link rel="canonical" href="([^"]*)"', t)
    canok = canon and canon.group(1).endswith(f"/{brand}/blog/{slug}.html")
    stars = len(re.findall(r"\*\*", re.sub(r"[0-9]\*{2,}[0-9.]*", "", t)))
    schema = t.count("https://schema.org")
    print(f"{slug[:50]:50} {c} h1={h1} ld={ld} og={og} canon={bool(canok)} stars={stars} schema={schema} bytes={len(t)}")
    if not (c == 200 and h1 == 1 and ld == 2 and og and canok and stars == 0 and schema >= 2):
        FAIL.append("page " + slug)

print("\n=== INDEXES ===")
for rel in ("blog/", "mili/blog/", "najie/blog/"):
    c, t = body(f"{BASE}/{rel}")
    print(f"/{rel:12} {c} bytes={len(t)} cards={t.count('article-card')}")
    if c != 200:
        FAIL.append("index " + rel)

c, t = body(f"{BASE}/blog/")
for brand, slug in PAGES:
    if slug not in t:
        FAIL.append("main index miss " + slug)
print("main index cards for 6 targets:", sum(1 for b, s in PAGES if s in t), "/6")

print("\n=== SITEMAP ===")
c, t = body(f"{BASE}/sitemap.xml")
locs = t.count("<loc>")
print(f"sitemap {c} loc={locs}")
for brand, slug in PAGES:
    if slug not in t:
        FAIL.append("sitemap miss " + slug)
if locs < 354:
    FAIL.append(f"sitemap loc {locs}")

print("\n=== COVERS ===")
for brand, slug in PAGES:
    c, _ = curl(f"{BASE}/img/{slug}.png", head=True)
    print(f"img/{slug}.png {c}")
    if c != 200:
        FAIL.append("img " + slug)

print("\n=== LIVE articles.json ===")
c, t = body(f"{BASE}/articles.json")
try:
    d = json.loads(t)
    print(f"{c} entries={len(d)}")
    top6 = [x["url"] for x in d[:6]]
    print("top6:", *top6, sep="\n  ")
    import os
    SITE = os.path.expanduser("~/wiki/najieip-verify")
    miss = [u for u in top6 if not os.path.exists(os.path.join(SITE, u.lstrip("/")))]
    if miss:
        FAIL.append("top6 no-page " + str(miss))
    if len(d) > 230:
        FAIL.append(f"articles.json not quarantined {len(d)}")
except Exception as e:
    print("parse fail", e, t[:200])
    FAIL.append("articles.json live")

print("\nFAILURES:", FAIL if FAIL else "NONE")

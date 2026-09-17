#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe-0917-index-links.py — 三个博客索引里每张卡片的 href 逐条探活

输出：非 200 的卡片（含所在索引、href、状态、卡片标题）→ site-inbox/index-link-probe-0917.json
用法：python3 probe-0917-index-links.py
"""
import json, os, re, sys
from concurrent.futures import ThreadPoolExecutor
import subprocess

SITE = os.path.expanduser("~/wiki/najieip-verify")
HOST = "https://najieip.com"
CARD = re.compile(r'<div class="article-card">')
HREF = re.compile(r'<h2><a href="([^"]+)"')
TITLE = re.compile(r'<h2><a href="[^"]*"[^>]*>([^<]*)')
INDEXES = ["blog/index.html", "mili/blog/index.html", "najie/blog/index.html"]


def probe(url):
    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
                        "-L", "--max-time", "25", url], capture_output=True, text=True)
    return url, r.stdout.strip()


rows = []
for rel in INDEXES:
    t = open(os.path.join(SITE, rel), encoding="utf-8").read()
    for m in CARD.finditer(t):
        seg = t[m.start():m.start() + 500]
        h = HREF.search(seg)
        if not h:
            rows.append({"index": rel, "href": "(no href)", "title": "(malformed)"})
            continue
        href = h.group(1)
        if href.startswith("http"):
            url = href
        elif href.startswith("/"):
            url = HOST + href
        else:
            url = HOST + "/" + os.path.dirname(rel) + "/" + href.lstrip("./")
        rows.append({"index": rel, "href": href, "url": url,
                     "title": (TITLE.search(seg).group(1) if TITLE.search(seg) else "")})

print("卡片总数:", len(rows))
uniq = {}
for r in rows:
    if "url" in r:
        uniq.setdefault(r["url"], []).append(r)
print("唯一 URL:", len(uniq))

dead = []
with ThreadPoolExecutor(max_workers=8) as ex:
    for url, code in ex.map(probe, list(uniq.keys())):
        if code != "200":
            for r in uniq[url]:
                dead.append(dict(r, status=code))

print("非 200 卡片:", len(dead))
for d in dead[:40]:
    print("  %s  [%s]  %s  |  %s" % (d.get("status"), d["index"], d["href"], d["title"][:40]))

json.dump({"total_cards": len(rows), "unique_urls": len(uniq), "dead": dead},
          open(os.path.join(SITE, "site-inbox/index-link-probe-0917.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("报告: site-inbox/index-link-probe-0917.json")

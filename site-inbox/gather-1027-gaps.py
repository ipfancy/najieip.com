#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gap scan v2: any <h2|h3><a href> in brand indexes vs main index. Dump card blocks."""
import re, os, json

BASE = os.path.expanduser("~/wiki/najieip-verify")
mainp = os.path.join(BASE, "blog/index.html")
main = open(mainp, encoding="utf-8").read()

def hrefs(t):
    return [m.group(1) for m in re.finditer(r'<h[23][^>]*><a href="([^"]+)"', t)]

main_set = set(hrefs(main))
print("main cards:", main.count('class="article-card"'), "hrefs:", len(main_set))

def card_block(t, href):
    """Locate the article-card div containing href via div-depth pairing."""
    i = t.find('href="%s"' % href)
    if i < 0:
        return None
    start = t.rfind('<div class="article-card">', 0, i)
    if start < 0:
        return None
    depth, j = 0, start
    while True:
        m = re.search(r'<div\b|</div>', t[j:])
        if not m:
            return None
        j += m.end()
        depth += 1 if m.group(0).startswith('<div') else -1
        if depth == 0:
            return t[start:j]

gaps = []
for brand in ("mili", "najie", "aipunajie"):
    p = os.path.join(BASE, brand, "blog/index.html")
    t = open(p, encoding="utf-8").read()
    seen = set()
    for h in hrefs(t):
        if h.startswith("./"):
            key = "/%s/blog/%s" % (brand, h[2:])
        elif h.startswith("/"):
            key = h
        else:
            key = "/%s/blog/%s" % (brand, h)
        if key in seen:
            continue
        seen.add(key)
        f = os.path.join(BASE, key.lstrip("/"))
        if not os.path.exists(f):
            gaps.append({"type": "FILE_MISSING", "brand": brand, "path": key}); continue
        body = open(f, encoding="utf-8").read()
        if os.path.getsize(f) < 1500 or 'http-equiv="refresh"' in body:
            continue
        if key not in main_set:
            blk = card_block(t, h)
            gaps.append({"type": "NO_MAIN_CARD", "brand": brand, "path": key,
                         "rel_href": h, "block": blk})

print("gaps:", len(gaps))
for g in gaps:
    print(g["type"], g.get("path"))
json.dump(gaps, open(os.path.join(BASE, "site-inbox/gaps-1027.json"), "w"),
          ensure_ascii=False, indent=1)

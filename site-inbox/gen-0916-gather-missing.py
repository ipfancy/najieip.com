#!/usr/bin/env python3
"""0916: build missing-card JSON for main blog/index.html from brand article pages.
Read-only. Writes site-inbox/missing-cards-0916.json
"""
import re, json, os
from collections import Counter

root = os.path.expanduser("~/wiki/najieip-verify")
os.chdir(root)

main_t = open("blog/index.html", encoding="utf-8").read()
BRANDS = ["najie", "mili", "aipunajie"]


def clean(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()


cands = []
for b in BRANDS:
    d = os.path.join(b, "blog")
    idx = open(os.path.join(d, "index.html"), encoding="utf-8").read()
    for f in sorted(os.listdir(d)):
        if not f.endswith(".html") or f == "index.html":
            continue
        if f in main_t:                      # already in main index (any href form)
            continue
        own = f in idx                       # present in its own brand index?
        path = f"/{b}/blog/{f}"
        t = open(os.path.join(d, f), encoding="utf-8").read()
        ogt = re.search(r'<meta property="og:title" content="([^"]*)"', t)
        desc = re.search(r'<meta property="og:description" content="([^"]*)"', t)
        dsc2 = re.search(r'<meta name="description" content="([^"]*)"', t)
        h1 = re.search(r'<h1[^>]*>(.*?)</h1>', t, flags=re.S)
        kw = re.search(r'<meta name="keywords" content="([^"]*)"', t)
        dp = re.search(r'"datePublished"\s*:\s*"([^"]+)"', t)
        # brand index card metadata (exact title/tags/date/brand line)
        card = re.search(re.escape(f'"{path}"') + r'.*?</div>\s*</div>', idx, flags=re.S)
        idx_meta = None
        ci = re.search(r'<h2><a href="\./' + re.escape(f) + r'">([^<]*)</a></h2>\s*<div class="meta">(.*?)</div>', idx, flags=re.S)
        if ci:
            idx_meta = {"title": clean(ci.group(1)), "meta": clean(ci.group(2))}
        cands.append({
            "brand": b, "file": f, "path": path, "in_own_index": own,
            "og_title": clean(ogt.group(1)) if ogt else "",
            "h1": clean(h1.group(1)) if h1 else "",
            "desc": clean((desc or dsc2).group(1)) if (desc or dsc2) else "",
            "kw": clean(kw.group(1)) if kw else "",
            "date_published": dp.group(1) if dp else "",
            "idx_meta": idx_meta,
            "size": len(t),
        })

real = [c for c in cands if c["in_own_index"]]
orphan = [c for c in cands if not c["in_own_index"]]
print(f"missing from main index: {len(cands)}  (in own brand index: {len(real)}  orphan: {len(orphan)})")
print("\nORPHANS (not in their own brand index -> skip):")
for c in orphan:
    print("  ", c["path"], c["size"], "B")

print("\nCANDIDATES:")
for c in sorted(real, key=lambda x: x["date_published"], reverse=True):
    print(f"  {c['date_published']}  {c['path']}  kw={c['kw'][:40]!r}  idx={'Y' if c['idx_meta'] else 'N'}")

json.dump(real, open("site-inbox/missing-cards-0916.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\nwrote site-inbox/missing-cards-0916.json")

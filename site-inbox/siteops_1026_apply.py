#!/usr/bin/env python3
# SiteOps 20261026: 主索引补 3 卡 + articles.json 补 1 条 (--apply)
import re, json, os, sys
BASE = "/Users/ziganghe/wiki/najieip-verify"
APPLY = "--apply" in sys.argv
TARGET = "2026-10-26"
TARGETS = [
    ("mili", "20261026-mili-divorce-inheritance-property"),
    ("najie", "20261026-najie-double11-ip-risk"),
    ("mili", "20261026-trade-secret-secret-point-fixation"),
]

def card_blocks(t):
    out = []
    for m in re.finditer(r'<div class="article-card">', t):
        s = m.start(); i = s; depth = 0
        while i < len(t):
            if t.startswith("<div", i):
                depth += 1; i = t.find(">", i) + 1; continue
            if t.startswith("</div>", i):
                depth -= 1; i += 6
                if depth == 0:
                    out.append((s, i, t[s:i])); break
                continue
            i += 1
    return out

def card_date(b):
    m = re.search(r'<div class="meta">(.*?)</div>', b, re.S)
    d = re.search(r'(\d{4}-\d{2}-\d{2})', m.group(1)) if m else None
    return d.group(1) if d else None

mp = f"{BASE}/blog/index.html"
main0 = open(mp, encoding="utf-8").read()
orig_cards = main0.count('<div class="article-card">')
t = main0
inserted = 0
for brand, slug in TARGETS:
    if f"/{brand}/blog/{slug}.html" in t:
        print(f"SKIP already present: {slug}")
        continue
    bt = open(f"{BASE}/{brand}/blog/index.html", encoding="utf-8").read()
    tmpl = None
    for s, e, b in card_blocks(bt):
        if slug in b:
            tmpl = b; break
    assert tmpl, f"no template for {slug}"
    card = tmpl.replace('href="./', f'href="/{brand}/blog/')
    assert card.startswith('<div class="article-card">'), card[:80]
    assert card.rstrip().endswith("</div>"), card[-60:]
    # re-scan positions each round (v3 rule)
    blocks = card_blocks(t)
    pos = None
    for s, e, b in blocks:
        d = card_date(b)
        if d and d < TARGET:
            pos = s; break
    assert pos is not None
    t2 = t[:pos] + card + "\n  " + t[pos:]
    assert t2.replace(card + "\n  ", "", 1) == t, f"external change on {slug}"
    t = t2; inserted += 1
    print(f"INSERT {slug} at {pos} (before {card_date(blocks[[i for i,(s,e,b) in enumerate(blocks) if s==pos][0]][2])})")

# assertions
new_cards = t.count('<div class="article-card">')
assert new_cards == orig_cards + inserted, (new_cards, orig_cards)
assert t.count("**") == 0, "markdown leak"
# div balance
depth = 0; bad = False
for m in re.finditer(r"<(/?)div\b", t):
    depth += -1 if m.group(1) else 1
    if depth < 0: bad = True; break
print(f"[assert] cards {orig_cards}->{new_cards}, div_end_depth={depth}, neg={bad}")
assert depth == 0 and not bad

# href uniqueness
from collections import Counter
c = Counter(re.findall(r'<h2><a href="(/[^"]+)"', t))
dups = [k for k, v in c.items() if v > 1]
print(f"[assert] dup hrefs={dups or 'none'}")
assert not dups

if APPLY:
    open(mp, "w", encoding="utf-8").write(t)
    print("WROTE blog/index.html")

# --- articles.json ---
ap = f"{BASE}/articles.json"
aj = json.load(open(ap, encoding="utf-8"))
slug = "20261026-trade-secret-secret-point-fixation"
if any(slug in json.dumps(a, ensure_ascii=False) for a in aj):
    print("articles.json: already present")
else:
    page = open(f"{BASE}/mili/blog/{slug}.html", encoding="utf-8").read()
    title = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S).group(1)
    title = re.sub(r"<[^>]+>", "", title).strip()
    desc = re.search(r'<meta name="description" content="([^"]*)"', page).group(1)
    entry = {"url": f"/mili/blog/{slug}.html", "title": title, "date": TARGET,
             "site": "mili", "description": desc}
    idx = next((i for i, a in enumerate(aj) if (a.get("date") or "") < TARGET), len(aj))
    print(f"articles.json insert at {idx} (before {aj[idx].get('date') if idx < len(aj) else 'END'}) title={title[:30]}")
    if APPLY:
        aj.insert(idx, entry)
        json.dump(aj, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        open(ap, "a", encoding="utf-8").write("\n")
        print(f"WROTE articles.json n={len(aj)}")

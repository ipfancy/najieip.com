#!/usr/bin/env python3
"""Structural verification: new card direct-child of .container, div depth, uniqueness."""
import re, os
ROOT = "/Users/ziganghe/wiki/najieip-verify"
SLUG = "20261006-nobel-icecube-patent-four-rules"
PAGE = os.path.join(ROOT, "mili/blog", SLUG + ".html")

t = open(PAGE, encoding="utf-8").read()
print("PAGE:", os.path.getsize(PAGE), "B")
print(" h1 =", t.count("<h1"), "| ld+json =", t.count("application/ld+json"),
      "| og:image =", "og:image" in t, "| ** =", t.count("**"), "| strong =", t.count("<strong>"))
m = re.search(r'<meta name="description" content="([^"]*)"', t)
title = re.search(r"<title>(.*?)</title>", t, re.S).group(1)
print(" desc len =", len(m.group(1)), "| desc repeats title =", m.group(1)[:20] in title)
for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
    import json; json.loads(b)
print(" JSON-LD blocks -> json.loads OK")
assert "https://***" not in t and t.count("https://schema.org") >= 2

for path, href in [(os.path.join(ROOT, "mili/blog/index.html"), f"./{SLUG}.html"),
                   (os.path.join(ROOT, "blog/index.html"), f"/mili/blog/{SLUG}.html")]:
    h = open(path, encoding="utf-8").read()
    body = h[h.find("<body"):]
    # depth of every article-card open tag; container is depth 1 -> cards must be depth 1
    depth, depth1, total = 0, 0, 0
    for m in re.finditer(r"<(/?)div", body):
        if m.group(1):
            depth -= 1
        else:
            if body[m.start():m.start() + 50].startswith('<div class="article-card"'):
                total += 1
                if depth == 1:
                    depth1 += 1
            depth += 1
    hrefs = re.findall(r'<h2><a href="([^"]+)"', body)
    dup = [x for x in set(hrefs) if hrefs.count(x) > 1]
    idx_in_body = body.find(f'<h2><a href="{href}"')
    prev = body[:idx_in_body]
    prev_cards = len(re.findall(r'<div class="article-card">', prev))
    prev_dates = re.findall(r'<div class="meta">.*?(\d{4}-\d{2}-\d{2})', prev, re.S)
    print(f"{os.path.basename(os.path.dirname(path)) or 'blog'}/index: cards={total} depth1={depth1} "
          f"dup={dup} position={prev_cards + 1} prev_dates={prev_dates[-2:]}")
    assert total == depth1, "card not a direct child of container"
    assert not dup, dup
    assert href in hrefs
    # date-descending: anything before the new card must be dated >= 2026-10-06
    assert all(d >= "2026-10-06" for d in prev_dates), prev_dates
print("ALL STRUCTURE CHECKS PASS")

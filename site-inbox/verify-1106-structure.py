#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify 2026-11-06 index structure + new cards"""
import re, os, json
from collections import Counter
REPO = os.path.expanduser("~/wiki/najieip-verify")

NEW = {
    "mili/blog/index.html": ["20261103-mili-guarantee-period-six-months",
                             "20261104-mili-inventor-reward-5-percent",
                             "20261106-mili-nda-vs-noncompete"],
    "blog/index.html": ["20261103-mili-guarantee-period-six-months",
                        "20261104-mili-inventor-reward-5-percent",
                        "20261106-mili-nda-vs-noncompete",
                        "20261106-mili-appraisal-opinion-review"],
}
fails = []
for rel, slugs in NEW.items():
    t = open(os.path.join(REPO, rel), encoding="utf-8").read()
    ncard = t.count('<div class="article-card">')
    # depth scan
    depth = 0; errors = 0
    for m in re.finditer(r'<(/?)div\b', t):
        if m.group(1) == "":
            depth += 1
        else:
            depth -= 1
            if depth < 0:
                errors += 1; depth = 0
    # malformed: each card must start cleanly with <div class="article-card"> followed by h2
    malformed = len([m for m in re.finditer(r'<div class="article-card">', t)
                     if not re.match(r'\s*<h2><a href="', t[m.end():m.end()+60])])
    hrefs = Counter(re.findall(r'<h2><a href="([^"]+)"', t))
    dup = {k: v for k, v in hrefs.items() if v > 1}
    # card dates at insert points
    seq = re.findall(r'<div class="article-card">.*?(\d{4}-\d{2}-\d{2})', t, re.S)
    print(f"[{rel}] cards={ncard} div_depth_end={depth} errs={errors} malformed={malformed} dups={len(dup)}")
    if depth != 0 or errors: fails.append(f"{rel} div imbalance depth={depth} errs={errors}")
    if malformed: fails.append(f"{rel} malformed={malformed}")
    if dup: fails.append(f"{rel} dup hrefs={list(dup)[:3]}")
    for s in slugs:
        cnt = len(re.findall(r'<h2><a href="[^"]*' + re.escape(s), t))
        print(f"   {s}: card_hits={cnt}")
        if cnt != 1: fails.append(f"{rel} {s} hits={cnt}")
    # prefix ordering: find index of first new card, dates before it must be >= its date
    # verify each new card date equals expected by reading the meta date inside its block
    for s in slugs:
        m = re.search(r'<h2><a href="[^"]*' + re.escape(s), t)
        if m:
            seg = t[m.start():m.start()+700]
            d = re.search(r'(\d{4}-\d{2}-\d{2})', seg)
            print(f"      date in card: {d.group(1) if d else 'NONE'}")

print("\nFAILS:", fails if fails else "NONE")

#!/usr/bin/env python3
"""Verify card placement + structure after 1017b insertion."""
import os, re

REPO = os.path.expanduser("~/wiki/najieip-verify")
SLUG = "customs-ip-post-filing-steps-20261017"

for idx in ["mili/blog/index.html", "blog/index.html"]:
    t = open(os.path.join(REPO, idx), encoding="utf-8").read()
    body = t[t.find("<body"):]
    cards = [m.start() for m in re.finditer(r'<div class="article-card">', body)]
    first_href = re.search(r'<div class="article-card">\s*<h2><a href="([^"]+)"', body).group(1)
    dates = re.findall(r'<div class="meta">.*?(\d{4}-\d{2}-\d{2})', body[:body.find('<div class="article-card">', cards[1])], re.S)
    print(f"{idx}: cards={len(cards)} first_href={first_href}")
    print(f"   first card date={dates[0] if dates else '?'} | slug in first card={SLUG in body[cards[0]:cards[1]]}")
    # date descending over prefix until first reversal
    seq = []
    for i, c in enumerate(cards):
        nxt = cards[i+1] if i+1 < len(cards) else len(body)
        m = re.search(r'(\d{4}-\d{2}-\d{2})', body[c:nxt])
        if m:
            seq.append(m.group(1))
    mono_break = next((i for i in range(1, len(seq)) if seq[i] > seq[i-1]), None)
    print(f"   date seq head={seq[:5]} monotonic_break_at={mono_break}")
    # malformed: each card must start with h2
    bad = sum(1 for i, c in enumerate(cards) if not re.match(r'<div class="article-card">\s*<h2><a href=', body[c:c+120]))
    print(f"   malformed_cards={bad} stars={t.count('**')} size={os.path.getsize(os.path.join(REPO, idx))}")

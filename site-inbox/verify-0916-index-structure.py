#!/usr/bin/env python3
"""Verify main blog/index.html structure: compare BEFORE (109 cards, known good) vs AFTER (157).
Checks: div balance, depth, card depth, malformed cards, duplicate hrefs, markdown leak, JSON-LD.
"""
import re, sys
from collections import Counter


def analyse(path, label):
    t = open(path, encoding='utf-8').read()
    print(f"===== {label}: {path} ({len(t)} B) =====")
    print("  article-card count:", t.count('<div class="article-card">'))
    print("  <div:", len(re.findall(r'<div\b', t)), " </div>:", t.count('</div>'),
          " balanced:", len(re.findall(r'<div\b', t)) == t.count('</div>'))

    # depth from <body>, counting div tags in document order
    depth = 0
    anomal = 0
    card_depths = Counter()
    body_seen = False
    for m in re.finditer(r'<body\b|</body>|<(/?)(div)\b[^>]*>', t):
        s = m.group(0)
        if s.startswith('<body'):
            body_seen = True
            continue
        if not body_seen:
            continue
        if m.group(0).startswith('<div class="article-card">'):
            card_depths[depth] += 1
        if m.group(1) == '/':
            depth -= 1
            if depth < 0:
                anomal += 1
        else:
            depth += 1
    print("  final depth:", depth, "| 'close with empty stack' anomalies:", anomal)
    print("  card depths:", dict(card_depths))

    # every card must start with <h2><a href= and be well-formed
    blocks = re.findall(r'<div class="article-card">(.*?)\n  </div>', t, flags=re.S)
    mal = [b[:70] for b in blocks
           if not ('<h2><a href=' in b and '<div class="meta">' in b and '<p>' in b)]
    print("  cards:", len(blocks), "malformed:", len(mal), mal[:2])
    # orphan double-open detection
    print("  orphan '<div class=\"article-card\">\\n  <div class=\"article-card\">':",
          t.count('<div class="article-card">\n  <div class="article-card">'))
    # cards whose opening tag is missing (block starting with <h2> right after a closing div + separator)
    refs = re.findall(r'<h2><a href="([^"]+)"', t)
    dups = {k: v for k, v in Counter(refs).items() if v > 1}
    print("  h2 links:", len(refs), "duplicates:", dups)
    print("  markdown leak '**':", t.count("**"), "| 'https://***':", t.count('https://***'))
    print("  schema.org occurrences:", t.count('https://schema.org'))
    dates = []
    for m in re.finditer(re.escape('<div class="article-card">'), t):
        d = re.search(r'(\d{4}-\d{2}-\d{2})', t[m.start():m.start() + 900])
        dates.append(d.group(1) if d else None)
    ds = [d for d in dates if d]
    print("  dated cards:", len(ds), "undated:", sum(1 for d in dates if not d),
          "monotonic desc:", all(a >= b for a, b in zip(ds, ds[1:])))
    print("  date range:", ds[0], "->", ds[-1])
    return dict(cards=len(blocks), depth=depth, anomal=anomal, dups=dups)


a = analyse('/tmp/blog-index-0916-before.html', 'BEFORE')
b = analyse('blog/index.html', 'AFTER')
print("\n=== DELTA ===")
print("  cards:", a['cards'], "->", b['cards'], "(+%d)" % (b['cards'] - a['cards']))
print("  depth:", a['depth'], "->", b['depth'], "| anomalies:", a['anomal'], "->", b['anomal'])
print("  dups:", a['dups'], "->", b['dups'])
ok = (b['cards'] == a['cards'] + 48 and b['depth'] == 0 and b['anomal'] == 0 and not b['dups'])
print("  RESULT:", "PASS" if ok else "FAIL")

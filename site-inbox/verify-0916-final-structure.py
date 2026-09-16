#!/usr/bin/env python3
"""Final structural verification of committed blog/index.html vs previous committed version.
Both sides dumped from git to unique temp paths, then analysed identically.
"""
import subprocess, re, os
from collections import Counter

os.chdir(os.path.expanduser("~/wiki/najieip-verify"))
PRE = "/tmp/idx0916_pre.html"
POST = "/tmp/idx0916_post.html"
for ref, out in [("HEAD~1", PRE), ("HEAD", POST)]:
    with open(out, "wb") as f:
        f.write(subprocess.run(["git", "show", f"{ref}:blog/index.html"],
                               capture_output=True, check=True).stdout)


def analyse(path, label):
    t = open(path, encoding="utf-8").read()
    cards = re.findall(r'<div class="article-card">', t)
    opens = len(re.findall(r'<div\b', t))
    closes = t.count('</div>')
    depth = 0
    anomal = 0
    dep_counter = Counter()
    body = False
    for m in re.finditer(r'<body\b|</body>|<(/?)(div)\b[^>]*>', t):
        s = m.group(0)
        if s.startswith('<body'):
            body = True
            continue
        if not body:
            continue
        if s.startswith('<div class="article-card">'):
            dep_counter[depth] += 1
        if m.group(1) == '/':
            depth -= 1
            if depth < 0:
                anomal += 1
        else:
            depth += 1
    blocks = re.findall(r'<div class="article-card">(.*?)\n  </div>', t, flags=re.S)
    mal = [b[:60] for b in blocks if not ('<h2><a href=' in b and '<div class="meta">' in b and '<p>' in b)]
    refs = re.findall(r'<h2><a href="([^"]+)"', t)
    dups = {k: v for k, v in Counter(refs).items() if v > 1}
    dates = []
    for m in re.finditer(re.escape('<div class="article-card">'), t):
        d = re.search(r'(\d{4}-\d{2}-\d{2})', t[m.start():m.start() + 900])
        dates.append(d.group(1) if d else None)
    ds = [d for d in dates if d]
    print(f"=== {label} ({len(t)} B) ===")
    print("  cards:", len(cards), "| <div>:", opens, "</div>:", closes, "balanced:", opens == closes)
    print("  final depth:", depth, "| empty-stack closes:", anomal, "| card depths:", dict(dep_counter))
    print("  parsed card blocks:", len(blocks), "| malformed:", len(mal), mal[:2])
    print("  h2 links:", len(refs), "| duplicate hrefs:", dups)
    print("  stray '**':", t.count("**"), "| https://***:", t.count("https://***"))
    print("  dated cards:", len(ds), "| undated:", len(dates) - len(ds),
          "| monotonic desc:", all(a >= b for a, b in zip(ds, ds[1:])))
    print("  date range:", ds[0], "->", ds[-1])
    return dict(cards=len(cards), depth=depth, anomal=anomal, mal=len(mal), dups=bool(dups),
                opens=opens, closes=closes)


a = analyse(PRE, "PREVIOUS (HEAD~1)")
b = analyse(POST, "COMMITTED (HEAD)")
print("\n=== DELTA ===")
checks = {
    "cards +48": b["cards"] == a["cards"] + 48,
    "div open/close balanced": b["opens"] == b["closes"],
    "div delta = +96": b["opens"] - a["opens"] == 96,
    "no empty-stack closes": b["anomal"] == 0,
    "all cards parse": b["mal"] == 0,
    "no dup hrefs": not b["dups"],
    "depth unchanged": a["depth"] == b["depth"],
}
for k, v in checks.items():
    print(("  PASS  " if v else "  FAIL  ") + k)
print("  RESULT:", "PASS" if all(checks.values()) else "FAIL")

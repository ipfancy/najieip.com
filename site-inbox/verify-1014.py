#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re, os, json, collections, subprocess
os.chdir(os.path.expanduser("~/wiki/najieip-verify"))

t = open("blog/index.html", encoding="utf-8", errors="ignore").read()
hrefs = re.findall(r'<h2><a href="([^"]+)"', t)
print("cards(div) =", t.count('<div class="article-card">'), " hrefs =", len(hrefs))
dups = [h for h, n in collections.Counter(hrefs).items() if n > 1]
print("dup hrefs:", dups)
print("stars:", t.count("**"), " top5:")
for h in hrefs[:5]: print("   ", h)

body = t[t.find("<body"):]
d = 0; neg = 0; dc = 0; start = None
for m in re.finditer(r"<(/?)div[^>]*>", body):
    if m.group(1) == "":
        if d == 1 and body[m.start():].startswith('<div class="article-card"'): dc += 1
        d += 1
    else:
        d -= 1
        if d < 0: neg += 1
print("final depth:", d, "neg:", neg, "depth1 cards:", dc)
assert d == 0 and neg == 0 and dc == len(hrefs) and not dups

# 六联判据 on 新页
for f in ["najie/blog/20261014-trademark-pattern-packaging-confusion.html",
          "najie/blog/layout-design-originality-claim-322-2026.html",
          "mili/blog/patent-vs-trade-secret-layering-2026.html"]:
    x = open(f, encoding="utf-8", errors="ignore").read()
    md = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', x)
    tt = re.search(r"<title>(.*?)</title>", x, re.S)
    ok = (len(re.findall(r"<h1[\s>]", x)) == 1 and x.count("application/ld+json") >= 2
          and "og:image" in x and x.count("**") == 0
          and not re.search(r"<p>\|.*?\|</p>", x)
          and md and tt and md.group(1)[:20] != re.sub(r"\s+", " ", tt.group(1)).strip()[:20])
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', x, re.S):
        json.loads(b)
    print("  %s  %s  bytes=%d ld=%d" % ("OK  " if ok else "FAIL", f, os.path.getsize(f), x.count("application/ld+json")))
    assert ok
print("VERIFY PASS")
print(subprocess.run("git diff --stat", shell=True, capture_output=True, text=True).stdout)

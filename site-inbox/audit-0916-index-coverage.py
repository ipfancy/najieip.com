#!/usr/bin/env python3
"""SiteOps 0916 audit: index coverage of brand articles vs main blog/index.html."""
import re
from pathlib import Path

root = Path.home() / "wiki/najieip-verify"
main_idx = (root / "blog/index.html").read_text(encoding="utf-8")
main_refs = re.findall(r'<h2><a href="([^"]+)"', main_idx)
main_set = set(main_refs)
print("main blog/index.html cards:", main_idx.count('class="article-card"'), "h2 links:", len(main_refs))

brands = ["najie", "mili", "aipunajie"]
for b in brands:
    d = root / b / "blog"
    if not d.exists():
        continue
    files = sorted(p.name for p in d.glob("*.html") if p.name != "index.html")
    idx = (d / "index.html").read_text(encoding="utf-8")
    idx_refs = set(re.findall(r'<h2><a href="([^"]+)"', idx))
    miss_own, miss_main = [], []
    for f in files:
        if f not in idx:
            miss_own.append(f)
        if f"/{b}/blog/{f}" not in main_set and f"./{f}" not in main_set:
            miss_main.append(f)
    print(f"\n[{b}] files={len(files)} own_index_links={len(idx_refs)}")
    print("  missing in own index:", miss_own)
    print("  missing in MAIN index:", miss_main)

# duplicate href check in main index
from collections import Counter
dups = {k: v for k, v in Counter(main_refs).items() if v > 1}
print("\n=== duplicate hrefs in main index ===", dups)

# brand index dups
for b in brands:
    d = root / b / "blog"
    if not d.exists():
        continue
    idx = (d / "index.html").read_text(encoding="utf-8")
    refs = re.findall(r'<h2><a href="([^"]+)"', idx)
    dd = {k: v for k, v in Counter(refs).items() if v > 1}
    if dd:
        print(f"dups in {b}/blog/index.html:", dd)

# div balance + depth check on main index
print("\n=== main index integrity ===")
print("div open:", len(re.findall(r'<div\b', main_idx)), "div close:", main_idx.count('</div>'))
print("markdown leak '**':", main_idx.count("**"))
depth = 0
anom = 0
for m in re.finditer(r'<(/?)(div|body)\b[^>]*>', main_idx):
    if m.group(2) == 'div':
        if m.group(1):
            depth -= 1
            if depth < 0:
                anom += 1
        else:
            depth += 1
print("final depth:", depth, "anomalies:", anom)
print("orphan double-card:", main_idx.count('<div class="article-card">\n  <div class="article-card">'))
